# Sierra — Native macOS App

A native SwiftUI/AppKit menu-bar build of Sierra. It runs as a status-bar app
("✨" icon), shows the Arc Reactor UI, listens for the **"Hey Sierra"** wake word
via on-device speech recognition, and talks to the Sierra backend at
`http://localhost:8000/chat`.

This is the native counterpart to the Electron app — the shipped binary is
`Sierra.app.zip` at the repo root.

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

**Text.** Typed messages use `http://localhost:8000/chat`
(`POST {"message": ...}` → `{"response": ...}`), served by
[`backend/server.py`](../backend/server.py) and backed by Gemini text generation.
Set `GEMINI_API_KEY` (and optionally `GEMINI_TEXT_MODEL`, default
`gemini-2.5-flash`) in the backend `.env`.

## Building

Open the `Sierra/` sources in Xcode (macOS target), or add them to the existing
Xcode project, then build and run. Start the backend first:

```bash
pip install -r requirements.txt          # from repo root
echo "GEMINI_API_KEY=AIza..." > .env
python backend/server.py                  # serves http://localhost:8000
```
