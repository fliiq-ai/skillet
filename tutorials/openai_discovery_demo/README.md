# OpenAI + Skillet Discovery Service Demo

This advanced tutorial demonstrates how to build an intelligent LLM agent that **dynamically discovers and uses Skillet skills** through the Discovery Service, rather than hardcoding skill endpoints.

## What This Demo Shows

- **🔍 Dynamic Skill Discovery**: Agent automatically finds relevant skills for user queries
- **🧠 Intelligent Selection**: Uses semantic search to match user intent with appropriate skills
- **⚡ Automatic Integration**: Converts skill schemas to OpenAI function definitions on-the-fly
- **🔄 Real-time Adaptation**: Skill catalog updates as new skills become available
- **🛡️ Graceful Handling**: Error recovery and fallback mechanisms

## Architecture Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   User Query    │    │ Discovery Service │    │ Skillet Skills  │
│ "What time is   │────│                  │────│                 │
│  it in Tokyo?"  │    │ 1. Search skills │    │ • Time Skill    │
└─────────────────┘    │ 2. Get schemas   │    │ • Fetch Skill   │
                       │ 3. Return info   │    │ • Memory Skill  │
┌─────────────────┐    └──────────────────┘    └─────────────────┘
│ OpenAI Agent    │             │
│                 │             │
│ 1. Query skills │─────────────┘
│ 2. Build funcs  │
│ 3. Call OpenAI  │    ┌──────────────────┐
│ 4. Execute      │────│     OpenAI       │
│ 5. Respond      │    │   Function       │
└─────────────────┘    │   Calling        │
                       └──────────────────┘
```

## Prerequisites

You'll need **5 terminal windows** for this demo:

1. **Terminal 1-3**: Skillet skills (time, fetch, memory)
2. **Terminal 4**: Discovery Service
3. **Terminal 5**: OpenAI Discovery Demo

## Setup Instructions

### Step 1: Start Skillet Skills

Open three terminal windows and start each skill on different ports:

```bash
# Terminal 1: Time Skill
cd examples/anthropic_time
pip install -r requirements.txt
uvicorn skillet_runtime:app --port 8001

# Terminal 2: Fetch Skill
cd examples/anthropic_fetch  
pip install -r requirements.txt
uvicorn skillet_runtime:app --port 8002

# Terminal 3: Memory Skill
cd examples/anthropic_memory
pip install -r requirements.txt
uvicorn skillet_runtime:app --port 8003
```

### Step 2: Start Discovery Service

```bash
# Terminal 4: Discovery Service
cd services/discovery
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Step 3: Configure OpenAI API Key

Create a `.env` file in this directory:

```bash
# In tutorials/openai_discovery_demo/
echo "OPENAI_API_KEY=your_openai_api_key_here" > .env
```

Or set the environment variable:

```bash
export OPENAI_API_KEY="your_openai_api_key_here"
```

### Step 4: Run the Discovery Demo

```bash
# Terminal 5: Discovery Demo
cd tutorials/openai_discovery_demo
pip install -r requirements.txt
python main.py
```

## Demo Walkthrough

### 1. Initialization

The agent starts by connecting to the Discovery Service and displays available skills:

```
🤖 Intelligent Skillet Agent
═══════════════════════════════════════════════════════════════════

✅ Agent initialized!
The agent will automatically discover and use relevant skills for your queries.

🔍 Discovering available skills...
┏━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━┓
┃ Name                 ┃ Category             ┃ Description          ┃ Use Cases            ┃
┡━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━┩
│ Time Skill           │ utility              │ Provides current...  │ Get current time...  │
│ Fetch Skill          │ web_scraping         │ Fetches and...       │ Scrape web content.. │
│ Memory Skill         │ memory_management    │ Persistent...        │ Remember user info.. │
└──────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┘
```

### 2. Intelligent Query Processing

Try these example queries to see the agent in action:

#### Time-related queries:
```
You: What time is it?
Agent: 🔍 Discovering available skills...
       🔧 Using Time Skill...
       It's currently 2:30 PM PST on January 15, 2024.
```

#### Web scraping queries:
```
You: Can you get the content from https://example.com?
Agent: 🔍 Discovering available skills...
       🔧 Using Fetch Skill...
       I've retrieved the content from https://example.com. Here's what I found: [content]
```

#### Memory-related queries:
```
You: Remember that I work at Anthropic
Agent: 🔍 Discovering available skills...
       🔧 Using Memory Skill...
       I've stored the information that you work at Anthropic in my memory.
```

