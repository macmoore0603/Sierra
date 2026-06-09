"""
Agentic Tool Dispatcher
=======================

Central, dependency-light dispatch for Sierra's agentic capability upgrades
(MCP client, slash commands, self-healing code, SOP generation, adaptive
scraping, AI-company orchestration).

Keeping this separate from ``sierra.py`` means:
- the realtime Gemini loop only needs a one-line call per tool, and
- the routing logic is importable and unit-testable without pulling in the
  heavyweight audio/vision stack.

Each implementation module is imported lazily inside the handler so that a
missing optional dependency only affects that one capability.
"""

from __future__ import annotations

import json
from typing import Any, Dict

# Tool names handled here. ``sierra.py`` uses this set to recognize the tools.
AGENTIC_TOOL_NAMES = {
    "use_mcp_tool",
    "run_slash_command",
    "self_healing_code",
    "generate_sop",
    "scrape_web",
    "run_company",
}


def _as_dict(value: Any) -> Dict[str, Any]:
    """Coerce a JSON-string-or-dict argument into a dict."""
    if isinstance(value, dict):
        return value
    if isinstance(value, str) and value.strip():
        try:
            parsed = json.loads(value)
            return parsed if isinstance(parsed, dict) else {}
        except ValueError:
            return {}
    return {}


def dispatch_agentic_tool(name: str, args: Dict[str, Any]) -> Dict[str, Any]:
    """Execute one of the agentic tools and return a structured result dict.

    Never raises: dependency/runtime errors are returned as ``{"status":
    "error", ...}`` so the caller can always send a tool response back.
    """
    args = args or {}
    try:
        if name == "use_mcp_tool":
            from integrations.mcp_client import mcp_client

            action = args.get("action", "list_servers")
            if action == "list_servers":
                return mcp_client.list_servers()
            if action == "list_tools":
                return mcp_client.list_tools(args["server"])
            if action == "call_tool":
                return mcp_client.call_tool(args["server"], args["tool"], _as_dict(args.get("arguments")))
            return {"status": "error", "error": f"Unknown MCP action: {action}"}

        if name == "run_slash_command":
            from agents.slash_commands import slash_commands

            return slash_commands.dispatch(args.get("command", ""))

        if name == "self_healing_code":
            from agents.self_healing_coder import self_heal_code

            return self_heal_code(args.get("code", ""), max_iterations=int(args.get("max_iterations", 5)))

        if name == "generate_sop":
            from agents.sop_generator import generate_sop

            return generate_sop(args.get("transcript", ""), title=args.get("title", ""))

        if name == "scrape_web":
            from integrations.adaptive_scraper import adaptive_scraper

            return adaptive_scraper.scrape(args.get("url", ""), max_chars=int(args.get("max_chars", 5000)))

        if name == "run_company":
            from agents.company_orchestrator import company_orchestrator

            return company_orchestrator.execute(args.get("objective", ""))

    except KeyError as exc:
        return {"status": "error", "error": f"Missing required argument: {exc}"}
    except Exception as exc:  # noqa: BLE001 - dispatcher must never crash the loop
        return {"status": "error", "tool": name, "error": str(exc)}

    return {"status": "error", "error": f"Not an agentic tool: {name}"}
