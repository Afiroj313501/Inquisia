from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.recommendation import (
    BookmarkCreateRequest,
    BookmarkResponse,
    FeedbackResponse,
    FeedbackUpsertRequest,
    RecommendationSetResponse,
    ResearchBriefResponse,
)
from app.services.brief_service import generate_topic_brief, get_cached_topic_brief
from app.services.recommendation_service import (
    add_bookmark,
    generate_recommendations,
    get_latest_recommendations,
    list_bookmarks,
    remove_bookmark,
    upsert_feedback,
)

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.post("/generate", response_model=RecommendationSetResponse)
def generate_topic_recommendations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> RecommendationSetResponse:
    """Generate and persist hybrid research topic recommendations from the latest interest profile."""
    return generate_recommendations(db, current_user.id)


@router.get("/latest", response_model=RecommendationSetResponse)
def read_latest_recommendations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> RecommendationSetResponse:
    """Retrieve the authenticated user's latest generated topic recommendations."""
    return get_latest_recommendations(db, current_user.id)


@router.get("/bookmarks", response_model=list[BookmarkResponse])
def read_bookmarks(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[BookmarkResponse]:
    """List all research topics bookmarked by the authenticated user."""
    return list_bookmarks(db, current_user.id)


@router.post(
    "/bookmarks",
    response_model=BookmarkResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_bookmark(
    payload: BookmarkCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> BookmarkResponse:
    """Bookmark a research topic from the catalog."""
    return add_bookmark(db, current_user.id, payload.topic_id)


@router.delete("/bookmarks/{topic_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_bookmark(
    topic_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    """Remove a bookmarked research topic."""
    remove_bookmark(db, current_user.id, topic_id)


@router.put("/feedback/{topic_id}", response_model=FeedbackResponse)
def submit_topic_feedback(
    topic_id: str,
    payload: FeedbackUpsertRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> FeedbackResponse:
    """Create or update a relevance rating and optional comment for a research topic."""
    feedback = upsert_feedback(
        db,
        user_id=current_user.id,
        topic_id=topic_id,
        rating=payload.rating,
        comment=payload.comment,
    )
    return FeedbackResponse.model_validate(feedback)


@router.get("/{topic_id}/brief", response_model=ResearchBriefResponse)
def read_cached_topic_brief(
    topic_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ResearchBriefResponse:
    """Retrieve a cached AI research brief for a topic, if previously generated."""
    return get_cached_topic_brief(db, current_user.id, topic_id)


@router.post("/{topic_id}/brief", response_model=ResearchBriefResponse)
def create_topic_brief(
    topic_id: str,
    refresh: bool = Query(default=False),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ResearchBriefResponse:
    """Generate (or return cached) AI-assisted exploratory research brief for a topic."""
    return generate_topic_brief(db, current_user.id, topic_id, refresh=refresh)
