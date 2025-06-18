#!/bin/bash
# Test script for the Time Skillet

BASE_URL="http://127.0.0.1:8000"

echo "--- Testing Time Skillet ---"

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

# Test 2: Get UTC time
echo -e "\n2. Getting current time in UTC (default)..."
curl -s -X POST "${BASE_URL}/run" \
  -H "Content-Type: application/json" \
  -d '{}'
echo ""

# Test 3: Get time in a specific timezone
echo -e "\n3. Getting current time in America/New_York..."
curl -s -X POST "${BASE_URL}/run" \
  -H "Content-Type: application/json" \
  -d '{"timezone": "America/New_York"}'
echo ""

# Test 4: Handle an invalid timezone
echo -e "\n4. Testing with an invalid timezone..."
curl -s -X POST "${BASE_URL}/run" \
  -H "Content-Type: application/json" \
  -d '{"timezone": "Mars/Olympus_Mons"}'
echo -e "\n\n--- Test Complete ---" 