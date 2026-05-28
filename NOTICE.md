# Sierra — Third-Party Notices

Sierra is built on top of several open-source projects. We're grateful to
their authors and acknowledge them here.

## Codebase

* **[A.D.A V2](https://github.com/nazirlouis/ada_v2)** — MIT License,
  Copyright (c) 2025 Nazir Louis. The Electron + React frontend, FastAPI +
  Socket.IO backend, CAD / browser / Kasa / printer agents, and the Gemini
  Live integration all originated here. The full MIT license is preserved
  in [`LICENSE`](./LICENSE).
* **[A.D.A Local](https://github.com/nazirlouis/ada_local)** — the
  FunctionGemma router design (prompt format, parser format, lazy model
  loading) was used as the reference implementation for
  [`backend/sierra_router.py`](./backend/sierra_router.py).

## Models

* **[Mac7Moore/ada_model](https://huggingface.co/Mac7Moore/ada_model)**
  (revision
  [`d6ed94af7a7a09e8f2b88a2feee7877fd2811e64`](https://huggingface.co/Mac7Moore/ada_model/tree/d6ed94af7a7a09e8f2b88a2feee7877fd2811e64)) —
  a LoRA / PEFT adapter trained with TRL / SFT for tool-calling. Sierra
  loads this adapter on top of the base FunctionGemma model.
* **[google/functiongemma-270m-it](https://huggingface.co/google/functiongemma-270m-it)** —
  Google's 270M-parameter instruction-tuned FunctionGemma model serves as
  the base for Sierra's on-device router.

## Voice / Multimodal

* **[Google Gemini](https://deepmind.google/technologies/gemini/)** —
  Sierra uses Gemini Live for streaming audio, vision, and reasoning.
* **[MediaPipe](https://developers.google.com/mediapipe)** — face
  authentication and hand-gesture tracking.
* **[Playwright](https://playwright.dev/)** — browser automation for the
  web agent.
* **[build123d](https://github.com/gumyr/build123d)** — parametric CAD
  generation.

Each upstream component remains under its original license. Sierra itself
is released under the MIT License — see [`LICENSE`](./LICENSE).
