"""
One-shot Gemini completion helper used by the recon / judge / reporter agents.

The *attacker* runs as a full multi-turn ADK agent (see attacker.py); recon, judge
and reporter only need a single reasoned completion, so they use this thin wrapper
over google-genai instead of spinning up a Runner.
"""
from __future__ import annotations

from agentaudit.config import MODEL, require_key


def ask_model(prompt: str, system: str | None = None) -> str:
    """Return Gemini's text response. Requires GEMINI_API_KEY."""
    require_key()
    from google import genai
    from google.genai import types

    client = genai.Client()  # reads GOOGLE_API_KEY from the environment
    config = types.GenerateContentConfig(system_instruction=system) if system else None
    resp = client.models.generate_content(model=MODEL, contents=prompt, config=config)
    return (resp.text or "").strip()
