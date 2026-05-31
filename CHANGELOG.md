# Sierra Changelog

All notable changes to Sierra will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased] - 2026-05-31

### Added
- **Project Vision section** in README: Explicit commitment to building the most powerful personal AI agent with deep ecosystem integrations, self-improvement, advanced memory/RAG, multi-agent orchestration (LangGraph/CrewAI), and robust safety/confirmation mechanisms.
- **Recent Improvements** highlight in README.
- Expanded capabilities table and architecture diagram to reflect safety, future multi-agent (`agents/`), and personal integrations direction.
- Comprehensive `CHANGELOG.md` to track iterative progress.
- Enhanced `.env.example` with clear sections for upcoming Google Calendar, Gmail, GitHub, and other personal integrations.
- Major upgrade to `backend/tools.py`: reorganized into clear categories, added detailed docstrings/comments, expanded tool surface area with placeholders for personal tools, memory, and safety-aware design. Better prepared for Gemini function calling + on-device router.

### Changed
- README.md polished for clarity, flow, and alignment with long-term goals (voice-first, privacy-focused, proactive, safe).
- Project structure documentation updated to include `backend/agents/`.

### Philosophy
This release continues the iterative "make Sierra better" development style. Every change brings us closer to a persistent, self-improving, deeply integrated personal AI that feels magical while staying private and safe.

## [0.1.0] - Initial Sierra-Ada v2 base

- Forked/extended from A.D.A V2 + A.D.A Local FunctionGemma router.
- Core features: Gemini 2.5 Native Audio voice, on-device intent router, parametric CAD (build123d), 3D printing integration, gesture control (MediaPipe), face authentication, web agent (Playwright), Kasa smart home, basic project memory.
- Electron + React frontend with Minority Report-style UI.
- Safety: tool permission system in settings.json.

---

> **Note**: Sierra is under active development. Check Git history and `devin/*` branches for the latest experimental work.
