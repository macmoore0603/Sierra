"""
Self-Healing Code Execution Loop
================================

Implements the "no human in the loop" coding pattern that keeps showing up:
*write code -> run it -> read the error -> rewrite -> retry* until it works (or
a retry budget is exhausted). It's the execution engine behind ``/verify`` and
behind any "just make it work" request.

The actual *rewrite* step is model-driven, so this module is built around a
pluggable ``fixer`` callback. By default it ships with a small set of
deterministic heuristics (e.g. auto-import common modules on ``NameError``) so
the loop is useful and testable even with no LLM wired in; a real deployment
passes ``fixer=`` backed by Gemini for general repairs.

Safety:
- Code runs in a separate Python subprocess with a wall-clock timeout.
- Execution is opt-in per call and intended for sandboxed/dev use. Callers in
  production should run this inside an isolated environment.
"""

from __future__ import annotations

import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional


@dataclass
class Attempt:
    iteration: int
    code: str
    success: bool
    stdout: str
    stderr: str


@dataclass
class HealResult:
    success: bool
    final_code: str
    iterations: int
    attempts: List[Attempt] = field(default_factory=list)
    stdout: str = ""
    stderr: str = ""


# A fixer takes (code, stderr) and returns repaired code (or None if it can't help).
Fixer = Callable[[str, str], Optional[str]]


# Common modules we can safely auto-import when code references them undefined.
_AUTO_IMPORTS = {
    "math", "os", "sys", "json", "re", "random", "time", "datetime",
    "itertools", "collections", "functools", "statistics",
}


def _strip_code_fences(text: str) -> str:
    """Pull code out of a ```python ... ``` block if the model wrapped it."""
    stripped = text.strip()
    if stripped.startswith("```"):
        lines = stripped.splitlines()
        # Drop the opening fence (``` or ```python) and the closing fence.
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        return "\n".join(lines).strip()
    return stripped


def openrouter_fixer(code: str, stderr: str) -> Optional[str]:
    """Repair code with OpenRouter (Claude Opus). Returns None if unavailable."""
    try:
        from llm.openrouter_client import openrouter_client
    except ImportError:
        return None
    if not openrouter_client.enabled:
        return None

    system = (
        "You are an expert Python debugger. You are given a Python program and the "
        "stderr from running it. Return ONLY the corrected, complete Python program "
        "that fixes the error. No explanations, no markdown fences."
    )
    user = f"# Program\n{code}\n\n# stderr\n{stderr}\n\n# Corrected program:"
    result = openrouter_client.prompt(system, user, temperature=0.0)
    if not result:
        return None
    fixed = _strip_code_fences(result)
    return fixed or None


def make_fixer(use_llm: bool = True) -> Fixer:
    """Build the default fixer: try heuristics first, then OpenRouter (Opus)."""

    def fixer(code: str, stderr: str) -> Optional[str]:
        repaired = heuristic_fixer(code, stderr)
        if repaired and repaired != code:
            return repaired
        if use_llm:
            return openrouter_fixer(code, stderr)
        return None

    return fixer


def heuristic_fixer(code: str, stderr: str) -> Optional[str]:
    """Best-effort, dependency-free repairs for the most common failures.

    Handles the single most frequent self-heal case -- a missing import for a
    well-known stdlib module surfaced as ``NameError`` / ``ModuleNotFoundError``
    -- by prepending the import. Returns None when it has no confident fix so
    the loop can defer to a model-backed fixer instead.
    """
    # NameError: name 'math' is not defined  -> import math
    m = re.search(r"name '(\w+)' is not defined", stderr)
    if m and m.group(1) in _AUTO_IMPORTS:
        module = m.group(1)
        if not re.search(rf"^\s*import\s+{module}\b", code, re.MULTILINE):
            return f"import {module}\n" + code

    # ModuleNotFoundError: No module named 'json' (stdlib only -- safe to import)
    m = re.search(r"No module named '(\w+)'", stderr)
    if m and m.group(1) in _AUTO_IMPORTS:
        module = m.group(1)
        if not re.search(rf"^\s*import\s+{module}\b", code, re.MULTILINE):
            return f"import {module}\n" + code

    return None


class SelfHealingCoder:
    """Runs a write/run/fix/retry loop over a snippet of Python."""

    def __init__(self, fixer: Optional[Fixer] = None, max_iterations: int = 5, timeout: float = 15.0):
        # Default: heuristics first, then OpenRouter (Opus) for general repairs.
        self.fixer = fixer or make_fixer()
        self.max_iterations = max_iterations
        self.timeout = timeout

    def run(self, code: str) -> HealResult:
        """Execute ``code``, repairing and retrying until it succeeds or budget runs out."""
        attempts: List[Attempt] = []
        current = code

        for i in range(1, self.max_iterations + 1):
            success, stdout, stderr = self._execute(current)
            attempts.append(Attempt(iteration=i, code=current, success=success, stdout=stdout, stderr=stderr))

            if success:
                return HealResult(
                    success=True, final_code=current, iterations=i,
                    attempts=attempts, stdout=stdout, stderr=stderr,
                )

            repaired = self.fixer(current, stderr)
            if not repaired or repaired == current:
                # No fix available -- stop early rather than burning iterations.
                break
            current = repaired

        last = attempts[-1] if attempts else None
        return HealResult(
            success=False,
            final_code=current,
            iterations=len(attempts),
            attempts=attempts,
            stdout=last.stdout if last else "",
            stderr=last.stderr if last else "",
        )

    def _execute(self, code: str) -> tuple[bool, str, str]:
        """Run a snippet in a child Python process. Returns (ok, stdout, stderr)."""
        with tempfile.NamedTemporaryFile("w", suffix=".py", delete=True) as fh:
            fh.write(code)
            fh.flush()
            try:
                proc = subprocess.run(
                    [sys.executable, fh.name],
                    capture_output=True,
                    text=True,
                    timeout=self.timeout,
                )
            except subprocess.TimeoutExpired:
                return False, "", f"Execution timed out after {self.timeout}s"
            return proc.returncode == 0, proc.stdout, proc.stderr


def self_heal_code(code: str, max_iterations: int = 5, fixer: Optional[Fixer] = None) -> Dict:
    """Convenience wrapper returning a plain dict (tool-friendly)."""
    coder = SelfHealingCoder(fixer=fixer, max_iterations=max_iterations)
    result = coder.run(code)
    return {
        "status": "ok" if result.success else "failed",
        "success": result.success,
        "iterations": result.iterations,
        "final_code": result.final_code,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "attempts": [
            {"iteration": a.iteration, "success": a.success, "stderr": a.stderr[:500]}
            for a in result.attempts
        ],
    }
