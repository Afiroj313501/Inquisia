"""create saved_papers table

Revision ID: 0006_create_saved_papers
Revises: 0005_create_recommendation_tables
Create Date: 2026-11-27 01:07:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0006_create_saved_papers"
down_revision: Union[str, None] = "0005_create_recommendation_tables"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "saved_papers",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("openalex_id", sa.String(length=80), nullable=False),
        sa.Column("topic_id", sa.String(length=80), nullable=True),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("authors", sa.JSON(), nullable=False),
        sa.Column("publication_year", sa.Integer(), nullable=True),
        sa.Column("venue", sa.String(length=255), nullable=True),
        sa.Column("cited_by_count", sa.Integer(), nullable=False),
        sa.Column("doi", sa.String(length=255), nullable=True),
        sa.Column("url", sa.Text(), nullable=True),
        sa.Column("open_access_url", sa.Text(), nullable=True),
        sa.Column("abstract", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "openalex_id", name="uq_saved_papers_user_openalex"),
    )
    op.create_index(op.f("ix_saved_papers_id"), "saved_papers", ["id"], unique=False)
    op.create_index(
        op.f("ix_saved_papers_openalex_id"), "saved_papers", ["openalex_id"], unique=False
    )
    op.create_index(op.f("ix_saved_papers_topic_id"), "saved_papers", ["topic_id"], unique=False)
    op.create_index(op.f("ix_saved_papers_user_id"), "saved_papers", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_saved_papers_user_id"), table_name="saved_papers")
    op.drop_index(op.f("ix_saved_papers_topic_id"), table_name="saved_papers")
    op.drop_index(op.f("ix_saved_papers_openalex_id"), table_name="saved_papers")
    op.drop_index(op.f("ix_saved_papers_id"), table_name="saved_papers")
    op.drop_table("saved_papers")
