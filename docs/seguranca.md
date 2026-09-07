# Segurança

## Regras atuais

- Usar usuário comum para administração; não operar diariamente como `root`.
- Usar SSH e Tailscale para acesso remoto privado.
- Não criar port forwarding para SSH, Open WebUI ou Ollama.
- Manter Open WebUI com autenticação habilitada.
- Não publicar a porta 11434 do Ollama.
- Não versionar senhas, tokens, chaves, IPs privados, arquivos `.env` ou volumes persistentes.
- Atualizar Ubuntu, Docker, drivers NVIDIA, imagens e modelos de forma planejada.
- Fazer backup de documentação, configurações sanitizadas e repositórios importantes.

## Autonomia gradual

| Nível | Permitido | Exige confirmação humana |
|---|---|---|
| Consulta | RAG, leitura de documentos e pesquisa web | Não, quando a fonte for autorizada |
| Desenvolvimento | Ler workspace, criar branch local, rodar testes/lint/build | Não, dentro de limites predefinidos |
| Alteração | Editar no workspace e gerar diff | Sim, antes de commit |
| Externo | Push, PR, mensagens, deploy, banco, APIs externas e compras | Sim, sempre |
| Sensível | `sudo`, firewall, Docker, roteador, segredos e produção | Sim, sempre e com revisão detalhada |

## Ferramentas

Ferramentas e plugins que executam Python/Bash podem executar código no servidor. Instalar somente código revisado e mantê-los restritos ao administrador. O agente próprio deverá usar allowlists, diretório de trabalho fixo, timeouts, logs e validação de caminhos.
