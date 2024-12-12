import requests
from typing import List, Optional, Dict, Callable, Any
import time
import threading
import json
from .exceptions import (
    SDKException,
    ModelNotFoundError,
    InvalidConfigError,
    ConnectionError,
    StreamingError,
    CallbackError
)
from .utils import SDKLogger, Metrics

"""
two main classes: conversation, client
"""

# defaults to qwen:1.8b
# TODO: Parse model name and parameters from config file or something like that


class ModelConfig:
    AVAILABLE_MODELS = ["qwen:0.5b", "qwen:1.8b", "gemma2:2b"]

    def __init__(self, model_name: str = "qwen:1.8b", **kwargs):
        if model_name not in self.AVAILABLE_MODELS:
            error_msg = f"Model '{model_name}' not found. Available models:\n" + \
                "\n".join(f"  • {model}" for model in self.AVAILABLE_MODELS)
            raise ModelNotFoundError(error_msg)

        self.model_name = model_name
        self.parameters = kwargs


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
# ! TODO: Add set role
class HiClient:
    def __init__(self, base_url="http://localhost:8000", track_conversation=False):
        self.base_url = base_url
        self.conversation = Conversation()
        self.system_prompt = None
        self.track_conversation = track_conversation
        self._continuous_chat = False
        self._callbacks = {}
        self.model_manager = ModelManager()
        self.logger = SDKLogger()
        self.metrics = Metrics()

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
            if not message.strip():
                raise InvalidConfigError("Message cannot be empty")

            payload = {
                "message": message,
                "conversation_history": self.conversation.get_history() if self.track_conversation else []
            }

            if self.system_prompt:
                payload["system_prompt"] = self.system_prompt

            if role:
                payload["role"] = role

            if not self.model_manager.model_config:
                raise InvalidConfigError(
                    "No model loaded. Call load_model() first")

            payload["model"] = self.model_manager.model_config.model_name
            payload["model_parameters"] = self.model_manager.model_config.parameters

            try:
                if 'on_request' in self._callbacks:
                    self._callbacks['on_request'](message)
            except Exception as e:
                raise CallbackError(f"Error in on_request callback: {str(e)}")

            try:
                response = requests.post(
                    f"{self.base_url}/chat",
                    json=payload,
                    stream=True
                )
                response.raise_for_status()
            except requests.exceptions.ConnectionError:
                raise ConnectionError(
                    f"Failed to connect to server at {self.base_url}")
            except requests.exceptions.HTTPError as e:
                raise ConnectionError(f"HTTP error occurred: {str(e)}")

            full_response = ""
            try:
                for chunk in response.iter_lines():
                    if chunk:
                        chunk_content = chunk.decode()
                        full_response += chunk_content

                        if 'on_token' in self._callbacks:
                            try:
                                self._callbacks['on_token'](chunk_content)
                            except Exception as e:
                                raise CallbackError(
                                    f"Error in on_token callback: {str(e)}")
            except Exception as e:
                raise StreamingError(
                    f"Error while streaming response: {str(e)}")

            if self.track_conversation:
                self.conversation.add_message("user", message)
                self.conversation.add_message("assistant", full_response)

            if 'on_response' in self._callbacks:
                try:
                    self._callbacks['on_response'](full_response)
                except Exception as e:
                    raise CallbackError(
                        f"Error in on_response callback: {str(e)}")

            latency = self.metrics.end_request()
            token_count = len(full_response.split())
            self.metrics.record_tokens(token_count)
            self.logger.info(
                f"Request completed in {latency:.2f}s with {token_count} tokens")

            return full_response

        except SDKException as e:
            if 'on_error' in self._callbacks:
                try:
                    self._callbacks['on_error'](str(e))
                except Exception as callback_error:
                    print(f"Error in error callback: {str(callback_error)}")
            raise

    def clear_conversation(self):
        self.conversation = Conversation()
