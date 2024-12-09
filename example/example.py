from sdk.client import HiClient

client = HiClient(track_conversation=False)

client.set_system_prompt(
    "please behave like a dog and only answer with barking to this:")

response = client.chat("Hello, how are you?", role="dog")


print(f"Dog: {response}")
