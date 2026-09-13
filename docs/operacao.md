# Operação do Bastiao

Guia operacional para manutenção, troubleshooting e operação diária do servidor.

## Status do Servidor

### Verificar se está rodando

```bash
# Verificar containers
docker ps

# Verificar serviços
systemctl status tailscaled
```

## Open WebUI

### Acesso Remoto

O Open WebUI está configurado para **acesso exclusivo via Tailscale** por motivos de segurança, não expondo portas diretamente na internet ou rede local.

**URL de acesso:**
```
http://100.84.226.99:3000
```

**Pré¬¬requisitos:**
- Tailscale instalado e conectado no dispositivo remoto
- Mesmo login Tailscale do servidor (`israelsiqueira@`)

### Configuraçª£o Docker Correta

O container do Open WebUI deve ser configurado com:

1. **Porta exposta apenas na interface do Tailscale** (n™o em `0.0.0.0`)
2. **Volume persistente** para dados (`open-webui:/app/backend/data`)
3. **Rede Docker compartilhada** com Ollama (`open-webui_default`)
4. **Vari•vel de ambiente correta** para Ollama (`OLLAMA_BASE_URL=http://ollama:11434`)

**Comando correto para criar/recriar o container:**

```bash
# Parar e remover container existente (se houver)
docker stop open-webui
docker rm open-webui

# Recriar com configuraçª£o corretadocker run -d \
  --name open-webui \
  -p 100.84.226.99:3000:8080 \
  -v open-webui:/app/backend/data \
  -e OLLAMA_BASE_URL=http://ollama:11434 \
  --network open-webui_default \
  --restart unless-stopped \
  ghcr.io/open-webui/open-webui:main
```

**Importante:**
- Substitua `100.84.226.99` pelo IP Tailscale atual do servidor (ver com `tailscale ip`)
- A rede `open-webui_default` é criada automaticamente quando o Ollama é executado
- O volume `open-webui` persiste os dados (conversas, usu•rios, configuraçııes, RAG)

### Diagn•stico de Problemas

#### 1. N™o consigo acessar remotamente

**Sintoma:** Navegador n™o carrega `http://100.84.226.99:3000`

**Diagn•stico:**

```bash
# No servidor, verificar se container est• rodando
docker ps

# Verificar se porta est• exposta corretamente
docker port open-webui

# Deve mostrar: 8080/tcp -> 100.84.226.99:3000
```

**Soluçııes:**

1. **Verificar Tailscale:**
   ```bash
   tailscale status
   # Deve mostrar servidor como online
   ```

2. **Verificar se porta est• escutando:**
   ```bash
   sudo ss -tlnp | grep 3000
   # Deve mostrar: 100.84.226.99:3000
   ```

3. **Testar conectividade (no cliente remoto):**
   ```powershell
   # Windows PowerShell
   Test-NetConnection -ComputerName 100.84.226.99 -Port 3000
   
   # Se TcpTestSucceeded = False, problema de rede/firewall
   ```

4. **Recriar container com porta correta:**
   ```bash
   docker stop open-webui && docker rm open-webui
   docker run -d \
     --name open-webui \
     -p 100.84.226.99:3000:8080 \
     -v open-webui:/app/backend/data \
     -e OLLAMA_BASE_URL=http://ollama:11434 \
     --network open-webui_default \
     --restart unless-stopped \
     ghcr.io/open-webui/open-webui:main
   ```

#### 2. Open WebUI n™o conecta ao Ollama

**Sintoma:** Erro nos logs: `Cannot connect to host ip_do_ollama:11434` ou modelos n™o aparecem

**Causa:** Vari•vel `OLLAMA_BASE_URL` configurada incorretamente

**Soluçª£o:**

```bash
# Verificar configuraçª£o atual
docker inspect open-webui | grep OLLAMA_BASE_URL

# Deve mostrar: OLLAMA_BASE_URL=http://ollama:11434

# Se estiver errado (ex: ip_do_ollama), recriar container:
docker stop open-webui && docker rm open-webui
docker run -d \
  --name open-webui \
  -p 100.84.226.99:3000:8080 \
  -v open-webui:/app/backend/data \
  -e OLLAMA_BASE_URL=http://ollama:11434 \
  --network open-webui_default \
  --restart unless-stopped \
  ghcr.io/open-webui/open-webui:main
```

