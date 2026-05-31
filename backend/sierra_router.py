"""
Sierra Local Router
===================

A small, fast, on-device function-calling router that sits in front of the
heavyweight Gemini Live pipeline. The router classifies the user's text into
one of Sierra's tool intents (or a passthrough "chat"/"reasoning" bucket) and
returns a structured ``(function_name, arguments)`` tuple.

It is a drop-in performance upgrade for Sierra:

* Instead of round-tripping every utterance to Google Gemini, Sierra first
  tries the local router. Short, well-defined intents (light control, timers,
  CAD prototype, web search, smart-home actions, etc.) are dispatched
  instantly from the device.
* Anything the router can't confidently route (or that it labels as
  ``chat`` / ``reasoning``) falls through to the existing Gemini Live API
  pipeline -- so multimodal voice/vision interactions still work exactly as
  before.

Model
-----

The router uses
`Mac7Moore/ada_model <https://huggingface.co/Mac7Moore/ada_model>`_, a LoRA
adapter on top of
`google/functiongemma-270m-it <https://huggingface.co/google/functiongemma-270m-it>`_
trained for tool / function calling. Total VRAM footprint is roughly 600 MB
in fp32 (less in bfloat16 on GPU). On CPU it still runs comfortably in
hundreds of milliseconds per query, which is well within the latency budget
for "instant" voice commands.

Design notes
------------

* The router is **optional**. If ``transformers`` / ``peft`` aren't installed
  or the model can't be downloaded (no internet, no HF token, etc.) Sierra
  silently falls back to Gemini-only mode -- nothing else in the app changes.
* Loading is lazy. The first call to :func:`get_router` warms up the model
  in a background thread; the second call returns the cached instance.
* The router exposes :meth:`SierraRouter.route` which returns
  ``(function_name, arguments_dict, confidence)``. Callers decide whether the
  confidence is high enough to act on locally or to forward to Gemini.

This module is heavily inspired by the
`A.D.A Local <https://github.com/nazirlouis/ada_local>`_ FunctionGemma router
(MIT licensed, Copyright (c) 2025 Nazir Louis) -- the parsing/format protocol
is intentionally compatible.
"""

from __future__ import annotations

import json
import logging
import os
import re
import threading
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("sierra.router")

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# HuggingFace repo for the fine-tuned LoRA adapter.
HF_ADAPTER_REPO = os.environ.get(
    "SIERRA_ROUTER_ADAPTER",
    "Mac7Moore/ada_model",
)

# Base model the adapter was trained on. Override if you have a local copy.
HF_BASE_MODEL = os.environ.get(
    "SIERRA_ROUTER_BASE_MODEL",
    "google/functiongemma-270m-it",
)

# Local cache directory. Defaults to ~/.cache/sierra/router.
LOCAL_CACHE_DIR = os.environ.get(
    "SIERRA_ROUTER_CACHE",
    os.path.join(os.path.expanduser("~"), ".cache", "sierra", "router"),
)

# Pinned revision of the adapter on HF (matches what the user linked).
ADAPTER_REVISION = os.environ.get(
    "SIERRA_ROUTER_ADAPTER_REV",
    "d6ed94af7a7a09e8f2b88a2feee7877fd2811e64",
)

# Maximum new tokens generated per route call. The function-calling format
# is compact, so 96 is plenty.
MAX_NEW_TOKENS = int(os.environ.get("SIERRA_ROUTER_MAX_NEW_TOKENS", "96"))

# Below this routing confidence we fall back to Gemini.
DEFAULT_CONFIDENCE_THRESHOLD = float(
    os.environ.get("SIERRA_ROUTER_THRESHOLD", "0.55")
)

# Which engine backs the router:
#   "auto"  -> try the local FunctionGemma adapter, fall back to Groq if it
#              can't load and GROQ_API_KEY is set.
#   "local" -> only the on-device adapter.
#   "groq"  -> skip the local model entirely and route via Groq.
ROUTER_ENGINE = os.environ.get("SIERRA_ROUTER_ENGINE", "auto").lower()

# Groq cloud fallback configuration (OpenAI-compatible API).
GROQ_BASE_URL = os.environ.get(
    "GROQ_BASE_URL", "https://api.groq.com/openai/v1"
)
GROQ_MODEL = os.environ.get(
    "SIERRA_GROQ_MODEL", "llama-3.3-70b-versatile"
)


