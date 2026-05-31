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
| `Sierra/ContentView.swift` | App entry point (`SierraApp`), `AppDelegate` (status item + daily-briefing notifications), and the chat / wake-word UI. |
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

For responses it calls the backend at `http://localhost:8000/chat`
(`POST {"message": ...}` → `{"response": ...}`). That REST route is served by
[`backend/server.py`](../backend/server.py) and is backed by Gemini text generation —
a fast request/response turn. Set `GEMINI_API_KEY` (and optionally `GEMINI_TEXT_MODEL`,
default `gemini-2.5-flash`) in the backend `.env`.

> **Full streaming voice (Gemini Live audio):** the backend also exposes a true
> real-time audio pipeline over **Socket.IO** (`start_audio` → `transcription` /
> `audio_data` events), which the Electron frontend uses. Wiring the native app to
> that pipeline (via a Socket.IO Swift client) is a future enhancement; today the
> native app uses on-device transcription + the `/chat` REST turn.

## Building

Open the `Sierra/` sources in Xcode (macOS target), or add them to the existing
Xcode project, then build and run. Start the backend first:

```bash
pip install -r requirements.txt          # from repo root
echo "GEMINI_API_KEY=AIza..." > .env
python backend/server.py                  # serves http://localhost:8000
```
