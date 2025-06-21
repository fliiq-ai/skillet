# Context7 Docs Skillet

A Skillet skill that retrieves up-to-date documentation for libraries and frameworks, inspired by the Context7 MCP server.

**Original MCP:** [Context7](https://github.com/upstash/context7)
- **Description:** Retrieve up-to-date documentation for libraries and frameworks
- **Features:** Smart documentation search, library-specific queries, relevance ranking
- **API:** `/docs` endpoint for documentation retrieval

## 🔐 **Credential Requirements**

✅ **Currently no credentials required!** This skill uses mock documentation data for demonstration.

**For production use, you would need:**
- **`CONTEXT7_API_KEY`** - API key for Context7 documentation service
- **`CONTEXT7_API_HOST`** - API endpoint (optional)

This makes the current version perfect for:
- Testing and learning Skillet concepts
- Development environments
- Understanding documentation search patterns
- Prototyping documentation-aware applications

## Description

This skill provides intelligent documentation retrieval for popular libraries and frameworks. It searches through documentation databases to find relevant code examples, API references, and usage guides based on your queries.

## Features

- **Smart Documentation Search**: Find relevant docs based on natural language queries
- **Library-Specific Search**: Target specific libraries or search across all available docs
- **Version Support**: Retrieve documentation for specific versions
- **Relevance Ranking**: Results are ranked by relevance to your query
- **Code Examples**: Includes practical code examples and usage patterns

## API Endpoints

### POST /docs
Retrieve documentation based on query.

**Request Body:**
```json
{
    "query": "react hooks",
    "library": "react",
    "version": "latest",
    "max_results": 5
}
```

**Response:**
```json
{
    "documentation": "# React Hooks\n\nReact Hooks are functions...",
    "source_url": "https://react.dev/reference/react/hooks",
    "library_info": {
        "query": "react hooks",
        "library": "react",
        "version": "latest",
        "topics_found": ["hooks"]
    },
    "results_count": 1
}
```

### GET /libraries
List available libraries in the documentation database.

**Response:**
```json
{
    "libraries": ["react", "nextjs", "fastapi"],
    "total": 3
}
```

### GET /health
Health check endpoint.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Start the server:
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
- List available libraries
- Test documentation retrieval for various libraries
- Test general search functionality
- Test error handling

## Supported Libraries

Currently includes mock documentation for:

- **React**: Hooks, components, state management
- **Next.js**: App router, routing, layouts
- **FastAPI**: Getting started, API development

## Query Examples

### Library-Specific Queries
```bash
# React hooks documentation
curl -X POST "http://localhost:8000/docs" \
    -H "Content-Type: application/json" \
    -d '{"query": "useState useEffect", "library": "react"}'

# Next.js routing
curl -X POST "http://localhost:8000/docs" \
    -H "Content-Type: application/json" \
    -d '{"query": "app router", "library": "nextjs"}'
```

### General Queries
```bash
# Search across all libraries
curl -X POST "http://localhost:8000/docs" \
    -H "Content-Type: application/json" \
    -d '{"query": "components", "max_results": 10}'
```

## Parameters

- **query**: Search query (required)
- **library**: Specific library name (optional)
- **version**: Library version (default: "latest")
- **max_results**: Maximum results to return (default: 5)

## Implementation Notes

This is a simplified implementation that demonstrates the Context7 concept using a mock documentation database. In a production environment, this would:

1. Connect to real documentation sources
2. Use advanced search algorithms
3. Support more libraries and frameworks
4. Provide real-time documentation updates
5. Include more sophisticated relevance ranking

## Extending the Database

To add more libraries or documentation, modify the `MOCK_DOCS_DB` dictionary in `skillet_runtime.py`:

```python
MOCK_DOCS_DB["your-library"] = {
    "latest": {
        "topic-name": {
            "content": "Documentation content...",
            "url": "https://docs.example.com"
        }
    }
}
```

