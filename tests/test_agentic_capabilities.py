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

import sys

import pytest

from agentic_dispatch import AGENTIC_TOOL_NAMES, dispatch_agentic_tool
from agents.slash_commands import SlashCommandRegistry
from agents.code_review import review, review_source
from agents.self_healing_coder import SelfHealingCoder, self_heal_code, heuristic_fixer, openrouter_fixer
from agents.sop_generator import generate_sop
from agents.company_orchestrator import CompanyOrchestrator
from integrations.mcp_client import MCPClient
from integrations.adaptive_scraper import AdaptiveScraper, _extract
from llm.openrouter_client import OpenRouterClient, openrouter_client


@pytest.fixture(autouse=True)
def _disable_openrouter(monkeypatch):
    """Keep the bulk of the suite hermetic: disable live OpenRouter calls.

    Tests that exercise the OpenRouter-backed paths re-enable it explicitly and
    mock the transport, so nothing here ever hits the network.
    """
    monkeypatch.setattr(openrouter_client, "api_key", "")


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


# ---------------------------------------------------------------------------
# OpenRouter client + LLM-backed paths (transport mocked, no network)
# ---------------------------------------------------------------------------
class TestOpenRouterClient:
    def test_disabled_without_key(self):
        client = OpenRouterClient(api_key="")
        assert client.enabled is False
        assert client.complete([{"role": "user", "content": "hi"}]) is None

    def test_default_model_is_opus(self):
        client = OpenRouterClient(api_key="k")
        assert "opus" in client.model.lower()

    def test_complete_parses_choice(self, monkeypatch):
        client = OpenRouterClient(api_key="k")
        monkeypatch.setattr(
            client, "_post",
            lambda url, payload, headers: {"choices": [{"message": {"content": "hello world"}}]},
        )
        assert client.complete([{"role": "user", "content": "hi"}]) == "hello world"

    def test_complete_returns_none_on_transport_error(self, monkeypatch):
        client = OpenRouterClient(api_key="k")

        def boom(url, payload, headers):
            raise OSError("network down")

        monkeypatch.setattr(client, "_post", boom)
        assert client.complete([{"role": "user", "content": "hi"}]) is None

    def test_prompt_builds_system_and_user(self, monkeypatch):
        client = OpenRouterClient(api_key="k")
        captured = {}

        def fake_post(url, payload, headers):
            captured["payload"] = payload
            return {"choices": [{"message": {"content": "ok"}}]}

        monkeypatch.setattr(client, "_post", fake_post)
        client.prompt("sys", "usr")
        roles = [m["role"] for m in captured["payload"]["messages"]]
        assert roles == ["system", "user"]


class TestOpenRouterBackedPaths:
    def test_self_healing_uses_openrouter_when_heuristic_cannot(self, monkeypatch):
        # Enable + mock so the failing snippet gets "repaired" by the LLM.
        monkeypatch.setattr(openrouter_client, "api_key", "k")
        monkeypatch.setattr(
            openrouter_client, "prompt",
            lambda system, user, **kw: "print('healed by opus')",
        )
        result = self_heal_code("raise RuntimeError('boom')", max_iterations=3)
        assert result["success"] is True
        assert "healed by opus" in result["stdout"]

    def test_openrouter_fixer_strips_code_fences(self, monkeypatch):
        monkeypatch.setattr(openrouter_client, "api_key", "k")
        monkeypatch.setattr(
            openrouter_client, "prompt",
            lambda system, user, **kw: "```python\nprint('x')\n```",
        )
        fixed = openrouter_fixer("broken", "Traceback ...")
        assert fixed == "print('x')"

    def test_company_worker_uses_openrouter(self, monkeypatch):
        monkeypatch.setattr(openrouter_client, "api_key", "k")
        monkeypatch.setattr(openrouter_client, "prompt", lambda system, user, **kw: "DELIVERABLE")
        company = CompanyOrchestrator()
        result = company.execute("Build the backend API")
        eng_tasks = [t for t in result["tasks"] if t["role"] == "engineering"]
        assert eng_tasks and eng_tasks[0]["result"]["engine"] == "openrouter"
        assert eng_tasks[0]["result"]["output"] == "DELIVERABLE"

    def test_sop_uses_openrouter_markdown(self, monkeypatch):
        monkeypatch.setattr(openrouter_client, "api_key", "k")
        monkeypatch.setattr(openrouter_client, "prompt", lambda system, user, **kw: "# Polished SOP\n1. Do it")
        result = generate_sop("do a then b", title="Test")
        assert result["engine"] == "openrouter"
        assert result["markdown"] == "# Polished SOP\n1. Do it"
        # Deterministic structure is still present.
        assert result["step_count"] >= 1
        assert "deterministic_markdown" in result


