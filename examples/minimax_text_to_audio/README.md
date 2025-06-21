# MiniMax Text-to-Audio Skillet

A Skillet skill that converts text to audio using MiniMax's text-to-speech API.

## Description

This skill provides high-quality text-to-speech conversion using MiniMax's TTS API. It supports multiple voices, adjustable speech speed and volume, and automatically downloads the generated audio files.

## 🔐 **Credential Requirements**

This skill **requires** the following credentials to function:

### **Required Environment Variables**
- **`MINIMAX_API_KEY`** - Your MiniMax API key
  - Get from: [MiniMax Developer Platform](https://platform.minimax.chat)
  - Format: Usually starts with `mk-` or similar prefix

### **Optional Environment Variables**
- **`MINIMAX_API_HOST`** - API endpoint (region-specific)
  - Default: `https://api.minimax.io`
  - Mainland China: `https://api.minimaxi.com`

### **Local Development Setup**
```bash
# Copy .env.example to .env and add your credentials
cp .env.example .env

# Edit .env file:
MINIMAX_API_KEY=mk-your-minimax-api-key-here
MINIMAX_API_HOST=https://api.minimax.io  # Optional, defaults to global endpoint
```

### **Production Deployment (Runtime Injection)**
For production applications like Fliiq, credentials can be provided at runtime:

```javascript
const response = await fetch('/api/minimax_text_to_audio/run', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    skill_input: {
      text: "Hello world",
      voice_id: "male-qn-qingse",
      speed: 1.0,
      volume: 0.8
    },
    credentials: {
      MINIMAX_API_KEY: "mk-your-api-key",
      MINIMAX_API_HOST: "https://api.minimax.io"  // Optional
    }
  })
});
```

### **Getting Your MiniMax API Key**

1. **Go to [MiniMax Developer Platform](https://platform.minimax.chat)**
2. **Sign up or log in to your account**
3. **Navigate to API Keys section**
4. **Create a new API key**
5. **Copy the key and add it to your environment variables**

## Features

- **High-Quality TTS**: Uses MiniMax's advanced text-to-speech technology
- **Multiple Voices**: Support for various male and female voices
- **Customizable Parameters**: Adjustable speed and volume
- **Audio Download**: Automatically downloads generated audio files
- **Voice Listing**: Get available voices for selection
- **Dual Endpoints**: Legacy and enhanced endpoints for maximum compatibility
- **Credential Injection**: Runtime credentials for production deployments

## API Endpoints

This skillet provides **two endpoints** to support different use cases:

### `/text_to_audio` - Legacy Endpoint (Backward Compatibility)

**Purpose**: Maintains existing API contract for current users

**Request Format:**
```json
POST /text_to_audio
{
  "text": "Text to convert to speech",
  "voice_id": "male-qn-qingse",
  "speed": 1.0,
  "volume": 0.8
}
```

**Credential Source**: Environment variables only (`.env` file)

---

### `/run` - Enhanced Endpoint (Production Ready)

**Purpose**: Modern endpoint supporting credential injection for production deployments

**Request Format Option 1 - Simple (same as /text_to_audio):**
```json
POST /run
{
  "text": "Text to convert to speech",
  "voice_id": "male-qn-qingse",
  "speed": 1.0,
  "volume": 0.8
}
```

**Request Format Option 2 - Enhanced (with credentials):**
```json
POST /run
{
  "skill_input": {
    "text": "Text to convert to speech",
    "voice_id": "male-qn-qingse",
    "speed": 1.0,
    "volume": 0.8
  },
  "credentials": {
    "MINIMAX_API_KEY": "mk-your-api-key",
    "MINIMAX_API_HOST": "https://api.minimax.io"
  }
}
```

**Credential Sources**: Environment variables OR runtime injection

## Response Format

Both endpoints return the same response format:

```json
{
    "audio_url": "https://...",
    "audio_file": "output/audio_abc123.mp3",
    "duration": 5.2,
    "voice_used": "male-qn-qingse"
}
```

### GET /voices
List available voices.

**Response:**
```json
{
    "voices": [
        {"id": "male-qn-qingse", "name": "Male Qingse", "language": "zh"},
        {"id": "female-shaonv", "name": "Female Shaonv", "language": "zh"}
    ]
}
```

### GET /health
Health check endpoint.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure MiniMax API credentials (see [Credential Requirements](#-credential-requirements) above)

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
- List available voices
- Test text-to-audio conversion
- Test different voices and parameters
- Test error handling

### **Regional Configuration**

| Region | API Host |
|--------|----------|
| Global | https://api.minimax.io |
| Mainland China | https://api.minimaxi.com |

## Parameters

- **text**: Text to convert (required)
- **voice_id**: Voice to use (default: "male-qn-qingse")
- **speed**: Speech speed, 0.5-2.0 (default: 1.0)
- **volume**: Audio volume, 0.1-1.0 (default: 1.0)

## Example Usage

```bash
# Basic text-to-speech
curl -X POST "http://localhost:8000/text_to_audio" \
    -H "Content-Type: application/json" \
    -d '{"text": "Hello world", "voice_id": "male-qn-qingse"}'

# Custom speed and volume
curl -X POST "http://localhost:8000/text_to_audio" \
    -H "Content-Type: application/json" \
    -d '{
        "text": "This is faster speech",
        "voice_id": "female-shaonv",
        "speed": 1.5,
        "volume": 0.9
    }'
```

## Output

Generated audio files are saved in the `output/` directory with unique filenames. The API returns both the original URL and the local file path.

