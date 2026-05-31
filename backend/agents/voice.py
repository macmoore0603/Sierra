#!/usr/bin/env python3
"""
Sierra Voice Layer (Echo)

Per-agent voice/persona support.
Handles STT/TTS with distinct voices or prompt-based personas.
Integrates with existing Sierra voice pipeline (low latency, interruptions).

Future: ElevenLabs, OpenAI TTS, system TTS, or on-device models per agent.
"""

from typing import Dict, Optional, Callable

AGENT_PERSONAS: Dict[str, Dict] = {
    "Director Sierra": {
        "voice_id": "director_default",
        "style": "calm, authoritative, helpful, and proactive",
        "greeting": "Sierra systems online. How can I assist you today?",
    },
    "Scout": {
        "voice_id": "scout_inquisitive",
        "style": "curious, precise, insightful",
        "greeting": "Scout here. I've been gathering intelligence for you.",
    },
    "Forge": {
        "voice_id": "forge_engineer",
        "style": "technical, clear, solution-oriented",
        "greeting": "Forge online. Ready to build or fix something?",
    },
    "Chronos": {
        "voice_id": "chronos_timekeeper",
        "style": "organized, calm, efficient",
        "greeting": "Chronos reporting. Your time is in good hands.",
    },
    "Echo": {
        "voice_id": "echo_voice",
        "style": "expressive, warm, natural",
        "greeting": "Echo listening. Voice systems ready.",
    },
    "Sentinel": {
        "voice_id": "sentinel_guardian",
        "style": "serious, protective, clear",
        "greeting": "Sentinel active. Safety protocols engaged.",
    },
    # Add more as needed
}

class VoiceManager:
    def __init__(self, tts_engine: Optional[Callable] = None):
        self.tts_engine = tts_engine  # Inject your existing TTS function
        self.current_agent = "Director Sierra"

    def set_agent(self, agent_role: str):
        self.current_agent = agent_role

    def speak(self, text: str, agent_role: Optional[str] = None):
        """Speak text using the persona of the specified (or current) agent."""
        role = agent_role or self.current_agent
        persona = AGENT_PERSONAS.get(role, AGENT_PERSONAS["Director Sierra"])
        styled_text = f"[{role}] ({persona['style']}): {text}"

        if self.tts_engine:
            # Call your existing Sierra TTS pipeline here
            self.tts_engine(styled_text, voice_id=persona.get("voice_id"))
        else:
            print(styled_text)  # Fallback for demo

    def get_persona_prompt(self, agent_role: str) -> str:
        """Return system prompt addition for LLM to role-play the voice style."""
        persona = AGENT_PERSONAS.get(agent_role, {})
        return f"You are speaking as {agent_role}. Style: {persona.get('style', 'helpful')}. "

# Example integration point with existing Sierra voice system
def get_voice_manager() -> VoiceManager:
    return VoiceManager()
