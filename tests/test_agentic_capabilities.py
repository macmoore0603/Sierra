"""
Tests for Sierra's agentic capability upgrades:
- MCP client (registry/transport error handling)
- Slash command system
- Self-healing code execution loop
- SOP / procedure generator
- Adaptive web scraper (extraction cascade, no network)
- AI-company orchestrator
- The central agentic dispatcher + tool declarations
"""

import pytest

from agentic_dispatch import AGENTIC_TOOL_NAMES, dispatch_agentic_tool
from agents.slash_commands import SlashCommandRegistry
from agents.self_healing_coder import SelfHealingCoder, self_heal_code, heuristic_fixer
from agents.sop_generator import generate_sop
from agents.company_orchestrator import CompanyOrchestrator
from integrations.mcp_client import MCPClient
from integrations.adaptive_scraper import AdaptiveScraper, _extract


# ---------------------------------------------------------------------------
# MCP client
# ---------------------------------------------------------------------------
class TestMCPClient:
    def test_register_and_list_servers(self):
        client = MCPClient(servers={})
        client.register_server("demo", "true")  # 'true' is a harmless no-op binary
        listed = client.list_servers()
        assert listed["status"] == "ok"
        assert "demo" in listed["servers"]

    def test_unknown_server_errors_gracefully(self):
        client = MCPClient(servers={})
        result = client.list_tools("does-not-exist")
        assert result["status"] == "error"
        assert "Unknown MCP server" in result["error"]

    def test_bad_command_does_not_raise(self):
        client = MCPClient(servers={"broken": {"command": "/nonexistent/binary/xyz"}}, timeout=2.0)
        result = client.call_tool("broken", "anything", {})
        assert result["status"] == "error"


# ---------------------------------------------------------------------------
# Slash commands
# ---------------------------------------------------------------------------
class TestSlashCommands:
    def setup_method(self):
        self.registry = SlashCommandRegistry()

    def test_help_lists_seven_canonical_commands(self):
        result = self.registry.dispatch("/help")
        assert result["status"] == "ok"
        names = {c["name"] for c in result["commands"]}
        for expected in ["/handoff", "/loop", "/code-review", "/verify", "/run", "/init", "/security-review"]:
            assert expected in names

    def test_unknown_command(self):
        result = self.registry.dispatch("/definitely-not-a-command")
        assert result["status"] == "error"
        assert "available" in result

    def test_not_a_command(self):
        assert self.registry.dispatch("just chatting")["status"] == "error"

    def test_loop_registers(self):
        result = self.registry.dispatch("/loop 60 check the news")
        assert result["status"] == "ok"
        assert result["scheduled"]["interval_seconds"] == 60
        assert "news" in result["scheduled"]["prompt"]

    def test_code_review_effort_level(self):
        result = self.registry.dispatch("/code-review deep src/app.py")
        assert result["effort_level"] == "deep"
        assert "src/app.py" in result["target"]

    def test_security_review_has_checklist(self):
        result = self.registry.dispatch("/security-review my branch")
        assert result["status"] == "ok"
        assert len(result["checklist"]) >= 3


# ---------------------------------------------------------------------------
# Self-healing coder
# ---------------------------------------------------------------------------
class TestSelfHealingCoder:
    def test_working_code_succeeds_first_try(self):
        result = self_heal_code("print('hello')")
        assert result["success"] is True
        assert result["iterations"] == 1
        assert "hello" in result["stdout"]

    def test_heuristic_fixes_missing_import(self):
        # References math.sqrt without importing math -> NameError, then auto-fixed.
        result = self_heal_code("print(math.sqrt(16))")
        assert result["success"] is True
        assert result["iterations"] >= 2
        assert "4.0" in result["stdout"]

    def test_unfixable_code_fails_within_budget(self):
        result = self_heal_code("raise ValueError('nope')", max_iterations=3)
        assert result["success"] is False
        assert result["iterations"] <= 3

    def test_heuristic_fixer_returns_none_when_no_fix(self):
        assert heuristic_fixer("x = 1", "some unrelated error") is None

    def test_custom_fixer_is_used(self):
        def fixer(code, stderr):
            return "print('patched')"

        coder = SelfHealingCoder(fixer=fixer, max_iterations=3)
        result = coder.run("raise RuntimeError('boom')")
        assert result.success is True
        assert "patched" in result.stdout


