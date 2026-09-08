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

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


def load_config(config_path: str) -> dict:
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def resolve_path(value: str, repo_root: Path) -> str:
    candidate = value.strip()
    if not candidate:
        return str(repo_root)
    path = Path(candidate)
    if path.is_absolute():
        return str(path)
    return str((repo_root / path).resolve())


def check_path(path: str) -> bool:
    return Path(path).exists()


def check_files(base_path: str, files: list[str]) -> list[str]:
    missing = []
    base = Path(base_path)
    for file in files:
        full = base / file
        if not full.is_file():
            missing.append(file)
    return missing


def check_ollama_model(model: str) -> bool:
    try:
        result = subprocess.run(
            ["docker", "exec", "ollama", "ollama", "list"],
            capture_output=True,
            text=True,
            check=True,
            timeout=20,
        )
        installed = {line.strip().split()[0] for line in result.stdout.splitlines() if line.strip()}
        model_name = model.split(":", 1)[0]
        for name in installed:
            if name == model or name == model_name:
                return True
        return False
    except (FileNotFoundError, subprocess.TimeoutExpired, subprocess.CalledProcessError):
        return False


def normalize_config(config: dict, repo_root: Path) -> dict:
    for kb in config.get("knowledge_bases", []):
        caminho = kb.get("caminho_servidor", "")
        if caminho:
            kb["caminho_servidor"] = resolve_path(caminho, repo_root)
        for proj in kb.get("projetos", []):
            proj_nome = proj.get("nome", "")
            if proj_nome and caminho:
                proj["caminho_servidor"] = str((Path(kb["caminho_servidor"]) / proj_nome).resolve())
    return config


def main():
    parser = argparse.ArgumentParser(description="Valida configuracao do Open WebUI e do RAG do Bastiao.")
    parser.add_argument("--config", type=str, help="Caminho do arquivo de configuracao JSON.")
    args = parser.parse_args()

    base_repo = Path(__file__).resolve().parent.parent
    config_path = Path(args.config) if args.config else base_repo / "rag" / "openwebui-config.json"

    if not config_path.exists():
        print(f"ERRO: arquivo de configuracao nao encontrado: {config_path}")
        return 1

    config = load_config(str(config_path))
    config = normalize_config(config, base_repo)

    print("=" * 60)
    print("VALIDACAO DAS BASES DE CONHECIMENTO E CONFIGURACOES")
    print(f"Repositório: {base_repo}")
    print(f"Configuração: {config_path}")
    print("=" * 60)

    failed = False
    knowledge_bases = config.get("knowledge_bases", [])
    print("\n1. BASES DE CONHECIMENTO\n")

    for kb in knowledge_bases:
        nome = kb.get("nome", "<sem nome>")
        caminho = kb.get("caminho_servidor", "")
        arquivos = kb.get("arquivos", [])
        projetos = kb.get("projetos", [])

        print(f"Base: {nome}")
        print(f"  Caminho esperado: {caminho}")

        if not check_path(caminho):
            print(f"  [!] CAMINHO NAO ENCONTRADO: {caminho}")
            failed = True
        else:
            print(f"  [OK] Caminho existe.")

        if arquivos:
            missing = check_files(caminho, arquivos)
            if missing:
                print(f"  [!] Arquivos ausentes: {missing}")
                failed = True
            else:
                print(f"  [OK] Todos os arquivos principais existem.")

        if projetos:
            for proj in projetos:
                proj_nome = proj.get("nome", "<sem nome>")
                proj_arquivos = proj.get("arquivos", [])
                proj_path = proj.get("caminho_servidor", str((Path(caminho) / proj_nome).resolve()))
                print(f"  Projeto: {proj_nome}")
                print(f"    Caminho esperado: {proj_path}")
                if not check_path(proj_path):
                    print(f"    [!] CAMINHO DO PROJETO NAO ENCONTRADO: {proj_path}")
                    failed = True
                else:
                    print(f"    [OK] Caminho do projeto existe.")
                    missing_proj = check_files(proj_path, proj_arquivos)
                    if missing_proj:
                        print(f"    [!] Arquivos ausentes no projeto: {missing_proj}")
                        failed = True
                    else:
                        print(f"    [OK] Arquivos do projeto existem.")

        print()

    embeddings = config.get("embeddings", {})
    print("2. EMBEDDINGS (OLLAMA)\n")

    modelo_emb = embeddings.get("modelo", "")
    base_url = embeddings.get("base_url", "")
    provider = embeddings.get("provider", "")

    print(f"Provider: {provider}")
    print(f"Base URL: {base_url}")
    print(f"Modelo: {modelo_emb}")

    if modelo_emb and check_ollama_model(modelo_emb):
        print(f"[OK] Modelo de embeddings instalado no Ollama.")
    else:
        print(f"[!] Modelo de embeddings NAO encontrado no Ollama.")
        print(f"    Para instalar, rode no servidor:")
        print(f"    docker exec ollama ollama pull {modelo_emb}")
        failed = True

    print()

    print("3. PROXIMOS PASSOS (MANUAIS, NO OPEN WEBUI)\n")
    instrucoes = config.get("instrucoes_configuracao", {}).get("passos", [])
    for i, passo in enumerate(instrucoes, start=1):
        print(f"{i}. {passo}")

    print()
    print("4. SUGESTOES DE TESTE DE RAG\n")
    testes = config.get("instrucoes_configuracao", {}).get("teste_rag_sugestoes", [])
    for t in testes:
        print(f"- {t}")

    print()
    print("=" * 60)
    print("FIM DO RELATORIO")
    print("=" * 60)

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
