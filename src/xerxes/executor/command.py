from typing import Any

from prompt_toolkit import Application
from prompt_toolkit.layout import Layout
from prompt_toolkit.layout.containers import Window
from prompt_toolkit.layout.controls import FormattedTextControl
from rich.console import Console
from rich.panel import Panel

from ..config.settings import get_settings
from ..tools.registry import get_registry
from ..ui.keybindings import create_command_preview_bindings, create_output_expansion_bindings

console = Console()


class CommandExecutor:
    def __init__(self, auto_approve_session: bool = False):
        self.registry = get_registry()
        self.settings = get_settings()
        self.auto_approve_session = auto_approve_session
        self.last_function_name: str | None = None
        self.last_arguments: dict[str, Any] | None = None

    def set_auto_approve(self, value: bool):
        self.auto_approve_session = value

    def execute_tool_call(self, function_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        try:
            if self._is_duplicate_command(function_name, arguments):
                return {
                    "success": False,
                    "error": "This command was just executed. The task is likely already complete. Please verify the state or try a different approach.",
                    "duplicate": True,
                }

            command = arguments.get("command", "")
            reasoning = arguments.get("reasoning", "")

            tool_name = function_name.replace("_execute", "")
            cli_command = self._get_cli_command(tool_name)
            full_command = f"{cli_command} {command}" if cli_command else command

            if not self.auto_approve_session:
                approval = self._show_command_preview(full_command, reasoning)

                if approval == "skip":
                    return {
                        "success": False,
                        "error": "Command skipped by user",
                        "skipped": True,
                    }
                elif approval == "always":
                    self.auto_approve_session = True
                    console.print("[green]Auto-approve enabled for this session[/green]\n")

            console.print(f"[cyan]Executing:[/cyan] {full_command}\n")

            result = self.registry.execute_function(function_name, arguments)

            self.last_function_name = function_name
            self.last_arguments = arguments

            if result.get("success"):
                if result.get("stdout"):
                    self._show_output(result["stdout"], "Output")
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

    def _is_duplicate_command(self, function_name: str, arguments: dict[str, Any]) -> bool:
        if self.last_function_name is None or self.last_arguments is None:
            return False

        return (
            self.last_function_name == function_name
            and self.last_arguments == arguments
        )

    def _get_cli_command(self, tool_name: str) -> str | None:
        tool = self.registry.get_tool(tool_name)
        return tool.cli_command if tool else None

    def _show_output(self, output: str, title: str) -> None:
        lines = output.split('\n')
        total_lines = len(lines)
        output_size_kb = len(output) / 1024

        if total_lines <= 20:
            console.print(Panel(output, title=title, border_style="green"))
        else:
            preview_lines = lines[:10] + [
                "",
                f"[dim]... ({total_lines - 15} lines hidden, {output_size_kb:.1f} KB total) ...[/dim]",
                ""
            ] + lines[-5:]
            preview = '\n'.join(preview_lines)

            console.print(Panel(
                preview,
                title=f"{title} (condensed - {total_lines} lines)",
                border_style="green"
            ))

            console.print("\n[dim]Press [bold cyan]Ctrl+O[/bold cyan] to expand full output, [bold green]Enter[/bold green] to continue[/dim]")

            bindings, state = create_output_expansion_bindings()
            layout = Layout(Window(FormattedTextControl(text="")))
            app = Application(layout=layout, key_bindings=bindings, full_screen=False)

            app.run()

            if state["expand"]:
                console.print(Panel(output, title=f"{title} (full)", border_style="cyan"))

            console.print()

    def _show_command_preview(self, command: str, reasoning: str) -> str:
        console.print()
        console.print(Panel(
            f"[bold cyan]Command:[/bold cyan]\n$ {command}\n\n"
            f"[bold green]Reasoning:[/bold green]\n{reasoning}",
            title="Command Preview",
            border_style="blue"
        ))

        console.print("\n[dim]Press [bold cyan]R[/bold cyan]=Run | [bold yellow]S[/bold yellow]=Skip | [bold green]A[/bold green]=Always[/dim]")

        bindings, state = create_command_preview_bindings()
        layout = Layout(Window(FormattedTextControl(text="")))
        app = Application(layout=layout, key_bindings=bindings, full_screen=False)

        app.run()

        return state["choice"] or "run"
