"""
Skillet CLI main entry point.
"""
import typer

app = typer.Typer()

@app.command()
def new(name: str):
    """Create a new Skillet skill."""
    typer.echo(f"Creating new skill: {name}")

@app.command()
def dev():
    """Start the development server."""
    typer.echo("Starting development server...")

if __name__ == "__main__":
    app() 