import os

from dotenv import load_dotenv
from google import genai


load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY is not configured in the .env file."
    )


client = genai.Client(
    api_key=GEMINI_API_KEY
)


MODEL_NAME = "gemini-3.6-flash"


def ask_llm(prompt: str) -> str:

    try:

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )

        if not response.text:
            raise RuntimeError(
                "Gemini returned an empty response."
            )

        return response.text

    except Exception as e:

        error_text = str(e)

        # -----------------------------------------
        # Gemini quota / rate limit
        # -----------------------------------------

        if (
            "429" in error_text
            or "RESOURCE_EXHAUSTED" in error_text
            or "quota" in error_text.lower()
        ):

            raise RuntimeError(
                "GEMINI_QUOTA_EXCEEDED"
            ) from e

        # -----------------------------------------
        # Other Gemini errors
        # -----------------------------------------

        raise RuntimeError(
            f"Gemini API error: {error_text}"
        ) from e