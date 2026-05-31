import React from 'react';

/**
 * GodModeStatusPills.jsx
 * 
 * Reusable, always-powered-on status indicators for pervasive God Mode.
 * Addresses Issues #6, #8, #12, #15.
 * 
 * In God Mode (the only mode):
 * - Never renders "off", "disabled", or warning states for core features.
 * - DAEMON pill always shows "GOD" (or "LIVE") and is tappable to force-reconnect.
 * - All pills use gold accents on black.
 * - Clicking Voice/Gestures/Presence surfaces the God Mode Permissions button guidance.
 */

export default function GodModeStatusPills({
  daemonStatus = 'GOD',
  voiceStatus = 'LIVE',
  gesturesStatus = 'GOD',
  presenceStatus = 'PRESENT',
  onForceReconnect,
  onOpenPermissions,
  className = '',
}) {
  const pillBase = 'px-3 py-1 rounded-full text-xs font-semibold flex items-center gap-1.5 cursor-pointer transition-all active:scale-95';
  const gold = 'bg-[#FFD700] text-black hover:bg-[#DAA520]';
  const darkGold = 'bg-[#C5A572] text-black hover:bg-[#D4AF37]';

  return (
    <div className={`flex flex-wrap gap-2 ${className}`}>
      {/* DAEMON / GOD pill - tappable for force reconnect */}
      <div
        onClick={() => onForceReconnect?.()}
        className={`${pillBase} ${gold} shadow-[0_0_8px_rgba(255,215,0,0.6)]`}
        title="God Mode active. Tap to force daemon reconnect."
      >
        <span>⚡</span>
        <span>DAEMON: {daemonStatus}</span>
      </div>

      {/* Voice Wake - always LIVE in God Mode */}
      <div
        onClick={() => onOpenPermissions?.()}
        className={`${pillBase} ${darkGold}`}
        title="Hey Sierra wake word auto-active in God Mode. Tap for permissions."
      >
        <span>🎤</span>
        <span>HEY SIERRA: {voiceStatus}</span>
      </div>

      {/* Gestures - always GOD (MediaPipe hand tracking) */}
      <div
        onClick={() => onOpenPermissions?.()}
        className={`${pillBase} ${darkGold}`}
        title="30+ gesture engine auto-active in God Mode (Camera required). Tap for permissions."
      >
        <span>✋</span>
        <span>GESTURES: {gesturesStatus}</span>
      </div>

      {/* Presence / Camera - always PRESENT (no CAMERA OFF ever in God Mode) */}
      <div
        onClick={() => onOpenPermissions?.()}
        className={`${pillBase} ${darkGold}`}
        title="Camera presence treated as available. Auto-forces in God Mode."
      >
        <span>👁️</span>
        <span>PRESENCE: {presenceStatus}</span>
      </div>

      {/* GOD Mode badge */}
      <div className={`${pillBase} border border-[#FFD700] text-[#FFD700] bg-black/80`}>
        🔓 GOD MODE
      </div>
    </div>
  );
}

// Example usage in App.jsx or a top HUD bar:
// <GodModeStatusPills
//   daemonStatus="GOD"
//   onForceReconnect={() => socket.emit('force_reconnect') || window.location.reload()}
//   onOpenPermissions={() => setShowSettings(true)}
// />