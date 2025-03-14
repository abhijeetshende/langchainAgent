from dotenv import load_dotenv
import sys
import os

import datetime
from langchain import hub
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.tools import Tool
from langchain_openai import ChatOpenAI


sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# Load environment variables
load_dotenv()

# Import tools from the extracted todo module
from .todo_tools import fetch_todos, get_today_todo, create_todo, update_todo, delete_todo

# ----------------------------
# Define General Tools
# ----------------------------

def get_current_time(*args, **kwargs):
    """Returns the current time in H:MM AM/PM format."""
    now = datetime.datetime.now()
    return now.strftime("%I:%M %p")

# ----------------------------
# Define the Tools List
# ----------------------------

tools = [
    Tool(
        name="Time",
        func=get_current_time,
        description="Useful for when you need to know the current time."
    ),
    Tool(
        name="FetchTodos",
        func=fetch_todos,
        description="Fetch all todo items from the database."
    ),
    Tool(
        name="GetTodayTodo",
        func=get_today_todo,
        description="Fetch todo items that are due today."
    ),
    Tool(
        name="CreateTodo",
        func=create_todo,
        description="Create a todo item. Input format: title|description|YYYY-MM-DD"
    ),
    Tool(
        name="UpdateTodo",
        func=update_todo,
        description="Update a todo item. Input format: id|title|description|YYYY-MM-DD"
    ),
    Tool(
        name="DeleteTodo",
        func=delete_todo,
        description="Delete a todo item by id. Input: id"
    ),
]

# ----------------------------
# Setup the Agent
# ----------------------------

prompt = hub.pull("hwchase17/react")
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0, streaming=True)

agent = create_react_agent(
    llm=llm,
    tools=tools,
    prompt=prompt,
    stop_sequence=True,
)

agent_executor = AgentExecutor.from_agent_and_tools(
    agent=agent,
    tools=tools,
    verbose=True,
    handle_parsing_errors=True,
)

def run_agent(input_text: str) -> str:
    """
    Runs the agent with the provided input and returns the response.
    
    Args:
        input_text (str): The input query for the agent.
        
    Returns:
        str: The agent's response.
    """
    response = agent_executor.invoke({"input": input_text})
    return response

# For testing purposes when running this module directly
if __name__ == "__main__":
    test_query = "What time is it?"
    print("Test query:", test_query)
    print("Response:", run_agent(test_query))
