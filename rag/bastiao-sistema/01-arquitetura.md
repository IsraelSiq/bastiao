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
  |- Agente Python: Explorer, Builder e Task Engine
       |- SQLite, auditoria, registro e executor controlado
```

## Componentes atuais

| Componente | Responsabilidade | Exposicao | Persistencia |
|---|---|---|---|
| Ubuntu Server | SO e servicos base | Rede privada | Disco local |
| SSH | Administracao remota | Rede local / Tailscale | Config do sistema |
| Tailscale | Acesso remoto privado | Tailnet | Conta/config Tailscale |
| Docker Compose | Orquestracao de containers | Local | Arquivos em `~/bastiao/infra/open-webui` |
| Open WebUI | Interface, autenticação, conversas e RAG | `100.84.226.99:3000` (Tailscale) | `./data` |
| Ollama | API e execucao de modelos locais | Apenas rede Docker | `./ollama` |
| NVIDIA Container Toolkit | Acesso da GPU aos containers | Interno | Config Docker |
| Agente Python | Tarefas, workspaces e ferramentas delimitadas | Local | SQLite e logs fora do repo |

## Fluxo de conversa

```text
Navegador
  -> Open WebUI:3000
  -> Ollama:11434 na rede Docker
  -> modelo local
  -> resposta no Open WebUI
```

A porta 11434 do Ollama **nao** deve ser publicada para LAN ou internet. O Open WebUI acessa o servico pelo DNS interno Docker: `http://ollama:11434`.

## Agente local atual

```text
Usuario
  -> Bastiao Core (qwen3:8b)
  -> Orquestrador Python
       |- RAG/documentos
       |- especialista de codigo (qwen2.5-coder:7b)
       |- Git e workspaces isolados
       |- testes/lint/build predefinidos
       |- registro versionado e schemas estritos
       |- adaptadores de leitura: arquivos, Git status/log
       |- executor isolado com timeout
       |- SQLite: tarefas, logs, aprovacoes e relatorios
```

O Core ainda não chama estas bibliotecas diretamente. Nenhum modelo recebe
acesso irrestrito ao host, Docker socket, `sudo`, segredos ou produção.
O Worker aplica concorrência explícita, timeout, cancelamento e recuperação sem
replay. O painel de aprovação é local em terminal, não é um serviço web.
