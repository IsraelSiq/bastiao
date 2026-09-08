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
- **Separação de responsabilidades**: modelo, memoria, ferramentas e permissoes sao componentes distintos.
- **Automacao gradual**: leitura e analise antes de escrita; testes e diff antes de commit; confirmacao antes de acoes externas.
- **Segredos fora do repo**: senhas, tokens, chaves e arquivos `.env` nunca entram no repositorio.

## Estado atual

- Ubuntu Server 26.04 LTS
- SSH e Tailscale para acesso remoto
- Docker Engine + Docker Compose
- Open WebUI (porta 3000, com autenticação)
- Ollama (API apenas na rede Docker)
- GPU NVIDIA GTX 1660 Ti (6 GB VRAM) com NVIDIA Container Toolkit
- Modelos: `qwen3:8b` (Core), `qwen2.5-coder:7b` (Dev), `llama3.2:3b` (rapido)
- Embeddings do RAG: `sentence-transformers/all-MiniLM-L6-v2` no Open WebUI.
- `nomic-embed-text:latest` permanece instalado no Ollama como alternativa.

## Estado do agente local

- O RAG usa `sentence-transformers/all-MiniLM-L6-v2`; `qwen3:8b` é o modelo de
  chat validado para conversas com fontes.
- As bases `Bastiao-Sistema` e `Projetos-Ativos` foram criadas e validadas.
- Explorer, Builder supervisionado, workspaces isolados, fila SQLite, auditoria
  e executor de ferramentas registradas já existem no repositório.
- As ferramentas atualmente integradas ao executor são leitura segura de
  arquivos e Git `status`/`log`; não há shell, Docker, rede ou APIs externas.
- O Task Engine aplica timeout interruptível, cancelamento ativo, concorrência
  configurável, verificação de disco e limites POSIX de CPU/memória.
- O painel local de terminal exibe fila/relatórios e registra aprovações
  explícitas com escopo e expiração.

## Próximos passos

- Reindexar esta base após atualizações documentais e validar uma resposta com
  fontes no Open WebUI.
- Automatizar backup externo com retenção, hashes e monitoramento de espaço.
