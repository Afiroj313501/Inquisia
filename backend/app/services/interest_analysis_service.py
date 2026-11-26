from collections import defaultdict
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.academic_profile import AcademicProfile
from app.models.assessment import AssessmentSession
from app.models.interest_profile import InterestProfile
from app.services.profile_service import get_profile_by_user_id
from app.services.question_bank import QUESTION_MAP

DOMAIN_LABELS: dict[str, str] = {
    "ai_ml": "Artificial Intelligence & Machine Learning",
    "nlp": "Natural Language Processing & Information Retrieval",
    "systems_security": "Distributed Systems & Cybersecurity",
    "hci": "Human-Computer Interaction & EdTech",
    "bio_health": "Computational Biology & Healthcare",
    "data_science": "Data Science & Computational Social Science",
}

DIMENSION_LABELS: dict[str, str] = {
    "theoretical_rigor": "Theoretical & Mathematical Rigor",
    "empirical_experimentation": "Empirical Experimentation & Benchmarking",
    "applied_engineering": "Systems & Applied Engineering",
    "human_centered_inquiry": "Human-Centered & Interdisciplinary Inquiry",
    "applied_impact": "Near-Term Real-World Impact",
}

_DOMAIN_KEYWORDS: dict[str, tuple[str, ...]] = {
    "ai_ml": ("ai", "machine learning", "deep learning", "artificial intelligence"),
    "nlp": ("nlp", "natural language", "language model", "information retrieval", "text"),
    "systems_security": ("systems", "distributed", "security", "cyber", "cloud", "network"),
    "hci": ("hci", "human-computer", "interaction", "ux", "education", "edtech"),
    "bio_health": ("bio", "health", "clinical", "genomics", "medical"),
    "data_science": ("data science", "economics", "social", "causal", "statistics"),
}

_EXPERIENCE_SCORES: dict[str, int] = {
    "none": 25,
    "beginner": 45,
    "intermediate": 70,
    "experienced": 90,
}

_LIMITATIONS_NOTE = (
    "These scores are deterministic, preference-weighted indicators derived from your "
    "assessment responses and academic profile. They are intended for research direction "
    "exploration and are not scientifically validated psychometric assessments."
)


def _normalize_scores(
    raw_totals: dict[str, float],
    contributions: dict[str, list[dict[str, object]]],
    labels: dict[str, str],
    scale_cap: float,
) -> list[dict[str, object]]:
    entries: list[dict[str, object]] = []
    for key, label in labels.items():
        raw = raw_totals.get(key, 0.0)
        score = min(100, max(0, round((raw / scale_cap) * 100)))
        entries.append(
            {
                "key": key,
                "label": label,
                "score": score,
                "contributions": contributions.get(key, []),
            }
        )
    entries.sort(key=lambda item: (-int(item["score"]), str(item["label"])))  # type: ignore[arg-type]
    return entries


def _compute_skill_confidence(
    answers: dict[str, object], profile: AcademicProfile | None
) -> dict[str, object]:
    math_rating = answers.get("q_math_comfort")
    coding_rating = answers.get("q_coding_comfort")
    math_comfort = math_rating if isinstance(math_rating, int) else 3
    coding_comfort = coding_rating if isinstance(coding_rating, int) else 3

    exp_level = profile.research_experience_level if profile else "none"
    exp_score = _EXPERIENCE_SCORES.get(exp_level, 25)
    skills_count = len(profile.technical_skills) if profile else 0
    langs_count = len(profile.programming_languages) if profile else 0

    math_pct = round((math_comfort / 5) * 100)
    coding_pct = round((coding_comfort / 5) * 100)
    breadth_bonus = min(100, (skills_count + langs_count) * 12)

    overall = round(
        0.35 * math_pct + 0.35 * coding_pct + 0.20 * exp_score + 0.10 * breadth_bonus
    )

    return {
        "math_comfort": math_comfort,
        "coding_comfort": coding_comfort,
        "experience_level": exp_level,
        "technical_skills_count": skills_count,
        "programming_languages_count": langs_count,
        "overall_confidence": min(100, max(0, overall)),
    }


