"""
Sierra Agents Package

Foundation for multi-agent orchestration.

Future goals:
- Use LangGraph or CrewAI for complex workflows
- Specialized agents: CAD Agent, Web Agent, Memory Agent, Personal Integration Agent, Proactive Agent
- Coordinated planning + execution with safety gates
- Self-improvement through agent feedback loops

This package will become the brain for advanced, persistent, proactive behavior.
"""

from .orchestrator import AgentOrchestrator

__all__ = ["AgentOrchestrator"]
