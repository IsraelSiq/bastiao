# Autorização e auditoria

## Princípios

O Bastião começa com menor privilégio. Leitura e testes predefinidos podem ser
permitidos pela política do projeto. Edição, commit, push, pull request,
deploy e APIs externas exigem aprovação humana explícita.

Uma aprovação é válida apenas para a tarefa, ação e workspace informados e
expira em horário UTC definido no momento da aprovação. Ela não pode ser
reutilizada para outra tarefa, ação ou workspace.

## Estados da tarefa

```text
pending -> planning -> awaiting_approval -> executing -> testing -> review -> completed
```

Uma tarefa também pode ficar `blocked`, `failed` ou `cancelled`. Transições
terminais não podem voltar a executar; tarefas bloqueadas ou falhas retornam
apenas ao planejamento após nova revisão.

## Auditoria

Os eventos são armazenados em JSON Lines fora do repositório, com permissão
`0600`. Cada evento contém o hash do evento anterior, criando uma trilha
detectável contra alterações acidentais.

Os logs devem registrar identificação da tarefa, ação, workspace, decisão de
autorização, início, resultado e falha. Nunca devem registrar valores de
segredos, conteúdo de `.env` ou chaves privadas.

## Implementação inicial

`agente/autorizacao.py` implementa os estados, validação de aprovação e a
trilha de auditoria. Esta camada ainda não executa comandos, edita arquivos ou
acessa GitHub/Docker; essa integração pertence ao Builder após revisão.
