# Sierra Changelog

## [Unreleased] - Agentic Capability Upgrades (June 2026)

Six new agentic capabilities, each wired into the Gemini tool surface
(`backend/tools.py`), routed by the on-device router where it makes sense
(`backend/sierra_router.py`), and dispatched through `backend/agentic_dispatch.py`:

- **MCP client** (`backend/integrations/mcp_client.py`): connect Sierra to external
  Model Context Protocol servers (research backends, adaptive scrapers, browser-use
  agents) and call their tools over stdio JSON-RPC. Zero hard deps; config-driven via
  `SIERRA_MCP_CONFIG`.
- **Slash commands** (`backend/agents/slash_commands.py`): `/handoff`, `/loop`,
  `/code-review`, `/verify`, `/run`, `/init`, `/security-review`, `/help`.
- **Self-healing code loop** (`backend/agents/self_healing_coder.py`): execute → read
  error → auto-repair → retry, with a pluggable model-backed fixer (heuristic fixer by
  default).
- **SOP generator** (`backend/agents/sop_generator.py`): turn a voice-note/transcript
  into a structured SOP, flagging vague steps and automation opportunities.
- **Adaptive web scraper** (`backend/integrations/adaptive_scraper.py`): resilient
  fetch + extraction cascade (Scrapling → BeautifulSoup → stdlib) with retries.
- **AI-company orchestrator** (`backend/agents/company_orchestrator.py`): decompose an
  objective into role-scoped tasks (eng/design/marketing/finance/ops/research),
  delegate to department workers, return a Kanban-style report.
- **OpenRouter (Claude Opus) backing** (`backend/llm/openrouter_client.py`): the
  reasoning-heavy capabilities (self-healing code fixer, AI-company role workers, SOP
  polishing) call OpenRouter with `anthropic/claude-opus-4.8` by default. Stdlib-only
  client; degrades gracefully to deterministic logic when `OPENROUTER_API_KEY` is unset
  or a call fails. Configurable via `OPENROUTER_MODEL` / `OPENROUTER_MAX_TOKENS`
  (default 1024 to stay within small account balances).
- **Local code/security review engine** (`backend/agents/code_review.py`, **no API**):
  AST + regex static analysis (dangerous `eval`/`exec`, `os.system`, `subprocess(shell=True)`,
  bare/`pass` excepts, unsafe `pickle`/`yaml.load`, mutable defaults, hardcoded
  secrets/AWS-keys/private-keys, tech-debt markers). Backs `/code-review` and
  `/security-review`, which now return real findings for a file/dir/source.
- **Executable `/run` + `/verify`** (no API): slash commands now actually run the given
  command in a bounded subprocess (no shell, timeout, capped output) and report
  pass/fail, instead of only emitting instructions.
- **Expanded self-healing heuristics** (no API): more stdlib auto-imports, Python-2
  `print` statement → `print(...)`, and tab/space normalization — so the loop repairs
  common failures without any model call.
- Tests in `tests/test_agentic_capabilities.py` (59 cases, no network/heavy deps).

## [Unreleased] - Pervasive God Mode Update (late May 2026)

### God Mode / Full Access Experience
- Made God Mode pervasive and automatic as the default and only experience.
- UI never shows "off", restricted, or warning states for core features (voice wake "Hey Sierra", gestures, face auth, camera presence, background processes) when full access is enabled.
- Added auto-force logic (onMount + delay + defensive guards) so voice, gestures, presence, and connection states are powered on immediately on app load.
- DAEMON / background connection indicator now shows "GOD" in full access mode and is force-tappable.
- Titlebar and HUD elements use "GOD" branding instead of "offline" / "connecting".
- Added dedicated `GOD_MODE.md` documenting the full philosophy, auto-force implementation, canonical app rule, and macOS permission activation flow.
- Updated README, ROADMAP, and ARCHITECTURE to treat pervasive God Mode as a core, top-priority principle.
- One prominent "ACTIVATE ALL PERMISSIONS NOW (God Mode)" button + helper script for aggressive macOS TCC activation (Camera for gestures, Accessibility, Automation, Full Disk, Screen Recording, etc.).
- Strict "canonical app only" rule: users must only launch the installed production build; build artifacts are never launched directly.

### Other Improvements
- (Previous items from earlier development)

---

*See GOD_MODE.md for the complete philosophy and implementation details from the extended "do all" development sessions.*
