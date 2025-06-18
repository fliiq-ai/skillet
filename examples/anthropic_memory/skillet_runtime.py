from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, create_model
import importlib, inspect, asyncio, os, yaml
from typing import List, Optional

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILLETFILE_PATH = os.getenv("SKILLETFILE", os.path.join(SCRIPT_DIR, "Skilletfile.yaml"))

# ── parse Skilletfile ──────────────────────────────────────────────
with open(SKILLETFILE_PATH) as f:
    meta = yaml.safe_load(f)

mod_name, func_name = meta["entry"].split(":")
skill_mod = importlib.import_module(mod_name)
skill_fn  = getattr(skill_mod, func_name)

# Type mapping from YAML to Python types
TYPE_MAP = {
    "string": str,
    "integer": int,
    "number": float,
    "boolean": bool,
    "array": List[str]  # Assuming array of strings for now
}

# build Pydantic model for the inputs
input_fields = {}
for k, v in meta.get("inputs", {}).items():
    field_type = TYPE_MAP.get(v["type"].lower(), str)
    is_required = v.get("required", True)
    
    if is_required:
        input_fields[k] = (field_type, Field(description=v.get("description", "")))
    else:
        input_fields[k] = (Optional[field_type], Field(default=None, description=v.get("description", "")))

InputModel = create_model("InputModel", **input_fields)

# build Pydantic model for the outputs
output_fields = {}
for k, v in meta.get("outputs", {}).items():
    field_type = TYPE_MAP.get(v["type"].lower(), str)
    if v.get("required") is False:
        output_fields[k] = (Optional[field_type], None)
    else:
        output_fields[k] = (field_type, ...)

OutputModel = create_model("OutputModel", **output_fields)

app = FastAPI(
    title=meta["name"],
    description=meta["description"],
    version=meta["version"]
)

@app.get("/inventory")
async def get_skill_inventory():
    """Return skill metadata for LLM decision-making about when and how to use this skill."""
    
    return {
        "skill": {
            "name": meta["name"],
            "description": meta["description"],
            "version": meta["version"],
            "category": "memory_management",
            "complexity": "intermediate",
            "use_cases": [
                "When user mentions people, organizations, or relationships",
                "For remembering user preferences and context across conversations",
                "Building knowledge graphs of entities and their connections",
                "Storing and retrieving facts about entities",
                "Managing persistent conversational memory"
            ],
            "example_queries": [
                "Remember that John works at Anthropic",
                "What do you know about Sarah?",
                "Who works at Google?",
                "Add this information about the meeting",
                "Search for people who speak Spanish"
            ],
            "input_types": ["entities", "relations", "observations", "search_queries"],
            "output_types": ["success_confirmation", "entity_data", "search_results"],
            "performance": "fast",
            "dependencies": ["file_system"],
            "works_well_with": ["conversation_management", "user_profiling", "relationship_tracking", "context_awareness"],
            "typical_workflow_position": "data_storage",
            "tags": ["memory", "knowledge_graph", "entities", "relationships", "persistence", "context"]
        }
    }

