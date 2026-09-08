import sys
from datetime import timedelta
from pathlib import Path
from subprocess import run

import pytest

from agente.autorizacao import Action, Approval, AuditLog, utc_now
from agente.builder import Builder, BuilderPolicy, is_writable_path, workspace_for


def approved(task_id: str, action: Action, workspace: Path) -> Approval:
    return Approval(task_id, action, workspace, "tester", utc_now() + timedelta(minutes=10))


def git_repo(path: Path) -> None:
    run(["git", "init"], cwd=path, check=True, capture_output=True, text=True)
    run(["git", "config", "user.name", "Tester"], cwd=path, check=True)
    run(["git", "config", "user.email", "tester@example.com"], cwd=path, check=True)
    (path / "README.md").write_text("base\n", encoding="utf-8")
    run(["git", "add", "README.md"], cwd=path, check=True)
    run(["git", "commit", "-m", "initial"], cwd=path, check=True, capture_output=True, text=True)


def test_workspace_id_cannot_escape_root(tmp_path: Path):
    with pytest.raises(ValueError):
        workspace_for(tmp_path, "../outside")


def test_write_rejects_sensitive_and_outside_paths(tmp_path: Path):
    workspace = tmp_path / "workspaces" / "task-1"
    workspace.mkdir(parents=True)
    assert is_writable_path(workspace, Path(".env")) is False
    assert is_writable_path(workspace, Path("../outside.txt")) is False
    assert is_writable_path(workspace, Path("src/main.py")) is True


def test_create_workspace_requires_explicit_approval(tmp_path: Path):
    source = tmp_path / "source"
    source.mkdir()
    git_repo(source)
    builder = Builder(tmp_path / "workspaces", AuditLog(tmp_path / "audit.jsonl"))
    with pytest.raises(PermissionError, match="aprovacao"):
        builder.create_workspace("task-1", source, None)


def test_builder_writes_runs_policy_and_reports_diff(tmp_path: Path):
    source = tmp_path / "source"
    source.mkdir()
    git_repo(source)
    root = tmp_path / "workspaces"
    workspace = workspace_for(root, "task-1")
    builder = Builder(root, AuditLog(tmp_path / "audit.jsonl"))
    builder.create_workspace("task-1", source, approved("task-1", Action.EDIT, workspace))
    builder.write_text("task-1", workspace, Path("src/main.py"), "print('ok')\n", approved("task-1", Action.EDIT, workspace))

    command = f'"{sys.executable}" -c "print(\'validated\')"'
    result = builder.run_command("task-1", workspace, command, BuilderPolicy((command,), (), ()))
    report = builder.diff_report("task-1", workspace)

    assert result["stdout"] == "validated"
    assert "src/" in report["status"]
    assert report["untracked"] == "src/main.py"
    assert report["diff"] == ""
    builder.commit("task-1", workspace, "add main", approved("task-1", Action.COMMIT, workspace))
    log = run(["git", "log", "-1", "--format=%s"], cwd=workspace, check=True, capture_output=True, text=True)
    assert log.stdout.strip() == "add main"


def test_builder_rejects_undeclared_command(tmp_path: Path):
    workspace = tmp_path / "workspaces" / "task-1"
    workspace.mkdir(parents=True)
    builder = Builder(tmp_path / "workspaces", AuditLog(tmp_path / "audit.jsonl"))
    with pytest.raises(PermissionError, match="nao autorizado"):
        builder.run_command("task-1", workspace, "echo unsafe", BuilderPolicy((), (), ()))


def test_builder_rejects_commit_without_matching_approval(tmp_path: Path):
    source = tmp_path / "source"
    source.mkdir()
    git_repo(source)
    root = tmp_path / "workspaces"
    workspace = workspace_for(root, "task-1")
    builder = Builder(root, AuditLog(tmp_path / "audit.jsonl"))
    builder.create_workspace("task-1", source, approved("task-1", Action.EDIT, workspace))

    with pytest.raises(PermissionError, match="aprovacao"):
        builder.commit("task-1", workspace, "must not commit", None)
