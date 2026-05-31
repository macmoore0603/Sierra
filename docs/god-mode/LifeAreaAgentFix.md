# LifeAreaAgent Registration Fix (2026-05-31)

**Issue**: During "yes and fix all issues" wave, LifeAreaAgent was failing to register:

```
Failed to auto-register agent LifeAreaAgent: Can't instantiate abstract class LifeAreaAgent with abstract methods can_handle, get_capabilities, get_system_prompt, handle_task
```

**Root cause**: The agent was not implementing the four abstract methods required by `BaseAgent`.

**Fix**:
- Added `LIFE_AREA` to `AgentRole`.
- Rewrote `daemon/pilot/agents/life_area_agent.py` as a proper concrete subclass of `BaseAgent`.
- Preserved the direct `handle(task)` RPC interface used by the Arc Reactor "LIFE ⚡" button and status bar.
- The agent now registers cleanly via both discovery and explicit registration in `server.py`.

**Also fixed in same wave**:
- Vite port 1420 conflicts during long reactivation sessions (aggressive cleanup in reactivation commands).
- Remaining "OFF" language in Arc Reactor top bar when God Mode is active (wake pill, conditional buttons now suppressed or say "GOD").

After this fix + clean reactivation, Life OS features (including persistence via MemoryStore and the reactive Life OS bar in the Arc Reactor) should work end-to-end in God Mode.

*Part of the continuous "do all / fix all / reactivate app" session.*