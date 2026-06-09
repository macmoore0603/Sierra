"""
OpenRouter Client
=================

A tiny, dependency-free client for OpenRouter's Chat Completions API, used to
back Sierra's agentic capabilities (self-healing coder, AI-company role workers,
SOP rewriting) with a strong reasoning model -- Claude Opus by default.

Design:
- **Stdlib only.** Uses ``urllib`` so it works on a bare backend; if ``requests``
  is present it is used for nicer timeouts/retries.
- **Graceful degradation.** If ``OPENROUTER_API_KEY`` is unset or a call fails,
  :meth:`OpenRouterClient.complete` returns ``None`` so callers fall back to
  their deterministic logic instead of crashing.
- **Configurable.** Model and base URL come from the environment:
    - ``OPENROUTER_API_KEY``  -- required to actually call the API.
    - ``OPENROUTER_MODEL``    -- defaults to ``anthropic/claude-opus-4.8``.
    - ``OPENROUTER_BASE_URL`` -- defaults to ``https://openrouter.ai/api/v1``.
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional
from urllib import request as urllib_request
from urllib.error import HTTPError, URLError

DEFAULT_MODEL = os.environ.get("OPENROUTER_MODEL", "anthropic/claude-opus-4.8")
DEFAULT_BASE_URL = os.environ.get("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
# OpenRouter reserves credit = max_tokens * output_price up front, so an
# oversized cap 402s on low-balance accounts. Keep a balance-safe default;
# raise OPENROUTER_MAX_TOKENS once the account has more credit.
DEFAULT_MAX_TOKENS = int(os.environ.get("OPENROUTER_MAX_TOKENS", "1024"))


class OpenRouterClient:
    """Minimal Chat Completions client for OpenRouter."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: float = 60.0,
    ):
        self.api_key = api_key if api_key is not None else os.environ.get("OPENROUTER_API_KEY", "")
        self.model = model or DEFAULT_MODEL
        self.base_url = (base_url or DEFAULT_BASE_URL).rstrip("/")
        self.timeout = timeout

    @property
    def enabled(self) -> bool:
        """True when an API key is configured (so calls can actually be made)."""
        return bool(self.api_key)

    def complete(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: Optional[int] = None,
    ) -> Optional[str]:
        """Return the assistant message content, or ``None`` on any failure.

        Callers should treat ``None`` as "LLM unavailable -- use fallback".
        """
        if not self.enabled:
            return None

        payload = {
            "model": model or self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens if max_tokens is not None else DEFAULT_MAX_TOKENS,
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            # Optional attribution headers OpenRouter recommends.
            "HTTP-Referer": os.environ.get("OPENROUTER_REFERER", "https://github.com/macmoore0603/Sierra"),
            "X-Title": "Sierra",
        }
        url = f"{self.base_url}/chat/completions"

        try:
            data = self._post(url, payload, headers)
        except (HTTPError, URLError, OSError, ValueError):
            return None

        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError):
            return None

    def prompt(self, system: str, user: str, **kwargs: Any) -> Optional[str]:
        """Convenience: single system+user turn."""
        return self.complete(
            [{"role": "system", "content": system}, {"role": "user", "content": user}],
            **kwargs,
        )

    # -- transport -----------------------------------------------------------

    def _post(self, url: str, payload: Dict[str, Any], headers: Dict[str, str]) -> Dict[str, Any]:
        try:
            import requests  # type: ignore

            resp = requests.post(url, json=payload, headers=headers, timeout=self.timeout)
            resp.raise_for_status()
            return resp.json()
        except ImportError:
            body = json.dumps(payload).encode("utf-8")
            req = urllib_request.Request(url, data=body, headers=headers, method="POST")
            with urllib_request.urlopen(req, timeout=self.timeout) as resp:  # noqa: S310 (trusted endpoint)
                return json.loads(resp.read().decode("utf-8"))


# Module-level singleton for convenient imports.
openrouter_client = OpenRouterClient()
