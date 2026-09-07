# Bastião Agent

Esta pasta reservará a especificação e a implementação do orquestrador do Bastião.

## Objetivo

Dar ao Bastião Core ferramentas explícitas para entender projetos, consultar modelos especialistas, pesquisar fontes, criar tarefas e operar workspaces isolados.

## Versão 0.1

O Explorer deve operar em modo somente leitura:

- listar arquivos permitidos;
- ler documentação e arquivos de projeto;
- identificar stack e comandos;
- consultar Git local e GitHub em leitura;
- executar testes predefinidos sem editar código;
- gerar relatório.

## Versão 0.2

O Builder poderá criar branch local, editar dentro do workspace, rodar testes/lint/build e gerar diff. Commit, push, PR, deploy ou ações externas continuarão exigindo aprovação humana explícita.

## Limites técnicos

- Diretório permitido: `~/bastiao/projetos/workspaces`.
- Sem `sudo`, Docker socket ou shell arbitrário.
- Sem leitura de `.env`, chaves, tokens, diretórios pessoais ou dados de produção.
- Comandos devem vir de política versionada por projeto.
- Toda execução deve ter timeout, logs e relatório.
