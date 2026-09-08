"""Executor de ferramentas registradas com correlação, autorização e auditoria."""

from __future__ import annotations

import multiprocessing
from pathlib import Path
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
        allowed, reason = is_authorized(AuthorizationRequest(task_id, tool.required_action, workspace), approval)
        self.audit_log.append("tool_authorization_checked", task_id, f"tool={tool.name}; allowed={allowed}; reason={reason}")
        if not allowed:
            raise PermissionError(reason)

        result = self._run_handler(tool.handler, str(workspace), call.arguments, task.timeout_seconds)
        if "error" in result:
            error_name = str(result["error"])
            self.task_store.add_report(task_id, "tool_error", f"tool={tool.name}; error={error_name}")
            self.audit_log.append("tool_failed", task_id, f"tool={tool.name}; error={error_name}")
            raise RuntimeError(f"ferramenta falhou: {error_name}")
        if result.get("timed_out"):
            self.task_store.add_report(task_id, "tool_timeout", f"tool={tool.name}")
            self.audit_log.append("tool_timed_out", task_id, f"tool={tool.name}")
            raise TimeoutError("ferramenta excedeu o limite da tarefa")
        self.task_store.add_report(task_id, "tool_result", f"tool={tool.name}")
        self.audit_log.append("tool_finished", task_id, f"tool={tool.name}")
        return result["value"]

    @staticmethod
    def _run_handler(handler: Any, workspace: str, arguments: dict[str, Any], timeout: int) -> dict[str, Any]:
        context = multiprocessing.get_context("spawn")
        results: multiprocessing.Queue[dict[str, Any]] = context.Queue()
        process = context.Process(target=_call_handler, args=(results, handler, workspace, arguments))
        process.start()
        process.join(timeout)
        if process.is_alive():
            process.terminate()
            process.join()
            return {"timed_out": True}
        if results.empty():
            return {"error": "handler terminou sem resultado"}
        return results.get()


def _call_handler(results: multiprocessing.Queue[dict[str, Any]], handler: Any, workspace: str, arguments: dict[str, Any]) -> None:
    try:
        results.put({"value": handler(workspace=workspace, **arguments)})
    except (FileNotFoundError, PermissionError, RuntimeError, OSError, TypeError, ValueError) as error:
        results.put({"error": type(error).__name__})
