#!/usr/bin/env bash
# Cria um snapshot local do Bastião e envia para o Google Drive via rclone.
#
# Requer o remote "gdrive" ja configurado (rclone config; ver
# docs/backup-restauracao.md#backup-externo-google-drive). Nunca falha
# silenciosamente: qualquer pre-requisito ausente interrompe o script com uma
# mensagem clara em vez de gravar em outro lugar.
#
# Os modelos do Ollama (infra/open-webui/ollama) sao excluidos do envio
# remoto de proposito: sao grandes (dezenas de GB), reproduziveis via
# 'ollama pull' e a cota gratuita do Google Drive costuma ser pequena. O
# backup local completo (docs/backup-restauracao.md) continua incluindo-os.
set -euo pipefail

REMOTE="${BACKUP_REMOTE:-gdrive:bastiao-backup}"
REMOTE_NAME="${REMOTE%%:*}"
RETENTION="${BACKUP_RETENTION:-5}"
REPO="${BASTIAO_REPO:-$HOME/bastiao}"

log() {
  printf '%s %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*"
}

fail() {
  log "ERRO: $*"
  exit 1
}

[ -d "$REPO" ] || fail "diretorio do repositorio nao encontrado: $REPO (defina BASTIAO_REPO)"
[ "$RETENTION" -gt 0 ] 2>/dev/null || fail "BACKUP_RETENTION deve ser um inteiro maior que zero"

command -v rclone >/dev/null 2>&1 ||
  fail "rclone nao encontrado. Instale com 'sudo apt-get install rclone' e configure o remote '${REMOTE_NAME}' (docs/backup-restauracao.md)."

rclone about "${REMOTE_NAME}:" >/dev/null 2>&1 ||
  fail "remote '${REMOTE_NAME}' nao configurado ou inacessivel. Rode 'rclone config' e crie o remote antes de continuar."

timestamp="$(date +%Y%m%d-%H%M%S)"
local_backup="$HOME/bastiao-backup-${timestamp}"
mkdir -p "$local_backup"

log "Criando snapshot local em $local_backup"
tar --exclude='infra/open-webui/data/cache' \
  -czf "$local_backup/runtime-data.tar.gz" -C "$REPO" infra/open-webui/data
tar --exclude='*/.venv' --exclude='*/.pytest_cache' --exclude='*/.ruff_cache' \
  -czf "$local_backup/projetos.tar.gz" -C "$REPO" projetos
for path in rag scripts docs roadmap README.md .github; do
  if [ -e "$REPO/$path" ]; then
    tar --exclude='.git' -czf "$local_backup/repository-$(echo "$path" | tr / _).tar.gz" \
      -C "$REPO" "$path"
  fi
done

(cd "$local_backup" && sha256sum -- *.tar.gz > SHA256SUMS && sha256sum -c SHA256SUMS)

log "Enviando snapshot para ${REMOTE}/${timestamp}/ (modelos Ollama excluidos de proposito)"
rclone copy "$local_backup" "${REMOTE}/${timestamp}"

log "Verificando integridade remota"
rclone check "$local_backup" "${REMOTE}/${timestamp}"

log "Aplicando retencao: mantendo os ${RETENTION} backups remotos mais recentes"
mapfile -t remote_dirs < <(rclone lsf "${REMOTE}" --dirs-only 2>/dev/null | sed 's:/$::' | sort)
count=${#remote_dirs[@]}
if [ "$count" -gt "$RETENTION" ]; then
  to_delete=$((count - RETENTION))
  for ((i = 0; i < to_delete; i++)); do
    old="${remote_dirs[$i]}"
    log "Removendo backup remoto antigo: ${REMOTE}/${old}"
    rclone purge "${REMOTE}/${old}"
  done
fi

log "Backup externo concluido: ${REMOTE}/${timestamp}/"
