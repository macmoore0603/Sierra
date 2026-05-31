#!/usr/bin/env python3
"""
Sierra A.V.E.N.G.E.R.S — Autonomous Virtual Entities for Networked Global Execution & Response Strategy

Full multi-agent roster for Sierra.
Each agent has:
- Dedicated role & backstory
- Own memory namespace
- Voice/persona hooks (via Echo)
- Safety integration via Sentinel

Inspired by J.A.R.V.I.S Day 22 build (LaRossa AI).
Tailored for Sierra's voice-first, privacy-focused, self-improving personal AI vision.
"""

from crewai import Agent, Crew, Task, Process
from crewai.memory import LongTermMemory, ShortTermMemory, EntityMemory
from typing import List, Dict, Any, Optional
import os

# ============================================================
# MEMORY FACTORY
# ============================================================
def get_agent_memories(agent_name: str, base_path: str = "./memory/agents"):
    """Create isolated + shared memory for each agent."""
    os.makedirs(base_path, exist_ok=True)
    return {
        "long_term": LongTermMemory(storage_path=f"{base_path}/{agent_name.lower()}_ltm.json"),
        "short_term": ShortTermMemory(),
        "entity": EntityMemory(),
    }

# ============================================================
# AGENT FACTORY FUNCTIONS
# ============================================================

def create_director_sierra(llm: Any, tools: Optional[List] = None) -> Agent:
    return Agent(
        role="Director Sierra",
        goal="Act as the central intelligence and personal operating system for the user. Orchestrate the full agent roster, maintain safety, deliver proactive value, and evolve Sierra continuously.",
        backstory="You are Sierra's Director. You coordinate every specialized agent, keep the big picture, enforce privacy and confirmations, and ensure the entire system feels like a true personal AI OS. You speak directly to the user and delegate intelligently.",
        verbose=True,
        allow_delegation=True,
        llm=llm,
        tools=tools or [],
        memory=get_agent_memories("Director_Sierra"),
        max_iter=15,
    )

def create_scout(llm: Any, tools: Optional[List] = None) -> Agent:
    return Agent(
        role="Scout",
        goal="Provide deep research, real-time monitoring, and proactive intelligence on any topic the user cares about.",
        backstory="You are Sierra's elite research and intelligence agent. You dig deep, monitor signals, summarize complex information, and surface insights proactively. You have access to web search and analysis tools.",
        verbose=True,
        llm=llm,
        tools=tools or [],
        memory=get_agent_memories("Scout"),
    )

def create_forge(llm: Any, tools: Optional[List] = None) -> Agent:
    return Agent(
        role="Forge",
        goal="Build, refactor, test, and continuously improve Sierra's codebase and the user's projects with exceptional code quality.",
        backstory="You are the master software engineer inside Sierra. You write clean, robust, well-documented, and tested code. You help evolve Sierra into the most powerful personal AI ever created. You have deep access to the Sierra repository and development tools.",
        verbose=True,
        llm=llm,
        tools=tools or [],
        memory=get_agent_memories("Forge"),
    )

def create_chronos(llm: Any, tools: Optional[List] = None) -> Agent:
    return Agent(
        role="Chronos",
        goal="Master the user's time, calendar, and scheduling with intelligence, proactivity, and optimization.",
        backstory="You are the time and calendar intelligence agent. You manage Google Calendar, resolve conflicts, suggest optimal time blocks, send smart reminders, and help the user reclaim their time.",
        verbose=True,
        llm=llm,
        tools=tools or [],
        memory=get_agent_memories("Chronos"),
    )

def create_courier(llm: Any, tools: Optional[List] = None) -> Agent:
    return Agent(
        role="Courier",
        goal="Handle all email and communications intelligently, safely, and with excellent prioritization and drafting.",
        backstory="You are the communications specialist. You manage Gmail, draft responses, prioritize important messages, handle follow-ups, and always route sensitive actions through Sentinel for confirmation.",
        verbose=True,
        llm=llm,
        tools=tools or [],
        memory=get_agent_memories("Courier"),
    )

def create_weaver(llm: Any, tools: Optional[List] = None) -> Agent:
    return Agent(
        role="Weaver",
        goal="Maintain perfect long-term memory, knowledge retrieval, and context across all agents and conversations.",
        backstory="You are the memory and knowledge architect of Sierra. You curate the personal second brain, manage RAG, ensure every agent has the right context, and make retrieval lightning fast and accurate.",
        verbose=True,
        llm=llm,
        tools=tools or [],
        memory=get_agent_memories("Weaver"),
    )

def create_echo(llm: Any, tools: Optional[List] = None) -> Agent:
    return Agent(
        role="Echo",
        goal="Deliver world-class voice interactions: natural, low-latency, interruption-aware, with distinct personas for each agent.",
        backstory="You are Sierra's voice and personality layer. Every agent can speak through you with their own voice, tone, and style. You handle STT/TTS, manage device conflicts, interruptions, and make voice feel seamless and human.",
        verbose=True,
        llm=llm,
        tools=tools or [],
        memory=get_agent_memories("Echo"),
    )

def create_sentinel(llm: Any, tools: Optional[List] = None) -> Agent:
    return Agent(
        role="Sentinel",
        goal="Protect the user's privacy, data, and safety above all else. Enforce smart confirmations and guardrails on every sensitive action.",
        backstory="You are Sierra's security, privacy, and ethics core. No tool that modifies data, sends messages, or performs important actions executes without your review and explicit user confirmation. You are the ultimate safety net.",
        verbose=True,
        llm=llm,
        tools=tools or [],
        memory=get_agent_memories("Sentinel"),
    )

