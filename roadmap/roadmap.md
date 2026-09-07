# Roadmap

## Fase 0: Fundação — concluída

- [x] Ubuntu Server 26.04 LTS
- [x] SSH remoto
- [x] Tailscale
- [x] Docker Engine e Docker Compose
- [x] Open WebUI com dados persistentes
- [x] Ollama isolado em Docker
- [x] Driver NVIDIA, Secure Boot/MOK e NVIDIA Container Toolkit
- [x] Modelos iniciais

## Fase 1: Conhecimento local

- [ ] Configurar embeddings do Open WebUI com `nomic-embed-text:latest`
- [ ] Criar base `Bastiao-Sistema`
- [ ] Criar base `Projetos-Ativos`
- [ ] Definir processo de curadoria e reindexação

## Fase 2: Bastião Explorer v0.1

- [ ] Workspace de repositório-piloto
- [ ] Mapeamento de stack, estrutura e comandos
- [ ] Leitura segura de arquivos não secretos
- [ ] Relatório de arquitetura e dependências
- [ ] Diagnóstico de testes em modo somente leitura

## Fase 3: Bastião Builder v0.1

- [ ] Criar branch local
- [ ] Editar somente dentro do workspace
- [ ] Executar testes, lint e build predefinidos
- [ ] Gerar relatório e `git diff`
- [ ] Exigir aprovação antes de commit/push

## Fase 4: Conectores e pesquisa

- [ ] GitHub em modo leitura
- [ ] Pesquisa web com fontes e registro de consultas
- [ ] Google Drive em pastas autorizadas
- [ ] Supabase de desenvolvimento em modo leitura

## Fase 5: Operação autônoma limitada

- [ ] Fila SQLite
- [ ] Estados: pendente, planejando, executando, testes, revisão, concluída, bloqueada
- [ ] Limites de tempo, custo e tentativas
- [ ] Logs, relatórios e painel de aprovação

## Fase 6: Extras

- [ ] Backup automatizado e teste de restauração
- [ ] Monitoramento de CPU, RAM, disco, GPU e temperatura
- [ ] Voz local: STT e TTS
- [ ] Integrações domésticas ou notificações, se fizer sentido
