# Bastiao – Modelos

## Catalogo inicial

| Modelo | Papel | Tamanho local | Uso recomendado |
|---|---|---:|---|
| `qwen3:8b` | Bastiao Core | 5.2 GB | Conversa, planejamento, sintese, RAG e futura orquestraçª£o |
| `qwen2.5-coder:7b` | Bastiao Dev | 4.7 GB | Codigo, APIs, SQL, testes, debugging, Docker e revisao de diff |
| `llama3.2:3b` | Modelo rapido | 2.0 GB | Perguntas simples, resumos e respostas de baixa latencia |
| `sentence-transformers/all-MiniLM-L6-v2` | Embeddings | Open WebUI | Provider ativo para indexacao e recuperacao RAG; nao usar como chat |
| `nomic-embed-text:latest` | Embeddings alternativo | 274 MB | Instalado no Ollama, mas nao e o provider ativo |

## Politica de roteamento futura

```text
Conversa, planejamento ou sintese -> qwen3:8b
Codigo, logs, testes, SQL ou revisao -> qwen2.5-coder:7b
Busca semantica em documentos -> sentence-transformers/all-MiniLM-L6-v2
Pedido simples com prioridade de latencia -> llama3.2:3b
```

## Operaçª£o

Listar modelos:

```bash
docker exec -it ollama ollama list
```

Ver modelos carregados na memoria:

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
