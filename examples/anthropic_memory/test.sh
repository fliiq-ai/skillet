#!/bin/bash
# Test script for the Knowledge Graph Memory Skillet

BASE_URL="http://127.0.0.1:8000"
MEMORY_FILE="memory.json"

# Cleanup previous test runs
rm -f "$MEMORY_FILE"

echo "--- Testing Knowledge Graph Memory Skillet ---"

# Test 0: Get skill inventory
echo -e "\n0. Getting skill inventory..."
curl -s -X GET "${BASE_URL}/inventory" \
  -H "Content-Type: application/json" | (json_pp || cat)
echo ""

# Test 1: Get tool schema
echo -e "\n1. Getting tool schema..."
curl -s -X GET "${BASE_URL}/schema" \
  -H "Content-Type: application/json" | (json_pp || cat)
echo ""

# Helper function to make requests
run_curl() {
  echo -e "\n$1"
  curl -s -X POST "${BASE_URL}/run" \
    -H "Content-Type: application/json" \
    -d "$2" | (json_pp || cat) # Pretty-print JSON if json_pp is available
  echo ""
}

# 2. Create entities
PARAMS='{\"entities\":[{\"name\":\"John_Smith\",\"entityType\":\"person\",\"observations\":[\"Speaks fluent Spanish\"]},{\"name\":\"Anthropic\",\"entityType\":\"organization\"}]}'
run_curl "2. Creating entities: 'John_Smith' and 'Anthropic'..." \
  "{\"operation\": \"create_entities\", \"params\": \"$PARAMS\"}"

# 3. Create relation
PARAMS='{\"relations\":[{\"from\":\"John_Smith\",\"to\":\"Anthropic\",\"relationType\":\"works_at\"}]}'
run_curl "3. Creating relation: John_Smith works_at Anthropic..." \
  "{\"operation\": \"create_relations\", \"params\": \"$PARAMS\"}"

# 4. Add observations
PARAMS='{\"observations\":[{\"entityName\":\"John_Smith\",\"contents\":[\"Graduated in 2019\",\"Prefers morning meetings\"]}]}'
run_curl "4. Adding observations to John_Smith..." \
  "{\"operation\": \"add_observations\", \"params\": \"$PARAMS\"}"

# 5. Read the entire graph to verify
run_curl "5. Reading graph to verify state..." \
  '{"operation": "read_graph"}'

# 6. Search for a node
PARAMS='{\"query\":\"spanish\"}'
run_curl "6. Searching for nodes with query 'spanish'..." \
  "{\"operation\": \"search_nodes\", \"params\": \"$PARAMS\"}"

# 7. Open a specific node
PARAMS='{\"names\":[\"Anthropic\"]}'
run_curl "7. Opening node 'Anthropic'..." \
  "{\"operation\": \"open_nodes\", \"params\": \"$PARAMS\"}"

# 8. Delete an observation
PARAMS='{\"deletions\":[{\"entityName\":\"John_Smith\",\"observations\":[\"Speaks fluent Spanish\"]}]}'
run_curl "8. Deleting an observation from John_Smith..." \
  "{\"operation\": \"delete_observations\", \"params\": \"$PARAMS\"}"

# 9. Delete a relation
PARAMS='{\"relations\":[{\"from\":\"John_Smith\",\"to\":\"Anthropic\",\"relationType\":\"works_at\"}]}'
run_curl "9. Deleting the 'works_at' relation..." \
  "{\"operation\": \"delete_relations\", \"params\": \"$PARAMS\"}"

# 10. Delete an entity
PARAMS='{\"entityNames\":[\"John_Smith\"]}'
run_curl "10. Deleting entity 'John_Smith'..." \
  "{\"operation\": \"delete_entities\", \"params\": \"$PARAMS\"}"

# 11. Read graph again to verify deletions
run_curl "11. Reading graph to verify deletions..." \
  '{"operation": "read_graph"}'

echo -e "\n--- Test Complete ---"
# Final cleanup
rm -f "$MEMORY_FILE" 