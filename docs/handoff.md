# Handoff — estado da sessão em 2026-09-08

Este documento existe para que qualquer pessoa (ou sessão do Copilot em outro
computador) saiba exatamente onde o trabalho parou, sem depender de memória
de uma sessão específica. Atualize-o ao final de cada sessão relevante; não é
necessário mantê-lo como histórico completo — apenas o estado mais recente.

## Estado confirmado em 2026-09-08 (noite)

- **Repositório `main`**: commit `ca1969a` (PR #57 mesclado).
- **Host Bastião** (`rael22@100.84.226.99` via Tailscale/SSH): sincronizado
  com `main` no commit `ca1969a`. `git pull --ff-only` aplicado sem conflitos
  com `projetos/` (não rastreado, preservado).
- **Testes**: `python -m pytest -q` → 52 passed (local e no host).
- **CI**: workflow `quality` verde no PR #57 e nos anteriores (#55, #56).
- **Containers no host**: `open-webui` e `ollama` healthy. Modelos presentes:
  `qwen3:8b`, `qwen2.5-coder:7b`, `llama3.2:3b`, `nomic-embed-text:latest`.
- **Diagnóstico operacional** (`scripts/diagnostico_operacional.py`): 0
  falhas, 0 alertas — inclusive a nova checagem de backup remoto.

## O que foi concluído nesta sessão

1. **Task Engine completo** (PR #56): cancelamento cooperativo, limites de
   CPU/memória (POSIX) e de espaço em disco, concorrência configurável no
   worker, aprovação persistida com escopo/expiração, e um painel local de
   terminal (`scripts/painel_tarefas.py`) para consultar fila, aprovar e
   cancelar tarefas. Issues #4, #27, #29, #30 fechadas com evidência.
2. **Documentação realinhada** (PR #55) com o código já integrado
   (Explorer, Builder, Task Engine), incluindo os 6 documentos RAG em
   `rag/bastiao-sistema/`.
3. **Backup externo automatizado para Google Drive** (PR #57):
   - `rclone` instalado e configurado no host (`remote: gdrive`, escopo
     restrito `drive.file`, `rclone.conf` com permissão `600`).
   - `scripts/backup_externo.sh` roda o backup local existente, envia para
     `gdrive:bastiao-backup/<timestamp>/`, verifica integridade com
     `rclone check` e aplica retenção (5 backups remotos mais recentes).
   - Modelos Ollama **excluídos de propósito** do envio remoto (grandes,
     reproduzíveis via `ollama pull`, cota gratuita do Drive limitada a
     ~16 GiB no momento).
   - **Primeiro backup remoto real já executado e verificado**:
     `gdrive:bastiao-backup/20260908-231138/` (9 arquivos, 0 diferenças).
   - Nova checagem `remote_backup_check` no diagnóstico operacional.

## Pendências (em ordem sugerida)

1. **Reindexar as bases RAG no Open WebUI (`Bastiao-Sistema` e
   `Projetos-Ativos`)** — a automação por navegador falhou repetidamente
   nesta sessão ("Webview not found", timeout). Ainda **não foi confirmado**
   que a reindexação aconteceu. Fazer manualmente:
   1. Acessar `http://100.84.226.99:3000` (Tailscale) e logar como admin.
   2. Ir em Workspace → Knowledge.
   3. Abrir `Bastiao-Sistema` → reenviar/atualizar os 6 arquivos de
      `rag/bastiao-sistema/` (o conteúdo de `04-operacao.md` mudou nesta
      sessão) → Reindex.
   4. Abrir `Projetos-Ativos` → conferir se `bastiao-piloto` está atualizado
      → Reindex.
   5. Validar com uma pergunta usando o modelo `qwen3:8b` (nunca
     `nomic-embed-text:latest` como chat — ele não suporta chat) e confirmar
     que as fontes citadas aparecem.
   - Há canvases de navegador abertos e não utilizados desta tentativa
     (`rag-validation`, `rag-validation-2`, `rag-knowledge-refresh`,
     `rag-validation-current`) — podem ser fechados quando não forem mais
     necessários.
2. **Issue #22 — Observabilidade e confiabilidade operacional**: próxima
   frente grande sugerida. Evoluir `scripts/diagnostico_operacional.py` para
   métricas persistidas ao longo do tempo, alertas com limiares/severidade, e
   possivelmente registrar eventos de diagnóstico como tarefas do Task
   Engine.
3. **Cosmético, baixa prioridade**: títulos corrompidos no GitHub —
   issue #17 (`Bastiã©¡ Core`) e #18 (`memÃ³ria`). Corrigir os títulos via
   `gh issue edit`.
4. **Backlog vivo**: ver `roadmap/backlog.md` para a lista completa e
   priorizada (RAG, políticas do Explorer/Builder, integração GitHub leitura,
   pesquisa web, painel de tarefas com interface autenticada).

## Decisões e convenções que devem ser respeitadas

- Sempre validar antes de alterar; nunca `git reset --hard`, `git clean`,
  `git add .`, `docker compose down -v`, ou remoção de dados ativos
  (`projetos/`, `infra/open-webui/data`, `infra/open-webui/ollama`) sem
  autorização explícita do usuário.
- Toda mudança de código/documentação segue o fluxo: branch → testes locais
  → commit → PR → aguardar CI verde → merge → sincronizar o host via SSH.
- O host é acessado via `rael22@100.84.226.99` (Tailscale), chave
  `~/.ssh/id_ed25519` sem passphrase — nunca revelar, copiar ou commitar essa
  chave.
- O `rclone.conf` no host contém um token OAuth do Google Drive com escopo
  restrito `drive.file`; mantenha a permissão `600` e nunca o copie para o
  repositório ou para fora do host.
- O Open WebUI só responde em `100.84.226.99:3000` (Tailscale); `127.0.0.1`
  não responde — isso é esperado, não é uma falha.
- Backup local mais recente no host antes desta sessão terminar:
  `/home/rael22/bastiao-backup-20260908-231138` (hashes presentes).
