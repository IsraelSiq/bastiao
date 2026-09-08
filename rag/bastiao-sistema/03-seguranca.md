# Bastiao – Seguranca

## Regras atuais

- Usar usuario comum para administração; nao operar diariamente como `root`.
- Usar SSH e Tailscale para acesso remoto privado.
- Nao criar port forwarding para SSH, Open WebUI ou Ollama.
- Manter Open WebUI com autenticação habilitada.
- Nao publicar a porta 11434 do Ollama.
- Vincular o Open WebUI apenas ao IP Tailscale privado do host.
- Nao versionar senhas, tokens, chaves, IPs privados, arquivos `.env` ou volumes persistentes.
- Atualizar Ubuntu, Docker, drivers NVIDIA, imagens e modelos de forma planejada.
- Validar hashes dos backups e testar restauracao temporaria antes de mudancas maiores.

## Autonomia gradual

| Nivel | Permitido | Exige confirmação humana |
|---|---|---|
| Consulta | RAG, leitura de documentos e pesquisa web | Nao, quando a fonte for autorizada |
| Desenvolvimento | Ler workspace e Git status/log | Nao, dentro da politica registrada |
| Alteração | Criar workspace, editar, testes/lint/build e gerar diff | Sim, com aprovacao `edit` valida |
| Externo | Commit, push, PR, mensagens, deploy, banco e APIs externas | Sim, sempre; commit/push exigem aprovacao especifica |
| Sensivel | `sudo`, firewall, Docker, roteador, segredos e producao | Sim, sempre e com revisao detalhada |

## Ferramentas

O executor só chama ferramentas versionadas e registradas. Hoje ele permite
somente leitura segura de arquivos e Git `status`/`log`, em processo isolado
com timeout, auditoria e escopo de tarefa/workspace. Não há shell, Docker,
rede, Git de escrita ou API externa no executor.

O Task Engine limita concorrência por Worker, encerra chamadas canceladas ou
expiradas e verifica espaço livre. Em Linux, o processo filho também recebe
limites de CPU e memória; decisões de aprovação são persistidas pelo painel
local de terminal com escopo e expiração.
