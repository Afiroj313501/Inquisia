import json
from typing import Any
from fastapi import HTTPException, status
import httpx
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.ai_artifact import AiArtifact
from app.models.saved_paper import SavedPaper
from app.schemas.interest import NicheSummaryResponse
from app.schemas.paper import LiteratureSynthesisResponse
from app.schemas.recommendation import ResearchBriefResponse
from app.services.interest_analysis_service import DOMAIN_LABELS, get_latest_interest_profile
from app.services.profile_service import get_profile_by_user_id
from app.services.topic_catalog import TOPIC_MAP

_AI_NOTICE = (
    "AI-generated exploratory research brief. Treat these questions and methodology "
    "suggestions as starting points and verify all claims against peer-reviewed literature."
)

_SYNTHESIS_NOTICE = (
    "AI-generated synthesis grounded strictly in your saved OpenAlex papers. "
    "Verify nuanced claims against the full text of each paper."
)


def _call_gemini_json(prompt: str) -> tuple[dict[str, object], str]:
    settings = get_settings()
    api_key = (settings.gemini_api_key or "").strip().strip('"').strip("'")
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI generation requires GEMINI_API_KEY to be configured on the server.",
        )

    endpoint = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{settings.gemini_model}:generateContent"
    )
    body = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"responseMimeType": "application/json"},
    }

    try:
        response = httpx.post(
            endpoint,
            params={"key": api_key},
            json=body,
            timeout=25.0,
        )
        response.raise_for_status()
        payload = response.json()
        raw_text = payload["candidates"][0]["content"]["parts"][0]["text"]
        parsed = json.loads(raw_text)
        if not isinstance(parsed, dict):
            raise ValueError("Expected JSON object from Gemini.")
        return parsed, settings.gemini_model
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 429:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Gemini free-tier rate limit reached. Please wait a minute and try again.",
            ) from exc
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Unable to generate AI response from Gemini right now.",
        ) from exc
    except (httpx.HTTPError, KeyError, IndexError, TypeError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Unable to generate AI response from Gemini right now.",
        ) from exc


def _get_cached_artifact(
    db: Session,
    user_id: int,
    artifact_type: str,
    target_key: str,
) -> AiArtifact | None:
    return db.scalar(
        select(AiArtifact).where(
            AiArtifact.user_id == user_id,
            AiArtifact.artifact_type == artifact_type,
            AiArtifact.target_key == target_key,
        )
    )


def _upsert_artifact(
    db: Session,
    user_id: int,
    artifact_type: str,
    target_key: str,
    model: str,
    payload: dict[str, Any],
) -> None:
    existing = _get_cached_artifact(db, user_id, artifact_type, target_key)
    if existing is None:
        db.add(
            AiArtifact(
                user_id=user_id,
                artifact_type=artifact_type,
                target_key=target_key,
                model=model,
                payload=payload,
            )
        )
    else:
        existing.model = model
        existing.payload = payload
    db.commit()


def get_cached_topic_brief(
    db: Session,
    user_id: int,
    topic_id: str,
) -> ResearchBriefResponse:
    """Return a previously generated topic brief from cache, or 404 if none exists."""
    if topic_id not in TOPIC_MAP:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Unknown research topic '{topic_id}'.",
        )
    cached = _get_cached_artifact(db, user_id, "topic_brief", topic_id)
    if cached is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No cached research brief for this topic yet.",
        )
    return ResearchBriefResponse.model_validate(cached.payload)


