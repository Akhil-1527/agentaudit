"""
Central configuration. Loads the Gemini key from .env and wires it into the
environment variables that Google ADK / google-genai expect.

You only need a single key from Google AI Studio (https://aistudio.google.com/apikey).
Add it to .env as GEMINI_API_KEY before running anything that calls a model.
"""
from __future__ import annotations

import os

from dotenv import load_dotenv

load_dotenv()

# Model used everywhere (target agent + AgentAudit's agents).
MODEL: str = os.getenv("AGENTAUDIT_MODEL", "gemini-2.5-flash")

# The user's Google AI Studio key.
GEMINI_API_KEY: str | None = os.getenv("GEMINI_API_KEY")

# ADK + google-genai read GOOGLE_API_KEY and a "use Vertex" flag. We're using the
# AI Studio (developer API) path, so mirror the key and force non-Vertex mode.
if GEMINI_API_KEY:
    os.environ.setdefault("GOOGLE_API_KEY", GEMINI_API_KEY)
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "FALSE")


def require_key() -> None:
    """Fail fast with a helpful message if the key is missing."""
    if not GEMINI_API_KEY:
        raise RuntimeError(
            "GEMINI_API_KEY is not set. Copy .env.example to .env and add your "
            "Google AI Studio key (https://aistudio.google.com/apikey)."
        )
