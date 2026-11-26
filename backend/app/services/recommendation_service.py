from fastapi import HTTPException, status
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.academic_profile import AcademicProfile
from app.models.interest_profile import InterestProfile
from app.models.recommendation import RecommendationSet, TopicBookmark, TopicFeedback
from app.schemas.recommendation import (
    BookmarkResponse,
    RecommendationSetResponse,
    TopicRecommendation,
)
from app.services.interest_analysis_service import DOMAIN_LABELS, get_latest_interest_profile
from app.services.profile_service import get_profile_by_user_id
from app.services.topic_catalog import TOPIC_CATALOG, TOPIC_MAP, ResearchTopic

_EXPERIENCE_ORDER: dict[str, int] = {
    "none": 0,
    "beginner": 1,
    "intermediate": 2,
    "experienced": 3,
}

_METHODOLOGY_NOTE = (
    "AI-assisted hybrid recommendations combining weighted interest alignment, skill and "
    "time feasibility, methodology fit, and TF-IDF semantic similarity against your academic "
    "profile. Scores are exploratory decision-support indicators rather than validated "
    "scientific measurements."
)


def _weighted_score(score_map: dict[str, int], weights: dict[str, float]) -> int:
    total_weight = sum(weights.values())
    if total_weight <= 0:
        return 0
    weighted = sum(score_map.get(key, 0) * weight for key, weight in weights.items()) / total_weight
    return min(100, max(0, round(weighted)))


def _compute_feasibility(
    topic: ResearchTopic,
    profile: AcademicProfile | None,
    skill_confidence: dict[str, object],
) -> int:
    user_exp = (
        profile.research_experience_level
        if profile is not None
        else str(skill_confidence.get("experience_level", "none"))
    )
    user_rank = _EXPERIENCE_ORDER.get(user_exp, 0)
    req_rank = _EXPERIENCE_ORDER.get(topic.min_experience_level, 0)

    if user_rank >= req_rank:
        exp_fit = 100
    elif req_rank - user_rank == 1:
        exp_fit = 65
    else:
        exp_fit = 30

    weekly_hours = profile.weekly_hours_available if profile is not None else None
    if weekly_hours is None:
        hours_fit = 75
    elif weekly_hours >= topic.min_weekly_hours:
        hours_fit = 100
    else:
        hours_fit = max(30, round((weekly_hours / max(1, topic.min_weekly_hours)) * 100))

    raw_conf = skill_confidence.get("overall_confidence", 50)
    overall_conf = int(raw_conf) if isinstance(raw_conf, (int, float)) else 50
    return min(100, max(0, round(0.45 * exp_fit + 0.30 * hours_fit + 0.25 * overall_conf)))


def _build_user_query(profile: AcademicProfile | None, interest_profile: InterestProfile) -> str:
    parts: list[str] = []
    if profile is not None:
        if profile.degree_program:
            parts.append(profile.degree_program)
        if profile.academic_background:
            parts.append(profile.academic_background)
        if profile.technical_skills:
            parts.append(" ".join(profile.technical_skills))
        if profile.programming_languages:
            parts.append(" ".join(profile.programming_languages))
        if profile.preferred_research_domains:
            parts.append(" ".join(profile.preferred_research_domains))
        if profile.research_experience_summary:
            parts.append(profile.research_experience_summary)
        if profile.career_goals:
            parts.append(profile.career_goals)

    for domain_key in interest_profile.top_domains:
        label = DOMAIN_LABELS.get(domain_key)
        if label:
            parts.append(label)

    return " ".join(parts).strip()


def _compute_semantic_similarities(
    topics: tuple[ResearchTopic, ...],
    profile: AcademicProfile | None,
    interest_profile: InterestProfile,
) -> list[int]:
    user_query = _build_user_query(profile, interest_profile)
    if not user_query:
        return [0] * len(topics)

    topic_docs = [
        f"{topic.title} {topic.description} {' '.join(topic.keywords)}" for topic in topics
    ]
    vectorizer = TfidfVectorizer(stop_words="english")
    matrix = vectorizer.fit_transform(topic_docs + [user_query])
    similarities = cosine_similarity(matrix[-1:], matrix[:-1])[0]
    return [min(100, max(0, round(float(sim) * 250))) for sim in similarities]


