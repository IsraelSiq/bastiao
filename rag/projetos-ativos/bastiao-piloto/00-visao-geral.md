# bastiao-piloto – Visao Geral

## Objetivo

`bastiao-piloto` e o primeiro projeto-piloto do Bastiao, usado para:

- Desenvolver e testar o Bastiao Explorer (leitura segura de repositorios).
- Desenvolver e testar o Bastiao Builder (edicao supervisionada de codigo).
- Servir como exemplo de projeto com RAG contextual.

## Stack inicial

- Linguagem: Python 3.11+
- Framework: FastAPI
- Testes: pytest
- Lint: ruff (ou flake8)
- Gerencia de dependencias: `requirements.txt` (futuro: `pyproject.toml` + `uv`/`pip`)
- Opcional: Docker com `Dockerfile` simples

## Criterios

- Sem segredos no codigo ou historico (nada de `.env` real, tokens, senhas).
- Comandos claros de `run`, `test`, `lint`.
- README simples e direto.
- Pequeno o suficiente para ser entendido rapidamente, mas realista.

## Proximos passos

- Implementar endpoint basico `/` e `/health`.
- Adicionar testes minimos.
- Configurar lint e testes de forma reprodutivel.
- Usar este projeto para validar o Explorer e o Builder.
