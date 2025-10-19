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

    @abstractmethod
    def get_function_schemas(self) -> list[dict[str, Any]]:
        pass

    def execute_command(self, command: list[str], timeout: int = 30) -> dict[str, Any]:
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

    @abstractmethod
    def is_destructive(self, function_name: str, arguments: dict[str, Any]) -> bool:
        pass

    @abstractmethod
    def execute_function(self, function_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        pass

    def get_version(self) -> str | None:
        if not self.is_installed():
            return None

        try:
            result = subprocess.run(
                [self.cli_command, "--version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            return result.stdout.strip() or result.stderr.strip()
        except Exception:
            return None
