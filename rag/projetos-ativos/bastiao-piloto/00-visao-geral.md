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
- Lint: ruff
- Gerencia de dependencias: `requirements.txt`
- Opcional: Docker com `Dockerfile` simples

## Criterios

- Sem segredos no codigo ou historico (nada de `.env` real, tokens, senhas).
- Comandos claros de `run`, `test`, `lint`.
- README simples e direto.
- Pequeno o suficiente para ser entendido rapidamente, mas realista.

## Estado atual

- Endpoints `/` e `/health` implementados.
- Testes minimos implementados em `tests/test_main.py`.
- Dependencias fixadas em `requirements.txt`.
- Lint configurado com Ruff.
- O projeto esta pronto para validar o Explorer e o Builder.
