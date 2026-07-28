#!/usr/bin/env bash
# Copia o payload do pipeline para public/, que e o que o navegador serve.
#
# So o NUCLEO -- o que a fatia 1 precisa para montar ficha. O indice completo
# tem 54 kinds e 9,4 MB crus; equipamento, magia e catalogo de referencia
# entram sob demanda, quando a tela que os usa existir.
#
# `public/base/` e gitignored: e derivado de pipeline/base/app/, que por sua
# vez e derivado de base/index.json. Rode `pipeline/build.sh` antes se a base
# mudou.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

ORIGEM="../pipeline/base/app"
DESTINO="public/base"

if [ ! -d "$ORIGEM" ]; then
  echo "!! $ORIGEM nao existe -- rode pipeline/build.sh (passo 9)" >&2
  exit 1
fi

# os kinds que montam ficha. Fora daqui: equipment, weapon, armor, shield,
# spell, ritual, relic, deity, trait, e as 28 sub-escolhas promovidas a kind.
NUCLEO=(class class-feature feat ancestry heritage background archetype skill)

rm -rf "$DESTINO"
mkdir -p "$DESTINO/por-kind"

for kind in "${NUCLEO[@]}"; do
  arquivo="$ORIGEM/por-kind/$kind.json"
  if [ -f "$arquivo" ]; then
    cp "$arquivo" "$DESTINO/por-kind/"
  else
    echo "!! kind ausente no payload: $kind" >&2
    exit 1
  fi
done

cp "$ORIGEM/_manifesto.json" "$DESTINO/"

# a prosa das sub-escolhas nao entra: o texto e buscado por registro, e a fatia
# 1 mostra so nome e mecanica
mkdir -p "$DESTINO/text"
for kind in "${NUCLEO[@]}"; do
  [ -f "../pipeline/base/text/$kind.json" ] && cp "../pipeline/base/text/$kind.json" "$DESTINO/text/"
done

cru=$(du -sb "$DESTINO/por-kind" | cut -f1)
comprimido=$(cat "$DESTINO"/por-kind/*.json | gzip -c | wc -c)
echo "nucleo: $(( cru / 1024 )) KB crus, $(( comprimido / 1024 )) KB gzip"
echo "prosa:  $(du -sh "$DESTINO/text" | cut -f1) (sob demanda, nao entra na carga inicial)"
echo "-> $DESTINO/"
