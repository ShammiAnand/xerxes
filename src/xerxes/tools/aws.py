from typing import Any

from .base import BaseTool


class AWSTool(BaseTool):
    @property
    def name(self) -> str:
        return "aws"

    @property
    def cli_command(self) -> str:
        return "aws"

    @property
    def description(self) -> str:
        return "AWS CLI for managing EC2, S3, Lambda, and other AWS services"

    def get_function_schemas(self) -> list[dict[str, Any]]:
        return [
            {
                "name": "aws_s3_ls",
                "description": "List S3 buckets or objects in a bucket",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "S3 path (s3://bucket/prefix or empty for all buckets)",
                        },
                    },
                },
            },
            {
                "name": "aws_ec2_describe_instances",
                "description": "List EC2 instances",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "region": {
                            "type": "string",
                            "description": "AWS region (e.g., us-east-1)",
                        },
                        "instance_ids": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Specific instance IDs to describe",
                        },
                    },
                },
            },
            {
                "name": "aws_lambda_list_functions",
                "description": "List Lambda functions",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "region": {
                            "type": "string",
                            "description": "AWS region",
                        },
                    },
                },
            },
            {
                "name": "aws_cloudwatch_logs",
                "description": "Get CloudWatch logs for a log group",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "log_group": {
                            "type": "string",
                            "description": "CloudWatch log group name",
                        },
                        "region": {
                            "type": "string",
                            "description": "AWS region",
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Number of log events to retrieve",
                        },
                    },
                    "required": ["log_group"],
                },
            },
            {
                "name": "aws_ec2_terminate_instances",
                "description": "Terminate EC2 instances (DESTRUCTIVE)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "instance_ids": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Instance IDs to terminate",
                        },
                        "region": {
                            "type": "string",
                            "description": "AWS region",
                        },
                    },
                    "required": ["instance_ids"],
                },
            },
        ]

    def is_destructive(self, function_name: str, arguments: dict[str, Any]) -> bool:
        destructive_keywords = ["terminate", "delete", "remove", "destroy"]
        return any(keyword in function_name.lower() for keyword in destructive_keywords)

    def execute_function(self, function_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        if function_name == "aws_s3_ls":
            return self._aws_s3_ls(**arguments)
        elif function_name == "aws_ec2_describe_instances":
            return self._aws_ec2_describe_instances(**arguments)
        elif function_name == "aws_lambda_list_functions":
            return self._aws_lambda_list_functions(**arguments)
        elif function_name == "aws_cloudwatch_logs":
            return self._aws_cloudwatch_logs(**arguments)
        elif function_name == "aws_ec2_terminate_instances":
            return self._aws_ec2_terminate_instances(**arguments)
        else:
            return {"success": False, "error": f"Unknown function: {function_name}"}

    def _aws_s3_ls(self, path: str | None = None) -> dict[str, Any]:
        cmd = ["aws", "s3", "ls"]
        if path:
            cmd.append(path)
        return self.execute_command(cmd)

    def _aws_ec2_describe_instances(
        self, region: str | None = None, instance_ids: list[str] | None = None
    ) -> dict[str, Any]:
        cmd = ["aws", "ec2", "describe-instances"]
        if region:
            cmd.extend(["--region", region])
        if instance_ids:
            cmd.extend(["--instance-ids"] + instance_ids)
        cmd.extend(["--output", "json"])
        return self.execute_command(cmd)

    def _aws_lambda_list_functions(self, region: str | None = None) -> dict[str, Any]:
        cmd = ["aws", "lambda", "list-functions"]
        if region:
            cmd.extend(["--region", region])
        cmd.extend(["--output", "json"])
        return self.execute_command(cmd)

    def _aws_cloudwatch_logs(
        self, log_group: str, region: str | None = None, limit: int | None = None
    ) -> dict[str, Any]:
        cmd = ["aws", "logs", "filter-log-events", "--log-group-name", log_group]
        if region:
            cmd.extend(["--region", region])
        if limit:
            cmd.extend(["--max-items", str(limit)])
        cmd.extend(["--output", "json"])
        return self.execute_command(cmd)

    def _aws_ec2_terminate_instances(
        self, instance_ids: list[str], region: str | None = None
    ) -> dict[str, Any]:
        cmd = ["aws", "ec2", "terminate-instances", "--instance-ids"] + instance_ids
        if region:
            cmd.extend(["--region", region])
        cmd.extend(["--output", "json"])
        return self.execute_command(cmd)
