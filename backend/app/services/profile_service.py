from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.academic_profile import AcademicProfile
from app.schemas.profile import AcademicProfileUpsert


def get_profile_by_user_id(db: Session, user_id: int) -> AcademicProfile | None:
    """Return the academic profile for a given user ID, or None if not created."""
    return db.scalar(
        select(AcademicProfile).where(AcademicProfile.user_id == user_id)
    )


def upsert_profile(
    db: Session,
    user_id: int,
    payload: AcademicProfileUpsert,
) -> AcademicProfile:
    """Create or update the user's academic profile."""
    profile = get_profile_by_user_id(db, user_id)
    data = payload.model_dump()

    if profile is None:
        profile = AcademicProfile(user_id=user_id, **data)
        db.add(profile)
    else:
        for field_name, value in data.items():
            setattr(profile, field_name, value)

    db.commit()
    db.refresh(profile)
    return profile
