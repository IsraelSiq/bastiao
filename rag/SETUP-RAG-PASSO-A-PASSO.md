# Passo a passo: configurar Open WebUI e RAG no Bastiao

Este documento explica como:

1. Atualizar o repositorio no servidor.
2. Rodar o script de validacao.
3. Confirmar o provider local de embeddings.
4. Configurar as bases de conhecimento no Open WebUI.
5. Testar RAG em conversas.

---

## 1. Atualizar o repositorio no servidor

No servidor Bastiao:

```bash
cd ~/bastiao
git pull
```

Confirme que os novos arquivos existem:

```bash
ls rag/openwebui-config.json
ls scripts/setup_openwebui.py
ls rag/SETUP-RAG-PASSO-A-PASSO.md
```

---

## 2. Rodar o script de validacao

O script `scripts/setup_openwebui.py`:

- Le `rag/openwebui-config.json`.
- Verifica se as pastas e arquivos das bases existem.
- Verifica se o provider e o modelo de embeddings estao configurados.
- Mostra um relatorio com o que esta OK e o que falta fazer.

### 2.1. Executar o script

No servidor:

```bash
cd ~/bastiao
python3 scripts/setup_openwebui.py --repo-root .
```

O script vai mostrar algo como:

- Bases de conhecimento:
  - Se os caminhos `/home/rael22/bastiao/rag/bastiao-sistema` e `/home/rael22/bastiao/rag/projetos-ativos` existem.
  - Se os arquivos `.md` de cada base estao presentes.
- Embeddings:
  - Se o provider `Sentence Transformers` e o modelo `sentence-transformers/all-MiniLM-L6-v2` estao configurados.
- Proximos passos manuais no Open WebUI.
- Sugestoes de perguntas para testar RAG.

Se algo estiver faltando (ex.: modelo de embeddings ou arquivos), o script vai indicar.

O script retorna código diferente de zero quando uma base, arquivo, configuração
ou dependência do Docker/Ollama falhar. Para usar em CI, rode:

```bash
python3 scripts/setup_openwebui.py --repo-root . --strict
```

O caminho do repositório também pode ser informado por `BASTIAO_REPO_ROOT`.
O arquivo JSON usa caminhos relativos para funcionar em qualquer checkout; o
caminho absoluto documentado continua disponível como referência operacional.

Em CI ou em uma máquina sem Docker/Ollama, valide os arquivos e a configuração
sem consultar o modelo de embeddings:

```bash
python3 scripts/setup_openwebui.py --repo-root . --skip-ollama --strict
```

---

## 3. Confirmar o provider de embeddings

O provider ativo do servidor e local:

```bash
sentence-transformers/all-MiniLM-L6-v2
```

O modelo `nomic-embed-text:latest` pode permanecer instalado no Ollama, mas nao
deve ser selecionado nem usado para reindexar as bases enquanto esta decisao
estiver vigente.

---

## 4. Configurar as bases de conhecimento no Open WebUI

### 4.1. Acessar o Open WebUI

1. No seu navegador, acesse o Open WebUI via Tailscale (ex.: `http://IP-DO-SERVIDOR:3000` ou o hostname que você usa).
2. Faça login como administrador.

### 4.2. Criar a base `Bastiao-Sistema`

1. Vá em **Knowledge** / **Knowledge Bases** (o nome pode variar conforme a versão).
2. Clique em **Create New Knowledge Base**.
3. Preencha:
   - **Name**: `Bastiao-Sistema`
   - **Description**: `Documentacao curada sobre o Bastiao: visao geral, arquitetura, modelos, seguranca, operacao e decisoes.`
4. Em **Files** / **Documents**:
   - Se permitir caminho absoluto: use o caminho do servidor para `rag/bastiao-sistema` (por exemplo, `/home/SEU_USUARIO/bastiao/rag/bastiao-sistema`).
   - Se pedir upload: faça upload dos 6 arquivos:
     - `00-visao-geral.md`
     - `01-arquitetura.md`
     - `02-modelos.md`
     - `03-seguranca.md`
     - `04-operacao.md`
     - `05-decisoes.md`
5. Salve/crie a base.

### 4.3. Criar a base `Projetos-Ativos`

1. Ainda em **Knowledge Bases**, clique em **Create New Knowledge Base**.
2. Preencha:
   - **Name**: `Projetos-Ativos`
   - **Description**: `Documentacao curada dos projetos ativos, usada para RAG contextual por projeto.`
3. Em **Files**:
   - Caminho: `/home/SEU_USUARIO/bastiao/rag/projetos-ativos` (ou upload da pasta).
4. Salve.

### 4.4. Configurar embeddings

1. Vá em **Settings** / **Embeddings** (ou similar).
2. Configure:
   - **Provider**: `Sentence Transformers`
   - **Model**: `sentence-transformers/all-MiniLM-L6-v2`
3. Salve.

### 4.5. Reindexar as bases

1. Volte para **Knowledge Bases**.
2. Para cada base (`Bastiao-Sistema`, `Projetos-Ativos`):
   - Clique em **Reindex** / **Refresh** / **Re-embed** somente depois de confirmar o provider acima.
   - Aguarde a conclusão.

### 4.6. Ajustes gerais recomendados

Em **Settings** / **General** (ou similar):

- Habilitar autenticação: **sim**.
- Permitir cadastro público: **não**.
- Modelo padrão: `qwen3:8b` (ou outro que preferir).

---

## 5. Testar RAG em conversas

1. Crie uma nova conversa.
2. Ative **RAG** / **Knowledge** e selecione:
   - `Bastiao-Sistema`
   - `Projetos-Ativos`
3. Faca perguntas como:

   - "Qual e a arquitetura atual do Bastiao?"
   - "Como funciona a autonomia gradual?"
   - "Quais sao os comandos de diagnostico do servidor?"
   - "Qual e o objetivo do bastiao-piloto?"
   - "Quais sao os comandos para rodar testes e lint no bastiao-piloto?"

4. Verifique se as respostas usam informacoes dos documentos (o Open WebUI costuma mostrar trechos usados pelo RAG).

---

## 6. Rotina de atualizacao

Sempre que adicionar ou modificar documentos em `rag/bastiao-sistema/` ou `rag/projetos-ativos/`:

1. No servidor:
   ```bash
   cd ~/bastiao
   git pull   # ou git add/commit/push se voce editou localmente
   ```
2. No Open WebUI:
   - Vá em **Knowledge Bases**.
   - Reindexe a base afetada (`Bastiao-Sistema` ou `Projetos-Ativos`).

---

## 7. Script de validacao (opcional, sempre que quiser)

Sempre que quiser validar a configuracao:

```bash
cd ~/bastiao
python3 scripts/setup_openwebui.py
```

Isso vai mostrar novamente:

- Se as bases estao ok.
- Se o modelo de embeddings esta instalado.
- Lembretes dos passos manuais e sugestoes de teste.
