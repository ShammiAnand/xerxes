import platform
import subprocess
from typing import Any

from .base import BaseTool


class ShellTool(BaseTool):
    def __init__(self):
        self.os_type = platform.system()
        self.is_windows = self.os_type == "Windows"
        self.shell_name = "powershell" if self.is_windows else "bash"
        self.shell_executable = "powershell.exe" if self.is_windows else "/bin/bash"
    @property
    def name(self) -> str:
        return "bash"

    @property
    def cli_command(self) -> str:
        return self.shell_name

    @property
    def description(self) -> str:
        if self.is_windows:
            return "Execute PowerShell commands with full shell capabilities including pipelines, cmdlets, and object manipulation"
        return "Execute bash commands with full shell capabilities including pipes, redirection, and command chaining"

    def is_installed(self) -> bool:
        return True

    def get_function_schemas(self) -> list[dict[str, Any]]:
        if self.is_windows:
            description = "Execute PowerShell commands. Supports pipelines (|), cmdlets, object manipulation (Select-Object, Where-Object), and all standard PowerShell features. Any CLI tool or cmdlet available on the system can be used."
            command_desc = "Complete PowerShell command to execute. Can include pipelines, cmdlets, object manipulation. Examples: 'kubectl get pods | Select-String Running', 'docker ps -a', 'Get-ChildItem -Path . -Filter \"*.py\" | Measure-Object'"
        else:
            description = "Execute bash commands. Supports pipes (|), redirection (>, >>), command chaining (&&, ||, ;), and all standard bash features. Any CLI tool available on the system can be used."
            command_desc = "Complete bash command to execute. Can include pipes, redirection, chaining. Examples: 'kubectl get pods | grep Running', 'docker ps -a && docker images', 'find . -name \"*.py\" | wc -l'"

        return [
            {
                "name": "bash_execute",
                "description": description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "command": {
                            "type": "string",
                            "description": command_desc,
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
            if self.is_windows:
                result = subprocess.run(
                    ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", command],
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    check=False,
                )
            else:
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
            if self.is_windows:
                result = subprocess.run(
                    ["powershell.exe", "-NoProfile", "-Command", "$PSVersionTable.PSVersion.ToString()"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
            else:
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
