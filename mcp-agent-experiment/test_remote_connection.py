#!/usr/bin/env python3
"""Test script for remote PostgreSQL connection"""

import asyncio
import asyncpg
import os
from dotenv import load_dotenv

async def test_remote_connection():
    """Test connection to remote PostgreSQL instance"""
    load_dotenv()
    
    # Get connection details from environment
    db_host = os.getenv('DB_HOST', '172.30.196.100')
    db_user = os.getenv('DB_USER', 'postgres')
    db_password = os.getenv('DB_PASSWORD', 'dev')
    db_name = os.getenv('DB_NAME', 'testdb')
    db_port = int(os.getenv('DB_PORT', '5432'))
    
    print(f"🔍 Testing connection to {db_host}:{db_port}/{db_name} as {db_user}")
    
    try:
        conn = await asyncpg.connect(
            host=db_host, port=db_port, user=db_user,
            password=db_password, database=db_name
        )
        
        version = await conn.fetchval("SELECT version()")
        print(f"✅ Connected! PostgreSQL version: {version[:50]}...")
        
        await conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_remote_connection())
    exit(0 if success else 1) 