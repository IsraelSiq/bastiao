# Arquitetura

## Visão geral

```text
Dispositivos autorizados
        |
Tailscale (rede privada)
        |
Ubuntu Server: Bastião
        |
Docker Compose
  |- Open WebUI: interface, usuários, conversas e RAG
  |- Ollama: inferência local de LLMs
  |- Futuro: agente Python, fila SQLite e conectores controlados
```

## Componentes atuais

| Componente | Responsabilidade | Exposição | Persistência |
|---|---|---|---|
| Ubuntu Server | Sistema operacional e serviços base | Rede privada | Disco local |
| SSH | Administração remota | Rede local/Tailscale | Configuração do sistema |
| Tailscale | Acesso remoto privado entre dispositivos autorizados | Tailnet | Conta/configuração Tailscale |
| Docker Compose | Orquestração de containers | Local | Arquivos em `~/bastiao/infra/open-webui` |
| Open WebUI | Interface, autenticação, conversas e RAG | `100.84.226.99:3000` (Tailscale) | `./data` |
| Ollama | API e execução dos modelos locais | Apenas rede Docker | `./ollama` |
| NVIDIA Container Toolkit | Acesso da GPU aos containers | Interno | Configuração Docker |

## Fluxo de conversa

```text
Navegador
  -> Open WebUI:3000
  -> Ollama:11434 na rede Docker
  -> modelo local
  -> resposta no Open WebUI
```

A porta 11434 do Ollama não deve ser publicada para a LAN ou internet. O Open
WebUI acessa o serviço pelo DNS interno Docker: `http://ollama:11434`. O Open
WebUI é vinculado ao IP Tailscale do host, não a todas as interfaces.

## Arquitetura futura

```text
Usuário
  -> Bastião Core (qwen3:8b)
  -> Orquestrador Python
       |- RAG/documentos
       |- especialista de código (qwen2.5-coder:7b)
       |- Git e workspaces isolados
       |- testes/lint/build predefinidos
       |- pesquisa web com fontes
       |- conectores GitHub, Drive e Supabase com permissões por ação
       |- SQLite: tarefas, logs, aprovações e relatórios
```

O Core planeja e sintetiza. Ferramentas executam operações delimitadas. Nenhum modelo recebe acesso irrestrito ao host, Docker socket, `sudo`, segredos ou produção.
