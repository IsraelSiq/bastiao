#!/usr/bin/env python3
"""Interface local de terminal para consultar e aprovar tarefas persistidas."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agente.autorizacao import Action, Approval, AuditLog, TaskState, utc_now
from agente.relatorios import queue_report, task_report
from agente.tarefas import TaskStore
from agente.worker import TaskWorker


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Painel local de tarefas do Bastião")
    parser.add_argument("--database", type=Path, required=True, help="Caminho do banco SQLite fora do repositório")
    parser.add_argument("--audit-log", type=Path, required=True, help="Caminho do log de auditoria fora do repositório")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("queue")
    show = subparsers.add_parser("show")
    show.add_argument("task_id")
    approve = subparsers.add_parser("approve")
    approve.add_argument("task_id")
    approve.add_argument("--action", choices=[action.value for action in Action], required=True)
    approve.add_argument("--approved-by", required=True)
    approve.add_argument("--expires-in-minutes", type=int, default=10)
    cancel = subparsers.add_parser("cancel")
    cancel.add_argument("task_id")
    return parser.parse_args()


def serialize(value: object) -> object:
    if isinstance(value, TaskState):
        return value.value
    if hasattr(value, "__dataclass_fields__"):
        return asdict(value)
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, datetime):
        return value.isoformat()
    raise TypeError(f"valor nao serializavel: {type(value).__name__}")


def main() -> None:
    args = parse_args()
    store = TaskStore(args.database, AuditLog(args.audit_log))
    store.initialize()
    if args.command == "queue":
        result: object = queue_report(store)
    elif args.command == "show":
        result = task_report(store, args.task_id)
    elif args.command == "approve":
        if args.expires_in_minutes <= 0:
            raise ValueError("expiracao deve ser positiva")
        task = store.get_task(args.task_id)
        approval = Approval(
            task.task_id,
            Action(args.action),
            Path(task.workspace),
            args.approved_by,
            utc_now() + timedelta(minutes=args.expires_in_minutes),
        )
        store.add_approval(approval)
        if task.state is TaskState.PLANNING:
            store.transition(task.task_id, TaskState.AWAITING_APPROVAL)
        result = {"approved": task.task_id, "action": args.action, "expires_at": approval.expires_at}
    else:
        result = asdict(TaskWorker(store).cancel(args.task_id))
    print(json.dumps(result, default=serialize, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