def _build_explanation(
    interest: int,
    feasibility: int,
    methodology: int,
    semantic: int,
) -> str:
    return (
        f"Interest alignment {interest}/100, skill feasibility {feasibility}/100, "
        f"methodology fit {methodology}/100, and profile text similarity {semantic}/100."
    )


def _hydrate_recommendation_set(
    db: Session,
    user_id: int,
    rec_set: RecommendationSet,
) -> RecommendationSetResponse:
    bookmarked_ids = set(
        db.scalars(select(TopicBookmark.topic_id).where(TopicBookmark.user_id == user_id)).all()
    )
    feedback_rows = db.scalars(
        select(TopicFeedback).where(TopicFeedback.user_id == user_id)
    ).all()
    ratings_by_topic = {row.topic_id: row.rating for row in feedback_rows}

    hydrated_results: list[TopicRecommendation] = []
    for item in rec_set.topic_results:
        topic_id = str(item["id"])
        enriched = {
            **item,
            "is_bookmarked": topic_id in bookmarked_ids,
            "user_rating": ratings_by_topic.get(topic_id),
        }
        hydrated_results.append(TopicRecommendation.model_validate(enriched))

    return RecommendationSetResponse(
        id=rec_set.id,
        user_id=rec_set.user_id,
        interest_profile_id=rec_set.interest_profile_id,
        methodology_note=rec_set.methodology_note,
        results=hydrated_results,
        created_at=rec_set.created_at,
        updated_at=rec_set.updated_at,
    )


def generate_recommendations(db: Session, user_id: int) -> RecommendationSetResponse:
    """Compute, persist, and return ranked hybrid topic recommendations for a user."""
    interest_profile = get_latest_interest_profile(db, user_id)
    if interest_profile is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Generate an interest profile before requesting topic recommendations.",
        )

    academic_profile = get_profile_by_user_id(db, user_id)
    domain_score_map = {
        str(entry["key"]): int(entry["score"]) for entry in interest_profile.domain_scores
    }
    dimension_score_map = {
        str(entry["key"]): int(entry["score"]) for entry in interest_profile.dimension_scores
    }

    semantic_scores = _compute_semantic_similarities(
        TOPIC_CATALOG, academic_profile, interest_profile
    )

    ranked_topics: list[dict[str, object]] = []
    for topic, semantic in zip(TOPIC_CATALOG, semantic_scores):
        interest = _weighted_score(domain_score_map, topic.domain_weights)
        feasibility = _compute_feasibility(
            topic, academic_profile, interest_profile.skill_confidence
        )
        methodology = _weighted_score(dimension_score_map, topic.dimension_weights)
        hybrid_score = min(
            100,
            max(
                0,
                round(0.40 * interest + 0.20 * feasibility + 0.20 * methodology + 0.20 * semantic),
            ),
        )
        ranked_topics.append(
            {
                "id": topic.id,
                "title": topic.title,
                "description": topic.description,
                "keywords": list(topic.keywords),
                "domain_tags": list(topic.domain_tags),
                "methodology_tags": list(topic.methodology_tags),
                "min_experience_level": topic.min_experience_level,
                "min_weekly_hours": topic.min_weekly_hours,
                "hybrid_score": hybrid_score,
                "score_breakdown": {
                    "interest_alignment": interest,
                    "skill_feasibility": feasibility,
                    "methodology_fit": methodology,
                    "semantic_similarity": semantic,
                    "explanation": _build_explanation(interest, feasibility, methodology, semantic),
                },
            }
        )

    ranked_topics.sort(
        key=lambda item: (
            -int(item["hybrid_score"]),  # type: ignore[arg-type]
            -int(item["score_breakdown"]["interest_alignment"]),  # type: ignore[index]
            str(item["title"]),
        )
    )

    existing = db.scalar(
        select(RecommendationSet).where(
            RecommendationSet.interest_profile_id == interest_profile.id
        )
    )
    if existing is None:
        rec_set = RecommendationSet(
            user_id=user_id,
            interest_profile_id=interest_profile.id,
            topic_results=ranked_topics,
            methodology_note=_METHODOLOGY_NOTE,
        )
        db.add(rec_set)
    else:
        existing.topic_results = ranked_topics
        existing.methodology_note = _METHODOLOGY_NOTE
        rec_set = existing

    db.commit()
    db.refresh(rec_set)
    return _hydrate_recommendation_set(db, user_id, rec_set)


