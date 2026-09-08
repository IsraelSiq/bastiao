from datetime import timedelta
from pathlib import Path

from agente.autorizacao import (
    Action,
    Approval,
    AuthorizationRequest,
    AuditLog,
    TaskState,
    is_authorized,
    transition_allowed,
    utc_now,
)


def test_read_requires_no_approval(tmp_path: Path):
    request = AuthorizationRequest("task-1", Action.READ, tmp_path)
    assert is_authorized(request, None)[0] is True


def test_external_actions_require_matching_unexpired_approval(tmp_path: Path):
    now = utc_now()
    request = AuthorizationRequest("task-1", Action.PUSH, tmp_path)
    approval = Approval("task-1", Action.PUSH, tmp_path, "israel", now + timedelta(minutes=10))
    assert is_authorized(request, approval, now) == (True, "aprovacao valida")


def test_approval_cannot_be_reused_for_another_workspace(tmp_path: Path):
    now = utc_now()
    request = AuthorizationRequest("task-1", Action.COMMIT, tmp_path / "other")
    approval = Approval("task-1", Action.COMMIT, tmp_path, "israel", now + timedelta(minutes=10))
    assert is_authorized(request, approval, now)[0] is False


def test_expired_approval_is_rejected(tmp_path: Path):
    now = utc_now()
    request = AuthorizationRequest("task-1", Action.DEPLOY, tmp_path)
    approval = Approval("task-1", Action.DEPLOY, tmp_path, "israel", now - timedelta(seconds=1))
    assert is_authorized(request, approval, now)[0] is False


def test_invalid_state_transition_is_rejected():
    assert transition_allowed(TaskState.PENDING, TaskState.COMPLETED) is False
    assert transition_allowed(TaskState.PENDING, TaskState.PLANNING) is True


def test_audit_log_chains_events(tmp_path: Path):
    log = AuditLog(tmp_path / "audit" / "events.jsonl")
    first = log.append("planned", "task-1", "scope confirmed")
    second = log.append("approved", "task-1", "edit approved")
    assert first["previous_hash"] == ""
    assert second["previous_hash"] == first["hash"]
