"""Explicit, repeatable synthetic fixtures; never executed during migrations or startup."""

from uuid import UUID

from sqlalchemy import Engine
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import SQLAlchemyError

from app.database import make_engine
from app.models import AnalyzedEmail, User

DEMO_USER_ID = UUID("11111111-1111-4111-8111-111111111111")
DEMO_EMAILS = [
    {
        "id": UUID("22222222-2222-4222-8222-222222222221"),
        "user_id": DEMO_USER_ID,
        "raw_content": "Subject: Verify your account\n\nAct now at https://login.example.invalid.",
        "classification_result": "Phishing",
        "confidence_score": 97.5,
        "risk_level": "Critical",
        "threat_indicators": ["urgency", "fake domain"],
        "ai_explanation": (
            "Synthetic example: urgency and an unrelated login domain suggest phishing."
        ),
    },
    {
        "id": UUID("22222222-2222-4222-8222-222222222222"),
        "user_id": DEMO_USER_ID,
        "raw_content": (
            "Subject: Limited sale\n\nUnrequested promotional offers from example.invalid."
        ),
        "classification_result": "Spam",
        "confidence_score": 89.0,
        "risk_level": "Medium",
        "threat_indicators": ["unsolicited promotion"],
        "ai_explanation": "Synthetic example: unsolicited advertising with no credential request.",
    },
    {
        "id": UUID("22222222-2222-4222-8222-222222222223"),
        "user_id": DEMO_USER_ID,
        "raw_content": "Subject: Meeting reminder\n\nOur agreed project meeting starts at 10 AM.",
        "classification_result": "Legitimate",
        "confidence_score": 99.0,
        "risk_level": "Low",
        "threat_indicators": [],
        "ai_explanation": "Synthetic example: an expected reminder without suspicious requests.",
    },
]


def seed_database(engine: Engine) -> None:
    with engine.begin() as connection:
        connection.execute(
            insert(User)
            .values(id=DEMO_USER_ID, email="demo@example.invalid")
            .on_conflict_do_nothing(index_elements=[User.id])
        )
        connection.execute(
            insert(AnalyzedEmail)
            .values(DEMO_EMAILS)
            .on_conflict_do_nothing(index_elements=[AnalyzedEmail.id])
        )


def main() -> int:
    engine = None
    try:
        engine = make_engine()
        seed_database(engine)
        print(f"Synthetic demo records ready for user {DEMO_USER_ID}.")
        return 0
    except (ValueError, SQLAlchemyError):
        print(
            "Seeding failed. Check DATABASE_URL, connectivity, and run alembic upgrade head first."
        )
        return 1
    finally:
        if engine is not None:
            engine.dispose()


if __name__ == "__main__":
    raise SystemExit(main())
