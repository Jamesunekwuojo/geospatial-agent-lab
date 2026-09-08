import os

from dotenv import load_dotenv
from groq import Groq

load_dotenv()


def create_groq_client() -> Groq:
    """Create a Groq API client from environment configuration."""

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise RuntimeError("GROQ_API_KEY is not configured. Add it to your .env file.")

    return Groq(api_key=api_key)


def get_model() -> str:
    """Return the configured Groq model."""

    return os.getenv(
        "GROQ_MODEL",
        "openai/gpt-oss-20b",
    )
