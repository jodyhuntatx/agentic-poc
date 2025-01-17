# Conversational API Agent with LangChain

Welcome to the GitHub repository for a conversational agent that utilizes LangChain to interact with APIs. This Python project demonstrates how to build a conversational agent capable of fetching weather data and summarizing Wikipedia articles, showcasing the integration of the OpenAPI specification within LangChain. 

The `open_agent_API.py` file is to create a conversational chatbot within your local terminal, I recommend using this code for the tutorial. Once you complete that, feel free to take a look at and play around with `API_agent_chatbot.py`, which creates a visual panel chatbot on your local machine.

When reading through this, I recommend attempting to implement these methods without looking at the code provided. If you want more context, please read the related blogpost before attempting to create this agent.

If you have already done this and want more resources, take a look at this deeplearning.ai course: https://www.deeplearning.ai/short-courses/functions-tools-agents-langchain/ 

## Project Setup

### Prerequisites

Before you start, ensure you have the following:
- Python 3.8 or higher installed on your system.
- `pip` for installing Python packages.
- An active OpenAI API key for accessing their models.

### Installation

Follow these steps to get your development environment ready:

1. **Clone the Repository**:
   Obtain a local copy of the code by running:
   ```bash
   git clone https://github.com/techindicium/OpenAPI-Agent-Tutorial.git
   cd conversational-agent-langchain
   ```

2. **Install Dependencies**:
   Install all necessary Python libraries to ensure the agent functions correctly:
   ```bash
   pip install openai requests pydantic wikipedia langchain-community dotenv
   ```

3. **Set Up Environment Variables**:
   Configure essential credentials and settings:
   - Create a `.env` file in the project's root directory.
   - Add your OpenAI API key to this file:
     ```plaintext
     OPENAI_API_KEY='your_openai_api_key_here'
     ```
   - Use the `dotenv` package to load these settings into your application:
     ```python
     from dotenv import load_dotenv
     load_dotenv()
     ```

### Usage

**Run the Agent**:
Start the interactive session where the agent is responsive to your queries about weather and Wikipedia summaries:
```bash
python open_agent_API.py
```
During the session, you can type queries and the agent will respond accordingly. Type 'exit' to terminate the session.

## Project Structure

Here’s a breakdown of the key files and their roles:
- **`open_agent_API.py`**: The main script that initializes and runs the conversational agent.
- **`.env`**: A hidden file that securely stores environment variables like API keys.

## Detailed Implementation

### Defining API Interaction Tools

Tools are specialized functions designed to extend the agent's capabilities by performing API interactions:

1. **Current Temperature Tool**:
   - **Purpose**: Fetches real-time temperature data from the Open-Meteo API based on user-specified geographic coordinates.
   - **Implementation Notes**: Utilizes the `requests` library to make HTTP requests and `pydantic` for input validation.

   ```python
   @tool(args_schema=OpenMeteoInput)
   def get_current_temperature(latitude: float, longitude: float) -> str:
       # Implementation with error handling and data extraction
   ```

2. **Wikipedia Search Tool**:
   - **Purpose**: Provides summaries of the top three Wikipedia articles related to a user's search query.
   - **Implementation Notes**: Leverages the `wikipedia-api` library to search and summarize articles.

   ```python
   @tool
   def search_wikipedia(query: str) -> str:
       # Implementation that handles disambiguation and errors
   ```

### Running the Agent

The agent operates through a chain of modules that manage the conversational flow:
- **Prompt Template**: Structures how messages are processed and presented, using placeholders for dynamic interaction.
- **Memory Management**: Uses `ConversationBufferMemory` to retain context of the conversation, crucial for maintaining a continuous and relevant dialogue.
- **Agent Execution**: `AgentExecutor` oversees the orchestration of input processing, tool invocation, and response generation.

```python
# Initialization and setup of the chat model, prompt templates, and agent chain
# Example functions to handle interaction
```
