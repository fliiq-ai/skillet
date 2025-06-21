# Playwright Navigate Skillet

A Skillet skill that navigates to web pages using Playwright browser automation with customizable viewport settings and wait conditions.

## 🔐 **Credential Requirements**

✅ **No credentials required!** This skill uses local browser automation without any external APIs.

This makes it perfect for:
- Testing and learning Skillet concepts
- Local web scraping and automation
- UI testing and page navigation
- Development environments without credential management

Note: This skill does require Playwright to be installed, but no API keys or authentication.

## Description

This skill enables automated web navigation using Playwright, allowing you to programmatically visit web pages, handle redirects, and gather page information. It's perfect for web scraping, testing, and automated browsing tasks.

## Features

- **Reliable Navigation**: Uses Playwright for robust web page navigation
- **Multiple Wait Conditions**: Support for different page load states
- **Custom Viewport**: Configurable browser viewport dimensions
- **User Agent Control**: Set custom user agent strings
- **Redirect Handling**: Automatically follows redirects
- **Performance Metrics**: Measures page load times
- **Error Handling**: Graceful handling of navigation failures

## API Endpoints

### POST /navigate
Navigate to a web page.

**Request Body:**
```json
{
    "url": "https://example.com",
    "wait_for": "load",
    "timeout": 30000,
    "user_agent": "Custom-Agent/1.0",
    "viewport_width": 1280,
    "viewport_height": 720
}
```

**Response:**
```json
{
    "success": true,
    "final_url": "https://example.com/",
    "title": "Example Domain",
    "status_code": 200,
    "load_time": 1.234
}
```

### GET /browsers
List available browsers.

**Response:**
```json
{
    "browsers": [
        {"name": "chromium", "description": "Chromium browser (default)"},
        {"name": "firefox", "description": "Firefox browser"},
        {"name": "webkit", "description": "WebKit browser (Safari)"}
    ],
    "default": "chromium"
}
```

### GET /health
Health check endpoint.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Install Playwright browsers:
```bash
playwright install
```

3. Start the server:
```bash
uvicorn skillet_runtime:app --reload
```

## Testing

Run the test script to verify functionality:
```bash
./test.sh
```

The test script will:
- Check server health
- List available browsers
- Test basic navigation
- Test custom viewport and user agent
- Test redirect handling
- Test error handling

## Parameters

- **url**: Target URL (required)
- **wait_for**: Wait condition - "load", "domcontentloaded", or "networkidle" (default: "load")
- **timeout**: Navigation timeout in milliseconds (default: 30000)
- **user_agent**: Custom user agent string (optional)
- **viewport_width**: Browser viewport width (default: 1280)
- **viewport_height**: Browser viewport height (default: 720)

## Wait Conditions

- **load**: Wait for the load event (default)
- **domcontentloaded**: Wait for DOMContentLoaded event
- **networkidle**: Wait for no network requests for 500ms

## Example Usage

```bash
# Basic navigation
curl -X POST "http://localhost:8000/navigate" \
    -H "Content-Type: application/json" \
    -d '{"url": "https://example.com"}'

# Navigation with custom settings
curl -X POST "http://localhost:8000/navigate" \
    -H "Content-Type: application/json" \
    -d '{
        "url": "https://example.com",
        "wait_for": "networkidle",
        "viewport_width": 1920,
        "viewport_height": 1080,
        "user_agent": "MyBot/1.0"
    }'

# Quick navigation (DOM ready)
curl -X POST "http://localhost:8000/navigate" \
    -H "Content-Type: application/json" \
    -d '{
        "url": "https://example.com",
        "wait_for": "domcontentloaded",
        "timeout": 10000
    }'
```

## Response Fields

- **success**: Whether navigation completed successfully
- **final_url**: Final URL (may differ from input due to redirects)
- **title**: Page title
- **status_code**: HTTP response status code
- **load_time**: Time taken to load the page (seconds)

## Error Handling

The skill handles various error conditions gracefully:

- Invalid URLs return 400 Bad Request
- Network timeouts return success=false with timing info
- Non-existent domains return success=false
- Invalid wait conditions return 400 Bad Request

## Browser Support

Currently uses Chromium browser by default. The skill can be extended to support:

- Firefox
- WebKit (Safari)
- Custom browser configurations

## Use Cases

- **Web Scraping**: Navigate to pages before extracting content
- **Testing**: Verify page loads and redirects
- **Monitoring**: Check website availability and performance
- **Automation**: Part of larger web automation workflows

