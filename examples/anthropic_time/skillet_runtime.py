from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, create_model
import importlib, inspect, asyncio, os, yaml

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
    "boolean": bool
}

# build Pydantic model for the inputs
fields = {
    k: (TYPE_MAP[v["type"].lower()], Field(None if v.get("required") is False else ..., description=v.get("description", "")))
    for k, v in meta["inputs"].items()
}
InputModel = create_model("InputModel", **fields)

class OutputModel(BaseModel):
    iso_8601: str
    time: str
    date: str
    timezone: str

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
            "category": "utility",
            "complexity": "simple",
            "use_cases": [
                "When user asks about the current time",
                "For scheduling and time-sensitive operations",
                "Converting between timezones",
                "Checking time in different locations",
                "Time-based calculations and comparisons"
            ],
            "example_queries": [
                "What time is it?",
                "What time is it in Tokyo?",
                "Tell me the current time in New York",
                "What's the local time?",
                "Give me the time in Pacific timezone"
            ],
            "input_types": ["timezone_string", "none"],
            "output_types": ["datetime_object", "formatted_time"],
            "performance": "fast",
            "dependencies": [],
            "works_well_with": ["scheduling", "calendar", "reminders", "meeting_planning"],
            "typical_workflow_position": "data_gathering",
            "tags": ["time", "timezone", "datetime", "utility", "quick"]
        }
    }

@app.get("/schema")
async def get_tool_schema():
    """Return the tool schema in a standardized format for LLM consumption."""
    
    # Convert Skilletfile inputs to function calling schema
    parameters = {
        "type": "object",
        "properties": {},
        "required": []
    }
    
    for param_name, param_info in meta["inputs"].items():
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
        "method": "POST"
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
