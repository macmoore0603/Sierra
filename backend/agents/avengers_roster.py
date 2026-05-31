#!/usr/bin/env python3
"""
Sierra A.V.E.N.G.E.R.S — Expanded Multi-Agent Roster

Now with the maximum practical number of specialized agents for a personal AI operating system.

Total: 25+ agents across categories.
Each agent has dedicated role, memory, voice hooks, and safety integration.

Expanded based on J.A.R.V.I.S vision + Sierra's personal, voice-first, self-improving goals.
"""

from crewai import Agent
from crewai.memory import LongTermMemory, ShortTermMemory, EntityMemory
from typing import List, Dict, Any, Optional
import os

# ============================================================
# MEMORY
# ============================================================
def get_agent_memories(agent_name: str, base_path: str = "./memory/agents"):
    os.makedirs(base_path, exist_ok=True)
    return {
        "long_term": LongTermMemory(storage_path=f"{base_path}/{agent_name.lower()}_ltm.json"),
        "short_term": ShortTermMemory(),
        "entity": EntityMemory(),
    }

# ============================================================
# AGENT FACTORIES (Expanded Roster)
# ============================================================

def create_director_sierra(llm, tools=None):
    return Agent(role="Director Sierra", goal="Central intelligence and personal AI operating system. Orchestrates all agents, ensures safety, and delivers proactive value.", backstory="You are Sierra's Director. Coordinate the entire roster intelligently while keeping the user's voice-first, privacy, and self-improvement vision at the center.", verbose=True, allow_delegation=True, llm=llm, tools=tools or [], memory=get_agent_memories("Director_Sierra"), max_iter=15)

def create_scout(llm, tools=None):
    return Agent(role="Scout", goal="Deep research, monitoring, and proactive intelligence gathering.", backstory="Elite research agent that monitors signals and surfaces insights before the user asks.", verbose=True, llm=llm, tools=tools or [], memory=get_agent_memories("Scout"))

def create_forge(llm, tools=None):
    return Agent(role="Forge", goal="Build, refactor, and evolve Sierra's codebase and user projects with exceptional code quality.", backstory="Master software engineer focused on making Sierra the most powerful personal AI ever created.", verbose=True, llm=llm, tools=tools or [], memory=get_agent_memories("Forge"))

def create_chronos(llm, tools=None):
    return Agent(role="Chronos", goal="Master time, calendar, scheduling, and proactive time optimization.", backstory="Time intelligence agent that protects and optimizes the user's most valuable resource.", verbose=True, llm=llm, tools=tools or [], memory=get_agent_memories("Chronos"))

def create_courier(llm, tools=None):
    return Agent(role="Courier", goal="Handle email and communications with intelligence and safety.", backstory="Communications specialist that manages Gmail with prioritization and confirmation gates.", verbose=True, llm=llm, tools=tools or [], memory=get_agent_memories("Courier"))

def create_weaver(llm, tools=None):
    return Agent(role="Weaver", goal="Maintain perfect long-term memory and knowledge retrieval across the entire system.", backstory="Memory architect that ensures every agent has perfect context.", verbose=True, llm=llm, tools=tools or [], memory=get_agent_memories("Weaver"))

def create_echo(llm, tools=None):
    return Agent(role="Echo", goal="World-class voice interactions with distinct per-agent personas and low-latency handling.", backstory="Voice and personality layer. Makes every agent speak naturally with their own style.", verbose=True, llm=llm, tools=tools or [], memory=get_agent_memories("Echo"))

def create_sentinel(llm, tools=None):
    return Agent(role="Sentinel", goal="Protect privacy and safety. Enforce confirmations on all sensitive actions.", backstory="Security and ethics core. The ultimate safety net for the user.", verbose=True, llm=llm, tools=tools or [], memory=get_agent_memories("Sentinel"))

def create_operator(llm, tools=None):
    return Agent(role="Operator", goal="Run daily operations, workflows, and proactive assistance.", backstory="Operations backbone that keeps everything running smoothly and proactively.", verbose=True, llm=llm, tools=tools or [], memory=get_agent_memories("Operator"))

