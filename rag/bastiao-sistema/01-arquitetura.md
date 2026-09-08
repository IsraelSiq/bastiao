# Bastiao – Arquitetura

## Visao geral

```text
Dispositivos autorizados
        |
Tailscale (rede privada)
        |
Ubuntu Server: Bastiao
        |
Docker Compose
  |- Open WebUI: interface, usuarios, conversas e RAG
  |- Ollama: inferencia local de LLMs
  |- Futuro: agente Python, fila SQLite e conectores controlados
```

## Componentes atuais

| Componente | Responsabilidade | Exposicao | Persistencia |
|---|---|---|---|
| Ubuntu Server | SO e servicos base | Rede privada | Disco local |
| SSH | Administracao remota | Rede local / Tailscale | Config do sistema |
| Tailscale | Acesso remoto privado | Tailnet | Conta/config Tailscale |
| Docker Compose | Orquestracao de containers | Local | Arquivos em `~/bastiao/infra/open-webui` |
| Open WebUI | Interface, autenticaçª£o, conversas e RAG | Porta 3000 | `./data` |
| Ollama | API e execucao de modelos locais | Apenas rede Docker | `./ollama` |
| NVIDIA Container Toolkit | Acesso da GPU aos containers | Interno | Config Docker |

## Fluxo de conversa

```text
Navegador
  -> Open WebUI:3000
  -> Ollama:11434 na rede Docker
  -> modelo local
  -> resposta no Open WebUI
```

A porta 11434 do Ollama **nao** deve ser publicada para LAN ou internet. O Open WebUI acessa o servico pelo DNS interno Docker: `http://ollama:11434`.

## Arquitetura futura

```text
Usuario
  -> Bastiao Core (qwen3:8b)
  -> Orquestrador Python
       |- RAG/documentos
       |- especialista de codigo (qwen2.5-coder:7b)
       |- Git e workspaces isolados
       |- testes/lint/build predefinidos
       |- pesquisa web com fontes
       |- conectores GitHub, Drive e Supabase com permissoes por acao
       |- SQLite: tarefas, logs, aprovacoes e relatorios
```

O Core planeja e sintetiza. Ferramentas executam operaçªµes delimitadas. Nenhum modelo recebe acesso irrestrito ao host, Docker socket, `sudo`, segredos ou producao.
