import React, { createContext, useContext, useEffect, useRef, useState } from 'react';
import * as Sierra from '../services/SierraAPI';
import { loadServerUrl, saveServerUrl, getServerUrlSync } from '../services/config';
import { discoverSierra } from '../services/discovery';

const SierraContext = createContext(null);

export function useSierra() {
  const ctx = useContext(SierraContext);
  if (!ctx) throw new Error('useSierra must be used inside <SierraProvider>');
  return ctx;
}

const MAX_MESSAGES = 200;
const MAX_ACTIVITY = 40;

export function SierraProvider({ children }) {
  const [serverUrl, setServerUrl] = useState(getServerUrlSync());
  const [connected, setConnected] = useState(false);     // socket live
  const [reachable, setReachable] = useState(null);      // REST /status ok
  const [serviceName, setServiceName] = useState(null);

  const [voiceState, setVoiceState] = useState('stopped'); // stopped|running|paused
  const [authenticated, setAuthenticated] = useState(true);
  const [lastRoute, setLastRoute] = useState(null);        // local router hint

  const [messages, setMessages] = useState([]);            // chat + synced transcript
  const [activity, setActivity] = useState([]);            // tool executions feed
  const [devices, setDevices] = useState([]);              // Kasa smart-home
  const [printStatus, setPrintStatus] = useState(null);
  const [project, setProject] = useState(null);
  const [lastError, setLastError] = useState(null);

  const [discovering, setDiscovering] = useState(false);
  const [discoveryProgress, setDiscoveryProgress] = useState(0); // 0..1

  const seenTranscript = useRef(new Set());

  const pushMessage = (msg) =>
    setMessages((prev) => [...prev, msg].slice(-MAX_MESSAGES));
  const pushActivity = (item) =>
    setActivity((prev) => [{ ...item, ts: Date.now() }, ...prev].slice(0, MAX_ACTIVITY));

  // --- wire up the socket + REST polling once on mount ---------------------
  useEffect(() => {
    let mounted = true;
    let pollTimer = null;

    const boot = async () => {
      const url = await loadServerUrl();
      if (!mounted) return;
      setServerUrl(url);
      Sierra.connectSocket();
      const ok = await refreshStatus();
      // Saved address didn't answer — try to find Sierra on the LAN automatically.
      if (!ok && mounted) {
        await discover();
      }
    };

    const unsubs = [
      Sierra.on('connection', ({ connected }) => {
        if (!mounted) return;
        setConnected(connected);
        if (!connected) setVoiceState('stopped');
      }),

      Sierra.on('status', (data) => {
        if (!mounted) return;
        const msg = (data && data.msg) || '';
        if (/started/i.test(msg)) setVoiceState('running');
        else if (/stopped/i.test(msg)) setVoiceState('stopped');
        else if (/paused/i.test(msg)) setVoiceState('paused');
        else if (/resumed/i.test(msg)) setVoiceState('running');
      }),

      Sierra.on('auth_status', (data) => {
        if (mounted && data) setAuthenticated(!!data.authenticated);
      }),

      // Live transcription from the desktop voice loop → keeps chat in sync.
      Sierra.on('transcription', (data) => {
        if (!mounted || !data || !data.text) return;
        const key = `${data.sender}|${data.text}`;
        if (seenTranscript.current.has(key)) return;
        seenTranscript.current.add(key);
        const role = /sierra/i.test(data.sender || '') ? 'sierra' : 'user';
        pushMessage({ role, text: data.text, source: 'voice' });
      }),

      Sierra.on('tool_execution', (data) => {
        if (!mounted || !data) return;
        pushActivity({
          tool: data.tool,
          args: data.args,
          status: data.status || 'executing',
          realtime: data.realtime,
        });
      }),

      Sierra.on('sierra_route', (data) => {
        if (mounted && data) setLastRoute(data);
      }),

      Sierra.on('kasa_devices', (data) => {
        if (mounted && Array.isArray(data)) setDevices(data);
      }),

      Sierra.on('print_status_update', (data) => {
        if (mounted && data) setPrintStatus(data);
      }),

      Sierra.on('project_update', (data) => {
        if (mounted && data) setProject(data.project);
      }),

      Sierra.on('error', (data) => {
        if (mounted && data) setLastError(data.msg || String(data));
      }),
    ];

    boot();
    // Heartbeat: REST /status every 15s so the dashboard reflects reachability
    // even when the socket is mid-reconnect.
    pollTimer = setInterval(() => { if (mounted) refreshStatus(); }, 15000);

    return () => {
      mounted = false;
      if (pollTimer) clearInterval(pollTimer);
      unsubs.forEach((u) => u && u());
      Sierra.disconnectSocket();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Scan the LAN for the Sierra backend and connect to it if found.
  async function discover() {
    if (discovering) return null;
    setDiscovering(true);
    setDiscoveryProgress(0);
    try {
      const found = await discoverSierra((scanned, total) => {
        setDiscoveryProgress(total ? scanned / total : 0);
      });
      if (found && found.url) {
        await updateServerUrl(found.url);
        return found;
      }
      return null;
    } catch (e) {
      return null;
    } finally {
      setDiscovering(false);
      setDiscoveryProgress(0);
    }
  }

  async function refreshStatus() {
    try {
      const data = await Sierra.checkStatus();
      setReachable(true);
      setServiceName(data.service || 'Sierra Backend');
      return true;
    } catch (e) {
      setReachable(false);
      return false;
    }
  }

  // --- actions exposed to screens -----------------------------------------
  async function sendChat(text) {
    const clean = (text || '').trim();
    if (!clean) return;
    pushMessage({ role: 'user', text: clean, source: 'chat' });

    // If a live voice session is running, route the text through it so it shows
    // up on the desktop too (true two-way sync); the reply arrives as a
    // 'transcription' event. Otherwise use the REST /chat round-trip.
    if (voiceState !== 'stopped' && Sierra.isSocketConnected()) {
      Sierra.sendUserInput(clean);
      return;
    }
    const reply = await Sierra.sendMessage(clean);
    pushMessage({ role: 'sierra', text: reply, source: 'chat' });
  }

  function clearMessages() {
    seenTranscript.current.clear();
    setMessages([]);
  }

  async function updateServerUrl(url) {
    const clean = await saveServerUrl(url);
    setServerUrl(clean);
    setConnected(false);
    setReachable(null);
    Sierra.connectSocket();
    await refreshStatus();
    return clean;
  }

  const startVoice = () => Sierra.startVoice();
  const stopVoice = () => Sierra.stopVoice();
  const pauseVoice = () => Sierra.pauseVoice();
  const resumeVoice = () => Sierra.resumeVoice();
  const confirmTool = (id, ok) => Sierra.confirmTool(id, ok);

  const value = {
    // connection
    serverUrl, connected, reachable, serviceName, refreshStatus, updateServerUrl,
    discover, discovering, discoveryProgress,
    // state
    voiceState, authenticated, lastRoute, messages, activity, devices,
    printStatus, project, lastError,
    // actions
    sendChat, clearMessages, startVoice, stopVoice, pauseVoice, resumeVoice,
    confirmTool,
  };

  return <SierraContext.Provider value={value}>{children}</SierraContext.Provider>;
}
