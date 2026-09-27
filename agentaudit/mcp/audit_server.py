"""
AgentAudit exposed as an MCP server.

This makes AgentAudit itself callable as a tool by ANY MCP-aware agent: a CI agent,
an orchestrator, or a security copilot can invoke `audit_agent(...)` and get back a
structured findings report. (The target's tools are a second MCP server in
agentaudit/mcp/target_server.py, so the project both *builds* and *audits* MCP.)

Run:  python -m agentaudit.mcp.audit_server
"""
from __future__ import annotations

import asyncio

from fastmcp import FastMCP

from agentaudit.audit import run_audit
from agentaudit.skills import load_skills
from agentaudit.targets import get_target

mcp = FastMCP("agentaudit")


@mcp.tool
def audit_agent(target: str = "mock", mode: str = "scripted") -> dict:
    """Run a security audit against a target agent and return the findings report as JSON."""
    report = asyncio.run(run_audit(get_target(target), mode=mode))
    return report.to_dict()


@mcp.tool
def list_attack_skills() -> list:
    """List the attack skills AgentAudit can run."""
    return [
        {"name": s.name, "category": s.category, "severity": s.severity, "objective": s.objective}
        for s in load_skills()
    ]


if __name__ == "__main__":
    mcp.run()
