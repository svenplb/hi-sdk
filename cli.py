import requests
import sys


def chat_with_llm():
    print("\n� PlamAI is ready! (Type 'exit' to quit)\n")

    while True:
        # Get user input with a prompt
        user_input = input("🧑 user: ").strip()

        # Check for exit command
        if user_input.lower() in ['exit', 'quit']:
            print("\n👋 Goodbye!")
            sys.exit(0)

        # Skip empty inputs
        if not user_input:
            continue

        try:
            # Make request to your FastAPI endpoint
            response = requests.post(
                "http://localhost:8000/chat",
                json={"message": user_input}
            )
            response.raise_for_status()

            # Print the AI response
            ai_response = response.json()["response"]
            print("\n🤖 AI:", ai_response.strip(), "\n")

        except Exception as e:
            print("\n❌ Error:", str(e), "\n")


if __name__ == "__main__":
    chat_with_llm()
