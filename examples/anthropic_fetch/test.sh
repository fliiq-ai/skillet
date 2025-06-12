#!/bin/bash
# Test script for the Fetch HTML Skillet

BASE_URL="http://127.0.0.1:8000/run"
TEST_URL="https://httpbin.org/html"

echo "--- Testing Fetch HTML Skillet ---"

# Test 1: Basic HTML Fetch
echo -e "\n1. Fetching raw HTML..."
curl -s -X POST "${BASE_URL}" \
  -H "Content-Type: application/json" \
  -d "{\"url\": \"${TEST_URL}\", \"as_markdown\": false}" | cut -c 1-80
echo "..."

# Test 2: Convert to Markdown
echo -e "\n2. Fetching as Markdown..."
curl -s -X POST "${BASE_URL}" \
  -H "Content-Type: application/json" \
  -d "{\"url\": \"${TEST_URL}\", \"as_markdown\": true}" | cut -c 1-80
echo "..."

# Test 3: Pagination Support
echo -e "\n3. Fetching with a start_index of 1500..."
curl -s -X POST "${BASE_URL}" \
  -H "Content-Type: application/json" \
  -d "{\"url\": \"${TEST_URL}\", \"start_index\": 1500, \"as_markdown\": false}" | cut -c 1-80
echo -e "...\n\n--- Test Complete ---" 