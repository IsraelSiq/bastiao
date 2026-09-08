# Worker de tarefas

O Worker coordena somente o ciclo de vida persistido de uma tarefa. Ele não
executa shell, Git, Docker, rede ou qualquer ação externa.

Uma tarefa pode iniciar apenas em `awaiting_approval`; cada início incrementa a
tentativa, respeitando `max_attempts`. Sucesso progride por `testing` até
`review`. Uma falha volta a `planning` apenas quando há tentativas restantes;
caso contrário permanece `failed`.

Após reinício, tarefas que estavam `executing` ou `testing` são movidas para
`blocked`. O Worker nunca as reinicia automaticamente, evitando a repetição de
uma alteração local ou ação externa incompleta. Cancelamento é persistido e
permitido apenas para tarefas não terminais.

O executor controlado de ferramentas será integrado posteriormente e precisará
obedecer às aprovações, ao escopo de workspace e aos limites já persistidos.
