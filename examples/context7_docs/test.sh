#!/bin/bash

# Test script for Context7 Docs Skillet
echo "--- Testing Context7 Docs Skillet ---"

# Check if server is running
echo "1. Checking server health..."
health_response=$(curl -s http://localhost:8000/health)
if [ $? -eq 0 ]; then
    echo "✓ Server is running"
    echo "Health response: $health_response"
else
    echo "✗ Server is not running. Please start with: uvicorn skillet_runtime:app --reload"
    exit 1
fi

# Test listing available libraries
echo ""
echo "2. Testing library listing..."
libraries_response=$(curl -s http://localhost:8000/libraries)
if [ $? -eq 0 ]; then
    echo "✓ Library listing successful"
    echo "Available libraries: $libraries_response"
else
    echo "✗ Library listing failed"
fi

# Test React hooks documentation
echo ""
echo "3. Testing React hooks documentation..."
react_hooks_response=$(curl -s -X POST "http://localhost:8000/docs" \
    -H "Content-Type: application/json" \
    -d '{
        "query": "hooks",
        "library": "react",
        "version": "latest",
        "max_results": 3
    }')

if [ $? -eq 0 ]; then
    echo "✓ React hooks documentation request successful"
    echo "Response: $react_hooks_response"
else
    echo "✗ React hooks documentation request failed"
fi

# Test Next.js app router documentation
echo ""
echo "4. Testing Next.js app router documentation..."
nextjs_response=$(curl -s -X POST "http://localhost:8000/docs" \
    -H "Content-Type: application/json" \
    -d '{
        "query": "app router",
        "library": "nextjs",
        "version": "latest"
    }')

if [ $? -eq 0 ]; then
    echo "✓ Next.js documentation request successful"
    echo "Response: $nextjs_response"
else
    echo "✗ Next.js documentation request failed"
fi

# Test general search across all libraries
echo ""
echo "5. Testing general search across all libraries..."
general_response=$(curl -s -X POST "http://localhost:8000/docs" \
    -H "Content-Type: application/json" \
    -d '{
        "query": "components",
        "max_results": 5
    }')

if [ $? -eq 0 ]; then
    echo "✓ General search request successful"
    echo "Response: $general_response"
else
    echo "✗ General search request failed"
fi

# Test FastAPI documentation
echo ""
echo "6. Testing FastAPI documentation..."
fastapi_response=$(curl -s -X POST "http://localhost:8000/docs" \
    -H "Content-Type: application/json" \
    -d '{
        "query": "getting started",
        "library": "fastapi"
    }')

if [ $? -eq 0 ]; then
    echo "✓ FastAPI documentation request successful"
    echo "Response: $fastapi_response"
else
    echo "✗ FastAPI documentation request failed"
fi

# Test error handling with empty query
echo ""
echo "7. Testing error handling with empty query..."
error_response=$(curl -s -X POST "http://localhost:8000/docs" \
    -H "Content-Type: application/json" \
    -d '{
        "query": "",
        "library": "react"
    }')

echo "Error handling response: $error_response"

# Test search for non-existent library
echo ""
echo "8. Testing search for non-existent library..."
nonexistent_response=$(curl -s -X POST "http://localhost:8000/docs" \
    -H "Content-Type: application/json" \
    -d '{
        "query": "components",
        "library": "nonexistent-lib"
    }')

if [ $? -eq 0 ]; then
    echo "✓ Non-existent library handled gracefully"
    echo "Response: $nonexistent_response"
else
    echo "✗ Non-existent library request failed"
fi

echo ""
echo "--- Test completed ---"
echo "Note: This is a mock implementation of Context7 functionality."
echo "In a real implementation, this would connect to Context7's documentation database."

