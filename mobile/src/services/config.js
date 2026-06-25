import AsyncStorage from '@react-native-async-storage/async-storage';

const STORAGE_KEY = '@sierra/serverUrl';

// The Sierra desktop backend (FastAPI + Socket.IO) listens on port 8000.
// On the same machine that's http://localhost:8000, but a phone has to reach
// the computer over the LAN, so the default is a placeholder the user edits in
// Settings to their computer's LAN IP, e.g. http://192.168.1.42:8000.
//
// NOTE: the desktop autostart binds uvicorn to 127.0.0.1 (localhost only). For
// the phone to connect, the backend must listen on the LAN interface — launch
// it with `--host 0.0.0.0` (see mobile/README.md).
export const DEFAULT_SERVER_URL = 'http://192.168.1.100:8000';

let cachedUrl = DEFAULT_SERVER_URL;

export function getServerUrlSync() {
  return cachedUrl;
}

export async function loadServerUrl() {
  try {
    const stored = await AsyncStorage.getItem(STORAGE_KEY);
    if (stored) {
      cachedUrl = normalizeUrl(stored);
    }
  } catch (e) {
    // fall back to default
  }
  return cachedUrl;
}

export async function saveServerUrl(url) {
  const clean = normalizeUrl(url);
  cachedUrl = clean;
  try {
    await AsyncStorage.setItem(STORAGE_KEY, clean);
  } catch (e) {
    // ignore persistence failure; in-memory value still updated
  }
  return clean;
}

export function normalizeUrl(url) {
  let u = (url || '').trim();
  if (!u) return DEFAULT_SERVER_URL;
  if (!/^https?:\/\//i.test(u)) {
    u = 'http://' + u;
  }
  // strip trailing slash
  return u.replace(/\/+$/, '');
}
