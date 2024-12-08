from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import json


app = FastAPI()


class ChatRequest(BaseModel):
    message: str


@app.get("/")
def root_route():
    return {"this is": "root"}


@app.post("/chat")
def chat_w_llm(chat_request: ChatRequest):
    ollama_url = "http://localhost:11434/api/generate"

    payload = {
        "model": "qwen:0.5b",
        "prompt": chat_request.message,
    }

    try:
        response = requests.post(ollama_url, json=payload, stream=True)
        response.raise_for_status()

        # Accumulate the response tokens
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
        print(f"Error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error: {str(e)}"
        )
