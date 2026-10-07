#!/usr/bin/env bash
# Start the stack once the Tailscale address exists. The port is bound to that
# address, so starting earlier leaves open-webui running without a published port.
set -u
cd "$(dirname "$0")"
bind="$(sed -n 's/^OPEN_WEBUI_BIND_ADDRESS=//p' .env)"

if [ -n "$bind" ] && [ "$bind" != "127.0.0.1" ] && [ "$bind" != "0.0.0.0" ]; then
  for _ in $(seq 1 90); do
    ip -4 addr show 2>/dev/null | grep -q "inet $bind/" && break
    sleep 2
  done
fi

docker compose up -d
if ! docker port open-webui 8080 >/dev/null 2>&1; then
  echo "$(date -Is) port not published; recreating open-webui"
  docker compose up -d --force-recreate open-webui
fi
