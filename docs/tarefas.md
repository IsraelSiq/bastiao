# Fila de tarefas

`agente/tarefas.py` fornece a persistência local da fila. O banco SQLite e o
log de auditoria devem estar fora do repositório e fora de workspaces editáveis.

O schema versionado registra tarefas, eventos, aprovações e relatórios. Cada
tarefa tem identificação, descrição, workspace, limite de tempo, limite de
tentativas e estado. As transições reutilizam a máquina de estados da política
de autorização e as inválidas são rejeitadas.

O estado é recuperado ao recriar `TaskStore` com o mesmo banco. O Worker
processa uma única chamada registrada por início explícito; tenta novamente
somente depois de nova transição/aprovação, respeita `max_attempts` e bloqueia
trabalho interrompido em vez de repeti-lo.

## Relatórios e aprovações

`agente/relatorios.py` oferece visões somente leitura da fila e de uma tarefa.
Elas incluem estado, eventos, aprovações registradas e resumos de relatórios,
mas não aprovam nem executam operações. Valores associados a `secret`, `token`,
`password` e `api_key` são redigidos antes de descrições ou resumos serem
persistidos.

O banco não deve conter conteúdo de arquivos, saídas completas de ferramentas
ou segredos. A interface humana de aprovação, concorrência configurável,
cancelamento ativo e quotas de CPU/RAM/disco continuam pendentes.
