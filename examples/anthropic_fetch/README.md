# Fetch HTML Skillet Example

This example demonstrates a basic Skillet skill that fetches HTML content from URLs, with options for markdown conversion and pagination. It's a Skillet-compatible implementation of the Anthropic fetch MCP.

## 🔐 **Credential Requirements**

✅ **No credentials required!** This skill works with public URLs without any API keys or configuration.

This makes it perfect for:
- Testing and learning Skillet concepts
- Fetching content from public websites
- Development environments without credential management
- Web scraping and content analysis tasks

## Quick Start

You'll need two terminal windows to run and test this skill:

### Terminal 1: Start the Server

```bash
# Make sure you're in the right directory
cd examples/anthropic_fetch

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
cd examples/anthropic_fetch

# Run the automated tests
./test.sh
```

A successful test run will show:
```
--- Testing Fetch HTML Skillet ---
1. Fetching raw HTML...
{"html":"<!DOCTYPE html>\n<html>\n  <head>\n  </head>\n  <body>\n      <h1>Herman Melville - Moby-Dick</h1>...",...}

2. Fetching as Markdown...
{"html":null,"markdown":"Herman Melville - Moby-Dick\n===========================",...}

3. Fetching with a start_index of 1500...
{"html":"had finally given in; and so it came to pass...",...}
```

## API Usage

You can also test individual endpoints manually using curl commands by making POST requests to the `/run` endpoint:

### 1. Basic HTML Fetch
```bash
curl -s -X POST http://127.0.0.1:8000/run \
  -H "Content-Type: application/json" \
  -d '{"url": "https://httpbin.org/html"}'
```

Response:
```json
{
  "html": "<!DOCTYPE html>\n<html>\n  <head>\n  </head>\n  <body>\n      <h1>Herman Melville - Moby-Dick</h1>\n\n      <div>\n        <p>\n          Availing himself of the mild, summer-cool weather...",
  "markdown": null
}
```

### Convert to Markdown
```bash
curl -s -X POST http://127.0.0.1:8000/run \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://httpbin.org/html",
    "as_markdown": true
  }'
```

Response:
```json
{
  "html": null,
  "markdown": "Herman Melville - Moby-Dick\n===========================\n\nAvailing himself of the mild, summer-cool weather..."
}
```

### Pagination Support
```bash
curl -s -X POST http://127.0.0.1:8000/run \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://httpbin.org/html",
    "start_index": 1500
  }'
```

Response (starts mid-story):
```json
{
  "html": null,
  "markdown": "had finally given in; and so it came to pass that every one now knew the shameful story of his wretched fate..."
}
```

## Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| url | string | Yes | The fully-qualified http(s) URL to fetch |
| as_markdown | boolean | No | Convert HTML to Markdown format |
| start_index | integer | No | Starting character index for pagination |

## Response Format

The response will always contain both `html` and `markdown` fields, with one being null depending on the `as_markdown` parameter:

```json
{
  "html": "<!DOCTYPE html>...",
  "markdown": null
}
```

or with markdown:
```json
{
  "html": null,
  "markdown": "# Page Title\n\nContent..."
}
```

## Limitations

- HTML content is truncated to 10,000 characters
- Only public URLs are supported (no authentication)

## Test URL

This example uses https://httpbin.org/html as a test endpoint, which returns a static HTML page containing an excerpt from Herman Melville's Moby-Dick. This endpoint is perfect for testing as it:
- Is publicly accessible
- Returns consistent content
- Contains enough text to demonstrate pagination
- Has proper HTML structure for markdown conversion 