# ---------------------------------------------------------------------------
# Tool catalogue exposed to the router
# ---------------------------------------------------------------------------
#
# These mirror Sierra's "fast path" intents -- things we can dispatch without
# bothering Gemini. Keep this list short and high-precision; everything else
# should fall through to ``chat`` (Gemini Live).


SIERRA_TOOLS: List[Dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "generate_cad_prototype",
            "description": (
                "Generate a 3D CAD prototype / wireframe from a natural "
                "language description (e.g. 'design a hex bolt with a 10mm "
                "head')."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "Description of the object to model.",
                    }
                },
                "required": ["prompt"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_web_agent",
            "description": (
                "Open a browser and let the autonomous agent complete a "
                "task on the web (e.g. 'find a USB-C cable on Amazon')."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "task": {
                        "type": "string",
                        "description": "Plain-English task for the agent.",
                    }
                },
                "required": ["task"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "control_light",
            "description": (
                "Turn a smart light on / off / dim it, or change its color."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "description": "on, off, dim, toggle",
                    },
                    "device_name": {
                        "type": "string",
                        "description": "Room or device label.",
                    },
                    "brightness": {
                        "type": "integer",
                        "description": "0-100",
                    },
                    "color": {
                        "type": "string",
                        "description": "Color name or hex code.",
                    },
                },
                "required": ["action"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "set_timer",
            "description": "Set a countdown timer.",
            "parameters": {
                "type": "object",
                "properties": {
                    "duration": {
                        "type": "string",
                        "description": "e.g. '5 minutes' or '1 hour'",
                    },
                    "label": {"type": "string"},
                },
                "required": ["duration"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "switch_project",
            "description": "Switch Sierra's active project context.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                },
                "required": ["name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Look something up on the web.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "chat",
            "description": (
                "Fallback: anything conversational, multimodal, or that "
                "requires the full Gemini Live pipeline (voice replies, "
                "vision, reasoning). Use this whenever no specific tool "
                "above fits."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "prompt": {"type": "string"},
                },
                "required": ["prompt"],
            },
        },
    },
]


VALID_FUNCTION_NAMES = {t["function"]["name"] for t in SIERRA_TOOLS}


# ---------------------------------------------------------------------------
# Result / availability dataclasses
# ---------------------------------------------------------------------------


@dataclass
class RouteResult:
    """Result of routing a single user utterance."""

    function: str
    arguments: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0
    latency_ms: float = 0.0
    raw_response: str = ""
    engine: str = "local"

    @property
    def is_fallback(self) -> bool:
        return self.function == "chat"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "function": self.function,
            "arguments": self.arguments,
            "confidence": self.confidence,
            "latency_ms": self.latency_ms,
            "is_fallback": self.is_fallback,
            "engine": self.engine,
        }


# ---------------------------------------------------------------------------
# Router implementation
# ---------------------------------------------------------------------------


