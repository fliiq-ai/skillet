"""
OpenAI + Skillet Discovery Service Demo

This demo shows how to build an LLM application that dynamically discovers
and uses Skillet skills through the Discovery Service, rather than hardcoding
skill endpoints.

Key features:
- Dynamic skill discovery
- Intelligent skill selection based on user queries
- Automatic function definition generation from skill schemas
- Graceful error handling and fallbacks
"""

import os
import asyncio
import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

import httpx
import openai
from openai import OpenAI
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.prompt import Prompt
from rich.markdown import Markdown
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

console = Console()

@dataclass
class SkillInfo:
    """Information about a discovered skill."""
    name: str
    description: str
    base_url: str
    endpoints: Dict[str, str]
    category: str
    complexity: str
    use_cases: List[str]
    tags: List[str]

class SkilletDiscoveryClient:
    """Client for interacting with the Skillet Discovery Service."""
    
    def __init__(self, discovery_url: str = "http://localhost:8000"):
        self.discovery_url = discovery_url
        self.client = httpx.AsyncClient()
    
    async def search_skills(self, query: str = None, category: str = None, 
                          complexity: str = None, tags: str = None) -> List[SkillInfo]:
        """Search for skills using the Discovery Service."""
        params = {}
        if query:
            params["query"] = query
        if category:
            params["category"] = category
        if complexity:
            params["complexity"] = complexity
        if tags:
            params["tags"] = tags
        
        try:
            response = await self.client.get(f"{self.discovery_url}/search", params=params)
            response.raise_for_status()
            data = response.json()
            
            skills = []
            for skill_data in data.get("skills", []):
                skill_info = skill_data.get("skill", {})
                skills.append(SkillInfo(
                    name=skill_info.get("name", "Unknown"),
                    description=skill_info.get("description", ""),
                    base_url=skill_info.get("base_url", ""),
                    endpoints=skill_info.get("endpoints", {}),
                    category=skill_info.get("category", ""),
                    complexity=skill_info.get("complexity", ""),
                    use_cases=skill_info.get("use_cases", []),
                    tags=skill_info.get("tags", [])
                ))
            
            return skills
        except Exception as e:
            console.print(f"[red]Error searching skills: {e}[/red]")
            return []
    
    async def get_skill_schema(self, skill: SkillInfo) -> Optional[Dict[str, Any]]:
        """Get the OpenAI function schema for a skill."""
        try:
            response = await self.client.get(skill.endpoints["schema"])
            response.raise_for_status()
            return response.json()
        except Exception as e:
            console.print(f"[red]Error getting schema for {skill.name}: {e}[/red]")
            return None
    
    async def execute_skill(self, skill: SkillInfo, parameters: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Execute a skill with the given parameters."""
        try:
            response = await self.client.post(skill.endpoints["run"], json=parameters)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            console.print(f"[red]Error executing {skill.name}: {e}[/red]")
            return None
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

class IntelligentSkilletAgent:
    """An OpenAI-powered agent that can discover and use Skillet skills dynamically."""
    
    def __init__(self, discovery_client: SkilletDiscoveryClient):
        self.discovery_client = discovery_client
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.available_skills: List[SkillInfo] = []
        self.skill_functions: List[Dict[str, Any]] = []
    
    async def refresh_skills(self, query: str = None):
        """Refresh the list of available skills, optionally filtering by query."""
        console.print("[blue]🔍 Discovering available skills...[/blue]")
        
        # Search for relevant skills
        if query:
            self.available_skills = await self.discovery_client.search_skills(query=query)
        else:
            # Get all available skills
            self.available_skills = await self.discovery_client.search_skills()
        
        # Build OpenAI function definitions
        self.skill_functions = []
        for skill in self.available_skills:
            schema = await self.discovery_client.get_skill_schema(skill)
            if schema and "parameters" in schema:
                function_def = {
                    "name": schema.get("name", skill.name).replace(" ", "_").replace("-", "_").lower(),
                    "description": schema.get("description", skill.description),
                    "parameters": schema["parameters"]
                }
                self.skill_functions.append(function_def)
        
        # Display discovered skills
        if self.available_skills:
            table = Table(title="Discovered Skills")
            table.add_column("Name", style="cyan")
            table.add_column("Category", style="green")
            table.add_column("Description", style="white")
            table.add_column("Use Cases", style="yellow")
            
            for skill in self.available_skills:
                use_cases = ", ".join(skill.use_cases[:2])  # Show first 2 use cases
                if len(skill.use_cases) > 2:
                    use_cases += "..."
                table.add_row(skill.name, skill.category, skill.description[:50] + "...", use_cases)
            
            console.print(table)
        else:
            console.print("[yellow]No skills discovered. Make sure the Discovery Service and skills are running.[/yellow]")
    
    async def chat(self, user_message: str) -> str:
        """Process a user message and potentially use discovered skills."""
        # First, try to find relevant skills for this query
        await self.refresh_skills(query=user_message)
        
        if not self.skill_functions:
            return "I don't have any relevant skills available to help with that request."
        
        # Create the OpenAI chat completion with function calling
        messages = [
            {
                "role": "system",
                "content": """You are a helpful AI assistant with access to various skills through the Skillet framework. 
                
When a user asks a question:
1. Determine if any of your available functions can help answer their question
2. Call the appropriate function with the correct parameters
3. Use the function result to provide a helpful response to the user
4. If no functions are relevant, respond normally

Available skills and their purposes:
""" + "\n".join([f"- {func['name']}: {func['description']}" for func in self.skill_functions])
            },
            {
                "role": "user", 
                "content": user_message
            }
        ]
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                functions=self.skill_functions,
                function_call="auto"
            )
            
            message = response.choices[0].message
            
            # Check if OpenAI wants to call a function
            if message.function_call:
                function_name = message.function_call.name
                function_args = json.loads(message.function_call.arguments)
                
                # Find the corresponding skill
                skill = None
                for s in self.available_skills:
                    skill_func_name = s.name.replace(" ", "_").replace("-", "_").lower()
                    if skill_func_name == function_name:
                        skill = s
                        break
                
                if skill:
                    console.print(f"[green]🔧 Using {skill.name} skill...[/green]")
                    
                    # Execute the skill
                    result = await self.discovery_client.execute_skill(skill, function_args)
                    
                    if result:
                        # Send the function result back to OpenAI for a final response
                        messages.append({
                            "role": "assistant",
                            "content": None,
                            "function_call": {
                                "name": function_name,
                                "arguments": message.function_call.arguments
                            }
                        })
                        messages.append({
                            "role": "function",
                            "name": function_name,
                            "content": json.dumps(result)
                        })
                        
                        final_response = self.openai_client.chat.completions.create(
                            model="gpt-4",
                            messages=messages
                        )
                        
                        return final_response.choices[0].message.content
                    else:
                        return f"I tried to use the {skill.name} skill, but it didn't respond properly."
                else:
                    return f"I wanted to use a skill called {function_name}, but I couldn't find it."
            else:
                # No function call needed, return the direct response
                return message.content
                
        except Exception as e:
            console.print(f"[red]Error in chat: {e}[/red]")
            return "I encountered an error while processing your request."

async def main():
    """Main demo function."""
    console.print(Panel.fit(
        "[bold blue]OpenAI + Skillet Discovery Service Demo[/bold blue]\n"
        "This demo shows dynamic skill discovery and usage with OpenAI.",
        title="🤖 Intelligent Skillet Agent"
    ))
    
    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        console.print("[red]❌ OpenAI API key not found![/red]")
        console.print("Please set your OPENAI_API_KEY environment variable or add it to a .env file.")
        return
    
    # Initialize the discovery client and agent
    discovery_client = SkilletDiscoveryClient()
    agent = IntelligentSkilletAgent(discovery_client)
    
    console.print("\n[green]✅ Agent initialized![/green]")
    console.print("[dim]The agent will automatically discover and use relevant skills for your queries.[/dim]")
    
    # Interactive loop
    try:
        while True:
            console.print("\n" + "="*60)
            user_input = Prompt.ask("\n[bold cyan]You[/bold cyan]", default="quit")
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                break
            
            console.print(f"\n[bold green]Agent[/bold green]: Thinking...")
            response = await agent.chat(user_input)
            
            # Display the response nicely
            console.print(f"\n[bold green]Agent[/bold green]: {response}")
    
    except KeyboardInterrupt:
        console.print("\n[yellow]Demo interrupted by user.[/yellow]")
    
    finally:
        await discovery_client.close()
        console.print("[green]✅ Demo completed![/green]")

if __name__ == "__main__":
    asyncio.run(main()) 