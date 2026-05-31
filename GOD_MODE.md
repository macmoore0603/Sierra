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

A dedicated privacy activation script lives at `scripts/macos-activate-permissions.sh`. It:
- Opens every relevant Privacy & Security pane.
- Gives clear drag-in instructions.

Run it for a clean start on permissions.

**Critical Rule**: Only ever launch the canonical installed production build. Build artifacts are never launched by end users.

## Impact on Safety & Architecture

- Safety gates in the orchestrator and integrations are **relaxed** for non-destructive actions in God Mode.
- Truly destructive actions (recursive deletes, etc.) still have strong confirmation, even in God Mode.
- The UI layer is designed to reflect full power at all times (no misleading "off" indicators).

### Real-time execution (implemented)

Tool calls now **execute the instant the model emits them** — no confirmation
round-trip blocks the audio loop. This is wired in `backend/sierra.py`
(`AudioLoop.god_mode` / `confirm_tools`) and configured in `backend/server.py`:

- `settings.json` → `"god_mode": true` (default) runs every tool immediately.
- `settings.json` → `"confirm_tools": [...]` is the only allow-list that still
  pauses for an explicit OK — reserved for truly destructive ops
  (`delete_file`, `delete_directory`, `delete_project`, `factory_reset`).
- Set `"god_mode": false` to fall back to per-tool `tool_permissions`
  (confirmation required by default).

## Implementation Notes (from Development Sessions)

- Auto-force logic lives in the frontend UI layer and runs early but safely (onMount + timeout).
- The DAEMON / background connection pill shows "GOD" and is force-tappable.
- Titlebar / HUD elements use "GOD" branding instead of "offline" or "connecting" when full access is enabled.
- All God Mode changes are permanent for this local/personal build — no toggles back to restricted mode.

## Reference React/Electron Implementation (Issues #6–#15)

**Concrete, ready-to-integrate code now lives in `docs/god-mode/`**.

These files turn the philosophy into actual components and hooks for the current Electron + React frontend (src/App.jsx + components/):

- `docs/god-mode/useGodModeAutoForce.js` — The core hook. Call once in App.jsx. Forces gestures (hand tracking), face auth, video/presence, and voice wake to powered-on states on mount and every reconnect. Never lets UI show "off". Directly solves the "gestures are off", "wake is off", "camera says off" reports.
- `docs/god-mode/GodModeStatusPills.jsx` — Four always-gold pills: DAEMON:GOD (tappable), HEY SIERRA:LIVE, GESTURES:GOD, PRESENCE:PRESENT + GOD MODE badge. Drop near TopAudioBar or as persistent HUD. No "off" rendering path exists in God Mode.
- `docs/god-mode/GodModePermissionsButton.jsx` — The giant gold "🔓 ACTIVATE ALL PERMISSIONS NOW (God Mode)" button + exact path instructions + script reference. Paste into SettingsWindow.jsx Privacy section.
- `docs/god-mode/GodModeHUDExample.jsx` — Shows how to wire the pills into the existing modular chrome (title bar + bottom indicators) so the whole app feels like full power.
- `docs/god-mode/README.md` — Integration guide + theme rules (black + metallic gold, no blue success states).

### Quick Integration Steps
1. Copy the hook and components into src/ (create hooks/ if desired).
2. Add the hook call near the top of App.jsx useEffects.
3. Replace any old toggle buttons or status text for gestures/voice with the new pills or forceGodModeFeature() redirect.
4. Drop the PermissionsButton into SettingsWindow.jsx.
5. Rebuild / restart — in God Mode the UI now lies to the user in the best way: everything looks and behaves LIVE from second one.

See the individual files for copy-paste snippets and comments linking back to the exact user quotes that drove them ("i want everything in sierra to have god mode", "never show off", "DAEMON is off", etc.).

## Native macOS Swift Client (Full Access)

Sierra also ships a native SwiftUI/AppKit menu-bar + Arc Reactor HUD app
(`macos/Sierra/`). It is configured with the complete "give Sierra access to
everything" treatment:

- **Info.plist**: 35+ `NS*UsageDescription` keys (microphone, speech recognition,
  camera, location variants, contacts, calendars, reminders, photos, local
  network, Apple Events automation, HealthKit, HomeKit, Face ID, etc.) plus
  open ATS for local networking.
- **Sierra.entitlements**: All relevant App Sandbox resource entitlements
  (device.audio-input, device.camera, personal-information.*, files.*,
  assets.*, network.client + server, automation.apple-events, etc.).
- No `com.apple.security.app-sandbox` key — the app remains unsandboxed for
  maximum God Mode reach (Apple Events, Full Disk, Accessibility, etc.).

After build/install, run `scripts/macos-activate-permissions.sh` and drag the
two canonical paths (`/Applications/Sierra.app` and the daemon venv Python)
into every Privacy & Security pane. The native HUD then participates in the
same pervasive God Mode rules as the primary Tauri Arc Reactor (no "off"
states for voice, gestures, presence, or system control when full access is
granted).

This gives users a lightweight status-bar native experience while the Tauri
Arc Reactor remains the default immersive hero view.

## Related Documents

- [ARCHITECTURE.md](./ARCHITECTURE.md) — God Mode philosophy section
- [ROADMAP.md](./ROADMAP.md) — Pervasive God Mode as top priority
- `scripts/macos-activate-permissions.sh` — One-command pane opener + instructions
- `macos/README.md` — Details on the native Swift full-access app
- Open issues #6–#15 + #29 on GitHub (implementation tracking)

---

*This is the result of the extended "do all" / "everything in Sierra to have God Mode" development work. The goal is zero friction and full power by default.*
