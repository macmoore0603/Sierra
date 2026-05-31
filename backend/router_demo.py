"""
Sierra real-time command router demo.

Routes natural-language commands through Sierra's router (the on-device
FunctionGemma adapter, or the Groq cloud fallback when ``GROQ_API_KEY`` is set)
and prints the structured tool call plus latency. This is the "Sierra does
commands in real time" fast path that sits in front of the Gemini Live loop.

Usage::

    # Force the Groq cloud engine (no local model download needed):
    SIERRA_ROUTER_ENGINE=groq GROQ_API_KEY=... python backend/router_demo.py

    # Pass your own commands:
    python backend/router_demo.py "turn off the lights" "set a timer for 5m"

    # Interactive REPL (no args):
    python backend/router_demo.py
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import sierra_router  # noqa: E402

DEMO_COMMANDS = [
    "turn off the kitchen lights",
    "design a hex bolt with a 10mm head",
    "set a timer for 5 minutes",
    "search the web for the best pizza in NYC",
    "open a browser and find a USB-C cable on Amazon",
    "switch to my Sierra project",
    "what do you think about the meaning of life?",
]


def _print_route(router, text: str) -> None:
    result = router.route(text)
    print(f"> {text}")
    print(
        f"    -> {result.function}  "
        f"args={result.arguments}  "
        f"conf={result.confidence:.2f}  "
        f"{result.latency_ms:.0f}ms  via {result.engine}"
    )


def main(argv: list[str]) -> int:
    router = sierra_router.get_router()
    if router is None:
        print(
            "No router available. Install the local model deps or set "
            "GROQ_API_KEY (optionally SIERRA_ROUTER_ENGINE=groq).",
            file=sys.stderr,
        )
        return 1

    engine = getattr(router, "engine", "local")
    print(f"Sierra router ready (engine: {engine}).\n")

    commands = argv[1:]
    if commands:
        for text in commands:
            _print_route(router, text)
        return 0

    if not sys.stdin.isatty():
        for text in DEMO_COMMANDS:
            _print_route(router, text)
        return 0

    print("Type a command (blank line or Ctrl-D to quit):")
    try:
        while True:
            text = input("\nsierra> ").strip()
            if not text:
                break
            _print_route(router, text)
    except EOFError:
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
