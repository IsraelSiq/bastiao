# Adaptadores e executor seguro

Os adaptadores iniciais fornecem somente leitura de arquivos permitidos e
consultas Git `status` e `log` limitadas ao workspace da tarefa. Eles reutilizam
a política de caminhos do Explorer e recusam segredos, volumes, traversal e
operações Git de escrita.

O executor resolve exclusivamente ferramentas registradas, exige que a tarefa
esteja `executing`, usa o workspace persistido da própria tarefa e registra
resultado ou erro sem salvar conteúdo retornado. Cada handler recebe apenas os
argumentos validados pelo contrato e o workspace da tarefa.

Cada chamada é isolada em processo filho e terminada se exceder o timeout
persistido da tarefa. Um encerramento deixa a tarefa em execução para que o
Worker a bloqueie durante recuperação, e nunca dispara replay automático.

Ferramentas que exigem edição ou ação externa continuam dependentes de
aprovação válida. Não há shell, `sudo`, Docker, rede, Git de escrita ou
repetição automática de operação.
