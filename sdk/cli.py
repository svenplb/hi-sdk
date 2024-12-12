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


def main():
    cli()


if __name__ == "__main__":
    main()
