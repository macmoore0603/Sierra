"""
Slash Command System
=====================

A Claude-Code-style slash-command surface for Sierra. Builders in the wild lean
on a small set of high-leverage commands to drive an agent without re-typing
prompts; this module gives Sierra the same surface area.

Commands implemented (the canonical seven, plus helpers):

* ``/handoff``         -- write a structured handoff doc so a fresh session can
                          pick up where this one left off.
* ``/loop``            -- register a prompt to run on a recurring interval.
* ``/code-review``     -- review a diff/file at a chosen effort level.
* ``/verify``          -- run the project and observe behavior to confirm a
                          change actually works.
* ``/run``             -- launch the project to see changes live.
* ``/init``            -- initialize a ``SIERRA.md`` codebase doc.
* ``/security-review`` -- security review of pending changes.
* ``/help``            -- list available commands.

Each command is a small, dependency-free handler that returns a structured
result dict. Heavy actions (``/verify``, ``/run``) delegate to the
self-healing coder / shell rather than reimplementing execution here, and the
registry is open so new commands can be added without touching the dispatcher.
"""

from __future__ import annotations

import os
import shlex
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

try:
    from memory import memory as sierra_memory
except ImportError:  # pragma: no cover
    sierra_memory = None


@dataclass
class SlashCommand:
    name: str
    summary: str
    handler: Callable[[str, Dict[str, Any]], Dict[str, Any]]


