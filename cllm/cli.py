import os
from pathlib import Path
import json
import sys
import asyncio
import typer
from openai import OpenAI
from typing import Optional
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.progress import Progress
from rich.prompt import Prompt

from cllm.utils.config import Config
from cllm.utils.thread_manager import ThreadManager

app = typer.Typer(
    name="cllm",
    help="CLI for interaction with language models like OpenAI GPT.",
    add_completion=False,
)
console = Console()
config = Config()
thread_manager = ThreadManager(config)


@app.command()
def ask(
    message: str = typer.Argument(...),
    model: str = typer.Option("gpt-3.5-turbo", "--model", "-m"),
    temperature: float = typer.Option(0.7, "--temperature", "-t"),
    max_tokens: int = typer.Option(1000, "--max-tokens"),
    markdown: bool = typer.Option(True, "--markdown/--no-markdown"),
    thread_id: Optional[str] = typer.Option(None, "--thread-id", "-th", help="Thread ID to maintain conversation context")
):
    asyncio.run(_ask_async(message, model, temperature, max_tokens, markdown, thread_id))


async def _ask_async(
    message: str,
    model: str,
    temperature: float,
    max_tokens: int,
    markdown: bool,
    thread_id: Optional[str]
) -> None:
    """Asynchronous implementation of the ask command with thread context support."""
    api_key = config.get_api_key()

    if not api_key:
        console.print("[bold red]API key not configured![/bold red]")
        console.print("Configure using the command: [bold]cllm config set-api-key[/bold]")
        sys.exit(1)

    client = OpenAI(api_key=api_key)

    thread_id = thread_id or config.get("default_thread", "default")
    #TODO use sqlite to store the thread history, and use transactions
    history = thread_manager.load_history(thread_id)

    history.append({"role": "user", "content": message})

    with Progress(transient=True) as progress:
        task = progress.add_task("[cyan]Processing request...", total=None)
        
        try:
            completion = client.chat.completions.create(
                model=model,
                messages=history,
                max_tokens=max_tokens,
                temperature=temperature,
            )
            progress.remove_task(task)
            
            reply = completion.choices[0].message.content
            
            history.append({"role": "assistant", "content": reply})
            
            thread_manager.save_history(history, thread_id)
            
            if markdown:
                md = Markdown(reply)
                console.print(Panel(md, title=f"Response ({model}) - Thread: {thread_id}", border_style="cyan"))
            else:
                console.print(Panel(reply, title=f"Response ({model}) - Thread: {thread_id}", border_style="cyan"))
                
        except Exception as e:
            progress.remove_task(task)
            error_message = str(e)
            # TODO be more specif about the errors, and treat them properly
            # Remove the user's message from history since the request failed
            history.pop()
            
            if "does not exist" in error_message and "model" in error_message:
                console.print(f"[bold red]The model `{model}` does not exist or you do not have access to it.[/bold red]")
            else:
                console.print(f"[bold red]Error: {error_message}[/bold red]")


@app.command(name="set-default-thread")
def set_default_thread(thread: str = typer.Argument(..., help="Default thread name")) -> None:
    """Set a default thread for the context managment"""
    config.set("default_thread", thread)
    console.print(f"[bold green]Default thread set to: {thread}[/bold green]")


@app.command(name="clear-thread")
def clear_thread(thread: str = typer.Argument(..., help="Nome da thread a ser limpa")) -> None:
    """Remove o histórico de uma thread específica."""
    thread_file = Path.home() / ".cllm" / "threads" / f"{thread}.json"
    
    if thread_file.exists():
        thread_file.unlink()
        console.print(f"[bold yellow]Thread '{thread}' removida com sucesso.[/bold yellow]")
    else:
        console.print(f"[red]Thread '{thread}' não encontrada.[/red]")


@app.command(name="list-config")
def config_cli() -> None:
    """Manages CLI configurations."""
    typer.echo("Current configurations:")
    typer.echo(f"API Key configured: {'Yes' if config.get_api_key() else 'No'}")
    typer.echo(f"Default model: {config.get('default_model', 'gpt-3.5-turbo')}")
    typer.echo(f"Default thread: {config.get('default_thread', 'default')}")


@app.command(name="list-threads")
def list_threads() -> None:
    """Lista todas as threads salvas localmente."""
    threads = thread_manager.list_threads()
    
    if not threads:
        console.print("[italic]Nenhuma thread encontrada.[/italic]")
        return

    console.print("[bold green]Threads disponíveis:[/bold green]")
    for thread in threads:
        console.print(f"• {thread}")


@app.command(name="set-api-key")
def set_api_key(key: Optional[str] = typer.Argument(None, help="OpenAI API key")) -> None:
    """Configures the OpenAI API key."""
    if not key:
        key = Prompt.ask("Enter your OpenAI API key", password=True)

    config.set_api_key(key)
    console.print("[bold green]API key successfully configured![/bold green]")


@app.command(name="set-default-model")
def set_default_model(model: str = typer.Argument(..., help="Default model to be used")) -> None:
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