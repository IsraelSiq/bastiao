# RAG no Bastiao

Esta pasta contem as bases de conhecimento usadas para RAG (Retrieval-Augmented Generation) no Bastiao.

## Bases

### Bastiao-Sistema

Documentacao curada sobre o proprio Bastiao: visao geral, arquitetura, modelos, seguranca, operacao e decisoes.

Local: `rag/bastiao-sistema/`

Uso: configurar no Open WebUI como base de conhecimento para conversas sobre o servidor, arquitetura e operacao.

### Projetos-Ativos

Documentacao e arquivos de projetos em desenvolvimento, usados para RAG contextual por projeto.

Local: `rag/projetos-ativos/` (a criar)

Uso: cada projeto tera sua propria subpasta com documentos curados (README, arquitetura, decisoes, operacao).

## Como adicionar documentos

1. Crie ou edite o arquivo Markdown na base apropriada.
2. Mantenha o conteudo claro, objetivo e "RAG-friendly" (titulos, listas, blocos de codigo quando necessario).
3. Evite segredos, tokens, senhas, IPs privados ou dados pessoais.
4. Commit e push normais.

## Reindexacao no Open WebUI

Sempre que adicionar ou modificar documentos:

1. No Open WebUI, va em **Knowledge Bases** (ou equivalente).
2. Selecione a base (`Bastiao-Sistema` ou futura `Projetos-Ativos`).
3. Acione a reindexacao/refresh dos documentos.
4. Aguarde a conclusao antes de usar RAG em conversas.

## Proximos passos

- Configurar embeddings com `nomic-embed-text:latest` no Open WebUI.
- Criar base `Projetos-Ativos` com um projeto-piloto.
- Definir rotina de curadoria e reindexacao.
