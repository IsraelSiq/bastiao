# Fila de tarefas

`agente/tarefas.py` fornece a persistência local da fila, sem worker ou
execução automática. O banco SQLite e o log de auditoria devem estar fora do
repositório e fora de workspaces editáveis.

O schema versionado registra tarefas, eventos, aprovações e relatórios. Cada
tarefa tem identificação, descrição, workspace, limite de tempo, limite de
tentativas e estado. As transições reutilizam a máquina de estados da política
de autorização e as inválidas são rejeitadas.

O estado é recuperado ao recriar `TaskStore` com o mesmo banco. A próxima
subtask adicionará worker, timeout, cancelamento e retry; nenhuma dessas ações
é disparada por esta entrega.

## Relatórios e aprovações

`agente/relatorios.py` oferece visões somente leitura da fila e de uma tarefa.
Elas incluem estado, eventos, aprovações registradas e resumos de relatórios,
mas não aprovam nem executam operações. Valores associados a `secret`, `token`,
`password` e `api_key` são redigidos antes de descrições ou resumos serem
persistidos.
