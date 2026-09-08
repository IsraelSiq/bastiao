# Bastiao – Seguranca

## Regras atuais

- Usar usuario comum para administraçª£o; nao operar diariamente como `root`.
- Usar SSH e Tailscale para acesso remoto privado.
- Nao criar port forwarding para SSH, Open WebUI ou Ollama.
- Manter Open WebUI com autenticaçª£o habilitada.
- Nao publicar a porta 11434 do Ollama.
- Nao versionar senhas, tokens, chaves, IPs privados, arquivos `.env` ou volumes persistentes.
- Atualizar Ubuntu, Docker, drivers NVIDIA, imagens e modelos de forma planejada.
- Fazer backup de documentaçª£o, configuraçªµes sanitizadas e repositorios importantes.

## Autonomia gradual

| Nivel | Permitido | Exige confirmaçª£o humana |
|---|---|---|
| Consulta | RAG, leitura de documentos e pesquisa web | Nao, quando a fonte for autorizada |
| Desenvolvimento | Ler workspace, criar branch local, rodar testes/lint/build | Nao, dentro de limites predefinidos |
| Alteraçª£o | Editar no workspace e gerar diff | Sim, antes de commit |
| Externo | Push, PR, mensagens, deploy, banco, APIs externas e compras | Sim, sempre |
| Sensivel | `sudo`, firewall, Docker, roteador, segredos e producao | Sim, sempre e com revisao detalhada |

## Ferramentas

Ferramentas e plugins que executam Python/Bash podem executar codigo no servidor. Instalar somente codigo revisado e mante-los restritos ao administrador. O agente proprio devera usar allowlists, diretorio de trabalho fixo, timeouts, logs e validaçª£o de caminhos.
