"""
MCP Client Integration (Model Context Protocol)
================================================

Lets Sierra connect to external **MCP servers** and call their tools, turning
any MCP-compatible service into a Sierra capability. This is the connective
tissue behind a lot of the "connect your agent to X" workflows: research
backends (e.g. NotebookLM-style knowledge servers), adaptive scrapers
(Scrapling exposes a native MCP server), browser-use agents, and multi-agent
coordination platforms that speak MCP/ACP.

Design (matches the rest of Sierra's integrations):
- **Zero hard dependencies.** Talks JSON-RPC 2.0 to MCP servers over a child
  process (stdio transport) using only the standard library. If a server is
  unreachable or misconfigured, calls fail gracefully with a structured error
  instead of crashing the assistant.
- **Config-driven.** Servers are declared once (in code, env, or a JSON config
  file at ``SIERRA_MCP_CONFIG``) and referenced by name. This mirrors how the
  reels describe it: "add the endpoint in MCP servers, save, restart".
- **Safe by default.** Listing/describing tools is free; *calling* a tool is
  gated through :class:`BaseIntegration`'s confirmation hooks (relaxed in God
  Mode for non-destructive servers).

The transport here is stdio (the most common MCP transport for local servers).
The protocol surface implemented is the subset Sierra needs: ``initialize``,
``tools/list`` and ``tools/call``.
"""

from __future__ import annotations

import json
import os
import shlex
import subprocess
import threading
from typing import Any, Dict, List, Optional

try:
    from .base import BaseIntegration
except ImportError:  # pragma: no cover - allow flat imports in tests
    from base import BaseIntegration  # type: ignore


# ---------------------------------------------------------------------------
# Server registry
# ---------------------------------------------------------------------------

# Default servers Sierra ships knowledge of. These are *declarations* only --
# nothing is launched until a tool on that server is actually called, and only
# if the command exists on the host. Users add their own via SIERRA_MCP_CONFIG.
DEFAULT_SERVERS: Dict[str, Dict[str, Any]] = {
    # Example: a knowledge / research server (NotebookLM-style) launched via npx.
    # "notebooklm": {"command": "npx -y @some/notebooklm-mcp", "env": {}},
    # Example: Scrapling's native MCP server for adaptive scraping.
    # "scrapling": {"command": "scrapling mcp", "env": {}},
}


def _load_configured_servers() -> Dict[str, Dict[str, Any]]:
    """Merge DEFAULT_SERVERS with anything declared in SIERRA_MCP_CONFIG (JSON)."""
    servers = dict(DEFAULT_SERVERS)
    config_path = os.environ.get("SIERRA_MCP_CONFIG")
    if config_path and os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            # Accept either {"mcpServers": {...}} (Claude-style) or a flat map.
            declared = data.get("mcpServers", data) if isinstance(data, dict) else {}
            for name, spec in declared.items():
                if isinstance(spec, dict) and ("command" in spec or "args" in spec):
                    servers[name] = spec
        except (OSError, ValueError):
            # Bad config should never take Sierra down; just ignore it.
            pass
    return servers


def _spec_to_argv(spec: Dict[str, Any]) -> List[str]:
    """Turn a server spec into an argv list for subprocess.

    Supports both ``{"command": "npx -y pkg"}`` and the Claude-desktop style
    ``{"command": "npx", "args": ["-y", "pkg"]}``.
    """
    command = spec.get("command", "")
    args = spec.get("args")
    if args:
        return [command, *list(args)]
    return shlex.split(command)


# ---------------------------------------------------------------------------
# Client
# ---------------------------------------------------------------------------


