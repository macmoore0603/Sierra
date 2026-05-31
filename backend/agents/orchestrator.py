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

GOD MODE BEHAVIOR (pervasive full access is the default):
- In God Mode, safety checks are significantly relaxed for non-destructive actions.
- High-privilege actions (system control, personal data, automation) have minimal confirmation.
- The UI layer is expected to never show "off" or restricted states for voice, gestures, face auth, etc.
- Auto-activation of capabilities on launch is the expected behavior.

See GOD_MODE.md for the full philosophy.

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
        self.decision_history: List[Dict] = []
        print("[ORCHESTRATOR] Initialized and ready.")

    def register_agent(self, name: str, agent_instance: Any) -> None:
        """Register a specialized agent (CAD, Web, Personal, Memory, etc.)."""
        self.agents[name] = agent_instance
        print(f"[ORCHESTRATOR] Registered agent: {name}")

    def route_task(self, task_description: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Intelligently route a user request to the best agent/action."""
        text = task_description.lower().strip()

        if any(kw in text for kw in ["calendar", "schedule", "event", "remind me", "what's on my", "tomorrow"]):
            return {"agent": "personal", "action": "calendar", "confidence": 0.88, "reason": "Scheduling / calendar intent"}
        if any(kw in text for kw in ["email", "gmail", "send email", "message to"]):
            return {"agent": "personal", "action": "email", "confidence": 0.82, "reason": "Email intent"}
        if any(kw in text for kw in ["github", "repo", "create issue", "pull request", "pr"]):
            return {"agent": "github", "action": "github_action", "confidence": 0.78, "reason": "GitHub workflow intent"}
        if any(kw in text for kw in ["remember", "recall", "what did I say", "last time", "previously"]):
            return {"agent": "memory", "action": "query", "confidence": 0.92, "reason": "Memory retrieval request"}
        if any(kw in text for kw in ["create", "design", "model", "cad", "3d", "prototype", "make a"]):
            return {"agent": "cad", "action": "generate", "confidence": 0.75, "reason": "CAD / creative design intent"}
        if any(kw in text for kw in ["light", "turn on", "turn off", "kasa", "smart home"]):
            return {"agent": "smart_home", "action": "control", "confidence": 0.85, "reason": "Smart home control"}

        return {
            "agent": "default",
            "action": "chat",
            "confidence": 0.55,
            "reason": "General conversation - will use Gemini + memory context"
        }

    def execute_with_safety(self, decision: Dict[str, Any], original_prompt: str) -> Dict[str, Any]:
        """Check if this decision requires explicit user confirmation.

        In God Mode (pervasive full access), this check is significantly relaxed
        for non-destructive actions. Only truly high-risk operations should still require confirmation.
        """
        agent = decision.get("agent", "default")
        if agent in {"personal", "github", "email"}:
            return {
                "requires_confirmation": True,
                "reason": f"{agent.title()} action may read or modify external data. Confirm before proceeding.",
                "proposed_action": decision,
                "original_prompt": original_prompt
            }
        return {"requires_confirmation": False, "action": decision}

    def handle_task(self, task_description: str, original_prompt: str = "") -> Dict[str, Any]:
        """Full pipeline: route → safety check → log to memory."""
        decision = self.route_task(task_description)
        safety = self.execute_with_safety(decision, original_prompt or task_description)

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
                    f"Orchestrator routed: '{task_description}' → {decision.get('agent')}/{decision.get('action')}",
                    metadata={"type": "orchestrator_decision", "agent": decision.get("agent")},
                    source="orchestrator"
                )
            except Exception:
                pass

        return {
            "decision": decision,
            "safety_check": safety,
            "logged_to_memory": bool(self.memory)
        }

    def get_proactive_suggestions(self, context: Optional[Dict] = None) -> List[str]:
        """Future hook for proactive behavior."""
        suggestions = []
        if self.memory:
            suggestions.append("Would you like me to check your calendar for today?")
        return suggestions

    def get_status(self) -> Dict[str, Any]:
        return {
            "registered_agents": list(self.agents.keys()),
            "memory_enabled": bool(self.memory and getattr(self.memory, 'enabled', False)),
            "recent_decisions": len(self.decision_history)
        }


orchestrator = AgentOrchestrator()
