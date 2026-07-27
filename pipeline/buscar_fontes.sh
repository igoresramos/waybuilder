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

# pf2etools e AoN: dumps versionados em dados_brutos/, nada a fazer aqui.
# Se um dia sairem do git, e aqui que a reconstrucao entra.
echo "ok"
