#!/bin/bash
# Test script for the Knowledge Graph Memory Skillet

BASE_URL="http://127.0.0.1:8000/run"
MEMORY_FILE="memory.json"

# Cleanup previous test runs
rm -f "$MEMORY_FILE"

echo "--- Testing Knowledge Graph Memory Skillet ---"

# Helper function to make requests
run_curl() {
  echo -e "\n$1"
  curl -s -X POST "${BASE_URL}" \
    -H "Content-Type: application/json" \
    -d "$2" | (json_pp || cat) # Pretty-print JSON if json_pp is available
  echo ""
}

# 1. Create entities
PARAMS='{\"entities\":[{\"name\":\"John_Smith\",\"entityType\":\"person\",\"observations\":[\"Speaks fluent Spanish\"]},{\"name\":\"Anthropic\",\"entityType\":\"organization\"}]}'
run_curl "1. Creating entities: 'John_Smith' and 'Anthropic'..." \
  "{\"operation\": \"create_entities\", \"params\": \"$PARAMS\"}"

# 2. Create relation
PARAMS='{\"relations\":[{\"from\":\"John_Smith\",\"to\":\"Anthropic\",\"relationType\":\"works_at\"}]}'
run_curl "2. Creating relation: John_Smith works_at Anthropic..." \
  "{\"operation\": \"create_relations\", \"params\": \"$PARAMS\"}"

# 3. Add observations
PARAMS='{\"observations\":[{\"entityName\":\"John_Smith\",\"contents\":[\"Graduated in 2019\",\"Prefers morning meetings\"]}]}'
run_curl "3. Adding observations to John_Smith..." \
  "{\"operation\": \"add_observations\", \"params\": \"$PARAMS\"}"

# 4. Read the entire graph to verify
run_curl "4. Reading graph to verify state..." \
  '{"operation": "read_graph"}'

# 5. Search for a node
PARAMS='{\"query\":\"spanish\"}'
run_curl "5. Searching for nodes with query 'spanish'..." \
  "{\"operation\": \"search_nodes\", \"params\": \"$PARAMS\"}"

# 6. Open a specific node
PARAMS='{\"names\":[\"Anthropic\"]}'
run_curl "6. Opening node 'Anthropic'..." \
  "{\"operation\": \"open_nodes\", \"params\": \"$PARAMS\"}"

# 7. Delete an observation
PARAMS='{\"deletions\":[{\"entityName\":\"John_Smith\",\"observations\":[\"Speaks fluent Spanish\"]}]}'
run_curl "7. Deleting an observation from John_Smith..." \
  "{\"operation\": \"delete_observations\", \"params\": \"$PARAMS\"}"

# 8. Delete a relation
PARAMS='{\"relations\":[{\"from\":\"John_Smith\",\"to\":\"Anthropic\",\"relationType\":\"works_at\"}]}'
run_curl "8. Deleting the 'works_at' relation..." \
  "{\"operation\": \"delete_relations\", \"params\": \"$PARAMS\"}"

# 9. Delete an entity
PARAMS='{\"entityNames\":[\"John_Smith\"]}'
run_curl "9. Deleting entity 'John_Smith'..." \
  "{\"operation\": \"delete_entities\", \"params\": \"$PARAMS\"}"

# 10. Read graph again to verify deletions
run_curl "10. Reading graph to verify deletions..." \
  '{"operation": "read_graph"}'

echo -e "\n--- Test Complete ---"
# Final cleanup
rm -f "$MEMORY_FILE" 