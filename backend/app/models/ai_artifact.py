from datetime import datetime, timezone
from typing import Any
from sqlalchemy import DateTime, ForeignKey, JSON, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class AiArtifact(Base):
    """Persisted Gemini AI research brief or literature synthesis to conserve quota."""

    __tablename__ = "ai_artifacts"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "artifact_type",
            "target_key",
            name="uq_ai_artifacts_user_type_key",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    artifact_type: Mapped[str] = mapped_column(String(40), index=True, nullable=False)
    target_key: Mapped[str] = mapped_column(String(120), index=True, nullable=False)
    model: Mapped[str] = mapped_column(String(80), nullable=False)
    payload: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utc_now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utc_now, onupdate=_utc_now, nullable=False
    )

    user = relationship("User", back_populates="ai_artifacts")
