import subprocess
from typing import Any

from .base import BaseTool


class ShellTool(BaseTool):
    @property
    def name(self) -> str:
        return "bash"

    @property
    def cli_command(self) -> str:
        return "bash"

    @property
    def description(self) -> str:
        return "Execute bash commands with full shell capabilities including pipes, redirection, and command chaining"

    def is_installed(self) -> bool:
        return True

    def get_function_schemas(self) -> list[dict[str, Any]]:
        return [
            {
                "name": "bash_execute",
                "description": "Execute bash commands. Supports pipes (|), redirection (>, >>), command chaining (&&, ||, ;), and all standard bash features. Any CLI tool available on the system can be used.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "command": {
                            "type": "string",
                            "description": "Complete bash command to execute. Can include pipes, redirection, chaining. Examples: 'kubectl get pods | grep Running', 'docker ps -a && docker images', 'find . -name \"*.py\" | wc -l'",
                        },
                        "reasoning": {
                            "type": "string",
                            "description": "Brief explanation of why running this command",
                        },
                    },
                    "required": ["command", "reasoning"],
                },
            }
        ]

    def execute_raw_command(self, command: list[str], timeout: int = 300) -> dict[str, Any]:
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False,
                executable="/bin/bash",
            )

            return {
                "success": result.returncode == 0,
                "stdout": result.stdout.strip(),
                "stderr": result.stderr.strip(),
                "exit_code": result.returncode,
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "stdout": "",
                "stderr": f"Command timed out after {timeout} seconds",
                "exit_code": -1,
            }
        except Exception as e:
            return {
                "success": False,
                "stdout": "",
                "stderr": str(e),
                "exit_code": -1,
            }

    def execute_function(self, function_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        if function_name != "bash_execute":
            return {"success": False, "error": f"Unknown function: {function_name}"}

        command_str = arguments.get("command", "")
        return self.execute_raw_command(command_str)

    def get_version(self) -> str | None:
        try:
            result = subprocess.run(
                ["bash", "--version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            first_line = result.stdout.split('\n')[0] if result.stdout else ""
            return first_line.strip()
        except Exception:
            return None
