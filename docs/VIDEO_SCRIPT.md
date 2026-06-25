# AgentAudit: 5-minute demo video script

Target length: under 5:00. The whole thing is a screen recording with voiceover.

**Recording plan that cannot fail on camera:**
- Do the live demo with `--target mock`. It is deterministic, needs no API key, and can never 503 or rate-limit mid-take.
- Show the already-rendered `acme-support` dashboard as proof it works against a real Gemini agent.
- Record the live-demo segment first; it is the one most likely to need a retake.

**Before you hit record:**
- Terminal open in `~/projects/agentaudit`, font size bumped up.
- Browser tab 1: `reports/acme-support-20260621-045112.report.html` (the real finding) ready.
- Browser tab 2: a fresh mock dashboard (or open it live during the demo).
- Antigravity open on one skill file for the build clip.
- Record system audio + mic.

---

### [0:00 – 0:30] Hook + problem
*On screen: you, or a title slide reading "AgentAudit".*

"Every team is shipping AI agents right now. Support bots, internal copilots, agents wired into real tools. And almost nobody security-tests them before they go live. An agent with an email tool or a refund tool is one clever message away from doing something it should not. I'm Akhil, I'm a cloud-security engineer, and AgentAudit is a red-team agent that tests other agents for exactly those flaws."

### [0:30 – 1:00] What it is
*On screen: the architecture diagram from docs/architecture.md.*

"You point AgentAudit at a target agent and it does what a human red-teamer would. It maps the target's tools, attacks it with a library of skills over several turns, judges whether each attack actually landed, and writes a report. Four roles: recon, attacker, judge, reporter. All built on Google's Agent Development Kit."

### [1:00 – 2:15] Live demo (mock target)
*On screen: terminal. Run `uv run agentaudit audit --target mock`.*

"Here it is against a deliberately vulnerable demo agent. No API key, fully offline, so it is deterministic. It is firing each attack skill at the target... and there is the result."

*On screen: the CRITICAL table appears.*

"Five attack classes, all of them landed. Critical indirect injection, data exfiltration, tool misuse. Risk score 160, critical."

*On screen: open the generated `*.report.html` dashboard.*

"And it writes this dashboard. The risk score, every finding with its severity, and the actual attacker-and-target exchange that proves it."

### [2:15 – 3:00] The real Gemini finding
*On screen: switch to the acme-support dashboard tab.*

"That was the intentionally weak target. This is the one that matters. I pointed AgentAudit at a real ADK and Gemini support agent, and it caught a genuine critical indirect-injection flaw. A hidden instruction planted in tool data that makes the agent turn against its own user. That is the attack that gets past an aligned model, and the tool found it and captured the evidence."

### [3:00 – 3:45] Why it is reliable: detectors + skills + Antigravity
*On screen: a skill detector in code, then the `agentaudit/skills/` folder, then Antigravity.*

"Two things make this trustworthy. First, the verdict comes from code, not vibes. Each skill has a detector that checks what the target actually did: called the dangerous tool, leaked the secret. So results are reproducible and you can gate a pipeline on them. Second, every attack is an Agent Skill, a SKILL.md plus a detector, so adding coverage is just dropping in a folder. I built these skills in Antigravity."

### [3:45 – 4:20] MCP + deployability
*On screen: the MCP server file, then `deploy/cloudrun.sh` and the Dockerfile, then `docker run` locally.*

"AgentAudit also exposes itself as an MCP server, so another agent can call it as a tool, and it wraps the target's tools as MCP too. It ships with a Dockerfile and a Cloud Run script. Here it is running as a container."

### [4:20 – 5:00] Impact + close
*On screen: back to the dashboard, then a title slide with the repo + video links.*

"The pitch is simple: do not ship an agent you have not red-teamed. AgentAudit makes that a one-command check you can run on every release, with a report a non-security person can act on. It demonstrates all six course concepts: multi-agent ADK, MCP, agent skills, security, deployability, and Antigravity. Code and setup are linked below. Thanks for watching."

---

**If you run long, cut in this order:** the MCP/deploy narration first, then trim the architecture segment. Never cut the live demo or the real-finding segment. Upload to YouTube as Unlisted and paste the link into the writeup.
