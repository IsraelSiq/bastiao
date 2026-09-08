from pathlib import Path
from datetime import timedelta

import pytest

from agente.autorizacao import Action, Approval, AuditLog, TaskState, utc_now
from agente.relatorios import queue_report, task_report
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


def test_reports_and_approvals_are_persisted_without_secret_values(tmp_path: Path):
    task_store = store(tmp_path)
    workspace = tmp_path / "workspace"
    task_store.create_task("task-1", "token=do-not-store", workspace)
    task_store.add_approval(Approval("task-1", Action.EDIT, workspace, "owner", utc_now() + timedelta(minutes=10)))
    task_store.add_report("task-1", "plan", "password=do-not-store")

    report = task_report(task_store, "task-1")
    queue = queue_report(task_store)

    assert report["task"].description == "token=[REDACTED]"
    assert report["reports"][0]["summary"] == "password=[REDACTED]"
    assert report["approvals"][0]["action"] == "edit"
    assert queue[0]["task"].task_id == "task-1"
