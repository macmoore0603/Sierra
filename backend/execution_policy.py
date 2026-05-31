"""
Real-time execution policy for Sierra's tool calls (God Mode).

Pure, dependency-free decision logic — deliberately importable without the
audio / Gemini / OpenCV stack so it can be unit-tested in isolation.

See GOD_MODE.md for the philosophy: God Mode runs tools in real time with no
confirmation friction, except for a small set of truly destructive operations.
"""

# Tools that remain confirmation-gated even in God Mode (destructive ops).
DEFAULT_CONFIRM_TOOLS = frozenset({
    "delete_file",
    "delete_directory",
    "delete_project",
    "factory_reset",
})


def requires_confirmation(tool_name, god_mode, confirm_tools=None, permissions=None):
    """Decide whether a tool call must pause for explicit human confirmation.

    Args:
        tool_name: the tool the model wants to run.
        god_mode: when True, run tools in real time (no confirmation) unless the
            tool is destructive.
        confirm_tools: iterable of tool names that always require confirmation,
            even in God Mode. Defaults to DEFAULT_CONFIRM_TOOLS when None.
        permissions: per-tool fallback map used when God Mode is off. A missing
            entry defaults to True (confirmation required) — fail safe.

    Returns:
        True  -> block and ask the user before executing.
        False -> execute immediately (real-time).
    """
    confirm = set(confirm_tools) if confirm_tools is not None else set(DEFAULT_CONFIRM_TOOLS)
    # Destructive ops are a hard gate — always confirm, even in God Mode and even
    # if a permission entry would otherwise allow them (GOD_MODE.md).
    if tool_name in confirm:
        return True
    # God Mode runs everything else in real time.
    if god_mode:
        return False
    # God Mode off: fall back to per-tool permissions (missing == confirm).
    return (permissions or {}).get(tool_name, True)
