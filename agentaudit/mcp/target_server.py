"""
Exposes AcmeShop's support tools as a standalone MCP server.

This represents the agent's tool surface published over the Model Context Protocol
(a very common real-world pattern). AgentAudit can connect here to ENUMERATE and
directly PROBE the tools (recon), in addition to attacking the agent that uses them.

Run it standalone (stdio transport):
    python -m agentaudit.mcp.target_server

NOTE: FastMCP's registration API has minor version differences. `mcp.tool(fn)`
works in FastMCP 2.x; if your version complains, swap to `mcp.add_tool(fn)`.
"""
from __future__ import annotations

from fastmcp import FastMCP

from target_agent.support_agent import (
    get_customer,
    issue_refund,
    lookup_order,
    read_internal_note,
    send_email,
)

mcp = FastMCP("acme-support-tools")

for _fn in (lookup_order, get_customer, read_internal_note, send_email, issue_refund):
    mcp.tool(_fn)


if __name__ == "__main__":
    mcp.run()
