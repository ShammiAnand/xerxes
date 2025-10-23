import json
import logging
import os
import sys
import time
import warnings
from contextlib import contextmanager

from rich.console import Console
from rich.markdown import Markdown

from ..config.settings import get_settings
from ..executor.command import CommandExecutor
from ..llm.vertex import VertexAIProvider
from ..tools.registry import get_registry
from ..ui.prompt import create_input_session, get_user_input
from .prompts import get_system_prompt
from .session import ChatSession

warnings.filterwarnings("ignore")
logging.getLogger("absl").setLevel(logging.CRITICAL)
logging.getLogger("google").setLevel(logging.CRITICAL)
os.environ["GRPC_VERBOSITY"] = "NONE"
os.environ["GLOG_minloglevel"] = "3"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"


@contextmanager
def suppress_stderr():
    stderr_fileno = sys.stderr.fileno()
    old_stderr = os.dup(stderr_fileno)
    devnull_fd = os.open(os.devnull, os.O_WRONLY)
    try:
        os.dup2(devnull_fd, stderr_fileno)
        yield
    finally:
        os.dup2(old_stderr, stderr_fileno)
        os.close(devnull_fd)
        os.close(old_stderr)


console = Console()


class Agent:
    def __init__(self):
        self.settings = get_settings()
        self.registry = get_registry()
        self.executor = CommandExecutor()
        self.session = ChatSession()
        self.last_interrupt_time = 0

        with suppress_stderr():
            self.llm = VertexAIProvider(
                project_id=self.settings.vertex_project_id,
                location=self.settings.vertex_location,
                model_name=self.settings.vertex_model,
                credentials_path=self.settings.google_application_credentials,
            )

        self._initialize_session()

    def _initialize_session(self) -> None:
        system_prompt = get_system_prompt()
        self.session.add_system_message(system_prompt)

    def _handle_interrupt(self) -> bool:
        current_time = time.time()
        time_since_last = current_time - self.last_interrupt_time
        self.last_interrupt_time = current_time

        if time_since_last < 2.0:
            return True
        return False

    def chat(self, user_message: str) -> str:
        self.session.add_message("user", user_message)
        tools = self.registry.get_function_schemas()

        max_iterations = 100
        iteration = 0

        try:
            while iteration < max_iterations:
                iteration += 1

                with console.status("[cyan]Thinking... (Ctrl+C to cancel, twice to exit)", spinner="dots"):
                    with suppress_stderr():
                        response = self.llm.chat(
                            messages=self.session.get_messages(),
                            tools=tools if tools else None,
                            max_tokens=self.settings.max_tokens,
                            temperature=self.settings.temperature,
                        )

                if response.tool_calls:
                    tool_results = []
                    num_commands = len(response.tool_calls)
                    any_skipped = False

                    for idx, tool_call in enumerate(response.tool_calls, 1):
                        if num_commands > 1:
                            console.print(f"[cyan]Command {idx}/{num_commands}[/cyan]")

                        result = self.executor.execute_tool_call(
                            tool_call.name, tool_call.arguments
                        )

                        if result.get("skipped"):
                            any_skipped = True
                            break

                        tool_results.append(
                            {
                                "tool_call_id": tool_call.id,
                                "function_name": tool_call.name,
                                "result": result,
                            }
                        )

                    if any_skipped:
                        console.print("[yellow]Command skipped. Returning control to user.[/yellow]\n")
                        return ""

                    tool_results_message = json.dumps(tool_results, indent=2)
                    self.session.add_message("user", f"Tool results:\n{tool_results_message}")

                elif response.content:
                    self.session.add_message("assistant", response.content)
                    return response.content

                else:
                    break

            return "I've completed the task or reached the maximum number of iterations."
        except KeyboardInterrupt:
            console.print("\n[yellow]Execution cancelled. You can now provide additional context.[/yellow]\n")
            return ""

    def run_interactive(self) -> None:
        console.print("Type your requests or 'exit' to quit\n")

        if not self.llm.is_available():
            console.print(
                "[red]Error: Vertex AI not properly configured. "
                "Please set vertex_project_id and ensure authentication is set up.[/red]"
            )
            return

        prompt_session = create_input_session()

        while True:
            try:
                user_input = get_user_input(prompt_session)

                if not user_input.strip():
                    continue

                if user_input.lower() in ("exit", "quit", "q"):
                    console.print("\n[cyan]Goodbye![/cyan]")
                    break

                console.print()

                response = self.chat(user_input)
                console.print(Markdown(response))
                console.print()

            except KeyboardInterrupt:
                should_exit = self._handle_interrupt()
                if should_exit:
                    console.print("\n\n[cyan]Goodbye![/cyan]")
                    break
                else:
                    console.print("\n[yellow]Press Ctrl+C again to exit[/yellow]\n")
                    continue
            except EOFError:
                console.print("\n\n[cyan]Goodbye![/cyan]")
                break
            except Exception as e:
                console.print(f"\n[red]Error: {str(e)}[/red]\n")
