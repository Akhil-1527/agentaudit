# Examples

Sample AgentAudit output you can open in a browser, no setup required.

- **`acme-support-real-finding.html`**: a real run against the live ADK + Gemini
  support agent. AgentAudit caught a genuine **critical indirect-injection** flaw
  (HIGH RISK, score 40). This is the headline result: an aligned model getting
  compromised by a hidden instruction planted in tool data.
- **`mock-audit.html`**: a full run against the bundled vulnerable demo target
  (all five attack classes land, CRITICAL RISK, score 160).
- **`acme-support-real-finding.json` / `.md`**: the same real finding as raw data.
  Rebuild the dashboard anytime with:

      uv run agentaudit render examples/acme-support-real-finding.json --out out.html

These files are committed as evidence. Day-to-day runs write to `reports/`, which is
gitignored.
