# Sierra Mobile

A React Native (Expo) companion app that **connects to and stays synced with the
Sierra desktop app** over your local network. It talks to the same backend the
desktop frontend uses — FastAPI + Socket.IO on port `8000` (`backend/server.py`).

## Screens

| Screen | What it does |
| --- | --- |
| **Dashboard** | Live JARVIS-style HUD: connection/sync status, voice-loop control (start/pause/stop the "Hey Sierra" session on your computer), last detected intent, smart-home (Kasa) devices, 3D-printer status, active project. |
| **Chat** | Text chat with Sierra via `POST /chat`. When a live voice session is running, your messages are pushed into it and the spoken transcript streams back here in real time. |
| **Agents** | Capability roster (Web, CAD, Printer, Smart Home, Calendar, GitHub) plus a live feed of every tool Sierra executes on your computer. |
| **Settings** | Set the desktop server address, test the connection, view diagnostics, and the exact command to expose the backend on your LAN. |

## How the sync works

- **REST** — `GET /status` (heartbeat) and `POST /chat` (`{message} → {response}`).
- **Socket.IO** — the app subscribes to the same events the desktop emits
  (`transcription`, `status`, `auth_status`, `tool_execution`, `kasa_devices`,
  `print_status_update`, `sierra_route`, `project_update`, `error`) and can send
  `start_audio` / `stop_audio` / `pause_audio` / `resume_audio` / `user_input`.

This means anything you say to Sierra on the computer shows up on the phone, and
anything you do on the phone is reflected on the computer.

## 📲 Get it on your phone

There are two ways, depending on whether you want the instant route or a real
installable app icon.

### Option A — Expo Go (instant, no build, no accounts)

Best for using it right now.

1. Install **Expo Go** on your phone: [iOS App Store](https://apps.apple.com/app/expo-go/id982107779) · [Google Play](https://play.google.com/store/apps/details?id=host.exp.exponent).
2. On the computer running Sierra:
   ```bash
   cd mobile
   ./scripts/get-on-phone.sh --with-backend
   ```
   (or `npm install && npm start` if you prefer to start the backend yourself).
3. **iPhone:** open the Camera app and point it at the QR code → tap the banner.
   **Android:** open Expo Go → *Scan QR code*.
4. The Sierra app loads and auto-discovers your computer on the Wi-Fi.

If your phone and computer are on different networks (or a locked-down Wi-Fi),
run `./scripts/get-on-phone.sh --tunnel` and the QR will work over the internet.

### Option B — Install a real standalone app (EAS Build)

Best for a permanent app icon you tap like any other app. This builds a signed
binary in Expo's cloud and gives you a **download link**.

```bash
cd mobile
npm install
npm install -g eas-cli
eas login          # free Expo account
eas init           # links the project (writes the EAS projectId)
npm run build:apk  # Android → downloadable .apk you install directly
# iOS:  npm run build:ios   (requires an Apple Developer account)
```

When the build finishes, EAS prints a URL (and emails it). Open that link on the
**Android** phone and tap the `.apk` to install. iOS installs go through
TestFlight/ad-hoc provisioning, which is why an Apple Developer account is needed.

> Why no pre-made file here? A signed `.ipa`/`.apk` is tied to *your* Apple /
> Google / Expo credentials and is produced by a cloud build, so it has to run
> from your account — the commands above are the one-time setup for that.

## Manual setup

```bash
cd mobile
npm install
npm start          # then scan the QR with Expo Go, or press i / a
```

## Connect to your computer

The backend defaults to **localhost only**. To let your phone reach it, start it
bound to the LAN (it then advertises itself via mDNS for auto-discovery):

```bash
cd backend
SIERRA_HOST=0.0.0.0 python server.py
# or: python -m uvicorn server:app_socketio --host 0.0.0.0 --port 8000
```

Then, on the same Wi-Fi network, just open the app:

1. **Automatic (recommended)** — the app auto-scans your Wi-Fi on launch and
   connects to the Sierra backend it finds. You can also tap **Auto-detect Sierra
   on Wi-Fi** in Settings (or the **Auto-detect** button on the Dashboard when
   offline). No IP address needed.
2. **Manual** — in **Settings**, enter `http://<computer-LAN-IP>:8000`
   (find it with `ipconfig getifaddr en0` on macOS), tap **Test**, then **Save**.

### How auto-discovery works
- The backend advertises an mDNS/Bonjour service `_sierra._tcp.local.`
  (`backend/discovery.py`) for native builds.
- In Expo Go, the app scans its own `/24` subnet for a host answering
  `GET /status` with the Sierra signature (`src/services/discovery.js`) — this
  works without any native modules.

> Security note: binding to `0.0.0.0` exposes the Sierra backend (which runs in
> God Mode with relaxed confirmations) to everyone on your network. Only do this
> on a trusted network.
