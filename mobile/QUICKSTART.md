# Sierra Mobile — Quickstart (copy & paste)

Get the Sierra app running on your phone, synced with your computer. Verified:
`npm install` resolves, deps match Expo SDK 51, and the app bundles clean.

> Replace `~/Sierra` below if your repo lives elsewhere.

## 1. Get this branch

```bash
cd ~/Sierra
git fetch origin claude/mobile-app-sierra-sync-w2llqx
git checkout claude/mobile-app-sierra-sync-w2llqx
```

## 2. One command — backend on the LAN + app QR code

```bash
cd ~/Sierra/mobile
./scripts/get-on-phone.sh --with-backend
```

This installs the mobile deps (first run), makes sure the backend's discovery
dep is present, starts the Sierra backend listening on your whole network
(`0.0.0.0:8000`), and prints a QR code.

If your phone and computer are on a locked-down or different Wi-Fi:

```bash
./scripts/get-on-phone.sh --with-backend --tunnel
```

## 3. On your phone

1. Install **Expo Go** — [iPhone](https://apps.apple.com/app/expo-go/id982107779) · [Android](https://play.google.com/store/apps/details?id=host.exp.exponent)
2. **iPhone:** open Camera, point at the QR, tap the banner.
   **Android:** open Expo Go → *Scan QR code*.
3. The app opens and **auto-detects your computer** on the Wi-Fi. Done.

---

## Already run the backend yourself?

Skip `--with-backend` and just show the QR:

```bash
cd ~/Sierra/mobile && npm install && npm start
```

Then start the backend on the LAN in another terminal:

```bash
cd ~/Sierra/backend && SIERRA_HOST=0.0.0.0 python server.py
```

## Want a permanent installed app (not Expo Go)?

```bash
cd ~/Sierra/mobile
npm install -g eas-cli
eas login          # free Expo account
eas init           # writes the EAS projectId
npm run build:apk  # Android → downloadable .apk install link
```

## If it doesn't auto-connect

Open **Settings** in the app → tap **Auto-detect Sierra on Wi-Fi**, or type
`http://<computer-LAN-IP>:8000` manually. Find the IP with:

```bash
ipconfig getifaddr en0   # macOS
```
