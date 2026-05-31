# backend/agents/neural_link.py
# Maxed Neural Link with Proactive Mode

from typing import Dict, Any, List
from datetime import datetime
import json
import os

class NeuralLink:
    def __init__(self, user_id: str = "default"):
        self.user_id = user_id
        self.storage_path = "./memory/neural_link"
        os.makedirs(self.storage_path, exist_ok=True)
        self.state_file = os.path.join(self.storage_path, f"{user_id}_state.json")
        self.user_state = self._load()

    def _load(self):
        if os.path.exists(self.state_file):
            with open(self.state_file) as f:
                return json.load(f)
        return {"energy": None, "focus": None, "goals": [], "last_updated": None}

    def update_state(self, updates: Dict):
        self.user_state.update(updates)
        self.user_state["last_updated"] = datetime.now().isoformat()
        with open(self.state_file, "w") as f:
            json.dump(self.user_state, f, indent=2)

    def get_context(self) -> str:
        return str(self.user_state)

    def predict_needs(self) -> List[str]:
        needs = []
        if self.user_state.get("energy") == "low":
            needs.append("Suggest break or energy reset")
        if self.user_state.get("focus") == "low":
            needs.append("Help with prioritization")
        return needs or ["User appears balanced"]

    def run_proactive_check(self):
        predictions = self.predict_needs()
        if predictions:
            return {"action": "proactive_suggestion", "suggestions": predictions}
        return None

class NeuralLinkManager:
    _instance = None
    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance.link = NeuralLink()
        return cls._instance

    def get_link(self):
        return self.link