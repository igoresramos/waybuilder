# Auditoria de estado -- o trabalho de 2026-07-31

Auditoria coordenada com 6 sub-agentes de medicao independente (Sonnet), um por
frente, todos READ-ONLY. Todo achado que muda veredito foi conferido pelo
coordenador com os proprios olhos contra o commit de referencia `132b83de0`
(citacoes ancoradas nele; o working tree podia estar em edicao paralela).
Commits do dia: `8c39ad128`, `1183b0ef4`, `650e7eba1`, `d9a86b318`,
`132b83de0` -- mais os auto-saves, que carregam parte do codigo (o proprio
`extratores/acoes.py` entrou por auto-save `045b5cc4e`/`2281cec46`, nao pelo
commit de feature).

Nada do projeto foi alterado alem deste relatorio. Scripts descartaveis
viveram no scratchpad da sessao.

---

## Frente 1 -- as fixtures regeneradas

**Veredito: OK, com a alegacao numerica errada.**

Medido de forma independente (diff estrutural JSON, chave a chave, recursivo,
`132b83de0~1` vs `132b83de0`):

- **34** fixtures no commit, **26** mudaram -- nao "17 das 33".
- Em TODAS as 26, os unicos caminhos que mudaram sao `visao.concedidos` e
  `visao.features`. **Nenhum** HP, AC, ataque, proficiencia, pericia, magia ou
  aviso mudou. A afirmacao "so `concedidos`" tambem e imprecisa: `features`
  mudou junto (sao os `grants[].grant_feat` dentro das features, trocando
  `wb:feat/<slug>` por `wb:action/<slug>`).
- As mudancas sao todas da mesma familia e batem com a causa declarada:
  - troca de kind no alvo do grant (`wb:feat/reactive-strike` ->
    `wb:action/reactive-strike` em `guerreiro3-mago2.json`;
    `wb:feat/quick-alchemy` -> `wb:action/quick-alchemy` em
    `campeao6-alquimista4-fa-nivel10.json`);
  - concessoes novas que antes nao pousavam (`wb:action/cast-a-spell` por
    Wizard Spellcasting, `wb:action/drain-bonded-item` por Arcane Bond,
    `wb:action/call-on-ancient-blood` por Ancient-Blooded Dwarf).
- Nenhuma fixture criada ou deletada; nenhuma remocao sem substituto.

Regenerar o gabarito aqui e legitimo: o oraculo e o motor Python, a base mudou
de proposito, e o diff prova que so o efeito intencional passou. O anti-padrao
"atualizar o esperado ate ficar verde" nao se materializou -- mas a defesa
("so concedidos, 17 de 33, resto identico") foi escrita de memoria, com os dois
numeros errados. Quem confere pela frase, nao pega; quem confere pelo diff,
pega.

**Conserto:** nenhum no conteudo. No processo: quando regenerar gabarito,
anexar o diff estrutural (que caminhos mudaram, por arquivo) ao LOG em vez de
resumo de cabeca.

---

## Frente 2 -- a exclusao das 37 taticas por trait

**Veredito: PROBLEMA -- funciona hoje por coincidencia de dados, sem
invariante.**

- `acoes.py` (`_docs_foundry`) **exclui por trait Foundry** `tactic`
  (`system.traits.value`).
- `taticas_kits.py` **inclui por categoria AoN** `tactic`
  (`aon_tactics.json`); o Foundry entra la so para xref/licenca, nunca para
  decidir populacao.
- Hoje os dois conjuntos coincidem (medido na fonte: 557 docs no pack, 37 com
  trait `tactic`, todos em `class/commander/`; 37 docs no dump AoN). Nada no
  codigo amarra essa coincidencia.
- Cenario de furo real: a Paizo publica acao com trait `tactic` que o dump AoN
  local ainda nao categorizou como `tactic` (lag de curadoria entre projetos
  independentes e normal). `acoes.py` a exclui pelo trait; `taticas_kits.py`
  nao a ve. **Some das duas fontes, em silencio.**
