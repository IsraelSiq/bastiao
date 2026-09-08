#!/usr/bin/env python3
"""Bastião Explorer: leitura segura de repositórios em modo somente leitura."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

FORBIDDEN_SEGMENTS = {
    ".git",
    ".venv",
    "venv",
    ".venv-explorer",
    ".pytest_cache",
    ".ruff_cache",
    "node_modules",
    "__pycache__",
    "secrets",
    "data",
    "ollama",
    "models",
    "vector-store",
    "chroma",
    "qdrant",
    "backups",
    "logs",
    "reports",
    "dist",
    "build",
    "target",
    ".idea",
    ".vscode",
}

def is_safe_path(base_dir: Path, target: Path) -> bool:
    try:
        target.relative_to(base_dir)
    except ValueError:
        return False

    lower_parts = {part.lower() for part in target.parts}
    if lower_parts & FORBIDDEN_SEGMENTS:
        return False

    name = target.name.lower()
    if name.startswith(".env"):
        return False
    if any(name.endswith(suffix) for suffix in (".pem", ".key", ".crt", ".pfx", ".p12", ".sqlite", ".db")):
        return False
    if target.is_symlink():
        try:
            return is_safe_path(base_dir, target.resolve())
        except OSError:
            return False
    return True


def iter_allowed_files(base_dir: Path) -> list[Path]:
    allowed: list[Path] = []
    for current, dirs, files in os.walk(base_dir):
        current_path = Path(current)
        dirs[:] = [
            d
            for d in dirs
            if d not in {
                ".git",
                ".hg",
                ".svn",
                ".venv",
                ".venv-explorer",
                ".pytest_cache",
                ".ruff_cache",
                "venv",
                "node_modules",
                "__pycache__",
            }
            and d.lower() not in FORBIDDEN_SEGMENTS
        ]
        for filename in files:
            file_path = current_path / filename
            if is_safe_path(base_dir, file_path):
                allowed.append(file_path)
    return sorted(allowed)


def read_text_file(path: Path, limit: int = 8000) -> str:
    if not path.is_file():
        return ""
    try:
        content = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        try:
            content = path.read_text(encoding="latin-1")
        except Exception:
            return ""
    return content[:limit]


def detect_stack(repo_root: Path) -> list[str]:
    stack: list[str] = []
    files_present = {p.name for p in repo_root.iterdir() if p.is_file()}

    if "pyproject.toml" in files_present or "requirements.txt" in files_present:
        stack.append("Python")
    if "package.json" in files_present:
        stack.append("Node.js")
    if "go.mod" in files_present:
        stack.append("Go")
    if "Cargo.toml" in files_present:
        stack.append("Rust")
    if "pom.xml" in files_present:
        stack.append("Java/Maven")
    if "Dockerfile" in files_present or "docker-compose.yml" in files_present or "compose.yaml" in files_present:
        stack.append("Docker")
    if not stack:
        stack.append("Não identificado")
    return stack


def detect_test_commands(repo_root: Path) -> list[str]:
    commands: list[str] = []
    markers = {
        "pytest": ["pytest.ini", "tox.ini", "pyproject.toml", "requirements.txt"],
        "npm": ["package.json"],
        "cargo": ["Cargo.toml"],
        "go": ["go.mod"],
    }

    for tool, marker_files in markers.items():
        if any((repo_root / name).exists() for name in marker_files):
            if tool == "pytest":
                commands.append("python -m pytest -q")
            elif tool == "npm":
                commands.append("npm test -- --runInBand")
            elif tool == "cargo":
                commands.append("cargo test")
            elif tool == "go":
                commands.append("go test ./...")

    if not commands:
        commands.append("Nenhum comando de teste automatizado detectado")
    return commands


def load_policy(repo_root: Path, policy_path: Path | None = None) -> dict[str, Any]:
    path = policy_path or repo_root / ".bastiao" / "explorer-policy.json"
    if not path.is_file():
        return {"test_commands": []}
    with path.open(encoding="utf-8") as policy_file:
        policy = json.load(policy_file)
    commands = policy.get("test_commands", [])
    if not isinstance(commands, list) or not all(isinstance(command, str) for command in commands):
        raise ValueError("test_commands deve ser uma lista de comandos textuais")
    return {"test_commands": commands}


def run_allowed_command(
    repo_root: Path,
    command: str,
    allowed_commands: list[str],
    timeout: int = 120,
) -> dict[str, Any]:
    if command not in allowed_commands:
        return {"error": "Comando não autorizado pela política do projeto.", "command": command}

    try:
        completed = subprocess.run(
            command,
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            shell=True,
            check=False,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as exc:
        return {"command": command, "error": f"Comando excedeu o timeout de {timeout}s.", "stdout": exc.stdout or "", "stderr": exc.stderr or ""}
    except OSError as exc:
        return {"command": command, "error": str(exc)}

    return {
        "command": command,
        "returncode": completed.returncode,
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
    }


def git_command(repo_root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(repo_root), *args],
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
    )


def git_status(repo_root: Path) -> tuple[str, str]:
    result = git_command(repo_root, "status", "--short", "--branch")
    if result.returncode == 0:
        return result.stdout.strip(), result.stderr.strip()
    return "Git não disponível ou repositório sem .git.", result.stderr.strip()


def git_log(repo_root: Path, limit: int = 5) -> str:
    result = git_command(repo_root, "log", "--oneline", "-n", str(limit))
    if result.returncode == 0:
        return result.stdout.strip()
    return "Sem histórico git disponível."


def _gh_json(repo_root: Path, *args: str) -> dict[str, Any] | list[Any]:
    result = subprocess.run(
        ["gh", *args],
        cwd=str(repo_root),
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "Falha na consulta GitHub.")
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError("A resposta do GitHub não é um JSON válido.") from exc


def github_readonly_info(repo_root: Path) -> dict[str, Any]:
    """Obtém metadados, issues e PRs sem executar operações de escrita."""
    try:
        metadata = _gh_json(
            repo_root,
            "repo",
            "view",
            "--json",
            "nameWithOwner,description,defaultBranchRef,url",
        )
        issues = _gh_json(
            repo_root,
            "issue",
            "list",
            "--state",
            "all",
            "--limit",
            "20",
            "--json",
            "number,title,state,url",
        )
        pull_requests = _gh_json(
            repo_root,
            "pr",
            "list",
            "--state",
            "all",
            "--limit",
            "20",
            "--json",
            "number,title,state,url",
        )
    except (FileNotFoundError, RuntimeError, subprocess.TimeoutExpired) as exc:
        return {"available": False, "error": str(exc)}

    if not isinstance(metadata, dict):
        return {"available": False, "error": "Metadados GitHub em formato inesperado."}
    return {
        "available": True,
        **metadata,
        "issues": issues if isinstance(issues, list) else [],
        "pull_requests": pull_requests if isinstance(pull_requests, list) else [],
    }


def safe_readme_summary(repo_root: Path) -> str:
    candidates = ["README.md", "README.MD", "readme.md", "README.rst"]
    for name in candidates:
        path = repo_root / name
        if path.exists() and is_safe_path(repo_root, path):
            content = read_text_file(path, limit=2000)
            return content.strip() or "README encontrado, mas vazio."
    return "README não encontrado neste repositório."


def build_report(
    repo_root: Path,
    max_files: int = 25,
    policy_path: Path | None = None,
    include_github: bool = False,
) -> dict:
    status_output, status_err = git_status(repo_root)
    files = iter_allowed_files(repo_root)
    truncated = [str(p.relative_to(repo_root)) for p in files[:max_files]]
    policy = load_policy(repo_root, policy_path)

    report = {
        "root": str(repo_root),
        "status": status_output,
        "git_error": status_err,
        "stack": detect_stack(repo_root),
        "test_commands": detect_test_commands(repo_root),
        "policy_test_commands": policy["test_commands"],
        "allowed_files": truncated,
        "readme_summary": safe_readme_summary(repo_root),
        "git_log": git_log(repo_root),
        "total_allowed_files": len(files),
    }
    if include_github:
        report["github"] = github_readonly_info(repo_root)
    return report


def run_readonly_checks(
    repo_root: Path,
    policy_path: Path | None = None,
    include_github: bool = False,
) -> dict:
    report = build_report(
        repo_root,
        policy_path=policy_path,
        include_github=include_github,
    )
    allowed_commands = report["policy_test_commands"]
    if not allowed_commands:
        report["readonly_test_result"] = "Nenhum teste automatizado detectado; execução de validação pulada com segurança."
        return report

    report["readonly_test_result"] = [
        run_allowed_command(repo_root, command, allowed_commands)
        for command in allowed_commands
    ]
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Explorer seguro em modo somente leitura.")
    parser.add_argument("repo", nargs="?", default=".", help="Caminho do repositório alvo")
    parser.add_argument("--json", action="store_true", help="Saída em JSON")
    parser.add_argument("--policy", type=str, help="Caminho da política de comandos do projeto")
    parser.add_argument(
        "--github",
        action="store_true",
        help="Consultar metadados do repositório GitHub em modo somente leitura",
    )
    args = parser.parse_args()

    repo_root = (Path(args.repo)).resolve()
    if not repo_root.exists():
        print(f"ERRO: caminho não existe: {repo_root}", file=sys.stderr)
        return 2

    if not repo_root.is_dir():
        print(f"ERRO: caminho não é um diretório: {repo_root}", file=sys.stderr)
        return 2

    policy_path = Path(args.policy).resolve() if args.policy else None
    report = run_readonly_checks(
        repo_root,
        policy_path=policy_path,
        include_github=args.github,
    )
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return 0

    print(f"Bastião Explorer — relatório de leitura segura")
    print(f"Repositório: {repo_root}")
    print("=" * 80)
    print("Status Git:")
    print(report["status"] or "Nenhuma saída do git status.")
    print("\nStack detectado:")
    print(", ".join(report["stack"]))
    print("\nComandos de teste detectados:")
    for command in report["test_commands"]:
        print(f"- {command}")
    print("\nArquivos permitidos (até 25):")
    for file in report["allowed_files"]:
        print(f"- {file}")
    print("\nResumo do README:")
    print(report["readme_summary"][:900])
    print("\nÚltimos commits:")
    print(report["git_log"] or "Sem log disponível.")
    if args.github:
        print("\nMetadados GitHub:")
        print(json.dumps(report["github"], indent=2, ensure_ascii=False))
    print("\nResultado de validação somente leitura:")
    if isinstance(report["readonly_test_result"], dict):
        print(json.dumps(report["readonly_test_result"], indent=2, ensure_ascii=False))
    else:
        print(report["readonly_test_result"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