def generate_topic_brief(
    db: Session,
    user_id: int,
    topic_id: str,
    *,
    refresh: bool = False,
) -> ResearchBriefResponse:
    """Generate (or return cached) Gemini-powered exploratory research brief for a topic."""
    topic = TOPIC_MAP.get(topic_id)
    if topic is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Unknown research topic '{topic_id}'.",
        )

    if not refresh:
        cached = _get_cached_artifact(db, user_id, "topic_brief", topic_id)
        if cached is not None:
            return ResearchBriefResponse.model_validate(cached.payload)

    profile = get_profile_by_user_id(db, user_id)
    saved_papers = list(
        db.scalars(
            select(SavedPaper.title)
            .where(SavedPaper.user_id == user_id)
            .order_by(SavedPaper.created_at.desc())
            .limit(5)
        ).all()
    )

    profile_context = (
        f"Education: {profile.education_level} ({profile.degree_program}), "
        f"Experience: {profile.research_experience_level}, "
        f"Skills: {', '.join(profile.technical_skills) or 'None listed'}"
        if profile is not None
        else "No academic profile provided."
    )
    papers_context = (
        "; ".join(saved_papers) if saved_papers else "No saved papers yet."
    )

    prompt = (
        f"You are an academic research mentor. Create a concise, realistic exploratory "
        f"research brief for a student interested in '{topic.title}'.\n"
        f"Topic summary: {topic.description}\n"
        f"Student background: {profile_context}\n"
        f"Saved literature titles: {papers_context}\n\n"
        f"Rules:\n"
        f"- Do NOT invent or cite any paper titles, authors, or DOIs not listed above.\n"
        f"- Return ONLY valid JSON with keys:\n"
        f'  "problem_framing": string (2-3 sentences),\n'
        f'  "research_questions": array of 3 concise strings,\n'
        f'  "suggested_methodology": string (2-3 sentences tailored to their experience).'
    )

    parsed, model_name = _call_gemini_json(prompt)
    questions_raw = parsed.get("research_questions")
    questions = (
        [str(q) for q in questions_raw[:5]]
        if isinstance(questions_raw, list)
        else []
    )

    brief = ResearchBriefResponse(
        topic_id=topic.id,
        topic_title=topic.title,
        model=model_name,
        problem_framing=str(parsed.get("problem_framing", "")),
        research_questions=questions,
        suggested_methodology=str(parsed.get("suggested_methodology", "")),
        ai_generated_notice=_AI_NOTICE,
    )
    _upsert_artifact(
        db,
        user_id,
        "topic_brief",
        topic_id,
        model_name,
        brief.model_dump(mode="json"),
    )
    return brief


def get_latest_literature_synthesis(
    db: Session,
    user_id: int,
) -> LiteratureSynthesisResponse:
    """Return the user's most recent cached literature synthesis, or 404 if none."""
    cached = db.scalar(
        select(AiArtifact)
        .where(
            AiArtifact.user_id == user_id,
            AiArtifact.artifact_type == "literature_synthesis",
        )
        .order_by(AiArtifact.updated_at.desc())
        .limit(1)
    )
    if cached is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No cached literature synthesis yet.",
        )
    return LiteratureSynthesisResponse.model_validate(cached.payload)


def synthesize_saved_papers(
    db: Session,
    user_id: int,
    topic_id: str | None = None,
    *,
    refresh: bool = False,
) -> LiteratureSynthesisResponse:
    """Synthesize (or return cached) themes and gaps across saved OpenAlex papers."""
    target_key = topic_id or "all"
    if not refresh:
        cached = _get_cached_artifact(db, user_id, "literature_synthesis", target_key)
        if cached is not None:
            return LiteratureSynthesisResponse.model_validate(cached.payload)

    papers = list(
        db.scalars(
            select(SavedPaper)
            .where(SavedPaper.user_id == user_id)
            .order_by(SavedPaper.created_at.desc())
            .limit(8)
        ).all()
    )
    if len(papers) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Save at least 2 OpenAlex papers before generating a literature synthesis.",
        )

    topic_title = TOPIC_MAP[topic_id].title if topic_id and topic_id in TOPIC_MAP else None
    paper_blocks = []
    for idx, p in enumerate(papers, start=1):
        abstract_snippet = (p.abstract or "No abstract available.")[:400]
        paper_blocks.append(
            f"{idx}. {p.title} ({p.publication_year or 'n.d.'}, {p.venue or 'Unknown venue'})\n"
            f"   Abstract: {abstract_snippet}"
        )

    topic_line = f"Target research topic: {topic_title}\n" if topic_title else ""
    prompt = (
        f"You are an academic literature synthesis assistant.\n"
        f"{topic_line}"
        f"Synthesize ONLY the following real papers saved by the student:\n"
        f"{chr(10).join(paper_blocks)}\n\n"
        f"Rules:\n"
        f"- Do NOT invent or cite any paper outside this list.\n"
        f"- Return ONLY valid JSON with keys:\n"
        f'  "common_themes": array of 3 concise strings,\n'
        f'  "methodological_gaps": array of 2-3 concise strings,\n'
        f'  "next_step_recommendation": string (2 sentences).'
    )

    parsed, model_name = _call_gemini_json(prompt)
    themes_raw = parsed.get("common_themes")
    gaps_raw = parsed.get("methodological_gaps")

    synthesis = LiteratureSynthesisResponse(
        paper_count=len(papers),
        paper_titles=[p.title for p in papers],
        model=model_name,
        common_themes=(
            [str(t) for t in themes_raw[:5]] if isinstance(themes_raw, list) else []
        ),
        methodological_gaps=(
            [str(g) for g in gaps_raw[:5]] if isinstance(gaps_raw, list) else []
        ),
        next_step_recommendation=str(parsed.get("next_step_recommendation", "")),
        ai_generated_notice=_SYNTHESIS_NOTICE,
    )
    _upsert_artifact(
        db,
        user_id,
        "literature_synthesis",
        target_key,
        model_name,
        synthesis.model_dump(mode="json"),
    )
    return synthesis


