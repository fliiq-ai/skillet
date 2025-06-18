# Skillet Multi-Skill Runtime Host

A FastAPI application that dynamically loads and hosts multiple Skillet skills in a single service, solving the "10+ microservices" problem while preserving all individual skill functionality.

## Problem Solved

**Before (Microservice Hell):**
```
┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│ Time Skill  │  │ Fetch Skill │  │Memory Skill │  │   ... 10+   │
│   :8001     │  │   :8002     │  │   :8003     │  │   Skills    │
└─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘
```
*Managing 10+ separate services becomes impractical*

**After (Consolidated Host):**
```
┌─────────────────────────────────────────────────────────────────┐
│                  Multi-Skill Runtime Host                       │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐│
│  │ Time Skill  │ │ Fetch Skill │ │Memory Skill │ │   10+ More  ││
│  │  /skills/   │ │  /skills/   │ │  /skills/   │ │   Skills    ││
│  │    time     │ │    fetch    │ │   memory    │ │             ││
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘│
│                        Single Port :8000                        │
└─────────────────────────────────────────────────────────────────┘
```
*Single service hosting multiple skills with preserved APIs*

## Key Features

- **🔄 Dynamic Loading**: Load skills from configuration without code changes
- **🔗 API Preservation**: All existing skill endpoints work unchanged
- **📦 Consolidated Hosting**: Single service, single port, multiple skills
- **🔧 Hot Reload**: Add/remove skills without restarting the service
- **🌐 Unified Discovery**: Combined catalog endpoint for all hosted skills
- **⚙️ Flexible Configuration**: YAML-based skill management
- **🛡️ Error Isolation**: One skill failure doesn't affect others

## Architecture

### Endpoint Structure

**Individual Skills (Preserved):**
```
GET  /skills/time/inventory     # Time skill inventory
GET  /skills/time/schema        # Time skill schema  
POST /skills/time/run           # Time skill execution

GET  /skills/fetch/inventory    # Fetch skill inventory
POST /skills/fetch/run          # Fetch skill execution

GET  /skills/memory/inventory   # Memory skill inventory
POST /skills/memory/run         # Memory skill execution
```

**Unified Host Endpoints:**
```
GET  /                          # Service information
GET  /health                    # Health check
GET  /catalog                   # Combined skill catalog
GET  /skills                    # List of loaded skills
POST /reload                    # Hot reload skills
```

### Skill Mounting

Each skill is dynamically imported and mounted as a sub-application:

```python
# Skills are mounted at /skills/{mount_path}
app.mount("/skills/time", time_skill_app)
app.mount("/skills/fetch", fetch_skill_app)  
app.mount("/skills/memory", memory_skill_app)
```

## Quick Start

### 1. Install Dependencies

```bash
cd services/runtime
pip install -r requirements.txt
```

### 2. Configure Skills

Edit `runtime-config.yaml` to specify which skills to load:

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
    
  - name: memory_skill
    path: ./examples/anthropic_memory
    mount: memory
    enabled: true
```

### 3. Start the Runtime Host

```bash
# From the skillet root directory
cd services/runtime
python multi_skill_host.py --config runtime-config.yaml --port 8000
```

Or using uvicorn directly:

```bash
uvicorn multi_skill_host:create_app --host 0.0.0.0 --port 8000 --reload
```

### 4. Test the Service

```bash
# Run comprehensive tests
./test.sh

# Or test manually
curl -s http://localhost:8000/ | jq '.'
curl -s http://localhost:8000/skills/time/run -X POST -H "Content-Type: application/json" -d '{"timezone": "UTC"}'
```

## Configuration

### Basic Configuration

```yaml
# runtime-config.yaml
skills:
  - name: my_skill
    path: ./path/to/skill
    mount: my_skill
    enabled: true

server:
  host: 0.0.0.0
  port: 8000
  reload: true
