#!/usr/bin/env python3
"""Gera um diagnostico somente leitura do host Bastião."""

from __future__ import annotations

import argparse
import json
import platform
import re
import shutil
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Sequence
from urllib.error import URLError
from urllib.request import urlopen


DEFAULT_TIMEOUT_SECONDS = 10
SECRET_PATTERN = re.compile(
    r"(?i)([a-z0-9_-]*(?:secret|token|password|api[_-]?key)[a-z0-9_-]*)=\S+"
)


@dataclass
class Check:
    name: str
    status: str
    detail: str


def redact(value: str) -> str:
    return SECRET_PATTERN.sub(lambda match: f"{match.group(1)}=***", value)


def run_command(command: Sequence[str], timeout: int) -> tuple[bool, str]:
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except FileNotFoundError:
        return False, f"comando indisponivel: {command[0]}"
    except subprocess.TimeoutExpired:
        return False, f"timeout apos {timeout}s"

    output = (result.stdout or result.stderr).strip()
    if result.returncode:
        return False, redact(output or f"codigo de saida {result.returncode}")
    return True, redact(output)


def command_check(name: str, command: Sequence[str], timeout: int) -> Check:
    ok, detail = run_command(command, timeout)
    return Check(name, "OK" if ok else "FALHA", detail)


def http_check(url: str, timeout: int) -> Check:
    try:
        with urlopen(url, timeout=timeout) as response:
            body = response.read().decode("utf-8", errors="replace").strip()
    except URLError as error:
        return Check("Open WebUI health", "FALHA", str(error.reason))
    except TimeoutError:
        return Check("Open WebUI health", "FALHA", f"timeout apos {timeout}s")

    return Check("Open WebUI health", "OK", redact(body))


def open_webui_url(timeout: int) -> str:
    ok, output = run_command(["tailscale", "ip", "-4"], timeout)
    if ok and output:
        return f"http://{output.splitlines()[0]}:3000/health"
    return "http://127.0.0.1:3000/health"


def directory_check(name: str, path: Path) -> Check:
    if not path.is_dir():
        return Check(name, "FALHA", f"diretorio ausente: {path}")
    try:
        usage = shutil.disk_usage(path)
    except OSError as error:
        return Check(name, "FALHA", f"nao foi possivel ler o diretorio: {error}")

    free_gib = usage.free / 1024**3
    status = "ALERTA" if free_gib < 10 else "OK"
    return Check(name, status, f"existe; espaco livre no volume: {free_gib:.1f} GiB")


def backup_check(home: Path) -> Check:
    backups = sorted(home.glob("bastiao-backup-*"), key=lambda item: item.stat().st_mtime)
    if not backups:
        return Check("Backups", "ALERTA", "nenhum diretorio bastiao-backup-* encontrado")
    latest = backups[-1]
    checksum_file = latest / "SHA256SUMS"
    status = "OK" if checksum_file.is_file() else "ALERTA"
    return Check("Backups", status, f"mais recente: {latest}; hashes: {'presentes' if checksum_file.is_file() else 'ausentes'}")


def build_checks(repo_root: Path, timeout: int, webui_url: str | None = None) -> list[Check]:
    infra_dir = repo_root / "infra" / "open-webui"
    home = repo_root.parent
    checks = [
        Check("Sistema operacional", "OK", f"{platform.system()} {platform.release()}"),
        command_check("Docker", ["docker", "--version"], timeout),
        command_check("Docker Compose", ["docker", "compose", "version"], timeout),
        command_check(
            "Containers",
            ["docker", "ps", "--format", "{{.Names}} {{.Status}} {{.Ports}}"],
            timeout,
        ),
        command_check(
            "Modelos Ollama",
            ["docker", "exec", "ollama", "ollama", "list"],
            timeout,
        ),
        command_check(
            "GPU",
            ["nvidia-smi", "--query-gpu=name,temperature.gpu,memory.used,memory.total", "--format=csv,noheader"],
            timeout,
        ),
        http_check(webui_url or open_webui_url(timeout), timeout),
        directory_check("Dados Open WebUI", infra_dir / "data"),
        directory_check("Modelos Ollama", infra_dir / "ollama"),
        backup_check(home),
    ]
    return checks


def format_report(checks: list[Check]) -> str:
    lines = ["DIAGNOSTICO OPERACIONAL DO BASTIAO", "=" * 40]
    for check in checks:
        lines.append(f"[{check.status}] {check.name}: {check.detail}")
    failures = sum(check.status == "FALHA" for check in checks)
    alerts = sum(check.status == "ALERTA" for check in checks)
    lines.extend(["=" * 40, f"Resumo: {failures} falha(s), {alerts} alerta(s)."])
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT_SECONDS)
    parser.add_argument("--json", action="store_true", dest="as_json")
    parser.add_argument("--open-webui-url", help="URL do endpoint /health do Open WebUI")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.timeout <= 0:
        raise SystemExit("--timeout deve ser maior que zero")

    checks = build_checks(args.repo_root.resolve(), args.timeout, args.open_webui_url)
    if args.as_json:
        print(json.dumps([asdict(check) for check in checks], ensure_ascii=False, indent=2))
    else:
        print(format_report(checks))
    return 1 if any(check.status == "FALHA" for check in checks) else 0


if __name__ == "__main__":
    raise SystemExit(main())
