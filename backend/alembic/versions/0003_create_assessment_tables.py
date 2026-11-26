"""create assessment tables

Revision ID: 0003_create_assessment_tables
Revises: 0002_create_academic_profiles
Create Date: 2026-11-27 00:40:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0003_create_assessment_tables"
down_revision: Union[str, None] = "0002_create_academic_profiles"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "assessment_sessions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=24), nullable=False),
        sa.Column("current_question_id", sa.String(length=80), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_assessment_sessions_id"), "assessment_sessions", ["id"], unique=False)
    op.create_index(
        op.f("ix_assessment_sessions_user_id"), "assessment_sessions", ["user_id"], unique=False
    )

    op.create_table(
        "assessment_responses",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("session_id", sa.Integer(), nullable=False),
        sa.Column("question_id", sa.String(length=80), nullable=False),
        sa.Column("answer_value", sa.JSON(), nullable=False),
        sa.Column("answered_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["session_id"], ["assessment_sessions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("session_id", "question_id", name="uq_assessment_session_question"),
    )
    op.create_index(op.f("ix_assessment_responses_id"), "assessment_responses", ["id"], unique=False)
    op.create_index(
        op.f("ix_assessment_responses_session_id"),
        "assessment_responses",
        ["session_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_assessment_responses_session_id"), table_name="assessment_responses")
    op.drop_index(op.f("ix_assessment_responses_id"), table_name="assessment_responses")
    op.drop_table("assessment_responses")
    op.drop_index(op.f("ix_assessment_sessions_user_id"), table_name="assessment_sessions")
    op.drop_index(op.f("ix_assessment_sessions_id"), table_name="assessment_sessions")
    op.drop_table("assessment_sessions")
