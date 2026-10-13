from typing import Literal

from fastapi import FastAPI
from pydantic import BaseModel, Field


app = FastAPI(
    title="VeriQo API",
    version="0.1.0",
)


# ---------------------------------------------------------
# Request schema
# ---------------------------------------------------------

class AnalysisRequest(BaseModel):
    text: str = Field(
        min_length=1,
        max_length=20_000,
    )


# ---------------------------------------------------------
# Response schema
# ---------------------------------------------------------

class AnalysisResponse(BaseModel):
    classification: Literal[
        "legitimate",
        "spam",
        "phishing",
    ]

    risk_level: Literal[
        "low",
        "medium",
        "high",
    ]

    tactics: list[str]

    recommendations: list[str]


# ---------------------------------------------------------
# Health endpoint
# ---------------------------------------------------------

@app.get("/health")
def health():
    return {
        "status": "ok"
    }


# ---------------------------------------------------------
# Walking-skeleton analysis endpoint
# ---------------------------------------------------------

@app.post(
    "/analyses",
    response_model=AnalysisResponse,
)
def analyze_email(
    request: AnalysisRequest,
):
    """
    Temporary fixture.

    This does NOT call Gemini yet.

    It only proves:

    Chrome Extension
        ->
    FastAPI
        ->
    Chrome Extension
    """

    return AnalysisResponse(
        classification="phishing",

        risk_level="high",

        tactics=[
            "urgency",
            "credential_request",
        ],

        recommendations=[
            "Do not provide credentials.",
            "Verify the sender independently.",
        ],
    )