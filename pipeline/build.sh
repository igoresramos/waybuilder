#!/usr/bin/env bash
# Build da base canonica, na ordem correta.
#
# A ordem importa e nao e obvia:
#   - `emitir_textos` roda ANTES de `fundir_renomeados`, porque a fusao usa
#     prosa para desempatar sucessor multiplo. Rodar fora de ordem faz o
#     desempate acontecer com prosa vazia, em silencio.
#   - o portao 7 roda ANTES da fusao. Depois dela a duplicata ja virou um
#     registro so e o portao passa por construcao -- era o defeito da primeira
#     versao.
#   - `desmembrar_colisoes` roda antes de `emitir_textos` para que os irmaos
#     criados tambem ganhem prosa.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

echo "== 0. fontes fixadas =="
./buscar_fontes.sh
[ -d dados_brutos/aon_dump ] || python3 dump_aon.py

echo "== 1. extratores =="
if [ "${WB_REEXTRAIR:-0}" = "1" ]; then
  for e in classes feats magias ancestrias equipamento companheiros referencia rituais aon_kinds; do
    echo "-- $e"
    python3 "extratores/$e.py"
  done
else
  echo "(pulado -- exporte WB_REEXTRAIR=1 para re-extrair das fontes)"
fi

echo "== 2. reconciliar =="
python3 reconciliar.py || true      # portao 5 ainda falha em 3 registros orfaos

echo "== 3. auditar divergencia entre fontes =="
python3 auditar_conflitos.py

echo "== 4. desmembrar colisoes de identidade =="
python3 desmembrar_colisoes.py

echo "== 4b. injetar tabela de conjuracao nas classes =="
python3 aplicar_conjuracao.py

echo "== 4c. separar sub-escolha de concessao na progressao =="
python3 aplicar_subclasses.py

echo "== 4d. resolver referencias orfas do predicado =="
python3 resolver_referencias.py

echo "== 4e. derivar o gate de nivel (class_level x character_level) =="
python3 derivar_gate_nivel.py

echo "== 4f. ensinar o predicado a falar de subclasse =="
python3 derivar_subclasse.py

echo "== 4g. unificar o modelo de efeito em grants =="
python3 unificar_efeitos.py

echo "== 4h. converter rule elements declarativos =="
python3 converter_rule_elements.py

echo "== 5. emitir prosa =="
python3 emitir_textos.py

echo "== 6. portoes, fase pre-fusao =="
python3 portoes.py --fase pre-fusao || true

echo "== 7. fundir legacy/remaster =="
python3 fundir_renomeados.py

echo "== 7b. normalizar traits na base inteira =="
# depois do ULTIMO escritor de index.json: auditar_conflitos e
# desmembrar_colisoes criam conflito de traits depois da reparacao que roda
# dentro do reconciliador, e registro de fonte unica nunca passava pela
# normalizacao. Aqui a garantia vale para a base toda.
python3 normalizar_traits.py

echo "== 8. portoes, fase final =="
python3 portoes.py --fase final

echo "== 9. emitir o payload do app =="
# ultimo passo, e depois dos portoes de proposito: o que o cliente carrega e
# DERIVADO da base auditada, nunca o contrario. Corta metadado de build (prov,
# xref, conflitos) e a prosa que vazou inline.
python3 emitir_app.py
