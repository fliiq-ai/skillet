# Supabase Execute SQL Skillet

A Skillet skill that executes SQL queries on Supabase databases with built-in security and read-only mode support.

## Description

This skill provides secure SQL query execution for Supabase databases. It includes read-only mode for safe data access, query validation, and protection against SQL injection attacks. Perfect for database operations in AI-driven applications.

## 🔐 **Credential Requirements**

This skill **requires** the following credentials to function:

### **Required Environment Variables**
- **`SUPABASE_URL`** - Your Supabase project URL  
  - Format: `https://your-project.supabase.co`
  - Get from: [Supabase Dashboard](https://app.supabase.com) → Project Settings → API

- **`SUPABASE_ANON_KEY`** OR **`SUPABASE_SERVICE_ROLE_KEY`** - Authentication key
  - **ANON_KEY**: For read-only operations (safer)
  - **SERVICE_ROLE_KEY**: For write operations (full access)
  - Get from: [Supabase Dashboard](https://app.supabase.com) → Project Settings → API

### **Local Development Setup**
```bash
# Copy .env.example to .env and add your credentials
cp .env.example .env

# Edit .env file:
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...  # Optional for write ops
```

### **Production Deployment (Runtime Injection)**
For production applications like Fliiq, credentials can be provided at runtime:

```javascript
const response = await fetch('/api/supabase_execute_sql/run', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    skill_input: {
      sql: "SELECT * FROM users",
      read_only: true
    },
    credentials: {
      SUPABASE_URL: "https://your-project.supabase.co",
      SUPABASE_ANON_KEY: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    }
  })
});
```

### **Getting Your Supabase Credentials**

1. **Go to [Supabase Dashboard](https://app.supabase.com)**
2. **Select your project**
3. **Navigate to Settings → API**
4. **Copy the values:**
   - Project URL → `SUPABASE_URL`
   - `anon` `public` key → `SUPABASE_ANON_KEY`
   - `service_role` `secret` key → `SUPABASE_SERVICE_ROLE_KEY`

## Features

- **Secure SQL Execution**: Built-in protection against SQL injection
- **Read-Only Mode**: Safe data access with read-only restrictions
- **Query Type Detection**: Automatic detection of SQL operation types
- **Performance Metrics**: Execution time tracking
- **Flexible Authentication**: Support for multiple Supabase key types
- **Error Handling**: Comprehensive error handling and validation
- **Dual Endpoints**: Legacy and enhanced endpoints for maximum compatibility
- **Credential Injection**: Runtime credentials for production deployments

## API Endpoints

This skillet provides **two endpoints** to support different use cases:

### `/execute_sql` - Legacy Endpoint (Backward Compatibility)

**Purpose**: Maintains existing API contract for current users

**Request Format:**
```json
POST /execute_sql
{
  "sql": "SELECT * FROM users WHERE active = true",
  "database_url": "https://your-project.supabase.co",
  "read_only": true,
  "timeout": 30
}
```

**Credential Source**: Environment variables only (`.env` file)

---

### `/run` - Enhanced Endpoint (Production Ready)

**Purpose**: Modern endpoint supporting credential injection for production deployments

**Request Format Option 1 - Simple (same as /execute_sql):**
```json
POST /run
{
  "sql": "SELECT * FROM users WHERE active = true",
  "read_only": true,
  "timeout": 30
}
```

**Request Format Option 2 - Enhanced (with credentials):**
```json
POST /run
{
  "skill_input": {
    "sql": "SELECT * FROM users WHERE active = true",
    "read_only": true,
    "timeout": 30
  },
  "credentials": {
    "SUPABASE_URL": "https://your-project.supabase.co",
    "SUPABASE_ANON_KEY": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}
```

**Credential Sources**: Environment variables OR runtime injection

## Response Format

Both endpoints return the same response format:

```json
{
    "success": true,
    "data": [
        {"id": 1, "name": "John Doe", "email": "john@example.com"},
        {"id": 2, "name": "Jane Smith", "email": "jane@example.com"}
    ],
    "row_count": 2,
    "execution_time": 0.123,
    "query_type": "SELECT"
}
```

### GET /query_types
List supported SQL query types.

**Response:**
```json
{
    "read_only": ["SELECT"],
    "write": ["INSERT", "UPDATE", "DELETE", "CREATE", "DROP", "ALTER"],
    "default_mode": "read_only"
}
```

### GET /health
Health check endpoint.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure Supabase credentials (see [Credential Requirements](#-credential-requirements) above)

3. Start the server:
```bash
uvicorn skillet_runtime:app --reload
```

## Testing

Run the test script to verify functionality:
```bash
./test.sh
```

The test script will:
- Check server health
- List supported query types
- Test SELECT queries (read-only)
- Test write operations
- Test security validations
- Test error handling

## Parameters

- **sql**: SQL query to execute (required)
- **database_url**: Supabase database URL (optional, uses env var if not provided)
- **read_only**: Restrict to read-only operations (default: true)
- **timeout**: Query timeout in seconds (default: 30)

## Security Features

### Read-Only Mode
By default, the skill operates in read-only mode, allowing only SELECT queries. This prevents accidental data modifications.

### SQL Injection Protection
The skill includes basic protection against common SQL injection patterns:
- Multiple statement execution
- SQL comments
- Dangerous stored procedures
- System commands

### Query Validation
All queries are validated before execution:
- Empty queries are rejected
- Query types are detected and validated
- Read-only restrictions are enforced

## Query Types

### Read-Only (Default)
- **SELECT**: Data retrieval queries

### Write Operations (read_only=false)
- **INSERT**: Add new records
- **UPDATE**: Modify existing records
- **DELETE**: Remove records
- **CREATE**: Create tables/indexes
- **DROP**: Remove tables/indexes
- **ALTER**: Modify table structure

## Example Usage

```bash
# Read data (safe, read-only)
curl -X POST "http://localhost:8000/execute_sql" \
    -H "Content-Type: application/json" \
    -d '{
        "sql": "SELECT * FROM users WHERE active = true",
        "read_only": true
    }'

# Insert data (requires read_only=false)
curl -X POST "http://localhost:8000/execute_sql" \
    -H "Content-Type: application/json" \
    -d '{
        "sql": "INSERT INTO users (name, email) VALUES ('\''John Doe'\'', '\''john@example.com'\'')",
        "read_only": false
    }'

# Complex query with joins
curl -X POST "http://localhost:8000/execute_sql" \
    -H "Content-Type: application/json" \
    -d '{
        "sql": "SELECT u.name, p.title FROM users u JOIN posts p ON u.id = p.user_id WHERE u.active = true",
        "read_only": true
    }'
```

## Response Fields

- **success**: Whether query executed successfully
- **data**: Query result data (array of objects)
- **row_count**: Number of rows affected/returned
- **execution_time**: Query execution time in seconds
- **query_type**: Type of SQL operation performed

## Error Handling

The skill handles various error conditions:

- **400 Bad Request**: Invalid SQL, empty queries, dangerous patterns
- **500 Internal Server Error**: Database connection issues, authentication failures
- **Timeout**: Queries exceeding the specified timeout

## Implementation Notes

This implementation includes a mock query execution system for demonstration purposes. In a production environment, it would:

1. Use Supabase's native query execution methods
2. Implement proper connection pooling
3. Support advanced query features
4. Include comprehensive logging
5. Support transaction management

## Best Practices

1. **Always use read-only mode** for data retrieval
2. **Validate user inputs** before constructing queries
3. **Use parameterized queries** when possible
4. **Use ANON_KEY for read operations** and SERVICE_ROLE_KEY only when necessary

