"""Controles locais de autorização e auditoria para tarefas do Bastião."""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
from pathlib import Path


class Action(StrEnum):
    READ = "read"
    EDIT = "edit"
    TEST = "test"
    COMMIT = "commit"
    PUSH = "push"
    PULL_REQUEST = "pull_request"
    DEPLOY = "deploy"
    EXTERNAL_API = "external_api"


class TaskState(StrEnum):
    PENDING = "pending"
    PLANNING = "planning"
    AWAITING_APPROVAL = "awaiting_approval"
    EXECUTING = "executing"
    TESTING = "testing"
    REVIEW = "review"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    FAILED = "failed"
    CANCELLED = "cancelled"


ALLOWED_TRANSITIONS: dict[TaskState, set[TaskState]] = {
    TaskState.PENDING: {TaskState.PLANNING, TaskState.CANCELLED},
    TaskState.PLANNING: {TaskState.AWAITING_APPROVAL, TaskState.BLOCKED, TaskState.FAILED},
    TaskState.AWAITING_APPROVAL: {TaskState.EXECUTING, TaskState.CANCELLED, TaskState.BLOCKED},
    TaskState.EXECUTING: {TaskState.TESTING, TaskState.REVIEW, TaskState.BLOCKED, TaskState.FAILED},
    TaskState.TESTING: {TaskState.REVIEW, TaskState.BLOCKED, TaskState.FAILED},
    TaskState.REVIEW: {TaskState.AWAITING_APPROVAL, TaskState.COMPLETED, TaskState.BLOCKED},
    TaskState.BLOCKED: {TaskState.PLANNING, TaskState.CANCELLED},
    TaskState.FAILED: {TaskState.PLANNING, TaskState.CANCELLED},
    TaskState.COMPLETED: set(),
    TaskState.CANCELLED: set(),
}

APPROVAL_REQUIRED = {
    Action.EDIT,
    Action.COMMIT,
    Action.PUSH,
    Action.PULL_REQUEST,
    Action.DEPLOY,
    Action.EXTERNAL_API,
}


@dataclass(frozen=True)
class Approval:
    task_id: str
    action: Action
    workspace: Path
    approved_by: str
    expires_at: datetime


@dataclass(frozen=True)
class AuthorizationRequest:
    task_id: str
    action: Action
    workspace: Path


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def transition_allowed(current: TaskState, target: TaskState) -> bool:
    return target in ALLOWED_TRANSITIONS[current]


def is_authorized(
    request: AuthorizationRequest,
    approval: Approval | None,
    now: datetime | None = None,
) -> tuple[bool, str]:
    if request.action not in APPROVAL_REQUIRED:
        return True, "acao permitida pela politica local"
    if approval is None:
        return False, "aprovacao explicita obrigatoria"
    if approval.task_id != request.task_id:
        return False, "aprovacao vinculada a outra tarefa"
    if approval.action != request.action:
        return False, "aprovacao vinculada a outra acao"
    if approval.workspace.resolve() != request.workspace.resolve():
        return False, "aprovacao vinculada a outro workspace"
    if approval.expires_at <= (now or utc_now()):
        return False, "aprovacao expirada"
    return True, "aprovacao valida"


class AuditLog:
    """Registro JSONL encadeado por hash; o diretório deve ficar fora do repositório."""

    def __init__(self, path: Path) -> None:
        self.path = path

    def append(self, event: str, task_id: str, detail: str, at: datetime | None = None) -> dict[str, str]:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        os.chmod(self.path.parent, 0o700)
        previous_hash = self._last_hash()
        payload = {
            "at": (at or utc_now()).isoformat(),
            "event": event,
            "task_id": task_id,
            "detail": detail,
            "previous_hash": previous_hash,
        }
        serialized = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        payload["hash"] = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
        with self.path.open("a", encoding="utf-8") as log_file:
            log_file.write(json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n")
        os.chmod(self.path, 0o600)
        return {key: str(value) for key, value in payload.items()}

    def _last_hash(self) -> str:
        if not self.path.is_file():
            return ""
        with self.path.open(encoding="utf-8") as log_file:
            lines = [line for line in log_file if line.strip()]
        if not lines:
            return ""
        try:
            return str(json.loads(lines[-1])["hash"])
        except (json.JSONDecodeError, KeyError) as error:
            raise ValueError("trilha de auditoria invalida") from error
