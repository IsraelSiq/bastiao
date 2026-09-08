# Segurança

## Regras atuais

- Usar usuário comum para administração; não operar diariamente como `root`.
- Usar SSH e Tailscale para acesso remoto privado.
- Não criar port forwarding para SSH, Open WebUI ou Ollama.
- Manter Open WebUI com autenticação habilitada.
- Vincular o Open WebUI somente ao endereço privado Tailscale do host.
- Não publicar a porta 11434 do Ollama.
- Não versionar senhas, tokens, chaves, IPs privados, arquivos `.env` ou volumes persistentes.
- Atualizar Ubuntu, Docker, drivers NVIDIA, imagens e modelos de forma planejada.
- Validar hashes dos backups e testar restauração em diretório temporário antes de mudanças maiores.
- Seguir o procedimento de [backup e restauração](backup-restauracao.md).

## Autonomia gradual

| Nível | Permitido | Exige confirmação humana |
|---|---|---|
| Consulta | RAG, leitura de documentos e pesquisa web | Não, quando a fonte for autorizada |
| Desenvolvimento | Ler workspace e consultas Git somente leitura | Não, dentro da política registrada |
| Alteração | Criar workspace, editar, testes/lint/build e gerar diff | Sim, com aprovação `edit` válida |
| Externo | Commit, push, PR, mensagens, deploy, banco, APIs externas e compras | Sim, sempre; commit/push também exigem aprovação específica |
| Sensível | `sudo`, firewall, Docker, roteador, segredos e produção | Sim, sempre e com revisão detalhada |

## Ferramentas

O agente próprio usa contrato versionado, allowlists, diretório de trabalho
fixo, timeout interruptível, auditoria encadeada e validação de caminhos. O
executor só invoca ferramentas registradas e, no estado atual, expõe apenas
leitura de arquivo permitido e Git `status`/`log`. Instalar ferramentas ou
plugins adicionais exige revisão de código e política antes do registro.

O Task Engine limita concorrência por Worker, permite cancelamento ativo e
verifica quotas de disco; limites de CPU/memória são aplicados no host Linux.
O painel de aprovação é local em terminal e requer acesso ao usuário do
sistema que protege o banco SQLite e o log de auditoria.
