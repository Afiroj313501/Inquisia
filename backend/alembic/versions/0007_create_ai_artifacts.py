"""create ai_artifacts table

Revision ID: 0007_create_ai_artifacts
Revises: 0006_create_saved_papers
Create Date: 2026-11-28 23:41:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0007_create_ai_artifacts"
down_revision: Union[str, None] = "0006_create_saved_papers"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "ai_artifacts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("artifact_type", sa.String(length=40), nullable=False),
        sa.Column("target_key", sa.String(length=120), nullable=False),
        sa.Column("model", sa.String(length=80), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "user_id",
            "artifact_type",
            "target_key",
            name="uq_ai_artifacts_user_type_key",
        ),
    )
    op.create_index(
        op.f("ix_ai_artifacts_artifact_type"), "ai_artifacts", ["artifact_type"], unique=False
    )
    op.create_index(op.f("ix_ai_artifacts_id"), "ai_artifacts", ["id"], unique=False)
    op.create_index(
        op.f("ix_ai_artifacts_target_key"), "ai_artifacts", ["target_key"], unique=False
    )
    op.create_index(op.f("ix_ai_artifacts_user_id"), "ai_artifacts", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_ai_artifacts_user_id"), table_name="ai_artifacts")
    op.drop_index(op.f("ix_ai_artifacts_target_key"), table_name="ai_artifacts")
    op.drop_index(op.f("ix_ai_artifacts_id"), table_name="ai_artifacts")
    op.drop_index(op.f("ix_ai_artifacts_artifact_type"), table_name="ai_artifacts")
    op.drop_table("ai_artifacts")