class SierraRouter:
    """Wraps the Mac7Moore/ada_model LoRA adapter for local function calling."""

    def __init__(
        self,
        adapter_repo: str = HF_ADAPTER_REPO,
        base_model: str = HF_BASE_MODEL,
        cache_dir: str = LOCAL_CACHE_DIR,
        adapter_revision: Optional[str] = ADAPTER_REVISION,
        device: Optional[str] = None,
    ) -> None:
        # Imports are deferred so that ``import sierra_router`` itself never
        # fails on machines without transformers/peft installed.
        try:
            import torch  # type: ignore
            from huggingface_hub import snapshot_download  # type: ignore
            from peft import PeftModel  # type: ignore
            from transformers import (  # type: ignore
                AutoModelForCausalLM,
                AutoTokenizer,
            )
        except ImportError as exc:  # pragma: no cover - depends on env
            raise RuntimeError(
                "Sierra router requires transformers, peft, huggingface_hub "
                "and torch. Install Sierra's optional deps via "
                "`pip install -r requirements.txt`."
            ) from exc

        os.makedirs(cache_dir, exist_ok=True)

        chosen_device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        dtype = torch.bfloat16 if chosen_device == "cuda" else torch.float32

        logger.info(
            "Loading Sierra router (base=%s, adapter=%s@%s, device=%s)",
            base_model,
            adapter_repo,
            (adapter_revision or "main")[:10],
            chosen_device,
        )

        start = time.time()

        adapter_path = snapshot_download(
            repo_id=adapter_repo,
            revision=adapter_revision,
            cache_dir=cache_dir,
            allow_patterns=[
                "adapter_config.json",
                "adapter_model.safetensors",
                "tokenizer.json",
                "tokenizer_config.json",
                "special_tokens_map.json",
                "chat_template.jinja",
            ],
        )

        self.tokenizer = AutoTokenizer.from_pretrained(adapter_path)
        base = AutoModelForCausalLM.from_pretrained(
            base_model,
            torch_dtype=dtype,
            device_map=chosen_device,
        )
        self.model = PeftModel.from_pretrained(base, adapter_path)
        self.model.eval()
        self.device = chosen_device
        self._torch = torch  # keep handle so callers don't need to import

        logger.info(
            "Sierra router ready in %.2fs (device=%s, dtype=%s)",
            time.time() - start,
            self.device,
            dtype,
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def route(
        self,
        user_text: str,
        confidence_threshold: float = DEFAULT_CONFIDENCE_THRESHOLD,
    ) -> RouteResult:
        """Classify ``user_text`` into a Sierra tool call."""

        if not user_text or not user_text.strip():
            return RouteResult(function="chat", arguments={"prompt": ""})

        prompt = self._build_prompt(user_text)
        torch = self._torch

        with torch.inference_mode():
            inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
            t0 = time.time()
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=MAX_NEW_TOKENS,
                do_sample=False,
                use_cache=True,
                pad_token_id=self.tokenizer.pad_token_id
                or self.tokenizer.eos_token_id,
            )
            latency_ms = (time.time() - t0) * 1000.0

        new_tokens = outputs[0][inputs["input_ids"].shape[1]:]
        response = self.tokenizer.decode(new_tokens, skip_special_tokens=False)

        function, arguments, confidence = self._parse(response, user_text)
        if confidence < confidence_threshold:
            function = "chat"
            arguments = {"prompt": user_text}

        return RouteResult(
            function=function,
            arguments=arguments,
            confidence=confidence,
            latency_ms=latency_ms,
            raw_response=response,
        )

    # ------------------------------------------------------------------
    # Prompt building / response parsing
    # ------------------------------------------------------------------

    _SYSTEM = (
        "You are Sierra's on-device function router. Pick exactly one of the "
        "provided tools that best matches the user's intent. If nothing fits, "
        "call `chat` with the user's message."
    )

    def _build_prompt(self, user_text: str) -> str:
        messages = [
            {"role": "developer", "content": self._SYSTEM},
            {"role": "user", "content": user_text},
        ]
        try:
            return self.tokenizer.apply_chat_template(
                messages,
                tools=SIERRA_TOOLS,
                add_generation_prompt=True,
                tokenize=False,
            )
        except Exception:  # pragma: no cover - template-dependent
            # Fallback: dump tools as JSON. The fine-tuned chat template
            # should always be present in the adapter repo, but if a user
            # points us at a vanilla base model we still produce *some*
            # prompt rather than blowing up.
            return (
                f"<system>{self._SYSTEM}</system>\n"
                f"<tools>{json.dumps(SIERRA_TOOLS)}</tools>\n"
                f"<user>{user_text}</user>\n"
            )

    @staticmethod
    def _parse(response: str, user_text: str) -> Tuple[str, Dict[str, Any], float]:
        """Best-effort parse of the model's function-call output."""

        # 1) Strict `call:<name>{key:<escape>value<escape>,...}` format used
        #    by the upstream FunctionGemma chat template.
        for name in VALID_FUNCTION_NAMES:
            if f"call:{name}" not in response:
                continue
            block_match = re.search(
                rf"call:{re.escape(name)}\{{([^}}]*)\}}", response
            )
            args: Dict[str, Any] = {}
            if block_match:
                body = block_match.group(1)
                arg_pattern = (
                    r"(\w+):(?:<escape>([^<]*)<escape>|([^,}]+))"
                )
                for m in re.finditer(arg_pattern, body):
                    key = m.group(1)
                    val = m.group(2) if m.group(2) is not None else m.group(3)
                    val = (val or "").strip()
                    if val.isdigit():
                        args[key] = int(val)
                    elif val.lower() in {"true", "false"}:
                        args[key] = val.lower() == "true"
                    else:
                        args[key] = val
            # If we parsed nothing useful, plug the user's text into the
            # most likely required field.
            if not args:
                args = SierraRouter._default_args(name, user_text)

            confidence = 0.95 if block_match else 0.75
            return name, args, confidence

        # 2) Plain JSON `{"name": "...", "arguments": {...}}` style.
        json_match = re.search(r"\{[\s\S]*\}", response)
        if json_match:
            try:
                payload = json.loads(json_match.group(0))
            except json.JSONDecodeError:
                payload = None
            if isinstance(payload, dict):
                name = payload.get("name") or payload.get("function")
                args = payload.get("arguments") or payload.get("parameters") or {}
                if name in VALID_FUNCTION_NAMES and isinstance(args, dict):
                    return name, args, 0.7

        # 3) Last resort: chat fallback.
        return "chat", {"prompt": user_text}, 0.0

    @staticmethod
    def _default_args(name: str, user_text: str) -> Dict[str, Any]:
        if name == "generate_cad_prototype":
            return {"prompt": user_text}
        if name == "run_web_agent":
            return {"task": user_text}
        if name == "set_timer":
            return {"duration": user_text}
        if name == "control_light":
            return {"action": "toggle", "device_name": user_text}
        if name == "switch_project":
            return {"name": user_text}
        if name == "web_search":
            return {"query": user_text}
        return {"prompt": user_text}


