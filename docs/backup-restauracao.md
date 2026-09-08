# Backup e restauração

## Escopo

O backup protege os dados que não podem ser recriados automaticamente:

- `infra/open-webui/data`: usuários, conversas, documentos enviados e índice vetorial;
- `infra/open-webui/ollama/models`: modelos locais do Ollama;
- `projetos`: checkouts e projetos locais;
- `rag`, `docs`, `roadmap`, `scripts`, `.github` e `README.md`: documentação e configuração versionada.

Não incluir chaves privadas, arquivos `.env`, caches de modelos regeneráveis,
ambientes virtuais, `.pytest_cache` ou `.ruff_cache`. Segredos devem ser
recuperados por um cofre ou procedimento administrativo separado.

## Política

- Criar backup antes de atualizar imagens, alterar Compose ou executar uma
  operação destrutiva.
- Manter ao menos um backup íntegro fora do diretório do repositório.
- Validar todos os arquivos com `sha256sum -c SHA256SUMS` imediatamente após a
  criação e antes de uma restauração.
- Manter backups datados até que uma restauração de teste seja aprovada.

O backup inicial validado em 2026-09-08 está em:

```text
/home/rael22/bastiao-backup-20260908-214936
```

## Criar backup

No host, execute o procedimento abaixo a partir de um diretório de destino
com espaço suficiente. Ajuste o destino para armazenamento externo quando
disponível.

```bash
set -eu
repo="$HOME/bastiao"
backup="$HOME/bastiao-backup-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$backup"

tar --exclude='infra/open-webui/data/cache' \
  -czf "$backup/runtime-data.tar.gz" -C "$repo" infra/open-webui/data
tar --exclude='infra/open-webui/ollama/cache' \
  --exclude='infra/open-webui/ollama/id_ed25519' \
  -czf "$backup/ollama-models.tar.gz" -C "$repo" infra/open-webui/ollama
tar --exclude='*/.venv' --exclude='*/.pytest_cache' --exclude='*/.ruff_cache' \
  -czf "$backup/projetos.tar.gz" -C "$repo" projetos

for path in rag scripts docs roadmap README.md .github; do
  [ -e "$repo/$path" ] &&
    tar --exclude='.git' -czf "$backup/repository-$(echo "$path" | tr / _).tar.gz" \
      -C "$repo" "$path"
done

(cd "$backup" && sha256sum *.tar.gz > SHA256SUMS && sha256sum -c SHA256SUMS)
```

## Teste de restauração sem impacto

Valide o backup e extraia uma cópia temporária; nunca extraia diretamente
sobre os dados ativos durante o teste.

```bash
set -eu
backup="$HOME/bastiao-backup-AAAAMMDD-HHMMSS"
(cd "$backup" && sha256sum -c SHA256SUMS)

restore_dir="$(mktemp -d "$HOME/bastiao-restore-test.XXXXXX")"
tar -xzf "$backup/repository-rag.tar.gz" -C "$restore_dir"
cmp -s "$restore_dir/rag/openwebui-config.json" \
  "$HOME/bastiao/rag/openwebui-config.json"
rm -rf "$restore_dir"
```

O teste é aprovado quando todos os hashes são válidos, `cmp` retorna zero e o
diretório temporário é removido. Em 2026-09-08, esse teste foi aprovado para a
documentação RAG.

## Restauração operacional

Uma restauração de `runtime-data.tar.gz` ou `ollama-models.tar.gz` substitui
dados ativos. Pare e obtenha revisão humana antes de iniciá-la.

1. Confirme hashes e extraia os arquivos para um diretório temporário.
2. Pare somente os serviços envolvidos com `docker compose stop`.
3. Renomeie o diretório ativo para uma cópia datada; não o apague.
4. Extraia o arquivo para a raiz do repositório.
5. Suba os serviços com `docker compose up -d`.
6. Confirme `docker compose ps`, o endpoint `/health`, login e coleções RAG.
7. Preserve a cópia datada até a validação funcional terminar.

Não use `docker compose down -v`, não remova volumes e não sobrescreva dados
ativos sem uma cópia reversível.
