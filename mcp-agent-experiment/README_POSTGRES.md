# MCP PostgreSQL Chatbot & Dashboard with Postgres MCP Pro

This is an advanced PostgreSQL chatbot that uses the powerful [Postgres MCP Pro](https://github.com/crystaldba/postgres-mcp) server for comprehensive database analysis, optimization, and management through natural language processing.

## ✨ Features

*   **Advanced PostgreSQL Analysis:** Interact with PostgreSQL using the professional-grade Postgres MCP Pro server
*   **Index Tuning & Optimization:** Intelligent index recommendations with cost-benefit analysis
*   **Query Performance Analysis:** Detailed execution plans and optimization suggestions
*   **Database Health Monitoring:** Comprehensive health checks and performance metrics
*   **Workload Analysis:** Analyze database workloads and identify bottlenecks
*   **Safe SQL Execution:** Configurable access controls with read-only and unrestricted modes
*   **Docker-First Approach:** Complete containerized setup for easy deployment

## 🚀 Quick Start

### Prerequisites

*   **Docker & Docker Compose:** Required for containerized deployment
*   **UV Package Manager:** For Python dependency management
*   **Python 3.10+:** For the agent scripts
*   **API Keys:** Groq or OpenAI API key for LLM functionality

### 1. One-Command Setup

```bash
git clone <your-repo>
cd mcp-agent-experiment
./setup_postgres.sh
```

This script will:
- ✅ Check all prerequisites
- 🐳 Pull the Postgres MCP Pro Docker image
- 🐘 Start PostgreSQL with sample data
- 🤖 Start the MCP Pro server with advanced features
- 🔗 Test all connections
- 📊 Launch pgAdmin for database management

### 2. Manual Setup (Alternative)

```bash
# 1. Install dependencies
uv sync

# 2. Create environment file
cp env.postgres.example .env
# Edit .env with your API keys

# 3. Start all services
docker-compose up -d

# 4. Test the advanced agent
source .venv/bin/activate
python agent_postgres_pro.py
```

## 🏗️ Architecture

The setup includes these services:

| Service | Port | Description |
|---------|------|-------------|
| **PostgreSQL** | 5432 | Main database with sample e-commerce data |
| **Postgres MCP Pro** | 8000 | Advanced MCP server with optimization tools |
| **pgAdmin** | 8080 | Web-based database administration |

## 🔧 Configuration

### Environment Variables

Create a `.env` file with:

```bash
# Database Connection
DB_HOST=localhost
DB_USER=postgres
DB_PASSWORD=dev
DB_NAME=testdb

# AI Model Configuration
MODEL_API_KEY=your_groq_or_openai_api_key
MODEL_ID=llama-3.3-70b-versatile
```

### MCP Pro Server Features

The [Postgres MCP Pro server](https://github.com/crystaldba/postgres-mcp) provides:

- **🔍 Database Health Checks:** Buffer cache hit rates, connection health, vacuum analysis
- **⚡ Index Tuning:** Advanced algorithms for optimal index recommendations
- **📈 Query Analysis:** EXPLAIN plans with optimization suggestions
- **🛡️ Safe Execution:** Read-only mode with SQL parsing protection
- **🧠 Schema Intelligence:** Context-aware SQL generation
- **📊 Performance Monitoring:** pg_stat_statements integration

## 💡 Usage Examples

### Basic Database Queries

```python
from agent_postgres_pro import run_postgres_agent_sse

# Simple data queries
await run_postgres_agent_sse("How many users are in the database?")
await run_postgres_agent_sse("What are the top-selling products?")
await run_postgres_agent_sse("Show me recent orders by status")
```

### Advanced Performance Analysis

```python
# Database health analysis
await run_postgres_agent_sse("Analyze database health and identify any performance issues")

# Index optimization
await run_postgres_agent_sse("Analyze the current workload and recommend indexes to improve performance")

# Query optimization
await run_postgres_agent_sse("What are the slowest queries and how can they be optimized?")

# Execution plan analysis
await run_postgres_agent_sse("EXPLAIN this query: SELECT * FROM orders JOIN users ON orders.user_id = users.id WHERE orders.status = 'pending'")
```

### Database Monitoring

```python
# Connection and resource monitoring
await run_postgres_agent_sse("Check buffer cache hit rates and connection health")

# Vacuum and maintenance analysis
await run_postgres_agent_sse("Analyze vacuum health and identify tables that need maintenance")

# Constraint validation
await run_postgres_agent_sse("Check for invalid constraints and data integrity issues")
```

## 🎯 Advanced Features

### 1. Index Tuning with Cost-Benefit Analysis

The system uses industrial-strength algorithms to:
- Analyze query workloads from `pg_stat_statements`
- Generate candidate indexes using column usage patterns
- Evaluate performance improvements with `hypopg` simulation
- Provide cost-benefit analysis for storage vs. performance trade-offs

### 2. Query Performance Optimization

- **Execution Plan Analysis:** Detailed EXPLAIN output with recommendations
- **Parameter Sampling:** Realistic parameter values for plan accuracy
- **Optimization Suggestions:** Specific recommendations for query improvements
- **Performance Prediction:** Simulate improvements before implementation

### 3. Comprehensive Health Monitoring

- **Buffer Cache Analysis:** Identify memory utilization issues
- **Connection Health:** Monitor connection pooling and utilization
- **Vacuum Health:** Prevent transaction ID wraparound issues
- **Replication Monitoring:** Check replication lag and status
- **Constraint Validation:** Ensure data integrity

## 🛠️ Development & Testing

### Running Tests

```bash
# Test database connection
python -c "import asyncio; from agent_postgres_pro import health_check_mcp_server; asyncio.run(health_check_mcp_server())"

# Test MCP Pro features
python agent_postgres_pro.py

# Run comprehensive demo
python -c "import asyncio; from agent_postgres_pro import demo_advanced_features; asyncio.run(demo_advanced_features())"
```

### Accessing Services

- **pgAdmin:** http://localhost:8080 (admin@example.com / admin)
- **MCP Pro Server:** http://localhost:8000 (health check: /health)
- **PostgreSQL:** localhost:5432 (postgres / dev)

### Logs and Monitoring

```bash
# Check MCP Pro server logs
docker-compose logs postgres-mcp

# Monitor PostgreSQL
docker-compose logs postgres

# Check all services
docker-compose ps
```

## 🔒 Security & Safety

### Access Modes

- **Unrestricted Mode:** Full read/write access for development
- **Restricted Mode:** Read-only with safety controls for production

### SQL Safety Features

- **SQL Parsing:** Prevents dangerous operations like COMMIT/ROLLBACK circumvention
- **Read-only Transactions:** Ensures data safety in restricted mode
- **Query Timeout:** Prevents long-running queries from impacting performance

## 🚨 Troubleshooting

### Common Issues

1. **MCP Pro server not starting:**
   ```bash
   docker-compose logs postgres-mcp
   docker pull crystaldba/postgres-mcp:latest
   ```

2. **Connection refused:**
   ```bash
   docker-compose ps  # Check if services are running
   docker-compose up -d  # Restart services
   ```

3. **Health check failures:**
   ```bash
   curl http://localhost:8000/health
   docker-compose restart postgres-mcp
   ```

### Performance Tuning

For production environments:
- Increase PostgreSQL shared_buffers
- Configure pg_stat_statements for workload analysis
- Set up proper connection pooling
- Monitor disk I/O and memory usage

## 📚 Resources

- [Postgres MCP Pro Documentation](https://github.com/crystaldba/postgres-mcp)
- [Model Context Protocol](https://modelcontextprotocol.io)
- [PostgreSQL Performance Tuning](https://www.postgresql.org/docs/current/performance-tips.html)

## 🤝 Contributing

Contributions are welcome! Please feel free to open issues or submit pull requests.

## 📄 License

MIT License - see LICENSE file for details. 