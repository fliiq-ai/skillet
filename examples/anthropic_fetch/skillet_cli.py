import typer, yaml, shutil, subprocess, tempfile, os, textwrap, sys, uvicorn
from pathlib import Path

app = typer.Typer(help="Fliiq Skillet CLI (MVP)")

TEMPLATE_SKILLETFILE = textwrap.dedent("""\
# Fliiq Skillet spec v0.1
    name: {name}
    version: 0.1.0
description: "Fetch raw HTML from a public URL (wrapper around Anthropic fetch MCP)."
license: MIT

runtime: python3.11          # supported: python, node, deno (MVP: python only)
entry: main:handler          # module:function (async or sync)

auth: none                   # or api_key / oauth2

inputs:
  url:
    type: string
    description: "Fully-qualified URL (http/https)."

outputs:
  html:
    type: string
    description: "Raw HTML limited to 10 000 chars."
""")

@app.command()
def new(name: str):
    """Create a new skill directory with template files."""
    Path(name).mkdir()
    (Path(name)/"Skilletfile.yaml").write_text(TEMPLATE_SKILLETFILE.format(name=name))
    (Path(name)/"main.py").write_text(textwrap.dedent("""\
        async def handler(params):
            return {"html": "<h1>Hello</h1>"}
    """))
    (Path(name)/"requirements.txt").write_text("fastapi\nuvicorn[standard]\n")
    typer.echo(f"Scaffolded skill in ./{name}")

@app.command()
def dev():
    """Run local FastAPI dev server."""
    # assumes cwd contains Skilletfile.yaml
    os.environ["SKILLETFILE"] = "Skilletfile.yaml"
    uvicorn.run("skillet_runtime:app", reload=True, port=8000)

@app.command()
def build():
    typer.echo("Packaging zip for AWS Lambda (MVP-placeholder)")
    tmp = tempfile.mkdtemp()
    shutil.make_archive("skill", "zip", ".")
    typer.echo("Created skill.zip")

@app.command()
def deploy():
    typer.echo("TODO: implement Cloudflare Workers or Lambda deploy")

if __name__ == "__main__":
    app()