def analyze_user_interests(
    db: Session, user_id: int, session_id: int | None = None
) -> InterestProfile:
    """Compute and persist an explainable InterestProfile from a completed assessment."""
    stmt = (
        select(AssessmentSession)
        .options(selectinload(AssessmentSession.responses))
        .where(
            AssessmentSession.user_id == user_id,
            AssessmentSession.status == "completed",
        )
    )
    if session_id is not None:
        stmt = stmt.where(AssessmentSession.id == session_id)
    else:
        stmt = stmt.order_by(AssessmentSession.id.desc()).limit(1)

    session = db.scalar(stmt)
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Complete an assessment session before generating an interest profile.",
        )

    profile = get_profile_by_user_id(db, user_id)
    answers = {resp.question_id: resp.answer_value for resp in session.responses}

    domain_raw: dict[str, float] = defaultdict(float)
    dimension_raw: dict[str, float] = defaultdict(float)
    domain_contribs: dict[str, list[dict[str, object]]] = defaultdict(list)
    dimension_contribs: dict[str, list[dict[str, object]]] = defaultdict(list)

    for qid, answer in answers.items():
        question = QUESTION_MAP.get(qid)
        if question is None:
            continue

        if question.question_type == "rating_scale" and isinstance(answer, int):
            weight = round(answer / (question.max_value or 5), 2)
            reason = f"{question.category}: rated {answer}/{question.max_value or 5}"
            if question.rating_target_domain:
                domain_raw[question.rating_target_domain] += weight
                domain_contribs[question.rating_target_domain].append(
                    {"source": f"assessment:{qid}", "reason": reason, "weight": weight}
                )
            if question.rating_target_dimension:
                dimension_raw[question.rating_target_dimension] += weight
                dimension_contribs[question.rating_target_dimension].append(
                    {"source": f"assessment:{qid}", "reason": reason, "weight": weight}
                )
            continue

        selected_ids = answer if isinstance(answer, list) else [answer]
        opt_map = {opt.id: opt for opt in question.options}
        for opt_id in selected_ids:
            opt = opt_map.get(str(opt_id))
            if opt is None:
                continue
            for d_key, w in opt.domain_weights.items():
                domain_raw[d_key] += w
                domain_contribs[d_key].append(
                    {
                        "source": f"assessment:{qid}",
                        "reason": f"Selected '{opt.label}'",
                        "weight": w,
                    }
                )
            for dim_key, w in opt.dimension_weights.items():
                dimension_raw[dim_key] += w
                dimension_contribs[dim_key].append(
                    {
                        "source": f"assessment:{qid}",
                        "reason": f"Selected '{opt.label}'",
                        "weight": w,
                    }
                )

    if profile and profile.preferred_research_domains:
        for pref in profile.preferred_research_domains:
            lowered = pref.lower()
            for d_key, keywords in _DOMAIN_KEYWORDS.items():
                if any(kw in lowered for kw in keywords):
                    domain_raw[d_key] += 0.4
                    domain_contribs[d_key].append(
                        {
                            "source": "academic_profile",
                            "reason": f"Profile preferred domain: '{pref}'",
                            "weight": 0.4,
                        }
                    )

    domain_scores = _normalize_scores(
        domain_raw, domain_contribs, DOMAIN_LABELS, scale_cap=1.8
    )
    dimension_scores = _normalize_scores(
        dimension_raw, dimension_contribs, DIMENSION_LABELS, scale_cap=2.2
    )
    skill_confidence = _compute_skill_confidence(answers, profile)
    top_domains = [
        str(entry["key"]) for entry in domain_scores if int(entry["score"]) > 0  # type: ignore[arg-type]
    ][:3]

    existing = db.scalar(
        select(InterestProfile).where(InterestProfile.session_id == session.id)
    )
    if existing is None:
        interest_profile = InterestProfile(
            user_id=user_id,
            session_id=session.id,
            domain_scores=domain_scores,
            dimension_scores=dimension_scores,
            skill_confidence=skill_confidence,
            top_domains=top_domains,
            limitations_note=_LIMITATIONS_NOTE,
        )
        db.add(interest_profile)
    else:
        existing.domain_scores = domain_scores
        existing.dimension_scores = dimension_scores
        existing.skill_confidence = skill_confidence
        existing.top_domains = top_domains
        existing.limitations_note = _LIMITATIONS_NOTE
        interest_profile = existing

    db.commit()
    db.refresh(interest_profile)
    return interest_profile


def get_latest_interest_profile(db: Session, user_id: int) -> InterestProfile | None:
    """Return the user's most recently generated InterestProfile, if any."""
    return db.scalar(
        select(InterestProfile)
        .where(InterestProfile.user_id == user_id)
        .order_by(InterestProfile.id.desc())
        .limit(1)
    )
