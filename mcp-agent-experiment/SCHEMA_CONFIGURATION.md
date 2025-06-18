# 🗂️ PostgreSQL Schema Configuration for MCP

This guide explains how to configure the postgres-mcp server to work with specific PostgreSQL schemas.

## 📋 Overview

PostgreSQL databases can contain multiple schemas (namespaces), and you might want to:
- Focus the MCP server on a specific schema (e.g., 'public', 'app', 'analytics')
- Limit AI queries to certain schemas for security
- Work with multiple schemas simultaneously
- Optimize performance by reducing the schema search space

## 🛠️ Configuration Methods

### Method 1: Interactive Configuration (Recommended)

Use the provided script for easy setup:

```bash
./configure_schema.sh
```

This script will:
- Show available schemas in your database
- Let you choose which schema(s) to use
- Update your configuration automatically
- Restart the MCP server with new settings

### Method 2: Manual Configuration

#### Step 1: Add Schema to Environment Variables

Add to your `.env` file:

```bash
# PostgreSQL Schema Configuration
DB_SCHEMA=public                    # Single schema
# DB_SCHEMA=public,app,analytics    # Multiple schemas
```

#### Step 2: Restart MCP Server

```bash
docker-compose down postgres-mcp
docker-compose up -d postgres-mcp
```

### Method 3: PostgreSQL Connection String Parameters

The schema is configured via the `search_path` parameter in the DATABASE_URI:

```bash
# Current configuration in docker-compose.yml
DATABASE_URI: postgresql://${DB_USER}:${DB_PASSWORD}@${DB_HOST}:${DB_PORT}/${DB_NAME}?search_path=${DB_SCHEMA:-public}
```

## 🎯 Schema Configuration Examples

### Example 1: Public Schema Only (Default)

```bash
# .env
DB_SCHEMA=public
```

**Result**: MCP server will primarily work with tables in the 'public' schema.

### Example 2: Custom Application Schema

```bash
# .env
DB_SCHEMA=app
```

**Result**: MCP server will focus on the 'app' schema for table discovery and queries.

### Example 3: Multiple Schemas

```bash
# .env
DB_SCHEMA=public,app,analytics
```

**Result**: MCP server will search tables across all specified schemas.

### Example 4: Schema Priority Order

```bash
# .env
DB_SCHEMA=app,public
```

**Result**: MCP server will search 'app' schema first, then 'public' as fallback.

## 🔍 How Schema Configuration Works

### PostgreSQL Search Path

The `search_path` parameter tells PostgreSQL which schemas to search when resolving unqualified table names:

```sql
-- Without search_path, you need fully qualified names
SELECT * FROM public.users;
SELECT * FROM app.products;

-- With search_path=app,public, you can use unqualified names
SELECT * FROM users;     -- Searches app.users, then public.users
SELECT * FROM products;  -- Searches app.products, then public.products
```

### MCP Server Behavior

1. **Table Discovery**: The MCP server will only show tables from configured schemas
2. **Query Generation**: AI will generate queries using unqualified table names
3. **Schema Isolation**: Prevents access to system schemas (pg_catalog, information_schema)

## 📚 Common Use Cases

### Use Case 1: Multi-Tenant Application

```bash
# Separate customer data by schema
DB_SCHEMA=customer_123
```

### Use Case 2: Development vs Production

```bash
# Development environment
DB_SCHEMA=dev,public

# Production environment  
DB_SCHEMA=prod
```

### Use Case 3: Data Analytics

```bash
# Focus on analytics tables
DB_SCHEMA=analytics,staging,public
```

### Use Case 4: Microservices

```bash
# Service-specific schema
DB_SCHEMA=user_service,shared
```

## 🧪 Testing Schema Configuration

### 1. Check Available Schemas

```sql
SELECT schema_name 
FROM information_schema.schemata 
WHERE schema_name NOT IN ('information_schema', 'pg_catalog', 'pg_toast')
ORDER BY schema_name;
```

