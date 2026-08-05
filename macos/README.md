# Sierra — Native macOS App

A native SwiftUI/AppKit menu-bar build of Sierra. It runs as a status-bar app
("✨" icon), shows the Arc Reactor UI, listens for the **"Hey Sierra"** wake word
via on-device speech recognition, and talks to the Sierra backend at
`http://localhost:8000/chat`.

This is the native counterpart to the Electron app.

> **`Sierra.app.zip` at the repo root is not this app.** That bundle is the
> Tauri/Rust build (`CFBundleIdentifier com.sierraos.app`, executable
> `sierra-os`, no SwiftUI symbols in it). Building the target here produces a
> separate `Sierra.app` with bundle id `com.macmoore.Sierra`.

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

There are two voice modes, and they are mutually exclusive because only one of
them can hold the microphone.

**Wake word (default).** `SFSpeechRecognizer` transcribes on-device, the wake
word starts a capture, a short silence ends it, and the text goes to `/chat`.
The reply is spoken with the system voice. No audio leaves the machine.

**Live session (Settings → Live Voice).** Hands the mic to the backend and
streams:

1. the app emits `start_audio`;
2. the backend's Gemini Live loop streams back `transcription` events
   (`{"sender": "User"|"Sierra", "text": ...}`), rendered into the chat as they
   arrive (the same speaker's bubble grows in place);
3. `audio_data` chunks (16-bit/24 kHz PCM) play the instant they arrive via
   `AudioStreamPlayer`;
4. `stop_audio` ends the session and the on-device wake-word loop resumes.

While a live session runs, the local recogniser is torn down and local TTS is
suppressed — otherwise both would capture the same mic and Sierra would answer
twice, over itself.

The client speaks Engine.IO v4 / Socket.IO v5 directly over
`URLSessionWebSocketTask` — **no third-party packages**, nothing to add in Xcode.

**Text.** Typed messages use `http://localhost:8000/chat`
(`POST {"message": ...}` → `{"response": ...}`), served by
[`backend/server.py`](../backend/server.py) and backed by Gemini text generation.
Set `GEMINI_API_KEY` (and optionally `GEMINI_TEXT_MODEL`, default
`gemini-2.5-flash`) in the backend `.env`.

## Building

```bash
open macos/Sierra.xcodeproj      # then ⌘R
```

Or from the command line:

```bash
xcodebuild -project macos/Sierra.xcodeproj -scheme Sierra -configuration Debug build
```

The target is configured with:

| Setting | Value |
|---|---|
| Bundle identifier | `com.macmoore.Sierra` (matches the `keychain-access-groups` in the entitlements) |
| Deployment target | macOS 14.0 — required by `Item.swift`, which uses SwiftData's `@Model` |
| Info.plist | `Sierra/Info.plist`, merged with the generated bundle keys (`GENERATE_INFOPLIST_FILE = YES`), so the usage descriptions survive |
| Entitlements | `Sierra/Sierra.entitlements` |
| Signing | Automatic, hardened runtime on |

No packages to resolve — every framework used (SwiftUI, AppKit, AVFoundation,
Speech, SwiftData, UserNotifications) ships with the OS and is linked
automatically from its `import`. Set your team in **Signing & Capabilities** on
first build.

Start the backend first, or the app launches with nothing to talk to:

```bash
pip install -r requirements.txt          # from repo root
echo "GEMINI_API_KEY=AIza..." > .env
python backend/server.py                  # serves http://localhost:8000
```
