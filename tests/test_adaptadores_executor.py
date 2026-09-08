from pathlib import Path
from subprocess import run

import pytest
from time import sleep

from agente.adaptadores import git_readonly, read_workspace_file
from agente.autorizacao import Action, AuditLog, TaskState
from agente.executor import ToolExecutor
from agente.ferramentas import ToolCall, ToolDefinition, ToolRegistry
from agente.tarefas import TaskStore


def slow_handler(workspace: str, path: str) -> dict[str, str]:
    sleep(1.2)
    return {"path": path}


def task_store(tmp_path: Path) -> TaskStore:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    (workspace / "README.md").write_text("safe", encoding="utf-8")
    run(["git", "init"], cwd=workspace, check=True, capture_output=True)
    store = TaskStore(tmp_path / "state" / "tasks.sqlite", AuditLog(tmp_path / "audit.jsonl"))
    store.initialize()
    store.create_task("task-1", "Read project", workspace)
    store.transition("task-1", TaskState.PLANNING)
    store.transition("task-1", TaskState.AWAITING_APPROVAL)
    store.transition("task-1", TaskState.EXECUTING)
    return store


def test_read_adapter_blocks_secrets_and_traversal(tmp_path: Path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    (workspace / "README.md").write_text("safe", encoding="utf-8")
    (workspace / ".env").write_text("SECRET=1", encoding="utf-8")
    assert read_workspace_file(str(workspace), "README.md")["content"] == "safe"
    with pytest.raises(PermissionError):
        read_workspace_file(str(workspace), ".env")
    with pytest.raises(PermissionError):
        read_workspace_file(str(workspace), "../outside")


def test_git_adapter_allows_only_read_operations(tmp_path: Path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    run(["git", "init"], cwd=workspace, check=True, capture_output=True)
    assert "##" in git_readonly(str(workspace), "status")["output"]
    with pytest.raises(PermissionError):
        git_readonly(str(workspace), "reset")


def test_executor_correlates_running_task_and_persists_redacted_report(tmp_path: Path):
    store = task_store(tmp_path)
    registry = ToolRegistry()
    registry.register(ToolDefinition("read-file", "1", "Read allowed file", Action.READ, {"path": str}, read_workspace_file))
    executor = ToolExecutor(registry, store, AuditLog(tmp_path / "audit.jsonl"))

    result = executor.execute("task-1", ToolCall("read-file", "1", {"path": "README.md"}))

    assert result["content"] == "safe"
    assert store.reports("task-1")[0]["summary"].startswith("tool=read-file")
    assert "safe" not in store.reports("task-1")[0]["summary"]


def test_executor_rejects_task_that_is_not_running(tmp_path: Path):
    store = task_store(tmp_path)
    store.transition("task-1", TaskState.TESTING)
    registry = ToolRegistry()
    registry.register(ToolDefinition("read-file", "1", "Read allowed file", Action.READ, {"path": str}, read_workspace_file))
    with pytest.raises(ValueError, match="em execucao"):
        ToolExecutor(registry, store, AuditLog(tmp_path / "audit.jsonl")).execute("task-1", ToolCall("read-file", "1", {"path": "README.md"}))


def test_executor_terminates_handler_at_task_timeout(tmp_path: Path):
    store = task_store(tmp_path)
    with store._connect() as connection:
        connection.execute("UPDATE tasks SET timeout_seconds = 1 WHERE task_id = 'task-1'")
    registry = ToolRegistry()
    registry.register(ToolDefinition("slow", "1", "Controlled timeout", Action.READ, {"path": str}, slow_handler))
    executor = ToolExecutor(registry, store, AuditLog(tmp_path / "audit.jsonl"))
    with pytest.raises(TimeoutError):
        executor.execute("task-1", ToolCall("slow", "1", {"path": "README.md"}))
    assert store.reports("task-1")[0]["report_type"] == "tool_timeout"
