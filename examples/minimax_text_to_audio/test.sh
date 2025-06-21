#!/bin/bash

# Test script for MiniMax Text-to-Audio Skillet
echo "--- Testing MiniMax Text-to-Audio Skillet ---"

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

# Test listing voices
echo ""
echo "2. Testing voice listing..."
voices_response=$(curl -s http://localhost:8000/voices)
if [ $? -eq 0 ]; then
    echo "✓ Voice listing successful"
    echo "Available voices: $voices_response"
else
    echo "✗ Voice listing failed"
fi

# Test text-to-audio conversion
echo ""
echo "3. Testing text-to-audio conversion..."
tts_response=$(curl -s -X POST "http://localhost:8000/text_to_audio" \
    -H "Content-Type: application/json" \
    -d '{
        "text": "Hello, this is a test of the MiniMax text-to-speech system.",
        "voice_id": "male-qn-qingse",
        "speed": 1.0,
        "volume": 0.8
    }')

if [ $? -eq 0 ]; then
    echo "✓ Text-to-audio request successful"
    echo "Response: $tts_response"
else
    echo "✗ Text-to-audio request failed (this is expected if no API key is configured)"
    echo "Response: $tts_response"
fi

# Test with different voice
echo ""
echo "4. Testing with female voice..."
female_response=$(curl -s -X POST "http://localhost:8000/text_to_audio" \
    -H "Content-Type: application/json" \
    -d '{
        "text": "This is a test with a female voice.",
        "voice_id": "female-shaonv",
        "speed": 1.2,
        "volume": 1.0
    }')

if [ $? -eq 0 ]; then
    echo "✓ Female voice request successful"
    echo "Response: $female_response"
else
    echo "✗ Female voice request failed (this is expected if no API key is configured)"
fi

# Test error handling with empty text
echo ""
echo "5. Testing error handling with empty text..."
error_response=$(curl -s -X POST "http://localhost:8000/text_to_audio" \
    -H "Content-Type: application/json" \
    -d '{
        "text": "",
        "voice_id": "male-qn-qingse"
    }')

echo "Error handling response: $error_response"

# Test error handling with invalid speed
echo ""
echo "6. Testing error handling with invalid speed..."
speed_error_response=$(curl -s -X POST "http://localhost:8000/text_to_audio" \
    -H "Content-Type: application/json" \
    -d '{
        "text": "Test text",
        "voice_id": "male-qn-qingse",
        "speed": 3.0
    }')

echo "Speed error response: $speed_error_response"

echo ""
echo "--- Test completed ---"
echo "Note: Text-to-audio conversion will fail if API key is not configured:"
echo "- MINIMAX_API_KEY: Get from MiniMax platform"
echo "- MINIMAX_API_HOST: API endpoint (defaults to https://api.minimax.io)"
echo ""
echo "If tests pass, check the 'output' directory for generated audio files."

