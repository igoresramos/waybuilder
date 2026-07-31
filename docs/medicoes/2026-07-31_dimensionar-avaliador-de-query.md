# Item 99 -- dimensionar o avaliador de query dos `ChoiceSet`

O item 99 fecha com "exige um avaliador de query, que e trabalho e risco novos e
ainda nao foi dimensionado". Este documento e o dimensionamento. Nao implementa
nada.

Fonte medida: `pipeline/dados_brutos/foundry_repo/packs/pf2e/` (varredura
recursiva, 17.688 itens em packs de jogador) contra `pipeline/base/index.json`
como esta versionado (19.604 registros). Nenhum script de `pipeline/` foi
executado.

**Tres premissas do item 99 nao se sustentam na medicao.** Estao marcadas no
texto e resumidas no fim.

---

## 1. As 194 regras, recontadas: quatro formas, nao duas

841 arquivos de class-feature no repo do Foundry. 126 deles carregam ao menos um
`ChoiceSet`. Total de regras: **194** -- o numero do item 99 esta certo.

O que muda e a reparticao:

| forma de `choices` | regras | registros | o que e |
|---|---:|---:|---|
| objeto com `filter` | **88** | 68 | query no COMPENDIO por predicado |
| array literal | 74 | 67 | lista de opcoes escrita a mao |
| objeto com `ownedItems` | 16 | 16 | query no INVENTARIO do personagem |
| string | 16 | 16 | ponteiro para uma escolha ANTERIOR do personagem |

O item 99 diz "104 de forma `query`". A soma fecha (88 + 16 = 104), mas junta
duas familias de custo diferente: 88 consultam o compendio inteiro, 16 consultam
a mochila. E as 16 de string nao sao query nenhuma -- sao
`flags.system.kineticist.elements` (5), `psychic.dedication.psiCantrips` (6),
`thaumaturge.adeptChoices`/`paragonChoices` (3) e `weaponGroups` (2): releem o
que o personagem ja escolheu.

**Daqui em diante, "as 88" sao as que exigem avaliador de compendio.**

---

## 2. A gramatica completa dos filtros

As 88 regras usam **70 formas distintas** de filtro. O custo do avaliador e o
tamanho desta tabela, entao ela vai inteira.

### Operadores (7 formas, 92 ocorrencias)

| operador | ocorrencias |
|---|---:|
| `or` | 36 |
| `not` | 20 |
| `lte` | 11 |
| `nor` | 10 |
| `and` | 10 |
| `xor` | 4 |
| `gte` | 1 |

Lista no topo e AND implicito.

### Atomos (20 formas, 317 ocorrencias + 6 literais numericos)

| atomo | ocorrencias | onde vive na base hoje |
|---|---:|---|
| `item:trait:X` | 138 | `traits` -- **existe** |
| `item:tag:X` | 81 | **nao existe** (e `system.traits.otherTags`) |
| `item:level:N` (igualdade) | 20 | `level` -- **existe** |
| `item:category:X` | 15 | `feat_category` / `weapon_category` -- parcial |
| `item:level` (comparacao) | 11 | `level` -- **existe** |
| `item:magical` | 11 | trait `magical` -- **existe** |
| `item:group:X` | 10 | `group` -- **existe** |
| `parent:granter:level` | 6 | nivel do concessor -- **existe no motor** |
| `item:base:X` | 5 | `base_item` -- **existe** |
| `item:type:X` | 4 | `kind` -- **existe** |
| `item:rarity:X` | 4 | `rarity` -- **existe** |
| `item:melee` | 2 | **nao existe** (precisa de `alcance`) |
| `item:damage:type:X` | 2 | `damage.tipo` -- **existe** |
| `armor-innovation:X` | 2 | escolha do ator |
| `sanctification:X` | 2 | escolha do ator (`deity_sanctification`) |
| `item:ranged` | 1 | **nao existe** (precisa de `alcance`) |
| `item:range-increment` | 1 | **nao existe** |
| `item:usage:hands:1` | 1 | `usage` -- **existe** |
| `item:<slug>` | 1 | `id` -- **existe** |
| `{actor\|flags...}` (interpolacao) | 72 (dentro dos 138 de trait) | escolha do ator |

Os 72 de interpolacao sao todos a mesma coisa repetida:
`item:trait:{actor|flags.system.kineticist.gate.one..six}`, 12 vezes cada, nas
4 regras de threshold do Kineticist.

