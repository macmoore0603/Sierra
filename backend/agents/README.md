# Sierra A.V.E.N.G.E.R.S — Multi-Agent Roster

**Autonomous Virtual Entities for Networked Global Execution & Response Strategy**

Inspired by the J.A.R.V.I.S Day 22 build (LaRossa AI / @larossa_tech).

## Overview

This module adds a powerful, specialized multi-agent system to Sierra. Each agent has:

- A clear role and backstory
- Dedicated long-term + short-term memory
- Voice/persona support (via Echo)
- Safety guardrails through Sentinel

The system evolves Sierra from a single assistant into a true personal AI operating system.

## Agents (15 total)

| Agent       | Role                          | Key Focus                          |
|-------------|-------------------------------|------------------------------------|
| Director    | Central orchestrator         | Coordination, safety, user interface |
| Scout       | Research & Intelligence      | Deep research, monitoring          |
| Forge       | Code & Engineering           | Sierra development, GitHub         |
| Chronos     | Calendar & Time              | Scheduling, reminders              |
| Courier     | Email & Communications       | Gmail, drafting, prioritization    |
| Weaver      | Memory & Knowledge           | RAG, long-term memory              |
| Echo        | Voice & Persona              | STT/TTS, interruptions, personas   |
| Sentinel    | Security & Privacy           | Confirmations, guardrails          |
| Operator    | Daily Operations             | Workflows, proactive tasks         |
| Maestro     | Meetings                     | Prep, notes, follow-ups            |
| Creator     | Content & Documentation      | Writing, reports, Sierra docs      |
| Evolver     | Self-Improvement             | Architecture upgrades, code review |
| Guardian    | Local & Device               | Files, on-device privacy           |
| Analyst     | Personal Intelligence        | Custom briefings (Duluth context)  |
| Toolsmith   | Tools & Integrations         | New capabilities                   |

## Quick Start

```python
from backend.agents.avengers_roster import create_sierra_avengers_crew, create_all_agents

# Assume you have your LLM ready (e.g. from existing Sierra setup)
llm = ...  # your ChatGroq / Gemini / etc.

crew, agents = create_sierra_avengers_crew(llm)

# Example task delegation
result = crew.kickoff([{"description": "Research the latest in personal AI agents and summarize key trends."}])
print(result)
```

## LangGraph Orchestration

See `langgraph_orchestrator.py` for a stateful supervisor that can route tasks intelligently and integrate human-in-the-loop confirmations.

## Tools

See `tools.py` for ready-to-use (and gated) tools for Calendar, Gmail, GitHub, local files, web search, etc.

All modifying actions are wrapped with Sentinel confirmation hooks.

## Voice

`voice.py` provides per-agent personas and a VoiceManager you can plug into Sierra's existing voice pipeline.

## Next Steps / Integration

1. Wire the Director into your main conversation loop in `backend/sierra.py` or `server.py`.
2. Connect real Google/Gmail/GitHub credentials securely.
3. Add more tools via Toolsmith.
4. Build a visual roster dashboard (React component or Streamlit).
5. Expand with more agents as needed.

This brings Sierra significantly closer to the "AI OS" vision while staying true to voice-first, privacy, and self-improvement principles.

Built for you, Mac. Let's keep making Sierra unstoppable.
