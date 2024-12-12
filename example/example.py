from sdk.client import HiClient
from sdk.utils import SDKLogger, Metrics

# Initialize logger and metrics
logger = SDKLogger("example")
metrics = Metrics()

# Create client
client = HiClient()
logger.info("Client initialized")

# List available models
models = client.model_manager.list_available_models()
logger.info(f"Available models: {models}")

# Load model and track performance
metrics.start_request()
client.load_model("gemma2:2b", temperature=0.5)
load_time = metrics.end_request()
logger.info(f"Model loaded in {load_time:.2f}s")

# Set system prompt
client.set_system_prompt(
    "create a python program for linear regression in a machine learning context")


def on_token(token):
    print(token, end="", flush=True)
    metrics.record_tokens(1)  # Count each token


client.register_callback("on_token", on_token)

# Start timing the chat request
metrics.start_request()

# Chat and stream response
for token in client.chat("Tell me a short joke"):
    pass  # The callback handles printing and token counting

# Get final metrics
chat_time = metrics.end_request()
final_metrics = metrics.get_metrics()

logger.info(f"Chat completed in {chat_time:.2f}s")
logger.info(f"Performance metrics: {final_metrics}")
