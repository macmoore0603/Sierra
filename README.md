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

### How to Activate Full God Mode Permissions (macOS)

1. In the app, go to Settings → macOS Privacy & Security.
2. Click the big gold button:
   > **🔓 ACTIVATE ALL PERMISSIONS NOW (God Mode)**
3. Drag these two paths into the open panes (especially **Camera**):
   - The installed Sierra app
   - The backend Python process
4. Run the privacy activation script for best results:
   ```bash
   # (path will be documented once the script is added to this repo)
   ```

After this, Sierra runs with true "everything unlocked" behavior.

See the upcoming `GOD_MODE.md` for the full philosophy and implementation details from the development sessions.

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

**Note**: After setup, run the (upcoming) God Mode permission activation flow for full system/gesture/camera access.

</details>

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

<p align="center">
  <strong>Sierra — built on the open-source <a href="https://github.com/nazirlouis/ada_v2">A.D.A V2</a> stack by Nazir Louis, extended with the <a href="https://github.com/nazirlouis/ada_local">A.D.A Local</a> Function-Gemma router and the <a href="https://huggingface.co/Mac7Moore/ada_model">Mac7Moore/ada_model</a> fine-tuned adapter on <a href="https://huggingface.co/google/functiongemma-270m-it">google/functiongemma-270m-it</a>.</strong><br>
  <em>Bridging AI, CAD, and Vision in a Single Interface — now with pervasive God Mode</em>
</p>
