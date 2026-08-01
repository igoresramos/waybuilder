#!/usr/bin/env bash
#
# Roda TODOS os mecanismos de verificacao do projeto e imprime um placar.
#
# Por que existe: em 01/08 havia SETE mecanismos de verificacao e nenhum
# comando que rodasse os sete. Nao ha `.github/`, nao ha git hook, e
# `app/package.json` nao tem script `test` -- conferido nesse dia. Na pratica
# isso significa que a unica forma de saber o estado era lembrar de sete
# comandos diferentes, e o que se mede por memoria nao se mede.
#
# O que NAO faz: nao roda `pipeline/build.sh`. O build reescreve
# `pipeline/base/index.json`, que e a entrada de quase todo mecanismo daqui --
# rodar os dois juntos misturaria "a base mudou" com "o verificador acusou", que
# sao perguntas diferentes. Este script mede a base que esta no disco AGORA.
#
# Efeito colateral conhecido, de proposito: alguns mecanismos gravam relatorio
# (`pipeline/base/relatorio_portoes_final.md`,
# `docs/2026-07-27_validacao-iconics.md`, e os `.png` das sondas de navegador).
# Rodar isto suja a arvore de trabalho. E o comportamento dos mecanismos, nao
# deste script -- ele nao suprime a gravacao porque o relatorio E o detalhe que
# o placar resume.
#
# Tres estados, nunca dois:
#   OK      rodou e passou
#   FALHA   rodou e acusou
#   PULADO  NAO rodou (falta dependencia). Nunca conta como aprovacao -- e a
#           mesma regra do `NAO MEDIDO` dos portoes (pipeline/portoes.py:940-942):
#           mecanismo que se desliga sozinho e devolve verde passa por ausencia
#           de ferramenta, que e justamente o defeito que ele existiria para
#           pegar.
#
# Uso:
#   ./verificar.sh            tudo (navegador PULADO se nao estiver instalado)
#   ./verificar.sh --rapido   pula os mecanismos de navegador sem tentar
#   ./verificar.sh --listar   so lista os mecanismos e sai
#
# Codigo de saida: 0 so se TODO mecanismo que rodou passou. PULADO nao reprova
# (senao a maquina sem navegador nunca ficaria verde e o script seria
# desligado), mas aparece no placar em amarelo e o resumo diz quantos foram.

set -uo pipefail
# sem `-e` de proposito: o objetivo e rodar os sete e mostrar o placar inteiro.
# Com `-e` o script morreria no primeiro vermelho e esconderia os outros seis --
# que e exatamente o relatorio que interessa quando algo quebra.

cd "$(dirname "${BASH_SOURCE[0]}")"
RAIZ=$(pwd)
LOGS="$RAIZ/docs/_verificacao"
mkdir -p "$LOGS"

RAPIDO=0
for arg in "$@"; do
  case "$arg" in
    --rapido) RAPIDO=1 ;;
    --listar)
      printf '%s\n' \
        "portoes da base        pipeline/portoes.py --fase final" \
        "oraculo do motor       motor/teste_motor.py" \
        "unittest pipeline      pipeline/testes/" \
        "unittest motor         motor/testes/" \
        "vitest do porte TS     app/src/**/*.test.ts" \
        "sondas de navegador    app/verificacao/verificar-*.mjs" \
        "iconics da Paizo       motor/validar_iconics.py"
      exit 0 ;;
    *) echo "argumento desconhecido: $arg" >&2; exit 2 ;;
  esac
done

# cor so em terminal: redirecionar para arquivo nao deve encher de escapes
if [ -t 1 ]; then
  VERDE=$'\033[32m'; VERM=$'\033[31m'; AMAR=$'\033[33m'; NEG=$'\033[1m'; ZERO=$'\033[0m'
else
  VERDE=""; VERM=""; AMAR=""; NEG=""; ZERO=""
fi

NOMES=(); ESTADOS=(); CONTAGENS=(); TEMPOS=(); LOGDE=()

registrar() {  # nome, estado, contagem, segundos, log
  NOMES+=("$1"); ESTADOS+=("$2"); CONTAGENS+=("$3"); TEMPOS+=("$4"); LOGDE+=("$5")
  local marca
  case "$2" in
    OK)     marca="${VERDE}ok    ${ZERO}" ;;
    FALHA)  marca="${VERM}FALHA ${ZERO}" ;;
    *)      marca="${AMAR}pulado${ZERO}" ;;
  esac
  printf '  %s %-22s %s\n' "$marca" "$1" "$3"
}

