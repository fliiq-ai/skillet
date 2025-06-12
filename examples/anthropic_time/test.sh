#!/bin/bash
# Test script for the Time Skillet

BASE_URL="http://127.0.0.1:8000/run"

echo "--- Testing Time Skillet ---"

# Test 1: Get UTC time
echo -e "\n1. Getting current time in UTC (default)..."
curl -s -X POST "${BASE_URL}" \
  -H "Content-Type: application/json" \
  -d '{}'
echo ""

# Test 2: Get time in a specific timezone
echo -e "\n2. Getting current time in America/New_York..."
curl -s -X POST "${BASE_URL}" \
  -H "Content-Type: application/json" \
  -d '{"timezone": "America/New_York"}'
echo ""

# Test 3: Handle an invalid timezone
echo -e "\n3. Testing with an invalid timezone..."
curl -s -X POST "${BASE_URL}" \
  -H "Content-Type: application/json" \
  -d '{"timezone": "Mars/Olympus_Mons"}'
echo -e "\n\n--- Test Complete ---" 