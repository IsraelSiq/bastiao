# Roadmap do Bastiao

Este documento descreve as fases de evolucao do Bastiao, da fundacao ate a autonomia supervisionada. Cada fase (a partir da Fase 1) esta associada a uma issue no GitHub para acompanhamento.

## Fase 0: Fundacao — concluida

- [x] Ubuntu Server 26.04 LTS
- [x] SSH remoto
- [x] Tailscale
- [x] Docker Engine e Docker Compose
- [x] Open WebUI com dados persistentes
- [x] Ollama isolado em Docker
- [x] Driver NVIDIA, Secure Boot/MOK e NVIDIA Container Toolkit
- [x] Modelos iniciais (`qwen3:8b`, `qwen2.5-coder:7b`, `llama3.2:3b`, `nomic-embed-text:latest`)

**Referencia:** `docs/decisoes/ADR-001-arquitetura-inicial.md`

---

## Fase 1: Conhecimento (RAG) — issue #1

- [ ] Configurar embeddings no Open WebUI com `nomic-embed-text:latest`
- [ ] Criar base de conhecimento `Bastiao-Sistema` (documentacao, arquitetura, operacoes, decisoes)
- [ ] Criar base `Projetos-Ativos` com um projeto-piloto sem segredos
- [ ] Definir processo de curadoria, versionamento e reindexacao de documentos

**Criterios de aceite:**

- Conversas no Open WebUI conseguem usar RAG sobre `Bastiao-Sistema`.
- Documentos curados estao fora do volume do Open WebUI e versionados/backupados.
- Processo de inclusao/atualizacao de documentos esta documentado.

**Issue:** https://github.com/IsraelSiq/bastiao/issues/1

---

## Fase 2: Explorer — issue #2

- [ ] Leitura segura de filesystem (allowlist de paths, sem `.env`, sem segredos)
- [ ] Integracao Git local em modo leitura (status, log, diff, branches)
- [ ] Detecao de stack (linguagens, dependencias, comandos de build/teste)
- [ ] Execucao de testes em modo somente leitura (comandos predefinidos)
- [ ] Gerar relatorio de arquitetura, dependencias e saude do projeto

**Criterios de aceite:**

- O Explorer consegue listar e ler arquivos permitidos de um repositorio-piloto.
- Identifica stack e comandos de teste/build e os registra em documento ou issue.
- Executa testes predefinidos sem editar codigo e gera relatorio legivel.

**Issue:** https://github.com/IsraelSiq/bastiao/issues/2

---

## Fase 3: Builder — issue #3

- [ ] Criar branch local por tarefa
- [ ] Edicao restrita ao workspace permitido
- [ ] Executar testes, lint e build predefinidos
- [ ] Gerar diff estruturado e relatorio de mudancas
- [ ] Exigir aprovacao humana antes de commit/push

**Criterios de aceite:**

- O Builder cria branch, edita dentro do workspace e roda testes/lint/build.
- Gera diff e relatorio claros antes de qualquer commit.
- Nenhum commit/push e feito sem aprovacao explicita do usuario.

**Issue:** https://github.com/IsraelSiq/bastiao/issues/3

---

## Fase 4: Agente (tarefas + fila) — issue #4

- [ ] Modelo de tarefa (id, descricao, estado, limites, logs)
- [ ] SQLite para fila de tarefas e historico
- [ ] Estados: pendente, planejando, executando, testes, revisao, concluida, bloqueada
- [ ] Limites de tempo, tentativas e escopo por tarefa
- [ ] Relatorios e painel de aprovacao

**Criterios de aceite:**

- Tarefas sao criadas, persistidas em SQLite e tem estado bem definido.
- O agente executa dentro dos limites de tempo/escopo e registra logs.
- Existe relatorio por tarefa e visao geral da fila.

**Issue:** https://github.com/IsraelSiq/bastiao/issues/4

---

## Fase 5: Mundo Externo — issue #5

- [ ] GitHub: leitura de repositorios, issues e PRs (via API)
- [ ] Pesquisa web com registro de fontes e consultas
- [ ] Google Drive em pastas autorizadas (leitura)
- [ ] APIs externas controladas (ex.: Supabase dev) com permissoes explicitas

**Criterios de aceite:**

- O Bastiao consegue consultar GitHub e web e citar fontes nas respostas.
- Acesso a Drive e APIs externas ocorre apenas em pastas/endpoints autorizados.
- Todas as chamadas externas tem logs e sao rastreaveis por tarefa.

**Issue:** https://github.com/IsraelSiq/bastiao/issues/5

---

## Fase 6: Bastiao completo — issue #6

- [ ] Voz local (STT/TTS) opcional
- [ ] Notificacoes e alertas (saude do servidor, falhas de container, disco, GPU)
- [ ] Monitoramento de CPU, RAM, disco, GPU e temperatura
- [ ] Autonomia supervisionada: tarefas recorrentes, relatorios e aprovacao continua

**Criterios de aceite:**

- O Bastiao emite alertas e notificacoes sobre problemas de infraestrutura.
- Existe painel ou relatorio periodico de saude do servidor.
- Tarefas recorrentes sao executadas com aprovacao/visao do usuario.

**Issue:** https://github.com/IsraelSiq/bastiao/issues/6
