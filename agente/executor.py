"""Executor de ferramentas registradas com correlação, autorização e auditoria."""

from __future__ import annotations

import multiprocessing
import os
from pathlib import Path
from queue import Empty
from shutil import disk_usage
from time import monotonic
from typing import Any

from agente.autorizacao import Approval, AuditLog, AuthorizationRequest, TaskState, is_authorized
from agente.ferramentas import ToolCall, ToolRegistry
from agente.tarefas import TaskStore


class ToolExecutor:
    def __init__(self, registry: ToolRegistry, task_store: TaskStore, audit_log: AuditLog) -> None:
        self.registry = registry
        self.task_store = task_store
        self.audit_log = audit_log

    def execute(self, task_id: str, call: ToolCall, approval: Approval | None = None) -> dict[str, Any]:
        task = self.task_store.get_task(task_id)
        if task.state is not TaskState.EXECUTING:
            raise ValueError("execucao requer tarefa em execucao")
        tool = self.registry.resolve(call)
        workspace = Path(task.workspace)
        approval = approval or self.task_store.active_approval(task_id, tool.required_action, workspace)
        allowed, reason = is_authorized(AuthorizationRequest(task_id, tool.required_action, workspace), approval)
        self.audit_log.append("tool_authorization_checked", task_id, f"tool={tool.name}; allowed={allowed}; reason={reason}")
        if not allowed:
            raise PermissionError(reason)

        if _available_disk_bytes(workspace) < task.min_free_disk_bytes:
            self.task_store.add_report(task_id, "resource_denied", f"tool={tool.name}; resource=disk")
            raise RuntimeError("espaco livre abaixo do limite da tarefa")
        result = self._run_handler(
            tool.handler,
            str(workspace),
            call.arguments,
            task.timeout_seconds,
            task.max_memory_bytes,
            task_id,
        )
        if "error" in result:
            error_name = str(result["error"])
            self.task_store.add_report(task_id, "tool_error", f"tool={tool.name}; error={error_name}")
            self.audit_log.append("tool_failed", task_id, f"tool={tool.name}; error={error_name}")
            raise RuntimeError(f"ferramenta falhou: {error_name}")
        if result.get("timed_out"):
            self.task_store.add_report(task_id, "tool_timeout", f"tool={tool.name}")
            self.audit_log.append("tool_timed_out", task_id, f"tool={tool.name}")
            raise TimeoutError("ferramenta excedeu o limite da tarefa")
        if result.get("cancelled"):
            self.task_store.add_report(task_id, "tool_cancelled", f"tool={tool.name}")
            self.audit_log.append("tool_cancelled", task_id, f"tool={tool.name}")
            raise InterruptedError("ferramenta cancelada")
        self.task_store.add_report(task_id, "tool_result", f"tool={tool.name}")
        self.audit_log.append("tool_finished", task_id, f"tool={tool.name}")
        return result["value"]

    def _run_handler(
        self,
        handler: Any,
        workspace: str,
        arguments: dict[str, Any],
        timeout: int,
        max_memory_bytes: int,
        task_id: str,
    ) -> dict[str, Any]:
        context = multiprocessing.get_context("spawn")
        results: multiprocessing.Queue[dict[str, Any]] = context.Queue()
        process = context.Process(target=_call_handler, args=(results, handler, workspace, arguments, max_memory_bytes, timeout))
        process.start()
        deadline = monotonic() + timeout
        while process.is_alive() and monotonic() < deadline:
            process.join(0.05)
            if self.task_store.get_task(task_id).state is TaskState.CANCELLED:
                process.terminate()
                process.join()
                return {"cancelled": True}
        if process.is_alive():
            process.terminate()
            process.join()
            return {"timed_out": True}
        try:
            return results.get(timeout=0.1)
        except Empty:
            return {"error": "handler terminou sem resultado"}


def _call_handler(
    results: multiprocessing.Queue[dict[str, Any]],
    handler: Any,
    workspace: str,
    arguments: dict[str, Any],
    max_memory_bytes: int,
    cpu_seconds: int,
) -> None:
    try:
        _apply_resource_limits(max_memory_bytes, cpu_seconds)
        results.put({"value": handler(workspace=workspace, **arguments)})
    except (FileNotFoundError, PermissionError, RuntimeError, OSError, TypeError, ValueError) as error:
        results.put({"error": type(error).__name__})


def _available_disk_bytes(path: Path) -> int:
    return disk_usage(path).free


def _apply_resource_limits(max_memory_bytes: int, cpu_seconds: int) -> None:
    if os.name != "posix":
        return
    import resource

    resource.setrlimit(resource.RLIMIT_AS, (max_memory_bytes, max_memory_bytes))
    resource.setrlimit(resource.RLIMIT_CPU, (cpu_seconds, cpu_seconds + 1))
