"""
Skillet Discovery Service

A simple aggregation service that polls multiple Skillet skills and provides
a unified catalog of available skills for LLM agents to discover and use.
"""

import asyncio
import json
import os
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException
import httpx
import yaml
from datetime import datetime

app = FastAPI(
    title="Skillet Discovery Service",
    description="Aggregates and serves a catalog of available Skillet skills",
    version="0.1.0"
)

# Global cache for skill inventories
skill_catalog: Dict[str, Any] = {}
last_updated: Optional[datetime] = None

def load_skill_urls() -> List[str]:
    """Load skill URLs from configuration file or environment variables."""
    
    # Try to load from config file first
    config_file = os.getenv("SKILLET_CONFIG", "skills.yaml")
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
            return config.get("skills", [])
    
    # Fall back to environment variable
    skills_env = os.getenv("SKILLET_SKILLS", "")
    if skills_env:
        return [url.strip() for url in skills_env.split(",") if url.strip()]
    
    # Default to local examples for testing
    return [
        "http://localhost:8001",  # anthropic_time
        "http://localhost:8002",  # anthropic_fetch  
        "http://localhost:8003",  # anthropic_memory
    ]

async def fetch_skill_inventory(client: httpx.AsyncClient, base_url: str) -> Optional[Dict[str, Any]]:
    """Fetch inventory from a single Skillet skill."""
    try:
        response = await client.get(f"{base_url}/inventory", timeout=5.0)
        response.raise_for_status()
        inventory = response.json()
        
        # Add metadata about the skill endpoint
        if "skill" in inventory:
            inventory["skill"]["base_url"] = base_url
            inventory["skill"]["endpoints"] = {
                "inventory": f"{base_url}/inventory",
                "schema": f"{base_url}/schema",
                "run": f"{base_url}/run"
            }
        
        return inventory
    except Exception as e:
        print(f"Failed to fetch inventory from {base_url}: {e}")
        return None

async def update_skill_catalog():
    """Update the global skill catalog by polling all configured skills."""
    global skill_catalog, last_updated
    
    skill_urls = load_skill_urls()
    new_catalog = {
        "discovery_service": {
            "name": "Skillet Discovery Service",
            "version": "0.1.0",
            "last_updated": datetime.now().isoformat(),
            "total_skills": 0,
            "available_skills": 0
        },
        "skills": []
    }
    
    async with httpx.AsyncClient() as client:
        # Fetch inventories from all skills concurrently
        tasks = [fetch_skill_inventory(client, url) for url in skill_urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for url, result in zip(skill_urls, results):
            new_catalog["discovery_service"]["total_skills"] += 1
            
            if result and not isinstance(result, Exception):
                new_catalog["skills"].append(result)
                new_catalog["discovery_service"]["available_skills"] += 1
            else:
                # Add placeholder for unavailable skills
                new_catalog["skills"].append({
                    "skill": {
                        "name": f"unavailable_skill_{url.split('/')[-1]}",
                        "base_url": url,
                        "status": "unavailable",
                        "error": str(result) if isinstance(result, Exception) else "No response"
                    }
                })
    
    skill_catalog = new_catalog
    last_updated = datetime.now()
    print(f"Updated skill catalog: {new_catalog['discovery_service']['available_skills']}/{new_catalog['discovery_service']['total_skills']} skills available")

@app.on_event("startup")
async def startup_event():
    """Initialize the skill catalog on startup."""
    await update_skill_catalog()

@app.get("/catalog")
async def get_skill_catalog():
    """Get the complete catalog of available Skillet skills."""
    if not skill_catalog:
        await update_skill_catalog()
    
    return skill_catalog

@app.get("/skills")
async def get_available_skills():
    """Get just the available skills (filtered to remove unavailable ones)."""
    if not skill_catalog:
        await update_skill_catalog()
    
    available_skills = [
        skill for skill in skill_catalog.get("skills", [])
        if skill.get("skill", {}).get("status") != "unavailable"
    ]
    
    return {
        "available_skills": len(available_skills),
        "skills": available_skills
    }

@app.get("/search")
async def search_skills(
    query: str = None,
    category: str = None,
    complexity: str = None,
    tags: str = None
):
    """Search skills by various criteria."""
    if not skill_catalog:
        await update_skill_catalog()
    
    available_skills = [
        skill for skill in skill_catalog.get("skills", [])
        if skill.get("skill", {}).get("status") != "unavailable"
    ]
    
    filtered_skills = available_skills
    
    # Apply filters
    if query:
        query_lower = query.lower()
        filtered_skills = [
            skill for skill in filtered_skills
            if (query_lower in skill.get("skill", {}).get("name", "").lower() or
                query_lower in skill.get("skill", {}).get("description", "").lower() or
                any(query_lower in uc.lower() for uc in skill.get("skill", {}).get("use_cases", [])) or
                any(query_lower in eq.lower() for eq in skill.get("skill", {}).get("example_queries", [])))
        ]
    
    if category:
        filtered_skills = [
            skill for skill in filtered_skills
            if skill.get("skill", {}).get("category", "").lower() == category.lower()
        ]
    
    if complexity:
        filtered_skills = [
            skill for skill in filtered_skills
            if skill.get("skill", {}).get("complexity", "").lower() == complexity.lower()
        ]
    
    if tags:
        tag_list = [tag.strip().lower() for tag in tags.split(",")]
        filtered_skills = [
            skill for skill in filtered_skills
            if any(tag in [t.lower() for t in skill.get("skill", {}).get("tags", [])] for tag in tag_list)
        ]
    
    return {
        "query": {
            "text": query,
            "category": category,
            "complexity": complexity,
            "tags": tags
        },
        "results": len(filtered_skills),
        "skills": filtered_skills
    }

@app.post("/refresh")
async def refresh_catalog():
    """Manually refresh the skill catalog."""
    await update_skill_catalog()
    return {
        "message": "Skill catalog refreshed",
        "last_updated": last_updated.isoformat() if last_updated else None,
        "available_skills": skill_catalog.get("discovery_service", {}).get("available_skills", 0),
        "total_skills": skill_catalog.get("discovery_service", {}).get("total_skills", 0)
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "last_updated": last_updated.isoformat() if last_updated else None,
        "catalog_size": len(skill_catalog.get("skills", []))
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 