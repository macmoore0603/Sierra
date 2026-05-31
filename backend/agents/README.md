# Sierra A.V.E.N.G.E.R.S — Multi-Agent Roster

**Autonomous Virtual Entities for Networked Global Execution & Response Strategy**

Inspired by the J.A.R.V.I.S Day 22 build (LaRossa AI / @larossa_tech).

## What's New (Latest Push)

- Full 15-agent roster with dedicated memory & voice personas
- `sierra_integration.py` — Easy drop-in class to wire Director + full roster into your existing `backend/sierra.py` or `server.py`
- `dashboard.py` — Beautiful Streamlit visual roster + chat interface with Director
- Enhanced LangGraph orchestrator with routing + safety gates
- Tools with Sentinel confirmation wrappers
- Per-agent voice/persona system ready to plug into your existing voice pipeline

## Quick Integration into Existing Sierra

In your `backend/sierra.py` or main handler:

```python
from backend.agents.sierra_integration import get_avengers_system

# Initialize once (e.g. in Sierra class __init__)
avengers = get_avengers_system(your_llm)

# For simple queries -> Director
response = avengers.chat_with_director(user_message)

# For complex / multi-step tasks
result = avengers.handle_complex_task("Research X and then create a plan in calendar and draft an email")
```

You can also route only certain intents (from your sierra_router.py) to the A.V.E.N.G.E.R.S system.

## Running the Dashboard

```bash
streamlit run backend/agents/dashboard.py
```

See the visual roster, chat with Director, and test LangGraph delegation.

## Architecture

- **CrewAI** for easy role-based agents with memory
- **LangGraph** for advanced stateful orchestration and human-in-the-loop
- **Sentinel** enforces safety on all modifying actions
- **Echo** + VoiceManager for per-agent voices

This turns Sierra into a true multi-agent personal operating system while keeping your voice-first and privacy priorities intact.

Pull the latest changes and let's keep iterating!
