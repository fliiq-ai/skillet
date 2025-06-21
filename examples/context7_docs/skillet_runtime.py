"""
Context7 Docs Skillet - Enhanced Runtime with Credential Injection Support

This runtime provides TWO endpoints to support different use cases:

1. /docs (Legacy) - Backward compatibility for existing users
   - Uses simple DocsRequest format
   - Reads credentials from environment variables only
   - Preserves existing integrations without breaking changes

2. /run (Enhanced) - Modern endpoint for production deployments
   - Supports both simple and enhanced request formats
   - Enables runtime credential injection from frontend applications
   - Compatible with Fliiq and multi-skill host architecture
   - Follows standard Skillet patterns

Both endpoints use the same underlying documentation logic, ensuring consistent behavior.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import json
from typing import Optional, Dict, Any, Union
from contextlib import contextmanager
import re
import os

app = FastAPI(
    title="Context7 Docs Skillet", 
    description="Retrieve up-to-date documentation - Enhanced with credential injection support",
    version="2.0.0"
)

# ═══════════════════════════════════════════════════════════════════
# REQUEST/RESPONSE MODELS
# ═══════════════════════════════════════════════════════════════════

class DocsRequest(BaseModel):
    """Legacy request model - preserved for backward compatibility with /docs endpoint"""
    query: str
    library: Optional[str] = None
    version: Optional[str] = "latest"
    max_results: Optional[int] = 5

class EnhancedDocsRequest(BaseModel):
    """Enhanced request model supporting credential injection for /run endpoint"""
    skill_input: Dict[str, Any]  # Contains: query, library, version, max_results
    credentials: Optional[Dict[str, str]] = None
    runtime_config: Optional[Dict[str, Any]] = None

class DocsResponse(BaseModel):
    """Response model used by both endpoints"""
    documentation: str
    source_url: str
    library_info: Dict[str, Any]
    results_count: int

# ═══════════════════════════════════════════════════════════════════
# CREDENTIAL INJECTION UTILITIES
# ═══════════════════════════════════════════════════════════════════

@contextmanager
def temp_env_context(credentials: Optional[Dict[str, str]] = None):
    """
    Context manager to temporarily inject environment variables.
    
    This allows credentials to be provided at request-time without
    storing them on the server or modifying the global environment.
    
    Args:
        credentials: Dict of environment variable names and values
    """
    if not credentials:
        yield
        return
    
    # Store original values to restore later
    original_values = {}
    for key, value in credentials.items():
        original_values[key] = os.environ.get(key)
        os.environ[key] = value
    
    try:
        yield
    finally:
        # Restore original environment state
        for key, original_value in original_values.items():
            if original_value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = original_value

# ═══════════════════════════════════════════════════════════════════
# DOCUMENTATION DATABASE
# ═══════════════════════════════════════════════════════════════════

# Mock documentation database - in a real implementation, this would connect to Context7's API
MOCK_DOCS_DB = {
    "react": {
        "latest": {
            "hooks": {
                "content": """# React Hooks

React Hooks are functions that let you use state and other React features in functional components.

## useState
```javascript
import { useState } from 'react';

function Counter() {
  const [count, setCount] = useState(0);
  return (
    <div>
      <p>You clicked {count} times</p>
      <button onClick={() => setCount(count + 1)}>
        Click me
      </button>
    </div>
  );
}
```

## useEffect
```javascript
import { useEffect, useState } from 'react';

function Example() {
  const [count, setCount] = useState(0);

  useEffect(() => {
    document.title = `You clicked ${count} times`;
  });

  return (
    <div>
      <p>You clicked {count} times</p>
      <button onClick={() => setCount(count + 1)}>
        Click me
      </button>
    </div>
  );
}
```""",
                "url": "https://react.dev/reference/react/hooks"
            },
            "components": {
                "content": """# React Components

Components are the building blocks of React applications.

## Function Components
```javascript
function Welcome(props) {
  return <h1>Hello, {props.name}</h1>;
}
```

## Class Components
```javascript
class Welcome extends React.Component {
  render() {
    return <h1>Hello, {this.props.name}</h1>;
  }
}
```""",
                "url": "https://react.dev/learn/your-first-component"
            }
        }
    },
    "nextjs": {
        "latest": {
            "app-router": {
                "content": """# Next.js App Router

The App Router is a new paradigm for building applications using React's latest features.

## File-based Routing
```
app/
  layout.js
  page.js
  dashboard/
    page.js
    settings/
      page.js
```

## Creating Routes
```javascript
// app/page.js
export default function Page() {
  return <h1>Hello, Next.js!</h1>
}

// app/dashboard/page.js
export default function Dashboard() {
  return <h1>Dashboard</h1>
}
```

## Layouts
```javascript
// app/layout.js
export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
```""",
                "url": "https://nextjs.org/docs/app"
            }
        }
    },
    "fastapi": {
        "latest": {
            "getting-started": {
                "content": """# FastAPI Getting Started

FastAPI is a modern, fast web framework for building APIs with Python.

## Installation
```bash
pip install fastapi uvicorn
```

## First Steps
```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}
```

