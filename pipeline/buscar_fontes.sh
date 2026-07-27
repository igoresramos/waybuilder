#!/usr/bin/env bash
# Reconstroi as fontes externas que nao cabem no git, nos pins da spec
# (specs/2026-07-26-schema-base.md). Idempotente: se ja existe no pin certo,
# nao faz nada.
#
# Motivo de existir: ate 2026-07-26 o clone do Foundry vivia num diretorio de
# scratchpad de sessao (/tmp/...). A sessao acabou, o clone sumiu, e 7 dos 10
# extratores pararam de rodar sem que nada no repo registrasse a dependencia.
set -euo pipefail

AQUI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BRUTOS="$AQUI/dados_brutos"

FOUNDRY_PIN="87f9e5028baaa10b70fdc766260b7886def17e04"
FOUNDRY_DIR="$BRUTOS/foundry_repo"

mkdir -p "$BRUTOS"

if [ -d "$FOUNDRY_DIR/.git" ]; then
  atual="$(git -C "$FOUNDRY_DIR" rev-parse HEAD)"
  if [ "$atual" = "$FOUNDRY_PIN" ]; then
    echo "foundry: ja no pin $FOUNDRY_PIN"
  else
    echo "foundry: HEAD em $atual, movendo para o pin"
    git -C "$FOUNDRY_DIR" fetch --filter=blob:none origin "$FOUNDRY_PIN"
    git -C "$FOUNDRY_DIR" checkout "$FOUNDRY_PIN"
  fi
else
  echo "foundry: clonando no pin $FOUNDRY_PIN (~615 MB, so packs/)"
  git clone --filter=blob:none --no-checkout \
    https://github.com/foundryvtt/pf2e.git "$FOUNDRY_DIR"
  git -C "$FOUNDRY_DIR" sparse-checkout init --cone
  git -C "$FOUNDRY_DIR" sparse-checkout set packs
  git -C "$FOUNDRY_DIR" checkout "$FOUNDRY_PIN"
fi

n=$(find "$FOUNDRY_DIR/packs/pf2e" -name '*.json' | wc -l)
echo "foundry: $n arquivos em packs/pf2e"
[ "$n" -gt 20000 ] || { echo "ERRO: checkout incompleto"; exit 1; }

# --------------------------------------------------------------------------
# pf2etools
# --------------------------------------------------------------------------
# Ate 2026-07-26 esta fonte vivia como 242 arquivos baixados um a um por HTTP,
# adivinhando nomes -- daí os 50 arquivos `.json.missing`, que sao chutes de
# nome que nao existem no repo, nao conteudo faltando. O repo tem 524 arquivos.
# `requires` tem precedencia pf2etools, entao rodar com 46% da fonte significa
# construir o predicado -- onde a houserule mora -- sobre dado parcial.
#
# ATENCAO: o repo vivo e `Pf2eToolsOrg/Pf2eTools`. `Pf2ools` (sem o "e") e um
# repo morto.
PF2E_TOOLS_PIN="7d1ec43f84437b43668cd677265f42b8e9a0bb05"   # dev, 2026-06-07
PF2E_TOOLS_REPO="$BRUTOS/pf2etools_repo"
PF2E_TOOLS_DIR="$BRUTOS/pf2etools"

if [ -d "$PF2E_TOOLS_REPO/.git" ]; then
  atual="$(git -C "$PF2E_TOOLS_REPO" rev-parse HEAD)"
  if [ "$atual" = "$PF2E_TOOLS_PIN" ]; then
    echo "pf2etools: ja no pin $PF2E_TOOLS_PIN"
  else
    echo "pf2etools: HEAD em $atual, movendo para o pin"
    git -C "$PF2E_TOOLS_REPO" fetch --depth 1 origin "$PF2E_TOOLS_PIN"
    git -C "$PF2E_TOOLS_REPO" checkout "$PF2E_TOOLS_PIN"
  fi
else
  echo "pf2etools: clonando"
  git clone --depth 1 --branch dev \
    https://github.com/Pf2eToolsOrg/Pf2eTools.git "$PF2E_TOOLS_REPO"
fi

# Os extratores esperam tudo achatado em pf2etools/, com ancestries/ e
# backgrounds/ em subpasta. Espelhar a convencao em vez de reescrever 7
# extratores.
echo "pf2etools: espelhando data/ para a convencao dos extratores"
mkdir -p "$PF2E_TOOLS_DIR"
for sub in class feats items spells optionalfeatures; do
  [ -d "$PF2E_TOOLS_REPO/data/$sub" ] && cp -f "$PF2E_TOOLS_REPO/data/$sub/"*.json "$PF2E_TOOLS_DIR/" 2>/dev/null || true
done
cp -f "$PF2E_TOOLS_REPO/data/"*.json "$PF2E_TOOLS_DIR/" 2>/dev/null || true
for sub in ancestries backgrounds; do
  mkdir -p "$PF2E_TOOLS_DIR/$sub"
  cp -f "$PF2E_TOOLS_REPO/data/$sub/"*.json "$PF2E_TOOLS_DIR/$sub/" 2>/dev/null || true
done
# marcadores de tentativa de download antiga: nao sao conteudo
find "$PF2E_TOOLS_DIR" -name '*.json.missing' -delete

n_pf=$(find "$PF2E_TOOLS_DIR" -name '*.json' | wc -l)
echo "pf2etools: $n_pf arquivos JSON"
# 382 e o total em escopo. Os 524 do repo incluem bestiary/ (129), book/ (5),
# generated/ (4) e adventure/ (1), que a spec poe fora de escopo.
[ "$n_pf" -ge 380 ] || { echo "ERRO: espelhamento incompleto"; exit 1; }

echo "ok"
