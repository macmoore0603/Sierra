"""
Tests for the God Mode real-time execution policy (backend/execution_policy.py).

These assert that in God Mode tools run immediately (no confirmation), that
truly destructive ops stay gated, and that disabling God Mode falls back to the
per-tool permission map. Pure logic — no Gemini / audio stack required.
"""
from execution_policy import requires_confirmation, DEFAULT_CONFIRM_TOOLS


class TestRealtimeExecutionPolicy:

    def test_god_mode_runs_normal_tools_immediately(self):
        for tool in ["write_file", "run_web_agent", "control_light", "generate_cad"]:
            assert requires_confirmation(tool, god_mode=True) is False

    def test_god_mode_still_gates_destructive_tools(self):
        for tool in DEFAULT_CONFIRM_TOOLS:
            assert requires_confirmation(tool, god_mode=True) is True

    def test_custom_confirm_tools_override_defaults(self):
        # A non-default tool can be explicitly gated...
        assert requires_confirmation("spend_money", god_mode=True,
                                      confirm_tools={"spend_money"}) is True
        # ...and a normally-destructive name runs if confirm_tools is emptied.
        assert requires_confirmation("delete_file", god_mode=True,
                                      confirm_tools=set()) is False

    def test_god_mode_off_falls_back_to_permissions(self):
        # Unknown tool defaults to confirmation required (fail safe).
        assert requires_confirmation("write_file", god_mode=False) is True
        # Explicit permission False (== no confirmation) is honored.
        assert requires_confirmation("write_file", god_mode=False,
                                     permissions={"write_file": False}) is False
        # Explicit permission True keeps the gate.
        assert requires_confirmation("write_file", god_mode=False,
                                     permissions={"write_file": True}) is True

    def test_destructive_gate_independent_of_permissions_in_god_mode(self):
        # Even if a destructive tool is "permitted", God Mode still confirms it.
        assert requires_confirmation("factory_reset", god_mode=True,
                                     permissions={"factory_reset": False}) is True
