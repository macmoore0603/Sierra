import { io } from 'socket.io-client';
import { getServerUrlSync } from './config';

// ---------------------------------------------------------------------------
// SierraAPI — the single bridge between the mobile app and the Sierra desktop
// backend (backend/server.py: FastAPI + Socket.IO on port 8000).
//
// Two channels, mirroring the desktop frontend:
//   * REST   — GET /status, POST /chat   (request/response text turns)
//   * Socket — real-time events so the phone stays SYNCED with whatever the
//              desktop app is doing: live transcription, voice-loop status,
//              tool executions, smart-home (Kasa) devices, 3D-printer status.
//
// The desktop app connects with io('http://localhost:8000'); the phone does the
// same but to the computer's LAN IP (configured in Settings).
// ---------------------------------------------------------------------------

let socket = null;
const listeners = new Map(); // event -> Set<fn>

// Socket.IO server events emitted by backend/server.py that we forward to the UI.
const SERVER_EVENTS = [
  'status',
  'auth_status',
  'transcription',
  'tool_execution',
  'tool_confirmation_request',
  'cad_status',
  'cad_thought',
  'project_update',
  'kasa_devices',
  'print_status_update',
  'sierra_route',
  'error',
];

function emitLocal(event, payload) {
  const set = listeners.get(event);
  if (set) set.forEach((fn) => {
    try { fn(payload); } catch (e) { /* listener error, ignore */ }
  });
}

/** Subscribe to a Sierra event. Returns an unsubscribe function. */
export function on(event, fn) {
  if (!listeners.has(event)) listeners.set(event, new Set());
  listeners.get(event).add(fn);
  return () => {
    const set = listeners.get(event);
    if (set) set.delete(fn);
  };
}

/** Open (or reopen) the realtime socket to the configured server. */
export function connectSocket() {
  const url = getServerUrlSync();
  if (socket) {
    try { socket.removeAllListeners(); socket.disconnect(); } catch (e) {}
    socket = null;
  }

  socket = io(url, {
    transports: ['websocket'],
    reconnection: true,
    reconnectionAttempts: Infinity,
    reconnectionDelay: 1500,
    timeout: 8000,
    forceNew: true,
  });

  socket.on('connect', () => emitLocal('connection', { connected: true, url }));
  socket.on('disconnect', (reason) =>
    emitLocal('connection', { connected: false, url, reason }));
  socket.on('connect_error', (err) =>
    emitLocal('connection', { connected: false, url, error: err?.message }));

  SERVER_EVENTS.forEach((evt) => socket.on(evt, (payload) => emitLocal(evt, payload)));

  return socket;
}

export function disconnectSocket() {
  if (socket) {
    try { socket.removeAllListeners(); socket.disconnect(); } catch (e) {}
    socket = null;
  }
}

export function isSocketConnected() {
  return !!(socket && socket.connected);
}

// --- Outbound socket actions (mirror the desktop controls) ------------------

export function startVoice(opts = {}) {
  if (socket) socket.emit('start_audio', opts);
}
export function stopVoice() {
  if (socket) socket.emit('stop_audio');
}
export function pauseVoice() {
  if (socket) socket.emit('pause_audio');
}
export function resumeVoice() {
  if (socket) socket.emit('resume_audio');
}
/** Push text into a running voice session (shows up on desktop too). */
export function sendUserInput(text) {
  if (socket) socket.emit('user_input', { text });
}
export function confirmTool(id, confirmed) {
  if (socket) socket.emit('confirm_tool', { id, confirmed });
}

// --- REST -------------------------------------------------------------------

/** Health/heartbeat check against GET /status. */
export async function checkStatus(timeoutMs = 6000) {
  const url = getServerUrlSync();
  const controller = new AbortController();
  const t = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const res = await fetch(`${url}/status`, { signal: controller.signal });
    clearTimeout(t);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json(); // { status, service }
  } catch (e) {
    clearTimeout(t);
    throw e;
  }
}

/**
 * Send a text message to Sierra via POST /chat.
 * Works whether or not the live voice loop is running, so the phone always
 * gets a real answer. Returns the assistant's reply string.
 */
export async function sendMessage(message, timeoutMs = 60000) {
  const url = getServerUrlSync();
  const controller = new AbortController();
  const t = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const res = await fetch(`${url}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message }),
      signal: controller.signal,
    });
    clearTimeout(t);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    return data.response ?? '(no response)';
  } catch (e) {
    clearTimeout(t);
    if (e.name === 'AbortError') {
      return "Sierra didn't respond in time. Is the desktop app running?";
    }
    return `Can't reach Sierra at ${url}. Check the server address in Settings and that the desktop app is running with --host 0.0.0.0.`;
  }
}
