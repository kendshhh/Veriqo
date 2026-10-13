import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai


# Explicitly load backend/.env
ENV_PATH = Path(__file__).with_name(".env")
load_dotenv(ENV_PATH)


api_key = os.getenv("GEMINI_API_KEY")
model = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")


if not api_key:
    raise RuntimeError(
        "GEMINI_API_KEY was not found in backend/.env"
    )


print("=== VeriQo Gemini Connection Test ===")
print("API key loaded: YES")
print(f"Model: {model}")
print("Sending one request...")


client = genai.Client(api_key=api_key)

response = client.models.generate_content(
    model=model,
    contents=(
        "This is a connection test for VeriQo. "
        "Reply with exactly: VERIQO_GEMINI_OK"
    ),
)


from google.genai import errors

try:
    response = client.models.generate_content(
        model=model,
        contents=(
            "This is a connection test for VeriQo. "
            "Reply with exactly: VERIQO_GEMINI_OK"
        ),
    )

    print()
    print("Gemini request: PASS")
    print("Response:", response.text)
    print()
    print("=== CONNECTION TEST PASSED ===")

except errors.ClientError as exc:
    print()
    print("Gemini request: FAIL")
    print("Client/API configuration error:")
    print(exc)
    raise SystemExit(1)

except errors.ServerError as exc:
    print()
    print("Gemini request: TEMPORARILY UNAVAILABLE")
    print("Gemini reached the server, but the service/model is unavailable.")
    print("Retry later or use another available stable model.")
    print(exc)
    raise SystemExit(2)