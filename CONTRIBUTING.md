# Contributing to Sierra

Thank you for your interest in contributing to Sierra! This guide will help you get started.

## Table of Contents
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Architecture Overview](#architecture-overview)
- [Adding New Agents](#adding-new-agents)
- [Creating Integrations](#creating-integrations)
- [Code Style](#code-style)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/Sierra.git`
3. Create a feature branch: `git checkout -b feature/your-feature-name`
4. Follow the development setup below

## Development Setup

### Prerequisites
- Python 3.10 or 3.11
- Node.js 16+
- macOS (currently the primary development platform)
- Google Gemini API key

### Backend Setup

```bash
# Create and activate Python environment
conda create -n sierra python=3.11 -y
conda activate sierra

# Install system dependencies (macOS)
brew install portaudio

# Install Python dependencies
pip install -r requirements.txt
playwright install chromium
```

### Frontend Setup

```bash
# Install Node dependencies
npm install

# Create environment file
cp .env.example .env
# Edit .env with your Gemini API key
```

### Running the Application

```bash
# Start both backend and frontend
conda activate sierra && npm run dev
```

## Architecture Overview

Sierra follows a modern client-server architecture:

```
┌─────────────────┐
│  Electron App   │ (React + JavaScript)
│  (Frontend)     │
└────────┬────────┘
         │ HTTP/WebSocket
         ▼
┌─────────────────────────────────────┐
│     FastAPI Backend (Python)        │
├─────────────────────────────────────┤
│ • Agent Orchestrator                │
│ • Memory & Context Management       │
│ • Tool Execution                    │
│ • Personal Integrations             │
│ • Gemini Native Audio Integration   │
└─────────────────────────────────────┘
```

### Key Components

- **`backend/server.py`**: FastAPI server and real-time audio handling
- **`backend/sierra.py`**: Core Sierra class and orchestration
- **`backend/agents/orchestrator.py`**: Intelligent routing and agent management
- **`backend/memory.py` + `context.py`**: Persistent semantic memory and context
- **`backend/tools.py`**: Function declarations for Gemini
- **`backend/integrations/`**: Personal integrations (Calendar, GitHub, etc.)
- **`frontend/src/`**: React components and UI logic

See [ARCHITECTURE.md](./ARCHITECTURE.md) for detailed technical documentation.

## Adding New Agents

Agents are specialized AI components that handle specific tasks or domains.

### Agent Structure

```python
# backend/agents/your_agent.py
from .base import BaseAgent

class YourAgent(BaseAgent):
    """Description of your agent's purpose."""
    
    def __init__(self, config=None):
        super().__init__(name="YourAgent", config=config)
    
    async def execute(self, task, context=None):
        """Execute the agent's logic."""
        # Implementation here
        return result
```

### Registering Your Agent

Add your agent to `backend/agents/orchestrator.py`:

```python
from .your_agent import YourAgent

# In the agents dictionary
self.agents['your_agent'] = YourAgent(config=config)
```

## Creating Integrations

Integrations connect Sierra to external services (Calendar, GitHub, etc.).

### Integration Template

```python
# backend/integrations/your_service.py
from .base import BaseIntegration

class YourServiceIntegration(BaseIntegration):
    """Integration with Your Service."""
    
    def __init__(self, config):
        super().__init__(name="YourService", config=config)
    
    async def authenticate(self):
        """Handle authentication flow."""
        pass
    
    async def get_data(self, query):
        """Fetch data from the service."""
        pass
    
    async def execute_action(self, action, params):
        """Execute an action in the service."""
        pass
```

### Registering Your Integration

Add to `backend/sierra.py`:

```python
from backend.integrations.your_service import YourServiceIntegration

# In initialization
self.integrations['your_service'] = YourServiceIntegration(config)
```

## Code Style

### Python
- Follow PEP 8
- Use type hints for all functions
- Docstrings for all public functions and classes
- Max line length: 100 characters

### JavaScript/React
- Use ES6+ features
- Follow Airbnb JavaScript style guide
- Use functional components and hooks
- Add prop-types or TypeScript types

### Naming Conventions
- Classes: `PascalCase`
- Functions/variables: `snake_case` (Python), `camelCase` (JavaScript)
- Constants: `UPPER_SNAKE_CASE`
- Private methods: prefix with `_`

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_agents.py

# Run with coverage
pytest --cov=backend tests/
```

### Writing Tests

```python
# tests/test_your_feature.py
import pytest
from backend.your_module import YourClass

class TestYourFeature:
    @pytest.fixture
    def setup(self):
        # Setup test fixtures
        return YourClass()
    
    def test_functionality(self, setup):
        result = setup.method()
        assert result == expected
```

## Submitting Changes

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/my-feature
   ```

2. **Make your changes**:
   - Write clear, descriptive commit messages
   - Keep commits focused and atomic
   - Update tests and documentation

3. **Test your changes**:
   ```bash
   pytest
   npm run lint  # if applicable
   ```

4. **Push and create a Pull Request**:
   ```bash
   git push origin feature/my-feature
   ```

5. **PR Guidelines**:
   - Use a clear, descriptive title
   - Reference related issues (#123)
   - Describe what changed and why
   - Include screenshots for UI changes
   - Ensure all tests pass

## God Mode Development

If adding God Mode features:

1. Review [GOD_MODE.md](./GOD_MODE.md) for philosophy and requirements
2. Reference implementation examples in `docs/god-mode/`
3. Ensure components/hooks follow the black + gold theme
4. Test with `useGodModeAutoForce` hook

## Getting Help

- Check [ARCHITECTURE.md](./ARCHITECTURE.md) for technical details
- Review [ROADMAP.md](./ROADMAP.md) for planned features
- Open an issue with detailed information
- Join discussions for architectural questions

## License

By contributing to Sierra, you agree that your contributions will be licensed under its MIT License.

Thank you for contributing! 🎉
