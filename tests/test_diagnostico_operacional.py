from pathlib import Path

from scripts.diagnostico_operacional import Check, backup_check, format_report, open_webui_url, redact, run_command


def test_redact_masks_secret_values():
    assert redact("WEBUI_SECRET_KEY=private-value") == "WEBUI_SECRET_KEY=***"


def test_run_command_reports_missing_binary():
    ok, detail = run_command(["command-that-does-not-exist"], timeout=1)
    assert ok is False
    assert "indisponivel" in detail


def test_backup_check_requires_checksum_file(tmp_path: Path):
    backup = tmp_path / "bastiao-backup-20260908-214936"
    backup.mkdir()
    assert backup_check(tmp_path).status == "ALERTA"

    (backup / "SHA256SUMS").write_text("hash archive.tar.gz\n", encoding="utf-8")
    assert backup_check(tmp_path).status == "OK"


def test_open_webui_url_uses_tailscale_address(monkeypatch):
    monkeypatch.setattr(
        "scripts.diagnostico_operacional.run_command",
        lambda command, timeout: (True, "100.84.226.99"),
    )
    assert open_webui_url(timeout=1) == "http://100.84.226.99:3000/health"


def test_format_report_counts_failures_and_alerts():
    report = format_report(
        [Check("a", "OK", "ok"), Check("b", "FALHA", "no"), Check("c", "ALERTA", "watch")]
    )
    assert "Resumo: 1 falha(s), 1 alerta(s)." in report
