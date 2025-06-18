# Skillet Discovery Service

A lightweight aggregation service that polls multiple Skillet skills and provides a unified catalog for LLM agents to discover and intelligently select appropriate skills.

## Overview

The Discovery Service solves a key challenge in multi-skill environments: **How does an LLM agent know what skills are available and when to use them?**

Instead of hardcoding skill endpoints, LLM applications can query the Discovery Service to:
- **Discover** all available skills dynamically
- **Search** for skills by capability, category, or use case
- **Get endpoints** for direct skill interaction
- **Filter** skills by complexity, tags, or other criteria

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   LLM Agent     │────│ Discovery Service │────│ Skillet Skills  │
│                 │    │                  │    │                 │
│ 1. What skills? │    │ Polls /inventory │    │ • Time Skill    │
│ 2. Search skills│────│ Aggregates data  │────│ • Fetch Skill   │
│ 3. Use skill    │    │ Serves catalog   │    │ • Memory Skill  │
└─────────────────┘    └──────────────────┘    │ • Custom Skills │
                                               └─────────────────┘
```

## Quick Start

### 1. Start Your Skillet Skills

First, make sure your Skillet skills are running on different ports:

```bash
# Terminal 1: Time skill
cd examples/anthropic_time
uvicorn skillet_runtime:app --port 8001

# Terminal 2: Fetch skill  
cd examples/anthropic_fetch
uvicorn skillet_runtime:app --port 8002

# Terminal 3: Memory skill
cd examples/anthropic_memory
uvicorn skillet_runtime:app --port 8003
```

### 2. Start the Discovery Service

```bash
# Terminal 4: Discovery service
cd services/discovery

# Install dependencies
pip install -r requirements.txt

# Start the discovery service
uvicorn main:app --reload --port 8000
```

The Discovery Service will be available at `http://localhost:8000`.

### 3. Test the Discovery Service

```bash
# Run the comprehensive test suite
./test.sh
```

## API Endpoints

### Core Endpoints

#### `GET /catalog`
Get the complete catalog of all skills (available and unavailable).

```bash
curl -s http://localhost:8000/catalog | jq '.'
```

#### `GET /skills`
Get only the available skills (filtered to remove unavailable ones).

```bash
curl -s http://localhost:8000/skills | jq '.'
```

#### `GET /search`
Search and filter skills by various criteria.

**Parameters:**
- `query` - Text search across name, description, use cases, example queries
- `category` - Filter by skill category (utility, web_scraping, memory_management, etc.)
- `complexity` - Filter by complexity level (simple, intermediate, advanced)
- `tags` - Comma-separated list of tags

**Examples:**

```bash
# Find skills related to time
curl -s "http://localhost:8000/search?query=time" | jq '.skills[].skill.name'

# Find simple utility skills
curl -s "http://localhost:8000/search?category=utility&complexity=simple" | jq '.'

# Find skills with datetime tags
curl -s "http://localhost:8000/search?tags=datetime" | jq '.'

# Complex search: web-related simple skills
curl -s "http://localhost:8000/search?query=web&complexity=simple" | jq '.'
```

### Management Endpoints

#### `POST /refresh`
Manually refresh the skill catalog by re-polling all configured skills.

```bash
curl -s -X POST http://localhost:8000/refresh | jq '.'
```

#### `GET /health`
Health check and service status.

```bash
curl -s http://localhost:8000/health | jq '.'
```

## Configuration

### Method 1: Configuration File (Recommended)

Create or modify `skills.yaml`:

```yaml
skills:
  - "http://localhost:8001"  # anthropic_time
  - "http://localhost:8002"  # anthropic_fetch
  - "http://localhost:8003"  # anthropic_memory
  - "https://your-production-skill.com"
```

### Method 2: Environment Variable

```bash
export SKILLET_SKILLS="http://localhost:8001,http://localhost:8002,http://localhost:8003"
uvicorn main:app --reload --port 8000
```

### Method 3: Custom Config File Location

```bash
export SKILLET_CONFIG="/path/to/your/skills.yaml"
uvicorn main:app --reload --port 8000
```

## Integration Examples

