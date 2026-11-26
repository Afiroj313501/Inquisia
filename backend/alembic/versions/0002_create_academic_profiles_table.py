"""create academic_profiles table

Revision ID: 0002_create_academic_profiles
Revises: 0001_create_users
Create Date: 2026-11-27 00:32:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0002_create_academic_profiles"
down_revision: Union[str, None] = "0001_create_users"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "academic_profiles",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("education_level", sa.String(length=40), nullable=False),
        sa.Column("degree_program", sa.String(length=160), nullable=False),
        sa.Column("academic_background", sa.Text(), nullable=True),
        sa.Column("technical_skills", sa.JSON(), nullable=False),
        sa.Column("programming_languages", sa.JSON(), nullable=False),
        sa.Column("preferred_research_domains", sa.JSON(), nullable=False),
        sa.Column("research_experience_level", sa.String(length=40), nullable=False),
        sa.Column("research_experience_summary", sa.Text(), nullable=True),
        sa.Column("career_goals", sa.Text(), nullable=True),
        sa.Column("weekly_hours_available", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_academic_profiles_id"), "academic_profiles", ["id"], unique=False)
    op.create_index(
        op.f("ix_academic_profiles_user_id"), "academic_profiles", ["user_id"], unique=True
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_academic_profiles_user_id"), table_name="academic_profiles")
    op.drop_index(op.f("ix_academic_profiles_id"), table_name="academic_profiles")
    op.drop_table("academic_profiles")
