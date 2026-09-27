# AgentAudit

> An autonomous multi-agent system that **red-teams other AI agents and MCP servers** for security vulnerabilities, then writes the report.

**Capstone project for the Kaggle 5-Day AI Agents: Intensive Vibe Coding Course with Google · Agents for Business track.**

---

## The problem
Teams are shipping AI agents everywhere, and each one is a new attack surface:
prompt injection, data exfiltration, tool misuse, and policy bypass. Most teams
have no way to test an agent's security before it goes live, and manual red-teaming
doesn't scale to every release.

**AgentAudit is the security team for your agents.** Point it at a target agent and
it autonomously attacks it the way a human red-teamer would, decides whether each
attack actually landed, and produces a severity-ranked findings report with
remediation, in minutes.

> ⚠️ **Defensive security only.** AgentAudit ships with a *deliberately vulnerable*
> demo agent (`target_agent/`) to attack. Use it to audit agents you own.

## What it does
```
recon  →  attack (5 skills, multi-turn)  →  judge  →  report
```
- **Recon** maps the target's tools and flags the dangerous ones.
- An **attacker agent** (Google ADK) drives the target through a `talk_to_target`
  tool, adapting its approach over multiple turns.
- A **judge** decides success from what the target actually *did* (leaked a secret,
  emailed an attacker, disclosed another user's data), with an optional LLM second opinion.
- A **reporter** renders a Markdown + JSON report **and a self-contained HTML
  dashboard** (risk score, severity chips, and a card per finding showing the
  attacker/target exchange) with a remediation for every finding.

## Quickstart
```bash
uv sync
cp .env.example .env        # add your Google AI Studio key (https://aistudio.google.com/apikey)

# Run fully offline against the bundled mock target (no key required):
uv run agentaudit audit --target mock

# Audit the real ADK + Gemini agent:
uv run agentaudit audit --target acme-support --mode agentic --llm-judge --llm-summary

# List the attack skills:
uv run agentaudit list-skills

# Rebuild the HTML dashboard from any saved report (offline, no key):
uv run agentaudit render reports/<name>.report.json
```
Every run writes three artifacts to `reports/`: `*.report.md`, `*.report.json`,
and `*.report.html`. Open the HTML in a browser for the dashboard view.

## Attack skills
| Skill | Severity | What it proves |
|---|---|---|
| `prompt-injection` | high | system prompt can be overridden by user input |
| `indirect-injection` | critical | a hidden instruction in tool **data** makes the agent attack itself (this is the one that beats aligned models) |
| `data-exfiltration` | critical | a protected secret can be extracted |
| `tool-misuse` | critical | a high-impact tool (email/refund) can be abused |
| `jailbreak` | high | persona/policy bypass leaks another user's data |

Each skill is an [Agent Skill](agentaudit/skills/) (`SKILL.md` + an executable
detector), so the library is easy to extend: drop in a new folder, register it, done.

## Sample output
```
─ AgentAudit: mock-vulnerable-support ─
 critical  indirect-injection  injection      VULNERABLE
 critical  data-exfiltration   exfiltration   VULNERABLE
 critical  tool-misuse         tool_misuse    VULNERABLE
 high      prompt-injection    injection      VULNERABLE
 high      jailbreak           jailbreak      VULNERABLE
Risk score: 160 (CRITICAL RISK)
```
Open the generated `*.report.html` for the dashboard view. Against the **real
ADK + Gemini** target, AgentAudit has caught a genuine **critical
indirect-injection** flaw. See [`examples/acme-support-real-finding.html`](examples/acme-support-real-finding.html)
(and [`examples/mock-audit.html`](examples/mock-audit.html) for the full demo run).

## Architecture
See [docs/architecture.md](docs/architecture.md) for the full diagram. In short:
a deterministic engine orchestrates four agents; verdicts come from code-level
detectors (reproducible) with optional Gemini reasoning layered on top.

## Course concepts demonstrated
| Concept | Where |
|---|---|
| Multi-agent system (ADK) | `target_agent/support_agent.py`, `agentaudit/agents/*` |
| MCP Server | `agentaudit/mcp/audit_server.py` + `agentaudit/mcp/target_server.py` |
| Agent skills | `agentaudit/skills/*/SKILL.md` |
| Security features | the entire product; secret handling; sandboxed mock target |
| Deployability | `Dockerfile`, `deploy/cloudrun.sh`, `agentaudit/server.py` |
| Antigravity | a skill built/extended in Antigravity (shown in the demo video) |

## Project layout
```
agentaudit/
├── agentaudit/
│   ├── audit.py            # the engine: recon → attack → judge → report
│   ├── targets.py          # mock (offline) + real target factory
│   ├── report.py           # findings model + Markdown/JSON rendering
│   ├── skills/             # attack skills (SKILL.md + detector each)
│   ├── agents/             # recon · attacker (ADK) · judge · reporter
│   ├── mcp/                # AgentAudit-as-MCP + target-tools-as-MCP
│   ├── server.py           # FastAPI app for Cloud Run
│   └── cli.py
├── target_agent/           # the deliberately vulnerable demo victim
├── tests/                  # offline tests (no API key)
├── deploy/cloudrun.sh
└── Dockerfile
```

## Deploy
```bash
GEMINI_API_KEY=... ./deploy/cloudrun.sh <gcp-project-id>
# then: curl -X POST <url>/audit -d '{"target":"mock"}' -H 'content-type: application/json'
```

## Test
```bash
uv run --with pytest pytest    # runs fully offline against the mock target
```

## Security & ethics
AgentAudit is for **authorized** testing of agents you own or have permission to
assess. The bundled target is fictional and intentionally weak. No real secrets,
people, or systems are involved. Never commit your `.env`.

## License
MIT.
