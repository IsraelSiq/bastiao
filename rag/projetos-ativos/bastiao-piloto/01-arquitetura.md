# bastiao-piloto - Arquitetura

## Estrutura de diretorios

```text
bastiao-piloto/
  README.md
  requirements.txt
  src/
    __init__.py
    main.py
  tests/
    __init__.py
    test_main.py
  Dockerfile
  .gitignore
```

## Componentes

- `src/main.py`: aplicacao FastAPI.
  - Endpoints iniciais:
    - `GET /` – mensagem de boas-vindas.
    - `GET /health` – saude da API (status 200, JSON simples).
- `tests/test_main.py`: testes minimos com pytest.
  - Testar `/` e `/health`.
- `requirements.txt`: dependencias.
  - `fastapi`
  - `uvicorn`
  - `pytest`
  - `ruff`

## Dependencias principais

- FastAPI: framework web.
- Uvicorn: servidor ASGI.
- pytest: testes.
- Ruff: lint.

## Evolucao futura

- Adicionar mais endpoints de exemplo.
- Incluir validacao de modelos (pydantic).
- Adicionar exemplos de erro e tratamento de excecoes.
- Criar `pyproject.toml` e migrar para `uv` ou `pip` moderno.
