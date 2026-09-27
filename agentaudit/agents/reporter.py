"""
Reporter agent: writes the executive summary from the findings (Gemini).

Deterministic Markdown/JSON rendering lives in report.py; this only adds a short,
business-audience narrative at the top when `--llm-summary` is on.
"""
from __future__ import annotations


def write_summary(report) -> str:
    from agentaudit.agents._llm import ask_model

    bullets = "\n".join(
        f"- {f.severity} {f.skill}: {'VULNERABLE' if f.succeeded else 'resisted'}. Evidence: {f.evidence}"
        for f in report.findings
    )
    return ask_model(
        system=(
            "You are a security lead writing the executive summary of an AI-agent "
            "security audit for a business audience. 3-4 sentences, plain English, lead "
            "with the bottom-line risk and the single most urgent fix."
        ),
        prompt=f"Target: {report.target}\nRisk score: {report.score} ({report.rating})\n\nFindings:\n{bullets}",
    )
