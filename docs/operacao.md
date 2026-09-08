# Operação

## Serviços

Os arquivos do Compose atual ficam fora deste repositório, em `~/bastiao/infra/open-webui`. Não versionar o arquivo real se ele contiver `WEBUI_SECRET_KEY`; use `infra/compose.example.yml` como referência sanitizada.

O exemplo versionado usa imagens fixadas por digest, health checks e exige um
endereço privado explícito em `OPEN_WEBUI_BIND_ADDRESS`. Para acesso remoto via
Tailscale, use o IP Tailscale do host (por exemplo, `100.x.y.z`) para manter a
porta inacessível pelas interfaces públicas. Nunca publique o Ollama no host.

Entrar no diretório de infraestrutura:

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

## Atualização e rollback

Antes de qualquer mudança:

1. Faça o backup dos diretórios persistentes `data` e `ollama`.
2. Valide o arquivo sem iniciar serviços:

```bash
export OPEN_WEBUI_BIND_ADDRESS="$(tailscale ip -4)"
export WEBUI_SECRET_KEY='valor-ja-existente-e-secreto'
docker compose config
```

3. Guarde a versão anterior do Compose e registre as imagens atuais:

```bash
cp compose.yml "compose.yml.$(date +%Y%m%d-%H%M%S).bak"
docker compose images
```

Depois da atualização, confirme `docker compose ps` e o endpoint `/health`.
Se houver falha, restaure o arquivo anterior e execute:

```bash
docker compose up -d
```

Não remova volumes, não execute `docker compose down -v` e não apague os
diretórios persistentes durante um rollback.

## Diagnóstico

```bash
cd ~/bastiao
python3 scripts/diagnostico_operacional.py --repo-root .
```

O diagnóstico é somente leitura. Ele verifica sistema, Docker, containers,
modelos Ollama, GPU, endpoint de saúde via Tailscale, diretórios persistentes e
o backup mais recente. Para consumo automatizado, use `--json`; para uma rede
sem Tailscale, informe `--open-webui-url http://ENDERECO:3000/health`.

## Backup

O backup verificado cobre os dados persistentes do Open WebUI, modelos Ollama,
projetos locais e documentação operacional. Antes de atualizações ou alterações
de Compose, crie um backup e confirme os hashes. O procedimento completo,
incluindo teste de restauração e rollback, está em
[Backup e restauração](backup-restauracao.md).
