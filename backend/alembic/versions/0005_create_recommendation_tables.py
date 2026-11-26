"""create recommendation tables

Revision ID: 0005_create_recommendations
Revises: 0004_create_interest_profiles
Create Date: 2026-11-27 00:56:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0005_create_recommendations"
down_revision: Union[str, None] = "0004_create_interest_profiles"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "recommendation_sets",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("interest_profile_id", sa.Integer(), nullable=False),
        sa.Column("topic_results", sa.JSON(), nullable=False),
        sa.Column("methodology_note", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["interest_profile_id"], ["interest_profiles.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_recommendation_sets_id"), "recommendation_sets", ["id"], unique=False)
    op.create_index(
        op.f("ix_recommendation_sets_interest_profile_id"),
        "recommendation_sets",
        ["interest_profile_id"],
        unique=True,
    )
    op.create_index(
        op.f("ix_recommendation_sets_user_id"), "recommendation_sets", ["user_id"], unique=False
    )

    op.create_table(
        "topic_bookmarks",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("topic_id", sa.String(length=80), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "topic_id", name="uq_topic_bookmarks_user_topic"),
    )
    op.create_index(op.f("ix_topic_bookmarks_id"), "topic_bookmarks", ["id"], unique=False)
    op.create_index(
        op.f("ix_topic_bookmarks_topic_id"), "topic_bookmarks", ["topic_id"], unique=False
    )
    op.create_index(
        op.f("ix_topic_bookmarks_user_id"), "topic_bookmarks", ["user_id"], unique=False
    )

    op.create_table(
        "topic_feedbacks",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("topic_id", sa.String(length=80), nullable=False),
        sa.Column("rating", sa.Integer(), nullable=False),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "topic_id", name="uq_topic_feedbacks_user_topic"),
    )
    op.create_index(op.f("ix_topic_feedbacks_id"), "topic_feedbacks", ["id"], unique=False)
    op.create_index(
        op.f("ix_topic_feedbacks_topic_id"), "topic_feedbacks", ["topic_id"], unique=False
    )
    op.create_index(
        op.f("ix_topic_feedbacks_user_id"), "topic_feedbacks", ["user_id"], unique=False
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_topic_feedbacks_user_id"), table_name="topic_feedbacks")
    op.drop_index(op.f("ix_topic_feedbacks_topic_id"), table_name="topic_feedbacks")
    op.drop_index(op.f("ix_topic_feedbacks_id"), table_name="topic_feedbacks")
    op.drop_table("topic_feedbacks")

    op.drop_index(op.f("ix_topic_bookmarks_user_id"), table_name="topic_bookmarks")
    op.drop_index(op.f("ix_topic_bookmarks_topic_id"), table_name="topic_bookmarks")
    op.drop_index(op.f("ix_topic_bookmarks_id"), table_name="topic_bookmarks")
    op.drop_table("topic_bookmarks")

    op.drop_index(op.f("ix_recommendation_sets_user_id"), table_name="recommendation_sets")
    op.drop_index(
        op.f("ix_recommendation_sets_interest_profile_id"), table_name="recommendation_sets"
    )
    op.drop_index(op.f("ix_recommendation_sets_id"), table_name="recommendation_sets")
    op.drop_table("recommendation_sets")