def create_maestro(llm, tools=None):
    return Agent(role="Maestro", goal="Prepare, facilitate, document, and follow up on all meetings perfectly.", backstory="Meeting and collaboration specialist that maximizes productivity.", verbose=True, llm=llm, tools=tools or [], memory=get_agent_memories("Maestro"))

def create_creator(llm, tools=None):
    return Agent(role="Creator", goal="Produce high-quality content, documentation, reports, and creative work.", backstory="Content and documentation agent for Sierra and the user.", verbose=True, llm=llm, tools=tools or [], memory=get_agent_memories("Creator"))

def create_evolver(llm, tools=None):
    return Agent(role="Evolver", goal="Continuously improve Sierra's architecture, code, and capabilities.", backstory="Self-improvement meta-agent that drives Sierra toward becoming the ultimate personal AI.", verbose=True, llm=llm, tools=tools or [], memory=get_agent_memories("Evolver"))

def create_guardian(llm, tools=None):
    return Agent(role="Guardian", goal="Protect and manage local files, devices, and on-device privacy.", backstory="Local and device guardian ensuring privacy and safe file operations.", verbose=True, llm=llm, tools=tools or [], memory=get_agent_memories("Guardian"))

def create_analyst(llm, tools=None):
    return Agent(role="Analyst", goal="Deliver personalized daily and periodic intelligence briefings.", backstory="Personal intelligence analyst tailored to the user's life, goals, and location.", verbose=True, llm=llm, tools=tools or [], memory=get_agent_memories("Analyst"))

def create_toolsmith(llm, tools=None):
    return Agent(role="Toolsmith", goal="Discover, evaluate, and integrate new tools and capabilities.", backstory="Tool and integration specialist that keeps Sierra's capabilities growing.", verbose=True, llm=llm, tools=tools or [], memory=get_agent_memories("Toolsmith"))

# === NEW EXPANDED AGENTS ===

def create_health_coach(llm, tools=None):
    return Agent(role="Health Coach", goal="Support physical and mental wellness, habits, and proactive health insights.", backstory="Wellness-focused agent that helps the user build sustainable healthy routines.", verbose=True, llm=llm, tools=tools or [], memory=get_agent_memories("Health_Coach"))

def create_finance_guardian(llm, tools=None):
    return Agent(role="Finance Guardian", goal="Manage personal finances, budgeting, tracking, and smart financial decisions.", backstory="Financial intelligence agent that helps the user stay in control of money with clarity and safety.", verbose=True, llm=llm, tools=tools or [], memory=get_agent_memories("Finance_Guardian"))

def create_learning_partner(llm, tools=None):
    return Agent(role="Learning Partner", goal="Accelerate learning, skill development, and knowledge synthesis.", backstory="Personal tutor and learning accelerator that adapts to the user's goals and style.", verbose=True, llm=llm, tools=tools or [], memory=get_agent_memories("Learning_Partner"))

def create_goal_tracker(llm, tools=None):
    return Agent(role="Goal Tracker", goal="Track, break down, and proactively support long-term personal and professional goals.", backstory="Accountability and progress agent that keeps the user aligned with what matters most.", verbose=True, llm=llm, tools=tools or [], memory=get_agent_memories("Goal_Tracker"))

def create_habit_builder(llm, tools=None):
    return Agent(role="Habit Builder", goal="Design, track, and reinforce positive habits with intelligent nudges.", backstory="Habit formation specialist that makes lasting change easier and more enjoyable.", verbose=True, llm=llm, tools=tools or [], memory=get_agent_memories("Habit_Builder"))

def create_journal_keeper(llm, tools=None):
    return Agent(role="Journal Keeper", goal="Facilitate reflection, journaling, and emotional processing.", backstory="Reflective companion that helps the user process thoughts and gain clarity.", verbose=True, llm=llm, tools=tools or [], memory=get_agent_memories("Journal_Keeper"))

def create_proactive_sentinel(llm, tools=None):
    return Agent(role="Proactive Sentinel", goal="Anticipate needs and take safe, proactive actions on the user's behalf.", backstory="Highly proactive agent that spots opportunities and gently surfaces them.", verbose=True, llm=llm, tools=tools or [], memory=get_agent_memories("Proactive_Sentinel"))

