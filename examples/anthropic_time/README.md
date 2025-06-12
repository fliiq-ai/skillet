# Get Current Time Skillet Example

This skill returns the current date and time, with support for any IANA-compliant timezone. It serves as a Skillet-compatible implementation of the Anthropic `time` MCP.

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

### Terminal 2: Run the Tests

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
1. Getting current time in UTC (default)...
{"iso_8601":"2025-06-12T04:46:33+00:00",...}

2. Getting current time in America/New_York...
{"iso_8601":"2025-06-12T00:46:33-04:00",...}

3. Testing with an invalid timezone...
{"detail":"400: Invalid timezone: 'Mars/Olympus_Mons'..."}
```

## API Usage

You can also test individual endpoints manually using curl commands by making POST requests to the `/run` endpoint:

### 1. Get Current Time in UTC (Default)

Send a request with an empty JSON object to get the time in the default UTC timezone.

```bash
curl -s -X POST http://127.0.0.1:8000/run \
  -H "Content-Type: application/json" \
  -d '{}'
```

### 2. Get Current Time in a Specific Timezone

Provide a timezone in the JSON payload to get the time for that location.

```bash
curl -s -X POST http://127.0.0.1:8000/run \
  -H "Content-Type: application/json" \
  -d '{"timezone": "America/Los_Angeles"}'
```

### 3. Handle Invalid Timezone

The skill will return an HTTP 500 error with a descriptive message if the timezone is not valid.

```bash
curl -s -X POST http://127.0.0.1:8000/run \
  -H "Content-Type: application/json" \
  -d '{"timezone": "Mars/Olympus_Mons"}'
```

*Expected Response: `{"detail":"ValueError: Invalid timezone: 'Mars/Olympus_Mons'"}`* 