Dos 81 `item:tag:X`, os valores distintos sao 40. Cada um nomeia um eixo:
`barbarian-instinct` (10 itens), `witch-patron` (16), `sorcerer-bloodline` (18),
`exemplar-ikon` (21), `kineticist-kinetic-gate` (6), e assim por diante.

---

## 3. PREMISSA DERRUBADA (1): o avaliador de query ja existe e ja roda

`motor/motor.py:3184` -- `_casa_filtro`. `motor/motor.py:3160` --
`_atomo_de_filtro`. Entraram na spec `2026-07-30-slot-de-feat-concedido`, para o
slot `feat_concedido`.

O que ele ja sabe:

| camada | estado |
|---|---|
| operadores `or` `and` `not` `nor` `xor` `lte` `lt` `gte` `gt` | **9 de 9 implementados** |
| operadores que as 88 usam | 7 -- **nenhum faltando** |
| atomos `item:trait` `item:level` `item:category` `item:rarity` | 4 de 20 formas |

`avaliar` (o de `requires`, com `all`/`any`/`not`) e **outro** avaliador, e
pergunta outra coisa: "este PERSONAGEM atende X". `_casa_filtro` pergunta "este
ITEM casa com X". Sao dois, e o segundo e o que interessa aqui.

Ele tambem ja carrega o risco. A regra e explicita no codigo: atomo
desconhecido conta em `self.filtro_ignorado` e **vale como satisfeito**.

E ja ha divida em producao com essa regra: **115 registros da base carregam
`choice.filtro`, 93 deles com predicado de verdade, e 44 desses 93 contem ao
menos um atomo que o motor ignora hoje** -- `item:slug` (74 ocorrencias),
`item:tag` (54), `item:ancestry` (7), estado do ator. O alargamento silencioso
ja acontece, em 44 filtros, sem o item 99.

O que falta de verdade e:

1. **Extracao.** O pipeline le `ChoiceSet` de feats
   (`extratores/feats.py:1083`), de heranca (`extratores/ancestrias.py:585`) e
   de companheiro. **Nao le de class-feature**: dos 847 class-features da base,
   **0** tem `choice` nos grants. O bloco que faz isso em `feats.py` ja existe e
   guarda o filtro verbatim.
2. **Vocabulario.** 16 das 20 formas de atomo.

Nao e "trabalho e risco novos". E vocabulario sobre motor pronto, mais uma
extracao que ja existe noutro extrator.

---

## 4. Cobertura medida, fatia por fatia

Rodei as 88 com vocabulario incremental. Universo: o compendio do Foundry
recortado por `itemType`. Verdade: o avaliador completo. "Exata" = conjunto
identico ao da verdade, sem sobra e sem falta.

| fatia | atomos que entram | exatas |
|---|---|---:|
| **V0** -- o motor de hoje | trait, level, category(feat), rarity | **18** / 88 |
| **V1** + `item:tag` | tag | **68** / 88 |
| **V2** + `item:type` | type | **69** / 88 |
| **V3** + equipamento | group, base, magical, melee, ranged, damage:type, usage, range-increment | **82** / 88 |
| **V4** + `parent:granter:level` | granter:level | **82** / 88 |
| **V5** + estado do ator | gate escolhido, sanctification, armor-innovation | **88** / 88 |

V4 empata com V3 porque medi com o concessor no nivel 20, onde `lte` e sempre
verdadeiro. Com o concessor no nivel 1 -- que e o caso real do gate do
Kineticist -- V3 da **76** e V4 da **82**: as 6 regras de gate so fecham com
`parent:granter:level`.

### (a) cobertos por termo existente: 18 das 88

### (b) pedem termo novo: 64 das 88

| termo novo | regras que ele fecha | tem campo na base? |
|---|---:|---|
| `item:tag:X` | 50 | **nao** -- campo `tags` novo, vindo de `otherTags` |
| equipamento (8 atomos) | 13 | 6 de 8 sim; `alcance` nao existe (0 de 1.039 weapons) |
| `item:type:X` | 1 | sim, e o `kind` |

Sobre o campo `tags`: **549 registros da base ganhariam `otherTags` nao-vazio**
(310 class-feature, 123 equipment, 79 feat, 32 tactic, 5 weapon). Os 847
class-features tem par no Foundry por `xref.foundry` -- a extracao e 1:1, sem
casamento por nome.

### (c) dependem de estado do Foundry: 6 das 88

E aqui a segunda surpresa: **nenhuma e inalcancavel.**

| dependencia | regras | por que e alcancavel |
|---|---:|---|
| `{actor\|...kineticist.gate.N}` | 4 | e a escolha de gate do proprio personagem, que viraria eixo na mesma fatia |
| `sanctification:holy/unholy` | 1 | o motor ja tem `_termo_deity_sanctification` (motor.py:2870) |
| `armor-innovation:power-suit` | 1 | e a innovation escolhida, que ja esta no balaio do Inventor |

