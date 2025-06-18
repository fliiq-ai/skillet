#!/bin/bash

# Test script for Skillet Discovery Service
# This script tests all endpoints of the discovery service

BASE_URL="http://localhost:8000"

echo "🔍 Testing Skillet Discovery Service"
echo "===================================="
echo

# Test 1: Health Check
echo "1. Testing health check..."
curl -s -X GET "$BASE_URL/health" \
  -H "Content-Type: application/json" | jq '.'
echo
echo "---"

# Test 2: Get full catalog
echo "2. Testing full catalog retrieval..."
curl -s -X GET "$BASE_URL/catalog" \
  -H "Content-Type: application/json" | jq '.discovery_service'
echo
echo "---"

# Test 3: Get available skills only
echo "3. Testing available skills retrieval..."
curl -s -X GET "$BASE_URL/skills" \
  -H "Content-Type: application/json" | jq '.'
echo
echo "---"

# Test 4: Search by query
echo "4. Testing search by query (time)..."
curl -s -X GET "$BASE_URL/search?query=time" \
  -H "Content-Type: application/json" | jq '.results, .skills[].skill.name'
echo
echo "---"

# Test 5: Search by category
echo "5. Testing search by category (utility)..."
curl -s -X GET "$BASE_URL/search?category=utility" \
  -H "Content-Type: application/json" | jq '.results, .skills[].skill.name'
echo
echo "---"

# Test 6: Search by complexity
echo "6. Testing search by complexity (simple)..."
curl -s -X GET "$BASE_URL/search?complexity=simple" \
  -H "Content-Type: application/json" | jq '.results, .skills[].skill.name'
echo
echo "---"

# Test 7: Search by tags
echo "7. Testing search by tags (datetime)..."
curl -s -X GET "$BASE_URL/search?tags=datetime" \
  -H "Content-Type: application/json" | jq '.results, .skills[].skill.name'
echo
echo "---"

# Test 8: Complex search
echo "8. Testing complex search (web + simple)..."
curl -s -X GET "$BASE_URL/search?query=web&complexity=simple" \
  -H "Content-Type: application/json" | jq '.results, .skills[].skill.name'
echo
echo "---"

# Test 9: Manual refresh
echo "9. Testing manual catalog refresh..."
curl -s -X POST "$BASE_URL/refresh" \
  -H "Content-Type: application/json" | jq '.'
echo
echo "---"

# Test 10: Show skill endpoints for integration
echo "10. Showing skill endpoints for integration..."
curl -s -X GET "$BASE_URL/skills" \
  -H "Content-Type: application/json" | jq '.skills[].skill | {name: .name, endpoints: .endpoints}'
echo

echo "✅ Discovery service testing completed!"
echo
echo "💡 Integration tip: Use the /search endpoint to find relevant skills,"
echo "   then use the returned endpoints to interact with specific skills." 