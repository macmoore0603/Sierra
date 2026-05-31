"""
Sierra Tools Definitions

This module defines the tools available to Sierra's AI (Gemini function calling + on-device router).

Design principles:
- Clear categorization for maintainability and future multi-agent orchestration.
- Strong emphasis on safety: many tools should require user confirmation (see settings.json tool_permissions).
- Ready for expansion into personal ecosystem integrations (Calendar, Gmail, GitHub, local files, memory/RAG).
- Compatible with the on-device FunctionGemma router for fast-path intents.

GOD MODE NOTE (Pervasive Full Access):
In God Mode (the default and intended experience), safety/confirmation requirements
are significantly relaxed for non-destructive high-privilege actions.
The UI layer is expected to never show "off" or restricted states for any core
capability (voice wake, gestures, face auth, background processes, personal integrations, etc.).
See GOD_MODE.md for the full philosophy of auto-activation and "no off states".

Future direction:
- Integrate with LangGraph / CrewAI for multi-agent workflows.
- Add RAG/memory tools backed by ChromaDB + sentence-transformers.
- Proactive tools that can suggest actions based on context.
"""

# =============================================================================
# CORE FILE & SYSTEM TOOLS
# =============================================================================

read_file_tool = {
    "name": "read_file",
    "description": "Reads the content of a file at the specified path. Use for inspecting code, notes, or project files.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "path": {
                "type": "STRING",
                "description": "The path of the file to read."
            }
        },
        "required": ["path"]
    }
}

read_directory_tool = {
    "name": "read_directory",
    "description": "Lists the contents of a directory. Useful for exploring project structure or finding files.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "path": {
                "type": "STRING",
                "description": "The path of the directory to list."
            }
        },
        "required": ["path"]
    }
}

write_file_tool = {
    "name": "write_file",
    "description": "Writes content to a file at the specified path. Overwrites if the file exists. **Requires user confirmation** for safety (see tool_permissions.write_file).",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "path": {
                "type": "STRING",
                "description": "The path of the file to write to."
            },
            "content": {
                "type": "STRING",
                "description": "The content to write to the file."
            }
        },
        "required": ["path", "content"]
    }
}

# =============================================================================
# CAD & CREATIVE TOOLS
# =============================================================================

generate_cad_prototype_tool = {
    "name": "generate_cad_prototype",
    "description": "Generates a 3D parametric model / STL prototype based on a user's description. Supports iteration ('make it thinner', 'add holes', etc.). Use for visualization, prototyping, or 3D design tasks. Output saved to projects/ folder.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "prompt": {
                "type": "STRING",
                "description": "The user's description of the object to create or modify."
            }
        },
        "required": ["prompt"]
    }
}

# =============================================================================
# SMART HOME & IOT
# =============================================================================

control_smart_home_tool = {
    "name": "control_smart_home",
    "description": "Control TP-Link Kasa smart home devices (lights, plugs, etc.). Supports on/off, color, brightness. Voice-friendly.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "action": {
                "type": "STRING",
                "description": "Action to perform: on, off, toggle, set_color, set_brightness."
            },
            "device_name": {
                "type": "STRING",
                "description": "Name or type of the device (e.g., 'kitchen light', 'living room plug')."
            },
            "value": {
                "type": "STRING",
                "description": "Optional value for color (hex) or brightness (0-100)."
            }
        },
        "required": ["action", "device_name"]
    }
}

# =============================================================================
# WEB & INFORMATION TOOLS
# =============================================================================

web_search_tool = {
    "name": "web_search",
    "description": "Perform a web search and return relevant results. Useful for research, current events, or fact-checking.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "query": {
                "type": "STRING",
                "description": "The search query."
            }
        },
        "required": ["query"]
    }
}

# Placeholder for full web agent (Playwright) - handled in web_agent.py but exposable here
open_browser_tool = {
    "name": "open_browser_and_act",
    "description": "Opens a browser and performs autonomous actions (navigate, click, type, scroll). **Requires user confirmation** for safety. Use for shopping, research, or form filling.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "task": {
                "type": "STRING",
                "description": "Natural language description of the browsing task to perform."
            }
        },
        "required": ["task"]
    }
}

