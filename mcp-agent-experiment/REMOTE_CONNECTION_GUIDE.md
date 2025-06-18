# 🌐 Connecting to Remote PostgreSQL Instance

This guide explains how to configure your MCP PostgreSQL Pro app to connect to a PostgreSQL database running on another WSL Ubuntu instance.

## 📋 Prerequisites

- PostgreSQL running on remote WSL instance
- Network access between WSL instances
- PostgreSQL configured to accept remote connections

## 🔍 Step 1: Find Remote WSL IP Address

On the **remote WSL instance** where PostgreSQL is running:

```bash
# Method 1: Get WSL IP address
ip addr show eth0 | grep "inet " | awk '{print $2}' | cut -d/ -f1

# Method 2: Alternative method
hostname -I | awk '{print $1}'

# Example output: 172.30.196.100
```

## ⚙️ Step 2: Configure PostgreSQL on Remote Instance

### Edit PostgreSQL Configuration

```bash
# Find PostgreSQL version and edit main config
sudo nano /etc/postgresql/*/main/postgresql.conf

# Add or modify this line:
listen_addresses = '*'          # Allow connections from all hosts
# OR for specific network:
# listen_addresses = '172.30.0.0/16'
```

### Configure Host-Based Authentication

```bash
# Edit authentication config
sudo nano /etc/postgresql/*/main/pg_hba.conf

# Add this line (adjust subnet as needed):
host    all             all             172.30.0.0/16           md5

# For specific IP ranges, you can use:
# host    all             all             172.30.196.0/24         md5
```

### Restart PostgreSQL Service

```bash
sudo systemctl restart postgresql
sudo systemctl status postgresql  # Verify it's running
```

## 🔧 Step 3: Update Environment Variables

Create a `.env` file in your project directory:

```bash
# --- Remote PostgreSQL Connection ---
DB_HOST=172.30.196.100          # Replace with your remote WSL IP
DB_USER=postgres                # Your PostgreSQL username
DB_PASSWORD=your_password       # Your PostgreSQL password
DB_NAME=your_database_name      # Your database name
DB_PORT=5432                    # PostgreSQL port (default 5432)

# --- AI Model Configuration ---
MODEL_API_KEY=your_api_key_here
MODEL_ID=gemini-2.0-flash-exp

# --- Example for common setup ---
# DB_HOST=172.30.196.100
# DB_USER=postgres
# DB_PASSWORD=dev
# DB_NAME=testdb
```

## 🧪 Step 4: Test the Connection

### Test Basic PostgreSQL Connection

```bash
# Install PostgreSQL client tools if not available
sudo apt update && sudo apt install postgresql-client

# Test connection from current WSL instance
pg_isready -h 172.30.196.100 -p 5432 -U postgres

# Test with psql (you'll be prompted for password)
psql -h 172.30.196.100 -p 5432 -U postgres -d testdb
```

### Test with Python Script

```python
import asyncpg
import asyncio

async def test_connection():
    try:
        conn = await asyncpg.connect(
            host='172.30.196.100',    # Your remote WSL IP
            port=5432,
            user='postgres',
            password='your_password',
            database='testdb'
        )
        
        result = await conn.fetchval("SELECT version()")
        print(f"✅ Connected successfully!")
        print(f"PostgreSQL version: {result}")
        
        await conn.close()
        return True
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

# Run the test
asyncio.run(test_connection())
```

## 🚀 Step 5: Run Your Application

```bash
# Activate virtual environment
source .venv/bin/activate

# Install dependencies if needed
uv sync

# Run the Streamlit app
streamlit run app_postgres_pro.py
```

## 🔍 Troubleshooting

### Common Issues and Solutions

#### 1. Connection Refused
```bash
# Check if PostgreSQL is running on remote instance
sudo systemctl status postgresql

# Check if PostgreSQL is listening on correct port
sudo netstat -tlnp | grep 5432

# Verify firewall settings (if applicable)
sudo ufw status
```

#### 2. Authentication Failed
```bash
# Verify user exists and has correct permissions
sudo -u postgres psql -c "\du"

# Reset password if needed
sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'new_password';"
```

#### 3. Host Not Allowed
```bash
# Check pg_hba.conf configuration
sudo cat /etc/postgresql/*/main/pg_hba.conf | grep host

# Verify client IP is in allowed range
ip addr show eth0 | grep inet
```

#### 4. Network Issues
```bash
# Test basic network connectivity
ping 172.30.196.100

# Test specific port connectivity
telnet 172.30.196.100 5432
# OR
nc -zv 172.30.196.100 5432
```

## 🔐 Security Considerations

### For Development
- Use strong passwords
- Limit access to specific IP ranges in pg_hba.conf
- Consider using SSL connections

### For Production
- Use SSL/TLS encryption
- Implement connection pooling
- Use dedicated database users with limited privileges
- Monitor connection logs

## 📝 Example Complete .env File

```bash
# Remote PostgreSQL Configuration
DB_HOST=172.30.196.100
DB_USER=postgres
DB_PASSWORD=secure_password_123
DB_NAME=production_db
DB_PORT=5432

# AI Model Configuration (choose one)
MODEL_API_KEY=your_gemini_api_key
MODEL_ID=gemini-2.0-flash-exp

# Alternative models:
# MODEL_ID=gemini-1.5-pro
# MODEL_ID=llama-3.3-70b-versatile
# MODEL_ID=gpt-4o
```

## 🎯 Advanced Configuration

### Connection Pooling
For production setups, consider using connection pooling:

```python
# In your application
import asyncpg

pool = await asyncpg.create_pool(
    host='172.30.196.100',
    port=5432,
    user='postgres',
    password='your_password',
    database='testdb',
    min_size=1,
    max_size=10
)
```

### SSL Configuration
To enable SSL connections:

```bash
# In postgresql.conf
ssl = on
ssl_cert_file = 'server.crt'
ssl_key_file = 'server.key'
```

## 📞 Getting Help

If you encounter issues:

1. Check PostgreSQL logs: `sudo tail -f /var/log/postgresql/postgresql-*-main.log`
2. Verify network connectivity between WSL instances
3. Test with simple tools before using the application
4. Check WSL networking documentation for your Windows version

---

**Note:** Replace `172.30.196.100` with your actual remote WSL instance IP address throughout this guide. 