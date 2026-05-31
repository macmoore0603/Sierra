import React from 'react';
import GodModeStatusPills from './GodModeStatusPills';

/**
 * GodModeHUDExample.jsx
 *
 * Shows how the God Mode status pills + auto-force integrate with the existing
 * modular UI (TopAudioBar, Visualizer, ToolsModule, etc.) in the Electron app.
 * Addresses the "make the entire chrome communicate full power" requirement (issues #12, 15).
 */

export default function GodModeHUDExample({
  currentTime,
  lastLocalRoute,
  onForceReconnect,
  onOpenSettings,
}) {
  return (
    <div className="fixed top-0 left-0 right-0 z-50 pointer-events-none">
      {/* Top bar with God Mode branding */}
      <div className="h-10 bg-black/95 border-b border-[#FFD700]/30 flex items-center justify-between px-4 text-sm pointer-events-auto">
        <div className="flex items-center gap-3">
          <div className="font-bold text-[#FFD700]">SIERRA</div>
          <div className="text-[#C5A572] text-xs">MOORE INDUSTRIES • GOD MODE</div>
        </div>

        {/* The never-off status pills live here - always visible */}
        <GodModeStatusPills
          daemonStatus="GOD"
          voiceStatus="LIVE"
          gesturesStatus="GOD"
          presenceStatus="PRESENT"
          onForceReconnect={onForceReconnect}
          onOpenPermissions={onOpenSettings}
          className=""
        />

        <div className="text-[#D4AF37] tabular-nums">{currentTime?.toLocaleTimeString()}</div>
      </div>

      {/* Optional subtle bottom-right God Mode indicator + local router telemetry */}
      <div className="absolute bottom-4 right-4 text-[10px] text-[#FFD700]/70 font-mono pointer-events-auto">
        {lastLocalRoute && (
          <div>ON-DEVICE: {lastLocalRoute.function} ({lastLocalRoute.confidence?.toFixed(2)})</div>
        )}
        <div className="text-right">🔓 EVERY OPTION ACCESS ACTIVE</div>
      </div>
    </div>
  );
}

// Integration note for App.jsx:
// Replace or wrap the existing top bar area with <GodModeHUDExample ... />
// The old TopAudioBar can stay below it or be merged.