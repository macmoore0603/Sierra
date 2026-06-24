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

## Setup

```bash
cd mobile
npm install
npm start          # then scan the QR with Expo Go, or press i / a
```

## Connect to your computer

The backend defaults to **localhost only**. To let your phone reach it:

1. Start the backend bound to the LAN:
   ```bash
   cd backend
   SIERRA_HOST=0.0.0.0 python server.py
   # or: python -m uvicorn server:app_socketio --host 0.0.0.0 --port 8000
   ```
2. Find your computer's LAN IP: `ipconfig getifaddr en0` (macOS).
3. In the app → **Settings**, set the server address to `http://<that-ip>:8000`
   and tap **Test**, then **Save & Connect**.
4. Make sure the phone and computer are on the **same Wi-Fi network**.

> Security note: binding to `0.0.0.0` exposes the Sierra backend (which runs in
> God Mode with relaxed confirmations) to everyone on your network. Only do this
> on a trusted network.