def get_latest_recommendations(db: Session, user_id: int) -> RecommendationSetResponse:
    """Return the user's most recent recommendation set, hydrated with bookmarks and ratings."""
    rec_set = db.scalar(
        select(RecommendationSet)
        .where(RecommendationSet.user_id == user_id)
        .order_by(RecommendationSet.id.desc())
        .limit(1)
    )
    if rec_set is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No topic recommendations have been generated yet.",
        )
    return _hydrate_recommendation_set(db, user_id, rec_set)


def _require_catalog_topic(topic_id: str) -> ResearchTopic:
    topic = TOPIC_MAP.get(topic_id)
    if topic is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Unknown research topic '{topic_id}'.",
        )
    return topic


def add_bookmark(db: Session, user_id: int, topic_id: str) -> BookmarkResponse:
    """Bookmark a curated research topic for the authenticated user."""
    topic = _require_catalog_topic(topic_id)
    existing = db.scalar(
        select(TopicBookmark).where(
            TopicBookmark.user_id == user_id,
            TopicBookmark.topic_id == topic_id,
        )
    )
    if existing is None:
        bookmark = TopicBookmark(user_id=user_id, topic_id=topic_id)
        db.add(bookmark)
        db.commit()
        db.refresh(bookmark)
    else:
        bookmark = existing

    return BookmarkResponse(
        id=bookmark.id,
        topic_id=bookmark.topic_id,
        title=topic.title,
        domain_tags=list(topic.domain_tags),
        created_at=bookmark.created_at,
    )


def remove_bookmark(db: Session, user_id: int, topic_id: str) -> None:
    """Remove a topic bookmark for the authenticated user."""
    bookmark = db.scalar(
        select(TopicBookmark).where(
            TopicBookmark.user_id == user_id,
            TopicBookmark.topic_id == topic_id,
        )
    )
    if bookmark is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bookmark for topic '{topic_id}' not found.",
        )
    db.delete(bookmark)
    db.commit()


def list_bookmarks(db: Session, user_id: int) -> list[BookmarkResponse]:
    """List all bookmarked topics for the authenticated user."""
    rows = db.scalars(
        select(TopicBookmark)
        .where(TopicBookmark.user_id == user_id)
        .order_by(TopicBookmark.created_at.desc())
    ).all()

    results: list[BookmarkResponse] = []
    for row in rows:
        topic = TOPIC_MAP.get(row.topic_id)
        if topic is None:
            continue
        results.append(
            BookmarkResponse(
                id=row.id,
                topic_id=row.topic_id,
                title=topic.title,
                domain_tags=list(topic.domain_tags),
                created_at=row.created_at,
            )
        )
    return results


def upsert_feedback(
    db: Session,
    user_id: int,
    topic_id: str,
    rating: int,
    comment: str | None,
) -> TopicFeedback:
    """Create or update relevance feedback for a curated research topic."""
    _require_catalog_topic(topic_id)
    cleaned_comment = comment.strip() if comment else None

    existing = db.scalar(
        select(TopicFeedback).where(
            TopicFeedback.user_id == user_id,
            TopicFeedback.topic_id == topic_id,
        )
    )
    if existing is None:
        feedback = TopicFeedback(
            user_id=user_id,
            topic_id=topic_id,
            rating=rating,
            comment=cleaned_comment,
        )
        db.add(feedback)
    else:
        existing.rating = rating
        existing.comment = cleaned_comment
        feedback = existing

    db.commit()
    db.refresh(feedback)
    return feedback
