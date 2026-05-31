#!/usr/bin/env bash
#
# install-macos-autostart.sh — make Sierra start automatically at login.
#
# Sets up two LaunchAgents:
#   • com.macmoore.sierra.backend — runs the FastAPI/Socket.IO backend
#       (RunAtLoad + KeepAlive, so it starts at login and auto-restarts if it dies)
#   • com.macmoore.sierra.app     — opens the Sierra macOS app at login
#
# Usage:
#   scripts/install-macos-autostart.sh [PYTHON] [REPO_DIR] [APP_PATH]
#
#   PYTHON    python with the backend deps installed (default: ./.venv/bin/python or python3)
#   REPO_DIR  repo root (default: the repo this script lives in)
#   APP_PATH  installed app (default: /Applications/Sierra.app)
#
# Uninstall:  launchctl unload ~/Library/LaunchAgents/com.macmoore.sierra.{backend,app}.plist
set -euo pipefail

REPO_DIR="${2:-$(cd "$(dirname "$0")/.." && pwd)}"
PYTHON="${1:-}"
if [ -z "$PYTHON" ]; then
  if [ -x "$REPO_DIR/.venv/bin/python" ]; then PYTHON="$REPO_DIR/.venv/bin/python"; else PYTHON="$(command -v python3)"; fi
fi
APP_PATH="${3:-/Applications/Sierra.app}"
LA="$HOME/Library/LaunchAgents"; mkdir -p "$LA"

echo "Python : $PYTHON"
echo "Repo   : $REPO_DIR"
echo "App    : $APP_PATH"

cat > "$LA/com.macmoore.sierra.backend.plist" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>com.macmoore.sierra.backend</string>
  <key>ProgramArguments</key><array>
    <string>$PYTHON</string><string>-m</string><string>uvicorn</string>
    <string>server:app_socketio</string><string>--host</string><string>127.0.0.1</string><string>--port</string><string>8000</string>
  </array>
  <key>WorkingDirectory</key><string>$REPO_DIR/backend</string>
  <key>EnvironmentVariables</key><dict><key>PYTHONUNBUFFERED</key><string>1</string></dict>
  <key>RunAtLoad</key><true/>
  <key>KeepAlive</key><true/>
  <key>StandardOutPath</key><string>/tmp/sierra-backend.log</string>
  <key>StandardErrorPath</key><string>/tmp/sierra-backend.log</string>
</dict></plist>
PLIST

cat > "$LA/com.macmoore.sierra.app.plist" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>com.macmoore.sierra.app</string>
  <key>ProgramArguments</key><array><string>/usr/bin/open</string><string>$APP_PATH</string></array>
  <key>RunAtLoad</key><true/>
</dict></plist>
PLIST

for label in backend app; do
  launchctl unload "$LA/com.macmoore.sierra.$label.plist" 2>/dev/null || true
  launchctl load -w "$LA/com.macmoore.sierra.$label.plist"
done

echo "Loaded. Backend + app will now start at login."
launchctl list | grep sierra || true
