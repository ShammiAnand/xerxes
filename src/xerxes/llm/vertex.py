import os
from typing import Any

from google.cloud import aiplatform
from vertexai.generative_models import Content, FunctionDeclaration, GenerativeModel, Part, Tool

from .base import BaseLLMProvider, LLMResponse, Message, ToolCall


class VertexAIProvider(BaseLLMProvider):
    def __init__(
        self,
        project_id: str | None = None,
        location: str = "us-central1",
        model_name: str = "claude-3-5-sonnet@20240620",
        **kwargs,
    ):
        super().__init__(**kwargs)

        self.project_id = project_id or os.getenv("GOOGLE_CLOUD_PROJECT")
        self.location = location
        self.model_name = model_name

        if self.project_id:
            aiplatform.init(project=self.project_id, location=self.location)

    def chat(
        self,
        messages: list[Message],
        tools: list[dict[str, Any]] | None = None,
        max_tokens: int = 4096,
        temperature: float = 0.0,
        **kwargs,
    ) -> LLMResponse:
        model = GenerativeModel(self.model_name)
        contents = self._convert_messages(messages)

        vertex_tools = None
        if tools:
            vertex_tools = [self._convert_tools(tools)]

        generation_config = {
            "max_output_tokens": max_tokens,
            "temperature": temperature,
        }

        response = model.generate_content(
            contents,
            tools=vertex_tools,
            generation_config=generation_config,
        )

        return self._parse_response(response)

    def _convert_messages(self, messages: list[Message]) -> list[Content]:
        contents = []
        system_instruction = None

        for msg in messages:
            if msg.role == "system":
                system_instruction = msg.content
            else:
                role = "model" if msg.role == "assistant" else msg.role
                contents.append(Content(role=role, parts=[Part.from_text(msg.content)]))

        if system_instruction:
            contents.insert(
                0, Content(role="user", parts=[Part.from_text(f"System: {system_instruction}")])
            )

        return contents

    def _convert_tools(self, tools: list[dict[str, Any]]) -> Tool:
        function_declarations = []

        for tool in tools:
            func_decl = FunctionDeclaration(
                name=tool["name"],
                description=tool.get("description", ""),
                parameters=tool.get("parameters", {}),
            )
            function_declarations.append(func_decl)

        return Tool(function_declarations=function_declarations)

    def _parse_response(self, response) -> LLMResponse:
        content = None
        tool_calls = []
        stop_reason = None

        if response.text:
            content = response.text

        if hasattr(response, "candidates") and response.candidates:
            candidate = response.candidates[0]

            if hasattr(candidate.content, "parts"):
                for part in candidate.content.parts:
                    if hasattr(part, "function_call") and part.function_call:
                        fc = part.function_call
                        tool_call = ToolCall(
                            id=fc.name,
                            name=fc.name,
                            arguments=dict(fc.args) if fc.args else {},
                        )
                        tool_calls.append(tool_call)

            if hasattr(candidate, "finish_reason"):
                stop_reason = str(candidate.finish_reason)

        usage = None
        if hasattr(response, "usage_metadata"):
            usage = {
                "prompt_tokens": response.usage_metadata.prompt_token_count,
                "completion_tokens": response.usage_metadata.candidates_token_count,
                "total_tokens": response.usage_metadata.total_token_count,
            }

        return LLMResponse(
            content=content,
            tool_calls=tool_calls if tool_calls else None,
            stop_reason=stop_reason,
            usage=usage,
        )

    def is_available(self) -> bool:
        if not self.project_id:
            return False

        try:
            aiplatform.init(project=self.project_id, location=self.location)
            return True
        except Exception:
            return False

    @property
    def name(self) -> str:
        return "vertex"