- Nenhum portao pega: o portao 9 audita so o lado AoN (ver frente 5 -- e nem
  esse lado ele cobre para acoes). Nao existe verificacao "todo doc Foundry
  com trait `tactic` virou registro em algum kind".

**Conserto:** cheque cruzado no build -- o conjunto {docs Foundry com trait
`tactic`} tem de ser igual ao conjunto extraido como `kind: tactic`; divergiu,
quebra com nome. Uma linha de portao, e a coincidencia vira invariante.

---

## Frente 3 -- `tipo: action` alcancando os kinds `action` e `tactic`

**Veredito: OK com ressalvas -- modelagem defensavel, protecao por convencao.**

- Nao e hack: `tipo` vem literalmente do Foundry, onde a tatica E
  `type: action`; o `kind: tactic` e cisao nossa. Traduzir `action` ->
  `{action, tactic}` reflete a fonte. Os unicos 4 blocos `tipo: action` da
  base sao os do Commander (`Tactical Excellence`/`Tactical Expansion`), todos
  com filtro `item:trait:tactic` + tags.
- **Paridade Python/TS: identica.** `motor/motor.py` (~3729-3733) e
  `app/src/motor/personagem.ts` (~3925-3931) tem a mesma condicao, o mesmo
  par de kinds e o mesmo gate por `base.kinds()`. Conferido linha a linha.
- Ressalvas, por ordem de peso:
  1. O alargamento dispara pela presenca de `"action"` no conjunto de tipos do
     GRUPO de blocos, nao por bloco individual. Um bloco `tipo: action` futuro
     de outra classe, com filtro fraco/indecidivel (e `_casa_filtro` trata
     atomo desconhecido como satisfeito), ofereceria taticas a nao-Commander.
     Os 37 registros `tactic` tem `requires: null` -- nenhuma segunda linha de
     defesa.
  2. Rotulo cosmetico: a listagem de escolhas pendentes (`abertos`) deriva
     `kind` do `tipo` sem o alargamento (motor.py ~3363, personagem.ts ~3561)
     -- o slot de tatica sai rotulado `action`. Igual nos dois motores, nao
     afeta candidatos.
  3. Comentarios dos motores ainda citam "19.606 registros" (base atual:
     20.126).

**Conserto:** condicionar o alargamento ao proprio bloco; considerar
`requires` de classe nos registros `tactic` como defesa em profundidade.

---

## Frente 4 -- o conserto do `recuperar_mecanica_equipamento.py`

**Veredito: PROBLEMA GRAVE -- o fix de path e correto, mas ligou uma fonte com
campo bugado e gravou tipo de dano errado em 11 armas.**

O que esta certo:

- Diagnostico e fix dos paths conferem em disco: `do_foundry` usava caminho
  fixo `dados_brutos/foundry/packs/...` (o clone real e `foundry_repo/`);
  `do_aon` procurava `aon_equipment_weapon.json`, nome que nao existe mais
  (real: `aon_dump/weapon.json`). Resultado `foundry 0 -> 1.328, aon 0 -> 399`
  e real.
- Precedencia Foundry-antes-de-AoN respeitada na regra de decisao (linhas
  ~288-297) e confirmada arma a arma nas que existem nas duas fontes.
- Os 3 exemplos-emblema batem com fonte e regra: Fist 1d4 B, Blowgun 1 P fixo,
  Shield Bash 1d4 B. Amostra de 8 armas de origem Foundry: todas corretas.

O que esta errado:

