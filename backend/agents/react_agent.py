# agents/react_agent.py
from dotenv import load_dotenv
import os
import datetime
from langchain import hub
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.tools import Tool
from langchain_openai import ChatOpenAI

# Load environment variables from .env file
load_dotenv()

# ----------------------------
# Database Setup for Todos
# ----------------------------
from sqlalchemy import create_engine, Column, Integer, String, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://abhijeet:abhi123@postgres:5432/mydatabase")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Todo(Base):
    __tablename__ = "todos"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    due_date = Column(Date)

Base.metadata.create_all(bind=engine)

# ----------------------------
# Define Tool Functions
# ----------------------------

def get_current_time(*args, **kwargs):
    """Returns the current time in H:MM AM/PM format."""
    now = datetime.datetime.now()
    return now.strftime("%I:%M %p")

def fetch_todos(*args, **kwargs):
    session = SessionLocal()
    try:
        todos = session.query(Todo).all()
        if not todos:
            return "No todos found."
        result = [f"{todo.id}: {todo.title} (due {todo.due_date})" for todo in todos]
        return "\n".join(result)
    finally:
        session.close()

def get_today_todo(*args, **kwargs):
    session = SessionLocal()
    today = datetime.date.today()
    try:
        todos = session.query(Todo).filter(Todo.due_date == today).all()
        if not todos:
            return "No todos for today."
        result = [f"{todo.id}: {todo.title} (due {todo.due_date})" for todo in todos]
        return "\n".join(result)
    finally:
        session.close()

def create_todo(input_str: str, *args, **kwargs):
    """
    Expects input_str to be formatted as: title|description|YYYY-MM-DD
    """
    try:
        parts = input_str.split("|")
        if len(parts) != 3:
            return "Invalid input format. Use: title|description|YYYY-MM-DD"
        title, description, due_date_str = parts
        due_date = datetime.datetime.strptime(due_date_str.strip(), "%Y-%m-%d").date()
        session = SessionLocal()
        todo = Todo(title=title.strip(), description=description.strip(), due_date=due_date)
        session.add(todo)
        session.commit()
        return f"Todo created with id {todo.id}."
    except Exception as e:
        return f"Error creating todo: {str(e)}"
    finally:
        session.close()

def update_todo(input_str: str, *args, **kwargs):
    """
    Expects input_str to be formatted as: id|title|description|YYYY-MM-DD
    """
    session = None  # initialize session to None
    try:
        parts = input_str.split("|")
        if len(parts) != 4:
            return "Invalid input format. Use: id|title|description|YYYY-MM-DD"
        id_str, title, description, due_date_str = parts
        todo_id = int(id_str.strip())
        due_date = datetime.datetime.strptime(due_date_str.strip(), "%Y-%m-%d").date()
        session = SessionLocal()
        todo = session.query(Todo).filter(Todo.id == todo_id).first()
        if not todo:
            return f"Todo with id {todo_id} not found."
        todo.title = title.strip()
        todo.description = description.strip()
        todo.due_date = due_date
        session.commit()
        return f"Todo with id {todo_id} updated."
    except Exception as e:
        return f"Error updating todo: {str(e)}"
    finally:
        if session:
            session.close()

def delete_todo(input_str: str, *args, **kwargs):
    """
    Expects input_str to be the id of the todo to delete.
    """
    session = None  # initialize session to None
    try:
        todo_id = int(input_str.strip())
        session = SessionLocal()
        todo = session.query(Todo).filter(Todo.id == todo_id).first()
        if not todo:
            return f"Todo with id {todo_id} not found."
        session.delete(todo)
        session.commit()
        return f"Todo with id {todo_id} deleted."
    except Exception as e:
        return f"Error deleting todo: {str(e)}"
    finally:
        if session:
            session.close()

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
