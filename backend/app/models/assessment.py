from datetime import datetime, timezone
from typing import Any
from sqlalchemy import DateTime, ForeignKey, JSON, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class AssessmentSession(Base):
    """Adaptive research interest assessment session for a user."""

    __tablename__ = "assessment_sessions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    status: Mapped[str] = mapped_column(String(24), default="in_progress", nullable=False)
    current_question_id: Mapped[str | None] = mapped_column(String(80), nullable=True)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utc_now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utc_now, onupdate=_utc_now, nullable=False
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    user = relationship("User", back_populates="assessment_sessions")
    responses = relationship(
        "AssessmentResponse",
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="AssessmentResponse.id",
    )


class AssessmentResponse(Base):
    """Individual question response within an assessment session."""

    __tablename__ = "assessment_responses"
    __table_args__ = (
        UniqueConstraint("session_id", "question_id", name="uq_assessment_session_question"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    session_id: Mapped[int] = mapped_column(
        ForeignKey("assessment_sessions.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    question_id: Mapped[str] = mapped_column(String(80), nullable=False)
    answer_value: Mapped[Any] = mapped_column(JSON, nullable=False)
    answered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utc_now, onupdate=_utc_now, nullable=False
    )

    session = relationship("AssessmentSession", back_populates="responses")
