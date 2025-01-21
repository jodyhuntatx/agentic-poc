import asyncio
from autogen_ext.tools.langchain import LangChainToolAdapter
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.messages import TextMessage
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.ui import Console
from autogen_core import CancellationToken

import logging
from pathlib import Path
Path("./logs").mkdir(parents=True, exist_ok=True)
logfile = f"./logs/langgraph.log"
logfmode = 'w'                # w = overwrite, a = append
# Log levels: NOTSET DEBUG INFO WARN ERROR CRITICAL
loglevel = logging.DEBUG
# Cuidado! DEBUG will leak secrets!
logging.basicConfig(filename=logfile, encoding='utf-8', level=loglevel, filemode=logfmode)

# Check for required env vars
import os
os.environ.get("OPENAI_API_KEY")

#########################################
# Create DB object with secrets from Conjur

# ----------------------------------------
# Function to get JWT for authentication
import json
import requests

# function to get JWT from IDP given only a workload ID as parameter
def jwtProvider_jwtThis(workload_id: str) -> str:
    logging.info("IDP is jwt-this on localhost.")
    jwt_issuer_url = "http://localhost:8000/token"
    urlenc_headers= { "Content-Type": "application/x-www-form-urlencoded" }
    payload = f"workload={workload_id}"
    resp_dict = json.loads(requests.request("POST", jwt_issuer_url,
                           headers=urlenc_headers, data=payload).text)
    jwt = ""
    if resp_dict:
      jwt = resp_dict['access_token']
      logging.info("JWT retrieved successfully.")
      logging.debug(f"JWT: {jwt}")
    else:
      raise RuntimeError(f"Error retrieving JWT. Response: {resp_dict}")
    return jwt

# ----------------------------------------
# Get secrets from Conjur
from conjurjwt import ConjurRetrieverJwt

conjur_subdomain = "cybr-secrets"
authn_jwt_id = "agentic"
workload_id = "ai-agent"
conjurRetriever = ConjurRetrieverJwt(conjur_subdomain, authn_jwt_id, jwtProvider_jwtThis)
username = ""
password = ""
try:
    username = conjurRetriever.getSecret("data/vault/JodyDemo/K8sSecrets-MySQL/username", workload_id)
    password = conjurRetriever.getSecret("data/vault/JodyDemo/K8sSecrets-MySQL/password", workload_id)
except Exception as e:
    logging.error(e)

# ----------------------------------------
# Create SQLDatabase object
from langchain_community.utilities.sql_database import SQLDatabase

address = '192.168.68.108'  # host IP
port = 32203                # Node port
database = 'petclinic'
mysql_uri = f"mysql+mysqlconnector://{username}:{password}@{address}:{port}/{database}"

logging.debug(f"MySQL URI: {mysql_uri}")
db = SQLDatabase.from_uri(mysql_uri)
database_schema = db.get_table_info()
logging.debug(f"{database} schema: {database_schema}")

#########################################
# Create SQL agent to be used by DB tool
from langchain_community.agent_toolkits import create_sql_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# Define the system message for the agent, including instructions and available tables
system_message = f"""You are a MySQL expert agent designed to interact with a MySQL database.
Given an input question, create a syntactically correct MySQL query to run, then look at the results of the query and return the answer.
Unless the user specifies a specific number of examples they wish to obtain, always limit your query to at most 100 results using the LIMIT clause as per MySQL. You can order the results to return the most informative data in the database..
You can order the results by a relevant column to return the most interesting examples in the database.
Never query for all columns from a table. You must query only the columns that are needed to answer the question. Wrap each column name in double quotes (") to denote them as delimited identifiers.
You have access to tools for interacting with the database.
Only use the given tools. Only use the information returned by the tools to construct your final answer.
You MUST double check your query before executing it. If you get an error while executing a query, rewrite the query and try again.

DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the database.

If the question does not seem related to the database, just return "I don't know" as the answer.
Before you execute the query, tell us why you are executing it and what you expect to find briefly.
Only use the following tables:
{database_schema}
"""

# Create a full prompt template for the agent using the system message and placeholders
full_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_message),
        ("human", '{input}'),
        MessagesPlaceholder("agent_scratchpad")
    ]
)

#########################################
# Create SQL tool wrapper that invokes the SQL agent

from langchain_core.tools import tool

@tool
def sql_tool(user_input):
    """
    Executes a SQL query using the sqlite_agent and returns the result.

    Args:
        user_input (str): The SQL query to be executed.

    Returns:
        str: The result of the SQL query execution. If an error occurs, the exception is returned as a string.
    """
    try:
        # Invoke the mysql_agent with the user input (SQL query)
        response = mysql_agent.invoke(user_input)

        # Extract the output from the response
        prediction = response['output']
        logging.debug(f"prediction: {prediction}")
    except Exception as e:
        # If an exception occurs, capture the exception message
        prediction = e

    # Return the result or the exception message
    return prediction

async def main() -> None:
    tool = LangChainToolAdapter(sql_tool)
    # Define an agent
    mysql_agent = AssistantAgent(
        name="assistant",
        model_client=OpenAIChatCompletionClient(
            model="gpt-4o-2024-08-06",
            # api_key="YOUR_API_KEY",
        ),
        tools=[tool],
    )
    while True:
        # Get user input from the console.
        user_input = input("Enter a message (type 'exit' to leave): ")
        if user_input.strip().lower() == "exit":
            break
        # Run the team and stream messages to the console.
        stream = mysql_agent.run_stream(task=user_input)
        await Console(stream)

asyncio.run(main())
