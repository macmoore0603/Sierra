"""
Central tool registry for Sierra.

All Gemini function declarations live here so that sierra.py, the router,
and tests share a single source of truth.
"""

generate_cad_prototype_tool = {
    "name": "generate_cad_prototype",
    "description": "Generates a 3D wireframe prototype based on a user's description. Use this when the user asks to 'visualize', 'prototype', 'create a wireframe', or 'design' something in 3D.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "prompt": {
                "type": "STRING",
                "description": "The user's description of the object to prototype."
            }
        },
        "required": ["prompt"]
    }
}

iterate_cad_tool = {
    "name": "iterate_cad",
    "description": "Modifies or iterates on the current CAD design based on user feedback. Use this when the user asks to adjust, resize, or change a previously generated 3D model.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "prompt": {
                "type": "STRING",
                "description": "The user's description of the changes to make."
            }
        },
        "required": ["prompt"]
    }
}

run_web_agent_tool = {
    "name": "run_web_agent",
    "description": "Opens a web browser and performs a task according to the prompt.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "prompt": {
                "type": "STRING",
                "description": "The detailed instructions for the web browser agent."
            }
        },
        "required": ["prompt"]
    }
}

create_project_tool = {
    "name": "create_project",
    "description": "Creates a new project folder to organize files.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "name": {
                "type": "STRING",
                "description": "The name of the new project."
            }
        },
        "required": ["name"]
    }
}

switch_project_tool = {
    "name": "switch_project",
    "description": "Switches the current active project context.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "name": {
                "type": "STRING",
                "description": "The name of the project to switch to."
            }
        },
        "required": ["name"]
    }
}

list_projects_tool = {
    "name": "list_projects",
    "description": "Lists all available projects.",
    "parameters": {
        "type": "OBJECT",
        "properties": {},
    }
}

list_smart_devices_tool = {
    "name": "list_smart_devices",
    "description": "Lists all available smart home devices (lights, plugs, etc.) on the network.",
    "parameters": {
        "type": "OBJECT",
        "properties": {},
    }
}

control_light_tool = {
    "name": "control_light",
    "description": "Controls a smart light device.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "target": {
                "type": "STRING",
                "description": "The IP address of the device to control."
            },
            "action": {
                "type": "STRING",
                "description": "The action to perform: 'turn_on', 'turn_off', or 'set'."
            },
            "brightness": {
                "type": "INTEGER",
                "description": "Optional brightness level (0-100)."
            },
            "color": {
                "type": "STRING",
                "description": "Optional color name (e.g., 'red', 'cool white') or 'warm'."
            }
        },
        "required": ["target", "action"]
    }
}

discover_printers_tool = {
    "name": "discover_printers",
    "description": "Discovers 3D printers available on the local network.",
    "parameters": {
        "type": "OBJECT",
        "properties": {},
    }
}

print_stl_tool = {
    "name": "print_stl",
    "description": "Prints an STL file to a 3D printer. Handles slicing the STL to G-code and uploading to the printer.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "stl_path": {
                "type": "STRING",
                "description": "Path to STL file, or 'current' for the most recent CAD model."
            },
            "printer": {
                "type": "STRING",
                "description": "Printer name or IP address."
            },
            "profile": {
                "type": "STRING",
                "description": "Optional slicer profile name."
            }
        },
        "required": ["stl_path", "printer"]
    }
}

get_print_status_tool = {
    "name": "get_print_status",
    "description": "Gets the current status of a 3D printer including progress, time remaining, and temperatures.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "printer": {
                "type": "STRING",
                "description": "Printer name or IP address."
            }
        },
        "required": ["printer"]
    }
}

write_file_tool = {
    "name": "write_file",
    "description": "Writes content to a file at the specified path. Overwrites if exists.",
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

read_directory_tool = {
    "name": "read_directory",
    "description": "Lists the contents of a directory.",
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

read_file_tool = {
    "name": "read_file",
    "description": "Reads the content of a file.",
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

# All tool declarations passed to Gemini's function-calling config.
tools_list = [{"function_declarations": [
    generate_cad_prototype_tool,
    iterate_cad_tool,
    run_web_agent_tool,
    create_project_tool,
    switch_project_tool,
    list_projects_tool,
    list_smart_devices_tool,
    control_light_tool,
    discover_printers_tool,
    print_stl_tool,
    get_print_status_tool,
    write_file_tool,
    read_directory_tool,
    read_file_tool,
]}]