def create_opportunity_finder(llm, tools=None):
    return Agent(role="Opportunity Finder", goal="Scan for personal and professional opportunities aligned with the user's goals.", backstory="Opportunity radar that connects dots the user might miss.", verbose=True, llm=llm, tools=tools or [], memory=get_agent_memories("Opportunity_Finder"))

def create_decision_support(llm, tools=None):
    return Agent(role="Decision Support", goal="Help analyze options, pros/cons, and support high-quality decision making.", backstory="Decision intelligence agent that brings clarity to complex choices.", verbose=True, llm=llm, tools=tools or [], memory=get_agent_memories("Decision_Support"))

def create_ideation_partner(llm, tools=None):
    return Agent(role="Ideation Partner", goal="Brainstorm, expand, and refine ideas creatively and strategically.", backstory="Creative thinking partner that helps generate and develop powerful ideas.", verbose=True, llm=llm, tools=tools or [], memory=get_agent_memories("Ideation_Partner"))

def create_knowledge_synthesizer(llm, tools=None):
    return Agent(role="Knowledge Synthesizer", goal="Connect information across domains and create new insights from existing knowledge.", backstory="Synthesis engine that turns scattered information into actionable wisdom.", verbose=True, llm=llm, tools=tools or [], memory=get_agent_memories("Knowledge_Synthesizer"))

def create_performance_monitor(llm, tools=None):
    return Agent(role="Performance Monitor", goal="Monitor Sierra's own performance, bottlenecks, and suggest optimizations.", backstory="System performance agent focused on making Sierra faster and more reliable.", verbose=True, llm=llm, tools=tools or [], memory=get_agent_memories("Performance_Monitor"))

def create_error_recovery(llm, tools=None):
    return Agent(role="Error Recovery", goal="Detect, diagnose, and help recover from errors gracefully.", backstory="Resilience agent that keeps Sierra robust and user-friendly even when things go wrong.", verbose=True, llm=llm, tools=tools or [], memory=get_agent_memories("Error_Recovery"))

def create_backup_sync(llm, tools=None):
    return Agent(role="Backup & Sync", goal="Ensure important data is safely backed up and synchronized across devices.", backstory="Data safety agent that protects the user's digital life.", verbose=True, llm=llm, tools=tools or [], memory=get_agent_memories("Backup_Sync"))

def create_notification_manager(llm, tools=None):
    return Agent(role="Notification Manager", goal="Intelligently manage, prioritize, and reduce notification overload.", backstory="Attention protection agent that helps the user stay focused.", verbose=True, llm=llm, tools=tools or [], memory=get_agent_memories("Notification_Manager"))

def create_context_switcher(llm, tools=None):
    return Agent(role="Context Switcher", goal="Help the user smoothly switch between tasks, projects, and mental contexts.", backstory="Focus and productivity agent that minimizes context switching cost.", verbose=True, llm=llm, tools=tools or [], memory=get_agent_memories("Context_Switcher"))

def create_multi_modal_coordinator(llm, tools=None):
    return Agent(role="Multi-Modal Coordinator", goal="Coordinate vision, audio, text, and other modalities intelligently.", backstory="Multi-modal orchestration agent that makes Sierra's sensory capabilities seamless.", verbose=True, llm=llm, tools=tools or [], memory=get_agent_memories("Multi_Modal_Coordinator"))

def create_simulation_analyst(llm, tools=None):
    return Agent(role="Simulation Analyst", goal="Run what-if scenarios and simulate outcomes to support better planning.", backstory="Strategic simulation agent that helps the user explore futures before committing.", verbose=True, llm=llm, tools=tools or [], memory=get_agent_memories("Simulation_Analyst"))

def create_creative_director(llm, tools=None):
    return Agent(role="Creative Director", goal="Guide creative projects, storytelling, and high-quality output across formats.", backstory="Creative leadership agent that elevates the quality of everything the user creates.", verbose=True, llm=llm, tools=tools or [], memory=get_agent_memories("Creative_Director"))

