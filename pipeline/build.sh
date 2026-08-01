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
  for e in classes feats _gerar_saida_magias ancestrias equipamento companheiros referencia rituais aon_kinds taticas_kits acoes; do
    echo "-- $e"
    python3 "extratores/$e.py"
  done
else
  echo "(pulado -- exporte WB_REEXTRAIR=1 para re-extrair das fontes)"
fi

echo "== 2. reconciliar =="
# `|| true` sozinho era o unico ponto cego do script: a intencao era tolerar o
# portao 5 (3 registros orfaos conhecidos), o efeito era tolerar QUALQUER morte.
# E `reconciliar.py` so grava index.json na ultima linha -- entao morrer antes
# disso deixava a base do build ANTERIOR intacta, e a cadeia inteira seguia
# mutando ela. Medido: 24 registros destruidos, 40 fabricados, 6.462 alterados,
# e dos 11 portoes so o 4 acusou.
# A tolerancia agora e explicita e verificada: o codigo de saida pode ser
# diferente de zero, mas o artefato TEM de ter sido reescrito nesta rodada.
_antes=$(stat -c %Y base/index.json 2>/dev/null || echo 0)
python3 reconciliar.py || echo "  reconciliar.py saiu != 0 (portao 5 conhecido) -- conferindo o artefato"
_depois=$(stat -c %Y base/index.json 2>/dev/null || echo 0)
if [ "$_depois" -le "$_antes" ]; then
  echo "!! reconciliar.py NAO reescreveu base/index.json -- morreu antes de gravar." >&2
  echo "!! seguir daqui mutaria a base do build anterior em silencio. Abortando." >&2
  exit 1
fi

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

echo "== 7c0. fundir duplicata de nome aon/foundry =="
# DEPOIS do portao 7 (pre-fusao), pela mesma razao que a fusao legacy/remaster:
# a fusao faz a duplicata virar um registro so, e rodar antes faria o portao
# passar por construcao.
# E DEPOIS de `normalizar_traits` (7b), o que a primeira versao errou: a regra
# de fusao exige `traits` IDENTICOS (fundir_duplicata_de_nome.py:305), e antes
# da normalizacao o lado AoN ainda carrega vocabulario legado (`necromancy`,
# `ifrit`). Rodando em 7a, 3 pares nao fundiam -- e o defeito era invisivel
# porque a base commitada tinha as 42 fusoes: o passo foi rodado A MAO sobre
# uma base ja normalizada, e so o build de ponta a ponta expos a diferenca.
# Achado por `comparar_bases.py`, que acusou 3 registros NASCIDOS no rebuild.
# Spec: specs/2026-08-01-fusao-de-duplicata-de-nome.md
python3 fundir_duplicata_de_nome.py

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

echo "== 7e0. eixo de ikon do Exemplar (o primeiro `escolhe: 3`) =="
# Antes do eixo de divindade so por ordem de leitura; os dois sao independentes.
# Depois da fusao, como todos os passos que emitem id: as opcoes sao os ids
# canonicos dos 21 ikons.
python3 derivar_eixo_de_ikon.py

echo "== 7e1. eixo de divindade nas classes que a exigem =="
# Depois da fusao e dos aliases: as opcoes sao os ids CANONICOS das 488
# divindades, e emitir antes pegaria id que a fusao ainda ia aposentar.
python3 derivar_escolha_de_divindade.py

echo "== 7e1b. santificacao: modal lido da prosa + eixo filtrado =="
# DEPOIS do eixo de divindade: as opcoes daqui respondem pela divindade
# escolhida, e o `requires` de cada uma cita o termo `deity_sanctification`.
python3 derivar_santificacao.py

echo "== 7e1c. fonte divina: o par da santificacao, so no Clerigo =="
python3 derivar_fonte_divina.py

echo "== 7e1c2. colapsar irmas DE NOVO, agora que os eixos novos existem =="
# O passo 7d roda antes de `derivar_escolha_de_divindade` (7e1), entao o eixo
# `deity` nao existia quando ele passou -- e `Ma'at` ficava DUAS vezes na lista
# do Campeao e do Clerigo (`wb:deity/maat` do remaster e `wb:deity/maat-ln` do
# Gods & Magic). Rodar de novo aqui alcanca os eixos criados em 7e1*, e e
# idempotente para os que ja foram colapsados.
python3 colapsar_opcoes_irmas.py

