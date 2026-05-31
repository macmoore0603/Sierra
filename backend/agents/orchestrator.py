"""
Sierra Agent Orchestrator

Lightweight but powerful coordinator for routing tasks to specialized agents.
Evolving toward full multi-agent orchestration (LangGraph / CrewAI ready).

Core principles:
- Respect tool_permissions and user confirmation requirements at every step
- Prefer on-device fast paths (router) when confident
- Log all decisions to memory for continuity + self-improvement
- Support proactive behavior (suggestions, reminders, follow-ups)
- Clean separation: routing → safety check → execution

This is becoming the central nervous system of Sierra.
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
        self.agents: Dict[str, Any] = {}
        self.memory = sierra_memory
        self.decision_history: List[Dict] = []  # lightweight in-memory log
        print("[ORCHESTRATOR] Initialized and ready.")

    def register_agent(self, name: str, agent_instance: Any) -> None:
        """Register a specialized agent (CAD, Web, Personal, Memory, etc.)."""
        self.agents[name] = agent_instance
        print(f"[ORCHESTRATOR] Registered agent: {name}")

    def route_task(self, task_description: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Intelligently route a user request to the best agent/action.

        Returns a structured decision dict.
        Future: Replace keyword logic with LLM router or LangGraph.
        """
        text = task_description.lower().strip()
        context = context or {}

        # High-confidence personal / proactive intents
        if any(kw in text for kw in ["calendar", "schedule", "event", "remind me", "what's on my", "tomorrow"]):
            return {"agent": "personal", "action": "calendar", "confidence": 0.88, "reason": "Scheduling / calendar intent"}

        if any(kw in text for kw in ["email", "gmail", "send email", "message to"]):
            return {"agent": "personal", "action": "email", "confidence": 0.82, "reason": "Email intent"}

        if any(kw in text for kw in ["github", "repo", "create issue", "pull request", "pr"]):
            return {"agent": "github", "action": "github_action", "confidence": 0.78, "reason": "GitHub workflow intent"}

        # Memory & self-improvement
        if any(kw in text for kw in ["remember", "recall", "what did I say", "last time", "previously"]):
            return {"agent": "memory", "action": "query", "confidence": 0.92, "reason": "Memory retrieval request"}

        # Creative / CAD
        if any(kw in text for kw in ["create", "design", "model", "cad", "3d", "prototype", "make a"]):
            return {"agent": "cad", "action": "generate", "confidence": 0.75, "reason": "CAD / creative design intent"}

        # Smart home (existing strength)
        if any(kw in text for kw in ["light", "turn on", "turn off", "kasa", "smart home"]):
            return {"agent": "smart_home", "action": "control", "confidence": 0.85, "reason": "Smart home control"}

        # Default → Gemini with memory context
        return {
            "agent": "default",
            "action": "chat",
            "confidence": 0.55,
            "reason": "General conversation - will use Gemini + memory context"
        }

    def execute_with_safety(self, decision: Dict[str, Any], original_prompt: str) -> Dict[str, Any]:
        """Check if this decision requires explicit user confirmation."""
        agent = decision.get("agent", "default")

        high_risk = {"personal", "github", "email"}
        if agent in high_risk:
            return {
                "requires_confirmation": True,
                "reason": f"{agent.title()} action may read or modify external data. Confirm before proceeding.",
                "proposed_action": decision,
                "original_prompt": original_prompt
            }

        return {
            "requires_confirmation": False,
            "action": decision
        }

    def handle_task(self, task_description: str, original_prompt: str = "") -> Dict[str, Any]:
        """Full pipeline: route → safety check → log to memory.

        This is the main entry point recommended for future use.
        """
        decision = self.route_task(task_description)
        safety = self.execute_with_safety(decision, original_prompt or task_description)

        # Log decision for memory + future self-improvement
        log_entry = {
            "prompt": task_description,
            "decision": decision,
            "safety": safety,
            "timestamp": __import__('datetime').datetime.now().isoformat()
        }
        self.decision_history.append(log_entry)

        if self.memory:
            try:
                self.memory.add_memory(
                    f"Orchestrator routed: '{task_description}' → {decision.get('agent')}/{decision.get('action')} (conf={decision.get('confidence')})",
                    metadata={"type": "orchestrator_decision", "agent": decision.get("agent")},
                    source="orchestrator"
                )
            except Exception:
                pass  # memory failures should never break routing

        return {
            "decision": decision,
            "safety_check": safety,
            "logged_to_memory": bool(self.memory)
        }

    def get_proactive_suggestions(self, context: Optional[Dict] = None) -> List[str]:
        """Future hook for proactive behavior (e.g. "You have a meeting in 30 min", "Want me to follow up on X?")."""
        suggestions = []
        if self.memory:
            # Placeholder: in future we can query memory for upcoming items
            suggestions.append("Would you like me to check your calendar for today?")
        return suggestions

    def get_status(self) -> Dict[str, Any]:
        return {
            "registered_agents": list(self.agents.keys()),
            "memory_enabled": bool(self.memory and getattr(self.memory, 'enabled', False)),
            "recent_decisions": len(self.decision_history)
        }


# Singleton
orchestrator = AgentOrchestrator()
