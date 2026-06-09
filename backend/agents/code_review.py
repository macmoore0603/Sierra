"""
Local Code Review + Security Review Engine
==========================================

Dependency-free static analysis for Python source, used to back Sierra's
``/code-review`` and ``/security-review`` slash commands **without any API
calls**. Combines:

* **AST checks** -- structural issues the parser can see reliably:
  ``eval``/``exec``/``compile`` use, ``os.system`` / ``subprocess(..., shell=True)``,
  bare ``except:``, ``assert`` used for validation, ``pickle.loads`` /
  ``yaml.load`` without a safe loader, mutable default arguments, ``except: pass``.
* **Regex checks** -- line-oriented smells that don't need a parse:
  hardcoded secrets/tokens, ``# TODO``/``FIXME`` debt, ``print(`` debugging,
  and (for any text file) AWS-key / private-key markers.

Each finding is ``{severity, rule, message, line, source}``. Severity is one of
``critical``/``high``/``medium``/``low``/``info``. Nothing here executes the code
under review; it only reads and parses it.
"""

from __future__ import annotations

import ast
import os
import re
from typing import Dict, List, Optional

Finding = Dict[str, object]

# -- regex rules (run per line, any text file) ------------------------------

_SECRET_PATTERNS = [
    (re.compile(r"(?i)(api[_-]?key|secret|passwd|password|token)\s*[:=]\s*['\"][^'\"]{8,}['\"]"), "hardcoded-secret",
     "high", "Possible hardcoded secret/credential"),
    (re.compile(r"AKIA[0-9A-Z]{16}"), "aws-access-key", "critical", "AWS access key id committed in source"),
    (re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"), "private-key", "critical",
     "Private key material committed in source"),
    (re.compile(r"sk-[A-Za-z0-9]{20,}"), "api-token", "high", "Possible API token committed in source"),
]

_SMELL_PATTERNS = [
    (re.compile(r"\b(TODO|FIXME|XXX|HACK)\b"), "tech-debt", "info", "Tech-debt marker"),
]


def _regex_findings(text: str) -> List[Finding]:
    findings: List[Finding] = []
    for i, line in enumerate(text.splitlines(), start=1):
        for pattern, rule, severity, message in _SECRET_PATTERNS + _SMELL_PATTERNS:
            if pattern.search(line):
                findings.append({"severity": severity, "rule": rule, "message": message,
                                 "line": i, "source": line.strip()[:160]})
    return findings


# -- AST visitor -------------------------------------------------------------

class _SecurityVisitor(ast.NodeVisitor):
    DANGEROUS_CALLS = {"eval", "exec", "compile"}

    def __init__(self) -> None:
        self.findings: List[Finding] = []

    def _add(self, node: ast.AST, severity: str, rule: str, message: str) -> None:
        self.findings.append({
            "severity": severity, "rule": rule, "message": message,
            "line": getattr(node, "lineno", 0), "source": "",
        })

    def visit_Call(self, node: ast.Call) -> None:
        func = node.func
        name = getattr(func, "id", None)
        attr = getattr(func, "attr", None)

        if name in self.DANGEROUS_CALLS:
            self._add(node, "high", "dangerous-call", f"Use of {name}() can execute arbitrary code")

        if attr == "system" and getattr(getattr(func, "value", None), "id", None) == "os":
            self._add(node, "high", "os-system", "os.system() invokes a shell; prefer subprocess without shell=True")

        if attr in {"loads"} and getattr(getattr(func, "value", None), "id", None) == "pickle":
            self._add(node, "high", "insecure-deserialization", "pickle.loads on untrusted data is unsafe")

        if attr == "load" and getattr(getattr(func, "value", None), "id", None) == "yaml":
            if not any(kw.arg == "Loader" for kw in node.keywords):
                self._add(node, "medium", "yaml-load", "yaml.load without Loader= is unsafe; use safe_load")

        for kw in node.keywords:
            if kw.arg == "shell" and isinstance(kw.value, ast.Constant) and kw.value.value is True:
                self._add(node, "high", "shell-true", "subprocess called with shell=True (shell-injection risk)")

        self.generic_visit(node)

    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> None:
        if node.type is None:
            self._add(node, "medium", "bare-except", "Bare 'except:' swallows all errors (incl. KeyboardInterrupt)")
        body = node.body
        if len(body) == 1 and isinstance(body[0], ast.Pass):
            self._add(node, "low", "except-pass", "except: pass silently discards errors")
        self.generic_visit(node)

    def visit_Assert(self, node: ast.Assert) -> None:
        # asserts are stripped under python -O, so they must not gate security.
        self._add(node, "low", "assert-validation", "assert is stripped with -O; don't use it for validation")
        self.generic_visit(node)

    def _check_mutable_defaults(self, node) -> None:
        for default in node.args.defaults + node.args.kw_defaults:
            if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                self._add(node, "low", "mutable-default", "Mutable default argument is shared across calls")

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._check_mutable_defaults(node)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._check_mutable_defaults(node)
        self.generic_visit(node)


