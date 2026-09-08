# bastiao-piloto - Operacao

## Pre-requisitos

- Python 3.11+
- `pip`
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
# Com o ambiente virtual ativado
ruff check src tests
```

## Build / Docker

```bash
docker build -t bastiao-piloto .
docker run -p 8000:8000 bastiao-piloto
```

## Comandos verificados no host

- Rodar: `uvicorn src.main:app --reload`
- Testes: `pytest`
- Lint: `ruff check src tests`

No host de validacao, os comandos equivalentes usando o ambiente virtual sao:

```bash
.venv/bin/pytest -q
.venv/bin/ruff check src tests
```

Resultado atual: 2 testes aprovados e Ruff sem erros.

## Proximos passos

- Padronizar scripts em `Makefile` ou `justfile`.
- Manter o CI GitHub Actions que executa pytest, Ruff e `docker build --check`.
- Documentar deploy (ex.: Docker, render, railway, etc.).
