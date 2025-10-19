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
        return "Manage AWS resources - EC2, S3, Lambda, CloudWatch, IAM, VPC, RDS, and all AWS services"
