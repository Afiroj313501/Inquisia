from datetime import datetime, timezone
from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class SavedPaper(Base):
    """Real academic paper saved by a user from OpenAlex discovery."""

    __tablename__ = "saved_papers"
    __table_args__ = (
        UniqueConstraint("user_id", "openalex_id", name="uq_saved_papers_user_openalex"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    openalex_id: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    topic_id: Mapped[str | None] = mapped_column(String(80), index=True, nullable=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    authors: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    publication_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    venue: Mapped[str | None] = mapped_column(String(255), nullable=True)
    cited_by_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    doi: Mapped[str | None] = mapped_column(String(255), nullable=True)
    url: Mapped[str | None] = mapped_column(Text, nullable=True)
    open_access_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    abstract: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utc_now, nullable=False
    )

    user = relationship("User", back_populates="saved_papers")
