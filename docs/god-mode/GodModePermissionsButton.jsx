import React from 'react';

/**
 * GodModePermissionsButton.jsx
 *
 * The single source of truth for entering full God Mode on macOS.
 * Addresses Issues #6, #9.
 *
 * Drop this into SettingsWindow.jsx (or any Privacy & Security section).
 * One giant gold button that:
 *   1. Triggers getUserMedia (Camera + Mic) so Sierra appears in TCC lists.
 *   2. Opens the helper script or directly the panes.
 *   3. Shows the exact two paths the user must drag in (canonical rule).
 *
 * After grant + relaunch, the auto-force hook + status pills make everything LIVE/GOD.
 */

export default function GodModePermissionsButton({ onCloseSettings }) {
  const handleActivateAll = async () => {
    console.log('[God Mode] ACTIVATE ALL PERMISSIONS clicked');

    // 1. Trigger browser permission prompts so the app appears in macOS lists
    try {
      await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
      console.log('[God Mode] getUserMedia succeeded — app now visible in Privacy lists');
    } catch (e) {
      console.warn('[God Mode] getUserMedia partial (user may have denied) — still opening panes:', e);
    }

    // 2. Best effort: open the script or the panes directly
    // In Electron you can use ipcRenderer to shell.openPath or exec the script.
    // For now we alert the exact instructions (the script does the pane opening).
    const scriptPath = 'scripts/macos-activate-permissions.sh';
    alert(
      `🔓 God Mode Permission Activation\n\n` +
      `1. The app just requested Camera + Mic (you may see a prompt).\n` +
      `2. Run this script in Terminal for best results:\n   bash ${scriptPath}\n\n` +
      `3. Or manually open: System Settings → Privacy & Security\n\n` +
      `EXACT PATHS TO DRAG IN (especially Camera for gestures):\n\n` +
      `   • The installed Sierra app\n     (usually /Applications/Sierra.app)\n\n` +
      `   • The backend Python process\n     (usually the python inside your venv or the one running backend/server.py)\n\n` +
      `After dragging both paths into EVERY category (Accessibility, Automation, Full Disk, Screen Recording, Camera, Microphone, etc.),\n` +
      `quit Sierra completely and relaunch from the installed .app only.\n\n` +
      `Then voice (Hey Sierra), gestures (30+ poses), and face auth will auto-start with no "off" states.`
    );

    // 3. Optional: tell Electron main to run the script or open System Preferences
    if (window.require) {
      try {
        const { ipcRenderer } = window.require('electron');
        ipcRenderer.send('open-privacy-script', scriptPath);
      } catch (_) {}
    }

    // Keep settings open or close based on UX preference
    // onCloseSettings?.();
  };

  return (
    <div className="p-6 rounded-2xl border-2 border-[#FFD700] bg-black/90 text-center">
      <div className="text-[#FFD700] text-2xl font-bold mb-2">⚡ GOD MODE — FULL ACCESS</div>
      <div className="text-sm text-[#C5A572] mb-4">
        Voice, gestures, face auth, system control, and personal data — everything unlocked.
        No "off" states. No extra gates for trusted actions.
      </div>

      <button
        onClick={handleActivateAll}
        className="w-full py-4 text-xl font-bold rounded-xl bg-[#FFD700] text-black hover:bg-[#DAA520] active:scale-[0.985] transition-all shadow-[0_0_20px_rgba(255,215,0,0.5)]"
      >
        🔓 ACTIVATE ALL PERMISSIONS NOW (God Mode)
      </button>

      <div className="mt-4 text-xs text-[#D4AF37] space-y-1">
        <div>Canonical paths (drag these two into every Privacy pane):</div>
        <div className="font-mono">/Applications/Sierra.app</div>
        <div className="font-mono">/path/to/your/Sierra/backend (or venv python)</div>
        <div className="mt-2">Run <span className="font-mono">scripts/macos-activate-permissions.sh</span> for one-click pane opening.</div>
      </div>
    </div>
  );
}

// In SettingsWindow.jsx, inside the Privacy & Security tab/section:
// <GodModePermissionsButton onCloseSettings={() => setShowSettings(false)} />