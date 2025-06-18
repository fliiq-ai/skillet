#!/bin/bash

# Test script for Skillet Multi-Skill Runtime Host
# This script tests the consolidated hosting of multiple skills

BASE_URL="http://localhost:8000"

echo "🏠 Testing Skillet Multi-Skill Runtime Host"
echo "============================================="
echo

# Test 1: Root endpoint - service info
echo "1. Testing root endpoint (service info)..."
curl -s -X GET "$BASE_URL/" \
  -H "Content-Type: application/json" | jq '.'
echo
echo "---"

# Test 2: Health check
echo "2. Testing health check..."
curl -s -X GET "$BASE_URL/health" \
  -H "Content-Type: application/json" | jq '.'
echo
echo "---"

# Test 3: Skills list
echo "3. Testing skills list..."
curl -s -X GET "$BASE_URL/skills" \
  -H "Content-Type: application/json" | jq '.'
echo
echo "---"

# Test 4: Unified catalog
echo "4. Testing unified catalog..."
curl -s -X GET "$BASE_URL/catalog" \
  -H "Content-Type: application/json" | jq '.runtime_host, .skills | length'
echo
echo "---"

# Test 5: Individual skill endpoints - Time Skill
echo "5. Testing Time Skill endpoints..."
echo "   5a. Time skill inventory:"
curl -s -X GET "$BASE_URL/skills/time/inventory" \
  -H "Content-Type: application/json" | jq '.skill.name, .skill.category'
echo
echo "   5b. Time skill schema:"
curl -s -X GET "$BASE_URL/skills/time/schema" \
  -H "Content-Type: application/json" | jq '.name, .description'
echo
echo "   5c. Time skill execution:"
curl -s -X POST "$BASE_URL/skills/time/run" \
  -H "Content-Type: application/json" \
  -d '{"timezone": "America/New_York"}' | jq '.iso_8601'
echo
echo "---"

# Test 6: Individual skill endpoints - Fetch Skill
echo "6. Testing Fetch Skill endpoints..."
echo "   6a. Fetch skill inventory:"
curl -s -X GET "$BASE_URL/skills/fetch/inventory" \
  -H "Content-Type: application/json" | jq '.skill.name, .skill.category'
echo
echo "   6b. Fetch skill execution:"
curl -s -X POST "$BASE_URL/skills/fetch/run" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://httpbin.org/json"}' | jq '.content | length'
echo
echo "---"

# Test 7: Individual skill endpoints - Memory Skill
echo "7. Testing Memory Skill endpoints..."
echo "   7a. Memory skill inventory:"
curl -s -X GET "$BASE_URL/skills/memory/inventory" \
  -H "Content-Type: application/json" | jq '.skill.name, .skill.category'
echo
echo "   7b. Memory skill - create entity:"
curl -s -X POST "$BASE_URL/skills/memory/run" \
  -H "Content-Type: application/json" \
  -d '{
    "operation": "create_entities",
    "params": "{\"entities\": [{\"name\": \"TestUser\", \"entityType\": \"person\", \"observations\": [\"Testing multi-skill host\"]}]}"
  }' | jq -r '.response | fromjson | .message'
echo
echo "   7c. Memory skill - read graph:"
curl -s -X POST "$BASE_URL/skills/memory/run" \
  -H "Content-Type: application/json" \
  -d '{"operation": "read_graph"}' | jq -r '.response | fromjson | .graph.entities | length'
echo
echo "---"

# Test 8: Error handling - non-existent skill
echo "8. Testing error handling (non-existent skill)..."
curl -s -X GET "$BASE_URL/skills/nonexistent/inventory" \
  -H "Content-Type: application/json" | head -3
echo
echo "---"

# Test 9: OpenAPI documentation
echo "9. Testing OpenAPI documentation availability..."
curl -s -X GET "$BASE_URL/docs" | head -5
echo
echo "---"

# Test 10: Skill reload (if supported)
echo "10. Testing skill reload..."
curl -s -X POST "$BASE_URL/reload" \
  -H "Content-Type: application/json" | jq '.message, .total_loaded'
echo

echo "✅ Multi-Skill Runtime Host testing completed!"
echo
echo "💡 Integration tips:"
echo "   • Individual skills are accessible at /skills/{skill_name}/*"
echo "   • Unified catalog available at /catalog"
echo "   • All existing skill APIs preserved"
echo "   • Discovery Service can point to this single host"
echo
echo "🔗 Example Discovery Service configuration:"
echo "   skills:"
echo "     - \"http://localhost:8000/skills/time\""
echo "     - \"http://localhost:8000/skills/fetch\""  
echo "     - \"http://localhost:8000/skills/memory\"" 