# ---------------------------------------------------------------------------
# SOP generator
# ---------------------------------------------------------------------------
class TestSOPGenerator:
    def test_numbered_steps_parsed(self):
        transcript = "1. Open the dashboard\n2. Export the report\n3. Email it to the team"
        result = generate_sop(transcript, title="Weekly Report")
        assert result["status"] == "ok"
        assert result["step_count"] == 3
        assert result["title"] == "Weekly Report"
        assert "# SOP: Weekly Report" in result["markdown"]

    def test_flags_automatable_steps(self):
        result = generate_sop("First, export the data. Then email the summary.")
        # 'export' and 'email' should be flagged automatable.
        assert len(result["automatable"]) >= 1

    def test_flags_vague_steps(self):
        result = generate_sop("1. Just handle it somehow\n2. Open the customer record and verify the address")
        assert 1 in result["needs_clarification"]

    def test_empty_transcript(self):
        result = generate_sop("")
        assert result["step_count"] == 0


# ---------------------------------------------------------------------------
# Adaptive scraper (no network)
# ---------------------------------------------------------------------------
class TestAdaptiveScraper:
    def test_extract_cascade_stdlib(self):
        html = "<html><head><title>Hi</title></head><body><p>Hello</p><a href='/x'>link</a><script>bad()</script></body></html>"
        extracted = _extract(html)
        assert extracted["title"] == "Hi"
        assert "Hello" in extracted["text"]
        assert "bad()" not in extracted["text"]  # script stripped
        # Engine depends on what's installed; all engines must strip scripts.
        assert extracted["engine"] in ("stdlib", "beautifulsoup", "scrapling")

    def test_rejects_non_http_url(self):
        scraper = AdaptiveScraper()
        result = scraper.scrape("ftp://example.com")
        assert result["status"] == "error"

    def test_unreachable_host_degrades(self):
        scraper = AdaptiveScraper(retries=1, timeout=2.0)
        result = scraper.scrape("http://localhost:1/definitely-not-listening")
        assert result["status"] == "error"
        assert "Failed after" in result["error"]


# ---------------------------------------------------------------------------
# AI-company orchestrator
# ---------------------------------------------------------------------------
class TestCompanyOrchestrator:
    def setup_method(self):
        self.company = CompanyOrchestrator()

    def test_role_assignment(self):
        assert self.company.assign_role("build the backend API") == "engineering"
        assert self.company.assign_role("design a new logo") == "design"
        assert self.company.assign_role("forecast revenue and budget") == "finance"

    def test_plan_splits_objective(self):
        run = self.company.plan("Build the app. Design the logo. Launch a marketing campaign.")
        assert len(run.tasks) == 3
        roles = {t.role for t in run.tasks}
        assert {"engineering", "design", "marketing"} <= roles

    def test_execute_returns_board_and_results(self):
        result = self.company.execute("Build the API. Market the launch.")
        assert result["status"] == "ok"
        assert result["task_count"] == 2
        assert len(result["board"]["done"]) == 2
        assert all(t["result"] is not None for t in result["tasks"])

    def test_custom_worker_registered(self):
        calls = []

        def worker(task, ctx):
            calls.append(task)
            return {"status": "ok", "did": task}

        self.company.register_worker("engineering", worker)
        self.company.execute("Build the backend service")
        assert calls  # the custom engineering worker ran


# ---------------------------------------------------------------------------
# Dispatcher + tool declarations
# ---------------------------------------------------------------------------
class TestAgenticDispatch:
    def test_dispatch_slash(self):
        result = dispatch_agentic_tool("run_slash_command", {"command": "/help"})
        assert result["status"] == "ok"

    def test_dispatch_sop(self):
        result = dispatch_agentic_tool("generate_sop", {"transcript": "1. Do A\n2. Do B"})
        assert result["step_count"] == 2

    def test_dispatch_company(self):
        result = dispatch_agentic_tool("run_company", {"objective": "Build the API"})
        assert result["status"] == "ok"

    def test_dispatch_self_healing(self):
        result = dispatch_agentic_tool("self_healing_code", {"code": "print(1+1)"})
        assert result["success"] is True

    def test_dispatch_mcp_list(self):
        result = dispatch_agentic_tool("use_mcp_tool", {"action": "list_servers"})
        assert result["status"] == "ok"

    def test_unknown_tool(self):
        result = dispatch_agentic_tool("not_a_tool", {})
        assert result["status"] == "error"

    def test_arguments_json_string_coerced(self):
        # call_tool with a JSON-string arguments field should not crash.
        result = dispatch_agentic_tool(
            "use_mcp_tool",
            {"action": "call_tool", "server": "nope", "tool": "x", "arguments": '{"a": 1}'},
        )
        assert result["status"] == "error"  # unknown server, but coercion worked

    def test_all_names_present_in_tools_list(self):
        from tools import tools_list

        declared = {fd["name"] for fd in tools_list[0]["function_declarations"]}
        assert AGENTIC_TOOL_NAMES <= declared
