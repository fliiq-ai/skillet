# Fliiq Skillet 🍳

**Skillet** is an HTTP-native, OpenAPI-first framework for packaging and running
reusable *skills* (micro-functions) that Large-Language-Model agents can call
over the network.

> "Cook up a skill in minutes, serve it over HTTPS, remix it in a workflow."

---

## Why another spec?

Current community standard **MCP** servers are great for quick sandbox demos
inside an LLM playground, but painful when you try to ship real-world agent
workflows:

| MCP Pain Point | Skillet Solution |
| -------------- | ---------------- |
| Default **stdio** transport; requires local pipes and custom RPC          | **Pure HTTP + JSON** with an auto-generated OpenAPI contract |
| One bespoke server **per repo**; Docker mandatory                         | Single-file **Skillfile.yaml** → deploy to Cloudflare Workers, AWS Lambda or raw FastAPI |
| No discovery or function manifest                                         | Registry + `/openapi.json` enable automatic client stubs & OpenAI function-calling |
| Heavy cold-start if each agent needs its own container                    | Skills are tiny (≤ 5 MB) Workers; scale-to-zero is instant |
| Secrets baked into code                                                   | Standard `.skillet.env` + runtime injection |
| Steep learning curve for non-infra devs                                   | `pip install fliiq-skillet` → `skillet new hello_world` → **done** |

### Key Concepts

* **Skilletfile.yaml ≤50 lines** — declarative inputs/outputs, runtime & entry-point
* **`skillet dev`** — hot-reload FastAPI stub for local testing
* **`skillet deploy`** — one-command deploy to Workers/Lambda (more targets soon)
* **Registry** — browse, star and import skills; share community "recipes" in the *Cookbook*
* **Cookbook** — visual builder that chains skills into agent workflows

### Quick start (Python)

```bash
pip install fliiq-skillet
skillet new fetch_html --runtime python
cd fetch_html
skillet dev          # Swagger UI on http://127.0.0.1:8000
```

## Examples

The `examples/` directory contains reference implementations of Skillet skills:

- [fetch_html_skillet](examples/fetch_html_skillet/README.md) - Fetches HTML content from URLs with markdown conversion and pagination support. A Skillet-compatible implementation of the Anthropic fetch MCP.

Each example includes:
- A complete `Skilletfile.yaml` configuration
- Implementation code
- API documentation and usage examples
- Tests demonstrating the skill's capabilities

To try an example:
```bash
cd examples/fetch_html_skillet
pip install -r requirements.txt
uvicorn skillet_runtime:app --reload
```

Then follow the example-specific README for API usage instructions.
