from sdk.client import HiClient

# new client
client = HiClient()

print("Available models:", client.model_manager.list_available_models())

client.load_model("gemma2:2b", temperature=0.5)

client.set_system_prompt(
    "create a python program for linear regression in a machine learning context")


def on_token(token):
    print(token, end="", flush=False)


client.register_callback("on_token", on_token)

response = client.chat("Tell me a short joke")

print("Model:", response)
