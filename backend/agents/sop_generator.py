"""
SOP / Procedure Generator ("Procedure Ops")
============================================

Turns a messy description of how something gets done -- a voice-note
transcript, a quick brain-dump, a list of half-formed steps -- into a clean,
structured Standard Operating Procedure document.

The pattern (from the "COO in a box" reels): you talk through a process, it
runs the interview, pushes back on vague steps, flags what should be automated,
and packages the result for the team.

This implementation is dependency-free and deterministic so it's testable and
runs on-device. It:
- splits free-form text into discrete steps (numbered lists, bullets, "then/
  next/after" connectors, or sentences),
- flags **vague** steps (e.g. "handle it", "deal with the stuff") that need
  clarification,
- flags steps that look **automatable** (export, email, upload, sync, schedule,
  backup...),
- emits Markdown plus a structured dict.

A model-backed deployment can pass the raw text through Gemini first for richer
rewriting; this module is the reliable fallback and structuring layer.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List

_VAGUE_MARKERS = [
    "handle it", "deal with", "the stuff", "etc", "and so on", "somehow",
    "figure out", "do the thing", "as needed", "various", "stuff",
]

_AUTOMATABLE_MARKERS = [
    "export", "email", "send", "upload", "download", "sync", "schedule",
    "backup", "back up", "copy", "paste", "rename", "format", "report",
    "notify", "remind", "log", "fetch", "scrape", "generate",
]

_STEP_SPLIT_RE = re.compile(
    r"(?:^|\n)\s*(?:\d+[\.\)]|[-*•])\s+"  # numbered or bulleted lines
)
_CONNECTOR_RE = re.compile(r"\b(?:then|next|after that|afterwards|finally)\b\s*,?\s*", re.IGNORECASE)


@dataclass
class SOPStep:
    number: int
    text: str
    vague: bool = False
    automatable: bool = False
    notes: List[str] = field(default_factory=list)


def _split_steps(raw: str) -> List[str]:
    """Extract discrete step strings from free-form text."""
    raw = raw.strip()
    if not raw:
        return []

    # First try explicit list markers.
    if _STEP_SPLIT_RE.search(raw):
        parts = _STEP_SPLIT_RE.split(raw)
    else:
        # Fall back to "then/next/..." connectors, then sentence boundaries.
        connector_split = _CONNECTOR_RE.split(raw)
        if len(connector_split) > 1:
            parts = connector_split
        else:
            parts = re.split(r"(?<=[.!?])\s+", raw)

    steps = [p.strip(" \t\n-*•.").strip() for p in parts]
    return [s for s in steps if s]


def _analyze_step(number: int, text: str) -> SOPStep:
    lowered = text.lower()
    step = SOPStep(number=number, text=text)

    if any(marker in lowered for marker in _VAGUE_MARKERS) or len(text.split()) < 3:
        step.vague = True
        step.notes.append("Vague — clarify the exact action, inputs, and done-criteria.")

    if any(marker in lowered for marker in _AUTOMATABLE_MARKERS):
        step.automatable = True
        step.notes.append("Candidate for automation.")

    return step


@dataclass
class SOP:
    title: str
    steps: List[SOPStep]
    created_at: str

    def to_markdown(self) -> str:
        lines = [f"# SOP: {self.title}", "", f"_Generated {self.created_at}_", ""]
        lines.append("## Steps\n")
        for step in self.steps:
            tags = []
            if step.vague:
                tags.append("⚠️ needs clarification")
            if step.automatable:
                tags.append("⚙️ automatable")
            suffix = f"  _({', '.join(tags)})_" if tags else ""
            lines.append(f"{step.number}. {step.text}{suffix}")
            for note in step.notes:
                lines.append(f"   - {note}")
        clarifications = [s for s in self.steps if s.vague]
        automations = [s for s in self.steps if s.automatable]
        if clarifications:
            lines.append("\n## Open questions")
            for s in clarifications:
                lines.append(f"- Step {s.number}: what exactly does \"{s.text}\" involve?")
        if automations:
            lines.append("\n## Automation opportunities")
            for s in automations:
                lines.append(f"- Step {s.number}: {s.text}")
        return "\n".join(lines) + "\n"


def generate_sop(transcript: str, title: str = "") -> Dict:
    """Build a structured SOP from a transcript/brain-dump.

    Returns a dict with the parsed steps and a rendered Markdown document.
    """
    title = title.strip() or "Untitled Procedure"
    raw_steps = _split_steps(transcript)
    steps = [_analyze_step(i + 1, text) for i, text in enumerate(raw_steps)]
    sop = SOP(title=title, steps=steps, created_at=datetime.now().isoformat(timespec="seconds"))
    return {
        "status": "ok",
        "title": title,
        "step_count": len(steps),
        "needs_clarification": [s.number for s in steps if s.vague],
        "automatable": [s.number for s in steps if s.automatable],
        "steps": [
            {"number": s.number, "text": s.text, "vague": s.vague, "automatable": s.automatable, "notes": s.notes}
            for s in steps
        ],
        "markdown": sop.to_markdown(),
    }
