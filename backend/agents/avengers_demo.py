#!/usr/bin/env python3
"""
Quick demo of Sierra A.V.E.N.G.E.R.S roster.
Run this to test the full crew.
"""

from backend.agents.avengers_roster import create_sierra_avengers_crew, create_all_agents
from backend.agents.voice import get_voice_manager

# Use your existing LLM setup from Sierra
# Example with Groq (replace with whatever Sierra uses)
try:
    from langchain_groq import ChatGroq
    llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.6)
except ImportError:
    print("Install langchain-groq or use your Sierra LLM")
    llm = None

if llm:
    print("\n=== Initializing Sierra A.V.E.N.G.E.R.S ===\n")
    crew, agents = create_sierra_avengers_crew(llm)

    print("Agents loaded:")
    for name, agent in agents.items():
        print(f"  - {agent.role}")

    # Simple demo task
    print("\n--- Running demo task via Director ---\n")
    task = "Give me a quick status update on how the new multi-agent roster improves Sierra."
    result = crew.kickoff([{"description": task}])
    print(result)

    # Voice demo
    vm = get_voice_manager()
    vm.speak("Multi-agent system online and ready to serve.", agent_role="Director Sierra")
else:
    print("LLM not available for demo.")
