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

## Backup

Antes de alterar imagens ou Compose, valide o backup por SHA-256 e execute um
teste de restauracao em diretorio temporario. O procedimento versionado fica em
`docs/backup-restauracao.md`; o backup validado em 2026-09-08 esta em
`/home/rael22/bastiao-backup-20260908-214936`.
