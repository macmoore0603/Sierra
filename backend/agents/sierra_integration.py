# backend/agents/sierra_integration.py
# Updated with Neural Link + Vision

from typing import Any, Optional
from backend.agents.avengers_roster import create_sierra_avengers_crew
from backend.agents.neural_link import NeuralLinkManager
from backend.agents.multimodal import get_vision_system

class SierraAVENGERS:
    def __init__(self, llm: Any):
        self.llm = llm
        self.crew, self.agents = create_sierra_avengers_crew(llm)
        self.neural_link = NeuralLinkManager().get_link()
        self.vision = get_vision_system(llm)
        self.director = self.agents.get("director")

    def chat_with_director(self, user_input: str, image_path: Optional[str] = None):
        context = self.neural_link.get_context()
        enriched = f"[NEURAL LINK CONTEXT]\n{context}\nUser: {user_input}"
        if image_path:
            enriched += "\n[VISUAL]\n" + self.vision.analyze_image(image_path)
        result = self.crew.kickoff([{"description": enriched}])
        return str(result)

    def analyze_image(self, image_path: str):
        return self.vision.analyze_image(image_path)

def get_avengers_system(llm):
    return SierraAVENGERS(llm)