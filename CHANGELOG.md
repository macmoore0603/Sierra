# Sierra Changelog

## [Unreleased] - Pervasive God Mode Update (late May 2026)

### God Mode / Full Access Experience
- Made God Mode pervasive and automatic as the default and only experience.
- UI never shows "off", restricted, or warning states for core features (voice wake "Hey Sierra", gestures, face auth, camera presence, background processes) when full access is enabled.
- Added auto-force logic (onMount + delay + defensive guards) so voice, gestures, presence, and connection states are powered on immediately on app load.
- DAEMON / background connection indicator now shows "GOD" in full access mode and is force-tappable.
- Titlebar and HUD elements use "GOD" branding instead of "offline" / "connecting".
- Added dedicated `GOD_MODE.md` documenting the full philosophy, auto-force implementation, canonical app rule, and macOS permission activation flow.
- Updated README, ROADMAP, and ARCHITECTURE to treat pervasive God Mode as a core, top-priority principle.
- One prominent "ACTIVATE ALL PERMISSIONS NOW (God Mode)" button + helper script for aggressive macOS TCC activation (Camera for gestures, Accessibility, Automation, Full Disk, Screen Recording, etc.).
- Strict "canonical app only" rule: users must only launch the installed production build; build artifacts are never launched directly.

### Other Improvements
- (Previous items from earlier development)

---

*See GOD_MODE.md for the complete philosophy and implementation details from the extended "do all" development sessions.*
