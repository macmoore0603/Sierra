#!/bin/bash
# macOS God Mode Permission Activation Helper for Sierra
# Run this to aggressively open all relevant Privacy & Security panes
# and get instructions for the exact paths to add.

set -e

echo "🔐 Sierra — God Mode macOS Permission Activation"
echo "=================================================="
echo ""

echo "This script will open every relevant Privacy & Security pane."
echo "After it runs, use the big 'ACTIVATE ALL PERMISSIONS NOW (God Mode)' button in the app."
echo ""

# Open main Privacy & Security pane
open "x-apple.systempreferences:com.apple.preference.security?Privacy" || true
sleep 1

# Specific panes (these anchors work on modern macOS)
panes=(
    "Privacy_Accessibility"
    "Privacy_ScreenCapture"
    "Privacy_Microphone"
    "Privacy_Camera"
    "Privacy_Automation"
    "Privacy_AllFiles"
    "Privacy_Contacts"
    "Privacy_Calendars"
    "Privacy_Reminders"
    "Privacy_Photos"
    "Privacy_LocationServices"
)

for pane in "${panes[@]}"; do
    echo "  → Opening $pane"
    open "x-apple.systempreferences:com.apple.preference.security?$pane" 2>/dev/null || true
    sleep 0.5
done

echo ""
echo "✅ Panes opened. Now in the Sierra app:" 
echo "1. Go to Settings → macOS Privacy & Security"
echo "2. Click the big gold 'ACTIVATE ALL PERMISSIONS NOW (God Mode)' button"
echo "3. Drag the two canonical paths into the open lists (especially Camera):"
echo "   - The installed Sierra app (e.g. /Applications/Sierra.app)"
echo "   - The backend Python / runtime process"

echo ""
echo "Run this script whenever you need a fresh start on permissions."
