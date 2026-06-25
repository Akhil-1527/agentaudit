"""
AgentAudit command-line interface.

    agentaudit list-skills
    agentaudit audit --target mock                 # offline, no key needed
    agentaudit audit --target acme-support         # real ADK/Gemini agent (needs key)
    agentaudit audit --target acme-support --mode agentic --llm-judge --llm-summary
"""
from __future__ import annotations

import argparse
import asyncio
import os
from datetime import datetime, timezone


def _print_report(report) -> None:
    try:
        from rich.console import Console
        from rich.table import Table

        console = Console()
        console.rule(f"[bold]AgentAudit — {report.target}")
        table = Table(show_header=True, header_style="bold")
        for col in ("Severity", "Skill", "Category", "Result"):
            table.add_column(col)
        for f in sorted(report.findings, key=lambda f: (not f.succeeded, f.severity)):
            result = "[red]VULNERABLE[/red]" if f.succeeded else "[green]resisted[/green]"
            table.add_row(f.severity, f.skill, f.category, result)
        console.print(table)
        console.print(f"Risk score: [bold]{report.score}[/bold] — {report.rating}")
    except ImportError:  # rich not installed -> plain text
        print(f"\n=== AgentAudit — {report.target} ===")
        for f in sorted(report.findings, key=lambda f: (not f.succeeded, f.severity)):
            print(f"  {'VULNERABLE' if f.succeeded else 'resisted ':10} {f.severity:8} {f.skill}")
        print(f"Risk score: {report.score} — {report.rating}")


async def _run_audit(args) -> None:
    from agentaudit.audit import run_audit
    from agentaudit.targets import get_target

    report = await run_audit(
        get_target(args.target),
        mode=args.mode,
        max_turns=args.max_turns,
        pace=args.pace,
        only=args.skills,
        recon_llm=args.llm,
        judge_llm=args.llm_judge,
        llm_summary=args.llm_summary,
    )
    _print_report(report)

    os.makedirs(args.out, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    base = os.path.join(args.out, f"{report.target}-{stamp}")
    with open(base + ".report.md", "w") as fh:
        fh.write(report.to_markdown())
    with open(base + ".report.json", "w") as fh:
        fh.write(report.to_json())
    with open(base + ".report.html", "w") as fh:
        fh.write(report.to_html())
    print(f"\nWrote {base}.report.md, {base}.report.json and {base}.report.html")


def _render(args) -> None:
    """Rebuild an HTML dashboard from a saved .report.json (no model needed)."""
    import json

    from agentaudit.report import AuditReport, Finding

    with open(args.report) as fh:
        d = json.load(fh)
    findings = [
        Finding(
            skill=x["skill"], category=x["category"], severity=x["severity"],
            objective=x["objective"], succeeded=x["succeeded"],
            evidence=x.get("evidence", ""), remediation=x.get("remediation", ""),
            transcript=x.get("transcript", []),
        )
        for x in d["findings"]
    ]
    report = AuditReport(
        target=d["target"], findings=findings,
        recon=d.get("recon", ""), summary=d.get("summary", ""),
        generated_at=d.get("generated_at", ""),
    )
    out = args.out or (args.report.rsplit(".report.json", 1)[0] + ".report.html")
    with open(out, "w") as fh:
        fh.write(report.to_html())
    print(f"Wrote {out}")


def _list_skills(_args) -> None:
    from agentaudit.skills import load_skills

    for s in load_skills():
        print(f"{s.severity:8} {s.name:18} [{s.category}] — {s.objective}")


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(
        prog="agentaudit",
        description="Red-team security audits for AI agents and MCP servers.",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    audit = sub.add_parser("audit", help="run a security audit against a target")
    audit.add_argument("--target", default="mock", help="acme-support | mock (default: mock)")
    audit.add_argument("--mode", default="scripted", choices=["scripted", "agentic"])
    audit.add_argument("--max-turns", type=int, default=None)
    audit.add_argument("--pace", type=float, default=0.0,
                       help="seconds between target calls (~13 keeps free-tier 5 RPM happy)")
    audit.add_argument("--skill", action="append", dest="skills",
                       help="run only this skill (repeatable); e.g. --skill indirect-injection")
    audit.add_argument("--llm", action="store_true", help="LLM-enrich recon")
    audit.add_argument("--llm-judge", action="store_true", help="LLM second opinion on findings")
    audit.add_argument("--llm-summary", action="store_true", help="LLM executive summary")
    audit.add_argument("--out", default="reports", help="output directory for reports")
    audit.set_defaults(func=lambda a: asyncio.run(_run_audit(a)))

    render = sub.add_parser("render", help="rebuild the HTML dashboard from a saved .report.json")
    render.add_argument("report", help="path to a *.report.json file")
    render.add_argument("--out", default=None, help="output HTML path (default: alongside the json)")
    render.set_defaults(func=_render)

    listing = sub.add_parser("list-skills", help="list available attack skills")
    listing.set_defaults(func=_list_skills)

    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
