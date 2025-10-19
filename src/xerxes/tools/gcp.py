from .base import BaseTool


class GCPTool(BaseTool):
    @property
    def name(self) -> str:
        return "gcp"

    @property
    def cli_command(self) -> str:
        return "gcloud"

    @property
    def description(self) -> str:
        return "Manage Google Cloud Platform - Compute Engine, GKE, Cloud Storage, Cloud Run, IAM, networking, and all GCP services"
