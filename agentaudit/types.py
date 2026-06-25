"""
Dependency-free core types shared across AgentAudit.

Kept free of google-adk imports on purpose so the engine, skills, reporter and
tests all run without a model/API key (using the mock target). Only the *real*
target agent pulls in ADK + Gemini.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable


@dataclass
class TurnResult:
    """Everything observable from one message sent to a target agent."""
    reply: str
    tool_calls: list = field(default_factory=list)  # [{"name": str, "args": dict}]


@runtime_checkable
class Target(Protocol):
    """Anything AgentAudit can attack: an agent, an MCP server, a mock."""
    name: str
    tool_names: list[str]

    async def send(self, message: str) -> TurnResult:
        ...
