"""Visões locais, somente leitura, para fila e aprovações persistidas."""

from __future__ import annotations

from typing import Any

from agente.tarefas import TaskStore


def task_report(store: TaskStore, task_id: str) -> dict[str, Any]:
    """Retorna o histórico persistido e os metadados seguros de uma tarefa."""
    return {
        **store.report(task_id),
        "approvals": store.approvals(task_id),
        "reports": store.reports(task_id),
    }


def queue_report(store: TaskStore) -> list[dict[str, Any]]:
    """Retorna a fila persistida sem executar, aprovar ou alterar tarefas."""
    return store.queue_view()
