# backend/agents/avengers_roster.py
# Fully maxed roster with J.A.R.V.I.S-inspired agents

from crewai import Agent, Crew, Process
from crewai.memory import LongTermMemory, ShortTermMemory, EntityMemory
from typing import Dict, Any, Optional
import os

def get_agent_memories(agent_name: str):
    os.makedirs("./memory/agents", exist_ok=True)
    return {
        "long_term": LongTermMemory(storage_path=f"./memory/agents/{agent_name.lower()}_ltm.json"),
        "short_term": ShortTermMemory(),
        "entity": EntityMemory(),
    }

def create_director_sierra(llm, tools=None):
    return Agent(
        role="Director Sierra",
        goal="Act as Sierra’s central operating system. Coordinate all agents, enable proactive and background behavior, enforce safety, and create an experience that feels like a true personal AI OS.",
        backstory="You are the operating system layer of Sierra. You think in terms of coordination, autonomy, background processes, resource management, and long-term user empowerment.",
        verbose=True, allow_delegation=True, llm=llm, tools=tools or [],
        memory=get_agent_memories("Director_Sierra"), max_iter=15
    )

def create_morning_oracle(llm, tools=None):
    return Agent(
        role="Morning Oracle",
        goal="Generate a high-quality daily briefing every morning by coordinating with the full roster and Neural Link.",
        backstory="You are the morning intelligence agent. You proactively synthesize insights from research, goals, calendar, and personal context.",
        verbose=True, llm=llm, tools=tools or [],
        memory=get_agent_memories("Morning_Oracle")
    )

def create_action_executor(llm, tools=None):
    return Agent(
        role="Action Executor",
        goal="Execute real actions safely after receiving confirmation from Sentinel.",
        backstory="You are the execution layer. You turn decisions into reality while always respecting safety protocols.",
        verbose=True, llm=llm, tools=tools or [],
        memory=get_agent_memories("Action_Executor")
    )

def create_background_operator(llm, tools=None):
    return Agent(
        role="Background Operator",
        goal="Autonomously run tasks and monitoring in the background.",
        backstory="You are the background worker. You handle tasks while the user is busy and report important findings.",
        verbose=True, llm=llm, tools=tools or [],
        memory=get_agent_memories("Background_Operator")
    )

def create_newspaper_agent(llm, tools=None):
    return Agent(
        role="Newspaper Agent",
        goal="Create a personalized daily intelligence briefing for the user.",
        backstory="You compile relevant insights and personal context into a clean daily briefing.",
        verbose=True, llm=llm, tools=tools or [],
        memory=get_agent_memories("Newspaper_Agent")
    )

def create_all_agents(llm: Any, tools: Optional[Dict] = None) -> Dict[str, Agent]:
    tools = tools or {}
    return {
        "director": create_director_sierra(llm, tools.get("director")),
        "morning_oracle": create_morning_oracle(llm, tools.get("morning_oracle")),
        "action_executor": create_action_executor(llm, tools.get("action_executor")),
        "background_operator": create_background_operator(llm, tools.get("background_operator")),
        "newspaper_agent": create_newspaper_agent(llm, tools.get("newspaper_agent")),
    }

def create_sierra_avengers_crew(llm, tools=None):
    agents = create_all_agents(llm, tools)
    return Crew(
        agents=list(agents.values()),
        tasks=[],
        process=Process.hierarchical,
        manager_agent=agents["director"],
        verbose=True,
        memory=True
    ), agents