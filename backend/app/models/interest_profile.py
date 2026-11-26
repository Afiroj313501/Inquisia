from datetime import datetime, timezone
from typing import Any
from sqlalchemy import DateTime, ForeignKey, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class InterestProfile(Base):
    """Explainable research interest profile derived from an assessment session."""

    __tablename__ = "interest_profiles"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    session_id: Mapped[int] = mapped_column(
        ForeignKey("assessment_sessions.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False,
    )
    domain_scores: Mapped[list[dict[str, Any]]] = mapped_column(JSON, nullable=False)
    dimension_scores: Mapped[list[dict[str, Any]]] = mapped_column(JSON, nullable=False)
    skill_confidence: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    top_domains: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    limitations_note: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utc_now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utc_now, onupdate=_utc_now, nullable=False
    )

    user = relationship("User", back_populates="interest_profiles")
