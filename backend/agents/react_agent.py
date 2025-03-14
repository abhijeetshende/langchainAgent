# agents/react_agent.py
from dotenv import load_dotenv
from langchain import hub
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.tools import Tool

from langchain_openai import ChatOpenAI



# Load environment variables from .env file
load_dotenv()

# Define a very simple tool function that returns the current time
def get_current_time(*args, **kwargs):
    """Returns the current time in H:MM AM/PM format."""
    import datetime
    now = datetime.datetime.now()
    return now.strftime("%I:%M %p")

# List of tools available to the agent
tools = [
    Tool(
        name="Time",
        func=get_current_time,
        description="Useful for when you need to know the current time",
    ),
]

# Pull the prompt template from the hub (ReAct: Reason and Action)
prompt = hub.pull("hwchase17/react")

# Initialize a ChatOpenAI model
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)


# Create the ReAct agent
agent = create_react_agent(
    llm=llm,
    tools=tools,
    prompt=prompt,
    stop_sequence=True,
)

# Create an agent executor from the agent and tools
agent_executor = AgentExecutor.from_agent_and_tools(
    agent=agent,
    tools=tools,
    verbose=True,
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