```

### Advanced Configuration

```yaml
skills:
  # Local skill
  - name: time_skill
    path: ./examples/anthropic_time
    mount: time
    enabled: true
    
  # Skill with custom dependencies
  - name: custom_skill
    path: ./custom/skills/my_skill
    mount: custom
    enabled: true
    
  # Disabled skill (for testing)
  - name: experimental_skill
    path: ./experimental/skill
    mount: experimental  
    enabled: false

server:
  host: 0.0.0.0
  port: 8000
  reload: true

settings:
  cors_enabled: true
  auto_reload_config: false
  log_level: info
```

## Usage Examples

### Basic Usage

```python
import httpx

async def use_consolidated_skills():
    async with httpx.AsyncClient() as client:
        # Get service info
        info = await client.get("http://localhost:8000/")
        print(f"Loaded skills: {info.json()['loaded_skills']}")
        
        # Use time skill
        time_result = await client.post(
            "http://localhost:8000/skills/time/run",
            json={"timezone": "America/New_York"}
        )
        
        # Use fetch skill
        fetch_result = await client.post(
            "http://localhost:8000/skills/fetch/run", 
            json={"url": "https://httpbin.org/json"}
        )
        
        return time_result.json(), fetch_result.json()
```

### Discovery Service Integration

Update your Discovery Service configuration to point to the consolidated host:

```yaml
# services/discovery/skills.yaml
skills:
  # Instead of individual services:
  # - "http://localhost:8001"  # time
  # - "http://localhost:8002"  # fetch  
  # - "http://localhost:8003"  # memory
  
  # Use consolidated host:
  - "http://localhost:8000/skills/time"
  - "http://localhost:8000/skills/fetch"
  - "http://localhost:8000/skills/memory"
```

### OpenAI Integration

The consolidated host works seamlessly with existing OpenAI integrations:

```python
# Get skills from consolidated host
skills_response = requests.get("http://localhost:8000/catalog")
skills = skills_response.json()["skills"]

# Build function definitions (same as before)
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

## Management Operations

### Hot Reload Skills

```bash
# Reload skills without restarting the service
curl -X POST http://localhost:8000/reload
```

### Health Monitoring

```bash
# Check service health
curl -s http://localhost:8000/health | jq '.'

# Get detailed skill status
curl -s http://localhost:8000/catalog | jq '.runtime_host'
```

### Skill Management

```bash
# List loaded skills
curl -s http://localhost:8000/skills | jq '.skills[].name'

# Get unified catalog
curl -s http://localhost:8000/catalog | jq '.skills | length'
```

## Deployment Options

### Development

```bash
# With auto-reload
python multi_skill_host.py --reload --port 8000
```

### Production

```bash
# Production settings
uvicorn multi_skill_host:create_app --host 0.0.0.0 --port 8000 --workers 4
```

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy runtime host
COPY services/runtime/ ./runtime/
COPY examples/ ./examples/

# Install dependencies
RUN pip install -r runtime/requirements.txt

# Install skill dependencies
RUN pip install -r examples/anthropic_time/requirements.txt
RUN pip install -r examples/anthropic_fetch/requirements.txt  
RUN pip install -r examples/anthropic_memory/requirements.txt

EXPOSE 8000

