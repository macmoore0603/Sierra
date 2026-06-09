"""
Sierra LLM Package

Shared clients for large language model providers used by Sierra's agentic
capabilities. Currently provides an OpenRouter client (Claude Opus by default).
"""

from .openrouter_client import OpenRouterClient, openrouter_client

__all__ = ["OpenRouterClient", "openrouter_client"]
