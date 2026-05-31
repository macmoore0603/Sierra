"""
CalendarIntegration - Example implementation of a personal integration.

This is a stub that demonstrates how to build real integrations on top of BaseIntegration.
In a real implementation, this would use the Google Calendar API (with OAuth + confirmation flows).

Shows the pattern for future integrations (Gmail, GitHub, etc.).
"""

from typing import Dict, Any, List
from datetime import datetime, timedelta

from .base import BaseIntegration


class CalendarIntegration(BaseIntegration):
    def __init__(self):
        super().__init__(name="calendar")

    def can_handle(self, intent: str) -> bool:
        intent = intent.lower()
        return any(kw in intent for kw in ["calendar", "schedule", "event", "meeting", "remind"])

    def execute(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Stub implementation. Replace with real Google Calendar calls."""
        action = action.lower()

        if action == "get_events":
            # Placeholder response
            return {
                "status": "success",
                "events": [
                    {"time": "10:00", "title": "Team standup"},
                    {"time": "14:30", "title": "Project review"}
                ],
                "message": "Here are your upcoming events (stub data)"
            }

        if action == "create_event":
            title = params.get("title", "New event")
            # In real version: call Google Calendar API here
            self.log_to_memory(f"Created calendar event: {title}", {"action": "create_event"})
            return {
                "status": "success",
                "message": f"Event '{title}' created (stub). In production this would call Google Calendar.",
                "requires_user_confirmation": True  # Safety: always confirm creation
            }

        return {
            "status": "error",
            "message": f"Unknown calendar action: {action}"
        }

    def get_upcoming_events(self, days: int = 1) -> List[Dict]:
        """Convenience method."""
        result = self.execute("get_events", {})
        return result.get("events", [])
