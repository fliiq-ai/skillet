#!/bin/bash

# Test script for Supabase Execute SQL Skillet
echo "--- Testing Supabase Execute SQL Skillet ---"

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

# Test listing query types
echo ""
echo "2. Testing query types listing..."
types_response=$(curl -s http://localhost:8000/query_types)
if [ $? -eq 0 ]; then
    echo "✓ Query types listing successful"
    echo "Query types: $types_response"
else
    echo "✗ Query types listing failed"
fi

# Test SELECT query (read-only)
echo ""
echo "3. Testing SELECT query (read-only mode)..."
select_response=$(curl -s -X POST "http://localhost:8000/execute_sql" \
    -H "Content-Type: application/json" \
    -d '{
        "sql": "SELECT * FROM users WHERE id = 1",
        "read_only": true
    }')

if [ $? -eq 0 ]; then
    echo "✓ SELECT query successful"
    echo "Response: $select_response"
else
    echo "✗ SELECT query failed"
fi

# Test another SELECT query with products
echo ""
echo "4. Testing SELECT query for products..."
products_response=$(curl -s -X POST "http://localhost:8000/execute_sql" \
    -H "Content-Type: application/json" \
    -d '{
        "sql": "SELECT name, price FROM products ORDER BY price DESC",
        "read_only": true
    }')

if [ $? -eq 0 ]; then
    echo "✓ Products SELECT query successful"
    echo "Response: $products_response"
else
    echo "✗ Products SELECT query failed"
fi

# Test INSERT query in read-only mode (should fail)
echo ""
echo "5. Testing INSERT query in read-only mode (should fail)..."
insert_readonly_response=$(curl -s -X POST "http://localhost:8000/execute_sql" \
    -H "Content-Type: application/json" \
    -d '{
        "sql": "INSERT INTO users (name, email) VALUES ('\''Test User'\'', '\''test@example.com'\'')",
        "read_only": true
    }')

echo "INSERT in read-only response: $insert_readonly_response"

# Test INSERT query in write mode
echo ""
echo "6. Testing INSERT query in write mode..."
insert_response=$(curl -s -X POST "http://localhost:8000/execute_sql" \
    -H "Content-Type: application/json" \
    -d '{
        "sql": "INSERT INTO users (name, email) VALUES ('\''Test User'\'', '\''test@example.com'\'')",
        "read_only": false
    }')

if [ $? -eq 0 ]; then
    echo "✓ INSERT query successful"
    echo "Response: $insert_response"
else
    echo "✗ INSERT query failed (this is expected if no Supabase credentials are configured)"
fi

# Test UPDATE query
echo ""
echo "7. Testing UPDATE query..."
update_response=$(curl -s -X POST "http://localhost:8000/execute_sql" \
    -H "Content-Type: application/json" \
    -d '{
        "sql": "UPDATE users SET name = '\''Updated User'\'' WHERE id = 1",
        "read_only": false
    }')

if [ $? -eq 0 ]; then
    echo "✓ UPDATE query successful"
    echo "Response: $update_response"
else
    echo "✗ UPDATE query failed"
fi

# Test error handling with empty SQL
echo ""
echo "8. Testing error handling with empty SQL..."
empty_sql_response=$(curl -s -X POST "http://localhost:8000/execute_sql" \
    -H "Content-Type: application/json" \
    -d '{
        "sql": "",
        "read_only": true
    }')

echo "Empty SQL response: $empty_sql_response"

# Test error handling with potentially dangerous SQL
echo ""
echo "9. Testing error handling with dangerous SQL..."
dangerous_sql_response=$(curl -s -X POST "http://localhost:8000/execute_sql" \
    -H "Content-Type: application/json" \
    -d '{
        "sql": "SELECT * FROM users; DROP TABLE users;",
        "read_only": true
    }')

echo "Dangerous SQL response: $dangerous_sql_response"

echo ""
echo "--- Test completed ---"
echo "Note: This is a mock implementation for demonstration purposes."
echo "To use with real Supabase, configure these environment variables:"
echo "- SUPABASE_URL: Your Supabase project URL"
echo "- SUPABASE_ANON_KEY: Your Supabase anonymous key"
echo "- SUPABASE_SERVICE_ROLE_KEY: Your Supabase service role key (for write operations)"

