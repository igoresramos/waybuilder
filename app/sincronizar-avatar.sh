#!/usr/bin/env bash
# Copia o acervo do avatar para public/, que e o que o navegador serve.
#
# Os assets vem do pacote `waybuilder-avatar` (repo proprio, pinado no
# package-lock). Vite NAO serve arquivo de dentro de node_modules -- por isso a
# copia, no mesmo espirito de `sincronizar-base.sh`.
#
# Sao 469 PNGs de atlas, ~9 MB: um por (slot, camada, corpo). Ate a
# consolidacao eram 2.800, e o precache do service worker so ativa quando TODOS
# baixam.
#
# `public/avatar/` e gitignored: e derivado do pacote.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

ORIGEM="node_modules/waybuilder-avatar/saida"
DESTINO="public/avatar"

if [ ! -d "$ORIGEM" ]; then
  echo "!! $ORIGEM nao existe -- rode npm install" >&2
  exit 1
fi

rm -rf "$DESTINO"
mkdir -p "$DESTINO"
cp -r "$ORIGEM"/. "$DESTINO"/

n=$(find "$DESTINO" -type f | wc -l)
mb=$(du -sm "$DESTINO" | cut -f1)
echo "avatar sincronizado: $n arquivos, ${mb} MB -> $DESTINO"
