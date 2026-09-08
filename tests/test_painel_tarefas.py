import json
import subprocess
import sys
from pathlib import Path

from agente.autorizacao import AuditLog, TaskState
from agente.tarefas import TaskStore


SCRIPT = Path(__file__).parents[1] / "scripts" / "painel_tarefas.py"


def test_terminal_panel_approves_and_displays_a_task(tmp_path: Path):
    database = tmp_path / "state" / "tasks.sqlite"
    audit_log = tmp_path / "state" / "audit.jsonl"
    store = TaskStore(database, AuditLog(audit_log))
    store.initialize()
    store.create_task("task-1", "Review task", tmp_path / "workspace")
    store.transition("task-1", TaskState.PLANNING)

    approved = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--database",
            str(database),
            "--audit-log",
            str(audit_log),
            "approve",
            "task-1",
            "--action",
            "edit",
            "--approved-by",
            "owner",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    queue = subprocess.run(
        [sys.executable, str(SCRIPT), "--database", str(database), "--audit-log", str(audit_log), "queue"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert json.loads(approved.stdout)["approved"] == "task-1"
    assert json.loads(queue.stdout)[0]["task"]["state"] == "awaiting_approval"
