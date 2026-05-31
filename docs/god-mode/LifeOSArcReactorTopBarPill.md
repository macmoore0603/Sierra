---
title: LIFE OS Top Status Bar Pill — Arc Reactor (Tauri Svelte)
date: 2026-05-31
description: The always-visible, clickable, gold "LIFE OS XX%" pill in the Arc Reactor top bar. God Mode only. Auto-populates from LifeAreaAgent. Fulfills "improve every single area of my life".
---

# LIFE OS Top Status Bar Pill (Arc Reactor)

**Status:** Implemented in local Tauri/Svelte ArcReactorDashboard.svelte (v0.8.0 session 2026-05-31)

**User intent:** Make Life OS a constant, scannable, clickable gold presence in the hero view (Arc Reactor) alongside DAEMON GOD and HEY SIERRA GOD. Zero OFF states when full_access_enabled.

## Behavior (God Mode)
- Only rendered when `$settings.advanced?.full_access_enabled === true`
- Shows dynamic "LIFE OS {lifeOverallScore}%" (live average across the 8 areas)
- Click anywhere on the pill → `queryLifeOS()` (refreshes scores + weekly brief + voices the state)
- Auto-triggers ~1.8s after dashboard mount in God Mode (graceful fallback sample data if agent still loading)
- Lower LIFE OS bar (detailed 8-area pills + brief) appears automatically when data is present
- No "OFF", no toggles, no warnings — matches the pervasive God Mode contract

## Top Bar Code (exact, from ArcReactorDashboard.svelte)

```svelte
<!-- Life OS — first-class in God Mode (pervasive "improve every single area of my life") -->
<span
  class="tb-pill life-pill"
  class:on={$settings.advanced?.full_access_enabled}
  onclick={() => queryLifeOS()}
  title="Click to refresh Life OS across all 8 areas"
>
  <span class="dot"></span>
  {#if $settings.advanced?.full_access_enabled}
    LIFE OS
    {#if lifeOverallScore > 0}
      <span class="score {lifeOverallScore >= 75 ? 'high' : lifeOverallScore >= 55 ? 'med' : 'low'}">{lifeOverallScore}%</span>
    {/if}
  {/if}
</span>
```

## Reactive State + Handler (excerpt)

```ts
let lifeBrief = $state("");
let lifeAreas = $state<Record<string, any>>({});
let lifeBusy = $state(false);
let lifeInitializing = $state(false);
let lifeOverallScore = $state(0);
let lifeNeedsAttention = $state("");

async function queryLifeOS() {
  lifeBusy = true;
  try {
    const stateRes = await call("life_area", { action: "get_state" });
    if (stateRes?.areas) {
      lifeAreas = stateRes.areas;
      const scores = Object.values(stateRes.areas).map((a: any) => a.score || 0);
      lifeOverallScore = scores.length > 0 ? Math.round(scores.reduce((sum, s) => sum + s, 0) / scores.length) : 0;
      // ... lowest area for attention hint
    }
    const briefRes = await call("life_area", { action: "weekly_brief" });
    if (briefRes?.brief) lifeBrief = briefRes.brief;
    session.sendCommand("Give me the current state of my life across all 8 areas");
  } catch (e) {
    // graceful fallback sample data
    lifeAreas = { health_fitness: { label: "Health & Fitness", score: 68, trend: "up" }, ... };
  } finally {
    lifeBusy = false;
  }
}

// Auto-surface on God Mode load
onMount(() => {
  setTimeout(() => {
    if (!Object.keys(lifeAreas).length && !lifeBusy) {
      lifeInitializing = true;
      queryLifeOS().catch(() => { /* fallback */ }).finally(() => lifeInitializing = false);
    }
  }, 1800);
});
```

## Backend (LifeAreaAgent + server.py)
- Proper `BaseAgent` subclass with `AgentRole.LIFE_AREA`
- Implements `can_handle`, `get_capabilities`, `get_system_prompt`, `handle_task` (fixed abstract class crash)
- Rich direct methods: `get_state`, `log_event`, `suggest`, `weekly_brief`, `proactive_tick`
- JSON-RPC handler `_handle_life_area` in `server.py:967`
- Registered explicitly in orchestrator + server startup
- Memory persistence: `memory.set_preference("life_area:" + area, ...)` with tags

See:
- `daemon/pilot/agents/life_area_agent.py`
- `daemon/pilot/server.py` (registration + handler)
- `daemon/pilot/agents/orchestrator.py`
- `LIFE_AREAS.md` (8-area model)

## Next (tracked in #21)
- Pull real data sources into the 8 areas (finance plugin, Apple Health via permissions, calendar, etc.)
- Proactive nudges from orchestrator when any area < threshold
- Dedicated Life OS modal / deeper cards in Arc Reactor
- iPhone PWA parity for the pill + brief
- Voice-first "Sierra, state of my life" fast path

## Related Issues
- #19 (Life OS Umbrella)
- #11, #15 (never show OFF states + persistent GOD indicators)
- #6 (pervasive God Mode)
- #17/#18 (Health + Finance first verticals)

This is the visible, always-on surface for the user's core request: "i want sierra to know and improve every single area of my life."
