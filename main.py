from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict
import requests
import json

app = FastAPI()


class ChatRequest(BaseModel):
    message: str
    conversation_history: List[Dict[str, str]] = []
    system_prompt: Optional[str] = None
    role: Optional[str] = None


@app.post("/chat")
def chat_w_llm(chat_request: ChatRequest):
    ollama_url = "http://localhost:11434/api/generate"

    # Build the prompt based on available context
    prompt = ""
    if chat_request.system_prompt:
        prompt += f"System: {chat_request.system_prompt}\n\n"

    if chat_request.role:
        prompt += f"You are acting as: {chat_request.role}\n\n"

    # Add conversation history
    for msg in chat_request.conversation_history:
        prompt += f"{msg['role']}: {msg['content']}\n"

    # Add current message
    prompt += f"\nUser: {chat_request.message}\n"

    payload = {
        "model": "qwen:1.8b",
        "prompt": prompt,
    }

    try:
        response = requests.post(ollama_url, json=payload, stream=True)
        response.raise_for_status()

        full_response = ""
        for line in response.iter_lines():
            if line:
                json_response = json.loads(line.decode())
                if "response" in json_response:
                    full_response += json_response["response"]
                if json_response.get("done", False):
                    break

        return {"response": full_response}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