- **11 armas de combinacao `(Melee)` gravadas com `tipo: piercing` quando a
  fonte diz slashing/bludgeoning.** O dump do AoN traz `damage_type` hardcoded
  `["Piercing"]` para as variantes `(Melee)` mesmo quando a string `damage`
  traz outra letra (`"1d8 S"`); `do_aon()` le `damage_type[0]` e ignora a
  letra. Conferido pelo coordenador na base do commit e nas duas fontes cruas:
  `Gun Sword (Melee)` emitido `d8 piercing`, Foundry `meleeUsage` diz `d8
  slashing`, AoN cru diz `"1d8 S"`; `Hammer Gun (Melee)` emitido `d10
  piercing`, Foundry diz `d10 bludgeoning`. Lista completa: Axe Musket, Black
  Powder Knuckle Dusters, Bow Staff, Cane Pistol, Crescent Cross, Gnome
  Amalgam Musket, Gun Sword, Hammer Gun, Mace Multipistol, Mikazuki, Piercing
  Wind (todas `(Melee)`). O bug de `do_aon` e pre-existente, mas dormia com
  `aon=0`; o fix de hoje o acordou e trocou `None` honesto por valor errado
  plausivel -- pior que a ausencia.
- Buraco de mecanismo: `do_foundry` so monta dano se `dmg.get("die")` for
  truthy; dano fixo do Foundry (`die: ""`, caso Blowgun/Dart Umbrella) nunca
  produz bloco, e a arma cai para o AoN. O valor final coincidiu, a
  precedencia declarada nao foi honrada -- foi sorte.
- `relatorio_mecanica_equipamento.md` diz **65** "ainda sem"; recontagem na
  base do commit da **70** (53 armas sem `damage`, 10 armaduras e 7 escudos
  sem `ac_bonus`). O script conta preenchimento parcial (municao que ganhou
  `group` mas nao tem dano) como "curado".

**Conserto:** em `do_aon`, derivar o tipo da LETRA da string `damage`
(`S`/`B`/`P`), nunca de `damage_type[]`; para armas de combinacao, preferir
`system.meleeUsage` do Foundry; aceitar dano fixo (`die` vazio) do Foundry; e
o portao de campo critico que o proprio item 113 ja desenha -- ele teria
pegado as 11 tambem, se comparar contra a fonte e nao so contra `None`.

---

## Frente 5 -- `xref.aon` vazio nas acoes

**Veredito: PROBLEMA -- o "173 de proposito" descreve 45% do vazio, e 140 dos
173 eram resolviveis por regra que o pipeline ja usa em 6 outros lugares.**

Contado na base do commit:

- `xref.aon` vazio em **382** das 520 acoes (73%), nao 173.
  - **209** sem NENHUM candidato no AoN (nome nao existe la -- ausencia real,
    nao bug de normalizacao; conferido com fuzzy). Nunca mencionados como
    categoria em LOG/TODO/docstring.
  - **173** com 2+ candidatos -- o numero citado. Desses, **140 (81%) sao par
    legado/remaster com vinculo EXPLICITO no dado** (`remaster_id`/
    `legacy_id`): ambiguidade resoluvel deterministicamente, pela regra que
    `ancestrias.py`, `classes.py`, `companheiros.py`, `equipamento.py`,
    `aon_kinds.py` e `desmembrar_colisoes.py` ja aplicam. So **33** sao
    genuinamente ambiguos (ex.: "Cast a Spell", 351 candidatos).
- A docstring de `acoes.py` diz "o desmembramento de colisoes decide, que e o
  passo que existe para isso" -- **impreciso**: `desmembrar_colisoes.py` age
  sobre xref preenchido errado, nao sobre vazio. Vazio nunca e decidido por
  ninguem.
- Custo hoje: zero funcional -- nada le `xref.aon` de acao (motor e app nao
  usam; a prosa fallback nunca e acionada: 0 dos 520 sem texto). Mas a
  cobertura de acao contra o AoN e inexistente por tres caminhos ao mesmo
  tempo: `comparar_com_aon.py` nao tem `action` em `FRENTES`, o portao 9 nao
  enxerga a categoria (frente 8 da spec -- ver abaixo), e o xref vazio
  impediria o cruzamento mesmo se cobrissem.

