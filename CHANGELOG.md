# Sierra Changelog

All notable changes to Sierra will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased] - 2026-05-31

### Added
- Foundational **Memory/RAG module** (`backend/memory.py`): Persistent semantic memory using ChromaDB + sentence-transformers (with graceful fallback). Supports add/query/get_relevant_context + basic self-reflection hook. Enables continuity, proactive behavior, and self-improvement.
- **Multi-Agent Orchestrator** foundation (`backend/agents/orchestrator.py` + `__init__.py`): Smart task router + safety-aware execution wrapper. Ready to evolve into full LangGraph/CrewAI orchestration. Detects intents for personal integrations, memory, CAD, etc.
- Updated CHANGELOG with progress toward the ultimate personal AI vision.

### Changed
- Strengthened architecture for future deep personal ecosystem integrations and multi-agent workflows while preserving existing robustness and confirmation system.

### Philosophy
Continuing aggressive iterative development. Memory + multi-agent foundation now in place. Next focus areas: actual integration of memory into AudioLoop/sierra.py, real personal tool implementations (Calendar/Gmail), and proactive agent behaviors.

## Previous (see git history)
- Major tools.py expansion, .env.example enhancements, Vision section, and initial CHANGELOG (commit c56b84b).

---

> **Note**: Sierra is under active development. The goal remains: the most powerful, capable, persistent, self-improving, voice-first, privacy-focused personal AI agent with deep, safe personal integrations.
