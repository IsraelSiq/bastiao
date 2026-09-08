# bastiao-piloto - Comandos verificados

## Endpoints implementados

- `GET /` retorna uma mensagem de boas-vindas.
- `GET /health` retorna `{"status": "ok"}`.

## Instalar dependencias

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Executar a API

```bash
uvicorn src.main:app --reload
```

A API fica disponível em `http://127.0.0.1:8000`.

## Executar testes

Com o ambiente virtual ativado:

```bash
pytest
```

No host de validação:

```bash
.venv/bin/pytest -q
```

Resultado verificado: 2 testes aprovados.

## Executar lint

Com o ambiente virtual ativado:

```bash
ruff check src tests
```

No host de validação:

```bash
.venv/bin/ruff check src tests
```

Resultado verificado: Ruff sem erros.
