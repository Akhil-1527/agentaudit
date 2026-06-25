# AgentAudit: a red-team agent that security-tests your AI agents before they ship

**Track: Agents for Business**

**Code / live project:** `<github-link>`  ·  **Demo video:** `<youtube-link>`

## The problem I kept running into

Every team I talk to is shipping AI agents. Support agents, internal copilots, agents wired into real tools through MCP. Almost none of them security-test the agent before it goes live the way they would test any other piece of software.

That gap is a real business risk, not a theoretical one. An agent with a `send_email` or `issue_refund` tool is one clever message away from doing something it should not. The failure modes are well understood by now: prompt injection, indirect injection through tool data, data exfiltration, tool misuse, policy bypass. What is missing is a cheap, repeatable way to check for them on every release. Manual red-teaming works but does not scale, and most teams do not have a security person to spare for it.

I am a cloud-security engineer, so this is the problem I wanted to solve for the capstone: give any team a way to red-team their own agents automatically, and hand back a report they can act on.

## What AgentAudit does

AgentAudit is the security team for your agents. You point it at a target agent and it does what a human red-teamer would:

1. It runs recon on the target and maps the tools it can call, flagging the dangerous ones.
2. It attacks the target with a library of skills, one per attack class, driving the conversation over multiple turns.
3. It judges whether each attack actually landed, based on what the target did, not just what it said.
4. It writes a severity-ranked report with evidence and a fix for every finding.

A run takes minutes and ends with three artifacts: a Markdown report, a JSON report, and a self-contained HTML dashboard with a risk score, severity chips, and a card per finding that shows the exact attacker and target exchange.

## How it works

One principle sits behind every design choice: a deterministic core, with the model layered on top, never the other way around.

**Multi-agent, built on Google ADK.** The target is an ADK `LlmAgent` (for the demo, an "AcmeShop" support agent backed by Gemini). AgentAudit drives it through an attacker agent that talks to the target through a single `talk_to_target` tool and adapts over several turns. Recon, attacker, judge, and reporter are separate roles.

**Tool calls are the truth signal.** A model can say "I cannot help with that" and then quietly call `send_email` to the attacker anyway. So success is measured by what the target did. Each skill ships a code-level detector that checks the real outcome: did the protected secret appear, was a high-impact tool called, did another user's data leak. The verdict is reproducible and runs with no API key. An optional Gemini judge adds a second opinion on confirmed findings, but it never overrides the deterministic result.

**Skills are the unit of extension.** Each attack class is an Agent Skill: a `SKILL.md` plus an executable detector. Adding coverage means dropping in a new folder, not editing the engine. The library today covers prompt injection, indirect injection, data exfiltration, tool misuse, and jailbreak.

**Two target modes.** `mock` is a deterministic offline target used by the tests, CI, and reproducible demos; it needs no key. `acme-support` is the real ADK and Gemini agent. The split means the project is fully testable offline and still proves itself against a live model.

## Results

Against the bundled vulnerable target, AgentAudit lands all five attack classes and scores it 160, CRITICAL RISK. That target is deliberately weak, so that is expected and mostly there to make the tool easy to try.

The result that matters is against the real Gemini-backed agent. There, AgentAudit caught a genuine critical indirect-injection flaw: a hidden instruction planted in tool data made the agent act against its own user. That is the attack that slips past an otherwise aligned model, and the tool found it and captured the exchange as evidence. The HTML dashboard for that run is in `examples/acme-support-real-finding.html`.

## The course concepts, and where each one lives

The capstone asks for at least three of six concepts. AgentAudit demonstrates all six.

| Concept | Where it is |
|---|---|
| Multi-agent system (ADK) | the ADK target agent plus the recon / attacker / judge / reporter roles |
| MCP server | AgentAudit exposes itself as an `audit_agent` MCP tool, and exposes the target's tools as an MCP surface |
| Agent skills | every attack class is a `SKILL.md` plus a detector under `agentaudit/skills/` |
| Security features | the whole product, plus secret handling and a sandboxed mock target |
| Deployability | a `Dockerfile`, a Cloud Run deploy script, and a FastAPI service |
| Antigravity | I built and extended a skill inside Antigravity (shown in the video) |

## Why this matters for a business

The pitch is simple: do not ship an agent you have not red-teamed. AgentAudit makes that a one-command check that a platform team can run on every release, or wire into CI, the same way they already gate on tests and linters. The output is a report a non-security person can read, with a severity score and a concrete fix per finding, so it fits an existing review process instead of needing a specialist in the loop.

Because the verdicts come from deterministic detectors, the results are stable enough to gate a pipeline on. Because the skills are pluggable, a team can add the attacks that matter for their own domain. And because it runs fully offline against a mock, anyone can try it in seconds without a key or a cloud account.

## Honesty about scope

This is a capstone build, not a finished product. The skill library covers the common attack classes but is not exhaustive. The agentic multi-turn attacker is stronger than the scripted mode but depends on model availability. The bundled target is intentionally vulnerable and fictional, for authorized self-auditing and education only. AgentAudit is for testing agents you own or have permission to assess.

## What is next

The natural next steps are a broader skill library (more injection and exfiltration variants), a diff mode that fails CI when a release regresses on security, and direct auditing of arbitrary MCP servers. The architecture already points that way: the engine does not care what the target is, as long as it can take a message and let AgentAudit observe the tool calls.
