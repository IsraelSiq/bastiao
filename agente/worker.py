"""Ciclo de vida seguro para tarefas persistidas, sem executar comandos."""

from __future__ import annotations

from threading import Lock
from agente.autorizacao import TaskState
from agente.executor import ToolExecutor
from agente.ferramentas import ToolCall
from agente.tarefas import Task, TaskStore


class TaskWorker:
    """Coordena estados e tentativas; executores de ferramentas são outra camada."""

    def __init__(self, task_store: TaskStore, max_concurrency: int = 1) -> None:
        if max_concurrency <= 0:
            raise ValueError("max_concurrency deve ser positivo")
        self.task_store = task_store
        self.max_concurrency = max_concurrency
        self._active_task_ids: set[str] = set()
        self._lock = Lock()

    def begin(self, task_id: str) -> Task:
        task = self.task_store.get_task(task_id)
        if task.state is not TaskState.AWAITING_APPROVAL:
            raise ValueError("inicio requer tarefa aguardando aprovacao")
        task = self.task_store.transition(task_id, TaskState.EXECUTING)
        return self.task_store.register_attempt(task.task_id)

    def succeed(self, task_id: str) -> Task:
        task = self.task_store.get_task(task_id)
        if task.state is not TaskState.EXECUTING:
            raise ValueError("conclusao requer tarefa em execucao")
        self.task_store.transition(task_id, TaskState.TESTING)
        return self.task_store.transition(task_id, TaskState.REVIEW)

    def fail(self, task_id: str) -> Task:
        task = self.task_store.get_task(task_id)
        if task.state is not TaskState.EXECUTING:
            raise ValueError("falha requer tarefa em execucao")
        self.task_store.transition(task_id, TaskState.FAILED)
        failed = self.task_store.get_task(task_id)
        if failed.attempts < failed.max_attempts:
            return self.task_store.transition(task_id, TaskState.PLANNING)
        return failed

    def cancel(self, task_id: str) -> Task:
        task = self.task_store.get_task(task_id)
        if task.state in {TaskState.COMPLETED, TaskState.CANCELLED}:
            raise ValueError("tarefa terminal nao pode ser cancelada")
        return self.task_store.transition(task_id, TaskState.CANCELLED)

    def recover_interrupted(self) -> list[Task]:
        recovered: list[Task] = []
        for state in (TaskState.EXECUTING, TaskState.TESTING):
            for task in self.task_store.list_tasks(state):
                recovered.append(self.task_store.transition(task.task_id, TaskState.BLOCKED))
        return recovered

    def execute_once(self, task_id: str, executor: ToolExecutor, call: ToolCall) -> dict:
        """Executa uma chamada única; novas tentativas exigem novo início explícito."""
        with self._lock:
            if len(self._active_task_ids) >= self.max_concurrency:
                raise RuntimeError("limite de concorrencia atingido")
            if task_id in self._active_task_ids:
                raise RuntimeError("tarefa ja esta em execucao neste worker")
            self._active_task_ids.add(task_id)
        try:
            self.begin(task_id)
            try:
                result = executor.execute(task_id, call)
            except TimeoutError:
                self.task_store.transition(task_id, TaskState.BLOCKED)
                raise
            except InterruptedError:
                raise
            except (FileNotFoundError, PermissionError, RuntimeError, OSError):
                self.fail(task_id)
                raise
            self.succeed(task_id)
            return result
        finally:
            with self._lock:
                self._active_task_ids.discard(task_id)
