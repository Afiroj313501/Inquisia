from datetime import datetime, timezone
from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    """Registered user account."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(120), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utc_now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utc_now, onupdate=_utc_now, nullable=False
    )

    academic_profile = relationship(
        "AcademicProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    assessment_sessions = relationship(
        "AssessmentSession",
        back_populates="user",
        cascade="all, delete-orphan",
        order_by="AssessmentSession.id.desc()",
    )
    interest_profiles = relationship(
        "InterestProfile",
        back_populates="user",
        cascade="all, delete-orphan",
        order_by="InterestProfile.id.desc()",
    )
    recommendation_sets = relationship(
        "RecommendationSet",
        back_populates="user",
        cascade="all, delete-orphan",
        order_by="RecommendationSet.id.desc()",
    )
    topic_bookmarks = relationship(
        "TopicBookmark",
        back_populates="user",
        cascade="all, delete-orphan",
        order_by="TopicBookmark.created_at.desc()",
    )
    topic_feedbacks = relationship(
        "TopicFeedback",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    saved_papers = relationship(
        "SavedPaper",
        back_populates="user",
        cascade="all, delete-orphan",
        order_by="SavedPaper.created_at.desc()",
    )
    ai_artifacts = relationship(
        "AiArtifact",
        back_populates="user",
        cascade="all, delete-orphan",
        order_by="AiArtifact.updated_at.desc()",
    )
