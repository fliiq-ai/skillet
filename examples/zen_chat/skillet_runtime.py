"""
Zen Chat Skillet - Enhanced Runtime with Credential Injection Support

This runtime provides TWO endpoints to support different use cases:

1. /chat (Legacy) - Backward compatibility for existing users
   - Uses simple request format
   - Reads credentials from environment variables only
   - Preserves existing integrations without breaking changes

2. /run (Enhanced) - Modern endpoint for production deployments
   - Supports both simple and enhanced request formats
   - Enables runtime credential injection from frontend applications
   - Compatible with Fliiq and multi-skill host architecture
   - Follows standard Skillet patterns

Both endpoints use the same underlying chat logic, ensuring consistent behavior.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import os
import json
from typing import Optional, Dict, Any, Union
from contextlib import contextmanager

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

app = FastAPI(
    title="Zen Chat Skillet", 
    description="Collaborative thinking with AI models - Enhanced with credential injection support",
    version="2.0.0"
)

# ═══════════════════════════════════════════════════════════════════
# REQUEST/RESPONSE MODELS
# ═══════════════════════════════════════════════════════════════════

class ChatRequest(BaseModel):
    """Legacy request model - preserved for backward compatibility with /chat endpoint"""
    prompt: str
    model: Optional[str] = "auto"
    max_tokens: Optional[int] = 1000

class EnhancedChatRequest(BaseModel):
    """Enhanced request model supporting credential injection for /run endpoint"""
    skill_input: Dict[str, Any]  # Contains: prompt, model, max_tokens
    credentials: Optional[Dict[str, str]] = None
    runtime_config: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    """Response model used by both endpoints"""
    response: str
    model_used: str
    reasoning: str

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
# AI MODEL INTEGRATION
# ═══════════════════════════════════════════════════════════════════

def get_available_models():
    """Check which AI models are available based on current API keys"""
    available = []
    
    if GEMINI_AVAILABLE and os.getenv("GEMINI_API_KEY"):
        available.append("gemini")
    if OPENAI_AVAILABLE and os.getenv("OPENAI_API_KEY"):
        available.append("openai")
    
    return available

def choose_model(preferred_model: str, available_models: list) -> tuple[str, str]:
    """Choose the best model based on preference and availability"""
    
    if preferred_model != "auto" and preferred_model in available_models:
        return preferred_model, f"User requested {preferred_model}"
    
    if "gemini" in available_models:
        return "gemini", "Gemini chosen for extended reasoning capabilities"
    elif "openai" in available_models:
        return "openai", "OpenAI chosen as fallback option"
    else:
        raise HTTPException(status_code=500, detail="No AI models available. Please configure API keys.")

def call_gemini(prompt: str, max_tokens: int) -> str:
    """Call Gemini API with fallback model support"""
    if not GEMINI_AVAILABLE:
        raise HTTPException(status_code=500, detail="Gemini library not available")
    
    try:
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        
        # Try multiple model names for compatibility
        model_names = ['gemini-2.0-flash', 'gemini-1.5-flash', 'gemini-pro']
        
        for model_name in model_names:
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        max_output_tokens=max_tokens,
                        temperature=0.7,
                    )
                )
                return response.text
            except Exception as model_error:
                print(f"Failed to use model {model_name}: {model_error}")
                continue
        
        # If all models fail, raise the last error
        raise HTTPException(status_code=500, detail="All Gemini models failed to respond")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gemini API error: {str(e)}")

def call_openai(prompt: str, max_tokens: int) -> str:
    """Call OpenAI API"""
    if not OPENAI_AVAILABLE:
        raise HTTPException(status_code=500, detail="OpenAI library not available")
    
    try:
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=0.7
        )
        
        return response.choices[0].message.content
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI API error: {str(e)}")

# ═══════════════════════════════════════════════════════════════════
# CORE CHAT LOGIC
# ═══════════════════════════════════════════════════════════════════

def execute_chat_logic(prompt: str, model: str = "auto", max_tokens: int = 1000) -> ChatResponse:
    """
    Core chat logic used by both legacy and enhanced endpoints.
    
    This function contains the actual chat execution and is called by both
    the legacy and enhanced endpoints to ensure consistent behavior.
    """
    if not prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")
    
    available_models = get_available_models()
    
    if not available_models:
        raise HTTPException(
            status_code=500, 
            detail={
                "error": "No AI models available - missing required credentials",
                "message": "No API keys found for OpenAI or Gemini models",
                "required_credentials": ["OPENAI_API_KEY", "GEMINI_API_KEY"],
                "how_to_get": {
                    "OPENAI_API_KEY": {
                        "url": "https://platform.openai.com/api-keys",
                        "steps": [
                            "1. Go to https://platform.openai.com/api-keys",
                            "2. Create a new API key",
                            "3. Copy the key (starts with 'sk-')",
                            "4. Set OPENAI_API_KEY environment variable"
                        ]
                    },
                    "GEMINI_API_KEY": {
                        "url": "https://makersuite.google.com/app/apikey",
                        "steps": [
                            "1. Go to https://makersuite.google.com/app/apikey",
                            "2. Create a new API key",
                            "3. Copy the key (starts with 'AIza')",
                            "4. Set GEMINI_API_KEY environment variable"
                        ]
                    }
                },
                "note": "You need at least one of these API keys for the skill to work"
            }
        )
    
    # Determine which model to use
    selected_model = None
    reasoning = ""
    
    if model in ["openai", "gpt"]:
        if "openai" in available_models:
            selected_model = "openai"
            reasoning = "OpenAI model requested and available"
        else:
            raise HTTPException(
                status_code=400, 
                detail={
                    "error": "OpenAI model requested but not available",
                    "message": "OPENAI_API_KEY not found or invalid",
                    "required_credentials": ["OPENAI_API_KEY"],
                    "how_to_get": "Get your OpenAI API key from: https://platform.openai.com/api-keys",
                    "available_models": available_models
                }
            )
    elif model == "gemini":
        if "gemini" in available_models:
            selected_model = "gemini"
            reasoning = "Gemini model requested and available"
        else:
            raise HTTPException(
                status_code=400, 
                detail={
                    "error": "Gemini model requested but not available",
                    "message": "GEMINI_API_KEY not found or invalid",
                    "required_credentials": ["GEMINI_API_KEY"],
                    "how_to_get": "Get your Gemini API key from: https://makersuite.google.com/app/apikey",
                    "available_models": available_models
                }
            )
    else:  # auto selection
        if "gemini" in available_models:
            selected_model = "gemini"
            reasoning = "Gemini chosen for extended reasoning capabilities"
        elif "openai" in available_models:
            selected_model = "openai"
            reasoning = "OpenAI chosen as Gemini unavailable"
    
    # Execute the request
    if selected_model == "openai":
        response_text = call_openai(prompt, max_tokens)
    elif selected_model == "gemini":
        response_text = call_gemini(prompt, max_tokens)
    else:
        raise HTTPException(status_code=500, detail="No models available")
    
    return ChatResponse(
        response=response_text,
        model_used=selected_model,
        reasoning=reasoning
    )

# ═══════════════════════════════════════════════════════════════════
# API ENDPOINTS
# ═══════════════════════════════════════════════════════════════════

@app.post("/chat", response_model=ChatResponse)
async def chat_legacy(request: ChatRequest):
    """
    LEGACY ENDPOINT: Preserved for backward compatibility
    
    This endpoint maintains the original zen_chat API contract to ensure
    existing integrations continue working without modifications.
    
    Limitations:
    - Only reads credentials from environment variables
    - Cannot accept runtime credential injection
    - Simple request format only
    
    Use cases:
    - Local development with .env files
    - Existing integrations that depend on the /chat endpoint
    - Simple testing and prototyping
    """
    return execute_chat_logic(
        prompt=request.prompt,
        model=request.model,
        max_tokens=request.max_tokens
    )

@app.post("/run", response_model=ChatResponse)
async def run_enhanced(request: Union[ChatRequest, EnhancedChatRequest]):
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
    
    1. Simple (same as /chat):
       {"prompt": "Hello", "model": "auto"}
    
    2. Enhanced (with credentials):
       {
         "skill_input": {"prompt": "Hello", "model": "auto"},
         "credentials": {"OPENAI_API_KEY": "sk-..."}
       }
    """
    
    if isinstance(request, EnhancedChatRequest):
        # Enhanced format: Extract credentials and inject them temporarily
        credentials = None
        if request.runtime_config and "credentials" in request.runtime_config:
            credentials = request.runtime_config["credentials"]
        elif request.credentials:
            credentials = request.credentials
        
        # Extract skill parameters from nested structure
        skill_input = request.skill_input
        prompt = skill_input.get("prompt", "")
        model = skill_input.get("model", "auto")
        max_tokens = skill_input.get("max_tokens", 1000)
        
        # Execute with credential injection
        with temp_env_context(credentials):
            return execute_chat_logic(prompt=prompt, model=model, max_tokens=max_tokens)
    
    else:
        # Simple format: Direct execution (same as /chat endpoint)
        return execute_chat_logic(
            prompt=request.prompt,
            model=request.model,
            max_tokens=request.max_tokens
        )

