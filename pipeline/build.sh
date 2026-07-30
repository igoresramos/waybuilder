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
  # `taticas_kits` DEPOIS de `aon_kinds`: ele monta o envelope com
  # `aon_kinds.converter()`, entao mudanca de schema la chega aqui de carona --
  # e ficar fora do laco fazia a saida em disco envelhecer em silencio (a de
  # 27/07 sobreviveu a spec de `grants_completos`, de 29/07).
  # `magias` roda por `_gerar_saida_magias.py`, e nao por `magias.py`: o
  # segundo so devolve a lista e IMPRIME a contagem -- o `__main__` dele nao
  # escreve arquivo nenhum. Chamar `magias.py` aqui era um no-op silencioso, e
  # por isso `saida/magias.json` ficou parado em 27/07 atravessando todos os
  # builds desde entao. Mesma classe do `taticas_kits`, que estava FORA do laco.
  for e in classes feats _gerar_saida_magias ancestrias equipamento companheiros referencia rituais aon_kinds taticas_kits; do
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

echo "== 4h2. gate de arquetipo (regra do livro que a fonte deixa implicita) =="
# "You can't select a feat from an archetype unless you have its dedication
# feat" -- escrito uma vez no livro e em nenhum `requires`. Sem este passo da
# para pegar feat avancado de arquetipo sem nunca ter pego a dedicacao.
python3 derivar_gate_arquetipo.py

echo "== 4h4. recuperar mecanica de equipamento nao casada =="
# nao e falta de fonte, e falha de matching: o Foundry escreve `Leather Armor`
# onde o AoN escreve `Leather`, e `Fist`/`Shield Bash` so existem no dump do
# AoN. Sem este passo, equipar couro nao mudava a CA.
python3 recuperar_mecanica_equipamento.py

echo "== 4h5. condicao de acesso (filiacao) lida do AoN =="
# 728 registros so estao disponiveis para quem tem certa filiacao ("Member of
# the Pathfinder Society", "Tian Xia origin") e a base nao carregava nada disso.
# O AoN publica `access` como campo -- e leitura, nao prosa.
python3 aplicar_acesso.py

echo "== 4h5b. beneficio dos backgrounds que ficaram vazios =="
# 10 backgrounds tinham boosts E skill_training vazios -- escolher `Refugee` nao
# mudava numero nenhum. Nao existem no Foundry; entraram pelo AoN, que tem
# `attribute` e `skill` em nove deles.
python3 aplicar_beneficio_de_background.py

echo "== 4h6. ranks de elevacao da magia, lidos do AoN =="
# `heightened` vazio significava "nao eleva" E "nao sei" ao mesmo tempo. O AoN
# publica `heighten_level` nos 2.461 docs: das 1.125 vazias, 664 estao certas e
# 461 sao lacuna de verdade.
python3 aplicar_ranks_de_magia.py

echo "== 4i. aplicar correcoes curadas =="
# o que exigiu leitura da prosa oficial porque as tres fontes estao vazias no
# ponto. Cada entrada declara o valor que ESPERA achar: se a fonte consertar o
# dado, este passo falha alto em vez de sobrescrever em silencio.
python3 aplicar_curadoria.py

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

echo "== 7c. aplicar aliases do remaster dentro de requires e subclasses =="
# DEPOIS DA FUSAO, e nao antes. Quem aposenta o id e a fusao (passo 7): rodando
# em 4h3 o script olhava uma base em que `metamagical-experimentation` ainda
# existia, nao via orfa nenhuma, e a fusao criava a orfa em seguida -- sem
# ninguem para voltar e reescrever quem citava o morto. O eixo `arcane-thesis`
# do Mago saia com uma opcao apontando para o nada.
python3 aplicar_aliases_em_requires.py

echo "== 7c2. grau legado que a fusao principal nao alcanca =="
# O AoN declara `remaster_id` so no doc BASE, entao `Cloak of Elvenkind
# (Greater)` ficava de pe ao lado de `Cloak of Illusions (Greater)` -- mesmo
# item, nivel 12, duas vezes. Depende dos aliases que a fusao (7) escreveu.
python3 fundir_graus_legados.py

echo "== 7c3. nome antigo como alias, fora de magia =="
# Achado na 4a rodada do Pathbuilder: `Desperate Wrath` nao carregava `Reckless
# Abandon`, entao quem digitasse o nome antigo achava so o feat goblin homonimo.
# Em magia isso saiu em 30/07; fora dela continuava aberto. Roda DEPOIS da fusao,
# que e quem escreve os aliases do par declarado.
python3 derivar_alias_legado.py

echo "== 7d. uma opcao por nome em cada eixo de sub-escolha =="
# a mesma causa do Campeao existe como `wb:cause/justice` e como
# `wb:class-feature/justice`, em kinds diferentes -- a fusao nao os ve como
# par. Com o 7c na ordem certa os dois viram opcao viva, e a tela oferecia
# `Justice` duas vezes.
python3 colapsar_opcoes_irmas.py

echo "== 7d1b. sub-escolha que existe com dois ids =="
# O mesmo instinto entra pelo AoN (`wb:instinct/animal`) e pelo Foundry
# (`wb:class-feature/animal-instinct`); os 25 feats de instinto citam o segundo
# e a tela oferece o primeiro. Roda depois do 7d, que decide a opcao viva.
python3 derivar_equivalencia_de_subescolha.py

echo "== 7d2. tradicao de conjuracao da subclasse para a opcao viva =="
# O AoN publica `tradition` como campo no kind dedicado (`wb:bloodline/genie`),
# mas quem o jogador escolhe e a class-feature irma. Roda DEPOIS do 7d, que e
# quem decide qual dos dois irmaos e a opcao viva.
python3 derivar_tradicao_de_subclasse.py

echo "== 7d3. weapon expertise desmembrada por classe =="
# `wb:class-feature/weapon-expertise` e UM registro para 14 classes, e entre
# elas ha marciais e nao-marciais. O Campeao 5 saia com `martial: trained` onde
# o livro diz expert -- dois pontos a menos em todo ataque com arma marcial.
python3 derivar_weapon_expertise.py

echo "== 7e. mecanica de dedicacao derivada da prosa oficial =="
# 61 dedicacoes chegam com `grants` vazio. Roda AQUI porque precisa da prosa
# (passo 5) e nao deve enriquecer registro que a fusao vai absorver (passo 7).
python3 derivar_mecanica_dedicacao.py

echo "== 7f. quem concede companheiro animal =="
# Sem isto, nenhum feat da base diz "eu concedo um companheiro" e o ator so
# entra por `doc[\"atores\"]` escrito a mao. Mesma janela do 7e: depois da prosa
# (5) e depois da fusao (7).
python3 derivar_concessao_de_ator.py

echo "== 7g. quem concede conjuracao de arquetipo =="
# 13 dedicacoes prometem conjuracao na prosa e nao entregavam nada na ficha.
# A tabela de slots ja vive no motor (`RANK_DEDICACAO`, verbatim da regra); este
# passo diz QUEM esta na rota e por qual cadeia Basic/Expert/Master.
python3 derivar_spellcasting_arquetipo.py

echo "== 8. portoes, fase final =="
python3 portoes.py --fase final

echo "== 9. emitir o payload do app =="
# ultimo passo, e depois dos portoes de proposito: o que o cliente carrega e
# DERIVADO da base auditada, nunca o contrario. Corta metadado de build (prov,
# xref, conflitos) e a prosa que vazou inline.
python3 emitir_app.py
