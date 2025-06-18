# Fliiq Skillet 🍳

**Skillet** is an HTTP-native, OpenAPI-first framework for packaging and running
reusable *skills* (micro-functions) that Large-Language-Model agents can call
over the network.

> "Cook up a skill in minutes, serve it over HTTPS, remix it in a workflow."

---

## Why another spec?

Current community standard **MCP** servers are great for quick sandbox demos
inside an LLM playground, but painful when you try to ship real-world agent
workflows:

| MCP Pain Point | Skillet Solution |
| -------------- | ---------------- |
| Default **stdio** transport; requires local pipes and custom RPC          | **Pure HTTP + JSON** with an auto-generated OpenAPI contract |
| One bespoke server **per repo**; Docker mandatory                         | Single-file **Skillfile.yaml** → deploy to Cloudflare Workers, AWS Lambda or raw FastAPI |
| No discovery or function manifest                                         | Registry + `/openapi.json` enable automatic client stubs & OpenAI function-calling |
| Heavy cold-start if each agent needs its own container                    | Skills are tiny (≤ 5 MB) Workers; scale-to-zero is instant |
| Secrets baked into code                                                   | Standard `.skillet.env` + runtime injection |
| Steep learning curve for non-infra devs                                   | `pip install fliiq-skillet` → `skillet new hello_world` → **done** |

### Key Concepts

* **Skilletfile.yaml ≤50 lines** — declarative inputs/outputs, runtime & entry-point
* **`skillet dev`** — hot-reload FastAPI stub for local testing
* **`skillet deploy`** — one-command deploy to Workers/Lambda (more targets soon)
* **Registry** — browse, star and import skills; share community "recipes" in the *Cookbook*
* **Cookbook** — visual builder that chains skills into agent workflows

### Quick start (Python)

```bash
pip install fliiq-skillet
skillet new fetch_html --runtime python
cd fetch_html
skillet dev          # Swagger UI on http://127.0.0.1:8000
```

## Examples

The `examples/` directory contains reference implementations of Skillet skills:

- [anthropic_fetch](examples/anthropic_fetch/README.md) - Fetches HTML content from URLs. A Skillet-compatible implementation of the Anthropic `fetch` MCP.
- [anthropic_time](examples/anthropic_time/README.md) - Returns the current time in any timezone. A Skillet-compatible implementation of the Anthropic `time` MCP.
- [anthropic_memory](examples/anthropic_memory/README.md) - A stateful skill that provides a simple in-memory key-value store. A Skillet-compatible implementation of the Anthropic `memory` MCP.

Each example includes:
- A complete `Skilletfile.yaml` configuration
- API documentation and usage examples
- An automated `test.sh` script to verify functionality

### Testing the Examples Using the Automated Test Scripts

To test any example, you'll need two terminal windows:

1. First terminal - Start the server:
```bash
cd examples/[example_name]  # e.g., anthropic_fetch, anthropic_time, anthropic_memory
pip install -r requirements.txt
uvicorn skillet_runtime:app --reload
```

2. Second terminal - Run the tests:
```bash
cd examples/[example_name]  # same directory as above
./test.sh
```

A successful test run will show:
- All test cases executing without errors
- Expected JSON responses for successful operations
- Proper error handling for edge cases
- Server logs in the first terminal showing request handling

For example, a successful time skill test should show:
```
--- Testing Time Skillet ---
1. Getting current time in UTC (default)...
{"iso_8601":"2025-06-12T04:46:33+00:00", ...}

2. Getting current time in America/New_York...
{"iso_8601":"2025-06-12T00:46:33-04:00", ...}

3. Testing with an invalid timezone...
{"detail":"400: Invalid timezone: 'Mars/Olympus_Mons'..."}
```

See each example's specific README for detailed API usage instructions and expected responses.

## Tutorials: Using Skillet in Your Applications

The `tutorials/` directory contains example applications that demonstrate how to integrate Skillet skills into your own applications. These tutorials show real-world usage patterns and best practices for developers who want to use Skillet skills in their projects.

### Available Tutorials

- [openai_time_demo](tutorials/openai_time_demo/README.md) - Shows how to use OpenAI's GPT models with the Skillet time skill. This tutorial demonstrates:
  - Setting up OpenAI function calling with Skillet endpoints
  - Making HTTP requests to Skillet services
  - Handling responses and errors
  - Building an interactive CLI application