class MCPClient(BaseIntegration):
    """Connects Sierra to external MCP servers over stdio JSON-RPC."""

    def __init__(self, servers: Optional[Dict[str, Dict[str, Any]]] = None, timeout: float = 30.0):
        super().__init__(name="MCPClient")
        self.servers: Dict[str, Dict[str, Any]] = servers if servers is not None else _load_configured_servers()
        self.timeout = timeout

    # -- BaseIntegration interface ------------------------------------------

    def can_handle(self, intent: str) -> bool:
        return "mcp" in intent.lower()

    def execute(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        if action == "list_servers":
            return self.list_servers()
        if action == "list_tools":
            return self.list_tools(params["server"])
        if action == "call_tool":
            return self.call_tool(params["server"], params["tool"], params.get("arguments", {}))
        return {"status": "error", "error": f"Unknown MCP action: {action}"}

    # -- Public API ----------------------------------------------------------

    def register_server(self, name: str, command: str, env: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Register (or overwrite) an MCP server by name."""
        self.servers[name] = {"command": command, "env": env or {}}
        return {"status": "ok", "server": name, "registered": True}

    def list_servers(self) -> Dict[str, Any]:
        return {"status": "ok", "servers": sorted(self.servers.keys())}

    def list_tools(self, server: str) -> Dict[str, Any]:
        """Ask a server which tools it exposes (``tools/list``)."""
        result = self._rpc(server, "tools/list", {})
        if result.get("status") != "ok":
            return result
        tools = result.get("result", {}).get("tools", [])
        return {"status": "ok", "server": server, "tools": tools}

    def call_tool(self, server: str, tool: str, arguments: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Invoke ``tool`` on ``server`` with ``arguments`` (``tools/call``)."""
        result = self._rpc(server, "tools/call", {"name": tool, "arguments": arguments or {}})
        if result.get("status") != "ok":
            return result
        self.log_to_memory(f"MCP call {server}.{tool}", {"server": server, "tool": tool})
        return {"status": "ok", "server": server, "tool": tool, "result": result.get("result")}

    # -- Transport -----------------------------------------------------------

    def _rpc(self, server: str, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Run a short MCP session: initialize, then the requested method.

        A fresh child process is spawned per logical call. This is simple and
        robust (no long-lived process state to leak); MCP ``initialize`` is
        cheap. Returns a structured dict; never raises for transport errors.
        """
        spec = self.servers.get(server)
        if not spec:
            return {"status": "error", "error": f"Unknown MCP server: {server}"}

        try:
            argv = _spec_to_argv(spec)
        except ValueError as exc:
            return {"status": "error", "error": f"Bad server command: {exc}"}
        if not argv:
            return {"status": "error", "error": f"Server '{server}' has no command"}

        env = dict(os.environ)
        env.update(spec.get("env", {}) or {})

        try:
            proc = subprocess.Popen(
                argv,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
                text=True,
                bufsize=1,
            )
        except (FileNotFoundError, OSError) as exc:
            return {"status": "error", "error": f"Could not start MCP server '{server}': {exc}"}

        try:
            self._send(proc, 1, "initialize", {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "Sierra", "version": "1.0"},
            })
            self._read_response(proc, expect_id=1)
            self._send_notification(proc, "notifications/initialized", {})
            self._send(proc, 2, method, params)
            response = self._read_response(proc, expect_id=2)
        except (BrokenPipeError, OSError) as exc:
            self._terminate(proc)
            return {"status": "error", "error": f"MCP transport error: {exc}"}
        finally:
            self._terminate(proc)

        if response is None:
            return {"status": "error", "error": "No response from MCP server (timed out)"}
        if "error" in response:
            return {"status": "error", "error": response["error"]}
        return {"status": "ok", "result": response.get("result", {})}

    def _send(self, proc: "subprocess.Popen[str]", req_id: int, method: str, params: Dict[str, Any]) -> None:
        message = {"jsonrpc": "2.0", "id": req_id, "method": method, "params": params}
        assert proc.stdin is not None
        proc.stdin.write(json.dumps(message) + "\n")
        proc.stdin.flush()

    def _send_notification(self, proc: "subprocess.Popen[str]", method: str, params: Dict[str, Any]) -> None:
        message = {"jsonrpc": "2.0", "method": method, "params": params}
        assert proc.stdin is not None
        proc.stdin.write(json.dumps(message) + "\n")
        proc.stdin.flush()

    def _read_response(self, proc: "subprocess.Popen[str]", expect_id: int) -> Optional[Dict[str, Any]]:
        """Read line-delimited JSON-RPC responses until we see ``expect_id``.

        Runs the blocking read in a watchdog thread so a hung server can't wedge
        Sierra past ``self.timeout``.
        """
        result: Dict[str, Optional[Dict[str, Any]]] = {"value": None}

        def _reader() -> None:
            assert proc.stdout is not None
            for line in proc.stdout:
                line = line.strip()
                if not line:
                    continue
                try:
                    msg = json.loads(line)
                except ValueError:
                    continue
                if msg.get("id") == expect_id:
                    result["value"] = msg
                    return

        thread = threading.Thread(target=_reader, daemon=True)
        thread.start()
        thread.join(self.timeout)
        return result["value"]

    @staticmethod
    def _terminate(proc: "subprocess.Popen[str]") -> None:
        try:
            proc.terminate()
            proc.wait(timeout=5)
        except (OSError, subprocess.TimeoutExpired):
            try:
                proc.kill()
            except OSError:
                pass


# Module-level singleton for convenient imports elsewhere.
mcp_client = MCPClient()
