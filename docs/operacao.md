# Operação

## Serviços

Os arquivos do Compose atual ficam fora deste repositório, em `~/bastiao/infra/open-webui`. Não versionar o arquivo real se ele contiver `WEBUI_SECRET_KEY`; use `infra/compose.example.yml` como referência sanitizada.

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
