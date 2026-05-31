#!/usr/bin/env python3
"""
One-line activation helper for Sierra A.V.E.N.G.E.R.S

Copy-paste this into your backend/sierra.py or server.py to instantly enable the full multi-agent system.
"""

# === ADD THIS IMPORT ===
from backend.agents.sierra_integration import get_avengers_system

# === ADD THIS IN YOUR SIERRA CLASS __init__ or server startup ===
# self.avengers = get_avengers_system(self.llm)   # or your LLM instance

# === EXAMPLE USAGE IN YOUR MAIN LOOP ===
"""
# When you receive a complex user request:
# if is_complex_task(user_input):
#     result = self.avengers.handle_complex_task(user_input)
#     return result["final_output"]
#
# For normal chat, you can still use your existing flow,
# or always route through Director for richer responses:
# response = self.avengers.chat_with_director(user_input)
"""

print("Sierra A.V.E.N.G.E.R.S activation helper ready.")
print("See sierra_integration.py and the main README for full wiring instructions.")
