"""Adaptadores seguros de filesystem e Git para workspaces de tarefas."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

from agente.explorer import is_safe_path, read_text_file


def read_workspace_file(workspace: str, path: str) -> dict[str, Any]:
    root = Path(workspace).resolve()
    target = (root / path).resolve()
    if not is_safe_path(root, target):
        raise PermissionError("arquivo fora da politica de leitura")
    content = read_text_file(target)
    if not content and not target.is_file():
        raise FileNotFoundError("arquivo permitido nao encontrado")
    return {"path": str(target.relative_to(root)), "content": content}


def git_readonly(workspace: str, operation: str) -> dict[str, str]:
    allowed = {
        "status": ("status", "--short", "--branch"),
        "log": ("log", "--oneline", "-n", "10"),
    }
    if operation not in allowed:
        raise PermissionError("operacao Git nao autorizada")
    completed = subprocess.run(
        ["git", "-C", workspace, *allowed[operation]],
        capture_output=True,
        text=True,
        check=False,
        timeout=15,
    )
    if completed.returncode:
        raise RuntimeError(completed.stderr.strip() or "consulta Git falhou")
    return {"operation": operation, "output": completed.stdout.strip()}
