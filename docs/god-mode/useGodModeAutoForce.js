import { useEffect } from 'react';

/**
 * useGodModeAutoForce.js
 *
 * The heart of pervasive God Mode for the Electron/React frontend.
 * Addresses Issues #6, #7, #10, #13, #14.
 *
 * Call this hook once early in App.jsx (or any root component).
 * When isGodMode === true (pervasive: always true in this build):
 *   - Forces hand tracking / gestures ON immediately (no manual enable).
 *   - Forces face auth to active/present state (graceful if no cam yet).
 *   - Forces voice wake listener intent to LIVE (backend will start on socket).
 *   - Suppresses any "off" / "CAMERA OFF" / "GESTURES OFF" UI states.
 *   - On any reconnect or settings load, re-forces the powered-on state.
 *
 * Graceful permission handling: If camera/mic not granted yet, still show
 * the feature as "GOD / LIVE" but surface a one-time "Tap to activate permissions".
 */

export function useGodModeAutoForce({
  isGodMode = true,           // Hardcoded true for pervasive God Mode build
  setIsHandTrackingEnabled,
  setFaceAuthEnabled,
  setIsVideoOn,
  setIsConnected,             // power / daemon
  socket,
  onOpenPermissions,          // callback to show Settings + God button
} = {}) {
  useEffect(() => {
    if (!isGodMode) return;

    console.log('[God Mode] Auto-force hook mounted — forcing full power states');

    // 1. Force gestures / hand tracking ON (MediaPipe) — the #1 "gestures are off" complaint
    if (setIsHandTrackingEnabled) {
      setIsHandTrackingEnabled(true);
      // Also update any ref used inside gesture loops
      if (typeof window !== 'undefined') {
        window.__sierra_god_gestures_forced = true;
      }
    }

    // 2. Force face auth to a powered-on / present state (even if not yet granted)
    if (setFaceAuthEnabled) {
      // In God Mode we treat face auth as "active / monitoring" intent
      // The actual lock screen behavior can still respect localStorage for unlock,
      // but the indicator must never say "off".
      setFaceAuthEnabled(true);
      localStorage.setItem('face_auth_enabled', 'true'); // persist intent
    }

    // 3. Force camera / video presence intent ON (no CAMERA OFF ever)
    if (setIsVideoOn) {
      // We don't force the actual video stream here (privacy),
      // but we set the UI state to "intent active" so HUD shows PRESENT/GOD.
      // Real stream starts on first gesture or explicit wake.
      setIsVideoOn(true);
    }

    // 4. Force daemon / background connection to "GOD" visual state
    if (setIsConnected) {
      setIsConnected(true);
    }

    // 5. Emit to backend that we are in God Mode (relaxed safety, auto-start listeners)
    if (socket && socket.connected) {
      socket.emit('god_mode_active', { enabled: true, auto_forced: true });
      // Ask backend to start wake word listener if it has one
      socket.emit('start_wake_word', { force: true });
    }

    // 6. Safety re-force on any future socket reconnect (watchdog)
    const reconnectHandler = () => {
      console.log('[God Mode] Reconnect detected — re-forcing states');
      if (setIsHandTrackingEnabled) setIsHandTrackingEnabled(true);
      if (setIsConnected) setIsConnected(true);
      if (socket) socket.emit('god_mode_active', { enabled: true, reconnected: true });
    };

    if (socket) {
      socket.on('connect', reconnectHandler);
    }

    return () => {
      if (socket) socket.off('connect', reconnectHandler);
    };
  }, [isGodMode, setIsHandTrackingEnabled, setFaceAuthEnabled, setIsVideoOn, setIsConnected, socket]);

  // Helper: call this from any "off" click handler to redirect to God activation
  function forceGodModeFeature(feature) {
    if (!isGodMode) return false;
    console.log(`[God Mode] Force-activating ${feature} via permissions flow`);
    onOpenPermissions?.();
    return true;
  }

  return { forceGodModeFeature };
}

// Minimal usage in App.jsx (add near other useEffects):
// const { forceGodModeFeature } = useGodModeAutoForce({
//   isGodMode: true, // pervasive
//   setIsHandTrackingEnabled,
//   setFaceAuthEnabled,
//   setIsVideoOn,
//   setIsConnected,
//   socket,
//   onOpenPermissions: () => setShowSettings(true),
// });

// Then in any old toggle that used to say "off":
// onClick={() => forceGodModeFeature('gestures') || actualOldToggle() }