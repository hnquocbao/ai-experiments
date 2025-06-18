import asyncio
import os
from dotenv import load_dotenv
from textwrap import dedent
from agno.agent import Agent, RunResponse
from agno.models.groq import Groq
from agno.models.openai import OpenAIChat
from agno.tools.mcp import MCPTools
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.sse import sse_client
from agno.utils.log import logger
from typing import Optional
from llm_model import get_model
import aiohttp


INSTRUCTIONS = dedent(
    """\
    You are an advanced PostgreSQL assistant with access to Postgres MCP Pro, a powerful database analysis and optimization tool.

    Your capabilities include:
    1. **Database Schema Analysis**: Understand and explore database structures with detailed schema information.
    2. **Query Execution**: Run SELECT queries and provide natural language summaries.
    3. **Performance Analysis**: Use explain plans and query optimization features.
    4. **Index Tuning**: Analyze and recommend database indexes for better performance.
    5. **Database Health Monitoring**: Check database health metrics and identify potential issues.
    6. **Workload Analysis**: Analyze database workloads and suggest optimizations.

    Available MCP Pro Tools:
    - `list_schemas`: List all database schemas
    - `list_objects`: List database objects (tables, views, etc.)
    - `get_object_details`: Get detailed information about specific database objects
    - `execute_sql`: Execute SQL statements with safety controls
    - `explain_query`: Get execution plans for queries
    - `get_top_queries`: Get slowest queries from pg_stat_statements
    - `analyze_workload_indexes`: Analyze workload and recommend indexes
    - `analyze_query_indexes`: Analyze specific queries for index recommendations
    - `analyze_db_health`: Perform comprehensive database health checks

    Your responses should be:
    - **Comprehensive yet accessible**: Provide detailed insights while remaining understandable
    - **Action-oriented**: Suggest specific improvements and optimizations when relevant
    - **Performance-focused**: Always consider performance implications
    - **Safety-conscious**: Mention any potential risks or considerations

    Examples of advanced queries you can handle:
    - "Analyze the database health and identify performance bottlenecks"
    - "What indexes should I add to improve query performance?"
    - "Show me the slowest queries and how to optimize them"
    - "Explain the execution plan for this complex query"
    - "What are the buffer cache hit rates and connection health?"

    Always provide actionable insights and recommendations based on the analysis.
    """
)

# Load environment variables from .env file
load_dotenv()
MODEL_ID = os.getenv("MODEL_ID")  # Optional, will use default if not set
MODEL_API_KEY = os.getenv("MODEL_API_KEY")
if not MODEL_API_KEY:
    raise ValueError("MODEL_API_KEY environment variable is not set. Please add it to your .env file.")

# Default model ID if not specified in environment variables
DEFAULT_MODEL_ID = "llama-3.3-70b-versatile"


async def postgres_pro_agent(session: ClientSession, model_id: Optional[str] = None) -> Agent:
    """
    Creates and configures an agent that interacts with Postgres MCP Pro server.

    Args:
        session (ClientSession): The MCP client session.
        model_id (Optional[str]): The ID of the language model to use.

    Returns:
        Agent: The configured agent.
    """
    
    # Initialize the MCP toolkit
    mcp_tools = MCPTools(session=session)
    await mcp_tools.initialize()
    
    # Use default model if none specified
    if not model_id:
        model_id = MODEL_ID or DEFAULT_MODEL_ID
    
    # Create and return the configured agent
    return Agent(
        model=get_model(model_id, MODEL_API_KEY),
        tools=[mcp_tools],
        instructions=INSTRUCTIONS,
        markdown=True,
        show_tool_calls=True,
    )


async def run_postgres_agent_sse(message: str, model_id: Optional[str] = None, mcp_url: str = "http://localhost:8000/sse") -> RunResponse:
    """
    Runs the PostgreSQL agent using SSE transport with Postgres MCP Pro server.

    Args:
        message (str): The message to send to the agent.
        model_id (Optional[str]): The ID of the language model to use.
        mcp_url (str): The URL of the MCP Pro server SSE endpoint.

    Returns:
        RunResponse: The agent's response.

    Raises:
        RuntimeError: If there is an error connecting to the MCP Pro server or running agent.
    """
    try:
        # SSE client returns (read, write) tuple like stdio_client
        async with sse_client(mcp_url) as (read, write):
            async with ClientSession(read, write) as session:
                agent = await postgres_pro_agent(session, model_id)
                response = await agent.arun(message)
                return response
    except Exception as e:
        raise RuntimeError(f"Error connecting to Postgres MCP Pro server or running agent: {e}") from e


