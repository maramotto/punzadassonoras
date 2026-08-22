#!/usr/bin/env bash
# Despliega la ultima version de master en el servidor de produccion:
# git pull + reconstruir la imagen + relanzar el contenedor.
#
# No incluye el primer despliegue en un servidor nuevo (DNS, vhost de nginx,
# certificado) -- eso esta documentado paso a paso en el README, seccion
# "Desplegar en un servidor nuevo".
#
# Uso:
#   scripts/desplegar.sh <host-ssh> [ruta-del-repo-en-el-servidor]
#
# Ejemplo:
#   scripts/desplegar.sh mi-servidor
#   scripts/desplegar.sh mi-servidor /opt/universopunzadas
#
# <host-ssh> es el alias que tengas configurado en tu ~/.ssh/config (o
# usuario@host directamente). No lleva valor por defecto a proposito: este
# script es publico, y el host de cada quien no.

set -euo pipefail

HOST="${1:?Uso: scripts/desplegar.sh <host-ssh> [ruta-del-repo]}"
RUTA="${2:-/opt/universopunzadas}"

echo "→ Actualizando codigo en ${HOST}:${RUTA}"
ssh "$HOST" "cd '$RUTA' && git pull"

echo "→ Reconstruyendo la imagen (build de tres etapas: datos, Astro, nginx)"
ssh "$HOST" "cd '$RUTA' && docker compose build"

echo "→ Relanzando el contenedor"
ssh "$HOST" "cd '$RUTA' && docker compose up -d"

echo "→ Estado del contenedor:"
ssh "$HOST" "docker ps --format '{{.Names}}: {{.Status}}' | grep universopunzadas"

echo "→ Hecho. Verifica en el navegador o con:"
echo "   curl -s -o /dev/null -w '%{http_code}\n' https://universopunzadas.com/"