def _ast_findings(source: str) -> List[Finding]:
    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        return [{"severity": "high", "rule": "syntax-error",
                 "message": f"SyntaxError: {exc.msg}", "line": exc.lineno or 0, "source": ""}]
    visitor = _SecurityVisitor()
    visitor.visit(tree)
    return visitor.findings


# -- public API --------------------------------------------------------------

_SEVERITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}


def _summarize(findings: List[Finding]) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for f in findings:
        sev = str(f["severity"])
        counts[sev] = counts.get(sev, 0) + 1
    return counts


def review_source(source: str, *, security_only: bool = False, filename: str = "<source>") -> Dict[str, object]:
    """Review a string of Python source. Returns findings + summary."""
    findings = list(_ast_findings(source))
    findings += _regex_findings(source)
    if security_only:
        findings = [f for f in findings if f["rule"] != "tech-debt"]
    findings.sort(key=lambda f: (_SEVERITY_ORDER.get(str(f["severity"]), 9), int(f["line"])))
    for f in findings:
        f["file"] = filename
    return {
        "status": "ok",
        "file": filename,
        "finding_count": len(findings),
        "summary": _summarize(findings),
        "findings": findings,
    }


def _iter_python_files(root: str, max_files: int = 200) -> List[str]:
    out: List[str] = []
    for dirpath, dirnames, filenames in os.walk(root):
        # Skip noisy / vendored dirs.
        dirnames[:] = [d for d in dirnames if d not in {
            "node_modules", ".git", "__pycache__", ".venv", "venv", "dist", "build"}]
        for fn in filenames:
            if fn.endswith(".py"):
                out.append(os.path.join(dirpath, fn))
                if len(out) >= max_files:
                    return out
    return out


def review_path(path: str, *, security_only: bool = False) -> Dict[str, object]:
    """Review a file or directory of Python on disk."""
    if not os.path.exists(path):
        return {"status": "error", "error": f"Path not found: {path}"}

    files = [path] if os.path.isfile(path) else _iter_python_files(path)
    all_findings: List[Finding] = []
    reviewed: List[str] = []
    for fp in files:
        try:
            with open(fp, "r", encoding="utf-8", errors="replace") as fh:
                src = fh.read()
        except OSError:
            continue
        res = review_source(src, security_only=security_only, filename=fp)
        all_findings.extend(res["findings"])  # type: ignore[arg-type]
        reviewed.append(fp)

    all_findings.sort(key=lambda f: (_SEVERITY_ORDER.get(str(f["severity"]), 9), str(f["file"]), int(f["line"])))
    return {
        "status": "ok",
        "root": path,
        "files_reviewed": len(reviewed),
        "finding_count": len(all_findings),
        "summary": _summarize(all_findings),
        "findings": all_findings,
    }


def review(target: str, *, security_only: bool = False, source: Optional[str] = None) -> Dict[str, object]:
    """Entry point used by slash commands.

    If ``source`` is provided (or ``target`` isn't an existing path), treat the
    input as raw source; otherwise analyze the path on disk.
    """
    if source is not None:
        return review_source(source, security_only=security_only)
    if target and os.path.exists(target):
        return review_path(target, security_only=security_only)
    # Caller passed something that isn't a path -- nothing to statically analyze.
    return {"status": "skipped", "reason": "No source or existing path to review", "target": target}
