# God Mode Reference Implementations (Electron / React)

**This folder contains concrete, copy-pasteable React component skeletons and hooks** that implement the pervasive God Mode requirements from the extended "do all" / "everything in Sierra to have God Mode" sessions.

These directly address the open high-priority issues #6–#15.

## Philosophy (Recap from GOD_MODE.md)

- **Never show "off" states** for voice ("Hey Sierra"), gestures (MediaPipe hand tracking), face auth, camera/presence, daemon/background, or personal integrations when God Mode is active.
- **Auto-force on load**: Use `useEffect` + `onMount` + safe timeouts to set all core features to `enabled: true` / `active: true` immediately.
- **GOD branding everywhere**: DAEMON pill becomes "GOD" (tappable for force-reconnect). Titlebar/HUD show "GOD" badge. Status pills use gold accents.
- **One-button permissions**: Big gold "🔓 ACTIVATE ALL PERMISSIONS NOW (God Mode)" that triggers getUserMedia + opens panes + prints exact drag-in paths (see the existing `scripts/macos-activate-permissions.sh`).
- **Canonical app rule**: Only the installed production build gets full access.

## Files in This Folder

- `GodModeStatusPills.jsx` — Reusable status pills (DAEMON/GOD, HEY SIERRA LIVE, GESTURES GOD, PRESENCE). Tappable force actions. Never renders "off" in God Mode.
- `useGodModeAutoForce.js` — Custom hook + example `useEffect` patterns for App.jsx (auto-start hand tracking/gestures, face auth, voice wake, suppress restricted states).
- `GodModePermissionsButton.jsx` — The giant gold activation button + guidance panel. Drop into SettingsWindow.jsx.
- `GodModeHUDExample.jsx` — Example integration with existing modular HUD (Visualizer, ToolsModule, etc.).

## How to Integrate (Current Electron/React UI)

1. Copy the hook into `src/hooks/useGodModeAutoForce.js` (create hooks/ dir if needed).
2. In `src/App.jsx`:
   - Import the hook.
   - Call it early: `useGodModeAutoForce({ isGodMode: true })` (hardcode true for pervasive mode; later drive from settings).
   - Force `isHandTrackingEnabled = true`, face auth states, etc. on mount in God Mode.
3. Add `<GodModeStatusPills daemonStatus="GOD" ... />` near TopAudioBar or as a persistent top-right HUD element.
4. In `src/components/SettingsWindow.jsx`, replace or augment the Privacy section with `<GodModePermissionsButton />`.
5. Update electron/main.js title or add IPC for "GOD" badge if window chrome is customized.

## Theme (Black + Gold)

Use these CSS vars (add to index.css or tailwind):
```css
--bg-primary: #000000;
--accent-gold: #FFD700;
--accent-gold-dark: #DAA520;
--text-gold: #D4AF37;
--success: #C5A572; /* gold instead of green */
```

No blue leaks. Success / active states = gold.

## Relation to Local Tauri Work

The local `/Users/user/Sierra` (Tauri + Svelte) has a production Arc Reactor Dashboard (19-ring + HUD pills) with identical God Mode auto-force logic already implemented in ArcReactorDashboard.svelte + App.svelte + SettingsPanel.svelte. These React examples are the parallel implementation for this Electron repo so both codebases stay in sync with the "pervasive God Mode" vision.

## Next

- Implementers: Start with the hook (most impactful for "never off" complaints).
- Test: After adding, launch the app — voice/gestures/face should report LIVE/GOD immediately (even before mic/camera grants; show guidance to button instead of error).
- Update issues #6–#15 with implementation links once merged.

See GOD_MODE.md for the full philosophy and the open issues for acceptance criteria.

---

*Generated during continuous "keep going do all and auto run" session on https://github.com/macmoore0603/Sierra — 2026-05-31.*