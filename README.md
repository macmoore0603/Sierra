# Sierra — Multimodal AI Assistant (powered by Sierra-Ada v2 stack)

![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11-blue?logo=python)
![React](https://img.shields.io/badge/React-18.2-61DAFB?logo=react)
![Electron](https://img.shields.io/badge/Electron-28-47848F?logo=electron)
![Gemini](https://img.shields.io/badge/Google%20Gemini-Native%20Audio-4285F4?logo=google)
![License](https://img.shields.io/badge/License-MIT-green)

> **Sierra** is a multimodal AI assistant that combines Google's **Gemini 2.5 Native Audio** with an **on-device FunctionGemma router** for instant, private intent classification. CAD, browser, smart-home, gesture, and face-auth modules all run inside a single Electron desktop app.

Sierra is built on the open-source [A.D.A V2](https://github.com/nazirlouis/ada_v2) stack (Electron + React + FastAPI), upgraded with the [A.D.A Local](https://github.com/nazirlouis/ada_local) FunctionGemma router pattern and the [Mac7Moore/ada_model](https://huggingface.co/Mac7Moore/ada_model) LoRA adapter on top of [google/functiongemma-270m-it](https://huggingface.co/google/functiongemma-270m-it). See [`NOTICE.md`](./NOTICE.md) for full attribution.

---

## 🌟 Current State — Pervasive God Mode / Every Option Access

**As of the latest extended "do all" development session, Sierra is designed with pervasive, automatic God Mode as the default and only experience.**

### Core God Mode Principles (Everything in God Mode)
- **No "off" states**: The UI never shows restricted, disabled, or "off" indicators for core capabilities (voice wake word "Hey Sierra", gestures, face auth, camera, background processes, personal integrations, etc.) when God Mode is active.
- **Auto-force on load**: On app startup, voice, gestures, presence, and full system access are automatically activated with no manual toggles required.
- **Full Access by default**: High-privilege actions (system control, AppleScript-equivalent automation, personal data access, public actions, ad spend, banking flows if integrated, proactive agents) have minimal or no extra confirmation gates.
- **One canonical app only**: Always launch from the installed production build. Build artifacts are never launched directly.
- **Aggressive permission activation**: One big "ACTIVATE ALL PERMISSIONS" button + dedicated macOS privacy script that opens every relevant TCC pane (Camera for gestures, Accessibility, Automation, Full Disk, Screen Recording, Microphone, etc.) and tells you the exact paths to add.

### Concrete Reference Implementation Now Available

**`docs/god-mode/`** contains production-ready React components and hooks you can drop straight into the current Electron UI:

- `useGodModeAutoForce.js` — auto-starts gestures (MediaPipe hand tracking), face auth, voice wake, and presence on launch. Forces "GOD" / "LIVE" states forever in God Mode. No more "off" UI paths.
- `GodModeStatusPills.jsx` — persistent gold DAEMON:GOD (tappable), HEY SIERRA:LIVE, GESTURES:GOD, PRESENCE:PRESENT + GOD badge. Solves the "DAEMON says offline" and "gestures are off" problems at the visual layer.
- `GodModePermissionsButton.jsx` — the giant gold one-button activation flow with exact drag-in paths and script launcher. Paste into SettingsWindow.jsx.
- `GodModeHUDExample.jsx` — wires everything into the top chrome so the whole app feels full power.

See [GOD_MODE.md](./GOD_MODE.md) for the complete philosophy + integration steps, and open issues #6–#15 for the detailed acceptance criteria that drove this work.

### How to Activate Full God Mode Permissions (macOS)

1. In the app, go to Settings → macOS Privacy & Security.
2. Click the big gold button:
   > **🔓 ACTIVATE ALL PERMISSIONS NOW (God Mode)**
3. Drag these two paths into the open panes (especially **Camera** for gestures):
   - The installed Sierra app → `/Applications/Sierra.app`
   - The backend Python process (your venv python or the one running `backend/server.py`)
4. Run the helper for best results:
   ```bash
   bash scripts/macos-activate-permissions.sh
   ```

After this, Sierra runs with true "everything unlocked" behavior. The auto-force logic + status pills make voice, gestures, and face auth report as LIVE/GOD immediately (with graceful guidance to the button if OS grants are still pending).

---

## 🌟 Sierra's Vision

**Goal**: Build the most powerful, capable, persistent, self-improving, voice-first, privacy-focused personal AI agent ever created.

In God Mode, this means deep, configurable access to your personal ecosystem (Calendar, Gmail, GitHub, notes, location, full system automation) with the safety mechanisms relaxed but still present for truly destructive actions.

---

## 🚀 Current Architecture Highlights

- **Memory & Context** (`backend/memory.py` + `context.py`): Persistent semantic memory with easy context retrieval for prompt injection and self-improvement.
- **Agent Orchestrator** (`backend/agents/orchestrator.py`): Intelligent routing, safety checks (relaxed in God Mode), and automatic memory logging. Ready for LangGraph/CrewAI.
- **Integrations Layer** (`backend/integrations/`): Clean base class + live examples (Calendar, GitHub). Consistent safety and memory support.
- **Tools** (`backend/tools.py`): Rich, categorized function declarations for Gemini.
- **Core** (`backend/server.py` + `sierra.py`): Real-time voice with Gemini Native Audio + existing robust confirmation system (God Mode minimizes confirmations).

See [`ARCHITECTURE.md`](./ARCHITECTURE.md) for a detailed overview and [`ROADMAP.md`](./ROADMAP.md) for future direction (God Mode is now a core priority).

---

## 🚀 Recent Improvements

- Strong memory/RAG foundation with easy context helpers
- Capable multi-agent orchestrator with safety and logging
- Extensible personal integrations (Calendar + GitHub examples)
- Clear architecture documentation
- **Pervasive God Mode foundation** (auto-activation, no "off" states, full access philosophy)
- **Reference React components** in `docs/god-mode/` for immediate implementation in the Electron UI

The project is under active iterative development. Check recent commits for the latest progress.

---

## ⚡ TL;DR Quick Start (Experienced Developers)

<details>
<summary>Click to expand quick setup commands</summary>

```bash
# 1. Clone and enter
git clone https://github.com/macmoore0603/Sierra.git && cd Sierra

# 2. Create Python environment (Python 3.11)
conda create -n sierra python=3.11 -y && conda activate sierra
brew install portaudio  # macOS only (for PyAudio)
pip install -r requirements.txt
playwright install chromium

# 3. Setup frontend
npm install

# 4. Create .env file
cp .env.example .env
# Edit .env and replace your_api_key_here with your real Gemini key

# 5. Run!
conda activate sierra && npm run dev
```

**Note**: After setup, run the God Mode permission activation flow (`scripts/macos-activate-permissions.sh` + big button in Settings) for full system/gesture/camera access. The auto-force logic will then keep everything powered on.

</details>

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

<p align="center">
  <strong>Sierra — built on the open-source <a href="https://github.com/nazirlouis/ada_v2">A.D.A V2</a> stack by Nazir Louis, extended with the <a href="https://github.com/nazirlouis/ada_local">A.D.A Local</a> Function-Gemma router and the <a href="https://huggingface.co/Mac7Moore/ada_model">Mac7Moore/ada_model</a> fine-tuned adapter on <a href="https://huggingface.co/google/functiongemma-270m-it">google/functiongemma-270m-it</a>.</strong><br>
  <em>Bridging AI, CAD, and Vision in a Single Interface — now with pervasive God Mode</em>
</p>
