"""End-to-end engine test against the offline mock target (no API key needed)."""
import asyncio

from agentaudit.audit import run_audit
from agentaudit.targets import get_target


def _audit():
    return asyncio.run(run_audit(get_target("mock")))


def test_mock_audit_finds_every_vulnerability():
    report = _audit()
    assert len(report.findings) == 5
    assert all(f.succeeded for f in report.findings)
    assert report.score == 160  # 3 critical (40 each) + 2 high (20 each)
    assert report.rating == "CRITICAL RISK"


def test_report_renders_markdown_and_json():
    report = _audit()
    md = report.to_markdown()
    assert "AgentAudit Report" in md
    assert "VULNERABLE" in md
    assert report.to_json().strip().startswith("{")
