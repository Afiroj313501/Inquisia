from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.profile import AcademicProfileResponse, AcademicProfileUpsert
from app.services.profile_service import get_profile_by_user_id, upsert_profile

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("", response_model=AcademicProfileResponse)
def read_my_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AcademicProfileResponse:
    """Retrieve the authenticated user's academic profile."""
    profile = get_profile_by_user_id(db, current_user.id)
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Academic profile has not been created yet.",
        )
    return AcademicProfileResponse.model_validate(profile)


@router.put("", response_model=AcademicProfileResponse)
def upsert_my_profile(
    payload: AcademicProfileUpsert,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AcademicProfileResponse:
    """Create or update the authenticated user's academic profile."""
    profile = upsert_profile(db, current_user.id, payload)
    return AcademicProfileResponse.model_validate(profile)
