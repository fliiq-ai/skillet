#!/bin/bash
# Test script for the Fetch HTML Skillet

BASE_URL="http://127.0.0.1:8000"
TEST_URL="https://httpbin.org/html"

echo "--- Testing Fetch HTML Skillet ---"

# Test 0: Get skill inventory
echo -e "\n0. Getting skill inventory..."
curl -s -X GET "${BASE_URL}/inventory" \
  -H "Content-Type: application/json"
echo ""

# Test 1: Get tool schema
echo -e "\n1. Getting tool schema..."
curl -s -X GET "${BASE_URL}/schema" \
  -H "Content-Type: application/json"
echo ""

# Test 2: Basic HTML Fetch
echo -e "\n2. Fetching raw HTML..."
curl -s -X POST "${BASE_URL}/run" \
  -H "Content-Type: application/json" \
  -d "{\"url\": \"${TEST_URL}\", \"as_markdown\": false}" | cut -c 1-80
echo "..."

# Test 3: Convert to Markdown
echo -e "\n3. Fetching as Markdown..."
curl -s -X POST "${BASE_URL}/run" \
  -H "Content-Type: application/json" \
  -d "{\"url\": \"${TEST_URL}\", \"as_markdown\": true}" | cut -c 1-80
echo "..."

# Test 4: Pagination Support
echo -e "\n4. Fetching with a start_index of 1500..."
curl -s -X POST "${BASE_URL}/run" \
  -H "Content-Type: application/json" \
  -d "{\"url\": \"${TEST_URL}\", \"start_index\": 1500, \"as_markdown\": false}" | cut -c 1-80
echo -e "...\n\n--- Test Complete ---" 