# Integration Guide for Sierra

## Overview

Integrations connect Sierra to external services like Calendar, GitHub, Email, etc. This guide walks you through creating and deploying new integrations.

## Table of Contents
- [Integration Basics](#integration-basics)
- [Creating an Integration](#creating-an-integration)
- [Authentication](#authentication)
- [Data Retrieval](#data-retrieval)
- [Action Execution](#action-execution)
- [Error Handling](#error-handling)
- [Testing](#testing)
- [Deployment](#deployment)

## Integration Basics

### What is an Integration?

An integration bridges Sierra and an external service, enabling:
- **Data retrieval**: Get calendar events, emails, GitHub issues, etc.
- **Action execution**: Create events, send emails, update GitHub issues
- **Bidirectional communication**: Two-way sync between Sierra and the service

### Built-in Integrations

Sierra currently includes:

1. **Calendar Integration** (`backend/integrations/calendar.py`)
   - Retrieve events
   - Create/update events
   - List calendars

2. **GitHub Integration** (`backend/integrations/github.py`)
   - List repositories
   - Get issues and PRs
   - Create/update issues
   - Manage workflows

## Creating an Integration

### Step 1: Create the File

```python
# backend/integrations/my_service.py
from .base import BaseIntegration
import logging

logger = logging.getLogger(__name__)

class MyServiceIntegration(BaseIntegration):
    """Integration with My Service."""
    
    def __init__(self, config):
        """
        Initialize the integration.
        
        Config should include:
        - api_key: API key for authentication
        - base_url: Base URL of the service (if applicable)
        - user_id: User identifier (if applicable)
        """
        super().__init__(name="MyService", config=config)
        self.api_key = config.get('api_key')
        self.base_url = config.get('base_url', 'https://api.myservice.com')
        self.session = None
    
    async def initialize(self):
        """Initialize the integration on startup."""
        # Setup HTTP session, verify credentials, etc.
        import aiohttp
        self.session = aiohttp.ClientSession()
    
    async def shutdown(self):
        """Clean up on shutdown."""
        if self.session:
            await self.session.close()
```

### Step 2: Implement Authentication

```python
    async def authenticate(self) -> bool:
        """
        Verify that we can connect to the service.
        
        Returns:
            True if authentication successful, False otherwise
        """
        try:
            # Make a test API call
            async with self.session.get(
                f"{self.base_url}/v1/user",
                headers=self._get_headers()
            ) as resp:
                if resp.status == 200:
                    logger.info(f"{self.name} authentication successful")
                    return True
                else:
                    logger.error(f"{self.name} auth failed: {resp.status}")
                    return False
        except Exception as e:
            logger.error(f"{self.name} auth error: {e}")
            return False
    
    def _get_headers(self) -> dict:
        """Get authorization headers."""
        return {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
```

### Step 3: Implement Data Retrieval

```python
    async def get_data(self, query: str) -> dict:
        """
        Retrieve data from the service.
        
        Args:
            query: Natural language query or structured request
        
        Returns:
            Dictionary with structured data
        """
        try:
            # Parse the query (you might use the agent orchestrator)
            # to understand what data is being requested
            
            # Example: retrieve items
            async with self.session.get(
                f"{self.base_url}/v1/items",
                headers=self._get_headers(),
                params={'query': query}
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return {
                        'status': 'success',
                        'data': data,
                        'count': len(data.get('items', []))
                    }
                else:
                    return {
                        'status': 'error',
                        'message': f'API returned {resp.status}'
                    }
        except Exception as e:
            logger.error(f"Error retrieving data: {e}")
            return {
                'status': 'error',
                'message': str(e)
            }
```

### Step 4: Implement Action Execution

```python
    async def execute_action(self, action: str, params: dict) -> dict:
        """
        Execute an action in the external service.
        
        Args:
            action: Action name (e.g., 'create_item', 'update_item')
            params: Action parameters
        
        Returns:
            Result of the action
        """
        try:
            if action == 'create_item':
                return await self._create_item(params)
            elif action == 'update_item':
                return await self._update_item(params)
            elif action == 'delete_item':
                return await self._delete_item(params)
            else:
                return {'status': 'error', 'message': f'Unknown action: {action}'}
        except Exception as e:
            logger.error(f"Action failed: {e}")
            return {'status': 'error', 'message': str(e)}
    
    async def _create_item(self, params: dict) -> dict:
        """Create a new item."""
        try:
            async with self.session.post(
                f"{self.base_url}/v1/items",
                headers=self._get_headers(),
                json=params
            ) as resp:
                data = await resp.json()
                return {
                    'status': 'success' if resp.status == 201 else 'error',
                    'data': data
                }
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    async def _update_item(self, params: dict) -> dict:
        """Update an existing item."""
        item_id = params.pop('id')
        try:
            async with self.session.patch(
                f"{self.base_url}/v1/items/{item_id}",
                headers=self._get_headers(),
                json=params
            ) as resp:
                data = await resp.json()
                return {
                    'status': 'success' if resp.status == 200 else 'error',
                    'data': data
                }
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    async def _delete_item(self, params: dict) -> dict:
        """Delete an item."""
        item_id = params.get('id')
        try:
            async with self.session.delete(
                f"{self.base_url}/v1/items/{item_id}",
                headers=self._get_headers()
            ) as resp:
                return {'status': 'success' if resp.status == 204 else 'error'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
```

## Authentication

### OAuth 2.0

For services using OAuth 2.0:

```python
class OAuth2Integration(BaseIntegration):
    async def authenticate(self) -> bool:
        """Handle OAuth 2.0 flow."""
        # Request authorization
        auth_url = self._get_auth_url()
        # User grants permission
        # Exchange code for token
        self.access_token = await self._exchange_code_for_token(code)
        return True
    
    def _get_auth_url(self) -> str:
        """Generate OAuth authorization URL."""
        return f"{self.base_url}/oauth/authorize?client_id={self.client_id}&...."
```

### API Keys

For API key authentication:

```python
class APIKeyIntegration(BaseIntegration):
    async def authenticate(self) -> bool:
        """Verify API key is valid."""
        # Store API key from config
        self.api_key = self.config.get('api_key')
        # Test the connection
        return await self._test_connection()
```

## Error Handling

```python
from backend.exceptions import IntegrationError

class RobustIntegration(BaseIntegration):
    async def get_data(self, query: str) -> dict:
        try:
            # API call
            pass
        except ConnectionError as e:
            logger.error(f"Connection failed: {e}")
            return {'status': 'error', 'message': 'Connection failed'}
        except TimeoutError as e:
            logger.error(f"Request timeout: {e}")
            return {'status': 'error', 'message': 'Request timeout'}
        except ValueError as e:
            logger.error(f"Invalid data: {e}")
            return {'status': 'error', 'message': 'Invalid data format'}
```

## Testing

### Unit Tests

```python
# tests/test_my_service_integration.py
import pytest
from unittest.mock import AsyncMock, patch
from backend.integrations.my_service import MyServiceIntegration

class TestMyServiceIntegration:
    @pytest.fixture
    def integration(self):
        config = {
            'api_key': 'test-key',
            'base_url': 'https://test.api.com'
        }
        return MyServiceIntegration(config)
    
    @pytest.mark.asyncio
    async def test_authenticate_success(self, integration):
        with patch.object(integration, 'session') as mock_session:
            mock_session.get = AsyncMock()
            mock_session.get.return_value.__aenter__.return_value.status = 200
            
            result = await integration.authenticate()
            assert result is True
    
    @pytest.mark.asyncio
    async def test_get_data(self, integration):
        with patch.object(integration, 'session') as mock_session:
            mock_session.get = AsyncMock()
            mock_session.get.return_value.__aenter__.return_value.status = 200
            mock_session.get.return_value.__aenter__.return_value.json = AsyncMock(
                return_value={'items': []}
            )
            
            result = await integration.get_data("test query")
            assert result['status'] == 'success'
```

## Deployment

### Step 1: Register the Integration

Add to `backend/sierra.py`:

```python
from backend.integrations.my_service import MyServiceIntegration

# In Sierra.__init__
self.integrations['my_service'] = MyServiceIntegration(
    config=self.config.get('integrations', {}).get('my_service', {})
)
```

### Step 2: Add Configuration

Update `.env.example` and `.env`:

```
MY_SERVICE_API_KEY=your-api-key
MY_SERVICE_BASE_URL=https://api.myservice.com
```

### Step 3: Update Tool Definitions

Add to `backend/tools.py`:

```python
{
    'name': 'my_service_get_items',
    'description': 'Retrieve items from My Service',
    'parameters': {
        'type': 'object',
        'properties': {
            'query': {
                'type': 'string',
                'description': 'Search query'
            }
        },
        'required': ['query']
    }
},
```

### Step 4: Document the Integration

Create `docs/integrations/my_service.md`:

```markdown
# My Service Integration

## Setup

1. Get API key from My Service
2. Add to .env: MY_SERVICE_API_KEY=...
3. Restart Sierra

## Usage

"Retrieve my items from My Service"
"Create a new item in My Service"

## API Reference

- `get_data(query)`: Retrieve items
- `execute_action('create_item', params)`: Create item
```

## Best Practices

1. **Error Handling**: Always handle API errors gracefully
2. **Logging**: Use appropriate log levels
3. **Rate Limiting**: Respect service rate limits
4. **Caching**: Cache data when appropriate
5. **Testing**: Write comprehensive tests
6. **Documentation**: Document configuration and usage
7. **Security**: Never hardcode secrets
8. **Async**: Use async/await for I/O operations

## Examples

See existing integrations:
- `backend/integrations/calendar.py` - Calendar service
- `backend/integrations/github.py` - GitHub API

Both show complete, production-ready examples.
