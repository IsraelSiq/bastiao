# Bastiao – Operaçª£o

## Serviçªµs

Os arquivos do Compose atual ficam fora deste repositorio, em `~/bastiao/infra/open-webui`. Nao versionar o arquivo real se ele contiver `WEBUI_SECRET_KEY`; use `infra/compose.example.yml` como referencia sanitizada.

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

Atualizar imagens e recriar serviçªµs:

```bash
docker compose pull
docker compose up -d
```

## Diagn ostico

```bash
uptime
free -h
df -h /
nvidia-smi
docker exec -it ollama ollama list
docker exec -it ollama ollama ps
```

## Backup minimo

- Repositorios de codigo devem ter remoto Git configurado.
- Documentos curados de RAG devem existir fora do volume do Open WebUI.
- Configuraçªµes sanitizadas ficam neste repositorio GitHub privado.
- Dados persistentes em `~/bastiao/infra/open-webui/data` e modelos em `~/bastiao/infra/open-webui/ollama` precisam de estrategia de backup antes de mudançªµes maiores.
