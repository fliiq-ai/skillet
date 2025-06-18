# Knowledge Graph Memory Skillet Example

This skill provides a persistent, stateful knowledge graph service. It is a Skillet-compatible implementation of the official Anthropic `memory` MCP.

The skill allows an agent to remember information about users, entities, and their relationships across conversations by storing data in a local `memory.json` file.

**Core Concepts:**
- **Entities**: Nodes in the graph (e.g., a person, an organization). Each has a unique name, a type, and a list of observations.
- **Relations**: Directed connections between entities (e.g., `John_Smith` -> `works_at` -> `Anthropic`).
- **Observations**: Atomic pieces of string-based information attached to an entity (e.g., "Speaks fluent Spanish").

## Quick Start

You'll need two terminal windows to run and test this skill:

### Terminal 1: Start the Server

```bash
# Make sure you're in the right directory
cd examples/anthropic_memory

# Install dependencies
pip install -r requirements.txt

# Start the server
uvicorn skillet_runtime:app --reload
```
The server will be available at `http://127.0.0.1:8000`. Keep this terminal open to see server logs.

### Terminal 2: Run the Automated Tests

In a new terminal window, run the comprehensive test script. This will create, modify, and delete graph elements, then clean up after itself.

```bash
# Navigate to the same directory
cd examples/anthropic_memory

# Run the automated tests
./test.sh
```
A successful run will execute 10 test steps, showing the JSON response for each operation.

## Schema Discovery

Before using the memory skill, you can retrieve its complete schema to understand all available operations and their parameters:

```bash
curl -s -X GET http://127.0.0.1:8000/schema \
  -H "Content-Type: application/json"
```

The schema response includes:
- **Basic tool information**: name, description, version
- **General parameters**: operation types and parameter structure
- **Detailed operations**: Complete specification for all 9 operations:
  - `create_entities` - Create new entities with observations
  - `create_relations` - Link entities with relationships
  - `add_observations` - Add facts to existing entities
  - `read_graph` - Retrieve the entire knowledge graph
  - `search_nodes` - Find entities matching a query
  - `open_nodes` - Get specific entities by name
  - `delete_observations` - Remove specific facts from entities
  - `delete_relations` - Remove relationships between entities
  - `delete_entities` - Remove entities and all their connections

Each operation includes detailed parameter schemas, making it easy for LLM applications to understand exactly how to interact with the memory system.

## API Usage

You can also test individual endpoints manually by making POST requests to the `/run` endpoint. The desired action is specified using the `operation` parameter in the JSON payload.

### Write Operations

#### 1. `create_entities`
Create one or more new entities.
```bash
curl -s -X POST http://127.0.0.1:8000/run -H "Content-Type: application/json" -d '{
  "operation": "create_entities",
  "entities": [{"name": "Jane_Doe", "entityType": "person", "observations": ["Is a doctor"]}]
}'
```

#### 2. `create_relations`
Connect two existing entities.
```bash
curl -s -X POST http://127.0.0.1:8000/run -H "Content-Type: application/json" -d '{
  "operation": "create_relations",
  "relations": [{"from": "Jane_Doe", "to": "General_Hospital", "relationType": "works_at"}]
}'
```

#### 3. `add_observations`
Add facts to an existing entity.
```bash
curl -s -X POST http://127.0.0.1:8000/run -H "Content-Type: application/json" -d '{
  "operation": "add_observations",
  "observations": [{"entityName": "Jane_Doe", "contents": ["Graduated from Med School"]}]
}'
```

### Read Operations

#### 4. `read_graph`
Retrieve the entire knowledge graph.
```bash
curl -s -X POST http://127.0.0.1:8000/run -H "Content-Type: application/json" -d '{
  "operation": "read_graph"
}'
```

#### 5. `search_nodes`
Find nodes matching a query string.
```bash
curl -s -X POST http://127.0.0.1:8000/run -H "Content-Type: application/json" -d '{
  "operation": "search_nodes", "query": "doctor"
}'
```

#### 6. `open_nodes`
Retrieve specific nodes by name.
```bash
curl -s -X POST http://127.0.0.1:8000/run -H "Content-Type: application/json" -d '{
  "operation": "open_nodes", "names": ["Jane_Doe"]
}'
```

### Delete Operations

#### 7. `delete_observations`
Remove specific observations from an entity.
```bash
curl -s -X POST http://127.0.0.1:8000/run -H "Content-Type: application/json" -d '{
  "operation": "delete_observations",
  "deletions": [{"entityName": "Jane_Doe", "observations": ["Is a doctor"]}]
}'
```

#### 8. `delete_relations`
Remove a specific relation.
```bash
curl -s -X POST http://127.0.0.1:8000/run -H "Content-Type: application/json" -d '{
  "operation": "delete_relations",
  "relations": [{"from": "Jane_Doe", "to": "General_Hospital", "relationType": "works_at"}]
}'
```

#### 9. `delete_entities`
Remove entities and all their associated relations.
```bash
curl -s -X POST http://127.0.0.1:8000/run -H "Content-Type: application/json" -d '{
  "operation": "delete_entities", "entityNames": ["Jane_Doe"]
}'
```

## Using Memory in LLM Applications

The knowledge graph memory can be effectively utilized in LLM applications to maintain context and personalize interactions. Here's an example system prompt that demonstrates how to integrate memory operations into your LLM's behavior:

### Example System Prompt

This prompt can be used in the "Custom Instructions" field of a Claude.ai Project or similar LLM configuration:

```
Follow these steps for each interaction:

1. User Identification:
   - You should assume that you are interacting with default_user
   - If you have not identified default_user, proactively try to do so.

2. Memory Retrieval:
   - Always begin your chat by saying only "Remembering..." and retrieve all relevant information from your knowledge graph
   - Always refer to your knowledge graph as your "memory"

3. Memory Tracking:
   - While conversing with the user, be attentive to any new information that falls into these categories:
     a) Basic Identity (age, gender, location, job title, education level, etc.)
     b) Behaviors (interests, habits, etc.)
     c) Preferences (communication style, preferred language, etc.)
     d) Goals (goals, targets, aspirations, etc.)
     e) Relationships (personal and professional relationships up to 3 degrees of separation)

4. Memory Update:
   - If any new information was gathered during the interaction, update your memory as follows:
     a) Create entities for recurring organizations, people, and significant events
     b) Connect them to the current entities using relations
     c) Store facts about them as observations
```

This prompt structure helps the LLM maintain consistent context across conversations while building a rich knowledge graph of user information and relationships.