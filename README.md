# Bastião

Servidor pessoal de IA local de Israel. Este repositório é a fonte de verdade para a arquitetura, decisões, operação, roadmap e agentes do projeto.

## Objetivo

Operar um servidor doméstico 24/7, acessível remotamente por rede privada, com IA local, memória documental, assistência de programação, pesquisa sob solicitação e automação gradual.

## Estado atual

- Ubuntu Server 26.04 LTS
- Acesso remoto por SSH e Tailscale
- Docker Engine 29.8.0 e Docker Compose v5.5.1
- Open WebUI em Docker, publicado na porta 3000 e com autenticação
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

## Documentação

- [Arquitetura](docs/arquitetura.md)
- [Hardware](docs/hardware.md)
- [Modelos](docs/modelos.md)
- [Segurança](docs/seguranca.md)
- [Operação](docs/operacao.md)
- [Backup e restauração](docs/backup-restauracao.md)
- [Autorização e auditoria](docs/autorizacao-auditoria.md)
- [Builder v0.1](docs/builder.md)
- [Roadmap](roadmap/roadmap.md)
- [Backlog](roadmap/backlog.md)

## Próxima meta

Implementar RAG documental inicial e o Bastião Explorer v0.1 para entendimento de repositórios em modo somente leitura.
