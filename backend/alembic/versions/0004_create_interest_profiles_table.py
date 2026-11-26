"""create interest_profiles table

Revision ID: 0004_create_interest_profiles
Revises: 0003_create_assessment_tables
Create Date: 2026-11-27 00:48:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0004_create_interest_profiles"
down_revision: Union[str, None] = "0003_create_assessment_tables"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "interest_profiles",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("session_id", sa.Integer(), nullable=False),
        sa.Column("domain_scores", sa.JSON(), nullable=False),
        sa.Column("dimension_scores", sa.JSON(), nullable=False),
        sa.Column("skill_confidence", sa.JSON(), nullable=False),
        sa.Column("top_domains", sa.JSON(), nullable=False),
        sa.Column("limitations_note", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["session_id"], ["assessment_sessions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_interest_profiles_id"), "interest_profiles", ["id"], unique=False)
    op.create_index(
        op.f("ix_interest_profiles_session_id"), "interest_profiles", ["session_id"], unique=True
    )
    op.create_index(
        op.f("ix_interest_profiles_user_id"), "interest_profiles", ["user_id"], unique=False
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_interest_profiles_user_id"), table_name="interest_profiles")
    op.drop_index(op.f("ix_interest_profiles_session_id"), table_name="interest_profiles")
    op.drop_index(op.f("ix_interest_profiles_id"), table_name="interest_profiles")
    op.drop_table("interest_profiles")
