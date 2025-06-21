# Get Current Time Skillet Example

This skill returns the current date and time, with support for any IANA-compliant timezone. It serves as a Skillet-compatible implementation of the Anthropic `time` MCP.

## 🔐 **Credential Requirements**

✅ **No credentials required!** This skill works out of the box without any API keys or configuration.

This makes it perfect for:
- Testing and learning Skillet concepts
- Development environments
- Situations where you need reliable functionality without external dependencies

## Quick Start

You'll need two terminal windows to run and test this skill:

### Terminal 1: Start the Server

```bash
# Make sure you're in the right directory
cd examples/anthropic_time

# Install dependencies
pip install -r requirements.txt

# Start the server
uvicorn skillet_runtime:app --reload
```

The server will be available at `http://127.0.0.1:8000`. Keep this terminal open to see server logs.

### Terminal 2: Run the Automated Tests

In a new terminal window:
```bash
# Navigate to the same directory
cd examples/anthropic_time

# Run the automated tests
./test.sh
```

A successful test run will show:
```
--- Testing Time Skillet ---
0. Getting skill inventory...
{"skill":{"name":"get_current_time","description":"Returns the current date and time...","use_cases":["When user asks about the current time"...]}}

1. Getting tool schema...
{"name":"get_current_time","description":"Returns the current date and time..."}

2. Getting current time in UTC (default)...
{"iso_8601":"2025-06-12T04:46:33+00:00",...}

3. Getting current time in America/New_York...
{"iso_8601":"2025-06-12T00:46:33-04:00",...}

4. Testing with an invalid timezone...
{"detail":"400: Invalid timezone: 'Mars/Olympus_Mons'..."}
```

## API Usage

The skill provides three main endpoints for different purposes:

### Inventory Endpoint: Skill Discovery

For LLM agents to understand when and how to use this skill:

```bash
curl -s -X GET http://127.0.0.1:8000/inventory \
  -H "Content-Type: application/json"
```

This returns metadata that helps LLMs decide when to use this skill:
- **Use cases**: When this skill should be selected
- **Example queries**: Sample user inputs that would trigger this skill
- **Categories and tags**: For skill classification and discovery
- **Performance characteristics**: To help with resource planning
- **Workflow position**: Where this skill fits in typical workflows

### Schema Endpoint: Technical Specification

For understanding the exact inputs and outputs:

```bash
curl -s -X GET http://127.0.0.1:8000/schema \
  -H "Content-Type: application/json"
```

This returns a standardized schema that includes:
- Tool name, description, and version
- Input parameters with types and descriptions
- Output schema with expected return format
- Endpoint and method information

### Execution Endpoint: Run the Skill

You can execute the skill by making POST requests to the `/run` endpoint:

#### 1. Get Current Time in UTC (Default)

Send a request with an empty JSON object to get the time in the default UTC timezone.

```bash
curl -s -X POST http://127.0.0.1:8000/run \
  -H "Content-Type: application/json" \
  -d '{}'
```

#### 2. Get Current Time in a Specific Timezone

Provide a timezone in the JSON payload to get the time for that location.

```bash
curl -s -X POST http://127.0.0.1:8000/run \
  -H "Content-Type: application/json" \
  -d '{"timezone": "America/Los_Angeles"}'
```

#### 3. Handle Invalid Timezone

The skill will return an HTTP 500 error with a descriptive message if the timezone is not valid.

```bash
curl -s -X POST http://127.0.0.1:8000/run \
  -H "Content-Type: application/json" \
  -d '{"timezone": "Mars/Olympus_Mons"}'
```

*Expected Response: `{"detail":"ValueError: Invalid timezone: 'Mars/Olympus_Mons'"}`* 