**Inalcancaveis de verdade: 0 das 88.** As 16 de `ownedItems` tambem nao sao --
o motor ja modela `doc["inventario"]` (motor.py:1061, 2002, 3871). As 16 de
string tambem nao -- releem escolha anterior do personagem.

---

## 5. PREMISSA DERRUBADA (2): "33" e "22" sao regras, nao opcoes

O item 99 diz que as queries "povoariam `Kineticist.KineticGate` (33) e
`Exemplar.Ikon` (22)". Os dois numeros vieram do LOG de 2026-07-30, onde sao
contagens de **regras `ChoiceSet` agrupadas pela chave i18n do prompt**. Nao sao
contagens de opcao.

Medido:

| | regras | opcoes que a query rende |
|---|---:|---:|
| Kineticist (todas as formas) | **33** (22 filter + 6 literal + 5 string) | o eixo de gate rende **6** |
| Exemplar / ikon | 22 pela chave de prompt; 47 nos 21 arquivos de ikon | a query de eixo rende **21** |

E o caso do Exemplar e pior que impreciso: **o eixo `ikon` do Exemplar ja existe
na base, com exatamente 21 opcoes e `escolhe: 3`** -- fechado no proprio
2026-07-30, item 97. A query nao destrava nada ali. Confirma o que ja esta
pronto.

### O que a query destrava mesmo

**(i) Eixo em classe que hoje nao tem bloco de subclasse.** Cinco classes nao
tem: Commander, Fighter, Guardian, Kineticist, Monk.

| classe | o que a query cria | opcoes |
|---|---|---:|
| **Kineticist** | eixo de gate (`item:tag:kineticist-kinetic-gate`) | **6** (Air, Earth, Fire, Metal, Water, Wood) |
| Kineticist | slot de impulso concedido por gate, nivel 1 | 4 por elemento |
| Kineticist | thresholds nos niveis 5 / 9 / 13 / 17 | 12 / 21 / 25 / 27 |
| **Commander** | escolha de tatica, 11 regras | **14 / 21 / 26 / 31** conforme o nivel |
| Fighter, Guardian, Monk | nada | -- |

Os 6 registros `wb:class-feature/*-gate` e os 37 `kind: tactic` estao hoje com
**0 referencias** em qualquer lugar da base -- orfaos completos. Fighter,
Guardian e Monk nao terem query e o resultado certo: nao tem subclasse.

**(ii) Balaio nomeado.** O balaio (`eixo: outras-opcoes`) tem 256 opcoes
distintas depois de normalizar os gemeos por `equivale_a`. As 88 queries tocam
**94** delas.

**(iii) Ikon fisico e implemento.** 16 regras `ownedItems` (os 16 ikons fisicos
do Exemplar) mais 9 regras `filter` sobre weapon/shield: 252 (Weapon Innovation
do Inventor), 248 (implemento Weapon do Thaumaturge), 134, 72, 62, 62, 50, 49,
30, 23 (implemento Shield), 15, 10. Isso nao e eixo de classe -- e vinculo com
item do inventario.

---

## 6. PREMISSA DERRUBADA (3): as 74 literais NAO cobrem zero do balaio

O item 99 afirma: "As 74 de lista LITERAL cobrem zero do balaio e zero dos
inalcancaveis (apontam para draconic-exemplar 95, animal-companion 12, skill
11 -- ja modelados)".

Medido: das 441 opcoes literais, **109 sao referencia de compendio por NOME**
(`Compendium.pf2e.classfeatures.Item.Dense Plating`), em 63 nomes distintos.
**Todos os 63 resolvem na base.** E **59 deles estao no balaio.**

| classe | opcoes do balaio nomeadas por literal |
|---|---:|
| Inventor | **47** |
| Wizard | **12** |

Arquivos: `revolutionary-innovation` (46 casamentos), `breakthrough-innovation`
(32), `weapon-innovation` (11), `school-of-thassilonian-rune-magic` (7),
`school-of-rooted-wisdom` (5), `enhanced-resistance` (4).

Essas 59 nao precisam de avaliador nenhum. E leitura direta de nome.

### O balaio inteiro, com as duas fontes