### 2. Verify Current Search Path

```sql
SHOW search_path;
```

### 3. Test Table Discovery

In your Streamlit app, ask:
- "List all tables in the database"
- "Show me the schema structure"
- "What tables are available in the [schema_name] schema?"

## 🔧 Advanced Configuration

### Environment Variable Options

```bash
# .env file
DB_HOST=172.30.196.100
DB_USER=baoha
DB_PASSWORD=Namco%409999
DB_NAME=2025_06_11_17_10_12_excel_02_04
DB_PORT=5432
DB_SCHEMA=public                    # Schema configuration

# Docker Configuration
NETWORK_MODE=host
```

### Dynamic Schema Switching

You can change schemas without restarting by updating the environment and restarting just the MCP service:

```bash
# Update schema in .env
echo "DB_SCHEMA=new_schema" >> .env

# Restart MCP server
docker-compose restart postgres-mcp
```

### Multiple Database Connections

For complex setups, you might run multiple MCP servers with different schema configurations:

```yaml
# docker-compose.yml
services:
  postgres-mcp-public:
    image: crystaldba/postgres-mcp:latest
    environment:
      DATABASE_URI: postgresql://${DB_USER}:${DB_PASSWORD}@${DB_HOST}:${DB_PORT}/${DB_NAME}?search_path=public
    ports:
      - "8000:8000"

  postgres-mcp-app:
    image: crystaldba/postgres-mcp:latest
    environment:
      DATABASE_URI: postgresql://${DB_USER}:${DB_PASSWORD}@${DB_HOST}:${DB_PORT}/${DB_NAME}?search_path=app
    ports:
      - "8001:8000"
```

## 🚨 Troubleshooting

### Schema Not Found

```bash
# Check if schema exists
./configure_schema.sh
# Choose option 4 to list available schemas
```

### Permission Issues

```sql
-- Grant schema access to user
GRANT USAGE ON SCHEMA app TO baoha;
GRANT SELECT ON ALL TABLES IN SCHEMA app TO baoha;
```

### Connection Issues After Schema Change

```bash
# Check MCP server logs
docker-compose logs postgres-mcp

# Test database connection
python test_remote_connection.py

# Restart with clean state
docker-compose down
docker-compose up -d postgres-mcp
```

## 💡 Best Practices

1. **Start with 'public'**: Use the default public schema for initial setup
2. **Use meaningful names**: Name schemas based on function (e.g., 'analytics', 'reporting')
3. **Limit scope**: Don't include unnecessary schemas to improve performance
4. **Test thoroughly**: Verify table discovery and query generation after changes
5. **Document schema purpose**: Keep track of what each schema contains
6. **Security first**: Only include schemas the AI should have access to

## 🔄 Quick Commands

```bash
# Interactive schema configuration
./configure_schema.sh

# Manual schema change
echo "DB_SCHEMA=your_schema" >> .env
docker-compose restart postgres-mcp

# Check current configuration
docker-compose config | grep DATABASE_URI

# View available schemas
python -c "
import asyncio, asyncpg, os
from dotenv import load_dotenv
load_dotenv()
async def main():
    conn = await asyncpg.connect(host=os.getenv('DB_HOST'), port=int(os.getenv('DB_PORT', '5432')), user=os.getenv('DB_USER'), password=os.getenv('DB_PASSWORD').replace('%40', '@'), database=os.getenv('DB_NAME'))
    schemas = await conn.fetch('SELECT schema_name FROM information_schema.schemata WHERE schema_name NOT IN (\'information_schema\', \'pg_catalog\', \'pg_toast\') ORDER BY schema_name')
    print('Available schemas:', [r['schema_name'] for r in schemas])
    await conn.close()
asyncio.run(main())
"
```

---

**Note**: Schema configuration affects how the AI discovers and queries your database tables. Choose schemas that contain the data you want the AI to work with. 