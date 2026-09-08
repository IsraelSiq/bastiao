from pathlib import Path

import pytest

from agente.autorizacao import Action, AuditLog, TaskState
from agente.adaptadores import read_workspace_file
from agente.executor import ToolExecutor
from agente.ferramentas import ToolCall, ToolDefinition, ToolRegistry
from agente.tarefas import TaskStore
from agente.worker import TaskWorker


def prepare(tmp_path: Path, attempts: int = 2) -> tuple[TaskStore, TaskWorker]:
    task_store = TaskStore(tmp_path / "tasks.sqlite", AuditLog(tmp_path / "audit.jsonl"))
    task_store.initialize()
    task_store.create_task("task-1", "Controlled task", tmp_path / "workspace", max_attempts=attempts)
    task_store.transition("task-1", TaskState.PLANNING)
    task_store.transition("task-1", TaskState.AWAITING_APPROVAL)
    return task_store, TaskWorker(task_store)


def test_worker_counts_attempt_and_moves_success_to_review(tmp_path: Path):
    store, worker = prepare(tmp_path)
    running = worker.begin("task-1")
    completed = worker.succeed("task-1")
    assert running.attempts == 1
    assert completed.state is TaskState.REVIEW


def test_worker_retries_only_with_remaining_attempts(tmp_path: Path):
    store, worker = prepare(tmp_path, attempts=2)
    worker.begin("task-1")
    assert worker.fail("task-1").state is TaskState.PLANNING
    store.transition("task-1", TaskState.AWAITING_APPROVAL)
    worker.begin("task-1")
    assert worker.fail("task-1").state is TaskState.FAILED


def test_recovery_blocks_interrupted_work_instead_of_repeating_it(tmp_path: Path):
    store, worker = prepare(tmp_path)
    worker.begin("task-1")
    recovered = worker.recover_interrupted()
    assert [task.task_id for task in recovered] == ["task-1"]
    assert store.get_task("task-1").state is TaskState.BLOCKED


def test_worker_cancellation_and_invalid_start_are_explicit(tmp_path: Path):
    store, worker = prepare(tmp_path)
    assert worker.cancel("task-1").state is TaskState.CANCELLED
    with pytest.raises(ValueError, match="inicio requer"):
        worker.begin("task-1")


def test_worker_executes_once_and_never_replays_automatically(tmp_path: Path):
    store, worker = prepare(tmp_path)
    workspace = Path(store.get_task("task-1").workspace)
    workspace.mkdir()
    (workspace / "README.md").write_text("safe", encoding="utf-8")
    registry = ToolRegistry()
    registry.register(ToolDefinition("read-file", "1", "Read file", Action.READ, {"path": str}, read_workspace_file))
    executor = ToolExecutor(registry, store, AuditLog(tmp_path / "audit.jsonl"))

    result = worker.execute_once("task-1", executor, ToolCall("read-file", "1", {"path": "README.md"}))

    assert result["content"] == "safe"
    assert store.get_task("task-1").state is TaskState.REVIEW
