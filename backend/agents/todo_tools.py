import datetime
from sqlalchemy import create_engine, Column, Integer, String, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

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
    session = None
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
    session = None
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
