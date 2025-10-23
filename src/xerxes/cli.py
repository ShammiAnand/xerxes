import os
import sys

os.environ["GRPC_VERBOSITY"] = "ERROR"
os.environ["GRPC_TRACE"] = ""
os.environ["GLOG_minloglevel"] = "3"

stderr_fileno = sys.stderr.fileno()
old_stderr = os.dup(stderr_fileno)
devnull = os.open(os.devnull, os.O_WRONLY)
os.dup2(devnull, stderr_fileno)

import typer
from rich.console import Console
from rich.table import Table

os.dup2(old_stderr, stderr_fileno)
os.close(devnull)
os.close(old_stderr)

from .agent.core import Agent
from .config.settings import get_settings
from .tools.registry import register_tool
from .tools.shell import ShellTool

app = typer.Typer(help="Xerxes: CLI Agent")
console = Console()


def init_tools():
    register_tool(ShellTool())


@app.command()
def chat():
    """Start an interactive chat session with the DevOps agent"""
    init_tools()
    agent = Agent()
    agent.run_interactive()


@app.command()
def config(
    action: str = typer.Argument(..., help="Action: set, show"),
    key: str = typer.Argument(None, help="Config key"),
    value: str = typer.Argument(None, help="Config value"),
):
    """Manage configuration settings"""
    settings = get_settings()

    if action == "show":
        console.print("\n[bold cyan]Current Configuration:[/bold cyan]\n")
        config_data = settings.model_dump(exclude_none=True)

        for k, v in config_data.items():
            console.print(f"[green]{k}:[/green] {v}")

        console.print()

    elif action == "set":
        if not key or not value:
            console.print("[red]Error: Both key and value required for 'set'[/red]")
            raise typer.Exit(1)

        try:
            settings.update_setting(key, value)
            console.print(f"[green]Set {key} = {value}[/green]")
        except ValueError as e:
            console.print(f"[red]Error: {e}[/red]")
            raise typer.Exit(1)

    else:
        console.print(f"[red]Unknown action: {action}[/red]")
        console.print("Available actions: show, set")
        raise typer.Exit(1)


@app.command()
def tools():
    """Check availability of common CLI tools in current shell"""
    import shutil

    common_tools = [
        "kubectl", "docker", "aws", "gcloud", "helm",
        "jq", "grep", "curl", "wget", "sed", "awk",
        "find", "netstat", "kill", "ps", "top", "git", "psql"
    ]

    table = Table(title="CLI Tools Availability")
    table.add_column("Tool", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Path", style="yellow")

    for tool_name in sorted(common_tools):
        tool_path = shutil.which(tool_name)
        if tool_path:
            table.add_row(tool_name, "[green]Available[/green]", tool_path)
        else:
            table.add_row(tool_name, "[red]Not Found[/red]", "-")

    console.print(table)


@app.command()
def version():
    """Show version information"""
    console.print("[cyan]Xerxes Agent[/cyan]")
    console.print("Version: 0.1.0")


if __name__ == "__main__":
    app()
