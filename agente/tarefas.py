"""Fila persistente de tarefas locais, sem execução automática."""

from __future__ import annotations

import sqlite3
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from agente.autorizacao import Action, Approval, AuditLog, TaskState, transition_allowed, utc_now
from agente.builder import TASK_ID_PATTERN

SCHEMA_VERSION = 2
SENSITIVE_VALUE = re.compile(r"(?i)\b(secret|token|password|api[_-]?key)\b(\s*[:=]\s*)([^\s,;]+)")


@dataclass(frozen=True)
class Task:
    task_id: str
    description: str
    workspace: str
    state: TaskState
    timeout_seconds: int
    max_attempts: int
    attempts: int
    max_memory_bytes: int
    min_free_disk_bytes: int
    created_at: str
    updated_at: str


class TaskStore:
    """Armazena a fila SQLite; o banco deve permanecer fora do repositório."""

    def __init__(self, database_path: Path, audit_log: AuditLog) -> None:
        self.database_path = database_path
        self.audit_log = audit_log

    def initialize(self) -> None:
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS schema_metadata (
                    version INTEGER NOT NULL
                );
                CREATE TABLE IF NOT EXISTS tasks (
                    task_id TEXT PRIMARY KEY,
                    description TEXT NOT NULL,
                    workspace TEXT NOT NULL,
                    state TEXT NOT NULL,
                    timeout_seconds INTEGER NOT NULL CHECK(timeout_seconds > 0),
                    max_attempts INTEGER NOT NULL CHECK(max_attempts > 0),
                    attempts INTEGER NOT NULL DEFAULT 0 CHECK(attempts >= 0),
                    max_memory_bytes INTEGER NOT NULL DEFAULT 1073741824 CHECK(max_memory_bytes > 0),
                    min_free_disk_bytes INTEGER NOT NULL DEFAULT 1073741824 CHECK(min_free_disk_bytes >= 0),
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS task_events (
                    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id TEXT NOT NULL REFERENCES tasks(task_id),
                    event_type TEXT NOT NULL,
                    detail TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS task_approvals (
                    approval_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id TEXT NOT NULL REFERENCES tasks(task_id),
                    action TEXT NOT NULL,
                    workspace TEXT NOT NULL,
                    approved_by TEXT NOT NULL,
                    expires_at TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS task_reports (
                    report_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id TEXT NOT NULL REFERENCES tasks(task_id),
                    report_type TEXT NOT NULL,
                    summary TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                """
            )
            columns = {row["name"] for row in connection.execute("PRAGMA table_info(tasks)")}
            if "max_memory_bytes" not in columns:
                connection.execute("ALTER TABLE tasks ADD COLUMN max_memory_bytes INTEGER NOT NULL DEFAULT 1073741824")
            if "min_free_disk_bytes" not in columns:
                connection.execute("ALTER TABLE tasks ADD COLUMN min_free_disk_bytes INTEGER NOT NULL DEFAULT 1073741824")
            if connection.execute("SELECT COUNT(*) FROM schema_metadata").fetchone()[0] == 0:
                connection.execute("INSERT INTO schema_metadata(version) VALUES (?)", (SCHEMA_VERSION,))
            else:
                connection.execute("UPDATE schema_metadata SET version = ?", (SCHEMA_VERSION,))
        self.database_path.chmod(0o600)

    def create_task(
        self,
        task_id: str,
        description: str,
        workspace: Path,
        timeout_seconds: int = 120,
        max_attempts: int = 1,
        max_memory_bytes: int = 1_073_741_824,
        min_free_disk_bytes: int = 1_073_741_824,
    ) -> Task:
        if not TASK_ID_PATTERN.fullmatch(task_id) or not description.strip():
            raise ValueError("tarefa requer id valido e descricao")
        if timeout_seconds <= 0 or max_attempts <= 0 or max_memory_bytes <= 0 or min_free_disk_bytes < 0:
            raise ValueError("limites devem ser positivos")
        now = utc_now().isoformat()
        with self._connect() as connection:
            connection.execute(
                "INSERT INTO tasks(task_id, description, workspace, state, timeout_seconds, max_attempts, attempts, max_memory_bytes, min_free_disk_bytes, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, 0, ?, ?, ?, ?)",
                (task_id, self._redact(description), str(workspace.resolve()), TaskState.PENDING, timeout_seconds, max_attempts, max_memory_bytes, min_free_disk_bytes, now, now),
            )
            self._event(connection, task_id, "created", "task created", now)
        self.audit_log.append("task_created", task_id, "persistent task created")
        return self.get_task(task_id)

    def transition(self, task_id: str, target: TaskState) -> Task:
        with self._connect() as connection:
            row = connection.execute("SELECT state FROM tasks WHERE task_id = ?", (task_id,)).fetchone()
            if row is None:
                raise KeyError("tarefa nao encontrada")
            current = TaskState(row["state"])
            if not transition_allowed(current, target):
                raise ValueError(f"transicao invalida: {current} -> {target}")
            now = utc_now().isoformat()
            connection.execute("UPDATE tasks SET state = ?, updated_at = ? WHERE task_id = ?", (target, now, task_id))
            self._event(connection, task_id, "state_changed", f"{current}->{target}", now)
        self.audit_log.append("task_state_changed", task_id, f"{current}->{target}")
        return self.get_task(task_id)

    def register_attempt(self, task_id: str) -> Task:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT attempts, max_attempts, state FROM tasks WHERE task_id = ?",
                (task_id,),
            ).fetchone()
            if row is None:
                raise KeyError("tarefa nao encontrada")
            if TaskState(row["state"]) is not TaskState.EXECUTING:
                raise ValueError("tentativa requer tarefa em execucao")
            if row["attempts"] >= row["max_attempts"]:
                raise ValueError("limite de tentativas atingido")
            now = utc_now().isoformat()
            connection.execute(
                "UPDATE tasks SET attempts = attempts + 1, updated_at = ? WHERE task_id = ?",
                (now, task_id),
            )
            self._event(connection, task_id, "attempt_started", f"attempt={row['attempts'] + 1}", now)
        self.audit_log.append("task_attempt_started", task_id, f"attempt={row['attempts'] + 1}")
        return self.get_task(task_id)

    def get_task(self, task_id: str) -> Task:
        with self._connect() as connection:
            row = connection.execute("SELECT * FROM tasks WHERE task_id = ?", (task_id,)).fetchone()
        if row is None:
            raise KeyError("tarefa nao encontrada")
        return self._to_task(row)

    def list_tasks(self, state: TaskState | None = None) -> list[Task]:
        query, parameters = "SELECT * FROM tasks", ()
        if state is not None:
            query, parameters = f"{query} WHERE state = ?", (state,)
        with self._connect() as connection:
            rows = connection.execute(f"{query} ORDER BY created_at", parameters).fetchall()
        return [self._to_task(row) for row in rows]

    def report(self, task_id: str) -> dict[str, object]:
        task = self.get_task(task_id)
        with self._connect() as connection:
            events = [dict(row) for row in connection.execute("SELECT event_type, detail, created_at FROM task_events WHERE task_id = ? ORDER BY event_id", (task_id,))]
        return {"task": task, "events": events}

    def add_report(self, task_id: str, report_type: str, summary: str) -> None:
        if not report_type.strip() or not summary.strip():
            raise ValueError("relatorio requer tipo e resumo")
        self.get_task(task_id)
        now = utc_now().isoformat()
        with self._connect() as connection:
            connection.execute(
                "INSERT INTO task_reports(task_id, report_type, summary, created_at) VALUES (?, ?, ?, ?)",
                (task_id, report_type, self._redact(summary), now),
            )
            self._event(connection, task_id, "report_added", f"type={report_type}", now)

    def approvals(self, task_id: str) -> list[dict[str, str]]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT action, workspace, approved_by, expires_at, created_at FROM task_approvals WHERE task_id = ? ORDER BY approval_id",
                (task_id,),
            ).fetchall()
        return [dict(row) for row in rows]

    def add_approval(self, approval: Approval) -> None:
        self.get_task(approval.task_id)
        now = utc_now().isoformat()
        with self._connect() as connection:
            connection.execute(
                "INSERT INTO task_approvals(task_id, action, workspace, approved_by, expires_at, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                (
                    approval.task_id,
                    str(approval.action),
                    str(approval.workspace.resolve()),
                    approval.approved_by,
                    approval.expires_at.isoformat(),
                    now,
                ),
            )
            self._event(connection, approval.task_id, "approval_recorded", f"action={approval.action}", now)
        self.audit_log.append("task_approval_recorded", approval.task_id, f"action={approval.action}")

    def active_approval(self, task_id: str, action: Action, workspace: Path, now: datetime | None = None) -> Approval | None:
        current = (now or utc_now()).isoformat()
        with self._connect() as connection:
            row = connection.execute(
                "SELECT action, workspace, approved_by, expires_at FROM task_approvals WHERE task_id = ? AND action = ? AND workspace = ? AND expires_at > ? ORDER BY approval_id DESC LIMIT 1",
                (task_id, str(action), str(workspace.resolve()), current),
            ).fetchone()
        if row is None:
            return None
        return Approval(task_id, Action(row["action"]), Path(row["workspace"]), row["approved_by"], datetime.fromisoformat(row["expires_at"]))
    def reports(self, task_id: str) -> list[dict[str, str]]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT report_type, summary, created_at FROM task_reports WHERE task_id = ? ORDER BY report_id",
                (task_id,),
            ).fetchall()
        return [dict(row) for row in rows]

    def queue_view(self) -> list[dict[str, object]]:
        return [
            {
                "task": task,
                "approvals": self.approvals(task.task_id),
                "reports": self.reports(task.task_id),
            }
            for task in self.list_tasks()
        ]

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    @staticmethod
    def _event(connection: sqlite3.Connection, task_id: str, event_type: str, detail: str, created_at: str) -> None:
        connection.execute("INSERT INTO task_events(task_id, event_type, detail, created_at) VALUES (?, ?, ?, ?)", (task_id, event_type, detail, created_at))

    @staticmethod
    def _to_task(row: sqlite3.Row) -> Task:
        values = dict(row)
        values["state"] = TaskState(values["state"])
        return Task(**values)

    @staticmethod
    def _redact(text: str) -> str:
        return SENSITIVE_VALUE.sub(r"\1\2[REDACTED]", text)
