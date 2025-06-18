# 🐳 Docker Compose Setup for Remote PostgreSQL

This guide explains how to use the modified `docker-compose.yml` with remote PostgreSQL instances.

## 🔧 Configuration Overview

The updated `docker-compose.yml` now supports:
- ✅ **Remote PostgreSQL connections** using environment variables
- ✅ **Local PostgreSQL** for development (optional)
- ✅ **Flexible configuration** through `.env` file
- ✅ **Service profiles** to choose local vs remote setup

## 📋 Quick Start

### Step 1: Create Environment File

Create a `.env` file in your project directory:

```bash
# ===== REMOTE POSTGRESQL CONNECTION =====
DB_HOST=172.30.196.100              # Your remote WSL IP
DB_USER=postgres                    # PostgreSQL username
DB_PASSWORD=your_password           # PostgreSQL password
DB_NAME=your_database               # Database name
DB_PORT=5432                        # PostgreSQL port

# ===== AI MODEL CONFIGURATION =====
MODEL_API_KEY=your_gemini_api_key
MODEL_ID=gemini-2.0-flash-exp

# ===== DOCKER CONFIGURATION =====
NETWORK_MODE=host                   # Better for remote connections
```

### Step 2: Start MCP Server for Remote PostgreSQL

```bash
# Start only the MCP server (no local PostgreSQL)
docker-compose up -d postgres-mcp

# Or start with pgAdmin too
docker-compose --profile remote up -d
```

### Step 3: Verify Connection

```bash
# Check if MCP server is running
curl http://localhost:8000/health

# Check logs
docker-compose logs postgres-mcp
```

## 🎯 Different Setup Scenarios

### Scenario 1: Remote PostgreSQL Only

```bash
# .env file
DB_HOST=172.30.196.100
DB_USER=postgres
DB_PASSWORD=dev
DB_NAME=testdb
DB_PORT=5432
MODEL_API_KEY=your_api_key
MODEL_ID=gemini-2.0-flash-exp

# Start services
docker-compose up -d postgres-mcp
```

### Scenario 2: Local PostgreSQL for Development

```bash
# .env file
DB_HOST=localhost
DB_USER=postgres
DB_PASSWORD=dev
DB_NAME=testdb
DB_PORT=5433
POSTGRES_PORT=5433
MODEL_API_KEY=your_api_key
MODEL_ID=gemini-2.0-flash-exp

# Start all local services
docker-compose --profile local up -d
```

### Scenario 3: Remote + pgAdmin

```bash
# .env file
DB_HOST=172.30.196.100
DB_USER=postgres
DB_PASSWORD=dev
DB_NAME=testdb
PGLADMIN_EMAIL=admin@example.com
PGLADMIN_PASSWORD=secure_password
PGLADMIN_PORT=8080

# Start remote setup with pgAdmin
docker-compose --profile remote up -d
```

## 📝 Environment Variables Reference

### Required Variables
```bash
DB_HOST=                  # PostgreSQL host (remote WSL IP or localhost)
DB_USER=                  # Database username
DB_PASSWORD=              # Database password
DB_NAME=                  # Database name
MODEL_API_KEY=            # AI model API key
```

### Optional Variables
```bash
DB_PORT=5432              # PostgreSQL port (default: 5432)
MODEL_ID=                 # AI model ID (default: depends on llm_model.py)
NETWORK_MODE=host         # Docker network mode (default: bridge)

# Local PostgreSQL (only if using --profile local)
POSTGRES_DB=testdb        # Local DB name
POSTGRES_USER=postgres    # Local DB user
POSTGRES_PASSWORD=dev     # Local DB password
POSTGRES_PORT=5433        # Local DB port

# pgAdmin (optional)
PGLADMIN_EMAIL=admin@example.com
PGLADMIN_PASSWORD=admin
PGLADMIN_PORT=8080
```

## 🔍 Service Profiles

### Using Profiles
```bash
# Remote PostgreSQL setup
docker-compose --profile remote up -d

# Local PostgreSQL setup  
docker-compose --profile local up -d

# Default: only MCP server
docker-compose up -d postgres-mcp
```

### Service Profile Mapping
- `postgres`: Local PostgreSQL (profile: `local`)
- `postgres-mcp`: MCP Server (always available)
- `pgadmin`: Database admin UI (profiles: `local`, `remote`)

## 🐛 Troubleshooting

### Common Issues

#### 1. MCP Server Can't Connect to Remote PostgreSQL
```bash
# Check if remote PostgreSQL allows connections
pg_isready -h 172.30.196.100 -p 5432 -U postgres

# Test with docker network
docker run --rm --network=host postgres:15 \
  pg_isready -h 172.30.196.100 -p 5432 -U postgres
```

#### 2. Environment Variables Not Loading
```bash
# Verify .env file exists and has correct values
cat .env

# Check if docker-compose reads the variables
docker-compose config
```

#### 3. Port Conflicts
```bash
# Check what's using the ports
sudo netstat -tlnp | grep 8000
sudo netstat -tlnp | grep 5432

# Change ports in .env if needed
DB_PORT=5433
PGLADMIN_PORT=8081
```

#### 4. Network Connection Issues
```bash
# Test network connectivity
ping 172.30.196.100
nc -zv 172.30.196.100 5432

# Try host networking mode
NETWORK_MODE=host
```

## 🔧 Advanced Configuration

### Custom Network for Remote Access
```yaml
# Add to docker-compose.yml if needed
networks:
  postgres-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
```

### SSL/TLS Connections
```bash
# In .env for SSL connections
DATABASE_URI=postgresql://${DB_USER}:${DB_PASSWORD}@${DB_HOST}:${DB_PORT}/${DB_NAME}?sslmode=require
```

### Connection Pooling
```bash
# For production, consider pgbouncer
docker run -d --name pgbouncer \
  -e POOL_MODE=transaction \
  -e SERVER_TLS_SSLMODE=prefer \
  -e DATABASE_URL=postgresql://user:pass@host:5432/db \
  pgbouncer/pgbouncer:latest
```

## 🚀 Running Your Application

After setting up Docker Compose:

```bash
# 1. Start the MCP server
docker-compose up -d postgres-mcp

# 2. Verify it's healthy
curl http://localhost:8000/health

# 3. Run your application
streamlit run app_postgres_pro.py
```

## 📊 Monitoring

### Check Service Status
```bash
# View running services
docker-compose ps

# Check specific service logs
docker-compose logs postgres-mcp
docker-compose logs pgadmin

# Follow logs in real-time
docker-compose logs -f postgres-mcp
```

### Health Checks
```bash
# MCP Server health
curl http://localhost:8000/health

# PostgreSQL health (if local)
docker-compose exec postgres pg_isready -U postgres

# Test connection from MCP server
docker-compose exec postgres-mcp psql $DATABASE_URI -c "SELECT version();"
```

## 🔐 Security Best Practices

1. **Use strong passwords** in production
2. **Limit network access** in pg_hba.conf
3. **Use SSL connections** for remote databases
4. **Regularly update** Docker images
5. **Monitor logs** for suspicious activity

## 📞 Getting Help

If you encounter issues:
1. Check service logs: `docker-compose logs postgres-mcp`
2. Verify environment variables: `docker-compose config`
3. Test database connectivity: `python test_remote_connection.py`
4. Check network connectivity between containers and remote host

---

**Note:** Replace `172.30.196.100` with your actual remote WSL instance IP address. 