# ---------------------------------------------------------------------------
# Local code-review / security-review engine (no API, no network)
# ---------------------------------------------------------------------------
class TestCodeReview:
    def test_detects_dangerous_calls(self):
        res = review_source("x = eval(input())\n")
        rules = {f["rule"] for f in res["findings"]}
        assert "dangerous-call" in rules

    def test_detects_hardcoded_secret(self):
        res = review_source("api_key = 'supersecretvalue123'\n")
        rules = {f["rule"] for f in res["findings"]}
        assert "hardcoded-secret" in rules

    def test_detects_shell_true_and_bare_except(self):
        src = "import subprocess\ntry:\n    subprocess.run('ls', shell=True)\nexcept:\n    pass\n"
        rules = {f["rule"] for f in review_source(src)["findings"]}
        assert "shell-true" in rules
        assert "bare-except" in rules

    def test_security_only_drops_tech_debt(self):
        src = "# TODO: clean this up\nx = 1\n"
        full = {f["rule"] for f in review_source(src)["findings"]}
        sec = {f["rule"] for f in review_source(src, security_only=True)["findings"]}
        assert "tech-debt" in full
        assert "tech-debt" not in sec

    def test_clean_code_has_no_findings(self):
        res = review_source("def add(a, b):\n    return a + b\n")
        assert res["finding_count"] == 0

    def test_syntax_error_reported(self):
        res = review_source("def broken(:\n")
        assert any(f["rule"] == "syntax-error" for f in res["findings"])

    def test_review_path_on_directory(self, tmp_path):
        (tmp_path / "a.py").write_text("import os\nos.system('echo hi')\n")
        res = review(str(tmp_path))
        assert res["status"] == "ok"
        assert res["files_reviewed"] == 1
        assert any(f["rule"] == "os-system" for f in res["findings"])

    def test_review_skips_non_path_non_source(self):
        assert review("current diff")["status"] == "skipped"


class TestSlashCommandExecution:
    def setup_method(self):
        self.reg = SlashCommandRegistry()

    def test_run_executes_command(self):
        res = self.reg.dispatch(f"/run {sys.executable} -c \"print('hello-run')\"")
        assert res["execution"]["executed"] is True
        assert res["execution"]["returncode"] == 0
        assert "hello-run" in res["execution"]["stdout"]

    def test_verify_passes_on_success(self):
        res = self.reg.dispatch(f"/verify {sys.executable} -c \"import sys; sys.exit(0)\"")
        assert res["passed"] is True

    def test_verify_fails_on_nonzero(self):
        res = self.reg.dispatch(f"/verify {sys.executable} -c \"import sys; sys.exit(3)\"")
        assert res["passed"] is False
        assert res["execution"]["returncode"] == 3

    def test_run_unknown_command_reports_error(self):
        res = self.reg.dispatch("/run this_command_does_not_exist_xyz")
        assert res["execution"]["executed"] is False

    def test_code_review_runs_local_analysis(self):
        res = self.reg.dispatch("/code-review deep x", context={"source": "y = eval('1')\n"})
        assert "analysis" in res
        assert res["analysis"]["finding_count"] >= 1

    def test_security_review_runs_local_analysis(self):
        res = self.reg.dispatch("/security-review", context={"source": "password = 'hunter2hunter2'\n"})
        assert "analysis" in res
        rules = {f["rule"] for f in res["analysis"]["findings"]}
        assert "hardcoded-secret" in rules


class TestHeuristicFixerExtras:
    def test_fixes_python2_print(self):
        fixed = heuristic_fixer("print 'hi'\n", "SyntaxError: Missing parentheses in call to 'print'")
        assert fixed == "print('hi')\n"

    def test_normalizes_tabs(self):
        fixed = heuristic_fixer("if True:\n\tprint(1)\n", "TabError: inconsistent use of tabs and spaces")
        assert "\t" not in fixed

    def test_autoimports_extended_module(self):
        fixed = heuristic_fixer("print(pathlib.Path('.'))\n", "NameError: name 'pathlib' is not defined")
        assert fixed.startswith("import pathlib\n")
