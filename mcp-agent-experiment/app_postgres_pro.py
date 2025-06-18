import streamlit as st
import asyncio
from agent_postgres_pro import run_postgres_agent_sse, run_postgres_agent_stdio, health_check_mcp_server
from typing import Dict, Any

st.set_page_config(
    page_title="PostgreSQL Pro MCP Agent",
    page_icon="🐘",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Report a bug": "https://github.com/vivekpathania/ai-experiments/issues"
    }
)

# Title and Header
st.title("🐘 PostgreSQL Pro MCP Agent")
st.write(
    "Advanced PostgreSQL database analysis and optimization using MCP Pro. "
    "This app provides comprehensive database health checks, performance analysis, and optimization recommendations."
)

# Sidebar
with st.sidebar:
    st.header("ℹ️ About PostgreSQL Pro")
    st.markdown(
        "This application provides advanced PostgreSQL database analysis capabilities including:\n\n"
        "• **Database Health Monitoring**: Check database health metrics and identify potential issues\n"
        "• **Performance Analysis**: Analyze query performance and identify bottlenecks\n"
        "• **Index Tuning**: Get recommendations for database indexes\n"
        "• **Query Optimization**: Analyze execution plans and suggest optimizations\n"
        "• **Workload Analysis**: Comprehensive database workload insights"
    )
    
    st.markdown("---")
    st.header("🚀 Quick Actions")
    
    # Quick action buttons in sidebar
    if st.button("🔍 Database Health Check", key="health_check_btn"):
        st.session_state.quick_query = "Perform a comprehensive database health check and report any issues or recommendations."
    
    if st.button("⚡ Performance Analysis", key="perf_analysis_btn"):
        st.session_state.quick_query = "What are the top 5 slowest queries in the database and how can they be optimized?"
    
    if st.button("📊 Index Recommendations", key="index_recommendations_btn"):
        st.session_state.quick_query = "Analyze the current workload and recommend indexes to improve performance."
    
    st.markdown("---")
    st.markdown("👨‍💻 Developed as an AI experiment. Contribute on [GitHub](https://github.com/vivekpathania/ai-experiments)")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "mcp_server_status" not in st.session_state:
    st.session_state.mcp_server_status = None
if "quick_query" not in st.session_state:
    st.session_state.quick_query = None

# Check MCP server status
@st.cache_data(ttl=60)  # Cache for 60 seconds
def check_server_status():
    try:
        # First try the health check
        health_result = asyncio.run(health_check_mcp_server())
        if health_result:
            return True
        
        # If health check fails, try quick connection test
        from agent_postgres_pro import quick_test_connection
        return asyncio.run(quick_test_connection())
    except Exception as e:
        st.warning(f"Server check failed: {e}")
        return False

server_healthy = check_server_status()

# Server status indicator
if server_healthy:
    st.success("✅ MCP Pro Server is running and healthy")
else:
    st.error("❌ MCP Pro Server is not available. Please start it with: `docker-compose up -d postgres-mcp`")
    st.info("💡 The app will attempt to use stdio transport as fallback.")

# Main chat interface
st.header("💬 PostgreSQL Pro Chat")

# Create a container for the chat messages
chat_container = st.container()

# Display chat history
with chat_container:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if message["role"] == "assistant" and message.get("error"):
                st.error(message["content"])
            else:
                st.markdown(message["content"])

# Handle quick query from sidebar
if st.session_state.quick_query:
    user_query = st.session_state.quick_query
    st.session_state.quick_query = None  # Clear the quick query
else:
    user_query = st.chat_input(
        "Ask about database performance, optimization, or health analysis...",
        key="chat_input"
    )

if user_query:
    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": user_query})
    
    # Display user message
    with chat_container:
        with st.chat_message("user"):
            st.markdown(user_query)
    
    # Process the query
    with st.spinner("🔍 Analyzing database... This may take a moment for complex queries."):
        try:
            # Add timeout wrapper for long-running queries
            async def run_query_with_timeout():
                if server_healthy:
                    return await run_postgres_agent_sse(user_query)
                else:
                    return await run_postgres_agent_stdio(user_query)
            
            # Run with 60 second timeout
            response = asyncio.run(asyncio.wait_for(run_query_with_timeout(), timeout=60.0))
            
            # Add successful response
            st.session_state.messages.append({
                "role": "assistant", 
                "content": response.content,
                "error": False
            })
            
            # Display response
            with chat_container:
                with st.chat_message("assistant"):
                    st.markdown(response.content)
                    
        except asyncio.TimeoutError:
            error_msg = "Query timed out after 60 seconds. Please try a simpler query or check your database connection."
            st.session_state.messages.append({
                "role": "assistant",
                "content": error_msg,
                "error": True
            })
            
            with chat_container:
                with st.chat_message("assistant"):
                    st.error(error_msg)
                    
        except ValueError as ve:
            error_msg = f"Configuration Error: {str(ve)}\n\nPlease check your .env file and ensure all database credentials are set."
            st.session_state.messages.append({
                "role": "assistant",
                "content": error_msg,
                "error": True
            })
            
            with chat_container:
                with st.chat_message("assistant"):
                    st.error(error_msg)
                    
        except RuntimeError as re:
            error_msg = f"Connection Error: {str(re)}\n\nPlease ensure the PostgreSQL MCP Pro server is running."
            st.session_state.messages.append({
                "role": "assistant",
                "content": error_msg,
                "error": True
            })
            
            with chat_container:
                with st.chat_message("assistant"):
                    st.error(error_msg)
                    
        except Exception as e:
            error_msg = f"Unexpected Error: {str(e)}"
            st.session_state.messages.append({
                "role": "assistant",
                "content": error_msg,
                "error": True
            })
            
            with chat_container:
                with st.chat_message("assistant"):
                    st.error(error_msg)

# Clear chat button
if st.session_state.messages:
    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

# Example queries section
with st.expander("💡 Example Queries"):
    st.markdown("""
    **Database Health & Performance:**
    - "Perform a comprehensive database health check"
    - "What are the current buffer cache hit rates?"
    - "Show me database connection statistics"
    
    **Query Optimization:**
    - "What are the top 5 slowest queries and how can I optimize them?"
    - "Analyze the execution plan for my complex JOIN query"
    - "Show me queries that are doing full table scans"
    
    **Index Analysis:**
    - "What indexes should I add to improve performance?"
    - "Analyze my current indexes and suggest improvements"
    - "Show me unused indexes that can be dropped"
    
    **Schema Analysis:**
    - "List all tables and their relationships"
    - "Show me the largest tables in my database"
    - "Analyze my database schema structure"
    """) 