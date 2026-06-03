"""Initial schema

Revision ID: 001
Revises:
Create Date: 2026-06-02
"""
from alembic import op
import sqlalchemy as sa

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "candidates",
        sa.Column("id",         sa.Integer(),    primary_key=True, autoincrement=True),
        sa.Column("name",       sa.String(255),  nullable=False),
        sa.Column("email",      sa.String(255),  nullable=False, unique=True),
        sa.Column("role",       sa.String(255),  nullable=False),
        sa.Column("experience", sa.Integer(),    nullable=False, default=0),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_candidates_email", "candidates", ["email"], unique=True)
    op.create_index("ix_candidates_role",  "candidates", ["role"])

    op.create_table(
        "evaluations",
        sa.Column("id",               sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("candidate_id",     sa.Integer(), sa.ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False),
        sa.Column("communication",    sa.Float(),   nullable=False),
        sa.Column("technical",        sa.Float(),   nullable=False),
        sa.Column("problem_solving",  sa.Float(),   nullable=False),
        sa.Column("ownership",        sa.Float(),   nullable=False),
        sa.Column("final_score",      sa.Float(),   nullable=False, default=0.0),
        sa.Column("comments",         sa.Text(),    nullable=True),
        sa.Column("interviewer_name", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_evaluations_candidate_id", "evaluations", ["candidate_id"])
    op.create_index("ix_evaluations_final_score",  "evaluations", ["final_score"])


def downgrade():
    op.drop_table("evaluations")
    op.drop_table("candidates")
