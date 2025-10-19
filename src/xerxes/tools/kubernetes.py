from typing import Any

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
        return "Kubernetes cluster management - get, describe, logs, and manage pods, deployments, services"

    def get_function_schemas(self) -> list[dict[str, Any]]:
        return [
            {
                "name": "kubectl_get",
                "description": "Get resources (pods, deployments, services, etc.)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "resource_type": {
                            "type": "string",
                            "description": "Resource type (pods, deployments, services, nodes, etc.)",
                        },
                        "namespace": {
                            "type": "string",
                            "description": "Namespace (defaults to 'default')",
                        },
                        "name": {
                            "type": "string",
                            "description": "Specific resource name (optional)",
                        },
                        "all_namespaces": {
                            "type": "boolean",
                            "description": "Get resources from all namespaces",
                        },
                    },
                    "required": ["resource_type"],
                },
            },
            {
                "name": "kubectl_describe",
                "description": "Describe a Kubernetes resource in detail",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "resource_type": {
                            "type": "string",
                            "description": "Resource type (pod, deployment, service, etc.)",
                        },
                        "name": {
                            "type": "string",
                            "description": "Resource name",
                        },
                        "namespace": {
                            "type": "string",
                            "description": "Namespace (defaults to 'default')",
                        },
                    },
                    "required": ["resource_type", "name"],
                },
            },
            {
                "name": "kubectl_logs",
                "description": "Get logs from a pod",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "pod_name": {
                            "type": "string",
                            "description": "Pod name",
                        },
                        "namespace": {
                            "type": "string",
                            "description": "Namespace (defaults to 'default')",
                        },
                        "container": {
                            "type": "string",
                            "description": "Container name (if pod has multiple containers)",
                        },
                        "tail": {
                            "type": "integer",
                            "description": "Number of lines to show from the end of the logs",
                        },
                        "follow": {
                            "type": "boolean",
                            "description": "Follow log output (stream logs)",
                        },
                    },
                    "required": ["pod_name"],
                },
            },
            {
                "name": "kubectl_delete",
                "description": "Delete a Kubernetes resource (DESTRUCTIVE)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "resource_type": {
                            "type": "string",
                            "description": "Resource type (pod, deployment, service, etc.)",
                        },
                        "name": {
                            "type": "string",
                            "description": "Resource name",
                        },
                        "namespace": {
                            "type": "string",
                            "description": "Namespace (defaults to 'default')",
                        },
                    },
                    "required": ["resource_type", "name"],
                },
            },
            {
                "name": "kubectl_apply",
                "description": "Apply a configuration from a file or stdin (DESTRUCTIVE)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "filename": {
                            "type": "string",
                            "description": "Path to YAML/JSON configuration file",
                        },
                        "namespace": {
                            "type": "string",
                            "description": "Namespace to apply to",
                        },
                    },
                    "required": ["filename"],
                },
            },
        ]

    def is_destructive(self, function_name: str, arguments: dict[str, Any]) -> bool:
        destructive_functions = {"kubectl_delete", "kubectl_apply", "kubectl_scale", "kubectl_restart"}
        return function_name in destructive_functions

    def execute_function(self, function_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        if function_name == "kubectl_get":
            return self._kubectl_get(**arguments)
        elif function_name == "kubectl_describe":
            return self._kubectl_describe(**arguments)
        elif function_name == "kubectl_logs":
            return self._kubectl_logs(**arguments)
        elif function_name == "kubectl_delete":
            return self._kubectl_delete(**arguments)
        elif function_name == "kubectl_apply":
            return self._kubectl_apply(**arguments)
        else:
            return {"success": False, "error": f"Unknown function: {function_name}"}

    def _kubectl_get(
        self,
        resource_type: str,
        namespace: str = "default",
        name: str | None = None,
        all_namespaces: bool = False,
    ) -> dict[str, Any]:
        cmd = ["kubectl", "get", resource_type]

        if all_namespaces:
            cmd.append("-A")
        elif namespace:
            cmd.extend(["-n", namespace])

        if name:
            cmd.append(name)

        cmd.append("-o=wide")

        return self.execute_command(cmd)

    def _kubectl_describe(
        self, resource_type: str, name: str, namespace: str = "default"
    ) -> dict[str, Any]:
        cmd = ["kubectl", "describe", resource_type, name, "-n", namespace]
        return self.execute_command(cmd)

    def _kubectl_logs(
        self,
        pod_name: str,
        namespace: str = "default",
        container: str | None = None,
        tail: int | None = None,
        follow: bool = False,
    ) -> dict[str, Any]:
        cmd = ["kubectl", "logs", pod_name, "-n", namespace]

        if container:
            cmd.extend(["-c", container])

        if tail:
            cmd.extend(["--tail", str(tail)])

        if follow:
            cmd.append("-f")

        return self.execute_command(cmd, timeout=60 if follow else 30)

    def _kubectl_delete(
        self, resource_type: str, name: str, namespace: str = "default"
    ) -> dict[str, Any]:
        cmd = ["kubectl", "delete", resource_type, name, "-n", namespace]
        return self.execute_command(cmd)

    def _kubectl_apply(self, filename: str, namespace: str | None = None) -> dict[str, Any]:
        cmd = ["kubectl", "apply", "-f", filename]

        if namespace:
            cmd.extend(["-n", namespace])

        return self.execute_command(cmd)