### For LLM Applications

Here's how an LLM application might use the Discovery Service:

```python
import httpx

async def discover_and_use_skills(user_query: str):
    async with httpx.AsyncClient() as client:
        # 1. Search for relevant skills
        search_response = await client.get(
            "http://localhost:8000/search",
            params={"query": user_query}
        )
        skills = search_response.json()["skills"]
        
        # 2. Select the most appropriate skill
        if skills:
            chosen_skill = skills[0]  # or use LLM to choose
            skill_endpoint = chosen_skill["skill"]["endpoints"]["run"]
            
            # 3. Get the skill's schema
            schema_response = await client.get(
                chosen_skill["skill"]["endpoints"]["schema"]
            )
            schema = schema_response.json()
            
            # 4. Use the skill
            result = await client.post(
                skill_endpoint,
                json={"your": "parameters"}
            )
            
            return result.json()
```

### For OpenAI Function Calling

The Discovery Service can be integrated into OpenAI function calling workflows:

```python
# Get available skills and their schemas
skills_response = requests.get("http://localhost:8000/skills")
skills = skills_response.json()["skills"]

# Build OpenAI function definitions from skill schemas
functions = []
for skill in skills:
    schema_response = requests.get(skill["skill"]["endpoints"]["schema"])
    schema = schema_response.json()
    
    functions.append({
        "name": schema["name"],
        "description": schema["description"],
        "parameters": schema["parameters"]
    })

# Use with OpenAI
response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "What time is it?"}],
    functions=functions,
    function_call="auto"
)
```

## Response Format

Each skill in the catalog includes:

```json
{
  "skill": {
    "name": "Time Skill",
    "description": "Provides current time and date information",
    "version": "1.0.0",
    "category": "utility",
    "complexity": "simple",
    "use_cases": ["Get current time", "Check date", "Timezone queries"],
    "example_queries": ["What time is it?", "What's today's date?"],
    "base_url": "http://localhost:8001",
    "endpoints": {
      "inventory": "http://localhost:8001/inventory",
      "schema": "http://localhost:8001/schema", 
      "run": "http://localhost:8001/run"
    },
    "tags": ["datetime", "utility", "timezone"],
    "performance": "fast",
    "dependencies": []
  }
}
```

## Production Deployment

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Variables for Production

```bash
# Skill endpoints (comma-separated)
SKILLET_SKILLS="https://skill1.prod.com,https://skill2.prod.com"

# Optional: Custom config file
SKILLET_CONFIG="/etc/skillet/skills.yaml"
```

## Advanced Features

### Automatic Refresh (Future Enhancement)

The service could be extended to automatically refresh the catalog at regular intervals:

```python
# Add to main.py
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()
scheduler.add_job(update_skill_catalog, 'interval', minutes=5)
scheduler.start()
```

### Skill Health Monitoring (Future Enhancement)

Track skill availability and response times:

```python
# Enhanced health tracking
skill_health = {
    "http://localhost:8001": {
        "status": "healthy",
        "last_check": "2024-01-15T10:30:00Z",
        "response_time_ms": 45,
        "uptime_percentage": 99.9
    }
}
```

## Troubleshooting

### Common Issues

1. **No skills found**: Check that your skills are running and accessible
2. **Connection errors**: Verify skill URLs in configuration
3. **Empty catalog**: Ensure skills implement `/inventory` endpoint

### Debug Mode

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
uvicorn main:app --reload --port 8000 --log-level debug
```

### Manual Testing

```bash
# Test individual skill connectivity
curl -s http://localhost:8001/inventory | jq '.'
curl -s http://localhost:8002/inventory | jq '.'
curl -s http://localhost:8003/inventory | jq '.'
```

## Next Steps

With the Discovery Service running, you can:

1. **Build LLM applications** that dynamically discover and use skills
2. **Create skill marketplaces** where skills register themselves
3. **Implement load balancing** across multiple instances of the same skill
4. **Add authentication** and rate limiting for production use
5. **Create monitoring dashboards** for skill health and usage

The Discovery Service provides the foundation for truly dynamic, scalable skill-based AI systems. 