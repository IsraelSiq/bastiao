"""Builder v0.1: alterações controladas em workspaces Git isolados."""

from __future__ import annotations

import json
import re
import shlex
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from agente.autorizacao import Action, Approval, AuditLog, AuthorizationRequest, is_authorized

TASK_ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]{0,62}$")
FORBIDDEN_PARTS = {".git", ".env", "data", "secrets", "logs", "backups", ".venv", "venv", "node_modules"}
FORBIDDEN_SUFFIXES = (".pem", ".key", ".crt", ".pfx", ".p12", ".sqlite", ".db")


@dataclass(frozen=True)
class BuilderPolicy:
    test_commands: tuple[str, ...]
    lint_commands: tuple[str, ...]
    build_commands: tuple[str, ...]

    @property
    def allowed_commands(self) -> tuple[str, ...]:
        return self.test_commands + self.lint_commands + self.build_commands


def load_policy(policy_path: Path) -> BuilderPolicy:
    with policy_path.open(encoding="utf-8") as policy_file:
        raw_policy = json.load(policy_file)
    if not isinstance(raw_policy, dict):
        raise ValueError("a politica do Builder deve ser um objeto JSON")

    sections: dict[str, tuple[str, ...]] = {}
    for name in ("test_commands", "lint_commands", "build_commands"):
        commands = raw_policy.get(name, [])
        if not isinstance(commands, list) or not all(isinstance(command, str) and command.strip() for command in commands):
            raise ValueError(f"{name} deve ser uma lista de comandos nao vazios")
        sections[name] = tuple(commands)
    return BuilderPolicy(**sections)


def workspace_for(workspace_root: Path, task_id: str) -> Path:
    if not TASK_ID_PATTERN.fullmatch(task_id):
        raise ValueError("task_id deve conter apenas letras minusculas, numeros e hifens")
    root = workspace_root.resolve()
    workspace = (root / task_id).resolve()
    try:
        workspace.relative_to(root)
    except ValueError as error:
        raise ValueError("workspace fora da raiz permitida") from error
    return workspace


def is_writable_path(workspace: Path, relative_path: Path) -> bool:
    if relative_path.is_absolute():
        return False
    candidate = (workspace / relative_path).resolve()
    try:
        candidate.relative_to(workspace.resolve())
    except ValueError:
        return False
    lowered_parts = {part.lower() for part in relative_path.parts}
    if lowered_parts & FORBIDDEN_PARTS:
        return False
    name = relative_path.name.lower()
    return not name.startswith(".env") and not name.endswith(FORBIDDEN_SUFFIXES)


class Builder:
    """Executa operações locais, sempre mediante política e autorização correspondente."""

    def __init__(self, workspace_root: Path, audit_log: AuditLog) -> None:
        self.workspace_root = workspace_root.resolve()
        self.audit_log = audit_log

    def create_workspace(
        self,
        task_id: str,
        source_repo: Path,
        approval: Approval | None,
    ) -> Path:
        workspace = workspace_for(self.workspace_root, task_id)
        self._authorize(task_id, Action.EDIT, workspace, approval)
        if workspace.exists():
            raise FileExistsError("workspace da tarefa ja existe")
        self._run_git(source_repo.resolve(), "rev-parse", "--is-inside-work-tree")
        self.workspace_root.mkdir(parents=True, exist_ok=True)
        self._run_git(source_repo.resolve(), "worktree", "add", "-b", f"builder/{task_id}", str(workspace), "HEAD")
        self.audit_log.append("workspace_created", task_id, f"workspace={workspace}")
        return workspace

    def write_text(
        self,
        task_id: str,
        workspace: Path,
        relative_path: Path,
        content: str,
        approval: Approval | None,
    ) -> None:
        self._authorize(task_id, Action.EDIT, workspace, approval)
        if not is_writable_path(workspace, relative_path):
            raise PermissionError("caminho de escrita fora da politica do Builder")
        target = (workspace / relative_path).resolve()
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        self.audit_log.append("file_written", task_id, f"path={relative_path.as_posix()}")

    def run_command(self, task_id: str, workspace: Path, command: str, policy: BuilderPolicy, timeout: int = 120) -> dict[str, Any]:
        self._assert_workspace(workspace)
        if command not in policy.allowed_commands:
            raise PermissionError("comando nao autorizado pela politica do Builder")
        if timeout <= 0:
            raise ValueError("timeout deve ser positivo")
        try:
            completed = subprocess.run(
                shlex.split(command),
                cwd=workspace,
                capture_output=True,
                text=True,
                check=False,
                timeout=timeout,
            )
        except subprocess.TimeoutExpired as error:
            self.audit_log.append("command_timed_out", task_id, f"command={command}")
            return {"command": command, "error": f"comando excedeu timeout de {timeout}s"}
        self.audit_log.append("command_finished", task_id, f"command={command}; returncode={completed.returncode}")
        return {
            "command": command,
            "returncode": completed.returncode,
            "stdout": completed.stdout.strip(),
            "stderr": completed.stderr.strip(),
        }

    def diff_report(self, task_id: str, workspace: Path) -> dict[str, str]:
        self._assert_workspace(workspace)
        report = {
            "status": self._run_git(workspace, "status", "--short").stdout.strip(),
            "diff": self._run_git(workspace, "diff", "--no-ext-diff", "--").stdout.strip(),
            "untracked": self._run_git(workspace, "ls-files", "--others", "--exclude-standard").stdout.strip(),
        }
        self.audit_log.append("diff_reported", task_id, "git diff generated")
        return report

    def commit(self, task_id: str, workspace: Path, message: str, approval: Approval | None) -> None:
        self._authorize(task_id, Action.COMMIT, workspace, approval)
        if not message.strip():
            raise ValueError("mensagem de commit obrigatoria")
        self._run_git(workspace, "add", "--all")
        self._run_git(workspace, "commit", "-m", message)
        self.audit_log.append("commit_created", task_id, "commit created")

    def push(self, task_id: str, workspace: Path, approval: Approval | None) -> None:
        self._authorize(task_id, Action.PUSH, workspace, approval)
        branch = self._run_git(workspace, "branch", "--show-current").stdout.strip()
        if not branch:
            raise RuntimeError("workspace sem branch ativa")
        self._run_git(workspace, "push", "origin", branch)
        self.audit_log.append("push_completed", task_id, f"branch={branch}")

    def _authorize(self, task_id: str, action: Action, workspace: Path, approval: Approval | None) -> None:
        allowed, reason = is_authorized(AuthorizationRequest(task_id, action, workspace), approval)
        self.audit_log.append("authorization_checked", task_id, f"action={action}; allowed={allowed}; reason={reason}")
        if not allowed:
            raise PermissionError(reason)
        self._assert_workspace(workspace)

    def _assert_workspace(self, workspace: Path) -> None:
        resolved = workspace.resolve()
        try:
            resolved.relative_to(self.workspace_root)
        except ValueError as error:
            raise PermissionError("workspace fora da raiz permitida") from error

    @staticmethod
    def _run_git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
        completed = subprocess.run(
            ["git", "-C", str(repo), *args],
            capture_output=True,
            text=True,
            check=False,
            timeout=30,
        )
        if completed.returncode:
            raise RuntimeError(completed.stderr.strip() or "comando Git falhou")
        return completed
