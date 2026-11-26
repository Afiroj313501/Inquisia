from datetime import datetime, timezone
from typing import Any
from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class RecommendationSet(Base):
    """Persisted hybrid topic recommendation ranking for an interest profile."""

    __tablename__ = "recommendation_sets"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    interest_profile_id: Mapped[int] = mapped_column(
        ForeignKey("interest_profiles.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False,
    )
    topic_results: Mapped[list[dict[str, Any]]] = mapped_column(JSON, nullable=False)
    methodology_note: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utc_now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utc_now, onupdate=_utc_now, nullable=False
    )

    user = relationship("User", back_populates="recommendation_sets")


class TopicBookmark(Base):
    """User-bookmarked research topic from the curated catalog."""

    __tablename__ = "topic_bookmarks"
    __table_args__ = (
        UniqueConstraint("user_id", "topic_id", name="uq_topic_bookmarks_user_topic"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    topic_id: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utc_now, nullable=False
    )

    user = relationship("User", back_populates="topic_bookmarks")


class TopicFeedback(Base):
    """User relevance rating and optional note on a recommended research topic."""

    __tablename__ = "topic_feedbacks"
    __table_args__ = (
        UniqueConstraint("user_id", "topic_id", name="uq_topic_feedbacks_user_topic"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    topic_id: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utc_now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utc_now, onupdate=_utc_now, nullable=False
    )

    user = relationship("User", back_populates="topic_feedbacks")