### 3. Dynamic Skill Discovery

The agent dynamically searches for relevant skills based on your query:

- **Query**: "What time is it?" → Discovers **Time Skill**
- **Query**: "Fetch a webpage" → Discovers **Fetch Skill**  
- **Query**: "Remember this fact" → Discovers **Memory Skill**
- **Query**: "web scraping" → Discovers **Fetch Skill**

## Key Features Demonstrated

### 1. Semantic Skill Matching

The agent uses the Discovery Service's search capabilities to find skills that match the user's intent:

```python
# Agent searches for skills related to user query
skills = await discovery_client.search_skills(query=user_message)
```

### 2. Automatic Function Definition Generation

Skill schemas are automatically converted to OpenAI function definitions:

```python
function_def = {
    "name": schema.get("name", skill.name).replace(" ", "_").lower(),
    "description": schema.get("description", skill.description),
    "parameters": schema["parameters"]
}
```

### 3. Real-time Skill Execution

When OpenAI decides to use a skill, the agent executes it in real-time:

```python
# Execute the skill with OpenAI's chosen parameters
result = await discovery_client.execute_skill(skill, function_args)
```

### 4. Context-Aware Responses

The agent provides intelligent responses by combining OpenAI's language capabilities with skill execution results.

## Advanced Usage Examples

### Multi-step Workflows

```
You: Get the current time and remember that I asked about it
Agent: 🔍 Discovering available skills...
       🔧 Using Time Skill...
       🔧 Using Memory Skill...
       It's currently 3:45 PM PST. I've also remembered that you asked about the time.
```

### Complex Queries

```
You: I need to scrape a website and remember the key information
Agent: 🔍 Discovering available skills...
       🔧 Using Fetch Skill...
       🔧 Using Memory Skill...
       I've retrieved the website content and stored the key information in memory.
```

## Configuration Options

### Custom Discovery Service URL

```python
discovery_client = SkilletDiscoveryClient("http://your-discovery-service.com")
```

### Skill Filtering

The agent can be configured to only discover certain types of skills:

```python
# Only discover simple utility skills
skills = await discovery_client.search_skills(
    category="utility", 
    complexity="simple"
)
```

## Error Handling

The demo includes comprehensive error handling:

- **Missing API Key**: Clear instructions for setup
- **Discovery Service Down**: Graceful fallback
- **Skill Unavailable**: Error messages and alternatives
- **Invalid Parameters**: Parameter validation and correction

## Extending the Demo

### Adding Custom Skills

1. Create your skill following the Skillet framework
2. Implement `/inventory`, `/schema`, and `/run` endpoints
3. Add your skill URL to the Discovery Service configuration
4. The agent will automatically discover and use your skill!

### Custom Agent Behavior

Modify the system prompt in `IntelligentSkilletAgent.chat()` to change how the agent behaves:

```python
system_content = """You are a specialized AI assistant for [your domain].
When users ask questions about [specific topic], prioritize using [specific skills].
Always explain what you're doing and why."""
```

### Integration with Other LLM Providers

The pattern can be adapted for other LLM providers:

- **Anthropic Claude**: Use function calling when available
- **Local Models**: Adapt the function calling format
- **Custom Models**: Implement your own function calling logic

## Production Considerations

### Security

- Validate all skill inputs and outputs
- Implement authentication for skill access
- Rate limit Discovery Service requests

### Performance

- Cache skill schemas to reduce Discovery Service calls
- Implement skill response caching
- Use connection pooling for HTTP requests

### Monitoring

- Log all skill discoveries and executions
- Monitor Discovery Service health
- Track skill usage patterns

## Troubleshooting

### Common Issues

1. **"No skills discovered"**
   - Check that all skills are running on correct ports
   - Verify Discovery Service is accessible
   - Test individual skill `/inventory` endpoints

2. **"OpenAI API key not found"**
   - Ensure `.env` file exists with correct key
   - Verify environment variable is set

3. **"Skill execution failed"**
   - Check skill logs for errors
   - Verify skill parameters match schema
   - Test skill directly with curl

### Debug Mode

Enable detailed logging by modifying the agent:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Next Steps

This demo provides the foundation for building production-ready LLM applications with dynamic skill discovery. Consider:

1. **Building a web interface** for the agent
2. **Adding authentication and user management**
3. **Implementing conversation history and context**
4. **Creating specialized agents** for different domains
5. **Adding skill marketplace integration**

The combination of Skillet's skill framework with dynamic discovery creates powerful, adaptable AI systems that can grow and evolve with your needs. 