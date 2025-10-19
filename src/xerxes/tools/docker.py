from typing import Any

from .base import BaseTool


class DockerTool(BaseTool):
    @property
    def name(self) -> str:
        return "docker"

    @property
    def cli_command(self) -> str:
        return "docker"

    @property
    def description(self) -> str:
        return "Docker container and image management - list, inspect, start, stop, and remove containers"

    def get_function_schemas(self) -> list[dict[str, Any]]:
        return [
            {
                "name": "docker_ps",
                "description": "List Docker containers",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "all": {
                            "type": "boolean",
                            "description": "Show all containers (default shows just running)",
                        },
                    },
                },
            },
            {
                "name": "docker_images",
                "description": "List Docker images",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "all": {
                            "type": "boolean",
                            "description": "Show all images (including intermediate)",
                        },
                    },
                },
            },
            {
                "name": "docker_inspect",
                "description": "Get detailed information about a container or image",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name_or_id": {
                            "type": "string",
                            "description": "Container or image name/ID",
                        },
                    },
                    "required": ["name_or_id"],
                },
            },
            {
                "name": "docker_logs",
                "description": "Fetch logs from a container",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "container": {
                            "type": "string",
                            "description": "Container name or ID",
                        },
                        "tail": {
                            "type": "integer",
                            "description": "Number of lines to show from the end",
                        },
                        "follow": {
                            "type": "boolean",
                            "description": "Follow log output",
                        },
                    },
                    "required": ["container"],
                },
            },
            {
                "name": "docker_stop",
                "description": "Stop a running container (DESTRUCTIVE)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "container": {
                            "type": "string",
                            "description": "Container name or ID",
                        },
                    },
                    "required": ["container"],
                },
            },
            {
                "name": "docker_start",
                "description": "Start a stopped container",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "container": {
                            "type": "string",
                            "description": "Container name or ID",
                        },
                    },
                    "required": ["container"],
                },
            },
            {
                "name": "docker_rm",
                "description": "Remove a container (DESTRUCTIVE)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "container": {
                            "type": "string",
                            "description": "Container name or ID",
                        },
                        "force": {
                            "type": "boolean",
                            "description": "Force removal of running container",
                        },
                    },
                    "required": ["container"],
                },
            },
        ]

    def is_destructive(self, function_name: str, arguments: dict[str, Any]) -> bool:
        destructive_functions = {"docker_stop", "docker_rm", "docker_rmi", "docker_prune"}
        return function_name in destructive_functions

    def execute_function(self, function_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        if function_name == "docker_ps":
            return self._docker_ps(**arguments)
        elif function_name == "docker_images":
            return self._docker_images(**arguments)
        elif function_name == "docker_inspect":
            return self._docker_inspect(**arguments)
        elif function_name == "docker_logs":
            return self._docker_logs(**arguments)
        elif function_name == "docker_stop":
            return self._docker_stop(**arguments)
        elif function_name == "docker_start":
            return self._docker_start(**arguments)
        elif function_name == "docker_rm":
            return self._docker_rm(**arguments)
        else:
            return {"success": False, "error": f"Unknown function: {function_name}"}

    def _docker_ps(self, all: bool = False) -> dict[str, Any]:
        cmd = ["docker", "ps"]
        if all:
            cmd.append("-a")
        return self.execute_command(cmd)

    def _docker_images(self, all: bool = False) -> dict[str, Any]:
        cmd = ["docker", "images"]
        if all:
            cmd.append("-a")
        return self.execute_command(cmd)

    def _docker_inspect(self, name_or_id: str) -> dict[str, Any]:
        cmd = ["docker", "inspect", name_or_id]
        return self.execute_command(cmd)

    def _docker_logs(
        self, container: str, tail: int | None = None, follow: bool = False
    ) -> dict[str, Any]:
        cmd = ["docker", "logs", container]
        if tail:
            cmd.extend(["--tail", str(tail)])
        if follow:
            cmd.append("-f")
        return self.execute_command(cmd, timeout=60 if follow else 30)

    def _docker_stop(self, container: str) -> dict[str, Any]:
        cmd = ["docker", "stop", container]
        return self.execute_command(cmd)

    def _docker_start(self, container: str) -> dict[str, Any]:
        cmd = ["docker", "start", container]
        return self.execute_command(cmd)

    def _docker_rm(self, container: str, force: bool = False) -> dict[str, Any]:
        cmd = ["docker", "rm", container]
        if force:
            cmd.append("-f")
        return self.execute_command(cmd)
