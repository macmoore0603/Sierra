#!/usr/bin/env python3
"""
Sierra Integration Layer (Updated with Neural Link)

Now includes the complete maxed-out Neural Link for deepest personalization.
"""

from typing import Any, Dict, Optional, List
from backend.agents.avengers_roster import create_sierra_avengers_crew, create_all_agents
from backend.agents.langgraph_orchestrator import create_sierra_langgraph_orchestrator
from backend.agents.voice import get_voice_manager
from backend.agents.neural_link import NeuralLinkManager

class SierraAVENGERS:
    """
    Drop-in integration with full A.V.E.N.G.E.R.S + Neural Link.
    """

    def __init__(self, llm: Any, enable_langgraph: bool = True):
        self.llm = llm
        self.crew, self.agents = create_sierra_avengers_crew(llm)
        self.voice_manager = get_voice_manager()

        # === Neural Link (Maxed Out) ===
        self.neural_link_manager = NeuralLinkManager()
        self.neural_link = self.neural_link_manager.get_link()

        if enable_langgraph:
            self.langgraph_app = create_sierra_langgraph_orchestrator(llm, self.agents)
        else:
            self.langgraph_app = None

        self.director = self.agents.get("director")

    def chat_with_director(self, user_input: str, use_voice: bool = False) -> str:
        # Inject Neural Link context for ultra-personalized response
        context = self.neural_link.get_full_context_for_director()
        enriched_input = f"[NEURAL LINK CONTEXT]\n{context['context_string']}\n\nUser: {user_input}"

        task = {"description": enriched_input}
        result = self.crew.kickoff([task])
        response = str(result)

        # Update Neural Link from interaction
        self.neural_link.update_user_state({"last_interaction": user_input[:100]}, source="chat")
        self.neural_link.consolidate_memory(user_input)

        if use_voice:
            self.voice_manager.speak(response, agent_role="Director Sierra")

        return response

    def handle_complex_task(self, task_description: str, route_via_langgraph: bool = True) -> Dict:
        context = self.neural_link.get_full_context_for_director()
        enriched_task = f"[NEURAL LINK CONTEXT]\n{context['context_string']}\nPredicted needs: {context['predicted_needs']}\n\nTask: {task_description}"

        if route_via_langgraph and self.langgraph_app:
            config = {"configurable": {"thread_id": "sierra-main"}}
            result = self.langgraph_app.invoke({
                "current_task": enriched_task,
                "messages": [{"role": "user", "content": enriched_task}],
                "safety_confirmed": False,
            }, config=config)
            return result
        else:
            result = self.crew.kickoff([{"description": enriched_task}])
            return {"final_output": str(result)}

    def get_roster_status(self) -> List[Dict]:
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

    def get_neural_link_context(self) -> Dict:
        return self.neural_link.get_full_context_for_director()


def get_avengers_system(llm: Any) -> SierraAVENGERS:
    return SierraAVENGERS(llm)
