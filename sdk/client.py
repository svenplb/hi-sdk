import requests
from typing import List, Optional, Dict


class Conversation:
    def __init__(self):
        self.messages: List[Dict[str, str]] = []

    def add_message(self, role: str, content: str):
        self.messages.append({"role": role, "content": content})

    def get_history(self) -> List[Dict[str, str]]:
        return self.messages


class HiClient:
    def __init__(self, base_url="http://localhost:8000", track_conversation=False):
        self.base_url = base_url
        self.conversation = Conversation()
        self.system_prompt = None
        self.track_conversation = track_conversation

    def set_system_prompt(self, prompt: str):
        self.system_prompt = prompt

    def enable_conversation_tracking(self):
        self.track_conversation = True

    def disable_conversation_tracking(self):
        self.track_conversation = False
        self.clear_conversation()

    def chat(self, message: str, role: Optional[str] = None) -> str:
        try:
            payload = {
                "message": message,
                "conversation_history": self.conversation.get_history() if self.track_conversation else []
            }

            if self.system_prompt:
                payload["system_prompt"] = self.system_prompt

            if role:
                payload["role"] = role

            response = requests.post(
                f"{self.base_url}/chat",
                json=payload
            )
            response.raise_for_status()

            response_content = response.json().get("response", "")

            if self.track_conversation:
                self.conversation.add_message("user", message)
                self.conversation.add_message("assistant", response_content)

            return response_content
        except requests.exceptions.RequestException as e:
            print(f"Error: {str(e)}")
            return None

    def clear_conversation(self):
        self.conversation = Conversation()
