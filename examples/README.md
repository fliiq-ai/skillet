# MCP to Skillet Conversion Examples

This directory contains Skillet implementations converted from popular MCP (Model Context Protocol) servers. Each example demonstrates how to transform MCP functionality into HTTP-native Skillet skills.

## Converted Skills

### 1. zen_chat
**Original MCP:** [Zen MCP Server](https://github.com/BeehiveInnovations/zen-mcp-server)
- **Description:** Collaborative thinking with AI models through intelligent orchestration
- **Features:** Automatic model selection, multi-model support (Gemini, OpenAI)
- **API:** `/chat` endpoint for AI conversations

### 2. minimax_text_to_audio
**Original MCP:** [MiniMax-MCP](https://github.com/MiniMax-AI/MiniMax-MCP)
- **Description:** High-quality text-to-speech conversion using MiniMax API
- **Features:** Multiple voices, adjustable speed/volume, audio file download
- **API:** `/text_to_audio` endpoint for TTS conversion

### 3. context7_docs
**Original MCP:** [Context7](https://github.com/upstash/context7)
- **Description:** Retrieve up-to-date documentation for libraries and frameworks
- **Features:** Smart documentation search, library-specific queries, relevance ranking
- **API:** `/docs` endpoint for documentation retrieval

### 4. playwright_navigate
**Original MCP:** [Playwright-MCP](https://github.com/microsoft/playwright-mcp)
- **Description:** Web page navigation using Playwright browser automation
- **Features:** Reliable navigation, custom viewport, redirect handling, performance metrics
- **API:** `/navigate` endpoint for web navigation

### 5. supabase_execute_sql
**Original MCP:** [Supabase-MCP](https://github.com/supabase-community/supabase-mcp)
- **Description:** Execute SQL queries on Supabase databases with security features
- **Features:** Read-only mode, SQL injection protection, query validation
- **API:** `/execute_sql` endpoint for database operations

## File Structure

Each skill follows the standard Skillet structure:

```
skill_name/
├── Skilletfile.yaml      # Skill configuration and schema
├── skillet_runtime.py    # Python FastAPI implementation
├── requirements.txt      # Python dependencies
├── test.sh              # Automated test script
└── README.md            # Documentation and usage guide
```

## Key Differences from MCP

### Transport Protocol
- **MCP:** Uses stdio or SSE transport with custom RPC
- **Skillet:** Pure HTTP + JSON with OpenAPI contracts

### Deployment
- **MCP:** Requires local pipes, custom server setup
- **Skillet:** Single-file deployment to cloud platforms (Workers, Lambda)

### Discovery
- **MCP:** No built-in discovery mechanism
- **Skillet:** Registry + `/openapi.json` for automatic discovery

### Configuration
- **MCP:** Secrets often baked into code
- **Skillet:** Standard environment variables + runtime injection

## Testing

Each skill includes a comprehensive test script. To test a skill:

1. Install dependencies:
   ```bash
   cd examples/skill_name
   pip install -r requirements.txt
   ```

2. Start the server:
   ```bash
   uvicorn skillet_runtime:app --reload
   ```

3. Run tests (in another terminal):
   ```bash
   ./test.sh
   ```

## Configuration

Most skills require API keys or configuration:

- **zen_chat:** `GEMINI_API_KEY`, `OPENAI_API_KEY`
- **minimax_text_to_audio:** `MINIMAX_API_KEY`, `MINIMAX_API_HOST`
- **context7_docs:** No external APIs (uses mock data)
- **playwright_navigate:** Requires `playwright install`
- **supabase_execute_sql:** `SUPABASE_URL`, `SUPABASE_ANON_KEY`

## Implementation Notes

### Conversion Strategy
1. **Analyzed** original MCP server functionality
2. **Identified** core tools/functions provided
3. **Re-implemented** in Python using FastAPI
4. **Created** Skillet configuration files
5. **Developed** comprehensive tests

### Design Decisions
- **Python Runtime:** All skills use Python for consistency
- **FastAPI Framework:** Provides automatic OpenAPI generation
- **Mock Implementations:** Some skills include mock data for testing
- **Security First:** Built-in validation and error handling
- **HTTP-Native:** Pure REST APIs with JSON payloads

### Limitations
- Some skills use simplified/mock implementations for demonstration
- Real production use would require full API integrations
- Error handling is basic but functional
- Performance optimizations not fully implemented

## Usage Examples

### zen_chat
```bash
curl -X POST "http://localhost:8000/chat" \
    -H "Content-Type: application/json" \
    -d '{"prompt": "Explain quantum computing", "model": "auto"}'
```

### minimax_text_to_audio
```bash
curl -X POST "http://localhost:8000/text_to_audio" \
    -H "Content-Type: application/json" \
    -d '{"text": "Hello world", "voice_id": "male-qn-qingse"}'
```

### context7_docs
```bash
curl -X POST "http://localhost:8000/docs" \
    -H "Content-Type: application/json" \
    -d '{"query": "react hooks", "library": "react"}'
```

### playwright_navigate
```bash
curl -X POST "http://localhost:8000/navigate" \
    -H "Content-Type: application/json" \
    -d '{"url": "https://example.com", "wait_for": "load"}'
```

### supabase_execute_sql
```bash
curl -X POST "http://localhost:8000/execute_sql" \
    -H "Content-Type: application/json" \
    -d '{"sql": "SELECT * FROM users", "read_only": true}'
```

## Next Steps

To extend these examples:

1. **Add More Skills:** Convert additional MCP servers
2. **Enhance Implementations:** Replace mock data with real API calls
3. **Improve Error Handling:** Add more robust error handling
4. **Add Authentication:** Implement proper auth mechanisms
5. **Optimize Performance:** Add caching, connection pooling
6. **Deploy to Cloud:** Use Skillet deployment tools

## Contributing

When adding new MCP-to-Skillet conversions:

1. Follow the established file structure
2. Include comprehensive tests
3. Document all configuration requirements
4. Provide clear usage examples
5. Maintain security best practices

## Credential Requirements Overview

**🔐 Skills that REQUIRE credentials:**

| Skill | Required Credentials | Optional Credentials | Notes |
|-------|---------------------|---------------------|-------|
| `zen_chat` | `OPENAI_API_KEY` OR `GEMINI_API_KEY` | Both for full functionality | Need at least one API key |
| `supabase_execute_sql` | `SUPABASE_URL`, `SUPABASE_ANON_KEY` OR `SUPABASE_SERVICE_ROLE_KEY` | - | ANON_KEY for read-only, SERVICE_ROLE_KEY for write |
| `minimax_text_to_audio` | `MINIMAX_API_KEY` | `MINIMAX_API_HOST` | HOST defaults to global endpoint |

**✅ Skills that DON'T need credentials:**

| Skill | Notes |
|-------|-------|
| `anthropic_time` | Works out of the box - perfect for testing |
| `anthropic_fetch` | Fetches public URLs only |
| `anthropic_memory` | Uses in-memory storage |
| `playwright_navigate` | Local browser automation (requires Playwright installed) |
| `context7_docs` | Uses mock data (would need `CONTEXT7_API_KEY` for production) |

### Getting Credentials

For skills that require credentials, each README contains:
- 🔗 Direct links to get API keys
- 📋 Step-by-step setup instructions
- 💡 Production deployment examples
- ⚠️ Enhanced error messages with credential-specific guidance

### Error Messages

All credential-dependent skills now provide enhanced error messages that include:
- Exactly which credentials are missing
- Direct links to get API keys
- Step-by-step instructions
- Format examples
- Documentation links

Example error response:
```json
{
  "error": "Missing required credential: OPENAI_API_KEY",
  "required_credentials": ["OPENAI_API_KEY"],
  "how_to_get": "Get your OpenAI API key from: https://platform.openai.com/api-keys",
  "steps": ["1. Go to https://platform.openai.com/api-keys", "2. Create a new API key", "..."]
}
```

