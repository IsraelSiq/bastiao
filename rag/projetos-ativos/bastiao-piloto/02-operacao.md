# bastiao-piloto – Operaçª£o

## Pre-requisitos

- Python 3.11+
- `pip` ou `uv`
- Git

## Rodar localmente

```bash
# Clonar o repositorio
git clone git@github.com:IsraelSiq/bastiao-piloto.git
cd bastiao-piloto

# Criar ambiente virtual
python -m venv .venv
source .venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Rodar a API
uvicorn src.main:app --reload
```

A API deve ficar disponivel em: `http://127.0.0.1:8000`

Endpoints:

- `GET /` – mensagem de boas-vindas.
- `GET /health` – saude da API.

## Testes

```bash
# Com o ambiente virtual ativado
pytest
```

## Lint

```bash
# Com ruff
ruff check src tests

# Ou, se usar flake8
flake8 src tests
```

## Build / Docker (opcional)

```bash
docker build -t bastiao-piloto .
docker run -p 8000:8000 bastiao-piloto
```

## Comandos resumidos

- Rodar: `uvicorn src.main:app --reload`
- Testes: `pytest`
- Lint: `ruff check src tests`

## Proximos passos

- Padronizar scripts em `Makefile` ou `justfile`.
- Adicionar CI basico (GitHub Actions) para testes e lint.
- Documentar deploy (ex.: Docker, render, railway, etc.).