# ---------------------------------------------------------------------------
# Groq cloud fallback router
# ---------------------------------------------------------------------------


class GroqRouter:
    """Cloud router using Groq's OpenAI-compatible function calling.

    A drop-in replacement for :class:`SierraRouter` (same ``route`` signature
    and :class:`RouteResult` output) for when the local FunctionGemma adapter
    can't be loaded but a ``GROQ_API_KEY`` is configured. Groq's LPU inference
    keeps latency low enough for "instant" command routing.
    """

    engine = "groq"

    _SYSTEM = (
        "You are Sierra's command router. Choose exactly one tool that best "
        "matches the user's intent. Use the `chat` tool for anything "
        "conversational, multimodal, or that doesn't fit another tool."
    )

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = GROQ_MODEL,
        base_url: str = GROQ_BASE_URL,
    ) -> None:
        # Deferred so importing this module never requires `requests`.
        try:
            import requests  # type: ignore
        except ImportError as exc:  # pragma: no cover - depends on env
            raise RuntimeError(
                "GroqRouter requires the `requests` package."
            ) from exc

        self._requests = requests
        self.api_key = api_key or os.environ.get("GROQ_API_KEY")
        if not self.api_key:
            raise RuntimeError("GroqRouter requires GROQ_API_KEY to be set.")
        self.model = model
        self.base_url = base_url.rstrip("/")
        logger.info("Sierra router using Groq cloud engine (model=%s)", self.model)

    def route(
        self,
        user_text: str,
        confidence_threshold: float = DEFAULT_CONFIDENCE_THRESHOLD,
    ) -> RouteResult:
        """Classify ``user_text`` into a Sierra tool call via Groq."""

        if not user_text or not user_text.strip():
            return RouteResult(
                function="chat", arguments={"prompt": ""}, engine=self.engine
            )

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": self._SYSTEM},
                {"role": "user", "content": user_text},
            ],
            "tools": SIERRA_TOOLS,
            "tool_choice": "auto",
            "temperature": 0,
            "max_tokens": MAX_NEW_TOKENS,
        }

        t0 = time.time()
        resp = self._requests.post(
            f"{self.base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=30,
        )
        latency_ms = (time.time() - t0) * 1000.0

        # Llama models on Groq occasionally emit a tool call in a format their
        # server-side parser rejects (HTTP 400 `tool_use_failed`). The intended
        # call is returned in `failed_generation`, so recover it instead of
        # failing the whole route.
        if resp.status_code == 400:
            recovered = self._recover_failed_generation(resp, user_text, latency_ms)
            if recovered is not None:
                return recovered

        resp.raise_for_status()

        message = resp.json()["choices"][0]["message"]
        tool_calls = message.get("tool_calls") or []

        if tool_calls:
            call = tool_calls[0].get("function", {})
            name = call.get("name", "chat")
            try:
                args = json.loads(call.get("arguments") or "{}")
            except (json.JSONDecodeError, TypeError):
                args = {}
            if name not in VALID_FUNCTION_NAMES:
                name, args = "chat", {"prompt": user_text}
            if not isinstance(args, dict) or not args:
                args = SierraRouter._default_args(name, user_text)
            confidence = 0.9 if name != "chat" else 0.5
            raw = json.dumps({"name": name, "arguments": args})
        else:
            # Model replied directly instead of calling a tool -> chat passthrough.
            name = "chat"
            args = {"prompt": user_text}
            confidence = 0.3
            raw = message.get("content") or ""

        if confidence < confidence_threshold:
            name = "chat"
            args = {"prompt": user_text}

        return RouteResult(
            function=name,
            arguments=args,
            confidence=confidence,
            latency_ms=latency_ms,
            raw_response=raw,
            engine=self.engine,
        )

    def _recover_failed_generation(
        self, resp, user_text: str, latency_ms: float
    ) -> Optional[RouteResult]:
        """Recover a tool call from Groq's ``tool_use_failed`` (400) payload.

        The malformed generation looks like
        ``<function=web_search{"query": "..."}</function>``; parse the function
        name + JSON args out of it. Returns ``None`` if this isn't a
        recoverable ``tool_use_failed`` error.
        """
        try:
            error = resp.json().get("error", {})
        except ValueError:
            return None
        if error.get("code") != "tool_use_failed":
            return None

        generated = error.get("failed_generation", "") or ""
        match = re.search(r"<function=(\w+)\s*(\{.*\})", generated, re.S)
        if not match:
            return None

        name = match.group(1)
        try:
            args = json.loads(match.group(2))
        except json.JSONDecodeError:
            args = {}
        if name not in VALID_FUNCTION_NAMES:
            name, args = "chat", {"prompt": user_text}
        if not isinstance(args, dict) or not args:
            args = SierraRouter._default_args(name, user_text)

        confidence = 0.85 if name != "chat" else 0.5
        return RouteResult(
            function=name,
            arguments=args,
            confidence=confidence,
            latency_ms=latency_ms,
            raw_response=generated,
            engine=self.engine,
        )


