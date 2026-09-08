"""Contrato e registro local de ferramentas, sem despacho de execução."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from agente.autorizacao import Action


@dataclass(frozen=True)
class ToolDefinition:
    name: str
    version: str
    description: str
    required_action: Action
    input_schema: dict[str, type]
    handler: Callable[..., dict[str, Any]]


@dataclass(frozen=True)
class ToolCall:
    name: str
    version: str
    arguments: dict[str, Any]


class ToolRegistry:
    """Registra definições imutáveis e valida chamadas antes do executor."""

    def __init__(self) -> None:
        self._tools: dict[tuple[str, str], ToolDefinition] = {}

    def register(self, tool: ToolDefinition) -> None:
        key = (tool.name, tool.version)
        if not tool.name or not tool.version:
            raise ValueError("ferramenta requer nome e versao")
        if key in self._tools:
            raise ValueError("ferramenta e versao ja registradas")
        if not all(isinstance(name, str) and isinstance(expected, type) for name, expected in tool.input_schema.items()):
            raise ValueError("schema de entrada invalido")
        self._tools[key] = tool

    def discover(self) -> list[ToolDefinition]:
        return sorted(self._tools.values(), key=lambda tool: (tool.name, tool.version))

    def resolve(self, call: ToolCall) -> ToolDefinition:
        try:
            tool = self._tools[(call.name, call.version)]
        except KeyError as error:
            raise KeyError("ferramenta ou versao nao registrada") from error
        self._validate_arguments(call.arguments, tool.input_schema)
        return tool

    @staticmethod
    def _validate_arguments(arguments: dict[str, Any], schema: dict[str, type]) -> None:
        if set(arguments) != set(schema):
            raise ValueError("argumentos diferem do schema declarado")
        for name, expected_type in schema.items():
            value = arguments[name]
            if type(value) is not expected_type:
                raise ValueError(f"argumento invalido: {name}")