# ---------------------------------------------------------------- 1. portoes
#
# Roda so a fase `final`. A fase `pre-fusao` mede um estado intermediario que
# so existe no meio do build (o portao 7 procura homonimo, e depois da fusao a
# duplicata virou um registro so) -- fora do build ela mediria a base errada.
echo
echo "${NEG}== 1/8  portoes da base ==${ZERO}"
LOG="$LOGS/1-portoes.log"; INI=$SECONDS
python3 pipeline/portoes.py --fase final >"$LOG" 2>&1; COD=$?
T=$((SECONDS - INI))
P_OK=$(grep -cE '^  portao [0-9]+ +OK' "$LOG")
P_FALHA=$(grep -cE '^  portao [0-9]+ +FALHA' "$LOG")
# `n/a` = portao que nao se aplica a esta fase; `??` = NAO MEDIDO por fonte
# ausente. Os dois entram na contagem para o placar nunca dizer "11/11" quando
# na verdade nove mediram.
P_NA=$(grep -cE '^  portao [0-9]+ +(n/a|\?\?)' "$LOG")
P_TOT=$((P_OK + P_FALHA + P_NA))
DET="$P_OK/$P_TOT passaram"
[ "$P_NA" -gt 0 ] && DET="$DET, $P_NA n/a"
[ "$P_FALHA" -gt 0 ] && DET="$DET, $P_FALHA FALHANDO"
registrar "portoes da base" "$([ $COD -eq 0 ] && echo OK || echo FALHA)" "$DET" "$T" "$LOG"

# ------------------------------------------------------- 2. oraculo do motor
echo
echo "${NEG}== 2/8  oraculo do motor ==${ZERO}"
LOG="$LOGS/2-oraculo.log"; INI=$SECONDS
python3 motor/teste_motor.py >"$LOG" 2>&1; COD=$?
T=$((SECONDS - INI))
# `checar()` imprime `  ok    <desc>` ou `  FALHA <desc>` (motor/teste_motor.py:25)
O_OK=$(grep -cE '^  ok    ' "$LOG")
O_FALHA=$(grep -cE '^  FALHA ' "$LOG")
registrar "oraculo do motor" "$([ $COD -eq 0 ] && echo OK || echo FALHA)" \
          "$((O_OK)) assercoes ok$([ "$O_FALHA" -gt 0 ] && echo ", $O_FALHA FALHANDO")" "$T" "$LOG"

# ----------------------------------------------------- 3 e 4. suites unittest
#
# `-t .` (top level) e obrigatorio: os testes se importam como
# `pipeline.testes.test_x`, entao a raiz do projeto tem de ser a raiz de
# descoberta. Sem isso o import do pacote falha antes de rodar um teste.
suite_unittest() {  # rotulo, diretorio, numero
  local rotulo="$1" dir="$2" num="$3"
  echo
  echo "${NEG}== $num/8  $rotulo ==${ZERO}"
  local log="$LOGS/$num-$(echo "$rotulo" | tr ' /' '--').log"
  local ini=$SECONDS
  python3 -m unittest discover -s "$dir" -t . >"$log" 2>&1
  local cod=$? t=$((SECONDS - ini))
  local total falhas erros esperadas det
  total=$(grep -oE '^Ran [0-9]+ test' "$log" | grep -oE '[0-9]+' | head -1)
  total=${total:-0}
  falhas=$(grep -oE 'failures=[0-9]+' "$log" | grep -oE '[0-9]+' | head -1)
  erros=$(grep -oE 'errors=[0-9]+' "$log" | grep -oE '[0-9]+' | head -1)
  # `expected failures` sao falhas DECLARADAS: o unittest sai 0 com elas, e sao
  # divida conhecida e registrada, nao regressao. Aparecem no placar para nao
  # sumirem de vista, mas nao pintam de vermelho.
  esperadas=$(grep -oE 'expected failures=[0-9]+' "$log" | grep -oE '[0-9]+' | head -1)
  det="$((total - ${falhas:-0} - ${erros:-0}))/$total passaram"
  [ -n "${esperadas:-}" ] && det="$det, $esperadas falha(s) declarada(s)"
  [ -n "${falhas:-}" ] && det="$det, ${falhas} FALHANDO"
  [ -n "${erros:-}" ] && det="$det, ${erros} ERRO"
  registrar "$rotulo" "$([ $cod -eq 0 ] && echo OK || echo FALHA)" "$det" "$t" "$log"
}
suite_unittest "unittest pipeline" pipeline/testes 3
suite_unittest "unittest motor" motor/testes 4