# ---------------------------------------------------------------------------
# Lazy singleton accessor
# ---------------------------------------------------------------------------


_router_singleton: Optional[SierraRouter] = None
_router_lock = threading.Lock()
_router_error: Optional[Exception] = None


def get_router() -> Optional[SierraRouter]:
    """Return the shared :class:`SierraRouter`, or ``None`` if unavailable.

    The first call may block on model download / load. Failures (no internet,
    missing dependencies, etc.) are logged once and cached so subsequent
    callers fall back to Gemini without retrying.
    """

    global _router_singleton, _router_error
    if _router_singleton is not None:
        return _router_singleton
    if _router_error is not None:
        return None

    with _router_lock:
        if _router_singleton is not None:
            return _router_singleton
        if _router_error is not None:
            return None

        # Explicit Groq-only mode: skip the local model entirely.
        if ROUTER_ENGINE == "groq":
            try:
                _router_singleton = GroqRouter()
                return _router_singleton
            except Exception as exc:  # pragma: no cover - depends on env
                logger.warning("Groq router unavailable: %s", exc)
                _router_error = exc
                return None

        try:
            _router_singleton = SierraRouter()
            return _router_singleton
        except Exception as exc:  # pragma: no cover - depends on env
            logger.warning("Local Sierra router unavailable: %s", exc)
            # Cloud fallback: route via Groq if configured (unless forced local).
            if ROUTER_ENGINE != "local" and os.environ.get("GROQ_API_KEY"):
                try:
                    _router_singleton = GroqRouter()
                    logger.info(
                        "Falling back to Groq cloud router for real-time "
                        "command routing."
                    )
                    return _router_singleton
                except Exception as groq_exc:  # pragma: no cover - depends on env
                    logger.warning("Groq router unavailable: %s", groq_exc)
                    _router_error = groq_exc
                    return None
            logger.warning("Falling back to Gemini-only mode.")
            _router_error = exc
            return None


def warm_up_async() -> threading.Thread:
    """Start loading the router in the background.

    Sierra's server calls this at startup so the very first user utterance
    doesn't pay the cold-start cost.
    """

    thread = threading.Thread(
        target=get_router, name="sierra-router-warmup", daemon=True
    )
    thread.start()
    return thread


__all__ = [
    "SIERRA_TOOLS",
    "VALID_FUNCTION_NAMES",
    "RouteResult",
    "SierraRouter",
    "GroqRouter",
    "get_router",
    "warm_up_async",
]