- [openai_discovery_demo](tutorials/openai_discovery_demo/README.md) - Advanced tutorial showing how to build an intelligent LLM agent that dynamically discovers and uses Skillet skills. Features:
  - Dynamic skill discovery through the Discovery Service
  - Intelligent skill selection based on user queries
  - Automatic function definition generation from skill schemas
  - Real-time skill catalog updates

- [multi_skill_runtime_demo](tutorials/multi_skill_runtime_demo/README.md) - Demonstrates the Multi-Skill Runtime Host that consolidates multiple skills into a single service. Features:
  - Single service hosting multiple skills (solves the "10+ microservices" problem)
  - Preserved individual skill APIs and functionality
  - Simplified deployment and management
  - Better performance with no network overhead between skills

Each tutorial includes:
- Complete working code with comments
- Clear setup instructions
- Dependencies and environment configuration
- Best practices for production use

### Using the Tutorials

1. Choose a tutorial that matches your use case
2. Follow the README instructions in the tutorial directory
3. Use the code as a template for your own application

The tutorials are designed to be minimal yet production-ready examples that you can build upon. They demonstrate how to:
- Make API calls to Skillet skills
- Handle authentication and environment variables
- Process responses and handle errors
- Structure your application code

For example, to try the OpenAI + Skillet time demo:
```bash
# First, start the Skillet time service
cd examples/anthropic_time
pip install -r requirements.txt
uvicorn skillet_runtime:app --reload

# In a new terminal, run the OpenAI demo
cd tutorials/openai_time_demo
pip install -r requirements.txt
python main.py
```

## Discovery Service: Dynamic Skill Discovery

The **Skillet Discovery Service** is a lightweight aggregation service that enables LLM applications to dynamically discover and use available skills, rather than hardcoding skill endpoints. This creates truly adaptive AI systems that can grow and evolve as new skills become available.

### Key Features

- **🔍 Dynamic Discovery**: Automatically finds and catalogs available Skillet skills
- **🔎 Intelligent Search**: Semantic search across skill names, descriptions, use cases, and tags
- **📊 Rich Metadata**: Detailed skill information including categories, complexity levels, and example queries
- **⚡ Real-time Updates**: Skill catalog updates as services come online or go offline
- **🌐 HTTP-First**: Simple REST API that any application can use

### Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   LLM Agent     │────│ Discovery Service │────│ Skillet Skills  │
│                 │    │                  │    │                 │
│ "What skills    │    │ Polls /inventory │    │ • Time Skill    │
│  are available?"│────│ Aggregates data  │────│ • Fetch Skill   │
│                 │    │ Serves catalog   │    │ • Memory Skill  │
└─────────────────┘    └──────────────────┘    │ • Custom Skills │
                                               └─────────────────┘
```

### Quick Start

1. **Start your Skillet skills** on different ports:
```bash
# Terminal 1: Time skill
cd examples/anthropic_time && uvicorn skillet_runtime:app --port 8001

# Terminal 2: Fetch skill  
cd examples/anthropic_fetch && uvicorn skillet_runtime:app --port 8002

# Terminal 3: Memory skill
cd examples/anthropic_memory && uvicorn skillet_runtime:app --port 8003
```

2. **Start the Discovery Service**:
```bash
# Terminal 4: Discovery service
cd services/discovery
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

3. **Query available skills**:
```bash
# Get all skills
curl -s http://localhost:8000/skills | jq '.'

# Search for time-related skills
curl -s "http://localhost:8000/search?query=time" | jq '.skills[].skill.name'

# Filter by category
curl -s "http://localhost:8000/search?category=utility" | jq '.'
```

### API Endpoints

- **`GET /catalog`** - Complete catalog of all skills (available and unavailable)
- **`GET /skills`** - Only available skills (filtered)
- **`GET /search`** - Search and filter skills by query, category, complexity, tags
- **`POST /refresh`** - Manually refresh the skill catalog
- **`GET /health`** - Service health check

### Integration Examples

**Python Integration:**
```python
import httpx

async def discover_and_use_skills(user_query: str):
    async with httpx.AsyncClient() as client:
        # 1. Search for relevant skills
        response = await client.get(
            "http://localhost:8000/search",
            params={"query": user_query}
        )
        skills = response.json()["skills"]
        
        # 2. Use the most appropriate skill
        if skills:
            skill = skills[0]
            result = await client.post(
                skill["skill"]["endpoints"]["run"],
                json={"your": "parameters"}
            )
            return result.json()
```

