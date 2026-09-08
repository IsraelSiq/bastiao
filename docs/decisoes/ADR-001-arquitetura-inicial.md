# ADR-001: Arquitetura inicial local-first

- Status: aceito
- Data: 2026-09-07

## Contexto

O projeto Bastião precisa executar modelos locais, ser acessível remotamente sem exposição pública direta e crescer para RAG, programação assistida e automação supervisionada.

## Decisão

Adotar Ubuntu Server 26.04 LTS como host, Tailscale para acesso remoto privado, Docker Compose para serviços, Ollama para execução de modelos locais e Open WebUI como interface.

Modelos iniciais:

- `qwen3:8b` como modelo Core.
- `qwen2.5-coder:7b` como especialista em desenvolvimento.
- `llama3.2:3b` para tarefas rápidas.
- `sentence-transformers/all-MiniLM-L6-v2` no Open WebUI para embeddings/RAG.
- `nomic-embed-text:latest` permanece instalado no Ollama como alternativa, mas nao e usado pelo provider atual.

A GPU NVIDIA GTX 1660 Ti será disponibilizada ao container Ollama via NVIDIA Container Toolkit.

## Consequências

- Modelos e dados permanecem no host quando não é necessária uma integração externa.
- A API do Ollama permanece apenas na rede Docker.
- Open WebUI é acessado pela porta 3000 em rede privada.
- A automação futura deve operar em workspaces isolados, com Git, testes e revisão humana antes de commit/push.
- O repositório GitHub contém somente documentação e exemplos sanitizados.