# ------------------------------------------------------------- 5. vitest (TS)
#
# O porte TS tem de derivar ficha IDENTICA a do motor Python -- e o
# `motor.test.ts` compara os dois campo a campo. Ele so falha por divergencia
# real entre as duas implementacoes, entao vermelho aqui significa que app e
# oraculo discordam.
echo
echo "${NEG}== 5/8  vitest do porte TS ==${ZERO}"
LOG="$LOGS/5-vitest.log"; INI=$SECONDS
if [ ! -d app/node_modules ]; then
  registrar "vitest do porte TS" PULADO "app/node_modules ausente -- rode 'npm ci' em app/" 0 "-"
else
  ( cd app && npx vitest run ) >"$LOG" 2>&1; COD=$?
  T=$((SECONDS - INI))
  # linha do vitest: "  Tests  1 failed | 145 passed (146)"
  V_LINHA=$(grep -E '^ *Tests +' "$LOG" | tail -1)
  V_TOT=$(printf '%s' "$V_LINHA" | grep -oE '\([0-9]+\)$' | tr -dc '0-9')
  V_PASS=$(printf '%s' "$V_LINHA" | grep -oE '[0-9]+ passed' | grep -oE '[0-9]+')
  V_FAIL=$(printf '%s' "$V_LINHA" | grep -oE '[0-9]+ failed' | grep -oE '[0-9]+')
  DET="${V_PASS:-0}/${V_TOT:-0} passaram"
  [ -n "${V_FAIL:-}" ] && DET="$DET, $V_FAIL FALHANDO"
  [ -z "$V_LINHA" ] && DET="vitest nao chegou a rodar -- ver $LOG"
  registrar "vitest do porte TS" "$([ $COD -eq 0 ] && echo OK || echo FALHA)" "$DET" "$T" "$LOG"
fi

