# God Mode — Pervasive Every Option Access

This document captures the philosophy and implementation goals for **pervasive God Mode** in Sierra, as developed during extended "do all" sessions.

## Core Principle

**In God Mode, nothing in Sierra is ever "off".**

When full access is active (the default and permanent state in this build):
- The UI **never** displays restricted, disabled, "off", or warning states for core capabilities.
- Voice ("Hey Sierra" wake word), gestures, face authentication, camera presence, background processes, and personal integrations are **always active** on app load via auto-force logic.
- High-privilege actions have minimal or zero extra confirmation friction.

## Auto-Force on Load

On every app startup in God Mode:
- Voice wake listener is automatically started.
- Gestures (MediaPipe or equivalent) are enabled.
- Camera/presence is treated as available (no "CAMERA OFF").
- Full system and personal access is assumed (subject only to OS-level grants).

The implementation uses defensive patterns (onMount + delay + try/catch) to avoid early crashes while ensuring the powered-on state is reflected immediately in the UI.

## Permission Activation Flow (macOS Focus)

Even with God Mode logic, the underlying OS still requires initial grants for camera, microphone, accessibility (automation), full disk, screen recording, etc.

### One-Click Activation

The app provides a single prominent button:

**🔓 ACTIVATE ALL PERMISSIONS NOW (God Mode)**

This button:
- Triggers getUserMedia for Camera + Mic (so Sierra appears in the system lists).
- Instructs the user on the exact paths to drag into the open Privacy panes.

### Recommended Paths (Canonical App Rule)

1. The installed production Sierra app (e.g. `/Applications/Sierra.app` or equivalent).
2. The backend Python / runtime process.

### Helper Script

A dedicated privacy activation script (to be added or referenced here) that:
- Resets relevant TCC entries.
- Aggressively triggers permission requests.
- Opens every relevant Privacy & Security pane.

Run it for a clean start on permissions.

**Critical Rule**: Only ever launch the canonical installed production build. Build artifacts are never launched by end users.

## Impact on Safety & Architecture

- Safety gates in the orchestrator and integrations are **relaxed** for non-destructive actions in God Mode.
- Truly destructive actions (recursive deletes, etc.) still have strong confirmation, even in God Mode.
- The UI layer is designed to reflect full power at all times (no misleading "off" indicators).

## Implementation Notes (from Development Sessions)

- Auto-force logic lives in the frontend UI layer and runs early but safely (onMount + timeout).
- The DAEMON / background connection pill shows "GOD" and is force-tappable.
- Titlebar / HUD elements use "GOD" branding instead of "offline" or "connecting" when full access is enabled.
- All God Mode changes are permanent for this local/personal build — no toggles back to restricted mode.

## Related Documents

- [ARCHITECTURE.md](./ARCHITECTURE.md) — God Mode philosophy section
- [ROADMAP.md](./ROADMAP.md) — Pervasive God Mode as top priority
- macOS privacy activation script (to be added)

---

*This is the result of the extended "do all" / "everything in Sierra to have God Mode" development work. The goal is zero friction and full power by default.*