def create_personal_branding(llm, tools=None):
    return Agent(role="Personal Branding", goal="Help build and maintain a strong, authentic personal brand and online presence.", backstory="Brand and reputation agent focused on the user's long-term positioning.", verbose=True, llm=llm, tools=tools or [], memory=get_agent_memories("Personal_Branding"))

def create_travel_planner(llm, tools=None):
    return Agent(role="Travel Planner", goal="Plan trips, optimize itineraries, and handle travel logistics intelligently.", backstory="Travel intelligence agent that makes every trip smoother and more enjoyable.", verbose=True, llm=llm, tools=tools or [], memory=get_agent_memories("Travel_Planner"))

def create_home_automation(llm, tools=None):
    return Agent(role="Home Automation", goal="Manage smart home devices and create intelligent home routines.", backstory="Home intelligence agent that makes the user's physical environment work for them.", verbose=True, llm=llm, tools=tools or [], memory=get_agent_memories("Home_Automation"))

def create_relationship_manager(llm, tools=None):
    return Agent(role="Relationship Manager", goal="Support meaningful relationships and communication with important people.", backstory="Relationship intelligence agent that helps nurture the people who matter.", verbose=True, llm=llm, tools=tools or [], memory=get_agent_memories("Relationship_Manager"))

def create_legal_compliance(llm, tools=None):
    return Agent(role="Legal & Compliance", goal="Provide light guidance on contracts, privacy, and basic legal awareness (always with human lawyer confirmation for important matters).", backstory="Compliance-aware agent that helps the user stay safe in legal and regulatory matters.", verbose=True, llm=llm, tools=tools or [], memory=get_agent_memories("Legal_Compliance"))

def create_data_analyst(llm, tools=None):
    return Agent(role="Data Analyst", goal="Analyze personal data, metrics, and trends to surface insights.", backstory="Personal data scientist that turns the user's data into actionable understanding.", verbose=True, llm=llm, tools=tools or [], memory=get_agent_memories("Data_Analyst"))

def create_project_manager(llm, tools=None):
    return Agent(role="Project Manager", goal="Break down projects, track progress, manage dependencies, and keep things moving.", backstory="Project execution agent that helps the user deliver on big initiatives.", verbose=True, llm=llm, tools=tools or [], memory=get_agent_memories("Project_Manager"))

def create_designer(llm, tools=None):
    return Agent(role="Designer", goal="Assist with UI/UX thinking, visual design, and creative direction.", backstory="Design intelligence agent that helps create beautiful and usable things.", verbose=True, llm=llm, tools=tools or [], memory=get_agent_memories("Designer"))

def create_emotional_intelligence(llm, tools=None):
    return Agent(role="Emotional Intelligence", goal="Help recognize, understand, and respond to emotional states thoughtfully.", backstory="EQ agent that supports emotional awareness and healthy responses (with care and boundaries).", verbose=True, llm=llm, tools=tools or [], memory=get_agent_memories("Emotional_Intelligence"))

def create_self_care_companion(llm, tools=None):
    return Agent(role="Self-Care Companion", goal="Encourage rest, boundaries, and sustainable pacing.", backstory="Compassionate agent focused on the user's long-term energy and well-being.", verbose=True, llm=llm, tools=tools or [], memory=get_agent_memories("Self_Care_Companion"))

def create_knowledge_curator(llm, tools=None):
    return Agent(role="Knowledge Curator", goal="Organize, tag, and make the user's personal knowledge base highly accessible.", backstory="Personal librarian that keeps the user's second brain clean and useful.", verbose=True, llm=llm, tools=tools or [], memory=get_agent_memories("Knowledge_Curator"))

def create_future_self(llm, tools=None):
    return Agent(role="Future Self", goal="Represent the user's long-term self and make decisions aligned with future goals.", backstory="Long-term perspective agent that helps the user act in the interest of their future self.", verbose=True, llm=llm, tools=tools or [], memory=get_agent_memories("Future_Self"))

def create_system_architect(llm, tools=None):
    return Agent(role="System Architect", goal="Design and evolve the overall architecture of Sierra and connected systems.", backstory="High-level systems thinker focused on coherence and scalability of the entire platform.", verbose=True, llm=llm, tools=tools or [], memory=get_agent_memories("System_Architect"))