| classe | balaio | por literal | por query | resto |
|---|---:|---:|---:|---:|
| Inventor | 52 | **47** | 9 | **1** |
| Alchemist | 33 | 0 | 0 | 33 |
| Thaumaturge | 30 | 0 | 0 | 30 |
| Sorcerer | 19 | 0 | 18 | 1 |
| Cleric | 18 | 0 | 0 | 18 |
| Exemplar | 18 | 0 | 18 | 0 |
| Animist | 17 | 0 | 4 | 13 |
| Summoner | 14 | 0 | 13 | 1 |
| Wizard | 14 | 12 | 14 | 0 |
| Oracle | 13 | 0 | 1 | 12 |
| Druid | 9 | 0 | 9 | 0 |
| Champion | 5 | 0 | 2 | 3 |
| Investigator | 5 | 0 | 5 | 0 |
| Ranger | 5 | 0 | 1 | 4 |
| Witch | 4 | 0 | 0 | 4 |
| **total** | **256** | **59** | **94** | **120** |

Interseccao literal/query: 17. Uniao: **136 de 256** (53%). Sobram **120** sem
explicacao em `ChoiceSet` nenhum -- e 106 desses 120 estao em cinco classes:
Alchemist 33, Thaumaturge 30, Cleric 18, Animist 13, Oracle 12.

---

## 7. Risco: lista vazia (3) contra lista errada (67)

A pergunta era quantos filtros, avaliados errado, dao lista VAZIA e quantos dao
lista ERRADA. Medido aplicando as 88 com o avaliador de hoje, sem vocabulario
novo:

| resultado | grupos | regras |
|---|---:|---:|
| exato | 18 | 18 |
| lista **VAZIA** | 3 | 3 |
| lista **ERRADA por excesso** | 49 | **67** |

As 3 vazias: `barrows-edge` (verdade 135 armas), `starshot` (62),
`titans-breaker` (51). Esvaziam porque `item:melee`/`item:ranged` sao
desconhecidos e caem dentro de um `nor` -- e o `nor` transforma
"desconhecido = satisfeito" em reprovacao. E o unico lugar onde a regra do
motor se inverte.

As 67 erradas: sobra **mediana de 16.383 itens**, maxima 16.392. As 6 regras de
`item:tag:kineticist-kinetic-gate` ofereceriam o compendio inteiro no lugar de 6
gates.

**A conclusao de risco e assimetrica e vale registrar: a regra "atomo
desconhecido vale como satisfeito" e correta para ESTREITAR um slot de feat que
ja existe, e destrutiva para DEFINIR um eixo do zero.** No slot de feat o pior
caso e oferecer feat demais numa lista que ja existia; no eixo, o pior caso e
oferecer 19.604 opcoes onde ha 6.

Como o risco cai por fatia:

| fatia | grupos com excesso | sobra mediana | sobra maxima | vazias |
|---|---:|---:|---:|---:|
| V0 (hoje) | 49 | 16.383 | 16.392 | 3 |
| V1 (+tag) | 15 | 66 | 554 | 3 |
| V3 (+equipamento) | 6 | 44 | 71 | 0 |
| V5 (completo) | 0 | 0 | 0 | 0 |

E um efeito colateral de nivel: sem `parent:granter:level`, o slot de impulso do
nivel 1 do Kineticist oferece **15** opcoes em vez de **4** -- 11 impulsos de
nivel acima do permitido, todos com cara de legais.

---

## 8. Proposta de recorte em fatias

**Fatia 0 -- as referencias literais por nome. Sem avaliador.**
Ler os 109 `Compendium.*.Item.<Nome>` das 74 listas literais.
Fecha: **59 opcoes do balaio** (Inventor 47, Wizard 12). Derruba o Inventor de 52
para 5 no balaio.
Custo: resolucao por nome, ja existente no pipeline.

**Fatia 1 -- extracao de `ChoiceSet` em class-feature + `item:tag`.**
Portar o bloco de `extratores/feats.py:1083` para class-feature; campo `tags` na
base a partir de `otherTags` (549 registros o ganham, 310 deles class-feature);
um atomo novo no `_atomo_de_filtro`.
Fecha: **68 das 88** exatas. Nomeia **94 do balaio**. Cria o eixo do Kineticist
(6 gates) e o do Commander (14 a 31 taticas). Derruba a sobra mediana de 16.383
para 66.

**Fatia 2 -- `parent:granter:level` e `item:type`.**
Fecha: **+1** exata (69/88), mas corrige o teto de nivel dos 6 slots de impulso
do Kineticist: 4 opcoes no nivel 1 em vez de 15.

