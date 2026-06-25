#!/usr/bin/env bash
#
# Get Sierra onto your phone the fast way (Expo Go + QR code).
#
#   1. Install "Expo Go" from the App Store / Google Play on your phone.
#   2. Run this script on the computer running the Sierra desktop app.
#   3. Scan the QR code it prints with the phone camera (iOS) or the Expo Go
#      app (Android). The Sierra app opens instantly — no build, no signing.
#
# The app then auto-discovers the Sierra backend on your Wi-Fi. Make sure the
# backend is running with SIERRA_HOST=0.0.0.0 (see --with-backend below).
#
# Usage:
#   ./scripts/get-on-phone.sh                 # just the app dev server (LAN)
#   ./scripts/get-on-phone.sh --tunnel        # use Expo tunnel (any network)
#   ./scripts/get-on-phone.sh --with-backend  # also start the backend on the LAN

set -e
cd "$(dirname "$0")/.."   # mobile/

MODE="lan"
WITH_BACKEND=0
for arg in "$@"; do
  case "$arg" in
    --tunnel) MODE="tunnel" ;;
    --with-backend) WITH_BACKEND=1 ;;
  esac
done

if [ ! -d node_modules ]; then
  echo "==> Installing dependencies (first run)…"
  npm install
fi

if [ "$WITH_BACKEND" = "1" ]; then
  echo "==> Ensuring the backend's LAN-discovery dep (zeroconf) is installed…"
  python -c "import zeroconf" 2>/dev/null || python -m pip install zeroconf
  echo "==> Starting Sierra backend on the LAN (0.0.0.0:8000)…"
  ( cd ../backend && SIERRA_HOST=0.0.0.0 python server.py ) &
  BACKEND_PID=$!
  trap 'kill $BACKEND_PID 2>/dev/null || true' EXIT
  sleep 2
fi

echo "==> Starting Expo. Scan the QR code with your phone."
if [ "$MODE" = "tunnel" ]; then
  exec npx expo start --tunnel
else
  exec npx expo start
fi
