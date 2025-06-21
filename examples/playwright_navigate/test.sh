#!/bin/bash

# Test script for Playwright Navigate Skillet
echo "--- Testing Playwright Navigate Skillet ---"

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

# Test listing available browsers
echo ""
echo "2. Testing browser listing..."
browsers_response=$(curl -s http://localhost:8000/browsers)
if [ $? -eq 0 ]; then
    echo "✓ Browser listing successful"
    echo "Available browsers: $browsers_response"
else
    echo "✗ Browser listing failed"
fi

# Test navigation to a simple website
echo ""
echo "3. Testing navigation to example.com..."
navigate_response=$(curl -s -X POST "http://localhost:8000/navigate" \
    -H "Content-Type: application/json" \
    -d '{
        "url": "https://example.com",
        "wait_for": "load",
        "timeout": 30000
    }')

if [ $? -eq 0 ]; then
    echo "✓ Navigation to example.com successful"
    echo "Response: $navigate_response"
else
    echo "✗ Navigation to example.com failed"
fi

# Test navigation with custom viewport
echo ""
echo "4. Testing navigation with custom viewport..."
viewport_response=$(curl -s -X POST "http://localhost:8000/navigate" \
    -H "Content-Type: application/json" \
    -d '{
        "url": "https://httpbin.org/user-agent",
        "wait_for": "domcontentloaded",
        "viewport_width": 1920,
        "viewport_height": 1080,
        "user_agent": "Playwright-Skillet-Test/1.0"
    }')

if [ $? -eq 0 ]; then
    echo "✓ Navigation with custom viewport successful"
    echo "Response: $viewport_response"
else
    echo "✗ Navigation with custom viewport failed"
fi

# Test navigation to a page that redirects
echo ""
echo "5. Testing navigation with redirect..."
redirect_response=$(curl -s -X POST "http://localhost:8000/navigate" \
    -H "Content-Type: application/json" \
    -d '{
        "url": "https://httpbin.org/redirect/1",
        "wait_for": "load"
    }')

if [ $? -eq 0 ]; then
    echo "✓ Navigation with redirect successful"
    echo "Response: $redirect_response"
else
    echo "✗ Navigation with redirect failed"
fi

# Test error handling with invalid URL
echo ""
echo "6. Testing error handling with invalid URL..."
invalid_url_response=$(curl -s -X POST "http://localhost:8000/navigate" \
    -H "Content-Type: application/json" \
    -d '{
        "url": "not-a-valid-url",
        "wait_for": "load"
    }')

echo "Invalid URL response: $invalid_url_response"

# Test error handling with invalid wait condition
echo ""
echo "7. Testing error handling with invalid wait condition..."
invalid_wait_response=$(curl -s -X POST "http://localhost:8000/navigate" \
    -H "Content-Type: application/json" \
    -d '{
        "url": "https://example.com",
        "wait_for": "invalid-condition"
    }')

echo "Invalid wait condition response: $invalid_wait_response"

# Test navigation to a non-existent domain
echo ""
echo "8. Testing navigation to non-existent domain..."
nonexistent_response=$(curl -s -X POST "http://localhost:8000/navigate" \
    -H "Content-Type: application/json" \
    -d '{
        "url": "https://this-domain-does-not-exist-12345.com",
        "wait_for": "load",
        "timeout": 5000
    }')

if [ $? -eq 0 ]; then
    echo "✓ Non-existent domain handled gracefully"
    echo "Response: $nonexistent_response"
else
    echo "✗ Non-existent domain request failed"
fi

echo ""
echo "--- Test completed ---"
echo "Note: Some tests may fail if network connectivity is limited."
echo "Make sure Playwright browsers are installed: playwright install"

