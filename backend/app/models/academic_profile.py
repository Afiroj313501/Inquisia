from datetime import datetime, timezone
from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class AcademicProfile(Base):
    """Academic background, skills, and research goals for a user."""

    __tablename__ = "academic_profiles"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False,
    )
    education_level: Mapped[str] = mapped_column(String(40), nullable=False)
    degree_program: Mapped[str] = mapped_column(String(160), nullable=False)
    academic_background: Mapped[str | None] = mapped_column(Text, nullable=True)
    technical_skills: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    programming_languages: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    preferred_research_domains: Mapped[list[str]] = mapped_column(
        JSON, default=list, nullable=False
    )
    research_experience_level: Mapped[str] = mapped_column(String(40), nullable=False)
    research_experience_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    career_goals: Mapped[str | None] = mapped_column(Text, nullable=True)
    weekly_hours_available: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utc_now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utc_now, onupdate=_utc_now, nullable=False
    )

    user = relationship("User", back_populates="academic_profile")
