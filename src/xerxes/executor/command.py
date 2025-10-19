from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

from ..config.settings import get_settings
from ..tools.registry import get_registry
from .safety import is_command_destructive

console = Console()


class CommandExecutor:
    def __init__(self):
        self.registry = get_registry()
        self.settings = get_settings()

    def execute_tool_call(self, function_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        try:
            is_destructive = self.registry.is_destructive(function_name, arguments)

            if is_destructive and self.settings.confirm_destructive:
                if not self._confirm_execution(function_name, arguments):
                    return {
                        "success": False,
                        "error": "Operation cancelled by user",
                        "cancelled": True,
                    }

            console.print(f"[cyan]Executing:[/cyan] {function_name}")

            result = self.registry.execute_function(function_name, arguments)

            if result.get("success"):
                if result.get("stdout"):
                    console.print(Panel(result["stdout"], title="Output", border_style="green"))
            else:
                if result.get("stderr"):
                    console.print(
                        Panel(result["stderr"], title="Error", border_style="red")
                    )

            return result

        except Exception as e:
            error_msg = f"Error executing {function_name}: {str(e)}"
            console.print(f"[red]{error_msg}[/red]")
            return {"success": False, "error": error_msg}

    def _confirm_execution(self, function_name: str, arguments: dict[str, Any]) -> bool:
        console.print("\n[yellow]⚠️  Destructive Operation Detected[/yellow]")
        console.print(f"[bold]Function:[/bold] {function_name}")
        console.print(f"[bold]Arguments:[/bold]")

        args_str = "\n".join(f"  {k}: {v}" for k, v in arguments.items())
        console.print(args_str)

        response = console.input("\n[yellow]Confirm execution? [y/N]:[/yellow] ")
        return response.lower() in ("y", "yes")
