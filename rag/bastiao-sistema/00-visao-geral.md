# Bastiao – Visao Geral

## O que e

O Bastiao e um servidor pessoal de IA local, operado 24/7 em casa, acessivel remotamente por rede privada (Tailscale). Ele executa modelos locais, fornece uma interface de chat (Open WebUI) e evolui para um assistente de programacao, pesquisa e automacao supervisionada.

## Objetivos

- Manter modelos, dados e conversas no servidor sempre que possivel (local-first).
- Oferecer IA local com privacidade e controle total.
- Assistir em programacao, leitura de projetos, pesquisa e tarefas operacionais.
- Evoluir para automacao supervisionada, com aprovacao humana para acoes externas ou irreversiveis.

## Principios

- **Local-first**: modelos e dados permanecem no servidor; integracoes externas sao opcionais e controladas.
- **Acesso remoto privado**: SSH, Open WebUI e Ollama nao sao expostos diretamente a internet; uso de Tailscale.
- **Separaçª£o de responsabilidades**: modelo, memoria, ferramentas e permissoes sao componentes distintos.
- **Automacao gradual**: leitura e analise antes de escrita; testes e diff antes de commit; confirmacao antes de acoes externas.
- **Segredos fora do repo**: senhas, tokens, chaves e arquivos `.env` nunca entram no repositorio.

## Estado atual

- Ubuntu Server 26.04 LTS
- SSH e Tailscale para acesso remoto
- Docker Engine + Docker Compose
- Open WebUI (porta 3000, com autenticaçª£o)
- Ollama (API apenas na rede Docker)
- GPU NVIDIA GTX 1660 Ti (6 GB VRAM) com NVIDIA Container Toolkit
- Modelos: `qwen3:8b` (Core), `qwen2.5-coder:7b` (Dev), `llama3.2:3b` (rapido), `nomic-embed-text:latest` (embeddings)

## Pr oximos passos

- Configurar RAG com `nomic-embed-text:latest` no Open WebUI.
- Criar base de conhecimento `Bastiao-Sistema` (esta pasta).
- Escolher um projeto-piloto para `Projetos-Ativos`.
- Implementar Bastiao Explorer (leitura segura de repositorios).
