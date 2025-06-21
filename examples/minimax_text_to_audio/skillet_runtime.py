"""
MiniMax Text-to-Audio Skillet - Enhanced Runtime with Credential Injection Support

This runtime provides TWO endpoints to support different use cases:

1. /text_to_audio (Legacy) - Backward compatibility for existing users
   - Uses simple TextToAudioRequest format
   - Reads credentials from environment variables only
   - Preserves existing integrations without breaking changes

2. /run (Enhanced) - Modern endpoint for production deployments
   - Supports both simple and enhanced request formats
   - Enables runtime credential injection from frontend applications
   - Compatible with Fliiq and multi-skill host architecture
   - Follows standard Skillet patterns

Both endpoints use the same underlying text-to-audio logic, ensuring consistent behavior.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import requests
import json
import time
from typing import Optional, Dict, Any, Union
from contextlib import contextmanager
import uuid

app = FastAPI(
    title="MiniMax Text-to-Audio Skillet", 
    description="Convert text to audio using MiniMax API - Enhanced with credential injection support",
    version="2.0.0"
)

# ═══════════════════════════════════════════════════════════════════
# REQUEST/RESPONSE MODELS
# ═══════════════════════════════════════════════════════════════════

class TextToAudioRequest(BaseModel):
    """Legacy request model - preserved for backward compatibility with /text_to_audio endpoint"""
    text: str
    voice_id: Optional[str] = "male-qn-qingse"
    speed: Optional[float] = 1.0
    volume: Optional[float] = 1.0

class EnhancedTextToAudioRequest(BaseModel):
    """Enhanced request model supporting credential injection for /run endpoint"""
    skill_input: Dict[str, Any]  # Contains: text, voice_id, speed, volume
    credentials: Optional[Dict[str, str]] = None
    runtime_config: Optional[Dict[str, Any]] = None

class TextToAudioResponse(BaseModel):
    """Response model used by both endpoints"""
    audio_url: str
    audio_file: str
    duration: float
    voice_used: str

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
# CORE TEXT-TO-AUDIO LOGIC
# ═══════════════════════════════════════════════════════════════════

def get_minimax_config():
    """Get MiniMax API configuration"""
    api_key = os.getenv("MINIMAX_API_KEY")
    api_host = os.getenv("MINIMAX_API_HOST", "https://api.minimax.io")
    
    if not api_key:
        raise HTTPException(
            status_code=500, 
            detail={
                "error": "Missing required credential: MINIMAX_API_KEY",
                "message": "MINIMAX_API_KEY environment variable is required",
                "required_credentials": ["MINIMAX_API_KEY"],
                "optional_credentials": ["MINIMAX_API_HOST"],
                "how_to_get": "Get your MiniMax API key from: https://platform.minimax.chat",
                "steps": [
                    "1. Go to https://platform.minimax.chat",
                    "2. Sign up or log in to your account",
                    "3. Navigate to API Keys section",
                    "4. Create a new API key",
                    "5. Copy the key and set MINIMAX_API_KEY environment variable"
                ],
                "format": "Usually starts with 'mk-' prefix",
                "documentation": "https://platform.minimax.chat/docs"
            }
        )
    
    return api_key, api_host

def call_minimax_tts(text: str, voice_id: str, speed: float, volume: float) -> dict:
    """Call MiniMax Text-to-Speech API"""
    api_key, api_host = get_minimax_config()
    
    url = f"{api_host}/v1/text_to_speech"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "text": text,
        "voice_id": voice_id,
        "speed": speed,
        "volume": volume,
        "audio_setting": {
            "sample_rate": 22050,
            "bitrate": 128000,
            "format": "mp3"
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"MiniMax API error: {str(e)}")

def download_audio(audio_url: str) -> str:
    """Download audio file from URL"""
    try:
        response = requests.get(audio_url, timeout=30)
        response.raise_for_status()
        
        # Create output directory if it doesn't exist
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate unique filename
        filename = f"audio_{uuid.uuid4().hex[:8]}.mp3"
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, "wb") as f:
            f.write(response.content)
        
        return filepath
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to download audio: {str(e)}")

async def text_to_audio_logic(text: str, voice_id: str = "male-qn-qingse", speed: float = 1.0, volume: float = 1.0) -> TextToAudioResponse:
    """
    Core text-to-audio logic used by both legacy and enhanced endpoints.
    
    This function contains the actual text-to-audio conversion and is called by both
    the legacy and enhanced endpoints to ensure consistent behavior.
    """
    
    # Validate inputs
    if not text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    
    if not (0.5 <= speed <= 2.0):
        raise HTTPException(status_code=400, detail="Speed must be between 0.5 and 2.0")
    
    if not (0.1 <= volume <= 1.0):
        raise HTTPException(status_code=400, detail="Volume must be between 0.1 and 1.0")
    
    # Call MiniMax API
    result = call_minimax_tts(text, voice_id, speed, volume)
    
    # Extract audio URL from response
    if "audio_url" not in result:
        raise HTTPException(status_code=500, detail="Invalid response from MiniMax API")
    
    audio_url = result["audio_url"]
    
    # Download audio file
    audio_file = download_audio(audio_url)
    
    # Get duration (estimate based on text length and speed)
    # This is an approximation - actual duration would need audio analysis
    estimated_duration = len(text.split()) * 0.6 / speed
    
    return TextToAudioResponse(
        audio_url=audio_url,
        audio_file=audio_file,
        duration=estimated_duration,
        voice_used=voice_id
    )

# ═══════════════════════════════════════════════════════════════════
# API ENDPOINTS
# ═══════════════════════════════════════════════════════════════════

@app.post("/text_to_audio", response_model=TextToAudioResponse)
async def text_to_audio_legacy(request: TextToAudioRequest):
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
    return await text_to_audio_logic(
        request.text,
        request.voice_id,
        request.speed,
        request.volume
    )

@app.post("/run", response_model=TextToAudioResponse)
async def run_enhanced(request: Union[TextToAudioRequest, EnhancedTextToAudioRequest]):
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
    
    1. Simple (same as /text_to_audio):
       {"text": "Hello world", "voice_id": "male-qn-qingse"}
    
    2. Enhanced (with credentials):
       {
         "skill_input": {"text": "Hello world", "voice_id": "male-qn-qingse"},
         "credentials": {"MINIMAX_API_KEY": "...", "MINIMAX_API_HOST": "..."}
       }
    """
    
    if isinstance(request, EnhancedTextToAudioRequest):
        # Enhanced format: Extract credentials and inject them temporarily
        credentials = None
        if request.runtime_config and "credentials" in request.runtime_config:
            credentials = request.runtime_config["credentials"]
        elif request.credentials:
            credentials = request.credentials
        
        # Extract skill parameters from nested structure
        skill_input = request.skill_input
        text = skill_input.get("text", "")
        voice_id = skill_input.get("voice_id", "male-qn-qingse")
        speed = skill_input.get("speed", 1.0)
        volume = skill_input.get("volume", 1.0)
        
        # Execute with credential injection
        with temp_env_context(credentials):
            return await text_to_audio_logic(text, voice_id, speed, volume)
    
    else:
        # Simple format: Direct execution (same as /text_to_audio endpoint)
        return await text_to_audio_logic(
            request.text,
            request.voice_id,
            request.speed,
            request.volume
        )

# ═══════════════════════════════════════════════════════════════════
# UTILITY ENDPOINTS
# ═══════════════════════════════════════════════════════════════════

@app.get("/voices")
async def list_voices():
    """List available voices (mock implementation)"""
    # This would typically call the MiniMax API to get available voices
    # For now, returning a mock list based on common MiniMax voices
    return {
        "voices": [
            {"id": "male-qn-qingse", "name": "Male Qingse", "language": "zh"},
            {"id": "female-shaonv", "name": "Female Shaonv", "language": "zh"},
            {"id": "male-youthful", "name": "Male Youthful", "language": "en"},
            {"id": "female-gentle", "name": "Female Gentle", "language": "en"}
        ]
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    try:
        api_key, api_host = get_minimax_config()
        return {
            "status": "healthy",
            "api_host": api_host,
            "api_key_configured": bool(api_key),
            "supports_credential_injection": True
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