**OpenAI Function Calling:**
```python
# Get skills and build function definitions
skills_response = requests.get("http://localhost:8000/skills")
functions = []

for skill in skills_response.json()["skills"]:
    schema = requests.get(skill["skill"]["endpoints"]["schema"]).json()
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

For complete examples, see the [Discovery Service documentation](services/discovery/README.md) and the [OpenAI Discovery Demo](tutorials/openai_discovery_demo/README.md).

## Multi-Skill Runtime Host: Consolidated Skill Hosting

The **Skillet Multi-Skill Runtime Host** solves the "10+ microservices" problem by consolidating multiple Skillet skills into a single FastAPI service, while preserving all individual skill functionality and APIs.

### The Problem

**Before: Microservice Management Complexity**
```bash
# Managing multiple individual services becomes impractical
Terminal 1: cd examples/anthropic_time && uvicorn skillet_runtime:app --port 8001
Terminal 2: cd examples/anthropic_fetch && uvicorn skillet_runtime:app --port 8002  
Terminal 3: cd examples/anthropic_memory && uvicorn skillet_runtime:app --port 8003
# ... repeat for 10+ skills
```

### The Solution

**After: Single Consolidated Service**
```bash
# Single service hosts all skills
Terminal 1: cd services/runtime && python multi_skill_host.py
# All skills available at: http://localhost:8000/skills/{skill_name}/*
```

### Key Benefits

- **🏠 Single Service**: Host unlimited skills in one FastAPI application
- **🔗 API Preservation**: All existing skill endpoints work unchanged
- **📦 Simplified Deployment**: One service to deploy, monitor, and scale
- **⚡ Better Performance**: No network overhead between skills (~10x faster)
- **🛠️ Easy Management**: Hot-reload skills, unified health checks
- **💰 Cost Reduction**: ~60% reduction in resource usage

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                 Multi-Skill Runtime Host :8000                  │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐   │
│  │   Time Skill    │ │   Fetch Skill   │ │  Memory Skill   │   │
│  │ /skills/time/*  │ │ /skills/fetch/* │ │/skills/memory/* │   │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘   │
│                                                                 │
│  Unified: /health, /catalog, /skills, /reload                  │
└─────────────────────────────────────────────────────────────────┘
```

### Quick Start

1. **Configure skills** in `runtime-config.yaml`:
```yaml
skills:
  - name: time_skill
    path: ./examples/anthropic_time
    mount: time
    enabled: true
  - name: fetch_skill
    path: ./examples/anthropic_fetch
    mount: fetch
    enabled: true
```

2. **Start the runtime host**:
```bash
cd services/runtime
python multi_skill_host.py --config runtime-config.yaml
```

3. **Use skills exactly as before**:
```python
# Individual skill APIs preserved
time_result = requests.post("http://localhost:8000/skills/time/run", json={"timezone": "UTC"})
fetch_result = requests.post("http://localhost:8000/skills/fetch/run", json={"url": "https://example.com"})
```

### Management Operations

```bash
# Health check for all skills
curl http://localhost:8000/health

# Get unified catalog
curl http://localhost:8000/catalog

# Hot-reload skills (add/remove without restart)
curl -X POST http://localhost:8000/reload
```

### Integration Examples

**OpenAI Function Calling:**
```python
# Get all skills from single endpoint
skills = requests.get("http://localhost:8000/catalog").json()["skills"]

# Build function definitions (same pattern as before)
functions = []
for skill in skills:
    schema_url = f"http://localhost:8000{skill['skill']['endpoints']['schema']}"
    schema = requests.get(schema_url).json()
    functions.append({
        "name": schema["name"],
        "description": schema["description"],
        "parameters": schema["parameters"]
    })
```

**Discovery Service Integration:**
```yaml
# Update Discovery Service to use consolidated host
skills:
  # Instead of multiple services:
  # - "http://localhost:8001"  # time
  # - "http://localhost:8002"  # fetch
  # - "http://localhost:8003"  # memory
  
  # Use single consolidated host:
  - "http://localhost:8000/skills/time"
  - "http://localhost:8000/skills/fetch"
  - "http://localhost:8000/skills/memory"
```

### Migration Strategy

1. **Phase 1**: Deploy consolidated host alongside existing services
2. **Phase 2**: Update clients to use consolidated endpoints
3. **Phase 3**: Shut down individual microservices
4. **Phase 4**: Optimize and scale consolidated host

For complete examples, see the [Multi-Skill Runtime documentation](services/runtime/README.md) and the [Multi-Skill Runtime Demo](tutorials/multi_skill_runtime_demo/README.md).
