from pathlib import Path

import pytest

from agente.autorizacao import AuditLog, TaskState
from agente.tarefas import TaskStore


def store(tmp_path: Path) -> TaskStore:
    result = TaskStore(tmp_path / "state" / "tasks.sqlite", AuditLog(tmp_path / "audit.jsonl"))
    result.initialize()
    return result


def test_task_persists_across_store_instances(tmp_path: Path):
    first = store(tmp_path)
    first.create_task("task-1", "Validate a project", tmp_path / "workspaces" / "task-1")
    recovered = store(tmp_path).get_task("task-1")
    assert recovered.state is TaskState.PENDING
    assert recovered.description == "Validate a project"


def test_invalid_transition_is_rejected_and_valid_transition_is_recorded(tmp_path: Path):
    task_store = store(tmp_path)
    task_store.create_task("task-1", "Validate a project", tmp_path / "workspace")
    with pytest.raises(ValueError, match="transicao invalida"):
        task_store.transition("task-1", TaskState.COMPLETED)
    task_store.transition("task-1", TaskState.PLANNING)
    assert task_store.report("task-1")["events"][-1]["detail"] == "pending->planning"


def test_task_limits_and_filtering_are_enforced(tmp_path: Path):
    task_store = store(tmp_path)
    with pytest.raises(ValueError):
        task_store.create_task("bad", "Invalid", tmp_path, timeout_seconds=0)
    task_store.create_task("task-1", "First", tmp_path / "one")
    task_store.create_task("task-2", "Second", tmp_path / "two")
    task_store.transition("task-2", TaskState.PLANNING)
    assert [task.task_id for task in task_store.list_tasks(TaskState.PENDING)] == ["task-1"]
