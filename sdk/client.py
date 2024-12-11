import requests
from typing import List, Optional, Dict, Callable, Any
import time
import threading
import json

"""
two main classes: conversation, client
"""

# defaults to qwen:1.8b
# TODO: Parse model name and parameters from config file or something like that


class ModelConfig:
    AVAILABLE_MODELS = ["qwen:0.5b", "qwen:1.8b", "gemma2:2b"]

    def __init__(self, model_name: str = "qwen:1.8b", **kwargs):
        try:
            if model_name not in self.AVAILABLE_MODELS:
                error_msg = f"Invalid Model Selection: '{model_name}'\nAvailable models:\n" + \
                    "\n".join(
                        f"  • {model}" for model in self.AVAILABLE_MODELS)
                raise ValueError(error_msg)
            self.model_name = model_name
            self.parameters = kwargs
        except Exception as e:
            print("\033[91m" + str(e) + "\033[0m")
            raise


class ModelManager:
    def __init__(self):
        self.current_model = None
        self.model_config = None

    def load_model(self, model_name: str, **kwargs):
        self.model_config = ModelConfig(model_name, **kwargs)

    def set_parameters(self, **kwargs):
        if self.model_config:
            self.model_config.parameters.update(kwargs)

    def list_available_models(self):
        return ModelConfig.AVAILABLE_MODELS


class Conversation:
    def __init__(self):
        self.messages: List[Dict[str, str]] = []

    def add_message(self, role: str, content: str):
        self.messages.append({"role": role, "content": content})

    def get_history(self) -> List[Dict[str, str]]:
        return self.messages


# client class, holds the conversation, system prompt, and callbacks
class HiClient:
    def __init__(self, base_url="http://localhost:8000", track_conversation=False):
        self.base_url = base_url
        self.conversation = Conversation()
        self.system_prompt = None
        self.track_conversation = track_conversation
        self._continuous_chat = False
        self._callbacks = {}
        self.model_manager = ModelManager()

    def load_model(self, model_name: str, **kwargs):
        self.model_manager.load_model(model_name, **kwargs)

    def set_model_parameters(self, **kwargs):
        self.model_manager.set_parameters(**kwargs)

    def set_system_prompt(self, prompt: str):
        self.system_prompt = prompt

    # register callbacks for different events (e.g., 'on_response', 'on_error')
    # Benachrichtigungshaken, auf bestimme Ereignisse reagieren
    def register_callback(self, event: str, callback: Callable):
        """Register callbacks for different events (e.g., 'on_response', 'on_error')"""
        self._callbacks[event] = callback

    # continous chat - always listening devices
    def start_continuous_chat(self, interval: float = 1.0):
        self._continuous_chat = True
        threading.Thread(target=self._continuous_chat_loop,
                         args=(interval,), daemon=True).start()

    def stop_continuous_chat(self):
        """Stop continuous chat mode"""
        self._continuous_chat = False

    def _continuous_chat_loop(self, interval: float):
        while self._continuous_chat:
            if 'on_listening' in self._callbacks:
                response = self._callbacks['on_listening']()
                if response:
                    self.chat(response)
            time.sleep(interval)

    # chat function, sends a message to the server and returns the response
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

            if self.model_manager.model_config:
                payload["model"] = self.model_manager.model_config.model_name
                payload["model_parameters"] = self.model_manager.model_config.parameters

            if 'on_request' in self._callbacks:
                self._callbacks['on_request'](message)

            response = requests.post(
                f"{self.base_url}/chat",
                json=payload,
                stream=True
            )
            response.raise_for_status()

            full_response = ""
            for chunk in response.iter_lines():
                if chunk:
                    chunk_content = chunk.decode()
                    full_response += chunk_content

                    if 'on_token' in self._callbacks:
                        self._callbacks['on_token'](chunk_content)

            if self.track_conversation:
                self.conversation.add_message("user", message)
                self.conversation.add_message("assistant", full_response)

            if 'on_response' in self._callbacks:
                self._callbacks['on_response'](full_response)

            return full_response

        except Exception as e:
            error_msg = f"\n\n❌ Error during chat:\n  • {str(e)}\n"
            if 'on_error' in self._callbacks:
                self._callbacks['on_error'](error_msg)
            print("\033[91m" + error_msg + "\033[0m")
            return None

    def clear_conversation(self):
        self.conversation = Conversation()
