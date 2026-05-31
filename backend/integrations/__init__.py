"""
Sierra Integrations Package

Foundation for deep, safe personal ecosystem integrations.

Planned integrations:
- Google Calendar & Gmail
- GitHub
- Notion / Linear / other productivity tools
- Local files + project memory
- Location-aware context

All integrations must respect:
- User confirmation for write/modify actions
- tool_permissions in settings.json
- Logging to SierraMemory for auditability and self-improvement

This package will grow into a clean, consistent interface layer.
"""

from .base import BaseIntegration

__all__ = ["BaseIntegration"]
