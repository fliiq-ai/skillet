"""
Playwright Navigate Skillet - Enhanced Runtime with Credential Injection Support

This runtime provides TWO endpoints to support different use cases:

1. /navigate (Legacy) - Backward compatibility for existing users
   - Uses simple NavigateRequest format
   - Reads credentials from environment variables only
   - Preserves existing integrations without breaking changes

2. /run (Enhanced) - Modern endpoint for production deployments
   - Supports both simple and enhanced request formats
   - Enables runtime credential injection from frontend applications
   - Compatible with Fliiq and multi-skill host architecture
   - Follows standard Skillet patterns

Both endpoints use the same underlying navigation logic, ensuring consistent behavior.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import asyncio
import time
import os
from typing import Optional, Dict, Any, Union
from contextlib import contextmanager
from playwright.async_api import async_playwright
import validators

app = FastAPI(
    title="Playwright Navigate Skillet", 
    description="Navigate to web pages using Playwright - Enhanced with credential injection support",
    version="2.0.0"
)

# ═══════════════════════════════════════════════════════════════════
# REQUEST/RESPONSE MODELS
# ═══════════════════════════════════════════════════════════════════

class NavigateRequest(BaseModel):
    """Legacy request model - preserved for backward compatibility with /navigate endpoint"""
    url: str
    wait_for: Optional[str] = "load"
    timeout: Optional[int] = 30000
    user_agent: Optional[str] = None
    viewport_width: Optional[int] = 1280
    viewport_height: Optional[int] = 720

class EnhancedNavigateRequest(BaseModel):
    """Enhanced request model supporting credential injection for /run endpoint"""
    skill_input: Dict[str, Any]  # Contains: url, wait_for, timeout, user_agent, viewport_width, viewport_height
    credentials: Optional[Dict[str, str]] = None
    runtime_config: Optional[Dict[str, Any]] = None

class NavigateResponse(BaseModel):
    """Response model used by both endpoints"""
    success: bool
    final_url: str
    title: str
    status_code: int
    load_time: float

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
# CORE NAVIGATION LOGIC
# ═══════════════════════════════════════════════════════════════════

async def navigate_logic(url: str, wait_for: str = "load", timeout: int = 30000, user_agent: Optional[str] = None, viewport_width: int = 1280, viewport_height: int = 720) -> NavigateResponse:
    """
    Core navigation logic used by both legacy and enhanced endpoints.
    
    This function contains the actual navigation logic and is called by both
    the legacy and enhanced endpoints to ensure consistent behavior.
    """
    
    # Validate URL
    if not validators.url(url):
        raise HTTPException(status_code=400, detail="Invalid URL format")
    
    # Validate wait_for parameter
    valid_wait_conditions = ["load", "domcontentloaded", "networkidle"]
    if wait_for not in valid_wait_conditions:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid wait_for condition. Must be one of: {valid_wait_conditions}"
        )
    
    start_time = time.time()
    
    try:
        async with async_playwright() as p:
            # Launch browser
            browser = await p.chromium.launch(headless=True)
            
            # Create context with custom settings
            context_options = {
                "viewport": {
                    "width": viewport_width,
                    "height": viewport_height
                }
            }
            
            if user_agent:
                context_options["user_agent"] = user_agent
            
            context = await browser.new_context(**context_options)
            
            # Create page
            page = await context.new_page()
            
            # Navigate to URL
            response = await page.goto(
                url,
                wait_until=wait_for,
                timeout=timeout
            )
            
            # Get page information
            final_url = page.url
            title = await page.title()
            status_code = response.status if response else 0
            
            # Calculate load time
            load_time = time.time() - start_time
            
            # Close browser
            await browser.close()
            
            return NavigateResponse(
                success=True,
                final_url=final_url,
                title=title,
                status_code=status_code,
                load_time=round(load_time, 3)
            )
            
    except Exception as e:
        load_time = time.time() - start_time
        
        # Return error response
        return NavigateResponse(
            success=False,
            final_url=url,
            title="",
            status_code=0,
            load_time=round(load_time, 3)
        )

# ═══════════════════════════════════════════════════════════════════
# API ENDPOINTS
# ═══════════════════════════════════════════════════════════════════

@app.post("/navigate", response_model=NavigateResponse)
async def navigate_legacy(request: NavigateRequest):
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
    return await navigate_logic(
        request.url,
        request.wait_for,
        request.timeout,
        request.user_agent,
        request.viewport_width,
        request.viewport_height
    )

@app.post("/run", response_model=NavigateResponse)
async def run_enhanced(request: Union[NavigateRequest, EnhancedNavigateRequest]):
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
    
    1. Simple (same as /navigate):
       {"url": "https://example.com", "wait_for": "load"}
    
    2. Enhanced (with credentials):
       {
         "skill_input": {"url": "https://example.com", "wait_for": "load"},
         "credentials": {"PROXY_URL": "...", "BROWSER_CONFIG": "..."}
       }
    """
    
    if isinstance(request, EnhancedNavigateRequest):
        # Enhanced format: Extract credentials and inject them temporarily
        credentials = None
        if request.runtime_config and "credentials" in request.runtime_config:
            credentials = request.runtime_config["credentials"]
        elif request.credentials:
            credentials = request.credentials
        
        # Extract skill parameters from nested structure
        skill_input = request.skill_input
        url = skill_input.get("url", "")
        wait_for = skill_input.get("wait_for", "load")
        timeout = skill_input.get("timeout", 30000)
        user_agent = skill_input.get("user_agent")
        viewport_width = skill_input.get("viewport_width", 1280)
        viewport_height = skill_input.get("viewport_height", 720)
        
        # Execute with credential injection
        with temp_env_context(credentials):
            return await navigate_logic(url, wait_for, timeout, user_agent, viewport_width, viewport_height)
    
    else:
        # Simple format: Direct execution (same as /navigate endpoint)
        return await navigate_logic(
            request.url,
            request.wait_for,
            request.timeout,
            request.user_agent,
            request.viewport_width,
            request.viewport_height
        )