async def run_postgres_agent_stdio(message: str, model_id: Optional[str] = None) -> RunResponse:
    """
    Runs the PostgreSQL agent using stdio transport with Postgres MCP Pro server.
    This is an alternative approach if SSE is not available.

    Args:
        message (str): The message to send to the agent.
        model_id (Optional[str]): The ID of the language model to use.

    Returns:
        RunResponse: The agent's response.
    """
    # Check for required PostgreSQL environment variables
    required_vars = ["DB_HOST", "DB_USER", "DB_PASSWORD", "DB_NAME"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

    # Build PostgreSQL connection string
    postgres_uri = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT', '5432')}/{os.getenv('DB_NAME')}"
    
    # Configure MCP server parameters using Docker with Postgres MCP Pro
    server_params = StdioServerParameters(
        command="docker",
        args=[
            "run",
            "-i",
            "--rm",
            "--network=host",
            "crystaldba/postgres-mcp",
            "--access-mode=unrestricted",
            postgres_uri
        ],
    )

    # Connect to the MCP server and run the agent
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                agent = await postgres_pro_agent(session, model_id)
                response = await agent.arun(message)
                return response
    except Exception as e:
        raise RuntimeError(f"Error connecting to Postgres MCP Pro server or running agent: {e}") from e


async def health_check_mcp_server(url: str = "http://localhost:8000/sse") -> bool:
    """
    Check if the MCP Pro server is healthy and responsive.
    
    Args:
        url (str): The SSE endpoint URL to check.

    Returns:
        bool: True if server is healthy, False otherwise.
    """
    try:
        # Try to connect to the SSE endpoint
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=3)) as response:
                # Accept any successful response or even connection error means server is up
                return response.status in [200, 400, 404, 405]  # Server is responding
    except aiohttp.ClientConnectorError:
        # Connection refused - server is not running
        logger.warning(f"Health check failed: Cannot connect to {url}")
        return False
    except Exception as e:
        # Other errors might still mean server is up but not responding to HTTP GET
        logger.warning(f"Health check got response: {e}")
        return True  # Assume server is up if we get any response


async def quick_test_connection() -> bool:
    """
    Quick test to see if we can connect to the MCP server via Docker.
    
    Returns:
        bool: True if connection is successful, False otherwise.
    """
    try:
        # Try a simple docker command to test the MCP connection
        import subprocess
        result = subprocess.run([
            "docker", "run", "--rm", "--network=host", 
            "crystaldba/postgres-mcp", "--help"
        ], capture_output=True, timeout=10)
        return result.returncode == 0
    except Exception as e:
        logger.warning(f"Quick connection test failed: {e}")
        return False


async def demo_advanced_features():
    """
    Demonstrates advanced features of Postgres MCP Pro.
    """
    print("🚀 Postgres MCP Pro Demo - Advanced Database Analysis")
    print("=" * 60)
    
    # Check if MCP Pro server is running
    if not await health_check_mcp_server():
        print("❌ MCP Pro server is not running. Start it with: docker-compose up -d postgres-mcp")
        return
    
    print("✅ MCP Pro server is healthy!")
    
    # Demo queries showcasing advanced features
    demo_queries = [
        {
            "title": "Database Health Analysis",
            "query": "Perform a comprehensive database health check and report any issues or recommendations.",
            "description": "Analyze buffer cache, connections, vacuum health, constraints, and more"
        },
        {
            "title": "Performance Bottleneck Identification",
            "query": "What are the top 5 slowest queries in the database and how can they be optimized?",
            "description": "Identify slow queries and get optimization suggestions"
        },
        {
            "title": "Index Tuning Recommendations",
            "query": "Analyze the current workload and recommend indexes to improve performance.",
            "description": "Advanced index analysis with cost-benefit evaluation"
        },
        {
            "title": "Query Execution Plan Analysis",
            "query": "EXPLAIN SELECT o.*, u.username, p.name FROM orders o JOIN users u ON o.user_id = u.id JOIN order_items oi ON o.id = oi.order_id JOIN products p ON oi.product_id = p.id WHERE o.status = 'completed'",
            "description": "Detailed execution plan analysis with optimization suggestions"
        }
    ]
    
    for i, demo in enumerate(demo_queries, 1):
        print(f"\n{i}. {demo['title']}")
        print(f"   Description: {demo['description']}")
        print(f"   Query: {demo['query'][:100]}...")
        
        try:
            response = await run_postgres_agent_sse(demo['query'])
            print(f"   ✅ Completed successfully")
            print(f"   Response preview: {response.content[:200]}...")
        except Exception as e:
            print(f"   ❌ Failed: {e}")
        
        print("-" * 60)


async def main():
    """
    Example usage of the Postgres MCP Pro agent.
    """
    try:
        # Test basic functionality
        logger.info("Testing Postgres MCP Pro agent...")
        
        # First, check if the server is running
        if await health_check_mcp_server():
            logger.info("✅ MCP Pro server is healthy, using SSE transport")
            response = await run_postgres_agent_sse("List all tables in the database and provide a summary of the data structure")
        else:
            logger.info("⚠️  MCP Pro server not available via SSE, trying stdio approach")
            response = await run_postgres_agent_stdio("List all tables in the database and provide a summary of the data structure")
        
        logger.info(f"Agent Response: {response.content}")
        
        # Run advanced demo
        print("\n" + "="*60)
        await demo_advanced_features()
        
    except ValueError as ve:
        logger.error(f"Configuration error: {ve}")
        logger.info("Make sure to set up your .env file with database credentials")
    except RuntimeError as re:
        logger.error(f"Runtime error: {re}")
        logger.info("Make sure Postgres MCP Pro server is running: docker-compose up -d postgres-mcp")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    asyncio.run(main()) 