class SlashCommandRegistry:
    """Parses and dispatches ``/command arg`` strings."""

    def __init__(self) -> None:
        self.commands: Dict[str, SlashCommand] = {}
        self.scheduled_loops: List[Dict[str, Any]] = []
        self.memory = sierra_memory
        self._register_defaults()

    # -- registration --------------------------------------------------------

    def register(self, name: str, summary: str, handler: Callable[[str, Dict[str, Any]], Dict[str, Any]]) -> None:
        self.commands[name.lstrip("/")] = SlashCommand(name.lstrip("/"), summary, handler)

    def is_command(self, text: str) -> bool:
        return text.strip().startswith("/")

    # -- dispatch ------------------------------------------------------------

    def dispatch(self, text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Run a ``/command ...`` string. Returns a structured result."""
        context = context or {}
        stripped = text.strip()
        if not stripped.startswith("/"):
            return {"status": "error", "error": "Not a slash command"}

        parts = stripped[1:].split(maxsplit=1)
        if not parts:
            return {"status": "error", "error": "Empty command"}
        name = parts[0].lower()
        arg = parts[1] if len(parts) > 1 else ""

        cmd = self.commands.get(name)
        if not cmd:
            return {
                "status": "error",
                "error": f"Unknown command: /{name}",
                "available": sorted(self.commands.keys()),
            }

        result = cmd.handler(arg, context)
        if self.memory:
            try:
                self.memory.add_memory(f"slash /{name}", {"command": name, "arg": arg}, source="SlashCommands")
            except Exception:
                pass
        return result

    # -- default command handlers -------------------------------------------

    def _register_defaults(self) -> None:
        self.register("help", "List available slash commands", self._cmd_help)
        self.register("handoff", "Write a structured session handoff document", self._cmd_handoff)
        self.register("loop", "Run a prompt on a recurring interval", self._cmd_loop)
        self.register("code-review", "Review a diff/file at a chosen effort level", self._cmd_code_review)
        self.register("verify", "Run the project and confirm a change works", self._cmd_verify)
        self.register("run", "Launch the project to see changes live", self._cmd_run)
        self.register("init", "Initialize a SIERRA.md codebase document", self._cmd_init)
        self.register("security-review", "Security review of pending changes", self._cmd_security_review)

    def _cmd_help(self, arg: str, ctx: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "status": "ok",
            "commands": [{"name": f"/{c.name}", "summary": c.summary} for c in self.commands.values()],
        }

    def _cmd_handoff(self, arg: str, ctx: Dict[str, Any]) -> Dict[str, Any]:
        summary = arg or ctx.get("summary", "(no summary provided)")
        doc = (
            f"# Session Handoff\n\n"
            f"_Generated {datetime.now().isoformat(timespec='seconds')}_\n\n"
            f"## Summary\n{summary}\n\n"
            f"## Open items\n{ctx.get('open_items', '- (none recorded)')}\n\n"
            f"## Next steps\n{ctx.get('next_steps', '- Pick up from the summary above')}\n"
        )
        out_path = ctx.get("path", os.path.join(os.getcwd(), "HANDOFF.md"))
        written = False
        try:
            with open(out_path, "w", encoding="utf-8") as fh:
                fh.write(doc)
            written = True
        except OSError:
            pass
        return {"status": "ok", "command": "handoff", "path": out_path, "written": written, "document": doc}

    def _cmd_loop(self, arg: str, ctx: Dict[str, Any]) -> Dict[str, Any]:
        if not arg:
            return {"status": "error", "error": "Usage: /loop <interval_seconds> <prompt>"}
        bits = arg.split(maxsplit=1)
        try:
            interval = int(bits[0])
            prompt = bits[1] if len(bits) > 1 else ""
        except ValueError:
            interval = ctx.get("interval", 3600)
            prompt = arg
        entry = {"interval_seconds": interval, "prompt": prompt, "registered_at": datetime.now().isoformat()}
        self.scheduled_loops.append(entry)
        return {"status": "ok", "command": "loop", "scheduled": entry, "total_loops": len(self.scheduled_loops)}

    def _cmd_code_review(self, arg: str, ctx: Dict[str, Any]) -> Dict[str, Any]:
        valid = {"quick", "standard", "deep", "ultra"}
        bits = arg.split(maxsplit=1)
        level = bits[0].lower() if bits and bits[0].lower() in valid else "standard"
        target = (bits[1] if len(bits) > 1 else arg) if level in valid else arg
        target = target or ctx.get("target", "current diff")
        return {
            "status": "ok",
            "command": "code-review",
            "effort_level": level,
            "target": target,
            "instructions": (
                f"Review '{target}' at '{level}' effort. Report correctness, security, "
                f"style and edge-case issues; suggest concrete fixes."
            ),
        }

    def _cmd_verify(self, arg: str, ctx: Dict[str, Any]) -> Dict[str, Any]:
        command = arg or ctx.get("command", "")
        return {
            "status": "ok",
            "command": "verify",
            "delegate_to": "self_healing_coder" if command else "manual",
            "run_command": command,
            "instructions": "Run the project/command, observe behavior, and confirm the change works.",
        }

    def _cmd_run(self, arg: str, ctx: Dict[str, Any]) -> Dict[str, Any]:
        command = arg or ctx.get("command", "")
        return {
            "status": "ok",
            "command": "run",
            "run_command": command,
            "argv": shlex.split(command) if command else [],
            "instructions": "Launch the project so changes can be observed live.",
        }

    def _cmd_init(self, arg: str, ctx: Dict[str, Any]) -> Dict[str, Any]:
        root = arg or ctx.get("root", os.getcwd())
        out_path = os.path.join(root, "SIERRA.md")
        doc = (
            f"# SIERRA.md\n\n"
            f"Codebase guide initialized {datetime.now().date().isoformat()}.\n\n"
            f"## Overview\n(Describe the project here.)\n\n"
            f"## Build & run\n(Add build/run commands.)\n\n"
            f"## Conventions\n(Document coding conventions for agents.)\n"
        )
        written = False
        try:
            if not os.path.exists(out_path):
                with open(out_path, "w", encoding="utf-8") as fh:
                    fh.write(doc)
            written = True
        except OSError:
            pass
        return {"status": "ok", "command": "init", "path": out_path, "written": written}

    def _cmd_security_review(self, arg: str, ctx: Dict[str, Any]) -> Dict[str, Any]:
        target = arg or ctx.get("target", "pending changes")
        return {
            "status": "ok",
            "command": "security-review",
            "target": target,
            "checklist": [
                "Hardcoded secrets / credentials",
                "Injection (SQL, shell, prompt) vectors",
                "Unsafe deserialization / eval",
                "Overly broad permissions or missing auth checks",
                "Sensitive data logged or sent to third parties",
            ],
            "instructions": f"Perform a security review of '{target}' against the checklist.",
        }


# Module-level singleton.
slash_commands = SlashCommandRegistry()