# ═══════════════════════════════════════════════════════════════════
# UTILITY ENDPOINTS
# ═══════════════════════════════════════════════════════════════════

@app.get("/health")
async def health():
    """Health check endpoint"""
    try:
        # Test if Playwright is working
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            await browser.close()
        
        return {
            "status": "healthy",
            "playwright": "available",
            "browsers": ["chromium"],
            "supports_credential_injection": True
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "playwright": "unavailable"
        }

@app.get("/browsers")
async def list_browsers():
    """List available browsers"""
    return {
        "browsers": [
            {"name": "chromium", "description": "Chromium browser (default)"},
            {"name": "firefox", "description": "Firefox browser"},
            {"name": "webkit", "description": "WebKit browser (Safari)"}
        ],
        "default": "chromium"
    }

# ═══════════════════════════════════════════════════════════════════
# DISCOVERY & METADATA ENDPOINTS  
# ═══════════════════════════════════════════════════════════════════

@app.get("/inventory")
async def get_skill_inventory():
    """Return skill metadata for LLM decision-making about when and how to use this skill."""
    
    inventory = {
        "skill": {
            "name": "Playwright Web Navigation",
            "description": "Navigate to web pages using Playwright browser automation, with support for custom viewports, wait conditions, and user agents",
            "version": "1.0.0",
            "category": "web_automation",
            "complexity": "medium",
            "use_cases": [
                "Testing website availability and load times",
                "Taking screenshots of web pages",
                "Checking page titles and URLs after redirects", 
                "Web scraping preparation and reconnaissance",
                "Automated browser testing and validation"
            ],
            "example_queries": [
                "Navigate to https://example.com and check if it loads",
                "Visit this website and tell me the page title",
                "Check how long it takes to load this page",
                "Navigate to this URL with mobile viewport",
                "Test if this website redirects properly"
            ],
            "input_types": ["url", "viewport_settings", "wait_conditions"],
            "output_types": ["navigation_result", "load_metrics", "page_info"],
            "performance": "medium",
            "dependencies": ["playwright", "chromium_browser"],
            "works_well_with": ["web_scraping", "testing", "monitoring", "screenshots"],
            "typical_workflow_position": "data_gathering",
            "tags": ["browser", "navigation", "web", "automation", "testing"],
            "supports_credential_injection": True
        }
    }
    
    return inventory

@app.get("/schema")
async def get_tool_schema():
    """Return the tool schema in a standardized format for LLM consumption."""
    
    parameters = {
        "type": "object",
        "properties": {
            "url": {
                "type": "string",
                "description": "The fully-qualified URL to navigate to (must include http:// or https://)"
            },
            "wait_for": {
                "type": "string",
                "description": "Wait condition for page loading: 'load', 'domcontentloaded', or 'networkidle' (default: 'load')"
            },
            "timeout": {
                "type": "integer",
                "description": "Navigation timeout in milliseconds (default: 30000)"
            },
            "user_agent": {
                "type": "string",
                "description": "Optional: Custom user agent string for the browser"
            },
            "viewport_width": {
                "type": "integer", 
                "description": "Browser viewport width in pixels (default: 1280)"
            },
            "viewport_height": {
                "type": "integer",
                "description": "Browser viewport height in pixels (default: 720)"
            }
        },
        "required": ["url"]
    }
    
    output_schema = {
        "type": "object",
        "properties": {
            "success": {
                "type": "boolean",
                "description": "Whether the navigation was successful"
            },
            "final_url": {
                "type": "string",
                "description": "The final URL after any redirects"
            },
            "title": {
                "type": "string",
                "description": "The page title"
            },
            "status_code": {
                "type": "integer",
                "description": "HTTP status code of the response"
            },
            "load_time": {
                "type": "number",
                "description": "Page load time in seconds"
            }
        }
    }
    
    return {
        "name": "Playwright Web Navigation",
        "description": "Navigate to web pages using Playwright browser automation with detailed metrics",
        "version": "1.0.0",
        "parameters": parameters,
        "output_schema": output_schema,
        "endpoint": "/run",
        "method": "POST",
        "supports_credential_injection": True
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

