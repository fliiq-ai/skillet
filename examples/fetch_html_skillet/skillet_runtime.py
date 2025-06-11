from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, create_model
import importlib, inspect, asyncio, os, yaml

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
    "boolean": bool
}

# build Pydantic model for the inputs
fields = {
    k: (TYPE_MAP[v["type"].lower()], Field(None if v.get("required") is False else ..., description=v.get("description", "")))
    for k, v in meta["inputs"].items()
}
InputModel = create_model("InputModel", **fields)

class OutputModel(BaseModel):
    html: str | None = None
    markdown: str | None = None

    class Config:
        extra = "allow"  # Allow extra fields like 'markdown' when as_markdown is true

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
