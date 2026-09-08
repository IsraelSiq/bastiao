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
ou segredos. O Worker recebe `max_concurrency`; o padrão é uma tarefa por vez.
O executor verifica espaço livre antes da chamada, aplica limite de memória e
CPU em hosts POSIX e encerra o processo filho ao receber cancelamento ou atingir
o timeout. Em Windows, a quota de memória/CPU depende do limite de timeout,
pois `resource` não está disponível.

## Painel local

`scripts/painel_tarefas.py` é uma interface de terminal para o operador local
consultar fila, inspecionar tarefa, registrar aprovação com expiração ou
cancelar uma tarefa. Ela requer os caminhos explícitos do banco e do log de
auditoria, ambos fora do repositório:

```bash
python3 scripts/painel_tarefas.py \
  --database ~/.local/state/bastiao/tasks.sqlite \
  --audit-log ~/.local/state/bastiao/audit.jsonl queue
```

Registrar uma aprovação de edição por dez minutos:

```bash
python3 scripts/painel_tarefas.py \
  --database ~/.local/state/bastiao/tasks.sqlite \
  --audit-log ~/.local/state/bastiao/audit.jsonl \
  approve TASK_ID --action edit --approved-by OPERADOR --expires-in-minutes 10
```

O painel não é um serviço web e não inicia execução de tarefas: ele apenas
persiste decisões explícitas do operador local. Proteja o banco e o log pelo
usuário do sistema que opera o Bastião.
