from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

from ..config.settings import get_settings
from ..tools.registry import get_registry
from .safety import is_command_destructive

console = Console()


class CommandExecutor:
    def __init__(self, auto_approve_session: bool = False):
        self.registry = get_registry()
        self.settings = get_settings()
        self.auto_approve_session = auto_approve_session

    def set_auto_approve(self, value: bool):
        self.auto_approve_session = value

    def execute_tool_call(self, function_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        try:
            command = arguments.get("command", "")
            reasoning = arguments.get("reasoning", "")

            tool_name = function_name.replace("_execute", "")
            cli_command = self._get_cli_command(tool_name)
            full_command = f"{cli_command} {command}" if cli_command else command

            is_destructive = self.registry.is_destructive(function_name, arguments)

            if not self.auto_approve_session:
                approval = self._show_command_preview(
                    full_command, reasoning, is_destructive
                )

                if approval == "skip":
                    return {
                        "success": False,
                        "error": "Command skipped by user",
                        "skipped": True,
                    }
                elif approval == "always":
                    self.auto_approve_session = True
                    console.print("[green]✓ Auto-approve enabled for this session[/green]\n")

            console.print(f"[cyan]Executing:[/cyan] {full_command}\n")

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

    def _get_cli_command(self, tool_name: str) -> str | None:
        tool = self.registry.get_tool(tool_name)
        return tool.cli_command if tool else None

    def _show_command_preview(self, command: str, reasoning: str, is_destructive: bool) -> str:
        console.print()
        if is_destructive:
            console.print("[yellow]⚠️  Destructive Operation[/yellow]")

        console.print(Panel(
            f"[bold cyan]Command:[/bold cyan]\n$ {command}\n\n"
            f"[bold green]Reasoning:[/bold green]\n{reasoning}",
            title="Command Preview",
            border_style="yellow" if is_destructive else "blue"
        ))

        response = console.input(
            "\n[[bold cyan]R[/bold cyan]]un / "
            "[[bold yellow]S[/bold yellow]]kip / "
            "[[bold green]A[/bold green]]lways for session? "
        ).strip().lower()

        if response in ("a", "always"):
            return "always"
        elif response in ("s", "skip", "n", "no"):
            return "skip"
        else:
            return "run"
