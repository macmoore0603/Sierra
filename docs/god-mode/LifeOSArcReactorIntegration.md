# Life OS in Arc Reactor (God Mode)

**Live in the 'all' waves:**

- LIFE ⚡ quick button in the bottom action bar of the 19-ring Arc Reactor dashboard.
- Reactive Life OS status bar (gold on black) showing:
  - Per-area pills with live scores + trend arrows (up/stable/down).
  - Truncated weekly brief from the LifeAreaAgent.
- Direct JSON-RPC `life_area` calls (get_state, weekly_brief, log_event) wired in server.py.
- Real persistence: events written to MemoryStore (user_preferences with life_area tags).

## How to use (after reactivation)
1. Open Sierra (Arc Reactor is the default hero view in God Mode).
2. Click the gold **LIFE ⚡** button.
3. Watch the bar populate with your 8 life areas + brief.
4. It also triggers a voice summary for full immersion.

## Code locations (local Tauri build)
- `tauri-app/ui/src/lib/components/ArcReactorDashboard.svelte` (button + bar + queryLifeOS + styles)
- `daemon/pilot/agents/life_area_agent.py` (core + persistence)
- `daemon/pilot/server.py` (JSON-RPC handler + registration)

This is the visible manifestation of "Sierra knows and improves every single area of my life" with pervasive God Mode (no off states, auto-force, full access).

Reactivate the app to see the latest.

*Part of the continuous 'do all' / auto-run session.*