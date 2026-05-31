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

## Building

Open the `Sierra/` sources in Xcode (macOS target), or add them to the existing
Xcode project, then build and run. The app expects the Sierra backend to be
running locally (`backend/server.py`).
