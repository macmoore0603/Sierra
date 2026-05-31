# Sierra API Documentation

## Overview

This document describes the main APIs for extending and interacting with Sierra programmatically.

## Table of Contents
- [Core Sierra Class](#core-sierra-class)
- [Agent Interface](#agent-interface)
- [Integration Interface](#integration-interface)
- [Memory & Context API](#memory--context-api)
- [Tools API](#tools-api)
- [Orchestrator API](#orchestrator-api)

## Core Sierra Class

The main entry point for Sierra functionality.

### Initialization

```python
from backend.sierra import Sierra

# Initialize Sierra
sierra = Sierra(
    config={
        'gemini_api_key': 'your-key',
        'voice_enabled': True,
        'god_mode': True,
    }
)

# Start the system
await sierra.initialize()
```

### Methods

#### `async def execute_command(command: str, context: dict = None)`

Execute a command through Sierra's orchestrator.

```python
result = await sierra.execute_command(
    "Check my calendar for tomorrow",
    context={
        'user_id': 'user123',
        'session_id': 'session456'
    }
)
print(result.output)  # Command result
```

**Returns**: `CommandResult` with `output`, `status`, and metadata

#### `async def add_memory(content: str, metadata: dict = None)`

Add information to Sierra's memory.

```python
await sierra.add_memory(
    content="User prefers morning meetings",
    metadata={
        'category': 'preference',
        'source': 'user_statement'
    }
)
```

#### `async def recall_context(query: str, limit: int = 5)`

Retrieve relevant context from memory.

```python
context = await sierra.recall_context(
    query="user preferences",
    limit=10
)
for item in context:
    print(item.content, item.relevance_score)
```

#### `def register_agent(agent_id: str, agent: BaseAgent)`

Register a new agent at runtime.

```python
from backend.agents.base import BaseAgent

class CustomAgent(BaseAgent):
    async def execute(self, task, context=None):
        return f"Executed: {task}"

sierra.register_agent('custom', CustomAgent())
```

#### `def register_integration(integration_id: str, integration: BaseIntegration)`

Register a new integration at runtime.

```python
sierra.register_integration('my_service', YourServiceIntegration(config))
```

## Agent Interface

### BaseAgent Class

```python
from backend.agents.base import BaseAgent

class MyAgent(BaseAgent):
    def __init__(self, config=None):
        super().__init__(name="MyAgent", config=config)
    
    async def execute(self, task: str, context: dict = None) -> dict:
        """
        Execute the agent's primary function.
        
        Args:
            task: The task description or command
            context: Optional context dict with user info, memory, etc.
        
        Returns:
            Dict with 'status', 'output', 'metadata'
        """
        # Implementation
        return {
            'status': 'success',
            'output': 'Agent output here',
            'metadata': {}
        }
```

### Properties & Methods

#### `name: str`
The agent's unique identifier.

#### `config: dict`
Agent-specific configuration.

#### `async def execute(task, context=None)`
Main execution method. Must be implemented by subclasses.

#### `async def initialize()`
Called on startup. Override for setup logic.

#### `async def shutdown()`
Called on shutdown. Override for cleanup.

## Integration Interface

### BaseIntegration Class

```python
from backend.integrations.base import BaseIntegration

class MyIntegration(BaseIntegration):
    def __init__(self, config):
        super().__init__(name="MyService", config=config)
    
    async def authenticate(self) -> bool:
        """Authenticate with the external service."""
        pass
    
    async def get_data(self, query: str) -> dict:
        """Retrieve data from the service."""
        pass
    
    async def execute_action(self, action: str, params: dict) -> dict:
        """Execute an action in the service."""
        pass
```

### Methods

#### `async def authenticate()`

Authenticate with the external service. Returns True if successful.

```python
is_authenticated = await integration.authenticate()
if is_authenticated:
    data = await integration.get_data(query)
```

#### `async def get_data(query: str)`

Fetch data from the service.

```python
data = await my_integration.get_data("get recent events")
print(data)  # Returns structured data
```

#### `async def execute_action(action: str, params: dict)`

Execute an action in the external service.

```python
result = await my_integration.execute_action(
    action="create_event",
    params={
        'title': 'Team Meeting',
        'time': '2026-06-01T14:00:00Z'
    }
)
```

## Memory & Context API

### Memory Class

```python
from backend.memory import Memory

memory = Memory()

# Store semantic data
await memory.add(
    content="User's preference",
    metadata={'category': 'preference'}
)

# Semantic search
results = await memory.search(
    query="What does the user prefer?",
    top_k=5
)

# Clear old entries
await memory.cleanup(days=30)
```

### Methods

#### `async def add(content: str, metadata: dict = None)`

Add a memory entry.

#### `async def search(query: str, top_k: int = 5)`

Perform semantic search on memories.

#### `async def get_by_id(memory_id: str)`

Retrieve a specific memory entry.

#### `async def update(memory_id: str, content: str, metadata: dict = None)`

Update an existing memory.

#### `async def delete(memory_id: str)`

Delete a memory entry.

### Context Class

```python
from backend.context import Context

context = Context()

# Build context for a command
command_context = context.build(
    user_id='user123',
    query='Check my calendar',
    relevant_memories=memories,
    time=datetime.now()
)
```

## Tools API

### Tool Definition

Tools are function declarations that Sierra can invoke:

```python
# backend/tools.py
TOOLS = [
    {
        'name': 'get_current_time',
        'description': 'Get the current time in the user\'s timezone',
        'parameters': {
            'type': 'object',
            'properties': {
                'timezone': {
                    'type': 'string',
                    'description': 'IANA timezone (e.g., America/New_York)'
                }
            }
        }
    },
    # More tools...
]
```

### Registering Custom Tools

```python
tools_module = {
    'my_tool': {
        'function': my_tool_function,
        'schema': {
            'name': 'my_tool',
            'description': 'What my tool does',
            'parameters': {...}
        }
    }
}

sierra.register_tools(tools_module)
```

## Orchestrator API

### Agent Orchestrator

The orchestrator routes commands to appropriate agents.

```python
from backend.agents.orchestrator import AgentOrchestrator

orchestrator = AgentOrchestrator()

# Route a task
result = await orchestrator.route(
    task="What's on my calendar today?",
    context=context,
    safety_checks=True  # Disable for God Mode
)
```

### Methods

#### `async def route(task: str, context: dict, safety_checks: bool = True)`

Intelligently route a task to the appropriate agent.

```python
result = await orchestrator.route(
    task="Send an email to John",
    context=context,
    safety_checks=not god_mode_enabled
)
```

#### `async def execute_with_memory(task: str, context: dict)`

Execute a task with automatic memory logging.

```python
result = await orchestrator.execute_with_memory(
    task="Remember that I like coffee in the morning",
    context=context
)
```

## Examples

### Example 1: Simple Command Execution

```python
from backend.sierra import Sierra

async def main():
    sierra = Sierra(config={'gemini_api_key': 'xxx'})
    await sierra.initialize()
    
    result = await sierra.execute_command(
        "What's the weather like tomorrow?"
    )
    print(result.output)
    
    await sierra.shutdown()

import asyncio
asyncio.run(main())
```

### Example 2: Custom Agent

```python
from backend.agents.base import BaseAgent
from backend.sierra import Sierra

class WeatherAgent(BaseAgent):
    async def execute(self, task, context=None):
        # Fetch and return weather
        return {
            'status': 'success',
            'output': 'Weather info here'
        }

async def main():
    sierra = Sierra(config=config)
    sierra.register_agent('weather', WeatherAgent())
    await sierra.initialize()

asyncio.run(main())
```

### Example 3: Memory Usage

```python
from backend.memory import Memory

async def main():
    memory = Memory()
    
    # Add memories
    await memory.add("User likes morning runs")
    await memory.add("User's boss is Sarah")
    
    # Search
    results = await memory.search("What does user like?")
    for result in results:
        print(result.content, result.score)

asyncio.run(main())
```

## Error Handling

### Common Exceptions

```python
from backend.exceptions import (
    SierraException,          # Base exception
    AuthenticationError,      # Auth failed
    IntegrationError,         # Integration issue
    ToolExecutionError,       # Tool execution failed
    MemoryError,              # Memory operation failed
)

try:
    result = await sierra.execute_command(command)
except AuthenticationError:
    print("Authentication failed")
except ToolExecutionError as e:
    print(f"Tool failed: {e}")
except SierraException as e:
    print(f"General error: {e}")
```

## Best Practices

1. **Always initialize and shutdown**: Use context managers or ensure cleanup
2. **Provide context**: Give agents and tools necessary information
3. **Handle errors**: Implement proper exception handling
4. **Use memory effectively**: Store reusable information
5. **Keep tasks focused**: Break complex operations into smaller tasks
6. **Log operations**: Enable logging for debugging
7. **Test incrementally**: Test agents and integrations in isolation

## Further Reading

- [ARCHITECTURE.md](../ARCHITECTURE.md) - System design
- [ROADMAP.md](../ROADMAP.md) - Future features
- [GOD_MODE.md](../GOD_MODE.md) - God Mode features
- [CONTRIBUTING.md](../CONTRIBUTING.md) - Contributing guidelines
