# Hardware

## Servidor

| Recurso | Informação |
|---|---|
| CPU | AMD Ryzen 5 com gráficos integrados; modelo exato ainda não registrado |
| RAM instalada | 32 GB |
| RAM reconhecida pelo Ubuntu | aproximadamente 26 GiB |
| GPU | NVIDIA GeForce GTX 1660 Ti |
| VRAM | 6144 MiB (6 GB) |
| Disco raiz | 218 GB |
| Espaço livre inicial após modelos base | aproximadamente 175 GB |
| Firmware | UEFI com Secure Boot habilitado |

## Implicações

- Modelos de 3B/4B oferecem melhor latência e ocupam pouco VRAM.
- Modelos 7B/8B quantizados são viáveis, mas podem usar RAM e offload parcial de GPU dependendo do contexto e da configuração.
- Não manter vários modelos grandes carregados simultaneamente.
- A GPU deve ser monitorada com `nvidia-smi`; memória, disco e carga do servidor com `free -h`, `df -h` e `uptime`.

## GPU

- Driver NVIDIA: 595.84
- CUDA reportado pelo driver: 13.2
- NVIDIA Container Toolkit instalado e configurado para Docker
- Secure Boot: habilitado; chave MOK cadastrada para módulos DKMS
