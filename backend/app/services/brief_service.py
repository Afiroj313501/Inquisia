import json
from fastapi import HTTPException, status
import httpx
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.saved_paper import SavedPaper
from app.schemas.recommendation import ResearchBriefResponse
from app.services.profile_service import get_profile_by_user_id
from app.services.topic_catalog import TOPIC_MAP

_AI_NOTICE = (
    "AI-generated exploratory research brief. Treat these questions and methodology "
    "suggestions as starting points and verify all claims against peer-reviewed literature."
)


def generate_topic_brief(
    db: Session,
    user_id: int,
    topic_id: str,
) -> ResearchBriefResponse:
    """Generate an optional Gemini-powered exploratory research brief for a topic."""
    topic = TOPIC_MAP.get(topic_id)
    if topic is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Unknown research topic '{topic_id}'.",
        )

    settings = get_settings()
    if not settings.gemini_api_key or not settings.gemini_api_key.strip():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI Research Brief requires GEMINI_API_KEY to be configured on the server.",
        )

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
            params={"key": settings.gemini_api_key.strip()},
            json=body,
            timeout=20.0,
        )
        response.raise_for_status()
        payload = response.json()
        raw_text = payload["candidates"][0]["content"]["parts"][0]["text"]
        parsed = json.loads(raw_text)
    except (httpx.HTTPError, KeyError, IndexError, TypeError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Unable to generate AI research brief from Gemini right now.",
        ) from exc

    questions_raw = parsed.get("research_questions")
    questions = (
        [str(q) for q in questions_raw[:5]]
        if isinstance(questions_raw, list)
        else []
    )

    return ResearchBriefResponse(
        topic_id=topic.id,
        topic_title=topic.title,
        model=settings.gemini_model,
        problem_framing=str(parsed.get("problem_framing", "")),
        research_questions=questions,
        suggested_methodology=str(parsed.get("suggested_methodology", "")),
        ai_generated_notice=_AI_NOTICE,
    )
