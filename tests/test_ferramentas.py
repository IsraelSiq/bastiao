import pytest

from agente.autorizacao import Action
from agente.ferramentas import ToolCall, ToolDefinition, ToolRegistry


def safe_handler(path: str) -> dict[str, str]:
    return {"path": path}


def tool(name: str = "read-file", version: str = "1") -> ToolDefinition:
    return ToolDefinition(name, version, "Reads an allowed file", Action.READ, {"path": str}, safe_handler)


def test_registry_discovers_versions_in_stable_order():
    registry = ToolRegistry()
    registry.register(tool("status", "2"))
    registry.register(tool("read-file", "1"))
    assert [(item.name, item.version) for item in registry.discover()] == [("read-file", "1"), ("status", "2")]


def test_registry_resolves_only_exact_version_and_schema():
    registry = ToolRegistry()
    registered = tool()
    registry.register(registered)
    assert registry.resolve(ToolCall("read-file", "1", {"path": "README.md"})) is registered
    with pytest.raises(KeyError):
        registry.resolve(ToolCall("read-file", "2", {"path": "README.md"}))
    with pytest.raises(ValueError, match="schema"):
        registry.resolve(ToolCall("read-file", "1", {"other": "README.md"}))
    with pytest.raises(ValueError, match="path"):
        registry.resolve(ToolCall("read-file", "1", {"path": 123}))


def test_registry_rejects_duplicate_name_and_version():
    registry = ToolRegistry()
    registry.register(tool())
    with pytest.raises(ValueError, match="ja registradas"):
        registry.register(tool())
