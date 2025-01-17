#!/usr/bin/python3

import json
import sqlite3
import os
import pandas as pd
import logging

from langchain import hub
from langchain_community.llms import LlamaCpp
from langchain_core.callbacks import BaseCallbackHandler, CallbackManager, StreamingStdOutCallbackHandler
from langchain.agents import Tool, AgentExecutor, create_react_agent
from langchain_community.tools import DuckDuckGoSearchRun, yahoo_finance_news
from langchain_experimental.utilities import PythonREPL
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent

MODELS_BASE_PATH='/home/ubuntu/models/'
os.environ['HF_HOME'] = MODELS_BASE_PATH
LLM_MODEL_PATH = MODELS_BASE_PATH + "Llama-3.2-3B-Instruct-Q5_K_L.gguf"

################################################
# Load LLM from disk
def loadLLM():
    logging.info("Loading LLM from disk...")

    # Callbacks support token-wise streaming
    callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])
    max_tokens = 16384
    temp = 0            # stick to the facts
    n_gpu_layers = 32   # layers to move to GPU.
    n_ctx = 8192        # Context window (128k)
    n_batch = 2048      # Should be between 1 and n_ctx, consider the amount of VRAM in your GPU.

    _llm = LlamaCpp(
        model_path=LLM_MODEL_PATH,
        max_tokens=max_tokens,
        temperature=temp,
        n_gpu_layers=n_gpu_layers,
        n_ctx=n_ctx,
        n_batch=n_batch,
        callback_manager=callback_manager,
        verbose=False,  # Verbose is required to pass to the callback manager
    )
    return _llm

llm = loadLLM()

python_repl = PythonREPL()
python_repl.run("print('Hello World! I am a langchain tool that allows running arbitrary Python code')")
python_repl.model_json_schema()
repl_tool = Tool(
    name="python_repl",
    description="A Python shell used to execute python commands. Input should be a valid python command.",
    func=python_repl.run,
)
repl_tool.invoke('print("Hello World!")')


duckduckgo_search = DuckDuckGoSearchRun()
duckduckgo_search.run("Who is the founder of Tesla?")
search_tool = Tool(
    name="duckduckgo_search",
    description="An interface to the DuckDuckGo search engine. Input should be a string.",
    func=duckduckgo_search.run,
)
search_tool.invoke("Who is the founder of Tesla?")

# With this overall framework in place, let us now create a few agents and see how the `langchain` abstractions work in practise.

# Example 1: Math Agent

# Let us now create an agent that is able to think through business math problems using the `PythonREPL` tool that we explored in the previous section.
# 
# In the following outputs notice how the ReAct `thought-action-observation` sequence is executed by the Math Agent we create using the abstractions of `langchain`.

# Since the ReAct agent is a common abstraction, we can use a prompt that is hosted on the `langchain` hub.

react_prompt = hub.pull("hwchase17/react")
print(f"react_prompt:\n.{react_prompt.template}\n\n")

print(react_prompt.template)
react_agent = create_react_agent(
    llm=llm,
    tools=[repl_tool],
    prompt=react_prompt
)
react_agent.get_prompts()

# The agent now needs an executor to parse input and use the ReAct paradigm to plan and execute the objective mentioned in the input. Agent executors were introduced in `langchain` to separate the planning stage and the execution stage of the ReAct paradigm.

react_agent_executor = AgentExecutor(
    agent=react_agent,
    tools=[repl_tool],
    verbose=True
)

user_input = "If $ 450 amounts to $ 630 in 6 years, what will it amount to in 2 years at the same interest rate?"
react_agent_executor.invoke(
    {
        'input': user_input
    }
)


# Example 2: Search Agent

# Let us now create a finance news agent that empowers analysts to search for relevant financial information.
# 
# We will attach two tools to the agent - `DuckDuckGoSearch` & `YahooFinanceNewsTool`.

duckduckgo_search = DuckDuckGoSearchRun()


search_tool = Tool(
    name="duckduckgo_search",
    description="An interface to the DuckDuckGo search engine. Input should be a string.",
    func=duckduckgo_search.run,
)

yahoo_finance_news = yahoo_finance_news.YahooFinanceNewsTool()

finance_news_tool = Tool(
    name="yahoo_finance_news",
    description="An interface to Yahoo finance. Input should contain a valid ticker symbol.",
    func=yahoo_finance_news.run
)

react_agent = create_react_agent(
    llm=llm,
    tools=[search_tool, finance_news_tool],
    prompt=react_prompt
)


react_agent.get_prompts()

react_agent_executor = AgentExecutor(
    agent=react_agent,
    tools=[search_tool, finance_news_tool],
    verbose=True
)

user_input = "What is the latest stock price of AAPL?"

react_agent_executor.invoke(
    {
        'input': user_input
    }
)

user_input = "What was TSLA's quarterly revenue from the latest earnings call?"

react_agent_executor.invoke(
    {
        'input': user_input
    }
)

user_input = "Summarize three key reasons for the steep fall in the Indian stock market on 28th February 2024."

react_agent_executor.invoke(
    {
        'input': user_input
    }
)

user_input=" What was the stock price variation of Netflix  in the last 3 months"

react_agent_executor.invoke(
    {
        'input': user_input
    }
)


# Example 3: SQL Agent

# Let us now create a database agent that translates user queries into valid SQL and executes this against the database. In contrast to the previous exampe, this agent is cutoff from the external world. It is rooted to the database on which it can run queries.

connection = sqlite3.connect("socialmedia.db")

path="/content/drive/MyDrive/GenAI/LLM Science and Engineering/"

users_df = pd.read_csv("/content/likes.csv")
media_df = pd.read_csv("/content/media.csv")
likes_df = pd.read_csv("/content/likes.csv")

users_df.sample(3)


likes_df.sample(3)

users_df.to_sql('users', connection, if_exists='append', index=False)

media_df.to_sql('media', connection, if_exists='append', index=False)

likes_df.to_sql('likes', connection, if_exists='append', index=False)


socialmedia_db = SQLDatabase.from_uri("sqlite:///socialmedia.db")

sqlite_agent = create_sql_agent(
    llm,
    db=socialmedia_db,
    agent_type="openai-tools",
    verbose=True
)

# Since this is a focused agent (i.e., executed only SQL), we do not need an executor to invoke this agent.
sqlite_agent.invoke("How many users have the location as DEL?")


# Let us check if the answer is correct.
sqlite_agent.invoke("How many users have liked more than 3 media items?")

sqlite_agent.invoke(
    "What is the location of the user who has liked most media items?"
    " Who is this user and how many media did this user like?"
)
