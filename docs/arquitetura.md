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
  |- Agente Python: Explorer, Builder e execução controlada
       |- SQLite: tarefas, eventos, aprovações e relatórios
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
| Agente Python | Exploração, Builder, fila e execução delimitada | Local | Banco SQLite e auditoria fora do repositório |

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

## Arquitetura do agente

```text
Usuário
  -> Bastião Core (qwen3:8b)
  -> Orquestrador Python
       |- RAG/documentos
       |- especialista de código (qwen2.5-coder:7b)
       |- Git e workspaces isolados
       |- testes/lint/build predefinidos
       |- registro versionado de ferramentas
       |- adaptadores: leitura de arquivos e Git somente leitura
       |- executor em processo isolado com timeout
       |- SQLite: tarefas, eventos, aprovações e relatórios
```

O Core ainda não está integrado a um modelo de linguagem. As bibliotecas locais
já impõem contrato de ferramentas, correlação com tarefa/workspace, timeout e
auditoria. Nenhum modelo recebe acesso irrestrito ao host, Docker socket,
`sudo`, segredos ou produção. Pesquisa web, GitHub, Drive e Supabase continuam
fora do executor.