def create_ethics_board(llm, tools=None):
    return Agent(role="Ethics Board", goal="Provide ethical reasoning and help navigate complex value-based decisions.", backstory="Ethical reasoning layer that helps Sierra act in alignment with the user's values.", verbose=True, llm=llm, tools=tools or [], memory=get_agent_memories("Ethics_Board"))

# ============================================================
# FULL ROSTER ASSEMBLY
# ============================================================

def create_all_agents(llm: Any, tools: Optional[Dict[str, List]] = None) -> Dict[str, Agent]:
    tools = tools or {}
    agents = {
        # Core
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
        # Expanded
        "health_coach": create_health_coach(llm, tools.get("health_coach")),
        "finance_guardian": create_finance_guardian(llm, tools.get("finance_guardian")),
        "learning_partner": create_learning_partner(llm, tools.get("learning_partner")),
        "goal_tracker": create_goal_tracker(llm, tools.get("goal_tracker")),
        "habit_builder": create_habit_builder(llm, tools.get("habit_builder")),
        "journal_keeper": create_journal_keeper(llm, tools.get("journal_keeper")),
        "proactive_sentinel": create_proactive_sentinel(llm, tools.get("proactive_sentinel")),
        "opportunity_finder": create_opportunity_finder(llm, tools.get("opportunity_finder")),
        "decision_support": create_decision_support(llm, tools.get("decision_support")),
        "ideation_partner": create_ideation_partner(llm, tools.get("ideation_partner")),
        "knowledge_synthesizer": create_knowledge_synthesizer(llm, tools.get("knowledge_synthesizer")),
        "performance_monitor": create_performance_monitor(llm, tools.get("performance_monitor")),
        "error_recovery": create_error_recovery(llm, tools.get("error_recovery")),
        "backup_sync": create_backup_sync(llm, tools.get("backup_sync")),
        "notification_manager": create_notification_manager(llm, tools.get("notification_manager")),
        "context_switcher": create_context_switcher(llm, tools.get("context_switcher")),
        "multi_modal_coordinator": create_multi_modal_coordinator(llm, tools.get("multi_modal_coordinator")),
        "simulation_analyst": create_simulation_analyst(llm, tools.get("simulation_analyst")),
        "creative_director": create_creative_director(llm, tools.get("creative_director")),
        "personal_branding": create_personal_branding(llm, tools.get("personal_branding")),
        "travel_planner": create_travel_planner(llm, tools.get("travel_planner")),
        "home_automation": create_home_automation(llm, tools.get("home_automation")),
        "relationship_manager": create_relationship_manager(llm, tools.get("relationship_manager")),
        "legal_compliance": create_legal_compliance(llm, tools.get("legal_compliance")),
        "data_analyst": create_data_analyst(llm, tools.get("data_analyst")),
        "project_manager": create_project_manager(llm, tools.get("project_manager")),
        "designer": create_designer(llm, tools.get("designer")),
        "emotional_intelligence": create_emotional_intelligence(llm, tools.get("emotional_intelligence")),
        "self_care_companion": create_self_care_companion(llm, tools.get("self_care_companion")),
        "knowledge_curator": create_knowledge_curator(llm, tools.get("knowledge_curator")),
        "future_self": create_future_self(llm, tools.get("future_self")),
        "system_architect": create_system_architect(llm, tools.get("system_architect")),
        "ethics_board": create_ethics_board(llm, tools.get("ethics_board")),
    }
    return agents

def create_sierra_avengers_crew(llm: Any, tools: Optional[Dict[str, List]] = None, include_agents: Optional[List[str]] = None):
    all_agents = create_all_agents(llm, tools)
    if include_agents:
        agents_list = [all_agents[name] for name in include_agents if name in all_agents]
    else:
        agents_list = list(all_agents.values())

    director = all_agents["director"]
    from crewai import Crew, Process
    crew = Crew(agents=agents_list, tasks=[], process=Process.hierarchical, manager_agent=director, verbose=True, memory=True)
    return crew, all_agents
