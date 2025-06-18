#!/bin/bash

# Script to configure PostgreSQL schema for postgres-mcp
echo "🗂️ Configuring PostgreSQL Schema for MCP Server"
echo "=" * 50

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to prompt for input with default value
prompt_with_default() {
    local prompt="$1"
    local default="$2"
    local result
    
    read -p "$prompt [$default]: " result
    echo "${result:-$default}"
}

echo -e "${BLUE}📋 Current Configuration${NC}"

# Show current environment
if [ -f .env ]; then
    echo "Current database configuration:"
    grep -E "^DB_" .env | head -5
    echo ""
fi

echo -e "${BLUE}🗂️ Schema Configuration Options${NC}"
echo "1. public (default PostgreSQL schema)"
echo "2. Custom schema name"
echo "3. Multiple schemas (comma-separated)"
echo "4. Show available schemas in your database"

choice=$(prompt_with_default "Enter choice (1-4)" "1")

case $choice in
    1)
        schema="public"
        echo -e "${GREEN}✅ Using 'public' schema${NC}"
        ;;
    2)
        schema=$(prompt_with_default "Enter custom schema name" "public")
        echo -e "${GREEN}✅ Using custom schema: '$schema'${NC}"
        ;;
    3)
        schema=$(prompt_with_default "Enter schemas (comma-separated)" "public,app")
        echo -e "${GREEN}✅ Using multiple schemas: '$schema'${NC}"
        ;;
    4)
        echo -e "${BLUE}🔍 Checking available schemas...${NC}"
        if command -v python3 >/dev/null 2>&1; then
            python3 -c "
import asyncio
import asyncpg
import os
from dotenv import load_dotenv

async def show_schemas():
    try:
        load_dotenv()
        conn = await asyncpg.connect(
            host=os.getenv('DB_HOST'),
            port=int(os.getenv('DB_PORT', '5432')),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD').replace('%40', '@'),
            database=os.getenv('DB_NAME')
        )
        
        schemas = await conn.fetch(\"\"\"
            SELECT schema_name 
            FROM information_schema.schemata 
            WHERE schema_name NOT IN ('information_schema', 'pg_catalog', 'pg_toast')
            ORDER BY schema_name
        \"\"\")
        
        print('Available schemas:')
        for row in schemas:
            print(f'  • {row[\"schema_name\"]}')
        
        await conn.close()
    except Exception as e:
        print(f'Error: {e}')

asyncio.run(show_schemas())
"
        else
            echo "Python3 not available. Cannot check schemas."
        fi
        
        schema=$(prompt_with_default "Enter schema name to use" "public")
        ;;
    *)
        schema="public"
        ;;
esac

# Update .env file
echo -e "\n${BLUE}📝 Updating configuration...${NC}"

# Add or update DB_SCHEMA in .env
if grep -q "^DB_SCHEMA=" .env 2>/dev/null; then
    sed -i "s/^DB_SCHEMA=.*/DB_SCHEMA=$schema/" .env
else
    echo "" >> .env
    echo "# PostgreSQL Schema Configuration" >> .env
    echo "DB_SCHEMA=$schema" >> .env
fi

echo -e "${GREEN}✅ Schema configuration updated:${NC}"
echo "DB_SCHEMA=$schema"

# Show updated DATABASE_URI
echo -e "\n${BLUE}🔗 Updated Connection String:${NC}"
source .env
echo "DATABASE_URI: postgresql://$DB_USER:*****@$DB_HOST:$DB_PORT/$DB_NAME?search_path=$schema"

echo -e "\n${BLUE}🔄 Restarting MCP server with new schema configuration...${NC}"

# Restart the MCP server
docker-compose down postgres-mcp 2>/dev/null || true
sleep 2

if docker-compose up -d postgres-mcp; then
    echo -e "${GREEN}✅ MCP server restarted successfully${NC}"
    
    # Wait a moment and check logs
    sleep 5
    echo -e "\n${BLUE}📋 Server Status:${NC}"
    if docker-compose logs postgres-mcp | grep -q "Successfully connected to database"; then
        echo -e "${GREEN}✅ Database connection successful with schema: $schema${NC}"
    else
        echo -e "${YELLOW}⚠️  Check logs for any issues:${NC}"
        echo "docker-compose logs postgres-mcp"
    fi
else
    echo -e "${RED}❌ Failed to restart MCP server${NC}"
    exit 1
fi

echo -e "\n${BLUE}🧪 Testing Schema Configuration${NC}"
echo "You can now test the schema configuration:"
echo "1. Check available tables: 'List all tables in the $schema schema'"
echo "2. Run your Streamlit app: streamlit run app_postgres_pro.py"

echo -e "\n${BLUE}💡 Schema Notes:${NC}"
echo "• The MCP server will now primarily work with the '$schema' schema"
echo "• You can still access other schemas by fully qualifying table names (e.g., other_schema.table_name)"
echo "• To change schemas later, run this script again or update DB_SCHEMA in .env" 