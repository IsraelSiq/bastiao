# Worker de tarefas

O Worker coordena o ciclo de vida persistido e pode solicitar uma única chamada
ao executor seguro. Ele não executa shell, Git de escrita, Docker, rede ou
qualquer ação externa.

Uma tarefa pode iniciar apenas em `awaiting_approval`; cada início incrementa a
tentativa, respeitando `max_attempts`. Sucesso progride por `testing` até
`review`. Uma falha volta a `planning` apenas quando há tentativas restantes;
caso contrário permanece `failed`.

Após reinício, tarefas que estavam `executing` ou `testing` são movidas para
`blocked`. O Worker nunca as reinicia automaticamente, evitando a repetição de
uma alteração local ou ação externa incompleta. Cancelamento é persistido e
permitido apenas para tarefas não terminais.

O executor recebe apenas ferramentas registradas, aplica o timeout persistido e
correlaciona a chamada ao workspace da tarefa. Timeout move a tarefa para
`blocked`; falhas retornam a `planning` somente quando restam tentativas. Não
há replay automático. A concorrência é limitada por `max_concurrency` (um por
padrão); excesso de chamadas é recusado, nunca enfileirado implicitamente.
