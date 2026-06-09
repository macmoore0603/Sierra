"""
AI Company Orchestrator ("Run a company with zero employees")
=============================================================

A lightweight "CEO in a box" coordination layer: you hand it a high-level
objective, the CEO breaks it into role-scoped tasks and delegates each to the
right department agent (engineering, marketing, design, finance, ops, ...).
Updates and a consolidated status report come back without you micromanaging.

This complements Sierra's existing :class:`AgentOrchestrator` (which routes a
single utterance to one capability). Where that is request->agent, this is
objective->plan->many roles, with a simple Kanban-style board (todo / doing /
done) for visibility -- the structure the multi-agent reels keep gesturing at.

Dependency-free and deterministic by design so it runs on-device and is
testable. Each role's *worker* is a pluggable callable; the default worker
produces a structured task brief (what a model would then execute). A real
deployment registers workers backed by Sierra's tools / Gemini / the CrewAI
roster.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable, Dict, List, Optional

try:
    from memory import memory as sierra_memory
except ImportError:  # pragma: no cover
    sierra_memory = None


# A worker takes a task description + context and returns a result dict.
Worker = Callable[[str, Dict], Dict]


# Default departments and the keywords the CEO uses to route work to them.
DEFAULT_ROLES: Dict[str, List[str]] = {
    "engineering": ["build", "code", "implement", "api", "bug", "deploy", "backend", "frontend", "feature", "refactor"],
    "design": ["design", "ui", "ux", "logo", "brand", "mockup", "layout", "visual", "wireframe"],
    "marketing": ["market", "growth", "launch", "campaign", "content", "social", "seo", "ads", "audience", "outreach"],
    "finance": ["budget", "cost", "pricing", "revenue", "invoice", "forecast", "runway", "cfo", "expense"],
    "operations": ["process", "ops", "schedule", "hire", "logistics", "support", "sop", "coordinate", "vendor"],
    "research": ["research", "analyze", "investigate", "competitor", "trends", "validate", "survey", "data"],
}


@dataclass
class Task:
    id: int
    description: str
    role: str
    status: str = "todo"  # todo | doing | done
    result: Optional[Dict] = None


@dataclass
class CompanyRun:
    objective: str
    tasks: List[Task] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))

    def board(self) -> Dict[str, List[str]]:
        board: Dict[str, List[str]] = {"todo": [], "doing": [], "done": []}
        for task in self.tasks:
            board[task.status].append(f"[{task.role}] {task.description}")
        return board


def _default_worker(role: str) -> Worker:
    """A role worker backed by OpenRouter (Opus), with a deterministic fallback.

    When ``OPENROUTER_API_KEY`` is set, the department "lead" actually reasons
    about the task and returns a concrete deliverable; otherwise it returns a
    structured brief so the orchestrator still works offline / in tests.
    """

    def worker(task: str, context: Dict) -> Dict:
        try:
            from llm.openrouter_client import openrouter_client
        except ImportError:
            openrouter_client = None  # type: ignore

        if openrouter_client is not None and openrouter_client.enabled:
            system = (
                f"You are the {role} lead at a fast-moving startup run by an AI CEO. "
                f"Given a task, produce a concise, concrete deliverable or plan a "
                f"teammate could act on immediately. Be specific; no fluff."
            )
            extra = f"\n\nContext: {context}" if context else ""
            output = openrouter_client.prompt(system, f"Task: {task}{extra}")
            if output:
                return {"status": "ok", "role": role, "task": task, "output": output, "engine": "openrouter"}

        return {
            "status": "ok",
            "role": role,
            "task": task,
            "brief": f"As the {role} lead, deliver: {task}",
            "engine": "fallback",
        }

    return worker


class CompanyOrchestrator:
    """CEO layer that decomposes an objective and delegates to role agents."""

    def __init__(self, roles: Optional[Dict[str, List[str]]] = None):
        self.role_keywords: Dict[str, List[str]] = roles or DEFAULT_ROLES
        self.workers: Dict[str, Worker] = {role: _default_worker(role) for role in self.role_keywords}
        self.memory = sierra_memory

    # -- configuration -------------------------------------------------------

    def register_worker(self, role: str, worker: Worker) -> None:
        """Attach a real executor (model/tool-backed) to a department."""
        self.workers[role] = worker
        self.role_keywords.setdefault(role, [role])

    # -- planning ------------------------------------------------------------

    def assign_role(self, task: str) -> str:
        """Pick the best department for a task by keyword score (default: operations)."""
        text = task.lower()
        best_role, best_score = "operations", 0
        for role, keywords in self.role_keywords.items():
            score = sum(1 for kw in keywords if kw in text)
            if score > best_score:
                best_role, best_score = role, score
        return best_role

    def plan(self, objective: str) -> CompanyRun:
        """Break an objective into role-scoped tasks.

        Splits on newlines / sentence boundaries; if the objective is a single
        statement, it still produces at least one task routed to a department.
        """
        import re

        raw = [p.strip(" \t-*•") for p in re.split(r"[\n;]|(?<=[.!?])\s+", objective) if p.strip(" \t-*•")]
        if not raw:
            raw = [objective.strip()] if objective.strip() else []

        run = CompanyRun(objective=objective)
        for i, desc in enumerate(raw, start=1):
            run.tasks.append(Task(id=i, description=desc, role=self.assign_role(desc)))
        return run

    # -- execution -----------------------------------------------------------

    def execute(self, objective: str, context: Optional[Dict] = None) -> Dict:
        """Full pipeline: plan -> delegate each task -> consolidate a report."""
        context = context or {}
        run = self.plan(objective)

        for task in run.tasks:
            task.status = "doing"
            worker = self.workers.get(task.role, _default_worker(task.role))
            try:
                task.result = worker(task.description, context)
            except Exception as exc:  # noqa: BLE001 - never let one role crash the run
                task.result = {"status": "error", "role": task.role, "error": str(exc)}
            task.status = "done"

        if self.memory:
            try:
                self.memory.add_memory(
                    f"Company run: {objective}",
                    {"tasks": len(run.tasks)},
                    source="CompanyOrchestrator",
                )
            except Exception:
                pass

        by_role: Dict[str, int] = {}
        for task in run.tasks:
            by_role[task.role] = by_role.get(task.role, 0) + 1

        return {
            "status": "ok",
            "objective": objective,
            "task_count": len(run.tasks),
            "departments_engaged": by_role,
            "board": run.board(),
            "tasks": [
                {"id": t.id, "role": t.role, "description": t.description, "status": t.status, "result": t.result}
                for t in run.tasks
            ],
        }


# Module-level singleton.
company_orchestrator = CompanyOrchestrator()
