from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.interest import (
    AnalyzeInterestRequest,
    InterestProfileResponse,
    NicheSummaryResponse,
)
from app.services.brief_service import generate_niche_summary, get_cached_niche_summary
from app.services.interest_analysis_service import (
    analyze_user_interests,
    get_latest_interest_profile,
)

router = APIRouter(prefix="/interests", tags=["interests"])


@router.post("/analyze", response_model=InterestProfileResponse)
def analyze_interests(
    payload: AnalyzeInterestRequest | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> InterestProfileResponse:
    """Generate an explainable interest profile from a completed assessment session."""
    target_session_id = payload.session_id if payload is not None else None
    profile = analyze_user_interests(db, current_user.id, session_id=target_session_id)
    return InterestProfileResponse.model_validate(profile)


@router.get("/niche-summary", response_model=NicheSummaryResponse)
def read_cached_niche_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> NicheSummaryResponse:
    """Retrieve the cached AI interdisciplinary niche summary for the latest interest profile."""
    return get_cached_niche_summary(db, current_user.id)


@router.post("/niche-summary", response_model=NicheSummaryResponse)
def create_niche_summary(
    refresh: bool = Query(default=False),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> NicheSummaryResponse:
    """Generate (or return cached) Gemini interdisciplinary niche summary."""
    return generate_niche_summary(db, current_user.id, refresh=refresh)


@router.get("/latest", response_model=InterestProfileResponse)
def read_latest_interest_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> InterestProfileResponse:
    """Retrieve the authenticated user's most recent explainable interest profile."""
    profile = get_latest_interest_profile(db, current_user.id)
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No interest profile has been generated yet.",
        )
    return InterestProfileResponse.model_validate(profile)


@router.get("/niche-summary", response_model=NicheSummaryResponse)
def read_cached_niche_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> NicheSummaryResponse:
    """Retrieve the cached AI interdisciplinary niche summary for the latest interest profile."""
    return get_cached_niche_summary(db, current_user.id)


@router.post("/niche-summary", response_model=NicheSummaryResponse)
def create_niche_summary(
    refresh: bool = Query(default=False),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> NicheSummaryResponse:
    """Generate (or return cached) Gemini interdisciplinary niche summary."""
    return generate_niche_summary(db, current_user.id, refresh=refresh)
