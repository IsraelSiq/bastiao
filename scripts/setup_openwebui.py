#!/usr/bin/env python3
"""
Script de validacao e apoio a configuracao do Open WebUI no Bastiao.

O que ele faz:
- Le rag/openwebui-config.json.
- Valida se as pastas e arquivos das bases de conhecimento existem.
- Verifica se o modelo de embeddings esta instalado no Ollama.
- Gera um relatorio em texto com:
  - O que esta OK.
  - O que falta fazer manualmente no Open WebUI.

Este script NAO configura o Open WebUI automaticamente (nao ha API oficial estavel).
Ele serve como guia estruturado e validador local.
"""

import json
import argparse
import os
import subprocess
from pathlib import Path
from typing import Any


EXIT_VALIDATION_ERROR = 1
EXIT_CONFIG_ERROR = 2
DOCKER_TIMEOUT_SECONDS = 10


def load_config(config_path: Path) -> dict[str, Any]:
    try:
        with config_path.open(encoding="utf-8") as config_file:
            config = json.load(config_file)
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"nao foi possivel ler a configuracao: {error}") from error
    if not isinstance(config, dict):
        raise ValueError("a configuracao deve conter um objeto JSON")
    return config


def resolve_base_path(base: dict[str, Any], repo_root: Path) -> Path:
    relative_path = base.get("caminho_relativo")
    if isinstance(relative_path, str) and relative_path:
        return (repo_root / relative_path).resolve()

    server_path = base.get("caminho_servidor")
    if not isinstance(server_path, str) or not server_path:
        raise ValueError("base sem caminho_relativo ou caminho_servidor")
    return Path(server_path).expanduser()


def check_files(base_path: Path, files: list[str]) -> list[str]:
    missing = []
    for relative_file in files:
        if not (base_path / relative_file).is_file():
            missing.append(relative_file)
    return missing


def check_ollama_model(model: str, timeout: int) -> tuple[bool, str]:
    try:
        result = subprocess.run(
            ["docker", "exec", "ollama", "ollama", "list"],
            capture_output=True,
            text=True,
            check=True,
            timeout=timeout,
        )
    except FileNotFoundError as error:
        return False, f"Docker nao esta instalado ou nao esta no PATH: {error}"
    except subprocess.TimeoutExpired:
        return False, f"Docker nao respondeu em {timeout}s"
    except subprocess.CalledProcessError as error:
        details = error.stderr.strip() or "sem detalhes adicionais"
        return False, f"falha ao consultar o container ollama: {details}"

    installed_models = {
        line.split(maxsplit=1)[0]
        for line in result.stdout.splitlines()
        if line.strip()
    }
    if model in installed_models:
        return True, f"modelo {model} encontrado"
    return False, f"modelo exato {model} nao encontrado"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        type=Path,
        help="caminho do JSON de configuracao (padrao: rag/openwebui-config.json)",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        help="raiz do repositorio a validar (ou BASTIAO_REPO_ROOT)",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=DOCKER_TIMEOUT_SECONDS,
        help=f"timeout da consulta ao Docker em segundos (padrao: {DOCKER_TIMEOUT_SECONDS})",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="mantido para uso em CI; falhas de validacao sempre retornam codigo nao-zero",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    configured_root = args.repo_root or os.environ.get("BASTIAO_REPO_ROOT")
    base_repo = (
        Path(configured_root)
        if configured_root
        else Path(__file__).resolve().parent.parent
    ).resolve()
    config_path = (args.config or base_repo / "rag" / "openwebui-config.json").resolve()

    if not config_path.exists():
        print(f"ERRO: arquivo de configuracao nao encontrado: {config_path}")
        return EXIT_CONFIG_ERROR

    try:
        config = load_config(config_path)
    except ValueError as error:
        print(f"ERRO: {error}")
        return EXIT_CONFIG_ERROR

    print("=" * 60)
    print("VALIDACAO DAS BASES DE CONHECIMENTO E CONFIGURACOES")
    print("=" * 60)
    validation_failed = False

    # Validar bases de conhecimento
    knowledge_bases = config.get("knowledge_bases", [])
    print("\n1. BASES DE CONHECIMENTO\n")

    for kb in knowledge_bases:
        nome = kb.get("nome", "<sem nome>")
        caminho = resolve_base_path(kb, base_repo)
        arquivos = kb.get("arquivos", [])
        projetos = kb.get("projetos", [])

        print(f"Base: {nome}")
        print(f"  Caminho esperado: {caminho}")

        if not caminho.is_dir():
            print(f"  [!] CAMINHO NAO ENCONTRADO: {caminho}")
            validation_failed = True
        else:
            print(f"  [OK] Caminho existe.")

        if arquivos:
            missing = check_files(caminho, arquivos)
            if missing:
                print(f"  [!] Arquivos ausentes: {missing}")
                validation_failed = True
            else:
                print(f"  [OK] Todos os arquivos principais existem.")

        if projetos:
            for proj in projetos:
                proj_nome = proj.get("nome", "<sem nome>")
                proj_arquivos = proj.get("arquivos", [])
                proj_path = caminho / proj_nome
                print(f"  Projeto: {proj_nome}")
                print(f"    Caminho esperado: {proj_path}")
                if not proj_path.is_dir():
                    print(f"    [!] CAMINHO DO PROJETO NAO ENCONTRADO: {proj_path}")
                    validation_failed = True
                else:
                    print(f"    [OK] Caminho do projeto existe.")
                    missing_proj = check_files(proj_path, proj_arquivos)
                    if missing_proj:
                        print(f"    [!] Arquivos ausentes no projeto: {missing_proj}")
                        validation_failed = True
                    else:
                        print(f"    [OK] Arquivos do projeto existem.")

        print()

    # Validar embeddings
    embeddings = config.get("embeddings", {})
    print("2. EMBEDDINGS (OLLAMA)\n")

    modelo_emb = embeddings.get("modelo", "")
    base_url = embeddings.get("base_url", "")
    provider = embeddings.get("provider", "")

    print(f"Provider: {provider}")
    print(f"Base URL: {base_url}")
    print(f"Modelo: {modelo_emb}")

    if not modelo_emb:
        print("[!] Modelo de embeddings nao configurado.")
        validation_failed = True
    else:
        model_ok, model_message = check_ollama_model(modelo_emb, args.timeout)
        if model_ok:
            print(f"[OK] {model_message}.")
        else:
            print(f"[!] {model_message}.")
            if "modelo exato" in model_message:
                print("    Para instalar, rode no servidor:")
                print(f"    docker exec ollama ollama pull {modelo_emb}")
            validation_failed = True

    print()

    # Resumo e proximos passos manuais
    print("3. PROXIMOS PASSOS (MANUAIS, NO OPEN WEBUI)\n")
    instrucoes = config.get("instrucoes_configuracao", {}).get("passos", [])
    for passo in instrucoes:
        print(f"- {passo}")

    print()
    print("4. SUGESTOES DE TESTE DE RAG\n")
    testes = config.get("instrucoes_configuracao", {}).get("teste_rag_sugestoes", [])
    for t in testes:
        print(f"- {t}")

    print()
    print("=" * 60)
    print("FIM DO RELATORIO")
    print("=" * 60)
    return EXIT_VALIDATION_ERROR if validation_failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
