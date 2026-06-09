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
# AGENTIC CAPABILITY UPGRADES
# (MCP, slash commands, self-healing code, SOP generation, adaptive scraping,
#  AI-company orchestration). Implementations live in backend/integrations/ and
#  backend/agents/.
# =============================================================================

use_mcp_tool = {
    "name": "use_mcp_tool",
    "description": "Connect to an external MCP (Model Context Protocol) server and call one of its tools, or list available servers/tools. Use to reach research backends, adaptive scrapers, browser-use agents, and other MCP-compatible services.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "action": {
                "type": "STRING",
                "description": "One of: list_servers, list_tools, call_tool."
            },
            "server": {
                "type": "STRING",
                "description": "Name of the registered MCP server (required for list_tools/call_tool)."
            },
            "tool": {
                "type": "STRING",
                "description": "Tool name to invoke on the server (required for call_tool)."
            },
            "arguments": {
                "type": "STRING",
                "description": "JSON object of arguments for the tool call (for call_tool)."
            }
        },
        "required": ["action"]
    }
}

run_slash_command_tool = {
    "name": "run_slash_command",
    "description": "Run a Claude-Code-style slash command: /handoff, /loop, /code-review, /verify, /run, /init, /security-review, /help. Drives common dev workflows without re-typing prompts.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "command": {
                "type": "STRING",
                "description": "The full slash command string, e.g. '/code-review deep src/app.py'."
            }
        },
        "required": ["command"]
    }
}

self_healing_code_tool = {
    "name": "self_healing_code",
    "description": "Run a Python snippet in a self-healing loop: execute, read errors, auto-repair, and retry until it works or the retry budget is exhausted. For sandboxed/dev use.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "code": {
                "type": "STRING",
                "description": "The Python code to run and repair."
            },
            "max_iterations": {
                "type": "INTEGER",
                "description": "Maximum number of fix/retry attempts (default 5)."
            }
        },
        "required": ["code"]
    }
}

generate_sop_tool = {
    "name": "generate_sop",
    "description": "Turn a voice-note transcript or brain-dump into a structured Standard Operating Procedure: extracts steps, flags vague ones, and highlights automation opportunities.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "transcript": {
                "type": "STRING",
                "description": "The free-form description of the process to formalize."
            },
            "title": {
                "type": "STRING",
                "description": "Optional title for the procedure."
            }
        },
        "required": ["transcript"]
    }
}

scrape_web_tool = {
    "name": "scrape_web",
    "description": "Fetch a web page and extract its title, text, and links using a resilient, self-adjusting cascade (Scrapling -> BeautifulSoup -> stdlib) with retries. Robust to layout changes.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "url": {
                "type": "STRING",
                "description": "The http(s) URL to scrape."
            },
            "max_chars": {
                "type": "INTEGER",
                "description": "Maximum characters of extracted text to return (default 5000)."
            }
        },
        "required": ["url"]
    }
}

run_company_tool = {
    "name": "run_company",
    "description": "Run the 'AI company' orchestrator: decompose a high-level objective into role-scoped tasks (engineering, design, marketing, finance, ops, research), delegate each to the right department agent, and return a Kanban-style status report.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "objective": {
                "type": "STRING",
                "description": "The high-level goal for the AI company to execute."
            }
        },
        "required": ["objective"]
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
    # Agentic capability upgrades
    use_mcp_tool,
    run_slash_command_tool,
    self_healing_code_tool,
    generate_sop_tool,
    scrape_web_tool,
    run_company_tool,
    # Safety
    confirm_action_tool
]}]

# Notes for developers:
# - Tools marked with confirmation requirements should be gated in server.py or the calling agent.
# - The on-device sierra_router.py can short-circuit many of these for speed/privacy.
# - When adding new tools, update this list and ensure corresponding implementation exists in agents/ or backend/.
# - For multi-agent future: each agent can have its own specialized tools subset.
# - In God Mode, many confirmation gates are relaxed for non-destructive use.
