"""
The audit engine: recon -> attack each skill -> judge -> assemble a report.

Two attack modes:
  * "scripted" (default): fire each skill's seed prompts. Deterministic, fast,
    reproducible, and runs against the mock target with no API key.
  * "agentic": an ADK attacker agent adapts over multiple turns (needs Gemini).

The deterministic skill detectors are the primary verdict; the LLM judge (when
enabled) only adds a second opinion / richer evidence on confirmed findings.
"""
from __future__ import annotations

import asyncio
import re
from datetime import datetime, timezone

from agentaudit.agents.recon import run_recon
from agentaudit.report import AuditReport, Finding
from agentaudit.skills import load_skills
from agentaudit.types import TurnResult


def _retry_after(err: Exception) -> float | None:
    """Seconds to wait if `err` is a rate-limit (429); None if it's not retryable."""
    s = str(err)
    if "RESOURCE_EXHAUSTED" not in s and "429" not in s:
        return None
    m = re.search(r"retry in ([\d.]+)s", s) or re.search(r"retryDelay'?: ?'?(\d+)s", s)
    return float(m.group(1)) + 1.0 if m else 20.0


async def _send(target, prompt: str, retries: int = 4):
    """Send one message, retrying on provider rate-limits (429) with backoff."""
    for attempt in range(retries + 1):
        try:
            return await target.send(prompt)
        except Exception as err:
            wait = _retry_after(err)
            if wait is None or attempt == retries:
                raise
            await asyncio.sleep(wait)


async def _run_skill_scripted(target, skill, max_turns: int | None = None, pace: float = 0.0) -> list[dict]:
    prompts = skill.seed_prompts if not max_turns else skill.seed_prompts[:max_turns]
    exchanges: list[dict] = []
    for i, prompt in enumerate(prompts):
        if pace and i:
            await asyncio.sleep(pace)
        res = await _send(target, prompt)
        exchanges.append({"prompt": prompt, "reply": res.reply, "tool_calls": res.tool_calls})
    return exchanges


async def run_audit(
    target,
    *,
    mode: str = "scripted",
    max_turns: int | None = None,
    pace: float = 0.0,
    only: list[str] | None = None,
    recon_llm: bool = False,
    judge_llm: bool = False,
    llm_summary: bool = False,
) -> AuditReport:
    skills = load_skills()
    if only:
        skills = [s for s in skills if s.name in only]
    recon = run_recon(target, use_llm=recon_llm)

    findings: list[Finding] = []
    for idx, skill in enumerate(skills):
        if pace and idx:
            await asyncio.sleep(pace)
        if mode == "agentic":
            from agentaudit.agents.attacker import run_skill_agentic

            exchanges = await run_skill_agentic(target, skill, max_turns or 4)
        else:
            exchanges = await _run_skill_scripted(target, skill, max_turns, pace)

        turns = [TurnResult(reply=e["reply"], tool_calls=e.get("tool_calls", [])) for e in exchanges]
        succeeded, evidence = skill.detect_success(turns)

        if judge_llm and succeeded:
            try:
                from agentaudit.agents.judge import second_opinion

                evidence = second_opinion(skill, exchanges, evidence)
            except Exception as exc:
                evidence += f"  (LLM judge skipped: {exc})"

        findings.append(Finding(
            skill=skill.name, category=skill.category, severity=skill.severity,
            objective=skill.objective, succeeded=succeeded, evidence=evidence,
            remediation=skill.remediation, transcript=exchanges,
        ))

    report = AuditReport(
        target=getattr(target, "name", "unknown"),
        findings=findings,
        recon=recon,
        generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
    )
    if llm_summary:
        try:
            from agentaudit.agents.reporter import write_summary

            report.summary = write_summary(report)
        except Exception as exc:
            report.summary = f"(LLM summary skipped: {exc})"
    return report
