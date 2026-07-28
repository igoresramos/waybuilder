#!/usr/bin/env bash
# Copia o payload do pipeline para public/, que e o que o navegador serve.
#
# A BASE INTEIRA -- os 54 kinds, 1,09 MB gzip. Ate 2026-07-28 vinham so os oito
# kinds que montam ficha, para segurar a carga inicial em 0,53 MB. O corte
# custava caro e em silencio: o motor calcula ataque e dano por arma, CA com cap
# de DEX e escudo, tabela de slots das 11 classes conjuradoras e ficha de
# companheiro -- e nada disso tinha dado no app. A aba de Ataques era
# eternamente vazia e todo personagem saia sem armadura, nao porque o motor
# errasse, mas porque o payload nao levava as armas.
#
# 1,09 MB num PWA que cacheia na primeira visita nao e problema; um construtor
# que nao sabe o que e uma espada, e.
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

rm -rf "$DESTINO"
mkdir -p "$DESTINO/por-kind" "$DESTINO/text"

cp "$ORIGEM"/por-kind/*.json "$DESTINO/por-kind/"
cp "$ORIGEM/_manifesto.json" "$DESTINO/"

# a prosa continua fora da carga inicial: ela sozinha e maior que o indice
# inteiro, e o app busca o texto de um registro so quando o jogador o abre.
cp ../pipeline/base/text/*.json "$DESTINO/text/"

kinds=$(ls "$DESTINO/por-kind" | wc -l)
cru=$(du -sb "$DESTINO/por-kind" | cut -f1)
comprimido=$(cat "$DESTINO"/por-kind/*.json | gzip -c | wc -c)
echo "base: $kinds kinds, $(( cru / 1024 )) KB crus, $(( comprimido / 1024 )) KB gzip"
echo "prosa: $(du -sh "$DESTINO/text" | cut -f1) (sob demanda, fora da carga inicial)"
echo "-> $DESTINO/"
