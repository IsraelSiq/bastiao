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
