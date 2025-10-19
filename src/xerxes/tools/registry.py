from typing import Any

from .base import BaseTool


class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, BaseTool] = {}

    def register(self, tool: BaseTool) -> None:
        self._tools[tool.name] = tool

    def get_tool(self, name: str) -> BaseTool | None:
        return self._tools.get(name)

    def get_all_tools(self) -> list[BaseTool]:
        return list(self._tools.values())

    def get_available_tools(self) -> list[BaseTool]:
        return [tool for tool in self._tools.values() if tool.is_installed()]

    def get_function_schemas(self) -> list[dict[str, Any]]:
        schemas = []
        for tool in self.get_available_tools():
            schemas.extend(tool.get_function_schemas())
        return schemas

    def execute_function(self, function_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        for tool in self.get_available_tools():
            schemas = tool.get_function_schemas()
            if any(schema["name"] == function_name for schema in schemas):
                return tool.execute_function(function_name, arguments)

        raise ValueError(f"Function '{function_name}' not found in any registered tool")

    def is_destructive(self, function_name: str, arguments: dict[str, Any]) -> bool:
        for tool in self.get_available_tools():
            schemas = tool.get_function_schemas()
            if any(schema["name"] == function_name for schema in schemas):
                command = arguments.get("command", "")
                return tool.is_destructive(command)

        return False


_registry = ToolRegistry()


def get_registry() -> ToolRegistry:
    return _registry


def register_tool(tool: BaseTool) -> None:
    _registry.register(tool)
