# Operação

## Serviços

Os arquivos do Compose atual ficam fora deste repositório, em `~/bastiao/infra/open-webui`. Não versionar o arquivo real se ele contiver `WEBUI_SECRET_KEY`; use `infra/compose.example.yml` como referência sanitizada.

O exemplo versionado usa imagens fixadas por digest, health checks e publica o
Open WebUI apenas em `127.0.0.1:3000`. Para acesso remoto via Tailscale, use
uma camada privada já aprovada (por exemplo, Tailscale Serve) ou revise a
interface de bind antes de aplicar. Nunca publique o Ollama no host.

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
uptime
free -h
df -h /
nvidia-smi
docker exec -it ollama ollama list
docker exec -it ollama ollama ps
```

## Backup mínimo

- Repositórios de código devem ter remoto Git configurado.
- Documentos curados de RAG devem existir fora do volume do Open WebUI.
- Configurações sanitizadas ficam neste repositório GitHub privado.
- Dados persistentes em `~/bastiao/infra/open-webui/data` e modelos em `~/bastiao/infra/open-webui/ollama` precisam de estratégia de backup antes de mudanças maiores.