# =============================================================================
# PERSONAL ECOSYSTEM INTEGRATIONS (Future / In Progress)
# These will enable deep, safe access to your personal data and services.
# All sensitive actions should go through confirmation flows.
# In God Mode these flows are minimized for non-destructive actions.
# =============================================================================

get_calendar_events_tool = {
    "name": "get_calendar_events",
    "description": "Retrieve upcoming events from Google Calendar. Supports natural language time ranges ('today', 'this week'). Proactive reminder potential.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "time_range": {
                "type": "STRING",
                "description": "Time range to query (e.g., 'today', 'tomorrow', 'this week')."
            }
        },
        "required": ["time_range"]
    }
}

send_email_tool = {
    "name": "send_email",
    "description": "Draft or send an email via Gmail. **High safety requirement** - always confirm with user before sending (relaxed in God Mode for non-destructive use).",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "to": {
                "type": "STRING",
                "description": "Recipient email address."
            },
            "subject": {
                "type": "STRING",
                "description": "Email subject line."
            },
            "body": {
                "type": "STRING",
                "description": "Email body content."
            }
        },
        "required": ["to", "subject", "body"]
    }
}

github_repo_tool = {
    "name": "github_action",
    "description": "Interact with GitHub repositories (list repos, create issues, read PRs, etc.). Useful for project management and code assistance.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "action": {
                "type": "STRING",
                "description": "Action to perform (e.g., list_repos, create_issue, get_prs)."
            },
            "repo": {
                "type": "STRING",
                "description": "Optional repository name (owner/repo or just repo if unambiguous)."
            },
            "details": {
                "type": "STRING",
                "description": "Additional details for the action (e.g., issue title/body)."
            }
        },
        "required": ["action"]
    }
}

# =============================================================================
# MEMORY, CONTEXT & SELF-IMPROVEMENT (Future)
# Backed by ChromaDB + sentence-transformers for RAG and persistent memory.
# =============================================================================

query_memory_tool = {
    "name": "query_memory",
    "description": "Search Sierra's long-term memory / project context using semantic search. Enables continuity across sessions and self-improvement.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "query": {
                "type": "STRING",
                "description": "Natural language query about past projects, preferences, or context."
            }
        },
        "required": ["query"]
    }
}

update_memory_tool = {
    "name": "update_memory",
    "description": "Store new information into Sierra's persistent memory. Supports building user model and proactive behavior.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "key": {
                "type": "STRING",
                "description": "Category or key for the memory (e.g., 'user_preferences', 'current_project')."
            },
            "value": {
                "type": "STRING",
                "description": "The information to remember."
            }
        },
        "required": ["key", "value"]
    }
}

# =============================================================================
# SAFETY & UTILITY
# =============================================================================

confirm_action_tool = {
    "name": "confirm_action",
    "description": "Explicitly request user confirmation before executing a sensitive action. Used internally for safety gates (relaxed in God Mode for non-destructive actions).",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "action_description": {
                "type": "STRING",
                "description": "Clear description of what will happen if confirmed."
            }
        },
        "required": ["action_description"]
    }
}

# =============================================================================
# MASTER TOOLS LIST (for Gemini / router)
# =============================================================================

tools_list = [{"function_declarations": [
    # Core
    read_file_tool,
    read_directory_tool,
    write_file_tool,
    # CAD
    generate_cad_prototype_tool,
    # Smart Home
    control_smart_home_tool,
    # Web
    web_search_tool,
    open_browser_tool,
    # Personal Integrations (future-ready)
    get_calendar_events_tool,
    send_email_tool,
    github_repo_tool,
    # Memory & Self-Improvement
    query_memory_tool,
    update_memory_tool,
    # Safety
    confirm_action_tool
]}]

# Notes for developers:
# - Tools marked with confirmation requirements should be gated in server.py or the calling agent.
# - The on-device sierra_router.py can short-circuit many of these for speed/privacy.
# - When adding new tools, update this list and ensure corresponding implementation exists in agents/ or backend/.
# - For multi-agent future: each agent can have its own specialized tools subset.
# - In God Mode, many confirmation gates are relaxed for non-destructive use.
