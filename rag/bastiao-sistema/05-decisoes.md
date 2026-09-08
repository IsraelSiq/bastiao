# Bastiao – Decisoes

## ADR-001: Arquitetura inicial local-first

- **Status:** aceito
- **Data:** 2026-09-07

### Contexto

O projeto Bastiao precisa executar modelos locais, ser acessivel remotamente sem exposição publica direta e crescer para RAG, programação assistida e automação supervisionada.

### Decisao

Adotar Ubuntu Server 26.04 LTS como host, Tailscale para acesso remoto privado, Docker Compose para serviços, Ollama para execucao de modelos locais e Open WebUI como interface.

Modelos iniciais:

- `qwen3:8b` como modelo Core.
- `qwen2.5-coder:7b` como especialista em desenvolvimento.
- `llama3.2:3b` para tarefas rapidas.
- `sentence-transformers/all-MiniLM-L6-v2` no Open WebUI para embeddings/RAG.
- `nomic-embed-text:latest` permanece instalado no Ollama como alternativa, mas nao e usado pelo provider atual.

A GPU NVIDIA GTX 1660 Ti sera disponibilizada ao container Ollama via NVIDIA Container Toolkit.

### Consequencias

- Modelos e dados permanecem no host quando nao e necessaria uma integração externa.
- A API do Ollama permanece apenas na rede Docker.
- Open WebUI e acessado pela porta 3000 em rede privada.
- A automação local opera em workspaces isolados, com Git, testes e revisão
  humana antes de commit/push. O executor integrado só expõe leitura segura e
  Git `status`/`log`; integrações externas continuam futuras.
- O repositorio GitHub contem somente documentação e exemplos sanitizados.

## Outras decisoes

Novas decisoes arquiteturais e operacionais serao registradas como ADRs em `docs/decisoes/` e resumidas aqui quando fizer sentido para o RAG.
