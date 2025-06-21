"""
Skillet Multi-Skill Runtime Host

A FastAPI application that can dynamically load and host multiple Skillet skills
in a single service, while preserving individual skill functionality and APIs.

Key features:
- Dynamic skill loading from configuration
- Preserves individual skill endpoints (/skills/{name}/...)
- Unified discovery endpoints (/catalog, /inventory)
- Flexible deployment (standalone skills OR consolidated host)
- Hot-reloading of skill configurations
"""

import os
import sys
import importlib.util
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

@dataclass
class SkillConfig:
    """Configuration for a loaded skill."""
    name: str
    path: str
    mount_path: str
    enabled: bool
    module: Any = None
    app: Any = None
    metadata: Dict[str, Any] = None

class MultiSkillHost:
    """
    Multi-Skill FastAPI Host that can dynamically load and serve multiple Skillet skills.
    """
    
    def __init__(self, config_path: str = "runtime-config.yaml", base_path: str = "."):
        self.config_path = config_path
        self.base_path = Path(base_path).resolve()
        self.skills: Dict[str, SkillConfig] = {}
        
        # Create the main FastAPI app
        self.app = FastAPI(
            title="Skillet Multi-Skill Runtime Host",
            description="Dynamically hosts multiple Skillet skills in a single service",
            version="1.0.0"
        )
        
        # Add CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Setup unified endpoints
        self.setup_unified_endpoints()
        
        # Load skills from configuration
        self.load_skills_from_config()
    
    def load_skills_from_config(self):
        """Load skills based on configuration file."""
        if not os.path.exists(self.config_path):
            print(f"⚠️  Configuration file {self.config_path} not found.")
            
            # Check if example config exists
            example_config = self.config_path.replace('.yaml', '.example.yaml')
            if os.path.exists(example_config):
                print(f"📋 Using example configuration: {example_config}")
                import shutil
                shutil.copy2(example_config, self.config_path)
                print(f"📝 Copied {example_config} → {self.config_path}")
            else:
                print("🔍 Creating default config with auto-discovery.")
                self.create_default_config()
        
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f) or {}
            
            skills_config = config.get('skills', [])
            print(f"📋 Loading {len(skills_config)} skills from configuration...")
            
            for skill_config in skills_config:
                if skill_config.get('enabled', True):
                    self.load_skill(skill_config)
                else:
                    print(f"⏭️  Skipping disabled skill: {skill_config.get('name', 'unknown')}")
            
            print(f"✅ Successfully loaded {len(self.skills)} skills")
            
        except Exception as e:
            print(f"❌ Error loading configuration: {e}")
            raise
    
    def create_default_config(self):
        """Create a default configuration file by auto-discovering all example skills."""
        print("🔍 Auto-discovering skills in examples directory...")
        
        # Auto-discover all skills in examples directory
        examples_dir = self.base_path / "examples"
        discovered_skills = []
        
        if examples_dir.exists():
            for skill_dir in examples_dir.iterdir():
                if skill_dir.is_dir() and (skill_dir / "skillet_runtime.py").exists():
                    skill_name = skill_dir.name
                    mount_name = skill_name.replace("_", "-")  # Use hyphens for URL-friendly mount paths
                    
                    discovered_skills.append({
                        'name': f'{skill_name}_skill',
                        'path': f'./examples/{skill_name}',
                        'mount': mount_name,
                        'enabled': True
                    })
                    print(f"  ✅ Found skill: {skill_name}")
        
        # Sort skills alphabetically for consistent ordering
        discovered_skills.sort(key=lambda x: x['name'])
        
        default_config = {
            'skills': discovered_skills,
            'server': {
                'host': '0.0.0.0',
                'port': 8000,
                'reload': True
            }
        }
        
        with open(self.config_path, 'w') as f:
            yaml.dump(default_config, f, default_flow_style=False, indent=2)
        
        print(f"📝 Created default configuration with {len(discovered_skills)} skills: {self.config_path}")
        print(f"🎯 Discovered skills: {', '.join([s['name'] for s in discovered_skills])}")
    
    def load_skill(self, skill_config: Dict[str, Any]):
        """Load a single skill and mount it to the main app."""
        skill_name = skill_config.get('name', 'unknown')
        skill_path = skill_config.get('path', '')
        mount_path = skill_config.get('mount', skill_name)
        
        print(f"🔧 Loading skill: {skill_name} from {skill_path}")
        
        try:
            # Resolve the full path
            full_path = (self.base_path / skill_path).resolve()
            runtime_file = full_path / "skillet_runtime.py"
            
            if not runtime_file.exists():
                print(f"❌ Skill runtime not found: {runtime_file}")
                return
            
            # Add the skill directory to Python path temporarily
            skill_dir = str(full_path)
            if skill_dir not in sys.path:
                sys.path.insert(0, skill_dir)
            
            try:
                # Import the skill module
                spec = importlib.util.spec_from_file_location(
                    f"skill_{skill_name}", str(runtime_file)
                )
                skill_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(skill_module)
                
                # Get the FastAPI app from the skill
                if hasattr(skill_module, 'app'):
                    skill_app = skill_module.app
                    
                    # Mount the skill app under /skills/{mount_path}
                    mount_point = f"/skills/{mount_path}"
                    self.app.mount(mount_point, skill_app)
                    
                    # Store skill information
                    skill_info = SkillConfig(
                        name=skill_name,
                        path=skill_path,
                        mount_path=mount_path,
                        enabled=True,
                        module=skill_module,
                        app=skill_app
                    )
                    
                    self.skills[mount_path] = skill_info
                    print(f"✅ Mounted skill '{skill_name}' at {mount_point}")
                    
                else:
                    print(f"❌ Skill module does not have 'app' attribute: {skill_name}")
                    
            finally:
                # Remove from path to avoid conflicts
                if skill_dir in sys.path:
                    sys.path.remove(skill_dir)
                    
        except Exception as e:
            print(f"❌ Failed to load skill '{skill_name}': {e}")
            import traceback
            traceback.print_exc()
    
    def setup_unified_endpoints(self):
        """Setup unified endpoints for the multi-skill host."""
        
        @self.app.get("/")
        async def root():
            """Root endpoint with service information."""
            return {
                "service": "Skillet Multi-Skill Runtime Host",
                "version": "1.0.0",
                "loaded_skills": len(self.skills),
                "skills": {
                    name: {
                        "mount_path": f"/skills/{skill.mount_path}",
                        "endpoints": {
                            "inventory": f"/skills/{skill.mount_path}/inventory",
                            "schema": f"/skills/{skill.mount_path}/schema",
                            "run": f"/skills/{skill.mount_path}/run"
                        }
                    }
                    for name, skill in self.skills.items()
                }
            }
        
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint."""
            return {
                "status": "healthy",
                "loaded_skills": len(self.skills),
                "skills": {
                    name: {
                        "status": "loaded",
                        "mount_path": skill.mount_path
                    }
                    for name, skill in self.skills.items()
                }
            }
        
        @self.app.get("/catalog")
        async def get_catalog():
            """Get unified catalog of all loaded skills."""
            catalog = {
                "runtime_host": {
                    "name": "Skillet Multi-Skill Runtime Host",
                    "version": "1.0.0",
                    "total_skills": len(self.skills),
                    "base_url": "http://localhost:8000"  # TODO: Make configurable
                },
                "skills": []
            }
            
            # Collect inventory from each skill
            for skill_name, skill in self.skills.items():
                try:
                    # Try to get inventory from the skill
                    inventory = await self.get_skill_inventory(skill_name)
                    if inventory and "skill" in inventory:
                        # Enhance with runtime host information
                        inventory["skill"]["base_url"] = f"http://localhost:8000/skills/{skill_name}"
                        inventory["skill"]["endpoints"] = {
                            "inventory": f"/skills/{skill_name}/inventory",
                            "schema": f"/skills/{skill_name}/schema",
                            "run": f"/skills/{skill_name}/run"
                        }
                        catalog["skills"].append(inventory)
                except Exception as e:
                    print(f"⚠️  Could not get inventory for skill '{skill_name}': {e}")
                    # Add placeholder for unavailable skill
                    catalog["skills"].append({
                        "skill": {
                            "name": skill_name,
                            "status": "loaded_but_no_inventory",
                            "mount_path": skill.mount_path,
                            "error": str(e)
                        }
                    })
            
            return catalog
        
        @self.app.get("/skills")
        async def get_skills():
            """Get list of loaded skills with their endpoints."""
            return {
                "total_skills": len(self.skills),
                "skills": [
                    {
                        "name": skill.name,
                        "mount_path": skill.mount_path,
                        "endpoints": {
                            "inventory": f"/skills/{skill.mount_path}/inventory",
                            "schema": f"/skills/{skill.mount_path}/schema",
                            "run": f"/skills/{skill.mount_path}/run"
                        }
                    }
                    for skill in self.skills.values()
                ]
            }
        
        @self.app.post("/reload")
        async def reload_skills():
            """Reload skills from configuration (hot reload)."""
            try:
                # Clear existing skills
                old_skills = list(self.skills.keys())
                self.skills.clear()
                
                # Reload from config
                self.load_skills_from_config()
                
                return {
                    "message": "Skills reloaded successfully",
                    "old_skills": old_skills,
                    "new_skills": list(self.skills.keys()),
                    "total_loaded": len(self.skills)
                }
            except Exception as e:
                return JSONResponse(
                    status_code=500,
                    content={"error": f"Failed to reload skills: {e}"}
                )
        
        @self.app.post("/rediscover")
        async def rediscover_skills():
            """Rediscover skills from examples directory and update configuration."""
            try:
                print("🔍 Rediscovering skills...")
                
                # Backup existing config if it exists
                if os.path.exists(self.config_path):
                    import shutil
                    backup_path = f"{self.config_path}.backup"
                    shutil.copy2(self.config_path, backup_path)
                    print(f"💾 Backed up existing config to: {backup_path}")
                
                # Create new config with auto-discovery
                self.create_default_config()
                
                # Clear and reload skills
                old_skills = list(self.skills.keys())
                self.skills.clear()
                self.load_skills_from_config()
                
                return {
                    "message": f"Rediscovered and loaded {len(self.skills)} skills",
                    "old_skills": old_skills,
                    "new_skills": list(self.skills.keys()),
                    "total_loaded": len(self.skills),
                    "skills": {
                        name: {
                            "name": skill.name,
                            "mount_path": skill.mount_path,
                            "path": skill.path
                        }
                        for name, skill in self.skills.items()
                    }
                }
                
            except Exception as e:
                return JSONResponse(
                    status_code=500,
                    content={"error": f"Failed to rediscover skills: {e}"}
                )
    
    async def get_skill_inventory(self, skill_name: str) -> Optional[Dict[str, Any]]:
        """Get inventory from a specific skill."""
        if skill_name not in self.skills:
            return None
        
        skill = self.skills[skill_name]
        
        # Try to call the skill's inventory endpoint
        try:
            # This is a bit hacky, but we need to simulate a request to the skill's inventory endpoint
            # In a real implementation, you might want to have skills expose their inventory function directly
            
            # For now, we'll try to access the skill's inventory function if it exists
            if hasattr(skill.module, 'get_inventory'):
                return await skill.module.get_inventory()
            elif hasattr(skill.module, 'inventory'):
                return skill.module.inventory()
            else:
                # Fallback: return basic info
                return {
                    "skill": {
                        "name": skill.name,
                        "mount_path": skill.mount_path,
                        "status": "loaded"
                    }
                }
        except Exception as e:
            print(f"⚠️  Error getting inventory for {skill_name}: {e}")
            return None

def create_app(config_path: str = "runtime-config.yaml", base_path: str = ".") -> FastAPI:
    """Create and configure the multi-skill host app."""
    host = MultiSkillHost(config_path=config_path, base_path=base_path)
    return host.app

def main():
    """Main entry point for running the multi-skill host."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Skillet Multi-Skill Runtime Host")
    parser.add_argument("--config", default="runtime-config.yaml", help="Configuration file path")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    
    args = parser.parse_args()
    
    print("🚀 Starting Skillet Multi-Skill Runtime Host")
    print(f"📋 Configuration: {args.config}")
    print(f"🌐 Server: {args.host}:{args.port}")
    
    # Create the app
    app = create_app(config_path=args.config)
    
    # Run the server
    uvicorn.run(
        "multi_skill_host:create_app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        factory=True
    )

if __name__ == "__main__":
    main() 