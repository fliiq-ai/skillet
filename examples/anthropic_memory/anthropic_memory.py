# This is a simple in-memory store.
# Data will be lost when the server process restarts.
MEMORY_STORE = {}

import os
import json
from typing import Dict, List, Any, Optional
from fastapi import HTTPException
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get the directory where this script is located for the memory file
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MEMORY_FILE_PATH = os.getenv("MEMORY_FILE_PATH", os.path.join(SCRIPT_DIR, "memory.json"))

class KnowledgeGraph:
    """Manages the knowledge graph, including persistence."""
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.entities: Dict[str, Dict[str, Any]] = {}
        self.relations: List[Dict[str, str]] = []
        self._load()

    def _load(self):
        """Loads the graph from the JSON file."""
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, 'r') as f:
                    data = json.load(f)
                    self.entities = data.get("entities", {})
                    self.relations = data.get("relations", [])
                logger.info(f"Knowledge graph loaded from {self.filepath}")
            except (json.JSONDecodeError, IOError) as e:
                logger.error(f"Error loading {self.filepath}: {e}. Starting with an empty graph.")
                self.entities, self.relations = {}, []
        else:
            logger.info("No memory file found. Starting with an empty graph.")

    def _save(self):
        """Saves the graph to the JSON file."""
        try:
            with open(self.filepath, 'w') as f:
                json.dump({"entities": self.entities, "relations": self.relations}, f, indent=2)
            logger.info(f"Knowledge graph saved to {self.filepath}")
        except IOError as e:
            logger.error(f"Error saving to {self.filepath}: {e}")
            raise HTTPException(status_code=500, detail="Failed to save knowledge graph.")

    def create_entities(self, entities: List[Dict]) -> Dict:
        count = 0
        for entity in entities:
            name = entity.get("name")
            if name and name not in self.entities:
                self.entities[name] = {
                    "entityType": entity.get("entityType", "unknown"),
                    "observations": list(set(entity.get("observations", [])))
                }
                count += 1
        if count > 0:
            self._save()
        return {"success": True, "message": f"Successfully created {count} new entities."}

    def create_relations(self, relations: List[Dict]) -> Dict:
        count = 0
        for rel in relations:
            if rel.get("from") in self.entities and rel.get("to") in self.entities:
                if rel not in self.relations:
                    self.relations.append(rel)
                    count += 1
        if count > 0:
            self._save()
        return {"success": True, "message": f"Successfully created {count} new relations."}

    def add_observations(self, observations: List[Dict]) -> Dict:
        updated_count = 0
        for obs in observations:
            entity_name = obs.get("entityName")
            if entity_name in self.entities:
                existing_obs = set(self.entities[entity_name].get("observations", []))
                new_obs = set(obs.get("contents", []))
                original_size = len(existing_obs)
                existing_obs.update(new_obs)
                if len(existing_obs) > original_size:
                    self.entities[entity_name]["observations"] = list(existing_obs)
                    updated_count += 1
        if updated_count > 0:
            self._save()
        return {"success": True, "message": f"Observations added to {updated_count} entities."}

    def delete_entities(self, entity_names: List[str]) -> Dict:
        deleted_count = 0
        for name in entity_names:
            if name in self.entities:
                del self.entities[name]
                self.relations = [r for r in self.relations if r['from'] != name and r['to'] != name]
                deleted_count += 1
        if deleted_count > 0:
            self._save()
        return {"success": True, "message": f"Successfully deleted {deleted_count} entities."}

    def delete_observations(self, deletions: List[Dict]) -> Dict:
        updated_count = 0
        for item in deletions:
            name = item.get("entityName")
            if name in self.entities:
                obs_to_delete = set(item.get("observations", []))
                current_obs = set(self.entities[name].get("observations", []))
                original_size = len(current_obs)
                current_obs -= obs_to_delete
                if len(current_obs) < original_size:
                     self.entities[name]["observations"] = list(current_obs)
                     updated_count += 1
        if updated_count > 0:
            self._save()
        return {"success": True, "message": f"Observations deleted from {updated_count} entities."}

    def delete_relations(self, relations_to_delete: List[Dict]) -> Dict:
        original_count = len(self.relations)
        self.relations = [r for r in self.relations if r not in relations_to_delete]
        deleted_count = original_count - len(self.relations)
        if deleted_count > 0:
            self._save()
        return {"success": True, "message": f"Successfully deleted {deleted_count} relations."}

    def read_graph(self) -> Dict:
        return {"success": True, "graph": {"entities": self.entities, "relations": self.relations}}

    def search_nodes(self, query: str) -> Dict:
        if not query:
            return {"success": False, "nodes": [], "message": "Query cannot be empty."}
        
        query = query.lower()
        results = []
        for name, data in self.entities.items():
            if query in name.lower() or query in data.get('entityType', '').lower() \
               or any(query in obs.lower() for obs in data.get('observations', [])):
                results.append({"name": name, **data})
        return {"success": True, "nodes": results}

    def open_nodes(self, names: List[str]) -> Dict:
        results = [{"name": name, **self.entities[name]} for name in names if name in self.entities]
        return {"success": True, "nodes": results}

# Create a single, global instance of the knowledge graph.
# This is crucial for maintaining state between requests.
graph = KnowledgeGraph(MEMORY_FILE_PATH)

def handler(params: dict) -> dict:
    """Dispatches requests to the appropriate KnowledgeGraph method."""
    operation = params.get("operation")
    if not operation:
        raise HTTPException(status_code=400, detail="'operation' field is required.")

    # The 'params' value is expected to be a JSON STRING from the request.
    # Load it into a Python dict. Default to an empty JSON object string.
    args_str = params.get("params", "{}")
    try:
        # Handle the case where params might not be provided for no-arg operations
        args = json.loads(args_str) if args_str else {}
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON format in 'params' field.")

    dispatch_map = {
        "create_entities": (graph.create_entities, "entities"),
        "create_relations": (graph.create_relations, "relations"),
        "add_observations": (graph.add_observations, "observations"),
        "delete_entities": (graph.delete_entities, "entityNames"),
        "delete_observations": (graph.delete_observations, "deletions"),
        "delete_relations": (graph.delete_relations, "relations"),
        "read_graph": (graph.read_graph, None),
        "search_nodes": (graph.search_nodes, "query"),
        "open_nodes": (graph.open_nodes, "names"),
    }

    if operation not in dispatch_map:
        raise HTTPException(status_code=400, detail=f"Invalid operation: {operation}")

    method, param_key = dispatch_map[operation]
    
    result = {}
    if param_key:
        if param_key not in args:
             raise HTTPException(status_code=400, detail=f"Missing required parameter '{param_key}' for operation '{operation}'.")
        result = method(args[param_key])
    else:
        result = method()
    
    # The 'response' field must be a JSON STRING in the final response.
    return {"response": json.dumps(result)} 