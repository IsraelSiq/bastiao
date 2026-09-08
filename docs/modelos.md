# Modelos locais

## Catálogo inicial

| Modelo | Papel | Tamanho local | Uso recomendado |
|---|---|---:|---|
| `qwen3:8b` | Bastião Core | 5.2 GB | Conversa, planejamento, síntese, RAG e futura orquestração |
| `qwen2.5-coder:7b` | Bastião Dev | 4.7 GB | Código, APIs, SQL, testes, debugging, Docker e revisão de diff |
| `llama3.2:3b` | Modelo rápido | 2.0 GB | Perguntas simples, resumos e respostas de baixa latência |
| `sentence-transformers/all-MiniLM-L6-v2` | Embeddings | Open WebUI | Provider ativo para indexação e recuperação RAG; não usar como chat |
| `nomic-embed-text:latest` | Embeddings alternativo | 274 MB | Instalado no Ollama, mas não é o provider ativo do Open WebUI |

## Política de roteamento futura

```text
Conversa, planejamento ou síntese -> qwen3:8b
Código, logs, testes, SQL ou revisão -> qwen2.5-coder:7b
Busca semântica em documentos -> sentence-transformers/all-MiniLM-L6-v2
Pedido simples com prioridade de latência -> llama3.2:3b
```

## Operação

Listar modelos:

```bash
docker exec -it ollama ollama list
```

Ver modelos carregados na memória:

```bash
docker exec -it ollama ollama ps
```

Atualizar todos os modelos instalados:

```bash
~/bastiao/scripts/atualizar-modelos-ollama.sh
```

Remover um modelo:

```bash
docker exec -it ollama ollama rm NOME_DO_MODELO
```
