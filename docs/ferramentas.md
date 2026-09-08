# Contrato de ferramentas

`agente/ferramentas.py` define o contrato versionado entre o Core e as
capacidades locais. Uma ferramenta declara nome, versão, descrição, ação
requerida, schema estrito de argumentos e handler.

O registro descobre ferramentas em ordem estável e resolve exclusivamente a
combinação exata de nome e versão. Argumentos extras, ausentes ou de tipo
divergente são recusados antes de qualquer execução.

O registro não chama handlers diretamente. `agente/executor.py` é a única
camada permitida a invocá-los: valida autorização, workspace, timeout,
correlação de tarefa e auditoria. Não há fallback para shell, Docker, rede ou
ferramentas não registradas.
