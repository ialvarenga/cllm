import os
import sys
import asyncio
import typer
from typing import Optional
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.progress import Progress
from rich.prompt import Prompt

from cllm.utils.config import Config
from cllm.utils.openai_client import OpenAIClient

app = typer.Typer(
    name="cllm",
    help="CLI for interaction with language models like OpenAI GPT.",
    add_completion=False,
)
console = Console()
config = Config()

@app.command()
def ask(
    message: str = typer.Argument(..., help="Message to send to the model"),
    model: str = typer.Option("gpt-3.5-turbo", "--model", "-m", help="Model to be used"),
    temperature: float = typer.Option(0.7, "--temperature", "-t", help="Temperature (0.0 to 1.0)"),
    max_tokens: int = typer.Option(1000, "--max-tokens", help="Maximum number of tokens in the response"),
    markdown: bool = typer.Option(True, "--markdown/--no-markdown", help="Render response as Markdown"),
):
    """Sends a message to the model and displays the response."""
    asyncio.run(_ask_async(message, model, temperature, max_tokens, markdown))

async def _ask_async(message: str, model: str, temperature: float, max_tokens: int, markdown: bool):
    """Asynchronous implementation of the ask command."""
    api_key = config.get_api_key()
    
    if not api_key:
        console.print("[bold red]API key not configured![/bold red]")
        console.print("Configure using the command: [bold]cllm config set-api-key[/bold]")
        sys.exit(1)
    
    with Progress(transient=True) as progress:
        task = progress.add_task("[cyan]Processing request...", total=None)
        
        client = OpenAIClient(api_key)
        response = await client.chat_completion(
            prompt=message,
            model=model,
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        progress.remove_task(task)
    
    text_response = client.extract_text_response(response)
    
    if markdown:
        md = Markdown(text_response)
        console.print(Panel(md, title=f"Response ({model})", border_style="cyan"))
    else:
        console.print(Panel(text_response, title=f"Response ({model})", border_style="cyan"))

@app.command()
def config_cli():
    """Manages CLI configurations."""
    typer.echo("Current configurations:")
    typer.echo(f"API Key configured: {'Yes' if config.get_api_key() else 'No'}")
    typer.echo(f"Default model: {config.get('default_model', 'gpt-3.5-turbo')}")

@app.command(name="set-api-key")
def set_api_key(
    key: Optional[str] = typer.Argument(None, help="OpenAI API key")
):
    """Configures the OpenAI API key."""
    if not key:
        key = Prompt.ask("Enter your OpenAI API key", password=True)
    
    config.set_api_key(key)
    console.print("[bold green]API key successfully configured![/bold green]")

@app.command(name="set-default-model")
def set_default_model(
    model: str = typer.Argument(..., help="Default model to be used")
):
    """Configures the default model."""
    config.set("default_model", model)
    console.print(f"[bold green]Default model set to: {model}[/bold green]")

def main():
    """Main entry point of the application."""
    dotenv_path = os.path.join(os.path.dirname(__file__), "..", ".env")
    if os.path.exists(dotenv_path):
        from dotenv import load_dotenv
        load_dotenv(dotenv_path)
    
    app()

if __name__ == "__main__":
    main()