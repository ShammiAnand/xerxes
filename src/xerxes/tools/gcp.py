from typing import Any

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
        return "Google Cloud Platform CLI for managing GCE, GCS, Cloud Run, and other GCP services"

    def get_function_schemas(self) -> list[dict[str, Any]]:
        return [
            {
                "name": "gcloud_compute_instances_list",
                "description": "List Google Compute Engine instances",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "project": {
                            "type": "string",
                            "description": "GCP project ID",
                        },
                        "zone": {
                            "type": "string",
                            "description": "GCP zone (e.g., us-central1-a)",
                        },
                    },
                },
            },
            {
                "name": "gcloud_storage_ls",
                "description": "List Cloud Storage buckets or objects",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "GCS path (gs://bucket/prefix or empty for all buckets)",
                        },
                    },
                },
            },
            {
                "name": "gcloud_run_services_list",
                "description": "List Cloud Run services",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "project": {
                            "type": "string",
                            "description": "GCP project ID",
                        },
                        "region": {
                            "type": "string",
                            "description": "GCP region",
                        },
                    },
                },
            },
            {
                "name": "gcloud_logging_read",
                "description": "Read Cloud Logging logs",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "filter": {
                            "type": "string",
                            "description": "Log filter query",
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Number of log entries to return",
                        },
                        "project": {
                            "type": "string",
                            "description": "GCP project ID",
                        },
                    },
                },
            },
            {
                "name": "gcloud_compute_instances_delete",
                "description": "Delete a Compute Engine instance (DESTRUCTIVE)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "instance_name": {
                            "type": "string",
                            "description": "Instance name",
                        },
                        "zone": {
                            "type": "string",
                            "description": "GCP zone",
                        },
                        "project": {
                            "type": "string",
                            "description": "GCP project ID",
                        },
                    },
                    "required": ["instance_name", "zone"],
                },
            },
        ]

    def is_destructive(self, function_name: str, arguments: dict[str, Any]) -> bool:
        destructive_keywords = ["delete", "remove", "destroy", "terminate"]
        return any(keyword in function_name.lower() for keyword in destructive_keywords)

    def execute_function(self, function_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        if function_name == "gcloud_compute_instances_list":
            return self._gcloud_compute_instances_list(**arguments)
        elif function_name == "gcloud_storage_ls":
            return self._gcloud_storage_ls(**arguments)
        elif function_name == "gcloud_run_services_list":
            return self._gcloud_run_services_list(**arguments)
        elif function_name == "gcloud_logging_read":
            return self._gcloud_logging_read(**arguments)
        elif function_name == "gcloud_compute_instances_delete":
            return self._gcloud_compute_instances_delete(**arguments)
        else:
            return {"success": False, "error": f"Unknown function: {function_name}"}

    def _gcloud_compute_instances_list(
        self, project: str | None = None, zone: str | None = None
    ) -> dict[str, Any]:
        cmd = ["gcloud", "compute", "instances", "list"]
        if project:
            cmd.extend(["--project", project])
        if zone:
            cmd.extend(["--zones", zone])
        cmd.extend(["--format", "json"])
        return self.execute_command(cmd)

    def _gcloud_storage_ls(self, path: str | None = None) -> dict[str, Any]:
        cmd = ["gcloud", "storage", "ls"]
        if path:
            cmd.append(path)
        return self.execute_command(cmd)

    def _gcloud_run_services_list(
        self, project: str | None = None, region: str | None = None
    ) -> dict[str, Any]:
        cmd = ["gcloud", "run", "services", "list"]
        if project:
            cmd.extend(["--project", project])
        if region:
            cmd.extend(["--region", region])
        cmd.extend(["--format", "json"])
        return self.execute_command(cmd)

    def _gcloud_logging_read(
        self, filter: str | None = None, limit: int | None = None, project: str | None = None
    ) -> dict[str, Any]:
        cmd = ["gcloud", "logging", "read"]
        if filter:
            cmd.append(filter)
        if limit:
            cmd.extend(["--limit", str(limit)])
        if project:
            cmd.extend(["--project", project])
        cmd.extend(["--format", "json"])
        return self.execute_command(cmd)

    def _gcloud_compute_instances_delete(
        self, instance_name: str, zone: str, project: str | None = None
    ) -> dict[str, Any]:
        cmd = ["gcloud", "compute", "instances", "delete", instance_name, "--zone", zone, "--quiet"]
        if project:
            cmd.extend(["--project", project])
        return self.execute_command(cmd)
