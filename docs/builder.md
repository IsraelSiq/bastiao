# Builder v0.1

O Builder cria e altera somente workspaces Git isolados sob
`~/bastiao/projetos/workspaces`. A raiz deve ser fornecida explicitamente pela
operação que o integra; ele rejeita qualquer caminho que não seja filho dela.

## Política e operações

Cada projeto deve declarar comandos de teste, lint e build em
`.bastiao/builder-policy.json`. O Builder executa apenas comandos textualmente
presentes nessa política, sem shell. A política de exemplo inclui somente a
suíte Python do Bastião.

Antes de criar um workspace ou editar um arquivo, é necessária uma aprovação
`edit` válida para a mesma tarefa e o mesmo workspace. O Builder bloqueia
traversal, `.git`, `.env`, certificados, bancos locais, volumes, logs e
backups. Para cada tarefa, o workspace recebe a branch `builder/<task-id>`.

Ele pode executar comandos predefinidos e gerar um relatório com `git status`,
`git diff --no-ext-diff` e arquivos não rastreados. Nenhum comando é executado
com shell.

## Limites de ações externas

`commit` e `push` existem apenas como operações explícitas e exigem,
respectivamente, aprovações `commit` e `push`, também vinculadas à mesma
tarefa e workspace e ainda dentro do prazo UTC. O Builder não cria pull
requests, não acessa Docker, não faz deploy e não usa APIs externas.

Todos os pedidos de autorização, operações permitidas, comandos executados e
relatórios de diff são enviados para a trilha de auditoria fora do repositório.
O conteúdo editado, mensagens de commit e segredos nunca são registrados nela.