def get_cached_niche_summary(db: Session, user_id: int) -> NicheSummaryResponse:
    """Return cached interdisciplinary niche summary for the user's latest interest profile."""
    interest_profile = get_latest_interest_profile(db, user_id)
    if interest_profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No interest profile has been generated yet.",
        )
    cached = _get_cached_artifact(
        db, user_id, "niche_summary", str(interest_profile.id)
    )
    if cached is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No cached niche summary yet.",
        )
    return NicheSummaryResponse.model_validate(cached.payload)


def generate_niche_summary(
    db: Session,
    user_id: int,
    *,
    refresh: bool = False,
) -> NicheSummaryResponse:
    """Generate (or return cached) Gemini interdisciplinary niche summary."""
    interest_profile = get_latest_interest_profile(db, user_id)
    if interest_profile is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Generate an interest profile before requesting a niche summary.",
        )

    target_key = str(interest_profile.id)
    if not refresh:
        cached = _get_cached_artifact(db, user_id, "niche_summary", target_key)
        if cached is not None:
            return NicheSummaryResponse.model_validate(cached.payload)

    domain_summary = ", ".join(
        f"{entry['label']} ({entry['score']}/100)"
        for entry in interest_profile.domain_scores[:3]
    )
    dimension_summary = ", ".join(
        f"{entry['label']} ({entry['score']}/100)"
        for entry in interest_profile.dimension_scores[:2]
    )
    top_domain_labels = [
        DOMAIN_LABELS.get(k, k) for k in interest_profile.top_domains
    ]

    profile = get_profile_by_user_id(db, user_id)
    profile_line = (
        f"Academic background: {profile.education_level} in {profile.degree_program}; "
        f"career goals: {profile.career_goals or 'Not specified'}."
        if profile is not None
        else "No academic profile provided."
    )

    prompt = (
        f"You are an academic research advisor.\n"
        f"Top interest domains: {domain_summary}\n"
        f"Top methodology dimensions: {dimension_summary}\n"
        f"{profile_line}\n\n"
        f"Synthesize how these strengths intersect into a realistic interdisciplinary "
        f"research niche for an early-stage researcher.\n"
        f"Rules:\n"
        f"- Do NOT invent or cite any papers, authors, or DOIs.\n"
        f"- Return ONLY valid JSON with keys:\n"
        f'  "niche_title": string (short 4-8 word title),\n'
        f'  "summary": string (2-3 concise sentences),\n'
        f'  "example_directions": array of 3 concise exploratory direction strings.'
    )

    parsed, model_name = _call_gemini_json(prompt)
    directions_raw = parsed.get("example_directions")

    niche = NicheSummaryResponse(
        interest_profile_id=interest_profile.id,
        top_domains=top_domain_labels,
        model=model_name,
        niche_title=str(parsed.get("niche_title", "Interdisciplinary Research Niche")),
        summary=str(parsed.get("summary", "")),
        example_directions=(
            [str(d) for d in directions_raw[:5]]
            if isinstance(directions_raw, list)
            else []
        ),
        ai_generated_notice=(
            "AI-generated exploratory niche synthesis based on your interest scores. "
            "Use it as inspiration alongside peer-reviewed literature."
        ),
    )
    _upsert_artifact(
        db,
        user_id,
        "niche_summary",
        target_key,
        model_name,
        niche.model_dump(mode="json"),
    )
    return niche
