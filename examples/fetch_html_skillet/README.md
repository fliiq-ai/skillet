# Fetch HTML Skillet Example

This example demonstrates a basic Skillet skill that fetches HTML content from URLs, with options for markdown conversion and pagination. It's a Skillet-compatible implementation of the Anthropic fetch MCP.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Start the server
uvicorn skillet_runtime:app --reload
```

## API Usage

The skill exposes a single endpoint `/run` that accepts POST requests with the following options:

### Basic HTML Fetch
```bash
curl -X POST http://127.0.0.1:8000/run \
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
curl -X POST http://127.0.0.1:8000/run \
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
curl -X POST http://127.0.0.1:8000/run \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://httpbin.org/html",
    "start_index": 1500,
    "as_markdown": true
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