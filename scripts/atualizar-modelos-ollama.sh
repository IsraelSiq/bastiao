#!/usr/bin/env bash
set -euo pipefail

echo "Modelos instalados:"
docker exec ollama ollama list

echo
docker exec ollama ollama list | tail -n +2 | awk '{print $1}' | while read -r model; do
  if [ -n "$model" ]; then
    echo "========================================"
    echo "Atualizando: $model"
    docker exec ollama ollama pull "$model"
  fi
done

echo
echo "Atualização finalizada."
docker exec ollama ollama list
