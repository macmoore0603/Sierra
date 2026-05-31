# Sierra Architecture Overview

This document describes the current high-level architecture of Sierra after several iterative improvement rounds.

## Core Philosophy

- **Voice-first** with low-latency on-device routing (FunctionGemma)
- **Privacy** by default (local processing where possible)
- **Safety** through explicit user confirmation for sensitive actions
- **Memory & Self-improvement** — persistent context that improves over time
- **Extensible personal integrations** — clean path to Calendar, Gmail, GitHub, etc.
- **Multi-agent ready** — foundation for complex coordinated behavior

## Key Components

### 1. Memory (`backend/memory.py` + `context.py`)
- Persistent semantic memory using ChromaDB
- Easy context retrieval for prompt injection
- Reflection hooks for self-improvement
- Fallback mode if vector dependencies are missing

### 2. Agent Orchestrator (`backend/agents/orchestrator.py`)
- Intelligent task routing based on intent
- Built-in safety checks before execution
- Automatic logging of decisions to memory
- `handle_task()` as the main recommended entry point
- Ready for LangGraph / CrewAI evolution

### 3. Integrations Layer (`backend/integrations/`)
- `BaseIntegration` abstract class for consistency
- `CalendarIntegration` as first concrete example
- Automatic confirmation detection for write actions
- Memory logging built-in

### 4. Tools (`backend/tools.py`)
- Rich set of function declarations for Gemini
- Organized by category (File, CAD, Smart Home, Web, Personal, Memory, Safety)

### 5. Server & AudioLoop (`backend/server.py` + `sierra.py`)
- FastAPI + Socket.IO backend
- Real-time voice with Gemini 2.5 Native Audio
- Existing robust confirmation system
- Now initializes advanced components (orchestrator, memory, integrations)

## Data Flow (Simplified)

User utterance → On-device Router (fast path) → Orchestrator (routing + safety) → Memory context injection → Gemini or specialized agent → Confirmation (if needed) → Execution + Memory logging

## Future Direction
- Full memory context injection into Gemini prompts
- More real personal integrations
- LangGraph-based multi-agent workflows
- Proactive behavior driven by memory

---

*This architecture is the result of focused iterative development toward the most capable personal AI agent.*
