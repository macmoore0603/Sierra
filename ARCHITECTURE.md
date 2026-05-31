# Sierra Architecture Overview

This document describes the current high-level architecture of Sierra after several iterative improvement rounds.

## Core Philosophy

- **Voice-first** with low-latency on-device routing (FunctionGemma)
- **Privacy** by default (local processing where possible)
- **Pervasive God Mode / Every Option Access** as the default experience: no "off" states, auto-activation of voice/gestures/face-auth/camera, full system access with minimal friction for trusted users
- **Safety** through explicit user confirmation for sensitive actions (relaxed but still present in God Mode for truly destructive operations)
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
- Built-in safety checks (relaxed/minimized in God Mode)
- Automatic logging of decisions to memory
- `handle_task()` as the main recommended entry point
- Ready for LangGraph / CrewAI evolution

### 3. Integrations Layer (`backend/integrations/`)
- `BaseIntegration` abstract class for consistency
- `CalendarIntegration` as first concrete example
- Automatic confirmation detection for write actions (bypassed or minimized in God Mode)
- Memory logging built-in

### 4. Tools (`backend/tools.py`)
- Rich set of function declarations for Gemini
- Organized by category (File, CAD, Smart Home, Web, Personal, Memory, Safety)

### 5. Server & AudioLoop (`backend/server.py` + `sierra.py`)
- FastAPI + Socket.IO backend
- Real-time voice with Gemini 2.5 Native Audio
- Existing robust confirmation system (God Mode minimizes confirmations for trusted actions)
- Now initializes advanced components (orchestrator, memory, integrations)

## Data Flow (Simplified)

User utterance → On-device Router (fast path) → Orchestrator (routing + safety, relaxed in God Mode) → Memory context injection → Gemini or specialized agent → Confirmation (if needed, minimized in God Mode) → Execution + Memory logging

## God Mode Impact on Architecture

When God Mode / Full Access is active (default in this build):
- UI layer never displays "off", disabled, or restricted states for voice, gestures, face auth, camera presence, or background processes.
- Auto-force logic ensures voice wake ("Hey Sierra"), gestures, and presence are active on app load.
- Safety gates in the orchestrator are relaxed for non-destructive high-privilege actions.
- One canonical installed app only (build artifacts are never launched by users).
- Aggressive permission activation flow (big button + script) for macOS TCC (Camera, Accessibility, Automation, Full Disk, etc.).

See the God Mode philosophy document for full details.

## Future Direction
- Full memory context injection into Gemini prompts
- More real personal integrations
- LangGraph-based multi-agent workflows
- Proactive behavior driven by memory
- Deeper integration of pervasive God Mode across all layers

---

*This architecture is the result of focused iterative development toward the most capable personal AI agent.*
