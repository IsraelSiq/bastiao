# Bastião

Servidor pessoal de IA local de Israel. Este repositório é a fonte de verdade para a arquitetura, decisões, operação, roadmap e agentes do projeto.

## Objetivo

Operar um servidor doméstico 24/7, acessível remotamente por rede privada, com IA local, memória documental, assistência de programação, pesquisa sob solicitação e automação gradual.

## Estado atual

- Ubuntu Server 26.04 LTS
- Acesso remoto por SSH e Tailscale
- Docker Engine 29.8.0 e Docker Compose v5.5.1
- Open WebUI em Docker, autenticado e publicado somente no IP Tailscale do host
- Ollama em Docker, acessível apenas pela rede interna Docker
- NVIDIA GeForce GTX 1660 Ti com 6144 MiB de VRAM
- Driver NVIDIA 595.84 e NVIDIA Container Toolkit
- Modelos locais: `qwen3:8b`, `qwen2.5-coder:7b`, `llama3.2:3b` e `nomic-embed-text:latest`

## Princípios

- Local-first: modelos, documentos e conversas permanecem no servidor quando possível.
- Acesso remoto privado: não expor SSH, Open WebUI ou Ollama diretamente à internet.
- Separação de responsabilidades: modelo, memória, ferramentas e permissões são componentes distintos.
- Automação gradual: leitura e análise antes de escrita; testes e diff antes de commit; confirmação antes de ações externas ou irreversíveis.
- Segredos nunca entram neste repositório.

## Agente local

As fundações do agente são locais e versionadas: Explorer somente leitura,
Builder supervisionado, workspaces Git isolados, fila SQLite, registro de
ferramentas, executor com timeout e relatórios redigidos. As únicas ferramentas
registradas hoje são leitura segura de arquivos e consultas Git `status`/`log`.
O agente não possui shell arbitrário, `sudo`, Docker, rede, APIs externas ou
Git de escrita pelo executor.

## Documentação

- [Arquitetura](docs/arquitetura.md)
- [Hardware](docs/hardware.md)
- [Modelos](docs/modelos.md)
- [Segurança](docs/seguranca.md)
- [Operação](docs/operacao.md)
- [Backup e restauração](docs/backup-restauracao.md)
- [Autorização e auditoria](docs/autorizacao-auditoria.md)
- [Builder v0.1](docs/builder.md)
- [Fila, relatórios e aprovações](docs/tarefas.md)
- [Worker de tarefas](docs/worker.md)
- [Contrato de ferramentas](docs/ferramentas.md)
- [Adaptadores e executor seguro](docs/executor.md)
- [Roadmap](roadmap/roadmap.md)
- [Backlog](roadmap/backlog.md)

## Próxima meta

Concluir os controles restantes da Fase 4: quotas de recursos, cancelamento
ativo, concorrência controlada e interface humana de aprovação.
