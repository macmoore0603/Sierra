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
- **Reference React implementations** in `docs/god-mode/` (GodModeStatusPills, useGodModeAutoForce hook, PermissionsButton, HUD example) — ready to drop in to make the "never off / GOD everywhere" vision real in the current UI

## High-Priority Next Steps

### 1. Pervasive God Mode / Full Access Experience (Highest Impact — Active)
- **Reference code delivered**: `docs/god-mode/` + updates to GOD_MODE.md / README (issues #6–#15 covered at the spec + example level).
- Next: Integrate the hook + pills + button into src/App.jsx and SettingsWindow.jsx (see incident issue #16 for a truncated edit during auto-run).
- One big "ACTIVATE ALL PERMISSIONS NOW (God Mode)" button + dedicated macOS privacy script (already at scripts/macos-activate-permissions.sh).
- **Canonical app rule** and relaxed confirmation gates in God Mode.

### 2. Life Areas Mastery — "Improve Every Single Area of My Life" (New Top-Tier Priority)
The user explicitly requested: "i want sierra to know and improve every single area of my life".

Sierra must become the intelligent, proactive, always-on coach/optimizer across **all** life domains:

- Health & Fitness (sleep, workouts, nutrition, recovery, biomarkers)
- Finance & Wealth (budgeting, investing, taxes, cashflow, net worth tracking)
- Career & Skills (goals, learning, networking, promotion prep, side projects)
- Relationships & Social (family, friends, dating, conflict resolution, quality time)
- Habits & Discipline (streaks, accountability, environment design)
- Creativity & Output (writing, music, art, side projects, deep work)
- Home & Environment (smart home, maintenance, decluttering, energy)
- Personal Growth & Spirituality (journaling, reflection, values alignment, mindfulness)

**Implementation approach**:
- New `LIFE_AREAS.md` (created in the same auto-run batch)
- Dedicated "Life Area Agents" or modules inside the orchestrator
- Deep integrations + memory context per area
- Proactive daily/weekly nudges via voice + notifications (in God Mode, minimal friction)
- Dashboard / HUD cards for each area (gold/black theme)
- One unified "Life OS" command surface ("Sierra, how am I doing on health this month?")

See the freshly created `LIFE_AREAS.md` and new follow-up issues.

### 3. Memory Activation (High Impact)
- Inject relevant memory context into Gemini prompts automatically
- Auto-log conversations and key events to long-term memory
- Build reflection / self-improvement loops per life area

### 4. Personal Integrations (High Impact)
- Implement real Google Calendar integration (with OAuth + confirmation, relaxed in God Mode)
- Add Gmail integration
- Add GitHub integration with real API calls
- Add finance (Plaid or similar) + health (Apple Health / Oura / Whoop) once permissions granted via God Mode flow

### 5. Multi-Agent Orchestration
- Evolve orchestrator into a proper LangGraph state machine with Life Area specialists
- Create specialized agents (Memory Agent, Proactive Agent, Personal Agent, God Mode Agent, Health Agent, Finance Agent...)
- Add agent-to-agent communication

### 6. Polish & Production Readiness
- Better error handling and logging
- More comprehensive testing
- Improved voice reliability and interruption handling
- Documentation and onboarding improvements (strong God Mode + Life Areas guide)

## Longer Term
- Full multi-agent crews (CrewAI style) per life area
- Advanced RAG and knowledge management across your entire digital + physical life
- Deeper local model usage for private life data
- Cross-device / mobile companion (PWA + native) that stays in God Mode 24/7
- True "Sierra as second brain / life OS" that literally improves every area measurably

---

*This roadmap is living and will be updated as we continue iterative development. God Mode pervasiveness + Life Area optimization are now the dual top-tier priorities.*
