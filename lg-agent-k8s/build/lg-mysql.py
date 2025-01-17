#!/usr/bin/python3


# Setup logging to new/overwritten logfile with loglevel
import logging
from pathlib import Path

Path("./logs").mkdir(parents=True, exist_ok=True)
logfile = f"./logs/langgraph.log"
logfmode = 'w'                # w = overwrite, a = append
# Log levels: NOTSET DEBUG INFO WARN ERROR CRITICAL
loglevel = logging.DEBUG
# Cuidado! DEBUG will leak secrets!
logging.basicConfig(filename=logfile, encoding='utf-8', level=loglevel, filemode=logfmode)


# Instantiate connection to hosted LLM
import os, sys
def _check_env(var: str):
    if not os.environ.get(var):
        print(f"Required env var {var} is not set.")
        sys.exit(-1)
_check_env("OPENAI_API_KEY")

from langchain_openai import ChatOpenAI
llm = ChatOpenAI()
'''
from langchain_mistralai import ChatMistralAI
llm = ChatMistralAI(
    model="mistral-large-latest",
    temperature=0,
    max_retries=2,
    # other params...
)
'''

#########################################
# Create search tool
_check_env("TAVILY_API_KEY")

from langchain_community.tools.tavily_search import TavilySearchResults

searchtool = TavilySearchResults(max_results=2)

#########################################
# Create DB object with secrets from Conjur

#----------------------------------------
# Function to get JWT for authentication
import json
import requests

# function to get JWT from IDP given only a workload ID as parameter
def jwtProvider_jwtThis(workload_id: str) -> str:
    logging.info("IDP is K8s cluster.")
    with open('/run/secrets/kubernetes.io/serviceaccount/token', 'r') as file:
      jwt = file.read()
    logging.debug(f"JWT: {jwt}")
    return jwt

#----------------------------------------
# Get secrets from Conjur
from conjurjwt import ConjurRetrieverJwt

conjur_subdomain= "cybr-secrets"
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

#----------------------------------------
# Create SQLDatabase object
from langchain_community.utilities.sql_database import SQLDatabase
address='10.96.200.217'  # cluster ip
port=3306                 # MySQL port
database='petclinic'
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

# Bind together the LLM, database, and prompt template to create a SQL agent
mysql_agent = create_sql_agent(
    llm=llm,
    db=db,
    prompt=full_prompt,
    agent_type="tool-calling",
    agent_executor_kwargs={'handle_parsing_errors': True},
    max_iterations=5,
    verbose=True
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

#########################################
# add tools to tool list
# https://langchain-ai.github.io/langgraph/reference/prebuilt
from langgraph.prebuilt import ToolNode, tools_condition

tools = [searchtool, sql_tool]
tool_node = ToolNode(tools=tools)

#########################################
# Build graph

# Create object for holding State and create StateGraph object
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

class State(TypedDict):
    # Messages have the type "list". The `add_messages` function
    # in the annotation defines how this state key should be updated
    # (in this case, it appends messages to the list, rather than overwriting them)
    messages: Annotated[list, add_messages]

graph_builder = StateGraph(State)

graph_builder.add_node("tools", tool_node)
logging.debug(f"tool_node: {tool_node}")

# Tell the LLM which tools it can call
llm_with_tools = llm.bind_tools(tools)

#########################################
# create chatbot node
def chatbot(state: State):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}

# The first argument is the unique node name
# The second argument is the function or object that will be called whenever
# the node is used.
graph_builder.add_node("chatbot", chatbot)

# The `tools_condition` function returns "tools" if the chatbot asks to use a tool, and "END" if
# it is fine directly responding. This conditional routing defines the main agent loop.
graph_builder.add_conditional_edges(
    "chatbot",
    tools_condition,
    # The following dictionary lets you tell the graph to interpret the condition's outputs as a specific node
    # It defaults to the identity function, but if you
    # want to use a node named something else apart from "tools",
    # You can update the value of the dictionary to something else
    # e.g., "tools": "my_tools"
    {"tools": "tools", END: END},
)

# Any time a tool is called, we return to the chatbot to decide the next step
graph_builder.add_edge("tools", "chatbot")
graph_builder.add_edge(START, "chatbot")
graph = graph_builder.compile()

'''
from langgraph.checkpoint.memory import MemorySaver
memory = MemorySaver()
graph = graph_builder.compile(checkpointer=memory)
config = {"configurable": {"thread_id": "1"}}
'''

###############################################
# Run chatbot

def stream_graph_updates(user_input: str):
    for event in graph.stream({"messages": [("user", user_input)]}):
        logging.debug(f"event: {event}")
        for value in event.values():
            print("Assistant:", value["messages"][-1].content)

while True:
    try:
        user_input = input("User: ")
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break

        stream_graph_updates(user_input)
    except:
        print("I am flummoxed.")
        break
