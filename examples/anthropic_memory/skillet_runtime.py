from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, create_model
import importlib, inspect, asyncio, os, yaml
from typing import List, Optional

SKILLETFILE_PATH = os.getenv("SKILLETFILE", "Skilletfile.yaml")

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
input_fields = {
    k: (TYPE_MAP.get(v["type"].lower(), str), Field(None if v.get("required") is False else ..., description=v.get("description", "")))
    for k, v in meta.get("inputs", {}).items()
}
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
