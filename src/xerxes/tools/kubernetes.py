from .base import BaseTool


class KubernetesTool(BaseTool):
    @property
    def name(self) -> str:
        return "kubernetes"

    @property
    def cli_command(self) -> str:
        return "kubectl"

    @property
    def description(self) -> str:
        return "Manage Kubernetes clusters - get, describe, create, delete pods, deployments, services, logs, and more"
