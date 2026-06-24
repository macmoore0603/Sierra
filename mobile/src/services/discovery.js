import * as Network from 'expo-network';

// ---------------------------------------------------------------------------
// Auto-discovery — find the Sierra desktop backend on the LAN so the user
// doesn't have to type an IP address.
//
// Expo Go can't do mDNS without a native module, so this scans the phone's own
// /24 subnet for a host answering GET /status with the Sierra signature. The
// backend also advertises via mDNS (backend/discovery.py) for native builds,
// but this subnet scan is the portable mechanism that works everywhere.
// ---------------------------------------------------------------------------

const PORT = 8000;
const PROBE_TIMEOUT_MS = 1200;
const BATCH_SIZE = 24; // probe this many hosts at once

/** Probe a single host:port for the Sierra /status signature. */
async function probe(host) {
  const url = `http://${host}:${PORT}`;
  const controller = new AbortController();
  const t = setTimeout(() => controller.abort(), PROBE_TIMEOUT_MS);
  try {
    const res = await fetch(`${url}/status`, { signal: controller.signal });
    clearTimeout(t);
    if (!res.ok) return null;
    const data = await res.json();
    if (data && typeof data.service === 'string' && /sierra/i.test(data.service)) {
      return { url, host, name: data.name || 'Sierra', service: data.service };
    }
    return null;
  } catch (e) {
    clearTimeout(t);
    return null;
  }
}

/**
 * Scan the local /24 subnet for the Sierra backend.
 * @param {(scanned:number, total:number, found?:object)=>void} onProgress
 * @returns the first match { url, host, name } or null.
 */
export async function discoverSierra(onProgress) {
  let ip;
  try {
    ip = await Network.getIpAddressAsync();
  } catch (e) {
    return null;
  }
  if (!ip || !/^\d+\.\d+\.\d+\.\d+$/.test(ip)) return null;

  const parts = ip.split('.');
  const base = `${parts[0]}.${parts[1]}.${parts[2]}`;
  const self = parseInt(parts[3], 10);

  // Order hosts so the most likely ones (router/low addresses + near the phone)
  // are probed first, giving a faster hit in the common case.
  const hosts = [];
  for (let i = 1; i <= 254; i++) {
    if (i !== self) hosts.push(`${base}.${i}`);
  }
  hosts.sort((a, b) => {
    const da = Math.abs(parseInt(a.split('.')[3], 10) - self);
    const db = Math.abs(parseInt(b.split('.')[3], 10) - self);
    return da - db;
  });

  const total = hosts.length;
  let scanned = 0;

  for (let i = 0; i < hosts.length; i += BATCH_SIZE) {
    const batch = hosts.slice(i, i + BATCH_SIZE);
    const results = await Promise.all(batch.map(probe));
    scanned += batch.length;
    const hit = results.find((r) => r);
    if (onProgress) onProgress(scanned, total, hit || undefined);
    if (hit) return hit;
  }
  return null;
}
