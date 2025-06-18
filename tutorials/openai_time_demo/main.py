import os
import json
import requests
from typing import Optional, Dict, Any
from rich.console import Console
from rich.panel import Panel
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Initialize Rich console for better output
console = Console()

# Skillet time service configuration
SKILLET_TIME_URL = os.getenv("SKILLET_TIME_URL", "http://localhost:8000/run")
SKILLET_SCHEMA_URL = os.getenv("SKILLET_SCHEMA_URL", "http://localhost:8000/schema")

def get_tool_schema() -> Dict[str, Any]:
    """
    Fetch the tool schema from the Skillet service.
    
    Returns:
        Dict containing the tool schema
    """
    try:
        response = requests.get(SKILLET_SCHEMA_URL)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        console.print(f"[red]Error fetching tool schema: {e}[/red]")
        return {}

def get_time(timezone: Optional[str] = None) -> Dict[str, Any]:
    """
    Call the Skillet time service to get the current time.
    
    Args:
        timezone: Optional IANA timezone identifier (e.g., 'America/New_York')
    
    Returns:
        Dict containing the time response
    """
    try:
        payload = {"timezone": timezone} if timezone else {}
        response = requests.post(SKILLET_TIME_URL, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        console.print(f"[red]Error calling Skillet time service: {e}[/red]")
        return {"error": str(e)}

def create_openai_function_from_schema(schema: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert Skillet schema to OpenAI function calling format.
    
    Args:
        schema: Skillet tool schema
    
    Returns:
        OpenAI function definition
    """
    return {
        "name": "get_time",
        "description": schema.get("description", "Get the current time"),
        "parameters": schema.get("parameters", {
            "type": "object",
            "properties": {
                "timezone": {
                    "type": "string",
                    "description": "IANA timezone identifier"
                }
            },
            "required": []
        })
    }

def process_user_query(user_input: str, functions: list) -> str:
    """
    Process user input through OpenAI and get time information.
    
    Args:
        user_input: User's question about time
        functions: List of available functions
    
    Returns:
        Formatted response string
    """
    try:
        # Get OpenAI's response with function calling
        messages = [{"role": "user", "content": user_input}]
        response = client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            messages=messages,
            functions=functions,
            function_call="auto"
        )
        
        # Extract the response
        message = response.choices[0].message
        
        # Check if OpenAI wants to call a function
        if message.function_call:
            # Parse the function arguments
            args = json.loads(message.function_call.arguments)
            
            # Call the Skillet time service
            time_response = get_time(args.get("timezone"))
            
            if "error" in time_response:
                return f"Sorry, there was an error: {time_response['error']}"
            
            # Add the function response to the conversation
            messages.append({
                "role": "function",
                "name": "get_time",
                "content": json.dumps(time_response)
            })
            
            # Get OpenAI to format the response
            final_response = client.chat.completions.create(
                model="gpt-3.5-turbo-0125",
                messages=messages
            )
            
            return final_response.choices[0].message.content
        
        return message.content
        
    except Exception as e:
        return f"Sorry, an error occurred: {str(e)}"

def main():
    """Main interactive loop."""
    console.print(Panel.fit(
        "[yellow]Welcome to the OpenAI + Skillet Time Demo![/yellow]\n"
        "This demo dynamically discovers the Skillet tool schema.\n"
        "Ask me about the time in any timezone!\n"
        "Type 'quit' to exit."
    ))
    
    # Fetch the tool schema from the Skillet service
    console.print("\n[blue]Fetching tool schema from Skillet service...[/blue]")
    schema = get_tool_schema()
    
    if not schema:
        console.print("[red]Failed to fetch tool schema. Make sure the Skillet service is running.[/red]")
        return
    
    console.print(f"[green]✓ Loaded tool: {schema.get('name', 'Unknown')} v{schema.get('version', '0.0.0')}[/green]")
    
    # Convert schema to OpenAI function format
    functions = [create_openai_function_from_schema(schema)]
    
    while True:
        try:
            # Get user input
            user_input = console.input("\n[bold green]You:[/bold green] ")
            
            # Check for exit command
            if user_input.lower() in ('quit', 'exit', 'q'):
                console.print("\n[yellow]Goodbye![/yellow]")
                break
            
            # Process the query
            console.print("\n[bold blue]Assistant:[/bold blue]", end=" ")
            response = process_user_query(user_input, functions)
            console.print(response)
            
        except KeyboardInterrupt:
            console.print("\n[yellow]Goodbye![/yellow]")
            break
        except Exception as e:
            console.print(f"\n[red]An error occurred: {e}[/red]")

if __name__ == "__main__":
    main()
