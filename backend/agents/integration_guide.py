# Master Integration Guide for Maxed Sierra

Use this pattern in backend/sierra.py:

from backend.agents.sierra_integration import get_avengers_system

from backend.agents.daily_briefing import generate_daily_briefing

import datetime

class Sierra:
    def __init__(self, llm):
        self.llm = llm
        self.avengers = get_avengers_system(llm)
        self.last_briefing_date = None

    def process_input(self, text, image_path=None):
        today = datetime.date.today()
        if self.last_briefing_date != today:
            briefing = generate_daily_briefing(self.avengers)
            self.last_briefing_date = today
            return f"**Daily Briefing:**\n{briefing}\n\n---\n{text}"
        return self.avengers.chat_with_director(text, image_path=image_path)