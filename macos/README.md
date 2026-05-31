# Sierra — Native macOS App

A native SwiftUI/AppKit menu-bar build of Sierra. It runs as a status-bar app
("✨" icon), shows the Arc Reactor / JARVIS HUD UI, listens for the **"Hey Sierra"** wake word
via on-device speech recognition, and can connect to the Sierra daemon.

**Primary production daemon**: the Python one at `http://localhost:8785` (or LAN 0.0.0.0:8785)
started via `./run-sierra.sh --24-7` or the `com.sierra.pilot` launchd agent (KeepAlive).
This daemon includes the full God Mode orchestrator, Life OS (8 areas), 16+ plugins,
and 24/7 background operation.

The native Swift app is a first-class full-access native client alongside the
Tauri Arc Reactor (default hero view) and the mobile PWA. The Swift client can be
updated to point at the real daemon (SierraSocketClient + the JSON-RPC endpoints
on 8785). The shipped binary is `Sierra.app.zip` at the repo root.

## Files

| File | Purpose |
|------|---------|
| `Sierra/ContentView.swift` | App entry point (`SierraApp`), `AppDelegate` (status item + daily-briefing notifications), and the chat / wake-word UI driven by a `SierraViewModel`. |
| `Sierra/SierraSocketClient.swift` | Dependency-free Socket.IO (v5) / Engine.IO (v4) client over `URLSessionWebSocketTask` — the real-time link to the backend. |
| `Sierra/AudioStreamPlayer.swift` | Streams Sierra's voice (`audio_data`, 16-bit/24 kHz PCM) to the speakers via `AVAudioEngine`. |
| `Sierra/Item.swift` | SwiftData model. |
| `Sierra/Info.plist` | Bundle config + **full privacy usage descriptions** (TCC). |
| `Sierra/Sierra.entitlements` | App capabilities + **App Sandbox resource access**. |
| `Sierra/Assets.xcassets` | App icon and accent color. |

## God Mode / Full Access

In line with Sierra's [God Mode](../GOD_MODE.md) "every option access" design, the
native app is configured to request **every** OS-gated resource:

- **`Info.plist`** declares all `NS*UsageDescription` strings — microphone,
  speech recognition, camera, location, contacts, calendars, reminders, photos,
  media, Bluetooth, local network, Desktop/Documents/Downloads/volumes, Apple
  Events automation, HealthKit, HomeKit, Face ID, Siri, motion, and nearby
  interaction. Without these the app crashes the moment it touches the mic or
  speech recognizer. App Transport Security is opened
  (`NSAllowsArbitraryLoads` + `NSAllowsLocalNetworking`) so it can reach the
  local backend over cleartext `http://localhost:8000`.
- **`Sierra.entitlements`** grants the macOS App Sandbox resource entitlements:
  audio input, camera, Bluetooth/USB/serial, location, address book, calendars,
  photos library, user-selected / Downloads files, app-scope bookmarks, music /
  movies / pictures assets, network client + server, printing, and Apple Events
  automation.

After installing the app, finish granting access with the helper script:

```bash
bash ../scripts/macos-activate-permissions.sh
```

## Real-time connection to the backend

The app's voice loop is real-time **on-device**: `SFSpeechRecognizer` + `AVAudioEngine`
do continuous wake-word detection ("Hey Sierra") and live partial transcription with
no server round-trip.

**Voice (true real-time, streaming).** Pressing the mic — or saying "Hey Sierra" —
opens a live **Socket.IO** session to the backend (`SierraSocketClient`):

1. the app emits `start_audio`;
2. the backend's Gemini Live loop streams back `transcription` events
   (`{"sender": "User"|"Sierra", "text": ...}`), rendered into the chat as they
   arrive (the same speaker's bubble grows in place);
3. `audio_data` chunks (16-bit/24 kHz PCM) are played the instant they arrive via
   `AudioStreamPlayer`, so you hear Sierra speak in real time;
4. `stop_audio` ends the turn and the app resumes on-device wake-word listening.

The client speaks Engine.IO v4 / Socket.IO v5 directly over
`URLSessionWebSocketTask` — **no third-party packages**, nothing to add in Xcode.

**Text.** Typed messages can use the real Sierra daemon JSON-RPC / HTTP endpoints
on port 8785 (the same ones the Tauri UI and mobile PWA use). The daemon
(`daemon/pilot/server.py`) supports the full Life OS, plugins, God Mode, and
orchestrator. See `daemon/pilot/server.py` and the Tauri UI API client for the
current endpoints.

## Building & Running (Current Architecture)

1. Start the real 24/7 Sierra daemon (recommended):

```bash
cd /Users/user/Sierra   # or your clone
./run-sierra.sh --24-7
# or for pure background:
launchctl load -w ~/Library/LaunchAgents/com.sierra.pilot.plist
```

This gives you the full God Mode + Life OS + plugins on 8785.

2. Open `macos/Sierra/` (or the Xcode project that contains it) and build the
native app target.

3. The native app will then have the complete "give Sierra access to everything"
entitlements + privacy strings. Run the permissions helper once:

```bash
bash scripts/macos-activate-permissions.sh
```

Then drag the two canonical paths into every Privacy & Security pane:
- `/Applications/Sierra.app`
- The venv Python: `.../Sierra/daemon/.venv/bin/python`

After grants, the native HUD + the Tauri Arc Reactor (primary) will both be in
full God Mode with no artificial "off" states.

See the root `README.md`, `GOD_MODE.md`, `LIFE_AREAS.md`, and `daemon/pilot/`
for the current architecture. The Swift client is the native menu-bar / status-bar
experience; the Tauri Arc Reactor is the default immersive hero view.
