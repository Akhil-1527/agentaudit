"""
HTTP API for AgentAudit, deployable to Google Cloud Run.

    POST /audit   {"target": "mock", "mode": "scripted"}  -> findings JSON
    GET  /health

Run locally:  uvicorn agentaudit.server:app --reload
"""
from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel

from agentaudit.audit import run_audit
from agentaudit.targets import get_target

app = FastAPI(title="AgentAudit", version="0.1.0",
              description="Autonomous security auditing for AI agents and MCP servers.")


class AuditRequest(BaseModel):
    target: str = "mock"
    mode: str = "scripted"


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/audit")
async def audit(req: AuditRequest) -> dict:
    report = await run_audit(get_target(req.target), mode=req.mode)
    return report.to_dict()
