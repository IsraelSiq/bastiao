# Bastiao – Operação

## Serviços

Os arquivos do Compose atual ficam fora deste repositorio, em `~/bastiao/infra/open-webui`. Nao versionar o arquivo real se ele contiver `WEBUI_SECRET_KEY`; use `infra/compose.example.yml` como referencia sanitizada.

O Open WebUI usa o IP Tailscale do host (`100.84.226.99:3000`) e o Ollama
permanece apenas na rede Docker. O Compose sanitizado usa imagens fixadas por
digest, health checks e segredo externo.

Entrar no diretorio de infraestrutura:

```bash
cd ~/bastiao/infra/open-webui
```

Ver status:

```bash
docker compose ps
```

Ver logs do Open WebUI:

```bash
docker compose logs --tail=100 open-webui
```

Ver logs do Ollama:

```bash
docker compose logs --tail=100 ollama
```

Atualizar imagens e recriar serviços:

```bash
docker compose pull
docker compose up -d
```

## Diagnostico

```bash
cd ~/bastiao
python3 scripts/diagnostico_operacional.py --repo-root .
```

O diagnóstico é somente leitura e verifica sistema, Docker, containers, modelos
Ollama, GPU, endpoint de saúde via Tailscale, diretórios persistentes e backup.

## Agente local

As bibliotecas do agente são validadas em CI e não são um serviço automático no
host. O banco SQLite, a auditoria e os workspaces devem ficar fora do
repositório, em diretórios com permissões restritas. Antes de usar uma versão
operacional do agente, valide a política de cada projeto e mantenha a
aprovação humana para escrita, commit e push.

O painel de tarefas requer caminhos explícitos para o banco SQLite e a
auditoria, fora do repositório. Use `scripts/painel_tarefas.py --help` para
consultar a fila, exibir uma tarefa, registrar aprovação ou cancelar uma
tarefa; ele não inicia execução automaticamente.

## Backup

Antes de alterar imagens ou Compose, valide o backup por SHA-256 e execute um
teste de restauracao em diretorio temporario. O procedimento versionado fica em
`docs/backup-restauracao.md`.

Alem do backup local, existe backup externo automatizado para o Google Drive
via `rclone` (`scripts/backup_externo.sh`), com escopo restrito `drive.file`,
verificacao de integridade (`rclone check`) e retencao dos 5 backups remotos
mais recentes. Os modelos Ollama sao excluidos do envio remoto de proposito
(grandes, reproduziveis via `ollama pull`, cota do Drive limitada). O
diagnostico operacional reporta o backup remoto mais recente ou alerta se o
`rclone` nao estiver configurado. Configurado e validado em 2026-09-08.
