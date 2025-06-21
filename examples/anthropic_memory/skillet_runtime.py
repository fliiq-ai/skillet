"""
Enhanced Framework-Based Skillet Runtime with Credential Injection Support

This runtime automatically loads skill configuration from Skilletfile.yaml and provides
enhanced credential injection capabilities for production deployments.

Features:
- Automatic Skilletfile.yaml parsing and model generation
- Runtime credential injection from client applications
- Backward compatibility with existing /run endpoint format
- Support for both environment variables and injected credentials
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, create_model
import importlib, inspect, asyncio, os, yaml
from typing import List, Optional, Dict, Any, Union
from contextlib import contextmanager

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILLETFILE_PATH = os.getenv("SKILLETFILE", os.path.join(SCRIPT_DIR, "Skilletfile.yaml"))

# ══════════════════════════════════════════════════════════════════════════════
# CREDENTIAL INJECTION UTILITIES
# ══════════════════════════════════════════════════════════════════════════════

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

# ══════════════════════════════════════════════════════════════════════════════
# SKILLETFILE PARSING AND MODEL GENERATION
# ══════════════════════════════════════════════════════════════════════════════

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

# Enhanced request model with credential support
class EnhancedSkillRequest(BaseModel):
    """Enhanced request model supporting credential injection"""
    skill_input: Dict[str, Any]  # Contains the original skill parameters
    credentials: Optional[Dict[str, str]] = None
    runtime_config: Optional[Dict[str, Any]] = None

# build Pydantic model for the outputs
output_fields = {}
for k, v in meta.get("outputs", {}).items():
    field_type = TYPE_MAP.get(v["type"].lower(), str)
    if v.get("required") is False:
        output_fields[k] = (Optional[field_type], None)
    else:
        output_fields[k] = (field_type, ...)

OutputModel = create_model("OutputModel", **output_fields)

# ══════════════════════════════════════════════════════════════════════════════
# FASTAPI APPLICATION SETUP
# ══════════════════════════════════════════════════════════════════════════════

app = FastAPI(
    title=f"{meta['name']} (Enhanced)",
    description=f"{meta['description']} - Enhanced with credential injection support",
    version=meta["version"]
)

# ══════════════════════════════════════════════════════════════════════════════
# CORE SKILL EXECUTION LOGIC
# ══════════════════════════════════════════════════════════════════════════════

async def execute_skill_logic(skill_input: Dict[str, Any]) -> Any:
    """
    Core skill execution logic used by both legacy and enhanced endpoints.
    
    This function contains the actual skill execution and is called by both
    the legacy and enhanced endpoints to ensure consistent behavior.
    """
    maybe_coroutine = skill_fn(skill_input)
    if inspect.iscoroutine(maybe_coroutine):
        result = await maybe_coroutine
    else:
        result = maybe_coroutine
    return result

# ══════════════════════════════════════════════════════════════════════════════
# API ENDPOINTS
# ══════════════════════════════════════════════════════════════════════════════

@app.post("/run", response_model=OutputModel)
async def run_skill_enhanced(request: Union[InputModel, EnhancedSkillRequest]):
    """
    Enhanced /run endpoint supporting both legacy and credential injection formats.
    
    This endpoint maintains backward compatibility while adding support for
    runtime credential injection from client applications.
    
    Request Format Options:
    
    1. Legacy (unchanged - backward compatible):
       {"operation": "create_entities", "params": "{}"}
    
    2. Enhanced (with credential injection):
       {
         "skill_input": {"operation": "create_entities", "params": "{}"},
         "credentials": {"API_KEY": "value"}
       }
    
    Features:
    - Runtime credential injection (perfect for Fliiq integration)
    - Backward compatible with existing request format
    - Temporary environment variable injection
    - Automatic cleanup after request completion
    """
    try:
        if isinstance(request, EnhancedSkillRequest):
            # Enhanced format: Extract credentials and inject them temporarily
            credentials = None
            if request.runtime_config and "credentials" in request.runtime_config:
                credentials = request.runtime_config["credentials"]
            elif request.credentials:
                credentials = request.credentials
            
            # Execute with credential injection
            with temp_env_context(credentials):
                result = await execute_skill_logic(request.skill_input)
                return result
        
        else:
            # Legacy format: Direct execution (backward compatibility)
            result = await execute_skill_logic(request.model_dump())
            return result
            
    except Exception as e:
        import traceback
        error_detail = f"{str(e)}\n{traceback.format_exc()}"
        raise HTTPException(status_code=500, detail=error_detail)

# ══════════════════════════════════════════════════════════════════════════════
# DISCOVERY & METADATA ENDPOINTS
# ══════════════════════════════════════════════════════════════════════════════

@app.get("/inventory")
async def get_skill_inventory():
    """Return skill metadata for LLM decision-making about when and how to use this skill."""
    
    inventory = {
        "skill": {
            "name": meta["name"],
            "description": meta["description"],
            "version": meta["version"],
            "category": "memory",
            "complexity": "moderate",
            "use_cases": [
                "When you need to store information across conversations",
                "For maintaining context between interactions",
                "When building a knowledge graph of related information",
                "For persistent data storage and retrieval",
                "When you need to remember entities and relationships"
            ],
            "example_queries": [
                "Remember that John is a software engineer",
                "What do you know about Alice?",
                "Create a relationship between Company X and Product Y",
                "Search for information about machine learning",
                "Store this fact for later use"
            ],
            "input_types": ["operations", "structured_data"],
            "output_types": ["operation_results", "stored_data"],
            "performance": "fast",
            "dependencies": [],
            "works_well_with": ["conversation", "knowledge_management", "data_analysis"],
            "typical_workflow_position": "data_storage",
            "tags": ["memory", "storage", "knowledge", "graph", "entities"],
            "supports_credential_injection": True
        }
    }
    
    return inventory

@app.get("/schema")
async def get_tool_schema():
    """Return the tool schema in a standardized format for LLM consumption."""
    
    # Convert Skilletfile inputs to function calling schema
    parameters = {
        "type": "object",
        "properties": {},
        "required": []
    }
    
    for param_name, param_info in meta.get("inputs", {}).items():
        parameters["properties"][param_name] = {
            "type": param_info["type"],
            "description": param_info.get("description", "")
        }
        if param_info.get("required", True):
            parameters["required"].append(param_name)
    
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
        "supports_credential_injection": True
    }
