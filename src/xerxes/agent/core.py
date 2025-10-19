import json
import logging
import os
import sys
import warnings
from contextlib import contextmanager

from rich.console import Console
from rich.markdown import Markdown
from rich.spinner import Spinner

from ..config.settings import get_settings
from ..executor.command import CommandExecutor
from ..llm.vertex import VertexAIProvider
from ..tools.registry import get_registry
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

        with suppress_stderr():
            self.llm = VertexAIProvider(
                project_id=self.settings.vertex_project_id,
                location=self.settings.vertex_location,
                model_name=self.settings.vertex_model,
                credentials_path=self.settings.google_application_credentials,
            )

        self._initialize_session()

    def _initialize_session(self) -> None:
        available_tools = [tool.name for tool in self.registry.get_available_tools()]
        system_prompt = get_system_prompt(available_tools)
        self.session.add_system_message(system_prompt)

    def chat(self, user_message: str) -> str:
        self.session.add_message("user", user_message)

        max_iterations = 10
        iteration = 0
        total_commands_executed = 0

        while iteration < max_iterations:
            iteration += 1

            tools = self.registry.get_function_schemas()

            with console.status("[cyan]Thinking...", spinner="dots") as status:
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

                if num_commands == 1:
                    total_commands_executed += 1
                    console.print(
                        f"[bold magenta]Step {iteration} - Command #{total_commands_executed}[/bold magenta]"
                    )
                    result = self.executor.execute_tool_call(
                        response.tool_calls[0].name, response.tool_calls[0].arguments
                    )
                    tool_results.append(
                        {
                            "tool_call_id": response.tool_calls[0].id,
                            "function_name": response.tool_calls[0].name,
                            "result": result,
                        }
                    )
                else:
                    console.print(
                        f"[bold magenta]Step {iteration} - Executing {num_commands} commands in parallel[/bold magenta]"
                    )
                    for idx, tool_call in enumerate(response.tool_calls, 1):
                        total_commands_executed += 1
                        console.print(f"  [cyan]└─ Command {idx}/{num_commands} (#{total_commands_executed})[/cyan]")

                        result = self.executor.execute_tool_call(
                            tool_call.name, tool_call.arguments
                        )

                        tool_results.append(
                            {
                                "tool_call_id": tool_call.id,
                                "function_name": tool_call.name,
                                "result": result,
                            }
                        )

                tool_results_message = json.dumps(tool_results, indent=2)
                self.session.add_message("user", f"Tool results:\n{tool_results_message}")

            elif response.content:
                self.session.add_message("assistant", response.content)
                return response.content

            else:
                break

        return "I've completed the task or reached the maximum number of iterations."

    def run_interactive(self) -> None:
        console.print("[bold cyan]Xerxes DevOps Agent[/bold cyan]")
        console.print("Type your requests or 'exit' to quit\n")

        if not self.llm.is_available():
            console.print(
                "[red]Error: Vertex AI not properly configured. "
                "Please set vertex_project_id and ensure authentication is set up.[/red]"
            )
            return

        available_tools = self.registry.get_available_tools()
        if not available_tools:
            console.print(
                "[yellow]Warning: No DevOps tools detected. "
                "Install aws, gcloud, kubectl, or docker to use their functions.[/yellow]\n"
            )
        else:
            tool_names = ", ".join(tool.name for tool in available_tools)
            console.print(f"[green]Available tools: {tool_names}[/green]\n")

        while True:
            try:
                user_input = console.input("[bold blue]You:[/bold blue] ")

                if not user_input.strip():
                    continue

                if user_input.lower() in ("exit", "quit", "q"):
                    console.print("\n[cyan]Goodbye![/cyan]")
                    break

                console.print()

                response = self.chat(user_input)

                console.print("[bold green]Xerxes:[/bold green]")
                console.print(Markdown(response))
                console.print()

            except KeyboardInterrupt:
                console.print("\n\n[cyan]Goodbye![/cyan]")
                break
            except Exception as e:
                console.print(f"\n[red]Error: {str(e)}[/red]\n")
