import json
import subprocess
import sys
from unittest.mock import patch

from agente.explorer import (
    build_report,
    detect_stack,
    github_readonly_info,
    is_safe_path,
    run_allowed_command,
)


def test_is_safe_path_blocks_sensitive_locations(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    secret = repo / ".env"
    secret.write_text("SECRET=1", encoding="utf-8")
    assert is_safe_path(repo, secret) is False

    safe = repo / "src" / "main.py"
    safe.parent.mkdir(parents=True, exist_ok=True)
    safe.write_text("print('ok')", encoding="utf-8")
    assert is_safe_path(repo, safe) is True


def test_iter_allowed_files_excludes_local_test_artifacts(tmp_path):
    from agente.explorer import iter_allowed_files

    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / ".venv-explorer").mkdir()
    (repo / ".venv-explorer" / "secret.txt").write_text("hidden", encoding="utf-8")
    (repo / ".pytest_cache").mkdir()
    (repo / ".pytest_cache" / "cache.txt").write_text("hidden", encoding="utf-8")
    (repo / ".ruff_cache").mkdir()
    (repo / ".ruff_cache" / "cache.txt").write_text("hidden", encoding="utf-8")
    (repo / "README.md").write_text("visible", encoding="utf-8")

    files = {path.relative_to(repo).as_posix() for path in iter_allowed_files(repo)}
    assert files == {"README.md"}


def test_detect_stack_recognizes_python_repo(tmp_path):
    repo = tmp_path / "python_repo"
    repo.mkdir()
    (repo / "requirements.txt").write_text("pytest\n", encoding="utf-8")
    (repo / "src").mkdir()
    (repo / "src" / "main.py").write_text("print('hello')\n", encoding="utf-8")
    assert "Python" in detect_stack(repo)


def test_build_report_includes_git_and_stack(tmp_path):
    repo = tmp_path / "git_repo"
    repo.mkdir()
    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True, text=True)
    subprocess.run(["git", "config", "user.name", "Tester"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.email", "tester@example.com"], cwd=repo, check=True)
    (repo / "README.md").write_text("Projeto de teste\n", encoding="utf-8")
    report = build_report(repo)
    assert report["status"]
    assert "README" in report["readme_summary"] or "Projeto de teste" in report["readme_summary"]
    assert isinstance(report["stack"], list)


def test_build_report_serializes_json(tmp_path):
    repo = tmp_path / "json_repo"
    repo.mkdir()
    (repo / "README.md").write_text("Repo json\n", encoding="utf-8")
    report = build_report(repo)
    json.dumps(report, ensure_ascii=False)
    assert "Repo json" in report["readme_summary"]


def test_policy_is_required_before_running_commands(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    result = run_allowed_command(repo, "python -c \"print('no')\"", [])
    assert "não autorizado" in result["error"]


def test_allowed_command_runs_inside_repository(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    command = f'"{sys.executable}" -c "print(\'ok\')"'
    result = run_allowed_command(repo, command, [command])
    assert result["returncode"] == 0
    assert result["stdout"] == "ok"


def test_github_info_is_read_only_and_parses_metadata(tmp_path):
    responses = [
        {
            "nameWithOwner": "IsraelSiq/bastiao",
            "description": "Servidor pessoal de IA local.",
            "defaultBranchRef": {"name": "main"},
            "url": "https://github.com/IsraelSiq/bastiao",
        },
        [{"number": 1, "title": "RAG", "state": "OPEN", "url": "https://example/issues/1"}],
        [{"number": 2, "title": "Explorer", "state": "OPEN", "url": "https://example/pulls/2"}],
    ]
    completed = [
        subprocess.CompletedProcess(
            args=["gh"],
            returncode=0,
            stdout=json.dumps(response),
            stderr="",
        )
        for response in responses
    ]
    with patch("agente.explorer.subprocess.run", side_effect=completed) as run:
        result = github_readonly_info(tmp_path)

    assert result["available"] is True
    assert result["nameWithOwner"] == "IsraelSiq/bastiao"
    assert result["issues"][0]["number"] == 1
    assert result["pull_requests"][0]["number"] == 2
    for call in run.call_args_list:
        command = call.args[0]
        assert command[0:2] in (["gh", "repo"], ["gh", "issue"], ["gh", "pr"])
        assert not any(action in command for action in ("create", "delete", "edit", "merge", "close"))


def test_github_info_reports_cli_failure(tmp_path):
    completed = subprocess.CompletedProcess(
        args=["gh"],
        returncode=1,
        stdout="",
        stderr="not authenticated",
    )
    with patch("agente.explorer.subprocess.run", return_value=completed):
        result = github_readonly_info(tmp_path)

    assert result == {"available": False, "error": "not authenticated"}
