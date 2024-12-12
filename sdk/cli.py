import click
from .client import HiClient, ModelConfig
from colorama import init, Fore, Style
import time

init()


@click.group()
def cli():
    """Command line interface for the HiClient SDK"""
    pass


@cli.command()
@click.option('--model', default='gemma2:2b', help='Model to load')
@click.option('--temp', default=0.7, help='Temperature for generation')
@click.option('--system-prompt', help='System prompt to use')
@click.option('--role', help='Role for the assistant')
@click.option('--stream/--no-stream', default=True, help='Enable/disable streaming')
def chat(model: str, temp: float, system_prompt: str, role: str, stream: bool):
    """Start an interactive chat session"""
    client = HiClient()

    try:
        print(f"{Fore.CYAN}Loading model {model}...{Style.RESET_ALL}")
        client.load_model(model, temperature=temp)

        if system_prompt:
            client.set_system_prompt(system_prompt)

        print(f"{Fore.GREEN}Model loaded! Type 'exit' to quit.{Style.RESET_ALL}\n")

        if stream:
            def on_token(token):
                print(token, end="", flush=True)
            client.register_callback("on_token", on_token)

        while True:
            try:
                msg = input(f"{Fore.BLUE}> {Style.RESET_ALL}")
                if msg.lower() == 'exit':
                    break

                if stream:
                    print(f"{Fore.GREEN}Assistant: {Style.RESET_ALL}", end="")
                    for _ in client.chat(msg, role=role):
                        pass  # Tokens are handled by callback
                    print("\n")
                else:
                    response = client.chat(msg, role=role)
                    print(f"{Fore.GREEN}Assistant:{Style.RESET_ALL} {response}\n")

            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except Exception as e:
                print(f"{Fore.RED}Error: {str(e)}{Style.RESET_ALL}")

    except Exception as e:
        print(f"{Fore.RED}Error: {str(e)}{Style.RESET_ALL}")


@cli.command()
def models():
    """List available models"""
    print(f"{Fore.CYAN}Available models:{Style.RESET_ALL}")
    for model in ModelConfig.AVAILABLE_MODELS:
        print(f"  • {model}")


@cli.command()
@click.option('--dev/--no-dev', default=False, help='Install in development mode')
def setup(dev):
    """Setup Hi SDK and all dependencies"""
    import subprocess
    import os
    import sys
    from pathlib import Path

    print(f"{Fore.CYAN}Setting up Hi SDK... Grab a coffee, this will take a while! ☕{Style.RESET_ALL}")

    try:
        # Install Ollama
        print("Installing Ollama...")
        subprocess.run("curl https://ollama.ai/install.sh | sh",
                       shell=True, check=True)

        # Pull models
        print("Downloading models...")
        subprocess.run("ollama pull gemma:2b", shell=True, check=True)

        if dev:
            # Create and activate venv
            subprocess.run("python3 -m venv venv", shell=True, check=True)
            subprocess.run("source venv/bin/activate", shell=True, check=True)

            # Install requirements and package
            print("Installing SDK in development mode...")
            subprocess.run("pip install -r requirements.txt",
                           shell=True, check=True)
            subprocess.run("pip install -e .", shell=True, check=True)

            # Add venv bin to PATH for 'hi' command
            venv_bin = Path("venv/bin").absolute()
            os.environ["PATH"] = f"{venv_bin}:{os.environ['PATH']}"

        # Start services
        print("Starting services...")
        subprocess.Popen("ollama serve", shell=True)
        subprocess.Popen(
            "python3 -m uvicorn main:app --host 0.0.0.0 --port 8000", shell=True)

        print(
            f"{Fore.GREEN}Setup complete! Try 'hi chat' to start chatting{Style.RESET_ALL}")

    except Exception as e:
        print(f"{Fore.RED}Error during setup: {str(e)}{Style.RESET_ALL}")


def main():
    cli()


if __name__ == "__main__":
    main()