**Fatia 3 -- vocabulario de equipamento.**
`group`, `base`, `magical`, `melee`, `ranged`, `damage:type`, `usage`,
`range-increment`. Precisa de um campo novo na base: `alcance` da arma (0 de
1.039 weapons tem hoje).
Fecha: **+13** (82/88). Elimina as **3 listas vazias**. Habilita os 16 ikons
fisicos do Exemplar e os implementos Weapon/Shield do Thaumaturge.

**Fatia 4 -- estado do ator.**
Gate escolhido, `sanctification`, `armor-innovation`.
Fecha: os **6 restantes** (88/88).

### O 80/20

**Fatia 0 + Fatia 1 fecham 68 das 88 queries e nomeiam 136 das 256 opcoes do
balaio (53%), com um atomo novo no motor.** As fatias 2, 3 e 4 juntas somam mais
20 queries exatas e nenhuma opcao nova de balaio -- o valor delas e correcao
(nivel certo, lista nao-vazia, ikon fisico), nao volume.

### O avaliador vale a pena?

Sim, com o recorte acima, e por razao diferente da que o item 99 dava.

- Ele **nao** destrava `Exemplar.Ikon` -- esse eixo ja esta pronto com 21
  opcoes.
- Ele destrava **2 eixos novos** em classes que hoje nao tem bloco nenhum:
  Kineticist (6 gates + slots de impulso) e Commander (11 escolhas de tatica,
  ate 31 opcoes). Os 6 registros de gate e os 37 de tactic estao com **0
  referencias** na base -- sao 43 registros inalcancaveis que passam a ser
  alcancaveis.
- Ele nomeia **94** das 256 opcoes do balaio, e a Fatia 0 (que nao e avaliador)
  nomeia outras 59.
- Ele paga divida existente: 44 dos 93 filtros que ja rodam em producao contem
  atomo ignorado hoje.

O que ele **nao** resolve: 120 das 256 opcoes do balaio continuam sem
explicacao, concentradas em Alchemist (33), Thaumaturge (30), Cleric (18),
Animist (13) e Oracle (12). Se o objetivo for esvaziar o balaio, o avaliador
chega a 53% e para.

---

## 9. O que eu NAO consegui medir

1. **De onde vem o resto do balaio.** As 120 opcoes sem explicacao nao tem fonte
   em `ChoiceSet` nenhum. Nao investiguei se ha outra estrutura no Foundry
   (`GrantItem` condicional, `flags`) ou se e mesmo prosa. Isso e outro item.
2. **O nivel real de `parent:granter:level` por regra.** Medi os extremos (1 e
   20). O valor certo depende de ligar cada regra ao nivel do class-feature
   concessor na progressao da classe -- que existe na base, mas eu nao fiz a
   ligacao regra a regra.
3. **As 16 de `ownedItems` contra inventario real.** Nao ha ficha de exemplo de
   Exemplar com armas no `motor/fixtures`. Simulei o predicado contra o
   compendio (que e o que a variante `granted` faz), nao contra uma mochila.
4. **Quantas taticas o Commander conhece no total.** As 11 regras dizem quais
   sao candidatas em cada nivel, nao quantas o personagem acumula. Esse numero
   esta na prosa, nao no `ChoiceSet`.
5. **Os packs `sf2e`.** Varri so `packs/pf2e`.
6. **A base pos-build.** Usei `pipeline/base/index.json` como versionado; nao
   rodei `build.sh`. Se a base mudou desde o ultimo commit, os numeros de opcao
   mudam junto.
7. **Os scripts desta medicao nao foram versionados** -- rodaram no scratchpad
   da sessao. Diferente de `docs/medicoes/medir_corte_multiclasse.py`, esta
   medicao nao e reproduzivel por script commitado hoje. Todos os numeros acima
   sao rederivaveis dos caminhos citados, mas o codigo precisaria ser reescrito.

---

## Resumo das tres premissas derrubadas

1. **"exige um avaliador de query, que e trabalho e risco novos"** -- o
   avaliador existe (`motor.py:3184`), tem 9 de 9 operadores e roda sobre 93
   filtros em producao. Falta vocabulario (16 de 20 atomos) e extracao de
   class-feature. E o risco nao e novo: 44 dos 93 filtros ja em producao contem
   atomo que o motor ignora.
2. **"povoariam Kineticist.KineticGate (33) e Exemplar.Ikon (22)"** -- 33 e 22
   sao contagens de REGRAS. As opcoes sao 6 e 21. E o eixo de ikon do Exemplar
   ja existe com essas 21.
3. **"as 74 de lista LITERAL cobrem zero do balaio"** -- cobrem 59, por
   referencia de compendio por nome: Inventor 47, Wizard 12.
