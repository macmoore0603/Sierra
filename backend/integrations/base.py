"""
BaseIntegration - Common interface for all personal ecosystem integrations.

Provides:
- Consistent structure
- Built-in safety/confirmation support
- Memory logging hooks
- Easy extension for Calendar, Gmail, GitHub, etc.
"""

from typing import Dict, Any, Optional
from abc import ABC, abstractmethod

try:
    from memory import memory as sierra_memory
except ImportError:
    sierra_memory = None


class BaseIntegration(ABC):
    """Abstract base for all Sierra personal integrations."""

    def __init__(self, name: str):
        self.name = name
        self.memory = sierra_memory

    @abstractmethod
    def can_handle(self, intent: str) -> bool:
        """Return True if this integration can handle the given intent."""
        pass

    @abstractmethod
    def execute(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the action. Should return result dict."""
        pass

    def requires_confirmation(self, action: str) -> bool:
        """Override to mark sensitive actions that need user approval."""
        sensitive_actions = {"create", "send", "update", "delete", "modify"}
        return any(s in action.lower() for s in sensitive_actions)

    def log_to_memory(self, message: str, metadata: Optional[Dict] = None):
        if self.memory:
            try:
                self.memory.add_memory(message, metadata=metadata or {}, source=self.name)
            except Exception:
                pass

    def safe_execute(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Wrapper that adds confirmation flag + memory logging."""
        result = self.execute(action, params)
        self.log_to_memory(f"{self.name} executed: {action}", {"action": action})
        if self.requires_confirmation(action):
            result["requires_user_confirmation"] = True
        return result
