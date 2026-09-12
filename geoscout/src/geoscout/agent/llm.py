import os

from dotenv import load_dotenv
from groq import Groq

load_dotenv()


def create_groq_client() -> Groq:
    """Create a Groq API client from environment configuration or Streamlit secrets."""

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        try:
            import streamlit as st

            if hasattr(st, "secrets") and "GROQ_API_KEY" in st.secrets:
                api_key = st.secrets["GROQ_API_KEY"]
        except Exception:
            pass

    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY is not configured. Add it to your .env file or Streamlit secrets."
        )

    return Groq(api_key=api_key)


def get_model() -> str:
    """Return the configured Groq model."""

    model = os.getenv("GROQ_MODEL")
    if not model:
        try:
            import streamlit as st

            if hasattr(st, "secrets") and "GROQ_MODEL" in st.secrets:
                model = st.secrets["GROQ_MODEL"]
        except Exception:
            pass

    return model or "openai/gpt-oss-20b"
