# Bastião Agent

Esta pasta reservará a especificação e a implementação do orquestrador do Bastião.

## Objetivo

Dar ao Bastião Core ferramentas explícitas para entender projetos, consultar modelos especialistas, pesquisar fontes, criar tarefas e operar workspaces isolados.

## Versão 0.1

O Explorer opera em modo somente leitura e já tem uma implementação inicial em `agente/explorer.py`.

Funcionalidades atuais:

- listar arquivos permitidos;
- bloquear acesso a caminhos sensíveis (`.env`, segredos, artefatos locais e diretórios de dados);
- ler apenas arquivos dentro do workspace permitido;
- identificar stack e comandos de teste mais prováveis;
- consultar Git local em modo leitura;
- consultar metadados, issues e pull requests do GitHub em modo leitura via `gh`;
- executar testes predefinidos sem editar código;
- gerar relatório legível em terminal ou JSON.

Os comandos executáveis devem ser declarados em `.bastiao/explorer-policy.json`.
Sem essa política, o Explorer apenas detecta possíveis comandos e não executa nenhum.

A consulta GitHub é opcional e deve ser solicitada com `--github`. Ela exige que o
`gh` esteja instalado e autenticado, mas usa somente `gh repo view`, `gh issue list`
e `gh pr list`; falhas de autenticação ou conectividade são reportadas sem
interromper a análise local.

Próximos refinamentos planejados:

- integração GitHub em leitura;
- allowlist por projeto e por política;
- execução segura de testes com timeout e logs;
- relatório exportável por tarefa.

## Versão 0.2 — concluída

O Builder cria branch local, edita dentro do workspace, roda testes/lint/build
predefinidos e gera diff. Commit e push exigem aprovação humana explícita; PR,
deploy e ações externas continuam fora do escopo.

O Builder v0.1 está implementado em `agente/builder.py`. Consulte
[`docs/builder.md`](../docs/builder.md) para a política, a raiz de workspaces e
os limites de aprovação.

## Limites técnicos

- Diretório permitido: `~/bastiao/projetos/workspaces`.
- Sem `sudo`, Docker socket ou shell arbitrário.
- Sem leitura de `.env`, chaves, tokens, diretórios pessoais ou dados de produção.
- Comandos devem vir de política versionada por projeto.
- Toda execução deve ter timeout, logs e relatório.