# ═══════════════════════════════════════════════════════════════════
# DISCOVERY & HEALTH ENDPOINTS
# ═══════════════════════════════════════════════════════════════════

@app.get("/health")
async def health():
    """Health check endpoint with enhanced capability reporting"""
    available_models = get_available_models()
    return {
        "status": "healthy",
        "available_models": available_models,
        "total_models": len(available_models),
        "supports_credential_injection": True,
        "endpoints": {
            "legacy": "/chat",
            "enhanced": "/run"
        }
    }

@app.get("/inventory")
async def get_skill_inventory():
    """
    Skill inventory for LLM discovery and integration.
    
    This endpoint provides metadata that helps LLMs and applications
    understand when and how to use this skill effectively.
    """
    return {
        "skill": {
            "name": "zen_chat",
            "description": "Collaborative thinking with AI models through intelligent orchestration",
            "version": "2.0.0",
            "category": "ai_chat",
            "complexity": "moderate",
            "use_cases": [
                "General conversation with AI models",
                "Comparative AI responses between providers",
                "Intelligent fallback between OpenAI and Gemini",
                "Multi-model AI orchestration"
            ],
            "required_credentials": {
                "OPENAI_API_KEY": "OpenAI API key for GPT models",
                "GEMINI_API_KEY": "Google Gemini API key for Gemini models"
            },
            "supports_credential_injection": True,
            "endpoints": {
                "legacy_chat": {
                    "path": "/chat",
                    "description": "Legacy endpoint for backward compatibility",
                    "credential_support": "environment_only"
                },
                "enhanced_run": {
                    "path": "/run", 
                    "description": "Enhanced endpoint with credential injection",
                    "credential_support": "environment_and_runtime"
                }
            },
            "example_queries": [
                "Help me brainstorm ideas for my project",
                "Compare different approaches to solving this problem",
                "What's your thoughts on this technical decision?"
            ]
        }
    }

@app.get("/schema")
async def get_tool_schema():
    """Return the tool schema in a standardized format for LLM consumption."""
    
    parameters = {
        "type": "object",
        "properties": {
            "prompt": {
                "type": "string",
                "description": "The user's message or question to send to the AI"
            },
            "model": {
                "type": "string", 
                "description": "The AI model to use: 'openai' for OpenAI GPT, 'gemini' for Google Gemini, or 'auto' for automatic selection"
            }
        },
        "required": ["prompt"]
    }
    
    output_schema = {
        "type": "object",
        "properties": {
            "response": {
                "type": "string",
                "description": "The AI's response to the user's prompt"
            },
            "model_used": {
                "type": "string",
                "description": "The actual AI model that was used to generate the response"
            },
            "token_count": {
                "type": "integer",
                "description": "Estimated number of tokens used in the conversation"
            }
        }
    }
    
    return {
        "name": "Zen Chat",
        "description": "A simple, focused chat interface that automatically chooses between OpenAI GPT and Google Gemini models for optimal responses",
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