# --------------------------------------------------- 6. sondas de navegador
#
# Os `verificar-*.mjs` provam no DOM o que nenhum teste de motor alcanca (que o
# numero certo CHEGA na tela). Custam duas dependencias que nao vem de graca:
# o binario do Chromium do Playwright e um servidor de dev de pe.
#
# Se o binario nao estiver instalado isto e PULADO, e nunca verde. A tentacao
# de contar "0 falhas" como aprovacao e o modo classico de um verificador
# mentir: `npm ci` nao baixa o navegador (ele vem de `npx playwright install`),
# entao a maquina limpa e exatamente o caso em que o falso verde apareceria.
echo
echo "${NEG}== 6/8  sondas de navegador (app/verificacao) ==${ZERO}"
SONDAS=(app/verificacao/verificar-*.mjs)
N_SONDAS=${#SONDAS[@]}
PORTA=5175
if [ "$RAPIDO" = "1" ]; then
  registrar "sondas de navegador" PULADO "$N_SONDAS script(s) -- --rapido" 0 "-"
elif [ ! -d app/node_modules ]; then
  registrar "sondas de navegador" PULADO "$N_SONDAS script(s) -- app/node_modules ausente" 0 "-"
elif ! ( cd app && node -e '
    import("playwright").then(async (p) => {
      // a sonda e um launch de verdade, nao um existsSync: `chromium.launch()`
      // usa o `chrome-headless-shell`, que e um download SEPARADO do
      // `chromium` -- checar o caminho do segundo daria instalado com o
      // primeiro faltando, e o PULADO viraria FALHA sem motivo.
      const nav = await p.chromium.launch();
      await nav.close();
    }).then(() => process.exit(0), () => process.exit(1));
  ' >/dev/null 2>&1 ); then
  registrar "sondas de navegador" PULADO \
            "$N_SONDAS script(s) -- sem navegador: 'npx playwright install chromium' em app/" 0 "-"
else
  LOG="$LOGS/6-sondas.log"; : >"$LOG"; INI=$SECONDS
  # `--strictPort`: sem isso o vite escorrega para a proxima porta livre e as
  # sondas iriam bater num servidor que nao e o nosso -- ou em nada.
  ( cd app && npx vite --port "$PORTA" --strictPort ) >"$LOGS/6-servidor.log" 2>&1 &
  SERVIDOR=$!
  trap '[ -n "${SERVIDOR:-}" ] && kill "$SERVIDOR" 2>/dev/null' EXIT
  DE_PE=0
  for _ in $(seq 1 60); do
    if curl -fsS "http://localhost:$PORTA/" >/dev/null 2>&1; then DE_PE=1; break; fi
    sleep 1
  done
  if [ "$DE_PE" = "0" ]; then
    registrar "sondas de navegador" PULADO \
              "$N_SONDAS script(s) -- dev server nao subiu na porta $PORTA" \
              "$((SECONDS - INI))" "$LOGS/6-servidor.log"
  else
    S_OK=0; S_FALHA=0; NOMES_RUINS=()
    for s in "${SONDAS[@]}"; do
      # a URL vai EXPLICITA: dois scripts trazem porta default diferente
      # (5173 em verificar-slots-de-criacao.mjs, 5175 no resto), e deixar o
      # default decidir faria um deles bater em porta vazia e reprovar sozinho.
      echo "### $s" >>"$LOG"
      if ( cd app && node "verificacao/$(basename "$s")" "http://localhost:$PORTA/" ) >>"$LOG" 2>&1; then
        S_OK=$((S_OK + 1)); echo "  ok"
      else
        S_FALHA=$((S_FALHA + 1)); NOMES_RUINS+=("$(basename "$s" .mjs)")
        echo "  FALHA $(basename "$s")"
      fi
    done
    T=$((SECONDS - INI))
    DET="$S_OK/$N_SONDAS passaram"
    [ "$S_FALHA" -gt 0 ] && DET="$DET, FALHANDO: ${NOMES_RUINS[*]}"
    registrar "sondas de navegador" "$([ "$S_FALHA" -eq 0 ] && echo OK || echo FALHA)" "$DET" "$T" "$LOG"
  fi
  kill "$SERVIDOR" 2>/dev/null; wait "$SERVIDOR" 2>/dev/null; SERVIDOR=""
  trap - EXIT
fi

# ------------------------------------------------------- 7. iconics da Paizo
#
# ATENCAO ao ler o vermelho daqui: este mecanismo NAO e um portao, e o codigo de
# saida dele nao se comporta como um. `motor/validar_iconics.py:600` faz
# `return 0 if not divergencias and not diverg_pericias else 1`, e em 01/08
# ha 723 divergencias de pericia que o proprio relatorio do arquivo documenta
# como fonte oficial INCOMPLETA, nao como erro do motor (o `system.skills` do
# ator so guarda a escolha discricionaria, nao o treino automatico). Ou seja:
# ele nao tem como sair 0, hoje nem depois de qualquer correcao no motor.
#
# Por isso o placar o separa. Ele conta como MEDICAO, imprime o numero que o
# README rastreia (HP que bate / avaliados), e nao reprova o script sozinho.
# Contar um sempre-vermelho como reprovacao seria o caminho mais curto para
# alguem desligar o verificador inteiro na primeira semana -- que e o risco que
# `pipeline/portoes.py:865` nomeia. O que ele PRECISA, para virar portao de
# verdade, e linha de base como a dos portoes 4 e 11: vermelho quando PIORA,
# nao quando diverge. Isso pede spec propria e nao esta feito.
echo
echo "${NEG}== 7/8  iconics da Paizo (medicao) ==${ZERO}"
LOG="$LOGS/7-iconics.log"; INI=$SECONDS
python3 motor/validar_iconics.py >"$LOG" 2>&1; COD=$?
T=$((SECONDS - INI))
I_BATE=$(grep -oE 'hp bate +[0-9]+' "$LOG" | grep -oE '[0-9]+$')
I_DIV=$(grep -oE 'hp diverge +[0-9]+' "$LOG" | grep -oE '[0-9]+$')
I_AVAL=$(grep -oE 'personagens avaliados: [0-9]+' "$LOG" | grep -oE '[0-9]+')
I_PER=$(grep -oE 'bate +[0-9]+ \([0-9.]+%\)' "$LOG" | grep -oE '[0-9.]+%' | head -1)
if [ $COD -eq 0 ]; then
  ESTADO_ICON=OK
  DET_ICON="sem divergencia (hp ${I_BATE:-?}/${I_AVAL:-?})"
else
  # medicao, nao reprovacao -- ver o bloco de comentario acima
  ESTADO_ICON=MEDIDO
  DET_ICON="hp ${I_BATE:-?} bate / ${I_DIV:-?} diverge de ${I_AVAL:-?}; pericia ${I_PER:-?}"
fi
NOMES+=("iconics da Paizo"); ESTADOS+=("$ESTADO_ICON"); CONTAGENS+=("$DET_ICON")
TEMPOS+=("$T"); LOGDE+=("$LOG")
printf '  %s %-22s %s\n' "${AMAR}medido${ZERO}" "iconics da Paizo" "$DET_ICON"

# ------------------------------------------------------------------- placar
FALHOU=0; PULOU=0; PASSOU=0
# ------------------------------------------------------------ 8. portao das specs
#
# Nao e portao de DADO: ele nao olha `base/index.json`, olha o frontmatter das
# specs. Por isso nao entra no `build.sh` -- o lugar dele e aqui, junto dos
# outros mecanismos. Ver `specs/CONVENCAO.md`.
#
# Custa menos de um segundo, entao roda sempre: nao tem modo `--rapido`.
echo
echo "${NEG}== 8/8  portao das specs ==${ZERO}"
LOG="$LOGS/8-specs.log"; INI=$SECONDS
python3 pipeline/verificar_specs.py >"$LOG" 2>&1; COD=$?
T=$((SECONDS - INI))
# linha final do script: "specs: 76 -- 75 implementada, 1 rascunho"
E_LINHA=$(grep -E '^specs: ' "$LOG" | tail -1)
E_FALHAS=$(grep -oE 'PORTAO DE SPECS: [0-9]+' "$LOG" | grep -oE '[0-9]+' | head -1)
DET="${E_LINHA#specs: }"
[ -n "${E_FALHAS:-}" ] && DET="$DET, $E_FALHAS FALHANDO"
[ -z "$E_LINHA" ] && DET="nao chegou a rodar -- ver $LOG"
registrar "portao das specs" "$([ $COD -eq 0 ] && echo OK || echo FALHA)" "$DET" "$T" "$LOG"

echo
echo "${NEG}=================== PLACAR ===================${ZERO}"
printf '%-24s %-8s %6s  %s\n' "MECANISMO" "ESTADO" "SEG" "CONTAGEM"
for i in "${!NOMES[@]}"; do
  case "${ESTADOS[$i]}" in
    OK)     cor="$VERDE"; PASSOU=$((PASSOU + 1)) ;;
    FALHA)  cor="$VERM";  FALHOU=$((FALHOU + 1)) ;;
    PULADO) cor="$AMAR";  PULOU=$((PULOU + 1)) ;;
    *)      cor="$AMAR" ;;   # MEDIDO
  esac
  printf '%-24s %s%-8s%s %6s  %s\n' \
    "${NOMES[$i]}" "$cor" "${ESTADOS[$i]}" "$ZERO" "${TEMPOS[$i]}" "${CONTAGENS[$i]}"
done
echo "${NEG}=============================================${ZERO}"
echo "  $PASSOU verde, $FALHOU vermelho, $PULOU pulado, 1 medicao"
echo "  logs completos em docs/_verificacao/"

if [ "$PULOU" -gt 0 ]; then
  echo
  echo "  ${AMAR}$PULOU mecanismo(s) NAO rodaram.${ZERO} Pulado nao e aprovado --"
  echo "  o placar acima nao diz nada sobre eles."
fi
if [ "$FALHOU" -gt 0 ]; then
  echo
  echo "  ${VERM}$FALHOU mecanismo(s) acusaram:${ZERO}"
  for i in "${!NOMES[@]}"; do
    [ "${ESTADOS[$i]}" = "FALHA" ] && echo "    - ${NOMES[$i]}: ${CONTAGENS[$i]}  (${LOGDE[$i]})"
  done
  exit 1
fi
exit 0
