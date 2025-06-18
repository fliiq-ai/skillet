"""
Multi-Skill Runtime Demo with OpenAI Integration

This demo shows how to use the Skillet Multi-Skill Runtime Host with OpenAI,
demonstrating the consolidated hosting approach where multiple skills are
served from a single endpoint.

Key features:
- Single service hosting multiple skills
- Preserved individual skill APIs
- Unified discovery and management
- Seamless OpenAI integration
"""

import os
import asyncio
import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

import httpx
from openai import OpenAI
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt
from rich.text import Text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

console = Console()

@dataclass
class ConsolidatedSkill:
    """Information about a skill hosted in the multi-skill runtime."""
    name: str
    description: str
    mount_path: str
    endpoints: Dict[str, str]
    category: str
    complexity: str
    use_cases: List[str]

class MultiSkillRuntimeClient:
    """Client for interacting with the Multi-Skill Runtime Host."""
    
    def __init__(self, runtime_url: str = "http://localhost:8000"):
        self.runtime_url = runtime_url
        self.client = httpx.AsyncClient()
    
    async def get_service_info(self) -> Dict[str, Any]:
        """Get information about the multi-skill runtime service."""
        try:
            response = await self.client.get(f"{self.runtime_url}/")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            console.print(f"[red]Error getting service info: {e}[/red]")
            return {}
    
    async def get_consolidated_skills(self) -> List[ConsolidatedSkill]:
        """Get all skills hosted in the runtime."""
        try:
            response = await self.client.get(f"{self.runtime_url}/catalog")
            response.raise_for_status()
            data = response.json()
            
            skills = []
            for skill_data in data.get("skills", []):
                skill_info = skill_data.get("skill", {})
                skills.append(ConsolidatedSkill(
                    name=skill_info.get("name", "Unknown"),
                    description=skill_info.get("description", ""),
                    mount_path=skill_info.get("mount_path", ""),
                    endpoints=skill_info.get("endpoints", {}),
                    category=skill_info.get("category", ""),
                    complexity=skill_info.get("complexity", ""),
                    use_cases=skill_info.get("use_cases", [])
                ))
            
            return skills
        except Exception as e:
            console.print(f"[red]Error getting consolidated skills: {e}[/red]")
            return []
    
    async def get_skill_schema(self, skill: ConsolidatedSkill) -> Optional[Dict[str, Any]]:
        """Get the OpenAI function schema for a consolidated skill."""
        try:
            schema_url = f"{self.runtime_url}{skill.endpoints['schema']}"
            response = await self.client.get(schema_url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            console.print(f"[red]Error getting schema for {skill.name}: {e}[/red]")
            return None
    
    async def execute_skill(self, skill: ConsolidatedSkill, parameters: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Execute a skill with the given parameters."""
        try:
            run_url = f"{self.runtime_url}{skill.endpoints['run']}"
            response = await self.client.post(run_url, json=parameters)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            console.print(f"[red]Error executing {skill.name}: {e}[/red]")
            return None
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Get the health status of the runtime host."""
        try:
            response = await self.client.get(f"{self.runtime_url}/health")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            console.print(f"[red]Error getting health status: {e}[/red]")
            return {}
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

class ConsolidatedSkilletAgent:
    """An OpenAI-powered agent that uses the Multi-Skill Runtime Host."""
    
    def __init__(self, runtime_client: MultiSkillRuntimeClient):
        self.runtime_client = runtime_client
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.available_skills: List[ConsolidatedSkill] = []
        self.skill_functions: List[Dict[str, Any]] = []
    
    async def initialize(self):
        """Initialize the agent by loading skills from the runtime host."""
        console.print("[blue]🔧 Connecting to Multi-Skill Runtime Host...[/blue]")
        
        # Get service info
        service_info = await self.runtime_client.get_service_info()
        if service_info:
            console.print(f"[green]✅ Connected to: {service_info.get('service', 'Unknown Service')}[/green]")
            console.print(f"[dim]Loaded skills: {service_info.get('loaded_skills', 0)}[/dim]")
        
        # Get available skills
        self.available_skills = await self.runtime_client.get_consolidated_skills()
        
        # Build OpenAI function definitions
        self.skill_functions = []
        for skill in self.available_skills:
            schema = await self.runtime_client.get_skill_schema(skill)
            if schema and "parameters" in schema:
                function_def = {
                    "name": schema.get("name", skill.name).replace(" ", "_").replace("-", "_").lower(),
                    "description": schema.get("description", skill.description),
                    "parameters": schema["parameters"]
                }
                self.skill_functions.append(function_def)
        
        # Display consolidated skills
        if self.available_skills:
            table = Table(title="Consolidated Skills (Single Runtime Host)")
            table.add_column("Name", style="cyan")
            table.add_column("Mount Path", style="green")
            table.add_column("Category", style="yellow")
            table.add_column("Description", style="white")
            
            for skill in self.available_skills:
                table.add_row(
                    skill.name,
                    skill.mount_path,
                    skill.category,
                    skill.description[:40] + "..." if len(skill.description) > 40 else skill.description
                )
            
            console.print(table)
        else:
            console.print("[yellow]No skills found in the runtime host.[/yellow]")
    
    async def chat(self, user_message: str) -> str:
        """Process a user message using consolidated skills."""
        if not self.skill_functions:
            return "No skills are available in the runtime host."
        
        # Create the OpenAI chat completion with function calling
        messages = [
            {
                "role": "system",
                "content": f"""You are a helpful AI assistant with access to skills hosted in a consolidated Skillet Multi-Skill Runtime.

All skills are available from a single service endpoint, making the system more efficient and easier to manage.

Available skills:
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
                    console.print(f"[green]🔧 Using {skill.name} (via consolidated runtime)...[/green]")
                    
                    # Execute the skill
                    result = await self.runtime_client.execute_skill(skill, function_args)
                    
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
                    return f"I wanted to use a skill called {function_name}, but I couldn't find it in the runtime."
            else:
                # No function call needed, return the direct response
                return message.content
                
        except Exception as e:
            console.print(f"[red]Error in chat: {e}[/red]")
            return "I encountered an error while processing your request."

async def demonstrate_consolidated_benefits():
    """Demonstrate the benefits of consolidated skill hosting."""
    console.print(Panel.fit(
        "[bold blue]Multi-Skill Runtime Benefits Demo[/bold blue]\n"
        "This demo shows the advantages of consolidated skill hosting.",
        title="🏠 Consolidated vs. Microservices"
    ))
    
    runtime_client = MultiSkillRuntimeClient()
    
    # Show service information
    service_info = await runtime_client.get_service_info()
    health_status = await runtime_client.get_health_status()
    
    console.print("\n[bold green]📊 Service Overview[/bold green]")
    console.print(f"Service: {service_info.get('service', 'Unknown')}")
    console.print(f"Total Skills: {service_info.get('loaded_skills', 0)}")
    console.print(f"Status: {health_status.get('status', 'Unknown')}")
    
    # Show individual skill endpoints
    console.print("\n[bold green]🔗 Individual Skill Endpoints (Preserved)[/bold green]")
    for skill_name, skill_info in service_info.get('skills', {}).items():
        console.print(f"  {skill_name}:")
        for endpoint_name, endpoint_path in skill_info.get('endpoints', {}).items():
            console.print(f"    {endpoint_name}: {endpoint_path}")
    
    # Show consolidated advantages
    console.print("\n[bold green]✅ Consolidated Hosting Advantages[/bold green]")
    advantages = [
        "Single service to manage (vs. 3+ separate services)",
        "One port to monitor (vs. multiple ports)",
        "Unified health checking and monitoring",
        "Simplified deployment and scaling",
        "Preserved individual skill APIs",
        "Hot-reloading of skill configurations"
    ]
    
    for advantage in advantages:
        console.print(f"  • {advantage}")
    
    await runtime_client.close()

async def main():
    """Main demo function."""
    console.print(Panel.fit(
        "[bold blue]Multi-Skill Runtime Demo with OpenAI[/bold blue]\n"
        "Experience the power of consolidated skill hosting!",
        title="🚀 Skillet Multi-Skill Runtime"
    ))
    
    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        console.print("[red]❌ OpenAI API key not found![/red]")
        console.print("Please set your OPENAI_API_KEY environment variable or add it to a .env file.")
        return
    
    # Initialize the runtime client and agent
    runtime_client = MultiSkillRuntimeClient()
    agent = ConsolidatedSkilletAgent(runtime_client)
    
    try:
        await agent.initialize()
        
        # Demonstrate consolidated benefits
        await demonstrate_consolidated_benefits()
        
        console.print("\n[green]✅ Agent initialized with consolidated skills![/green]")
        console.print("[dim]All skills are hosted in a single runtime service.[/dim]")
        
        # Interactive loop
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
        await runtime_client.close()
        console.print("[green]✅ Demo completed![/green]")

if __name__ == "__main__":
    asyncio.run(main()) 