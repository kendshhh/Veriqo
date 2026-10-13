"""Create users and their analyzed emails.

Revision ID: 0001
Revises: None
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None

classification = postgresql.ENUM(
    "Phishing", "Spam", "Legitimate", name="classification_result", create_type=False
)
risk = postgresql.ENUM("Low", "Medium", "High", "Critical", name="risk_level", create_type=False)


def upgrade() -> None:
    classification.create(op.get_bind(), checkfirst=False)
    risk.create(op.get_bind(), checkfirst=False)
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("email", sa.Text(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint("length(btrim(email)) > 0", name="users_email_not_empty"),
    )
    op.create_index("users_email_unique", "users", [sa.text("lower(btrim(email))")], unique=True)
    op.create_table(
        "analyzed_emails",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("raw_content", sa.Text(), nullable=False),
        sa.Column("classification_result", classification, nullable=False),
        sa.Column("confidence_score", sa.Float(precision=53), nullable=False),
        sa.Column("risk_level", risk, nullable=False),
        sa.Column(
            "threat_indicators",
            postgresql.JSONB(),
            server_default=sa.text("'[]'::jsonb"),
            nullable=False,
        ),
        sa.Column("ai_explanation", sa.Text(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.CheckConstraint(
            "length(btrim(raw_content)) > 0", name="analyzed_emails_raw_content_not_empty"
        ),
        sa.CheckConstraint(
            "confidence_score >= 0 AND confidence_score <= 100",
            name="analyzed_emails_confidence_range",
        ),
        sa.CheckConstraint(
            "CASE WHEN jsonb_typeof(threat_indicators) = 'array' "
            "THEN NOT jsonb_path_exists(threat_indicators, "
            "'strict $[*] ? (@.type() != \"string\")') ELSE false END",
            name="analyzed_emails_threat_indicators_array",
        ),
        sa.CheckConstraint(
            "length(btrim(ai_explanation)) > 0", name="analyzed_emails_explanation_not_empty"
        ),
    )
    op.create_index(
        "analyzed_emails_user_history_idx",
        "analyzed_emails",
        ["user_id", sa.text("created_at DESC NULLS LAST"), sa.text("id DESC NULLS LAST")],
    )


def downgrade() -> None:
    op.drop_table("analyzed_emails")
    op.drop_table("users")
    risk.drop(op.get_bind(), checkfirst=False)
    classification.drop(op.get_bind(), checkfirst=False)
