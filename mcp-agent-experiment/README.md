# MCP SQL Chatbot & Dashboard

This project demonstrates how to build an interactive SQL chatbot and a dynamic dashboard using natural language processing (NLP) and the Modular Control Protocol (MCP). It allows users to query an SQL database using natural language and visualize the data in a web-based dashboard.

## Features

*   **Natural Language SQL Queries:** Interact with an SQL database using natural language. The chatbot understands your questions and translates them into SQL queries.
*   **Dynamic Dashboard Generation:** Generate interactive HTML dashboards based on the database schema and data.
*   **Database Schema Analysis:** The system analyzes the database schema to identify the domain, key metrics, and appropriate visualizations.
*   **MCP Integration:** Leverages the Modular Control Protocol (MCP) for secure and efficient database interaction.
*   **Interactive Charts:** Uses Chart.js to create interactive charts in the dashboard.
*   **Responsive Design:** The generated dashboards are responsive and mobile-friendly, thanks to Tailwind CSS.
*   **UV Package Manager:** Uses UV package manager for dependency management.

## Project Structure

*   **`app.py`:** The main Streamlit application that provides the user interface for the chatbot and dashboard.
*   **`agent.py`:** Contains the code for the natural language SQL query agent.
*   **`dashboard_agent.py`:** Contains the code for the dashboard generation agent.

## Prerequisites

*   **UV:** This project uses the UV package manager. Install it by following the instructions on the UV website: https://astral.sh/uv.
*   **Python 3.9+:** Ensure you have Python 3.9 or a later version installed.
*   **MCP SQL Server:** You need an MCP SQL server running. You can set it up using the `uvx` command.
*   **Database:** An SQL database (e.g., MySQL, PostgreSQL) with some data.
*   **Environment Variables:** Set the following environment variables in a `.env` file in the project root:
    *   `MODEL_API_KEY`: Your API key for the chosen model provider (Groq, OpenAI, or Gemini).
    *   `MODEL_ID`: The model id to use (see supported models below).
    *   `DB_HOST`: The hostname or IP address of your database server.
    *   `DB_USER`: The username for your database.
    *   `DB_PASSWORD`: The password for your database.
    *   `DB_NAME`: The name of your database.

### Supported AI Models

*   **Groq Models:**
    *   `llama-3.3-70b-versatile` (default)
    *   `mixtral-8x7b-32768`
*   **OpenAI Models:**
    *   `gpt-4o`
    *   `gpt-3.5-turbo`
*   **Google Gemini Models:**
    *   `gemini-2.0-flash-exp`
    *   `gemini-1.5-pro`
    *   `gemini-1.5-flash`

## Setup and Installation (using UV)

1.  **Clone the Repository:**

    ```bash
    git clone https://github.com/vivekpathania/ai-experiments
    cd mcp-agent-experiment
    ```

2.  **Install Dependencies with UV:**

    ```bash
    uv sync
    ```
    This command will:
    * Create a virtual environment if one does not exist.
    * Install all the dependencies listed in the `pyproject.toml` file.

3.  **Create `.env` File:**

    Create a `.env` file in the project root and add your environment variables:

    ```
    DB_HOST=your_db_host
    DB_USER=your_db_user
    DB_PASSWORD=your_db_password
    DB_NAME=your_db_name
    MODEL_API_KEY=your_api_key_here
    MODEL_ID=gemini-2.0-flash-exp
    ```
    
    **Getting API Keys:**
    *   **Groq:** Get your free API key from [Groq Console](https://console.groq.com/)
    *   **OpenAI:** Get your API key from [OpenAI Platform](https://platform.openai.com/)
    *   **Google Gemini:** Get your API key from [Google AI Studio](https://aistudio.google.com/)


## Running the Application

1.  **Activate the Virtual Environment:**
    UV will create a `.venv` folder in your project.
    ```bash
    source .venv/bin/activate  # On Linux/macOS
    .venv\Scripts\activate  # On Windows
    ```

2.  **Run the Streamlit App:**

    ```bash
    streamlit run app.py
    ```

3.  **Access the App:**

    Open your web browser and go to the URL provided in the terminal (usually `http://localhost:8501`).

## Usage

### Chatbot Tab

1.  **Ask Questions:** In the "Chatbot" tab, type your questions about the database in natural language (e.g., "List all employees," "What are the top-selling products?").
2.  **View Results:** The chatbot will respond with a natural language summary of the data.

### Dashboard Tab

1.  **Generate Dashboard:** In the "Dashboard" tab, click the "Generate Dashboard" button.
2.  **View Dashboard:** The app will analyze the database schema and generate an interactive HTML dashboard with charts and tables.

## Key Components

*   **`agent.py`:**
    *   Defines the `db_connection_agent` which is responsible for understanding user queries and generating SQL.
    *   Uses the `get_schema` and `read_query` tools from the MCP toolkit.
    *   Returns a natural language summary of the query results.
*   **`dashboard_agent.py`:**
    *   Defines the `run_agent` function, which orchestrates the dashboard generation process.
    *   Uses the `analyze_database` function to analyze the database schema and identify key metrics.
    *   Uses the `get_data_from_database` function to fetch data for the identified metrics.
    *   Uses the `generate_html_dashboard` function to create the HTML dashboard.
    *   Includes retry logic and JSON validation.
*   **`app.py`:**
    *   The main Streamlit application.
    *   Provides the user interface for the chatbot and dashboard.
    *   Uses `st.session_state` to persist chat messages.
    *   Uses `st.container` and JavaScript to keep the chat at the top of the screen.
    *   Uses `st.tabs` to create the "Chatbot" and "Dashboard" tabs.

## Contributing

Contributions are welcome! Please feel free to open issues or submit pull requests.

## License

MIT
