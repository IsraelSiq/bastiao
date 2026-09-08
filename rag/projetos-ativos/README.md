# Projetos-Ativos

Esta pasta contem a documentacao curada dos projetos ativos que o Bastiao vai usar para RAG contextual.

## Estrutura

Cada projeto tem sua propria subpasta:

```text
rag/projetos-ativos/
  README.md
  NOME-DO-PROJETO/
    00-visao-geral.md
    01-arquitetura.md
    02-operacao.md
    03-comandos-verificados.md
```

## Projetos atuais

- `bastiao-piloto` – primeiro projeto-piloto, usado para validar Explorer,
  Builder supervisionado e políticas por projeto.

## Como adicionar um projeto

1. Crie uma subpasta `NOME-DO-PROJETO/`.
2. Adicione pelo menos:
   - `00-visao-geral.md` – objetivo, stack, contexto.
   - `01-arquitetura.md` – estrutura, modulos, dependencias.
   - `02-operacao.md` – como rodar, testar, fazer build e deploy.
   - `03-comandos-verificados.md` – comandos executados e resultados.
3. Mantenha o conteudo claro e "RAG-friendly" (titulos, listas, blocos de codigo).
4. Evite segredos, tokens, senhas, IPs privados ou dados pessoais.
5. Commit e push normais.

## Reindexacao no Open WebUI

Sempre que adicionar ou modificar documentos:

1. No Open WebUI, va em **Knowledge Bases**.
2. Selecione ou crie a base `Projetos-Ativos`.
3. Aponte para `rag/projetos-ativos/` (ou faca upload dos arquivos).
4. Acione a reindexacao/refresh.
5. Aguarde a conclusao antes de usar RAG em conversas sobre projetos.
