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
        return "Manage Docker containers and images - ps, inspect, logs, start, stop, rm, build, run, and more"