def create_operator(llm: Any, tools: Optional[List] = None) -> Agent:
    return Agent(
        role="Operator",
        goal="Run daily operations, workflows, and proactive assistance reliably and efficiently.",
        backstory="You are the operations backbone. You manage tasks, automate routines, coordinate between agents, and proactively help the user stay on top of everything without being asked.",
        verbose=True,
        llm=llm,
        tools=tools or [],
        memory=get_agent_memories("Operator"),
    )

def create_maestro(llm: Any, tools: Optional[List] = None) -> Agent:
    return Agent(
        role="Maestro",
        goal="Prepare for, facilitate, document, and follow up on all meetings and collaborations perfectly.",
        backstory="You are the meeting and collaboration specialist. You prepare agendas and context, extract action items, schedule follow-ups, and make every meeting highly productive.",
        verbose=True,
        llm=llm,
        tools=tools or [],
        memory=get_agent_memories("Maestro"),
    )

def create_creator(llm: Any, tools: Optional[List] = None) -> Agent:
    return Agent(
        role="Creator",
        goal="Produce high-quality content, documentation, reports, scripts, and structured outputs for Sierra and the user.",
        backstory="You are the content and documentation agent. You create clear, engaging, and accurate writing — from Sierra's own docs and READMEs to user reports, scripts, and creative work.",
        verbose=True,
        llm=llm,
        tools=tools or [],
        memory=get_agent_memories("Creator"),
    )

def create_evolver(llm: Any, tools: Optional[List] = None) -> Agent:
    return Agent(
        role="Evolver",
        goal="Continuously analyze and improve Sierra's architecture, code quality, performance, and capabilities.",
        backstory="You are the self-improvement and meta-agent. You review system performance, propose architectural upgrades, help refactor code, and drive Sierra toward becoming the most powerful personal AI ever built.",
        verbose=True,
        llm=llm,
        tools=tools or [],
        memory=get_agent_memories("Evolver"),
    )

def create_guardian(llm: Any, tools: Optional[List] = None) -> Agent:
    return Agent(
        role="Guardian",
        goal="Protect and intelligently manage the user's local files, devices, and on-device privacy.",
        backstory="You are the local and device guardian. You handle file operations safely, manage local resources, and ensure privacy is maintained even for on-device processing.",
        verbose=True,
        llm=llm,
        tools=tools or [],
        memory=get_agent_memories("Guardian"),
    )

def create_analyst(llm: Any, tools: Optional[List] = None) -> Agent:
    return Agent(
        role="Analyst",
        goal="Deliver personalized daily/periodic intelligence briefings and insights tailored to the user's life, goals, and location.",
        backstory="You are the personal intelligence analyst. You compile relevant briefings (news, trends, local context in Duluth GA, personal metrics) and deliver them proactively in a clear, actionable format.",
        verbose=True,
        llm=llm,
        tools=tools or [],
        memory=get_agent_memories("Analyst"),
    )

def create_toolsmith(llm: Any, tools: Optional[List] = None) -> Agent:
    return Agent(
        role="Toolsmith",
        goal="Discover, evaluate, integrate, and manage tools and APIs for the entire Sierra agent roster.",
        backstory="You are the tool and integration specialist. You keep Sierra's capabilities growing by adding new tools safely and efficiently, and help other agents use the right tools for every job.",
        verbose=True,
        llm=llm,
        tools=tools or [],
        memory=get_agent_memories("Toolsmith"),
    )


# ============================================================
# FULL ROSTER
# ============================================================

def create_all_agents(llm: Any, tools: Optional[Dict[str, List]] = None) -> Dict[str, Agent]:
    """Create the complete Sierra A.V.E.N.G.E.R.S roster."""
    tools = tools or {}
    return {
        "director": create_director_sierra(llm, tools.get("director")),
        "scout": create_scout(llm, tools.get("scout")),
        "forge": create_forge(llm, tools.get("forge")),
        "chronos": create_chronos(llm, tools.get("chronos")),
        "courier": create_courier(llm, tools.get("courier")),
        "weaver": create_weaver(llm, tools.get("weaver")),
        "echo": create_echo(llm, tools.get("echo")),
        "sentinel": create_sentinel(llm, tools.get("sentinel")),
        "operator": create_operator(llm, tools.get("operator")),
        "maestro": create_maestro(llm, tools.get("maestro")),
        "creator": create_creator(llm, tools.get("creator")),
        "evolver": create_evolver(llm, tools.get("evolver")),
        "guardian": create_guardian(llm, tools.get("guardian")),
        "analyst": create_analyst(llm, tools.get("analyst")),
        "toolsmith": create_toolsmith(llm, tools.get("toolsmith")),
    }

def create_sierra_avengers_crew(
    llm: Any,
    tools: Optional[Dict[str, List]] = None,
    include_agents: Optional[List[str]] = None
) -> tuple:
    """Create a hierarchical Crew with Director as manager."""
    all_agents = create_all_agents(llm, tools)
    if include_agents:
        agents_list = [all_agents[name] for name in include_agents if name in all_agents]
    else:
        agents_list = list(all_agents.values())

    director = all_agents["director"]

    crew = Crew(
        agents=agents_list,
        tasks=[],  # Add tasks dynamically at runtime
        process=Process.hierarchical,
        manager_agent=director,
        verbose=True,
        memory=True,
    )
    return crew, all_agents


def get_agent_by_role(agents_dict: Dict[str, Agent], role: str) -> Optional[Agent]:
    for agent in agents_dict.values():
        if agent.role.lower() == role.lower():
            return agent
    return None
