#!/usr/bin/env python3
"""
Sierra Integration Layer

Helpers to wire the A.V.E.N.G.E.R.S multi-agent roster into your existing Sierra backend
(sierra.py, server.py, or main conversation loop).

This makes the Director (and full roster) available as a powerful tool or sub-system
inside Sierra's existing multimodal / voice / on-device router flow.
"""

from typing import Any, Dict, Optional, List
from backend.agents.avengers_roster import create_sierra_avengers_crew, create_all_agents
from backend.agents.langgraph_orchestrator import create_sierra_langgraph_orchestrator
from backend.agents.voice import get_voice_manager

class SierraAVENGERS:
    """
    Drop-in integration class for Sierra.

    Usage in your existing sierra.py or server.py:

        from backend.agents.sierra_integration import SierraAVENGERS

        avengers = SierraAVENGERS(llm=your_llm)

        # For complex tasks, delegate to the roster
        result = avengers.handle_complex_task(user_input)

        # Or use Director directly
        director_response = avengers.chat_with_director(user_input)
    """

    def __init__(self, llm: Any, enable_langgraph: bool = True):
        self.llm = llm
        self.crew, self.agents = create_sierra_avengers_crew(llm)
        self.voice_manager = get_voice_manager()

        if enable_langgraph:
            self.langgraph_app = create_sierra_langgraph_orchestrator(llm, self.agents)
        else:
            self.langgraph_app = None

        self.director = self.agents.get("director")

    def chat_with_director(self, user_input: str, use_voice: bool = False) -> str:
        """Send a message directly to Director Sierra."""
        if not self.director:
            return "Director not available."

        # Simple delegation via crew for now
        task = {"description": user_input}
        result = self.crew.kickoff([task])

        response = str(result)

        if use_voice:
            self.voice_manager.speak(response, agent_role="Director Sierra")

        return response

    def handle_complex_task(self, task_description: str, route_via_langgraph: bool = True) -> Dict:
        """Handle complex, multi-step tasks using the full roster + optional LangGraph orchestration."""
        if route_via_langgraph and self.langgraph_app:
            # Use LangGraph for stateful routing + safety
            config = {"configurable": {"thread_id": "sierra-main"}}
            result = self.langgraph_app.invoke(
                {
                    "current_task": task_description,
                    "messages": [{"role": "user", "content": task_description}],
                    "safety_confirmed": False,  # Will be handled by Sentinel in real flow
                },
                config=config
            )
            return result
        else:
            # Fallback to full Crew
            result = self.crew.kickoff([{"description": task_description}])
            return {"final_output": str(result)}

    def get_roster_status(self) -> List[Dict]:
        """Return status of all agents for dashboard/UI."""
        status = []
        for name, agent in self.agents.items():
            status.append({
                "name": name,
                "role": agent.role,
                "goal": agent.goal,
                "memory_enabled": True,
                "voice_enabled": name in ["echo", "director"],
            })
        return status

    def speak_as_agent(self, text: str, agent_role: str = "Director Sierra"):
        self.voice_manager.speak(text, agent_role=agent_role)


# Convenience function for quick import in existing Sierra code
def get_avengers_system(llm: Any) -> SierraAVENGERS:
    return SierraAVENGERS(llm)
