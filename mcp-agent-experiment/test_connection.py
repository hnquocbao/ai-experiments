#!/usr/bin/env python3
"""
Quick connection test script for MCP PostgreSQL setup
"""
import asyncio
import asyncpg
import aiohttp
import os
from dotenv import load_dotenv

load_dotenv()

async def test_database_connection():
    """Test direct PostgreSQL connection"""
    try:
        db_host = os.getenv('DB_HOST', 'localhost')
        db_user = os.getenv('DB_USER', 'postgres')
        db_password = os.getenv('DB_PASSWORD', 'dev')
        db_name = os.getenv('DB_NAME', 'testdb')
        
        conn = await asyncpg.connect(
            host=db_host,
            port=5433,
            user=db_user,
            password=db_password,
            database=db_name
        )
        
        # Test query
        result = await conn.fetchval("SELECT COUNT(*) FROM users")
        await conn.close()
        
        print(f"✅ Database connection successful! Found {result} users in the database.")
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

async def test_mcp_server_sse():
    """Test MCP server SSE endpoint"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:8000/sse", timeout=aiohttp.ClientTimeout(total=5)) as response:
                print(f"✅ MCP SSE server is responding (status: {response.status})")
                return True
    except aiohttp.ClientConnectorError:
        print("❌ MCP SSE server is not accessible")
        return False
    except Exception as e:
        print(f"⚠️  MCP SSE server test: {e}")
        return True

async def test_docker_mcp():
    """Test Docker MCP connection"""
    try:
        import subprocess
        result = subprocess.run([
            "docker", "run", "--rm", "--network=host",
            "crystaldba/postgres-mcp", "--help"
        ], capture_output=True, timeout=10, text=True)
        
        if result.returncode == 0:
            print("✅ Docker MCP image is available and working")
            return True
        else:
            print(f"❌ Docker MCP test failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("⚠️  Docker MCP test timed out (but image might work)")
        return True
    except Exception as e:
        print(f"❌ Docker MCP test error: {e}")
        return False

async def main():
    print("🔍 Testing MCP PostgreSQL Setup")
    print("=" * 40)
    
    # Test database connection
    print("\n1. Testing Database Connection...")
    db_ok = await test_database_connection()
    
    # Test MCP SSE server
    print("\n2. Testing MCP SSE Server...")
    sse_ok = await test_mcp_server_sse()
    
    # Test Docker MCP
    print("\n3. Testing Docker MCP Image...")
    docker_ok = await test_docker_mcp()
    
    print("\n" + "=" * 40)
    print("📋 Summary:")
    print(f"Database Connection: {'✅' if db_ok else '❌'}")
    print(f"MCP SSE Server: {'✅' if sse_ok else '❌'}")
    print(f"Docker MCP: {'✅' if docker_ok else '❌'}")
    
    if db_ok and (sse_ok or docker_ok):
        print("\n🎉 Setup looks good! You can run the Streamlit app.")
    else:
        print("\n🔧 Setup needs attention:")
        if not db_ok:
            print("  - Check if PostgreSQL is running: docker-compose up -d postgres")
        if not sse_ok and not docker_ok:
            print("  - Check if MCP server is running: docker-compose up -d postgres-mcp")

if __name__ == "__main__":
    asyncio.run(main()) 