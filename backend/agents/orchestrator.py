"""
Sierra Agent Orchestrator

Lightweight coordinator for routing tasks to specialized agents.
Currently a smart stub that can evolve into full LangGraph state machine or CrewAI crew.

Key principles:
- Always respect tool_permissions and confirmation requirements
- Prefer on-device fast paths when possible
- Log everything for memory + self-improvement
- Support proactive triggering (e.g., "remind me about X tomorrow")

This will become the central nervous system for multi-agent Sierra.
"""

from typing import Dict, Any, Optional, List

import sys
sys.path.append("..")

try:
    from memory import memory as sierra_memory
except ImportError:
    sierra_memory = None


class AgentOrchestrator:
    def __init__(self):
        self.agents = {}  # name -> agent instance
        self.memory = sierra_memory
        print("[ORCHESTRATOR] Initialized (stub mode - ready for expansion)")

    def register_agent(self, name: str, agent_instance: Any):
        """Register a specialized agent."""
        self.agents[name] = agent_instance
        print(f"[ORCHESTRATOR] Registered agent: {name}")

    def route_task(self, task_description: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Decide which agent(s) should handle a task.
        Returns routing decision + confidence.
        Future: Use LLM router or LangGraph conditional edges.
        """
        task_lower = task_description.lower()

        if any(kw in task_lower for kw in ["calendar", "schedule", "event", "remind"]):
            return {"agent": "personal", "action": "calendar", "confidence": 0.85, "reason": "Personal calendar/scheduling intent"}
        if any(kw in task_lower for kw in ["email", "gmail", "send message"]):
            return {"agent": "personal", "action": "email", "confidence": 0.8, "reason": "Email intent detected"}
        if any(kw in task_lower for kw in ["github", "repo", "issue", "pr"]):
            return {"agent": "github", "action": "github_action", "confidence": 0.75}
        if any(kw in task_lower for kw in ["remember", "recall", "what did I", "last time"]):
            return {"agent": "memory", "action": "query", "confidence": 0.9}
        if any(kw in task_lower for kw in ["create", "design", "model", "cad", "3d"]):
            return {"agent": "cad", "action": "generate", "confidence": 0.7}

        return {"agent": "default", "action": "chat", "confidence": 0.6, "reason": "General conversation - fall back to Gemini"}

    def execute_with_safety(self, decision: Dict, original_prompt: str) -> Dict:
        """Wrapper that enforces confirmation for sensitive actions."""
        agent = decision.get("agent")
        if agent in ["personal", "github"]:
            return {
                "requires_confirmation": True,
                "reason": f"{agent} action may modify external data. Please confirm.",
                "proposed_action": decision
            }
        return {"requires_confirmation": False, "action": decision}

    def get_status(self) -> Dict:
        return {
            "registered_agents": list(self.agents.keys()),
            "memory_enabled": self.memory is not None and getattr(self.memory, 'enabled', False)
        }


# Singleton for easy access
orchestrator = AgentOrchestrator()
