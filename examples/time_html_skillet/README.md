# Get Current Time Skillet Example

This skill returns the current date and time, with support for any IANA-compliant timezone. It serves as a Skillet-compatible implementation of the Anthropic `time` MCP.

## Quick Start

From this directory (`examples/time_html_skillet`):

```bash
# Install dependencies
pip install -r requirements.txt

# Start the server
uvicorn skillet_runtime:app --reload
```

The server will be available at `http://127.0.0.1:8000`.

## API Usage

You can test the skill by making POST requests to the `/run` endpoint.

### 1. Get Current Time in UTC (Default)

Send a request with an empty JSON object to get the time in the default UTC timezone.

```bash
curl -X POST http://127.0.0.1:8000/run \
  -H "Content-Type: application/json" \
  -d '{}'
```

### 2. Get Current Time in a Specific Timezone

Provide a timezone in the JSON payload to get the time for that location.

```bash
curl -X POST http://127.0.0.1:8000/run \
  -H "Content-Type: application/json" \
  -d '{"timezone": "America/Los_Angeles"}'
```

### 3. Handle Invalid Timezone

The skill will return an HTTP 500 error with a descriptive message if the timezone is not valid.

```bash
curl -X POST http://127.0.0.1:8000/run \
  -H "Content-Type: application/json" \
  -d '{"timezone": "Mars/Olympus_Mons"}'
```

This will result in a response like:
```json
{
  "detail": "Invalid timezone: 'Mars/Olympus_Mons'"
}
``` 