Achado conexo, conferido pelo coordenador no codigo: **a prova 7 da spec
("portao 9 passa com `action` fora de `FORA_DE_ESCOPO`) passa por vacuidade.**
`censo_aon()` le apenas os apelidos versionados `dados_brutos/aon_*.json`;
`CENSO_APELIDO` nao tem entrada para acoes e `aon_actions.json` nao existe em
disco -- a categoria `action` nunca entra no censo. Remover a linha do
`FORA_DE_ESCOPO` nao fez o portao passar a cobrar acoes; fez o portao
continuar cego com a lista dizendo que ele ve. O comentario novo em
`portoes.py` ("`action` SAIU daqui em 31/07: o pack passou a ser extraido")
vende cobertura que nao existe.

**Conserto:** aplicar a desambiguacao por `remaster_id` no `_indice_aon` de
`acoes.py` (140 xrefs de graca, zero chute); registrar os 209 sem candidato
como categoria propria no relatorio do extrator; e ou criar o apelido
`aon_actions.json` para o censo, ou devolver `action` ao `FORA_DE_ESCOPO` com
o motivo escrito ("categoria AoN poluida por ativacao de item") -- cegueira
declarada e melhor que cegueira fantasiada de cobertura.

---

## Frente 6 -- o pack inteiro (520) em vez das 317

**Veredito: OK -- decisao defensavel, registrada e barata; a meta nao foi
ajustada em silencio. Duas ressalvas de honestidade.**

- Nao ha violacao de SDD: a spec aprovada (Decisao 2) decide pelos 520 e
  registra a discordancia com o relatorio de terreno abertamente, com 4
  argumentos (dependencia de ordem, sub-regra de portao, custo, doutrina do
  item 97). O codigo implementa a spec. Terreno e insumo, nao spec.
- Custo real medido (nao estimado): os 203 nao referenciados custam **~5,1 KB
  gzip** no indice (<1% do nucleo). O "+21 KB" do PROJECT.md e o kind inteiro
  entrando (manifesto: `action.gzip_bytes: 15475` + crescimento de feat/
  class-feature), e confere.
- A mudanca 0,53 -> 0,55 MB no PROJECT.md veio **no mesmo commit, na mesma
  linha, com o motivo escrito ao lado do numero**. Nao e mover a trave depois
  do chute -- e registrar que a trave mudou e por que. O numero era
  descritivo ("cabe em"), nao orcamento aprovado; se Igor o tratava como teto,
  ai sim a mudanca merecia um aceite explicito, que nao esta registrado.
- Ressalvas:
  1. Dos 203 extras, **203 (100%) sao peso morto absoluto hoje** -- nenhuma
     query, choice, grant ou tela alcanca qualquer um (medido; os unicos
     ChoiceSet de `itemType: action` filtram por `item:trait:tactic`). E
     catalogo por doutrina, nao por uso -- coerente com o item 97, mas o LOG
     nao diz "100% inertes", e devia.
  2. A spec diz "entra o pack INTEIRO (557)" e o codigo entrega 520. A
     exclusao das 37 taticas e correta, mas o rotulo "inteiro" da Decisao 2
     contradiz a implementacao no literal.

---

## Frente 7 -- coerencia da documentacao (a "salada")

**Veredito: PROBLEMA GRAVE -- e aqui que mora a reclamacao do Igor, e o pior
achado da auditoria inteira esta nesta frente.**

### 7a. O achado que muda o placar do dia: "spec implementada" nao e verdade

LOG.md ("Spec `2026-07-31-kind-action` implementada") e TODO item 111
("IMPLEMENTADO 2026-07-31") vendem a spec como entregue. **A Decisao 5 --
traduzir os 26 predicados avaliaveis para `grants[].se` -- nao foi
implementada.** Conferido pelo coordenador no commit:

- `converter_rule_elements.py` continua pulando TODO `GrantItem` com
  `predicate` (contador "GrantItem com predicate", linhas ~131-132);
- a base emitida tem **zero** ocorrencias de `grants[].se` (varrida inteira);
- consequencia direta: `wb:cause/justice`, `wb:cause/liberation` e as 11
  `wb:way/*` do Gunslinger continuam com `grants: []`. **As deeds do
  Gunslinger e as reacoes do Campeao -- a motivacao-titulo da spec ("concessao
  quebrada em duas classes") -- continuam nao concedidas.**
- Das provas da secao "Como se prova que funciona", as de numero 2, 3, 4, 5 e
  6 nao passam (Gunslinger com deed da Way, `Way of the Drifter` concedendo
  `wb:action/into-the-fray`, Campeao com Retributive/Liberating, o `or` do
  predicado, os 18 pulados com motivo no relatorio) e a 7 passa por vacuidade
  (frente 5). O que o dia entregou de fato: o kind existe, o catalogo esta na
  base, 263 grants ESTATICOS de class features pousaram (290 -> 27 sem alvo,
  numeros reais), e o falso positivo do `Into the Fray` sumiu -- porque agora
  nada e concedido ali, nao porque o certo e concedido.
- O comentario novo em `emitir_app.py` justifica `action` no nucleo com "a
  deed do Gunslinger e a reacao do Campeao sao concedidas no nivel 1 e
  precisam estar la na primeira tela" -- descreve uma concessao que nao
  existe na base emitida.

Nao ha, em TODO, LOG ou PROJECT, uma linha dizendo "Decisao 5 fica para
quando o grant condicional existir". A dependencia e real (o `se` e da spec
grant-condicional, que e so documento) -- mas entao o item 111 esta PARCIAL,
nao implementado, e o Gunslinger/Campeao continuam no placar de quebrados.

### 7b. PROJECT.md desmentido pelos arquivos do proprio commit

- "**Fila em 19 itens e nenhum `alta`**" -- real no mesmo commit: 24 itens,
  4 com `alta` (110, 111, 112, 113).
- Bloqueio do 69/107 descrito como "GrantItem com UUID dinamico... pula os
  163 casos" -- o proprio item 107, re-medido no mesmo dia, diz que essa
  explicacao esta errada para o Campeao e que os casos sao 221 (206+15).
- "84, que agora pede triagem dos 57 'so nosso'" -- a triagem foi feita hoje
  (item 84 e `docs/medicoes/2026-07-31_triagem-57-so-nosso.md`, que ainda por
  cima recontou 56, nao 57).

### 7c. Numeros que nao se propagaram

| conceito | valor velho, onde | valor certo, onde |
|---|---|---|
| pares condicionais | 79/64 -- TODO item 107, LOG | **44** -- spec v2 e review |
| UUID dinamico pulados | 163 -- PROJECT.md, spec gemeo-do-grant-item | **221** -- TODO 107, LOG, spec v2, review |
| violacoes simulacao | 343 -- TODO item 114 | **344** -- o proprio `simulacao-raw.md` regenerado (reproduzido de novo nesta auditoria: 344) |
| triagem "so nosso" | 57 -- PROJECT, nome do doc | **56** -- recontagem no proprio doc |
| xref vazio | 173 "de proposito" -- LOG, TODO, docstring | **382**, dos quais 173 ambiguos e 140 resolviveis (frente 5) |

### 7d. Higiene do TODO

- Itens **85, 98, 108, 109** dizem "FECHADO" no texto e seguem na lista de
  pendentes (a regra do proprio cabecalho manda concluido para
  `todo-concluidos.md`). O 111 fica sem status apesar do "IMPLEMENTADO" (e
  esta certo ficar aberto -- ver 7a -- mas por motivo que o texto nao da).
- Item 107 se autocontradiz no proprio `desc`: um paragrafo afirma o que o
  paragrafo seguinte ("RE-MEDIDO... ESTE PARAGRAFO ESTA ERRADO") desmente. O
  historico embutido sem poda e o que faz o TODO parecer salada.
- Itens 84 e 110 descrevem o mesmo achado com prioridades diferentes
  (media vs alta), violando o criterio do cabecalho.
- Duas coisas diferentes reivindicam o nome "portao 11" (o gate de vocabulario
  da spec grant-condicional e o portao de campo critico do item 113/doc
  proprio).

### 7e. Specs entre si, e specs vs review

- kind-action x grant-condicional v2: **concordam** na emenda (18 certos / 26
  traduziveis / 44 total) -- sem contradicao. Ressalva: "44" significa coisas
  diferentes nas duas specs (44 pares ActiveEffectLike x 44 GrantItem com
  predicate para acoes) -- coincidencia numerica que confunde.
- A v2 incorporou 13 das ~20 exigencias do review adversarial. **6 ficaram sem
  resposta e sem nota de descarte**: corrigir o "Taumaturgo 30/30" do item 69;
  os 3 leitores orfaos do Alquimista; o avaliador tri-state como tipo proprio;
  o caso Runtsage; corrigir o texto do item 107 (ainda com 79/64 e "balde de
  293"); e o comportamento de eixo/slot quando o `se` ja decidiu (pendencia
  fantasma na UI).

### 7f. README e LESSONS

- README.md parado em 27/07: "19.738 registros em 52 kinds" (real: 20.126 em
  58), "os 8 portoes" (real: 10), iconics "117/129" (real: 118/136), front
  listado como pendente (existe desde 28/07), `acoes.py` ausente da lista de
  extratores.
- LESSONS.md: as 6 licoes de hoje batem com o codigo, linha a linha. Nada a
  corrigir. Achado colateral: as licoes 5 e 6 documentam, sem nomear, que
  existem DOIS avaliadores de predicado com gramaticas diferentes no motor
  (`_casa_filtro` vs `avaliar`) -- duplicidade nao documentada em lugar
  nenhum.

**Conserto (frente inteira):** uma passada unica de sincronizacao com fonte de
verdade definida: numeros medidos vivem no relatorio/spec mais recente e TODO/
LOG/PROJECT apontam para ele em vez de repetir; itens fechados migram para
`todo-concluidos.md`; item 111 rebaixado a PARCIAL com a Decisao 5 pendente
nomeada; paragrafo morto do 107 podado; "portao 11" renumerado num dos dois.

---

## Frente 8 -- o que esta verificado de verdade vs o que so parece

**Veredito: PROBLEMA -- os 2 relatorios gerados por script estao atuais; a
camada narrativa de `docs/` envelhece sem nada acusar, e 4 docs afirmam hoje
numeros que a base desmente.**

| relatorio | estado | evidencia (doc vs recontagem na base do commit) |
|---|---|---|
| `2026-07-27_simulacao-raw.md` | ATUAL | regenerado dentro do commit; 344 violacoes, reproduzido 344 |
| `2026-07-27_validacao-iconics.md` | ATUAL | 118/136 HP e 62,9% pericia, reproduzidos linha a linha |
| `auditoria-arquetipos.md` | VELHO FINGINDO COBERTURA | diz 61/226 dedicacoes sem grants e cita Cavalier/Fighter/Wizard Dedication como CRITICO; real 49/226, e os 3 exemplos ja estao corrigidos na base |
| `2026-07-28_validacao-equipamento-runas.md` | VELHO FINGINDO COBERTURA | diz 110 armas sem damage; real 53 (o fix de hoje) |
| `2026-07-27_fichas-montadas.md` | VELHO FINGINDO COBERTURA | D2 (Marshal concede 2 expert de graca) e D5 (motor ignora `weapon_proficiency`) desmentidos pela base/motor atuais |
| `2026-07-30_comparacao-pathbuilder-rodada-3.md` | VELHO no placar | Fighter12 discorda 12 (real 13), Ranger4 discorda 26 (real 23); o achado central segue valido |
| `2026-07-27_ruido-de-avisos.md` | SUSPEITO, nao verificado | cita 43 `grant_item` dinamicos irresoluveis; a reemissao de hoje mudou exatamente esse mecanismo |
| `pipeline/base/relatorio_*.md` | ATUAIS | regenerados pelo build; exceto a contagem 65 vs 70 do `relatorio_mecanica_equipamento.md` (frente 4) |

O mecanismo do defeito e estrutural: de ~57 arquivos em `docs/`, so 2 sao
escritos por script versionado (`simular_raw.py`, `validar_iconics.py` -- e
`simular_raw` nao roda no `build.sh`, item 114 ja cobra). Todo o resto e
narrativa manual sintetizando scripts descartaveis que morreram no scratchpad
-- congela no dia em que foi escrito e nao ha nada que o marque como vencido.

**Conserto:** cabecalho obrigatorio nos docs narrativos ("medido sobre a base
de DATA/commit X; numeros NAO se auto-atualizam") e, para os 4 fingindo
cobertura, ou re-rodar ou carimbar SUPERSEDED apontando o substituto. Por o
`simular_raw.py` no build (item 114a) resolve a classe inteira para os
gerados.

---

## Os 5 problemas que importam, em ordem de gravidade

1. **"Spec kind-action implementada" e meia-verdade** (frente 7a). A Decisao 5
   nao existe no codigo, `grants[].se` nao existe na base, e Gunslinger e
   Campeao -- a motivacao-titulo -- continuam com `grants: []` nas Ways e
   causas. Provas 2-6 da spec nao passam; a 7 passa por vacuidade. LOG e TODO
   registram entrega cheia.
2. **11 armas de combinacao com tipo de dano ERRADO na base** (frente 4). O
   fix de paths acordou o `damage_type` bugado do dump AoN e trocou `None`
   honesto por `piercing` falso em Gun Sword, Hammer Gun, Axe Musket e mais 8.
   Dado errado plausivel e pior que dado ausente.
3. **Cobertura fantasma em tres pontos** (frentes 2 e 5): portao 9 cego para a
   categoria `action` com o comentario dizendo que ve; exclusao das 37 taticas
   amarrada a uma coincidencia entre trait Foundry e categoria AoN sem
   invariante; "173 xref vazios de proposito" que na verdade sao 382, com 140
   resolviveis por regra que o pipeline ja usa em 6 lugares.
4. **Documentacao dessincronizada no mesmo commit** (frentes 7b-7d):
   PROJECT.md com fila/bloqueio/numeros desmentidos pelo TODO ao lado;
   79-vs-44, 163-vs-221, 343-vs-344, 57-vs-56 convivendo; 4 itens FECHADOS
   listados como pendentes; item 107 se autocontradizendo; dois "portao 11".
   E a "salada" nomeada.
5. **4 relatorios narrativos fingindo cobertura hoje** (frente 8) + relatorio
   de mecanica contando 65 onde ha 70 -- a mesma classe de defeito que o item
   114 registrou de manha continua aberta em mais arquivos do que o item diz.

## O que esta solido

- As fixtures regeneradas: 26/34, mudancas confinadas a `concedidos`/
  `features`, todas explicadas pelo kind novo; HP/AC/ataques/proficiencias
  intocados. Nao houve "afinar o gabarito ate passar".
- A paridade Python/TS da mudanca de motor: identica nos dois lados.
- O fix de paths do `recuperar_mecanica_equipamento.py` em si, e as 53 armas
  re-hidratadas de fonte correta (Blowgun, Fist, Shield Bash conferidas RAW).
- A decisao dos 520 e a forma de registrar a meta nova (justificativa inline,
  mesmo commit); manifesto e payload conferem com o declarado.
- LESSONS.md do dia: 6 de 6 licoes batem com o codigo.
- Os numeros centrais do commit (290->27, 556->819, 520, 20.126 registros, 58
  kinds) sao reais -- o problema nunca foi o numero medido, foi o que se
  afirmou em volta dele.
