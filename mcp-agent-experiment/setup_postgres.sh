#!/bin/bash

# Setup script for MCP PostgreSQL Agent with Postgres MCP Pro
set -e

echo "🚀 Setting up MCP PostgreSQL Agent with Postgres MCP Pro..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is required but not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose is required but not installed. Please install Docker Compose first."
    exit 1
fi

# Check if UV is installed
if ! command -v uv &> /dev/null; then
    echo "❌ UV is required but not installed. Please install UV first."
    echo "Visit: https://docs.astral.sh/uv/getting-started/installation/"
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp env.postgres.example .env
    echo "✅ .env file created. Please edit it with your API keys and database settings."
    echo "📋 Required environment variables:"
    echo "   - MODEL_API_KEY: Your Groq or OpenAI API key"
    echo "   - MODEL_ID: Your preferred model ID"
    echo ""
    read -p "Press Enter to continue after editing .env file..."
fi

# Install Python dependencies
echo "📦 Installing Python dependencies..."
uv sync

# Pull the latest Postgres MCP Pro image
echo "🐳 Pulling Postgres MCP Pro Docker image..."
docker pull crystaldba/postgres-mcp:latest

# Start all services with Docker Compose
echo "🐘 Starting PostgreSQL and MCP Pro server..."
docker-compose up -d

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL to be ready..."
timeout 60s bash -c 'while ! docker-compose exec postgres pg_isready -U postgres -d testdb; do sleep 2; done'

if [ $? -eq 0 ]; then
    echo "✅ PostgreSQL is ready!"
else
    echo "❌ PostgreSQL failed to start within 60 seconds"
    exit 1
fi

# Wait for MCP Pro server to be ready
echo "⏳ Waiting for MCP Pro server to be ready..."
timeout 30s bash -c 'while ! curl -s http://localhost:8000/health > /dev/null 2>&1; do sleep 2; done'

if [ $? -eq 0 ]; then
    echo "✅ MCP Pro server is ready!"
else
    echo "⚠️  MCP Pro server might still be starting up. Check logs with: docker-compose logs postgres-mcp"
fi

# Test database connection
echo "🔗 Testing database connection..."
if command -v python3 &> /dev/null; then
    python3 -c "
import asyncio
import os
from dotenv import load_dotenv

async def test_connection():
    try:
        # Try to import asyncpg for connection testing
        try:
            import asyncpg
        except ImportError:
            print('⚠️  asyncpg not installed, skipping connection test')
            return True
            
        load_dotenv()
        
        conn = await asyncpg.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=5432,
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', 'dev'),
            database=os.getenv('DB_NAME', 'testdb')
        )
        
        # Test query
        result = await conn.fetch('SELECT COUNT(*) as table_count FROM information_schema.tables WHERE table_schema = \'public\'')
        table_count = result[0]['table_count']
        
        await conn.close()
        print(f'✅ Database connection successful! Found {table_count} tables.')
        return True
    except Exception as e:
        print(f'❌ Database connection failed: {e}')
        return False

if asyncio.run(test_connection()):
    print('')
    print('🎉 Setup completed successfully!')
    print('')
    print('🔥 Services running:')
    print('   📊 PostgreSQL: localhost:5432')
    print('   🤖 MCP Pro Server: http://localhost:8000')
    print('   🌐 pgAdmin: http://localhost:8080 (admin@example.com / admin)')
    print('')
    print('🔧 Next steps:')
    print('1. Activate virtual environment: source .venv/bin/activate')
    print('2. Test the advanced agent: python agent_postgres_pro.py')
    print('3. Or run with Streamlit: streamlit run app.py')
    print('')
    print('🚀 Advanced features available:')
    print('   • Index tuning and recommendations')
    print('   • Query explain plans and optimization')
    print('   • Database health checks and monitoring')
    print('   • Safe SQL execution with access controls')
else:
    print('❌ Setup failed. Please check your configuration.')
    exit 1
" || {
    echo "⚠️  Could not test connection, but setup appears complete."
    echo ""
    echo "🎉 Setup completed!"
    echo ""
    echo "🔥 Services running:"
    echo "   📊 PostgreSQL: localhost:5432"
    echo "   🤖 MCP Pro Server: http://localhost:8000"
    echo "   🌐 pgAdmin: http://localhost:8080 (admin@example.com / admin)"
    echo ""
    echo "🔧 Next steps:"
    echo "1. Install asyncpg: pip install asyncpg"
    echo "2. Activate virtual environment: source .venv/bin/activate"
    echo "3. Test the advanced agent: python agent_postgres_pro.py"
    echo "4. Or run with Streamlit: streamlit run app.py"
}
else
    echo "❌ Python3 not found. Please install Python 3.9+ first."
    exit 1
fi

echo ""
echo "📋 Quick test commands:"
echo "docker-compose logs postgres-mcp  # Check MCP server logs"
echo "curl http://localhost:8000/health  # Check MCP server health"
echo "python -c \"import asyncio; from agent_postgres_pro import run_postgres_agent_sse; asyncio.run(run_postgres_agent_sse('Analyze database health'))\"" 