@app.get("/schema")
async def get_tool_schema():
    """Return the tool schema in a standardized format for LLM consumption."""
    
    # Define detailed operation schemas for the memory skill
    operations = {
        "create_entities": {
            "description": "Create one or more new entities in the knowledge graph",
            "parameters": {
                "entities": {
                    "type": "array",
                    "description": "List of entities to create",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "description": "Unique name for the entity"},
                            "entityType": {"type": "string", "description": "Type of entity (e.g., person, organization)"},
                            "observations": {"type": "array", "description": "List of observations about the entity", "items": {"type": "string"}}
                        },
                        "required": ["name"]
                    }
                }
            },
            "required": ["entities"]
        },
        "create_relations": {
            "description": "Create relationships between existing entities",
            "parameters": {
                "relations": {
                    "type": "array",
                    "description": "List of relations to create",
                    "items": {
                        "type": "object",
                        "properties": {
                            "from": {"type": "string", "description": "Name of the source entity"},
                            "to": {"type": "string", "description": "Name of the target entity"},
                            "relationType": {"type": "string", "description": "Type of relationship (e.g., works_at, knows)"}
                        },
                        "required": ["from", "to", "relationType"]
                    }
                }
            },
            "required": ["relations"]
        },
        "add_observations": {
            "description": "Add observations to existing entities",
            "parameters": {
                "observations": {
                    "type": "array",
                    "description": "List of observations to add",
                    "items": {
                        "type": "object",
                        "properties": {
                            "entityName": {"type": "string", "description": "Name of the entity to add observations to"},
                            "contents": {"type": "array", "description": "List of observation strings", "items": {"type": "string"}}
                        },
                        "required": ["entityName", "contents"]
                    }
                }
            },
            "required": ["observations"]
        },
        "read_graph": {
            "description": "Retrieve the entire knowledge graph",
            "parameters": {},
            "required": []
        },
        "search_nodes": {
            "description": "Search for nodes matching a query string",
            "parameters": {
                "query": {"type": "string", "description": "Search query to match against entity names, types, and observations"}
            },
            "required": ["query"]
        },
        "open_nodes": {
            "description": "Retrieve specific nodes by name",
            "parameters": {
                "names": {"type": "array", "description": "List of entity names to retrieve", "items": {"type": "string"}}
            },
            "required": ["names"]
        },
        "delete_observations": {
            "description": "Remove specific observations from entities",
            "parameters": {
                "deletions": {
                    "type": "array",
                    "description": "List of observation deletions",
                    "items": {
                        "type": "object",
                        "properties": {
                            "entityName": {"type": "string", "description": "Name of the entity to delete observations from"},
                            "observations": {"type": "array", "description": "List of observation strings to delete", "items": {"type": "string"}}
                        },
                        "required": ["entityName", "observations"]
                    }
                }
            },
            "required": ["deletions"]
        },
        "delete_relations": {
            "description": "Remove specific relations from the graph",
            "parameters": {
                "relations": {
                    "type": "array",
                    "description": "List of relations to delete",
                    "items": {
                        "type": "object",
                        "properties": {
                            "from": {"type": "string", "description": "Name of the source entity"},
                            "to": {"type": "string", "description": "Name of the target entity"},
                            "relationType": {"type": "string", "description": "Type of relationship to delete"}
                        },
                        "required": ["from", "to", "relationType"]
                    }
                }
            },
            "required": ["relations"]
        },
        "delete_entities": {
            "description": "Remove entities and all their associated relations",
            "parameters": {
                "entityNames": {"type": "array", "description": "List of entity names to delete", "items": {"type": "string"}}
            },
            "required": ["entityNames"]
        }
    }
    
    # Convert Skilletfile inputs to function calling schema
    parameters = {
        "type": "object",
        "properties": {
            "operation": {
                "type": "string",
                "description": "The operation to perform",
                "enum": list(operations.keys())
            },
            "params": {
                "type": "string",
                "description": "JSON-encoded string containing operation-specific parameters"
            }
        },
        "required": ["operation"]
    }
    
    # Convert outputs to schema
    output_schema = {
        "type": "object",
        "properties": {}
    }
    
    if "outputs" in meta:
        for output_name, output_info in meta["outputs"].items():
            output_schema["properties"][output_name] = {
                "type": output_info["type"],
                "description": output_info.get("description", "")
            }
    
    return {
        "name": meta["name"],
        "description": meta["description"],
        "version": meta["version"],
        "parameters": parameters,
        "output_schema": output_schema,
        "endpoint": "/run",
        "method": "POST",
        "operations": operations
    }

@app.post("/run", response_model=OutputModel)
async def run_skill(payload: InputModel):
    try:
        maybe_coroutine = skill_fn(payload.model_dump())
        if inspect.iscoroutine(maybe_coroutine):
            result = await maybe_coroutine
        else:
            result = maybe_coroutine
        return result
    except Exception as e:
        import traceback
        error_detail = f"{str(e)}\n{traceback.format_exc()}"
        raise HTTPException(status_code=500, detail=error_detail)
