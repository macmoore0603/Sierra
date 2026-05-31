"""
Sierra Context Helper

Easy utilities to work with long-term memory across the system.
Makes the Memory module immediately useful for context injection, logging, and agent reasoning.
"""

from typing import Optional, Dict, Any

try:
    from memory import memory as sierra_memory
except ImportError:
    sierra_memory = None


def get_relevant_context(query: str, max_length: int = 1800) -> str:
    """Return relevant long-term memory formatted for prompt injection."""
    if not sierra_memory or not getattr(sierra_memory, 'enabled', False):
        return ""
    try:
        ctx = sierra_memory.get_relevant_context(query, max_tokens=max_length)
        if ctx:
            return f"\n[Long-term Memory Context]\n{ctx}\n[End Memory Context]\n"
    except Exception:
        pass
    return ""


def add_to_memory(text: str, metadata: Optional[Dict[str, Any]] = None, source: str = "system") -> str:
    """Simple way to store something in long-term memory."""
    if sierra_memory:
        try:
            return sierra_memory.add_memory(text, metadata=metadata or {}, source=source)
        except Exception:
            pass
    return ""


def memory_enabled() -> bool:
    return bool(sierra_memory and getattr(sierra_memory, 'enabled', False))
