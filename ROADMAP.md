# Sierra Roadmap

This document outlines the current direction and prioritized next steps for Sierra.

## Vision
Make Sierra the most powerful, capable, persistent, self-improving, voice-first, privacy-focused personal AI agent **with pervasive God Mode / Every Option Access as the default experience**.

## Current Strengths (as of late May 2026)
- On-device FunctionGemma router for fast, private intent classification
- Rich tool surface for Gemini
- Persistent semantic memory with context helpers
- Intelligent Agent Orchestrator with safety checks (relaxed in God Mode)
- Extensible personal integrations (Calendar + GitHub examples)
- Solid Electron + React frontend with gesture and face auth
- **Foundation for pervasive God Mode** (no "off" states, auto-activation of voice/gestures/face-auth)

## High-Priority Next Steps

### 1. Pervasive God Mode / Full Access Experience (Highest Impact)
- Implement auto-force logic so voice ("Hey Sierra"), gestures, face auth, and camera presence are always active on app load when God Mode is enabled (no manual toggles).
- UI must never show "off", disabled, or restricted states for core capabilities in God Mode.
- One big "ACTIVATE ALL PERMISSIONS NOW (God Mode)" button + dedicated macOS privacy script that opens every relevant TCC pane (Camera for gestures, Accessibility, Automation, Full Disk, Screen Recording, Microphone, etc.) and tells the user the exact paths to add.
- **Canonical app rule**: Only the installed production build in /Applications (or equivalent) is used. Build artifacts are never launched directly.
- Relaxed confirmation gates for high-privilege actions in God Mode while keeping safety for truly destructive operations.

### 2. Memory Activation (High Impact)
- Inject relevant memory context into Gemini prompts automatically
- Auto-log conversations and key events to long-term memory
- Build reflection / self-improvement loops

### 3. Personal Integrations (High Impact)
- Implement real Google Calendar integration (with OAuth + confirmation, relaxed in God Mode)
- Add Gmail integration
- Add GitHub integration with real API calls

### 4. Multi-Agent Orchestration
- Evolve orchestrator into a proper LangGraph state machine
- Create specialized agents (Memory Agent, Proactive Agent, Personal Agent, God Mode Agent)
- Add agent-to-agent communication

### 5. Polish & Production Readiness
- Better error handling and logging
- More comprehensive testing
- Improved voice reliability and interruption handling
- Documentation and onboarding improvements (strong God Mode guide)

## Longer Term
- Full multi-agent crews (CrewAI style)
- Advanced RAG and knowledge management
- Deeper local model usage
- Cross-device / mobile companion experience
- True 24/7 background operation with God Mode always active

---

*This roadmap is living and will be updated as we continue iterative development. God Mode pervasiveness is now a top-tier priority.*
