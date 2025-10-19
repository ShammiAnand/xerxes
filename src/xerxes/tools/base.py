import shlex
import shutil
import subprocess
from abc import ABC, abstractmethod
from typing import Any


class BaseTool(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def cli_command(self) -> str:
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        pass

    def is_installed(self) -> bool:
        return shutil.which(self.cli_command) is not None

    def get_function_schemas(self) -> list[dict[str, Any]]:
        return [
            {
                "name": f"{self.name}_execute",
                "description": f"Execute {self.cli_command} commands. {self.description}",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "command": {
                            "type": "string",
                            "description": f"The complete {self.cli_command} command to execute (without the '{self.cli_command}' prefix)",
                        },
                        "reasoning": {
                            "type": "string",
                            "description": "Brief explanation of why you're running this command and what you expect it to do",
                        },
                    },
                    "required": ["command", "reasoning"],
                },
            }
        ]

    def execute_raw_command(self, command: list[str], timeout: int = 30) -> dict[str, Any]:
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False,
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

    def is_destructive(self, command: str) -> bool:
        destructive_keywords = [
            "delete",
            "remove",
            "destroy",
            "terminate",
            "kill",
            "stop",
            "rm",
            "prune",
            "drop",
            "truncate",
            "purge",
        ]
        command_lower = command.lower()
        return any(keyword in command_lower for keyword in destructive_keywords)

    def execute_function(self, function_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        if function_name != f"{self.name}_execute":
            return {"success": False, "error": f"Unknown function: {function_name}"}

        command_str = arguments.get("command", "")

        full_command = f"{self.cli_command} {command_str}"
        command_parts = shlex.split(full_command)

        return self.execute_raw_command(command_parts)

    def get_version(self) -> str | None:
        if not self.is_installed():
            return None

        try:
            # TODO:: for kubectl, instead of `--version` use `version`
            result = subprocess.run(
                [self.cli_command, "--version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            return result.stdout.strip() or result.stderr.strip()
        except Exception:
            return None