## Run the server
```bash
uvicorn main:app --reload
```""",
                "url": "https://fastapi.tiangolo.com/tutorial/first-steps/"
            }
        }
    }
}

# ═══════════════════════════════════════════════════════════════════
# CORE DOCUMENTATION LOGIC
# ═══════════════════════════════════════════════════════════════════

def search_documentation(query: str, library: Optional[str] = None, version: str = "latest", max_results: int = 5) -> Dict[str, Any]:
    """Search for documentation based on query"""
    
    results = []
    
    # If library is specified, search within that library
    if library and library.lower() in MOCK_DOCS_DB:
        lib_data = MOCK_DOCS_DB[library.lower()]
        if version in lib_data:
            version_data = lib_data[version]
            for topic, doc_data in version_data.items():
                if query.lower() in topic.lower() or query.lower() in doc_data["content"].lower():
                    results.append({
                        "library": library,
                        "topic": topic,
                        "content": doc_data["content"],
                        "url": doc_data["url"],
                        "relevance": calculate_relevance(query, doc_data["content"])
                    })
    else:
        # Search across all libraries
        for lib_name, lib_data in MOCK_DOCS_DB.items():
            if version in lib_data:
                version_data = lib_data[version]
                for topic, doc_data in version_data.items():
                    if query.lower() in topic.lower() or query.lower() in doc_data["content"].lower():
                        results.append({
                            "library": lib_name,
                            "topic": topic,
                            "content": doc_data["content"],
                            "url": doc_data["url"],
                            "relevance": calculate_relevance(query, doc_data["content"])
                        })
    
    # Sort by relevance and limit results
    results.sort(key=lambda x: x["relevance"], reverse=True)
    return results[:max_results]

def calculate_relevance(query: str, content: str) -> float:
    """Calculate relevance score for search results"""
    query_words = query.lower().split()
    content_lower = content.lower()
    
    score = 0
    for word in query_words:
        # Count occurrences of each query word
        score += content_lower.count(word)
    
    return score

def format_documentation(results: list) -> str:
    """Format search results into readable documentation"""
    if not results:
        return "No documentation found for the given query."
    
    formatted_docs = []
    for result in results:
        formatted_docs.append(f"""
## {result['library'].title()} - {result['topic'].title()}

{result['content']}

**Source:** {result['url']}
""")
    
    return "\n".join(formatted_docs)

def execute_docs_logic(query: str, library: Optional[str] = None, version: str = "latest", max_results: int = 5) -> DocsResponse:
    """
    Core documentation logic used by both legacy and enhanced endpoints.
    
    This function contains the actual documentation search and is called by both
    the legacy and enhanced endpoints to ensure consistent behavior.
    """
    if not query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    # Search for documentation
    results = search_documentation(query, library, version, max_results)
    
    if not results:
        return DocsResponse(
            documentation="No documentation found for the given query. Try different keywords or check the library name.",
            source_url="",
            library_info={"query": query, "library": library},
            results_count=0
        )
    
    # Format documentation
    formatted_docs = format_documentation(results)
    
    # Get primary source URL (from first result)
    primary_url = results[0]["url"] if results else ""
    
    # Create library info
    library_info = {
        "query": query,
        "library": library or "multiple",
        "version": version,
        "topics_found": [r["topic"] for r in results]
    }
    
    return DocsResponse(
        documentation=formatted_docs,
        source_url=primary_url,
        library_info=library_info,
        results_count=len(results)
    )

# ═══════════════════════════════════════════════════════════════════
# API ENDPOINTS
# ═══════════════════════════════════════════════════════════════════

@app.post("/docs", response_model=DocsResponse)
async def get_documentation_legacy(request: DocsRequest):
    """
    LEGACY ENDPOINT: Preserved for backward compatibility
    
    This endpoint maintains the original API contract for existing integrations.
    It uses environment variables only and the simple request format.
    
    Features:
    - Original request/response format
    - Environment variable credentials only
    - Backward compatible with existing code
    - No breaking changes for current users
    """
    return execute_docs_logic(
        request.query, 
        request.library, 
        request.version, 
        request.max_results
    )

@app.post("/run", response_model=DocsResponse)
async def run_enhanced(request: Union[DocsRequest, EnhancedDocsRequest]):
    """
    ENHANCED ENDPOINT: Modern production-ready endpoint
    
    This is the primary endpoint for new integrations and production deployments.
    It supports both simple and enhanced request formats for maximum flexibility.
    
    Features:
    - Runtime credential injection (perfect for Fliiq integration)
    - Backward compatible with simple format
    - Follows standard Skillet patterns
    - Compatible with multi-skill host architecture
    
    Request Format Options:
    
    1. Simple (same as /docs):
       {"query": "react hooks", "library": "react"}
    
    2. Enhanced (with credentials):
       {
         "skill_input": {"query": "react hooks", "library": "react"},
         "credentials": {"CONTEXT7_API_KEY": "..."}
       }
    """
    
    if isinstance(request, EnhancedDocsRequest):
        # Enhanced format: Extract credentials and inject them temporarily
        credentials = None
        if request.runtime_config and "credentials" in request.runtime_config:
            credentials = request.runtime_config["credentials"]
        elif request.credentials:
            credentials = request.credentials
        
        # Extract skill parameters from nested structure
        skill_input = request.skill_input
        query = skill_input.get("query", "")
        library = skill_input.get("library")
        version = skill_input.get("version", "latest")
        max_results = skill_input.get("max_results", 5)
        
        # Execute with credential injection
        with temp_env_context(credentials):
            return execute_docs_logic(query, library, version, max_results)
    
    else:
        # Simple format: Direct execution (same as /docs endpoint)
        return execute_docs_logic(
            request.query, 
            request.library, 
            request.version, 
            request.max_results
        )

# ═══════════════════════════════════════════════════════════════════
# UTILITY ENDPOINTS
# ═══════════════════════════════════════════════════════════════════

@app.get("/libraries")
async def list_libraries():
    """List available libraries in the documentation database"""
    return {
        "libraries": list(MOCK_DOCS_DB.keys()),
        "total": len(MOCK_DOCS_DB)
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "available_libraries": len(MOCK_DOCS_DB),
        "service": "context7_docs_enhanced",
        "supports_credential_injection": True
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

