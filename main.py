from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, validator
from typing import List, Optional, Dict, Any
import requests
import json
from fastapi.responses import StreamingResponse

app = FastAPI()


class ChatRequest(BaseModel):
    message: str
    conversation_history: List[Dict[str, str]] = []
    system_prompt: Optional[str] = None
    role: Optional[str] = None
    model: str = "qwen:1.8b"
    model_parameters: Optional[Dict[str, Any]] = None

    @validator('model')
    def validate_model(cls, v):
        valid_models = ["qwen:0.5b", "qwen:1.8b", "gemma2:2b"]
        if v not in valid_models:
            raise ValueError(
                f"Model {v} not supported. Available models: {valid_models}")
        return v


@app.post("/chat")
async def chat_w_llm(chat_request: ChatRequest):
    ollama_url = "http://localhost:11434/api/generate"

    # Build the prompt based on available context
    prompt = ""
    if chat_request.system_prompt:
        prompt += f"System: {chat_request.system_prompt}\n\n"

    # TODO: might want to improve this
    if chat_request.role:
        prompt += f"You are acting as: {chat_request.role}\n\n"

    # Add conversation history
    for msg in chat_request.conversation_history:
        prompt += f"{msg['role']}: {msg['content']}\n"

    # Add current message
    prompt += f"\nUser: {chat_request.message}\n"

    payload = {
        "model": chat_request.model,
        "prompt": prompt,
        "stream": True  # Enable streaming
    }

    if chat_request.model_parameters:
        payload.update(chat_request.model_parameters)

    try:
        response = requests.post(ollama_url, json=payload, stream=True)
        response.raise_for_status()

        async def generate():
            for line in response.iter_lines():
                if line:
                    json_response = json.loads(line.decode())
                    if "response" in json_response:
                        yield json_response["response"]

        return StreamingResponse(generate(), media_type="text/event-stream")

    except requests.exceptions.ConnectionError:
        raise HTTPException(
            status_code=503, detail="Ollama server is not accessible")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