#### 3. Conversas/configuraçııes desapareceram

**Sintoma:** Open WebUI aparece "zerado", sem conversas ou modelos configurados

**Diagn•stico:**

```bash
# Verificar se volume existe e tem dados
docker volume inspect open-webui

# Ver conteœdo do volume
docker run --rm -v open-webui:/data alpine ls -la /data

# Deve mostrar:
# - webui.db (banco de dados, ~600KB+ se tem dados)
# - cache/
# - uploads/
# - vector_db/
```

**Causas possiveis:**

1. **Cache do navegador:** Testar em aba an™nima (`Ctrl + Shift + N`)
2. **Usu•rio diferente:** Verificar email logado (perfil → settings)
3. **Volume recriado:** Se container foi recriado sem `-v open-webui:/app/backend/data`
4. **Dados perdidos:** Se volume foi deletado ou container rodou sem volume

**Recuperaçª£o:**

```bash
# Verificar usu•rios no banco
docker run --rm -v open-webui:/data alpine sh -c "
  cat /data/webui.db | strings | grep -i '@' || echo 'Sem usu•rios'
"

# Se n™o tiver dados, restaurar de backup (se existir)
docker stop open-webui
docker run --rm -v open-webui:/data -v ~/backups:/backup alpine \
  tar xzf /backup/webui-YYYYMMDD.tar.gz -C /data
```

### Backup do Open WebUI

**Backup manual:**

```bash
# Parar container
docker stop open-webui

# Copiar volume para backup
docker run --rm -v open-webui:/data -v ~/backups:/backup alpine \
  tar czf /backup/webui-$(date +%Y%m%d-%H%M).tar.gz /data

# Reiniciar container
docker start open-webui
```

**Backup autom•tico (cron):**

```bash
# Adicionar ao crontab (backup di•rio …s 3am)
0 3 * * * docker run --rm -v open-webui:/data -v ~/backups:/backup alpine tar czf /backup/webui-$(date +\%Y\%m\%d).tar.gz /data
```

### Restaurar de Backup

```bash
# Parar container
docker stop open-webui && docker rm open-webui

# Remover volume atual (opcional, se quiser limpar)
docker volume rm open-webui

# Recriar volume
docker volume create open-webui

# Restaurar backup
docker run --rm -v open-webui:/data -v ~/backups:/backup alpine \
  tar xzf /backup/webui-YYYYMMDD.tar.gz -C /data

# Recriar container
docker run -d \
  --name open-webui \
  -p 100.84.226.99:3000:8080 \
  -v open-webui:/app/backend/data \
  -e OLLAMA_BASE_URL=http://ollama:11434 \
  --network open-webui_default \
  --restart unless-stopped \
  ghcr.io/open-webui/open-webui:main
```

## Ollama

### Verificar modelos instalados

```bash
docker exec ollama ollama list
```

### Instalar novo modelo

```bash
docker exec ollama ollama pull qwen2.5-coder:7b
```

### Verificar se est• rodando

```bash
docker ps | grep ollama
curl http://localhost:11434/api/tags
```

## Tailscale

### Verificar status

```bash
tailscale status
```

### IP do servidor

```bash
tailscale ip
```

### Reiniciar Tailscale

```bash
sudo systemctl restart tailscaled
```

## Logs œteis

### Open WebUI

```bash
docker logs open-webui --tail 100
```

### Ollama

```bash
docker logs ollama --tail 50
```

### Tailscale

```bash
sudo journalctl -u tailscaled -n 50
```

## Comandos R•pidos

```bash
# Reiniciar tudo
docker restart open-webui ollama
sudo systemctl restart tailscaled

# Verificar uso de disco
df -h
docker system df

# Limpar containers parados
docker container prune -f

# Verificar espaço em disco
docker system df
```

## Checklist de Operaçª£o Di•ria

- [ ] `docker ps` - todos os containers rodando?
- [ ] `tailscale status` - conectado?
- [ ] Acessar `http://IP_TAILSCALE:3000` - Open WebUI funcionando?
- [ ] `docker exec ollama ollama list` - modelos disponiveis?
- [ ] `df -h` - espaço em disco OK?

## ReferŒncias

- [Arquitetura](arquitetura.md)
- [Seguran•a](seguranca.md)
- [Hardware](hardware.md)
- [Modelos](modelos.md)
