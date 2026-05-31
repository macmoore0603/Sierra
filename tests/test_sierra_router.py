"""
Tests for sierra_router.

These tests exercise the response-parsing logic and the lazy / fail-safe
loading behaviour of the on-device router *without* downloading the
Mac7Moore/ada_model adapter or the FunctionGemma base weights. The actual
inference path is covered by integration tests / manual smoke tests on a
machine with the model present.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

BACKEND_DIR = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(BACKEND_DIR))

import sierra_router  # noqa: E402


# ---------------------------------------------------------------------------
# Catalogue / metadata
# ---------------------------------------------------------------------------


class TestSierraToolCatalogue:
    def test_chat_fallback_is_always_present(self):
        names = {t["function"]["name"] for t in sierra_router.SIERRA_TOOLS}
        assert "chat" in names, (
            "Sierra router must always expose the `chat` fallback tool so "
            "that ambiguous utterances can be forwarded to Gemini Live."
        )

    def test_valid_function_names_match_catalogue(self):
        names = {t["function"]["name"] for t in sierra_router.SIERRA_TOOLS}
        assert names == sierra_router.VALID_FUNCTION_NAMES

    def test_every_tool_has_a_description_and_parameters(self):
        for tool in sierra_router.SIERRA_TOOLS:
            fn = tool["function"]
            assert fn["description"].strip(), fn["name"]
            assert isinstance(fn["parameters"], dict)
            assert fn["parameters"]["type"] == "object"


# ---------------------------------------------------------------------------
# Response parsing
# ---------------------------------------------------------------------------


class TestRouterParser:
    """``SierraRouter._parse`` is a ``@staticmethod`` so we can call it
    directly without loading the model."""

    def test_parse_call_with_escape_format(self):
        resp = (
            "call:control_light{action:<escape>on<escape>,"
            "device_name:<escape>living room<escape>}"
        )
        name, args, conf = sierra_router.SierraRouter._parse(resp, "turn on the lights")
        assert name == "control_light"
        assert args == {"action": "on", "device_name": "living room"}
        assert conf >= 0.9

    def test_parse_call_with_integer_argument(self):
        resp = "call:control_light{action:<escape>dim<escape>,brightness:30}"
        name, args, conf = sierra_router.SierraRouter._parse(resp, "dim the lights")
        assert name == "control_light"
        assert args["action"] == "dim"
        assert args["brightness"] == 30
        assert isinstance(args["brightness"], int)

    def test_parse_call_with_boolean_argument(self):
        resp = "call:set_timer{duration:<escape>5 minutes<escape>,silent:true}"
        name, args, _ = sierra_router.SierraRouter._parse(resp, "5 min")
        assert name == "set_timer"
        assert args["silent"] is True

    def test_parse_call_without_arguments_uses_defaults(self):
        resp = "call:web_search{}"
        name, args, conf = sierra_router.SierraRouter._parse(
            resp, "best pizza in nyc"
        )
        assert name == "web_search"
        assert args == {"query": "best pizza in nyc"}
        # Empty argument block is parsed but the values are filled in from
        # the user prompt, so confidence stays in the "high" band.
        assert 0.6 <= conf <= 1.0

    def test_parse_json_function_call_style(self):
        resp = (
            'Sure! {"name": "set_timer", "arguments": '
            '{"duration": "10 minutes", "label": "pasta"}}'
        )
        name, args, conf = sierra_router.SierraRouter._parse(resp, "pasta timer")
        assert name == "set_timer"
        assert args == {"duration": "10 minutes", "label": "pasta"}
        assert conf > 0.5

    def test_parse_unknown_function_falls_back_to_chat(self):
        resp = "call:nuke_the_planet{target:<escape>earth<escape>}"
        name, args, conf = sierra_router.SierraRouter._parse(resp, "do the thing")
        assert name == "chat"
        assert args == {"prompt": "do the thing"}
        assert conf == 0.0

    def test_parse_empty_response_falls_back_to_chat(self):
        name, args, conf = sierra_router.SierraRouter._parse("", "hello there")
        assert name == "chat"
        assert args == {"prompt": "hello there"}
        assert conf == 0.0


# ---------------------------------------------------------------------------
# Default-arg helper
# ---------------------------------------------------------------------------


class TestRouterDefaultArgs:
    @pytest.mark.parametrize(
        "fn,expected_key",
        [
            ("generate_cad_prototype", "prompt"),
            ("run_web_agent", "task"),
            ("set_timer", "duration"),
            ("switch_project", "name"),
            ("web_search", "query"),
        ],
    )
    def test_default_args_use_correct_field(self, fn, expected_key):
        out = sierra_router.SierraRouter._default_args(fn, "demo text")
        assert expected_key in out
        assert out[expected_key] == "demo text"

    def test_default_args_for_control_light_uses_toggle(self):
        out = sierra_router.SierraRouter._default_args(
            "control_light", "kitchen lamp"
        )
        assert out["action"] == "toggle"
        assert out["device_name"] == "kitchen lamp"


# ---------------------------------------------------------------------------
# RouteResult dataclass
# ---------------------------------------------------------------------------


class TestRouteResult:
    def test_chat_is_fallback(self):
        r = sierra_router.RouteResult(function="chat", arguments={"prompt": "hi"})
        assert r.is_fallback is True

    def test_named_tool_is_not_fallback(self):
        r = sierra_router.RouteResult(function="set_timer")
        assert r.is_fallback is False

    def test_to_dict_contains_expected_keys(self):
        r = sierra_router.RouteResult(
            function="set_timer",
            arguments={"duration": "5m"},
            confidence=0.91,
            latency_ms=42.0,
        )
        d = r.to_dict()
        assert set(d.keys()) == {
            "function", "arguments", "confidence", "latency_ms",
            "is_fallback", "engine",
        }
        assert d["function"] == "set_timer"
        assert d["arguments"] == {"duration": "5m"}
        assert d["is_fallback"] is False


# ---------------------------------------------------------------------------
# Lazy singleton accessor must never raise
# ---------------------------------------------------------------------------


class TestRouterSingletonSafety:
    def test_get_router_returns_none_when_model_unavailable(self, monkeypatch):
        """If the model can't be loaded and no Groq key is set, ``get_router``
        must return ``None`` (not raise) so the rest of Sierra keeps working."""
        # Reset any cached state from earlier tests
        monkeypatch.setattr(sierra_router, "_router_singleton", None)
        monkeypatch.setattr(sierra_router, "_router_error", None)
        monkeypatch.delenv("GROQ_API_KEY", raising=False)

        def boom(*args, **kwargs):
            raise RuntimeError("simulated: no internet / no torch")

        monkeypatch.setattr(sierra_router, "SierraRouter", boom)

        assert sierra_router.get_router() is None
        # Second call uses the cached failure path and must also return None.
        assert sierra_router.get_router() is None


# ---------------------------------------------------------------------------
# Groq cloud fallback router
# ---------------------------------------------------------------------------


class _FakeResponse:
    def __init__(self, payload, status_code=200):
        self._payload = payload
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")

    def json(self):
        return self._payload


class _FakeRequests:
    """Minimal stand-in for the ``requests`` module used by GroqRouter."""

    def __init__(self, message=None, response=None):
        self._message = message
        self._response = response
        self.last_payload = None

    def post(self, url, headers=None, json=None, timeout=None):
        self.last_payload = json
        if self._response is not None:
            return self._response
        return _FakeResponse({"choices": [{"message": self._message}]})


class TestGroqRouter:
    def test_requires_api_key(self, monkeypatch):
        monkeypatch.delenv("GROQ_API_KEY", raising=False)
        with pytest.raises(RuntimeError):
            sierra_router.GroqRouter()

    def test_routes_tool_call(self, monkeypatch):
        router = sierra_router.GroqRouter(api_key="test-key")
        router._requests = _FakeRequests(
            {
                "tool_calls": [
                    {
                        "function": {
                            "name": "set_timer",
                            "arguments": '{"duration": "5 minutes"}',
                        }
                    }
                ]
            }
        )

        result = router.route("set a timer for 5 minutes")
        assert result.function == "set_timer"
        assert result.arguments == {"duration": "5 minutes"}
        assert result.engine == "groq"
        assert result.confidence >= 0.55
        # The Sierra tool catalogue must be forwarded to Groq.
        assert router._requests.last_payload["tools"] == sierra_router.SIERRA_TOOLS

    def test_direct_reply_falls_back_to_chat(self, monkeypatch):
        router = sierra_router.GroqRouter(api_key="test-key")
        router._requests = _FakeRequests({"content": "Hello there!"})

        result = router.route("how are you?")
        assert result.function == "chat"
        assert result.arguments == {"prompt": "how are you?"}
        assert result.is_fallback is True

    def test_unknown_tool_name_falls_back_to_chat(self, monkeypatch):
        router = sierra_router.GroqRouter(api_key="test-key")
        router._requests = _FakeRequests(
            {"tool_calls": [{"function": {"name": "nope", "arguments": "{}"}}]}
        )

        result = router.route("do something weird")
        assert result.function == "chat"

    def test_recovers_from_tool_use_failed(self, monkeypatch):
        """Groq sometimes returns a 400 with the intended call in
        `failed_generation`; the router should recover it, not crash."""
        router = sierra_router.GroqRouter(api_key="test-key")
        failed = _FakeResponse(
            {
                "error": {
                    "code": "tool_use_failed",
                    "failed_generation": (
                        '<function=web_search{"query": "weather in Boston"}'
                        "</function>"
                    ),
                }
            },
            status_code=400,
        )
        router._requests = _FakeRequests(response=failed)

        result = router.route("what's the weather in Boston?")
        assert result.function == "web_search"
        assert result.arguments == {"query": "weather in Boston"}
        assert result.engine == "groq"

    def test_engine_override_selects_groq(self, monkeypatch):
        monkeypatch.setattr(sierra_router, "_router_singleton", None)
        monkeypatch.setattr(sierra_router, "_router_error", None)
        monkeypatch.setattr(sierra_router, "ROUTER_ENGINE", "groq")
        monkeypatch.setenv("GROQ_API_KEY", "test-key")

        router = sierra_router.get_router()
        assert isinstance(router, sierra_router.GroqRouter)
