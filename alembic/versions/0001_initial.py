"""initial schema

Revision ID: 0001_initial
Revises:
"""
from alembic import op
import sqlalchemy as sa


revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("hashed_password", sa.Text(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "research_sessions",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("question", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="running"),
        sa.Column("answer", sa.Text(), nullable=True),
        sa.Column("sub_questions", sa.JSON(), nullable=False),
        sa.Column("contradictions", sa.JSON(), nullable=False),
        sa.Column("gaps", sa.JSON(), nullable=False),
        sa.Column("iterations", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_index(
        "ix_research_sessions_user_id",
        "research_sessions",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        "ix_research_sessions_status",
        "research_sessions",
        ["status"],
        unique=False,
    )

    op.create_table(
        "research_sources",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("session_id", sa.String(length=36), nullable=False),
        sa.Column("question", sa.Text(), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("url", sa.Text(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("score", sa.Float(), nullable=True),
        sa.Column(
            "credibility_label",
            sa.String(length=50),
            nullable=False,
            server_default="Unknown",
        ),
        sa.Column(
            "credibility_score",
            sa.Float(),
            nullable=False,
            server_default="0.3",
        ),
        sa.ForeignKeyConstraint(
            ["session_id"], ["research_sessions.id"], ondelete="CASCADE"
        ),
    )
    op.create_index(
        "ix_research_sources_session_id",
        "research_sources",
        ["session_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_research_sources_session_id", table_name="research_sources")
    op.drop_table("research_sources")

    op.drop_index("ix_research_sessions_status", table_name="research_sessions")
    op.drop_index("ix_research_sessions_user_id", table_name="research_sessions")
    op.drop_table("research_sessions")

    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
