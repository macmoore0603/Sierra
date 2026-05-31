import React, { useEffect, useState, useRef } from 'react';
import io from 'socket.io-client';

import Visualizer from './components/Visualizer';
import TopAudioBar from './components/TopAudioBar';
import CadWindow from './components/CadWindow';
import BrowserWindow from './components/BrowserWindow';
import ChatModule from './components/ChatModule';
import ToolsModule from './components/ToolsModule';
import { Mic, MicOff, Settings, X, Minus, Power, Video, VideoOff, Layout, Hand, Printer, Clock } from 'lucide-react';
import { FilesetResolver, HandLandmarker } from '@mediapipe/tasks-vision';
// MemoryPrompt removed - memory is now actively saved to project
import ConfirmationPopup from './components/ConfirmationPopup';
import AuthLock from './components/AuthLock';
import KasaWindow from './components/KasaWindow';
import PrinterWindow from './components/PrinterWindow';
import SettingsWindow from './components/SettingsWindow';

// GOD MODE PERVASIVE AUTO-FORCE (see docs/god-mode/)
// In the permanent God Mode build we import the reference hook and force
// gestures/face/voice/presence to powered-on states on every mount/reconnect.
// This eliminates all "off" / "DAEMON offline" / "gestures are off" states.
// import { useGodModeAutoForce } from './hooks/useGodModeAutoForce';


const socket = io('http://localhost:8000');
const { ipcRenderer } = window.require('electron');

function App() {
    // =========================================================================
    // GOD MODE PERVASIVE — EVERYTHING AUTO-FORCED ON (no toggles, no "off" states)
    // =========================================================================
    // This build treats God Mode as the only mode. The hook below (when uncommented
    // and the file copied from docs/god-mode/) will:
    //   • setIsHandTrackingEnabled(true) immediately
    //   • treat face auth and camera presence as active
    //   • tell backend "god_mode_active" so safety is relaxed
    //   • re-force on any socket reconnect
    // See docs/god-mode/useGodModeAutoForce.js and GOD_MODE.md for the full pattern.
    // The four status pills (DAEMON:GOD etc.) should be rendered in the top chrome.
    // =========================================================================

    const [status, setStatus] = useState('Disconnected');