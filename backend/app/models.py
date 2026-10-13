"""The two related resources specified by Issue #5."""

from datetime import datetime
from enum import StrEnum
from uuid import UUID

from sqlalchemy import CheckConstraint, DateTime, Enum, Float, ForeignKey, Index, Text, func, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Classification(StrEnum):
    PHISHING = "Phishing"
    SPAM = "Spam"
    LEGITIMATE = "Legitimate"


class RiskLevel(StrEnum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class User(Base):
    __tablename__ = "users"
    __table_args__ = (CheckConstraint("length(btrim(email)) > 0", name="users_email_not_empty"),)

    id: Mapped[UUID] = mapped_column(primary_key=True, server_default=text("gen_random_uuid()"))
    email: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    analyzed_emails: Mapped[list["AnalyzedEmail"]] = relationship(
        back_populates="user", cascade="all, delete-orphan", passive_deletes=True
    )


Index("users_email_unique", func.lower(func.btrim(User.email)), unique=True)


class AnalyzedEmail(Base):
    __tablename__ = "analyzed_emails"
    __table_args__ = (
        CheckConstraint(
            "length(btrim(raw_content)) > 0", name="analyzed_emails_raw_content_not_empty"
        ),
        CheckConstraint(
            "confidence_score >= 0 AND confidence_score <= 100",
            name="analyzed_emails_confidence_range",
        ),
        CheckConstraint(
            "CASE WHEN jsonb_typeof(threat_indicators) = 'array' "
            "THEN NOT jsonb_path_exists(threat_indicators, "
            "'strict $[*] ? (@.type() != \"string\")') ELSE false END",
            name="analyzed_emails_threat_indicators_array",
        ),
        CheckConstraint(
            "length(btrim(ai_explanation)) > 0", name="analyzed_emails_explanation_not_empty"
        ),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, server_default=text("gen_random_uuid()"))
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    raw_content: Mapped[str] = mapped_column(Text)
    classification_result: Mapped[Classification] = mapped_column(
        Enum(
            Classification,
            name="classification_result",
            values_callable=lambda e: [v.value for v in e],
        )
    )
    confidence_score: Mapped[float] = mapped_column(Float(precision=53))
    risk_level: Mapped[RiskLevel] = mapped_column(
        Enum(RiskLevel, name="risk_level", values_callable=lambda e: [v.value for v in e])
    )
    threat_indicators: Mapped[list[str]] = mapped_column(JSONB, server_default=text("'[]'::jsonb"))
    ai_explanation: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    user: Mapped[User] = relationship(back_populates="analyzed_emails")


Index(
    "analyzed_emails_user_history_idx",
    AnalyzedEmail.user_id,
    AnalyzedEmail.created_at.desc().nulls_last(),
    AnalyzedEmail.id.desc().nulls_last(),
)
