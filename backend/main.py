# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from fastapi.middleware.cors import CORSMiddleware

from agents.react_agent import run_agent  # Your LangChain agent function

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Adjust as needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]

@app.post("/chat")
def chat_endpoint(request: ChatRequest):
    if not request.messages or len(request.messages) == 0:
        raise HTTPException(status_code=422, detail="No messages provided")
    
    # Use the content of the last message as the input
    input_text = request.messages[-1].content
    
    # Process the input using your LangChain agent
    response_text = run_agent(input_text)
    
    return {"response": response_text}