CMD ["python", "runtime/multi_skill_host.py", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose

```yaml
version: '3.8'
services:
  skillet-runtime:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./runtime-config.yaml:/app/runtime-config.yaml
    environment:
      - LOG_LEVEL=info
      
  skillet-discovery:
    build: ./services/discovery
    ports:
      - "8001:8000"
    environment:
      - SKILLET_SKILLS=http://skillet-runtime:8000/skills/time,http://skillet-runtime:8000/skills/fetch,http://skillet-runtime:8000/skills/memory
```

## Migration Guide

### From Individual Services

**Before (individual services):**
```bash
# Terminal 1
cd examples/anthropic_time && uvicorn skillet_runtime:app --port 8001

# Terminal 2  
cd examples/anthropic_fetch && uvicorn skillet_runtime:app --port 8002

# Terminal 3
cd examples/anthropic_memory && uvicorn skillet_runtime:app --port 8003
```

**After (consolidated host):**
```bash
# Single terminal
cd services/runtime && python multi_skill_host.py
```

**Client code changes:**
```python
# Before
time_url = "http://localhost:8001/run"
fetch_url = "http://localhost:8002/run"

# After  
time_url = "http://localhost:8000/skills/time/run"
fetch_url = "http://localhost:8000/skills/fetch/run"
```

### Gradual Migration

You can migrate gradually by running both models simultaneously:

1. **Phase 1**: Run individual services + consolidated host
2. **Phase 2**: Update clients to use consolidated endpoints
3. **Phase 3**: Shut down individual services

## Advanced Features

### Custom Skill Loading

```python
# Extend MultiSkillHost for custom loading logic
class CustomSkillHost(MultiSkillHost):
    def load_skill(self, skill_config):
        # Custom skill loading logic
        # Add authentication, validation, etc.
        super().load_skill(skill_config)
```

### Middleware Integration

```python
# Add custom middleware to the host
host = MultiSkillHost()
host.app.add_middleware(CustomMiddleware)
```

### Monitoring Integration

```python
# Add metrics and monitoring
from prometheus_fastapi_instrumentator import Instrumentator

instrumentator = Instrumentator()
instrumentator.instrument(host.app)
instrumentator.expose(host.app)
```

## Troubleshooting

### Common Issues

1. **Skill not loading**
   - Check skill path in configuration
   - Verify `skillet_runtime.py` exists
   - Check skill dependencies are installed

2. **Import conflicts**
   - Skills are loaded in isolated environments
   - Check for naming conflicts in skill modules

3. **Port conflicts**
   - Default port is 8000
   - Use `--port` to specify different port

### Debug Mode

```bash
# Enable debug logging
LOG_LEVEL=DEBUG python multi_skill_host.py --reload
```

### Skill Isolation

Each skill runs in its own module namespace, preventing conflicts:

```python
# Skills can't interfere with each other
skill_a.some_function()  # Won't affect skill_b
skill_b.some_function()  # Independent execution
```

## Performance Considerations

### Memory Usage

- Each skill loads once and stays in memory
- Shared dependencies are reused
- Memory usage: ~10-50MB per skill

### Response Times

- No network overhead between skills
- Faster than microservice calls
- Typical response time: <10ms for skill routing

### Scaling

- Single process handles all skills
- Use multiple workers for high load
- Consider skill-specific scaling needs

## Future Enhancements

### Planned Features

- **Skill Versioning**: Load multiple versions of the same skill
- **Resource Limits**: Per-skill CPU/memory limits
- **Skill Marketplace**: Dynamic skill installation
- **Load Balancing**: Route to multiple skill instances
- **Skill Analytics**: Usage metrics and performance monitoring

### Extensibility

The runtime host is designed to be extensible:

```python
# Plugin system for custom functionality
class SkillPlugin:
    def on_skill_load(self, skill): pass
    def on_skill_execute(self, skill, params): pass
    def on_skill_error(self, skill, error): pass
```

## Best Practices

1. **Configuration Management**
   - Use version control for `runtime-config.yaml`
   - Environment-specific configurations
   - Validate configurations before deployment

2. **Skill Development**
   - Keep skills stateless when possible
   - Use proper error handling
   - Implement health checks

3. **Deployment**
   - Use process managers (systemd, supervisor)
   - Implement proper logging
   - Monitor resource usage

4. **Security**
   - Validate skill inputs
   - Implement authentication if needed
   - Use HTTPS in production

The Multi-Skill Runtime Host provides the perfect balance between the flexibility of microservices and the simplicity of monolithic deployment, making it practical to host dozens of skills in a single, manageable service. 