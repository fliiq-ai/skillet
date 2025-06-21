# Zen Chat Skillet

A Skillet skill that provides collaborative thinking with AI models through intelligent model orchestration, inspired by the Zen MCP server.

### zen_chat
**Original MCP:** [Zen MCP Server](https://github.com/BeehiveInnovations/zen-mcp-server)
- **Description:** Collaborative thinking with AI models through intelligent orchestration
- **Features:** Automatic model selection, multi-model support (Gemini, OpenAI)
- **API:** `/chat` endpoint for AI conversations

- **Multi-Provider Support**: Works with both OpenAI GPT and Google Gemini models
- **Intelligent Fallback**: Automatically switches between available models
- **Dual Endpoint Design**: Legacy and modern endpoints for maximum compatibility
- **Credential Injection**: Runtime credentials for production deployments
- **Auto Model Selection**: Chooses the best available model based on preference

This skill automatically selects the best available AI model (Gemini or OpenAI) for responding to prompts, providing reasoning for the model choice. It's designed to give you the best AI assistance by leveraging the strengths of different models.

### Local Development

- **Automatic Model Selection**: Chooses the best available model based on capabilities
- **Manual Model Selection**: Allows you to specify a preferred model
- **Multi-Model Support**: Works with Google Gemini and OpenAI GPT models
- **Reasoning Transparency**: Explains why a particular model was chosen
- **Configurable Output**: Adjustable token limits for responses

## API Endpoints

This skillet provides **two endpoints** to support different use cases:

### `/chat` - Legacy Endpoint (Backward Compatibility)

**Purpose**: Maintains existing API contract for current users

**Request Format:**
```json
POST /chat
{
  "prompt": "Explain quantum computing",
  "model": "auto",        // "auto", "openai", or "gemini"
  "max_tokens": 100
}
```

**Credential Source**: Environment variables only (`.env` file)

**Use Cases:**
- Local development with `.env` files
- Existing integrations depending on `/chat` endpoint
- Simple testing and prototyping

---

### `/run` - Enhanced Endpoint (Production Ready)

**Purpose**: Modern endpoint supporting credential injection for production deployments

**Request Format Option 1 - Simple (same as /chat):**
```json
POST /run
{
  "prompt": "Explain quantum computing", 
  "model": "auto",
  "max_tokens": 100
}
```

**Request Format Option 2 - Enhanced (with credentials):**
```json
POST /run
{
  "skill_input": {
    "prompt": "Explain quantum computing",
    "model": "auto",
    "max_tokens": 100
  },
  "credentials": {
    "OPENAI_API_KEY": "sk-...",
    "GEMINI_API_KEY": "AIza..."
  }
}
```

**Credential Sources**: Environment variables OR runtime injection

**Use Cases:**
- Production deployments (Fliiq integration)
- Runtime credential injection
- Multi-skill host compatibility
- Future feature development

## Response Format

Both endpoints return the same response format:

```json
{
  "response": "Quantum computing uses quantum mechanics...",
  "model_used": "gemini",
  "reasoning": "Gemini chosen for extended reasoning capabilities"
}
```

## Model Selection Logic

1. **User Specified**: If you specify `"model": "openai"` or `"model": "gemini"`, that model is used
2. **Auto Selection**: If `"model": "auto"` (default):
   - Prefers Gemini for extended reasoning capabilities
   - Falls back to OpenAI if Gemini unavailable
   - Fails gracefully if no models available

## Credential Configuration

### Local Development (.env file)
```bash
# Copy .env.example to .env and fill in your keys
OPENAI_API_KEY=sk-your-openai-key-here
GEMINI_API_KEY=AIza-your-gemini-key-here
```

### Production Deployment (Runtime Injection)
```javascript
// Frontend application (e.g., Fliiq)
const response = await fetch('/api/zen_chat/run', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    skill_input: {
      prompt: "Help me brainstorm project ideas",
      model: "auto"
    },
    credentials: {
      OPENAI_API_KEY: userApiKey,
      GEMINI_API_KEY: userGeminiKey
    }
  })
});
```

## API Key Setup

### OpenAI API Key
1. Visit [OpenAI API Keys](https://platform.openai.com/api-keys)
2. Create a new API key
3. Add to `.env` as `OPENAI_API_KEY=sk-...`

### Google Gemini API Key
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Add to `.env` as `GEMINI_API_KEY=AIza...`

## Testing

Run the comprehensive test suite:

```bash
./test.sh
```

The test script will:
- ✅ Test both legacy `/chat` and enhanced `/run` endpoints
- ✅ Verify credential injection functionality
- ✅ Test both OpenAI and Gemini integration
- ✅ Demonstrate auto model selection
- ✅ Validate backward compatibility
- ✅ Show graceful error handling

## Production Integration

### Fliiq Integration Example

```javascript
// In your Fliiq application
const chatWithAI = async (userMessage, userCredentials) => {
  const response = await fetch('/api/skillets/zen_chat/run', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      skill_input: {
        prompt: userMessage,
        model: "auto",
        max_tokens: 500
      },
      credentials: userCredentials
    })
  });
  
  return await response.json();
};
```

### Multi-Skill Host Integration

This skillet is compatible with the Skillet Multi-Skill Runtime Host:

```yaml
# runtime-config.yaml
skills:
  - name: zen_chat
    path: ./examples/zen_chat
    mount: chat
    enabled: true
```

## Architecture Benefits

### Why Two Endpoints?

1. **`/chat` (Legacy)**:
   - ✅ Zero breaking changes for existing users
   - ✅ Simple local development workflow
   - ❌ Limited to environment variable credentials

2. **`/run` (Enhanced)**:
   - ✅ Production-ready credential injection
   - ✅ Compatible with Fliiq and multi-skill host
   - ✅ Follows standard Skillet patterns
   - ✅ Future-proof for new features

### Security Features

- **No Credential Storage**: API keys are never stored on the server
- **Temporary Injection**: Credentials are injected only for the duration of the request
- **Environment Isolation**: Original environment variables are restored after each request
- **Clear Error Messages**: Helpful feedback when credentials are missing or invalid

## Troubleshooting

### "No AI models available" Error
- **Cause**: No valid API keys found
- **Solution**: Check your `.env` file or ensure credentials are being injected properly

### "Gemini API error" 
- **Cause**: Invalid Gemini API key or model unavailable
- **Solution**: Verify your Gemini API key and check the [Google AI Studio](https://makersuite.google.com/)

### "OpenAI API error"
- **Cause**: Invalid OpenAI API key or quota exceeded
- **Solution**: Check your OpenAI API key and billing status

## Next Steps

This skillet is ready for:
- ✅ **Local Development**: Use with `.env` files
- ✅ **Production Deployment**: Integrate with Fliiq or other applications
- ✅ **Multi-Skill Hosting**: Works with the runtime host
- ✅ **Credential Injection**: Supports runtime credential management

