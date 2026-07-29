#!/usr/bin/env bash
# Reconstroi a copia local do Pathbuilder 2e a partir do CDN publico.
#
# Os dois arquivos de DADOS (7,6 MB juntos) ficam fora do git: cada versao nova
# do app troca o nome do arquivo (`data131` -> `data_remastered71` -> ...), e
# versionar cada uma soma alguns MB permanentes no historico de um repo que ja
# passou por uma reescrita por peso. O resto dos assets e pequeno e continua
# versionado, porque e o que faz a copia abrir.
#
# Mesmo criterio de `pipeline/dados_brutos/`: reconstruivel por receita fica
# fora; o que exigiu julgamento humano fica dentro.
#
# Uso: bash docs/referencia-pathbuilder/app-local/baixar-assets.sh
set -euo pipefail

CDN="https://pathbuilder2e-data.b-cdn.net"
AQUI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DESTINO="$AQUI/assets"

# so os que o .gitignore exclui -- o resto ja esta no repo
DADOS=(data131.txt data_remastered71.txt)

mkdir -p "$DESTINO"
for arquivo in "${DADOS[@]}"; do
  if [ -s "$DESTINO/$arquivo" ]; then
    echo "ja existe: $arquivo"
    continue
  fi
  echo -n "baixando $arquivo ... "
  curl -sSf -o "$DESTINO/$arquivo" "$CDN/$arquivo"
  echo "$(du -h "$DESTINO/$arquivo" | cut -f1)"
done

echo "-> $DESTINO"
echo "rodar: cd app && node verificacao/pathbuilder-local.mjs"