echo "== 7e1d. requisito de sub-escolha preso no residuo =="
# DEPOIS de todos os eixos existirem (divindade, santificacao, fonte, ikon): o
# mapa `<opcao> <eixo>` sai das proprias `subclasses`.
python3 derivar_requisito_de_subescolha.py

echo "== 7e1d2. pericia divina + clausulas de divindade no residuo =="
# Depois de `derivar_escolha_de_divindade.py` e da santificacao: `divine_skill`,
# `favored_weapon` e os dominios so existem na base aqui, e e por isso que a
# conversao nao cabe no parser de `feats.py`, que roda na EXTRACAO.
python3 derivar_requisito_de_divindade.py

echo "== 7e1e. parcelas de dano: weapon specialization e furia =="
# Depois do desmembramento de colisoes (os tres `Greater Weapon Specialization`
# tem ids diferentes) e depois de `aplicar_subclasses.py` (os gemeos de
# instinto ja existem para receber `rage_damage` pelos dois ids).
python3 derivar_parcelas_de_dano.py

echo "== 7e2. categoria de feat que sobrou vazia =="
# Roda TARDE de proposito: 8 dos 164 feats sem categoria nascem em
# `desmembrar_colisoes.py`, depois do extrator, e so um passo sobre a base
# inteira alcanca tanto esses quanto os que nao casaram com o AoN.
python3 derivar_categoria_de_feat.py

echo "== 7e1f. escolha aninhada: o balaio do Inventor vira eixo =="
# DEPOIS de `colapsar_opcoes_irmas` (7e1c2), que decide qual id de cada par e a
# opcao viva -- mover para o eixo antes disso moveria o irmao errado.
python3 derivar_escolha_aninhada.py

echo "== 7e2a. arquetipo do feat, lido da dedicacao no requires =="
# ANTES do gate de arquetipo nao da: `derivar_gate_arquetipo.py` roda no 4h2 e
# depende de `archetype` ja estar preenchido. Aqui e tarde de proposito -- o que
# se ganha e a lista do arquetipo e a procedencia, nao o gate.
python3 derivar_arquetipo_do_feat.py

echo "== 7e2b. tags do Foundry + eixos por query (Kineticist e Commander) =="
# ORDEM OBRIGATORIA: a tag entra na base ANTES de virar eixo. `item:tag` era
# ignorado pelo motor, e atomo ignorado conta como SATISFEITO -- o eixo sairia
# com os 19.604 registros dentro.
python3 derivar_eixo_por_tag.py

echo "== 7d3. variante por subclasse =="
# `Field Discovery (Bomber)` nao e escolha: o campo de pesquisa ja decidiu.
# DEPOIS do passo acima, que nomeia o balaio pela tag -- o gate so olha o que
# SOBROU no balaio, e a ordem inversa gatearia opcao que virou eixo.
python3 derivar_variante_por_subclasse.py

echo "== 7d4. pericia com Recall Knowledge =="
# Tres feats se ofereciam a quem nao podia pega-los: a clausula real vivia em
# `requires_residuo` e o `requires` guardava so o gate de nivel. O Pathbuilder
# apontou, em 12 sondas de skill_feat rodadas em paralelo.
python3 derivar_pericia_de_recall.py

echo "== 7d5. gate elemental do Kineticist =="
# 24 das 314 divergencias da bancada eram impulsos oferecidos a quem nao
# tinha o elemento. A regra e da fonte: composite exige TODOS os listados.
python3 derivar_gate_elemental.py

echo "== 7e3. estatisticas de familiar e eidolon =="
# A DECIMA PRIMEIRA lacuna de leitura: `aon_dump/rules.json` tem 3.645 registros
# e nenhum extrator o abria. Familiar e eidolon derivam do mestre -- o que
# existe e formula, nao tabela, e por isso procurar tabela nunca achou nada.
python3 derivar_estatisticas_de_ator.py

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

echo "== 10. essa base saiu deste codigo? =="
# O repo nao conseguia responder isso. `comparar_bases.py` foi escrito
# exatamente para a pergunta e tinha ZERO chamadas -- a fronteira mais fragil
# do projeto nao e entre modulos, e entre build e artefato.
# NAO aborta: um build legitimo muda a base de proposito, e transformar isso em
# erro treinaria todo mundo a ignorar. O que ele nao pode e ser silencioso --
# diff registro a registro contra o commitado, na cara, todo build.
python3 comparar_bases.py HEAD || echo "  ^^ a base difere do commitado -- confira se a mudanca e a que voce queria"
