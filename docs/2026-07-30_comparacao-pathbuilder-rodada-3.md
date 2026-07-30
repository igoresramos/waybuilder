# Comparacao com o Pathbuilder -- 3a rodada (2026-07-30)

Fase 5 do plano. Terreno NOVO: `ancestry_feat`, que nunca tinha sido comparado,
e nivel alto (Fighter 12), alem de uma classe nova (Ranger 4).

## O placar, e o que ele nao diz

| combinacao | so no PB | so no WB | discordam |
|---|---:|---:|---:|
| Fighter 1 / ancestry_feat | 18 | 0 | 0 |
| Fighter 12 / class_feat (dedicacoes) | 0 | 3 | 12 |
| Ranger 4 / class_feat (class feats) | 1 | 1 | 0 |
| Ranger 4 / class_feat (dedicacoes) | 0 | 3 | 26 |

O placar bruto e ruim de ler. A triagem e o que importa, e ela deu **UM defeito
nosso** -- que foi consertado nesta mesma rodada.

## 1. DEFEITO NOSSO, consertado: o divisor rasga a clausula antes do parser

`Tupilaq Carver` sai disponivel para um Guerreiro 1 e o Pathbuilder o barra --
e ali ele esta certo. O pre-requisito e:

> You have a spellcasting class feature with the divine or primal tradition

Um Guerreiro nao conjura. A clausula caia inteira em `requires_residuo`, e pelo
principio zero o motor nao reprova sobre o que nao avalia.

**A causa nao era falta de termo.** `spellcasting_tradition` existe desde
29/07. A causa e que `_expr` divide em `" or "` **antes** de chamar `_atomo`:
a frase virava `"...with the divine"` + `"primal tradition"`, e nenhum dos dois
casa com coisa nenhuma. E a mesma classe do defeito do item 91 -- o divisor roda
antes do parser e nao sabe o que esta cortando.

Conserto: a frase inteira e reconhecida ANTES do corte (passo 2b de `_expr`).

Na mesma passada, duas familias irmas que so passaram a ter resposta por causa
do **item 78 de hoje** (a subclasse resolve a tradicao):

- `divine spells`, `bloodline that grants arcane spells` -- 7 clausulas. Antes
  do bloodline carregar `tradition`, casar isto teria produzido reprovacao
  ERRADA num Feiticeiro, porque o motor nao sabia a tradicao dele.
- `you're able to cast spells`, `able to cast spells using spell slots` -- 4
  clausulas. A contracao `you're` nao estava no padrao e mandava
  `familiar-sage-dedication` inteiro para o residuo.

Resultado: clausulas de residuo **602 -> 598**, e a divergencia do
`ancestry_feat` foi para **zero**.

## 2. Renomeacao do Pathbuilder -- 7 pares novos, mesmo padrao de sempre

`Shory Aerialist` -> `Aerialist`, `Saoc Astrology` -> `Astrology`,
`Irriseni Ice-Witch` -> `Ice-Witch`, `Quah Bond` -> `Tribal Bond`,
`Tupilaq Carver` -> `Construct Carver`, `Shory Aeromancer` -> `Aeromancer`,
`Heir of the Saoc` -> `Heir of the Astrologers`.

Sai o nome proprio de Golarion (Shory, Saoc, Irriseni, Quah, Tupilaq) e entra o
generico. Verificado do mesmo jeito das 26 anteriores: os 7 da esquerda existem
na nossa base; os 7 da direita **nao existem em nenhum dos 43.686 docs do dump
do AoN**. Nossa base esta certa; a tabela de traducao foi para 33 pares.

## 3. Diferenca de modelo -- os 18 do `ancestry_feat`

O Pathbuilder lista as **60** ancestry feats de todas as ancestrias e pinta de
vermelho as 42 que nao cabem; nos oferecemos as 42 da ancestria do personagem.
Dos 25 que ele tinha e nos nao, **22 ele mesmo marca em vermelho**.

E defensavel dos dois lados e nao produz numero errado. Fica declarado.

## 4. Diferenca de modelo -- as dedicacoes que discordam

Das 26 do Ranger 4, 21 sao `wb=False pb=True` com motivo do tipo "exige nature
>= trained; tem untrained". E a familia JA DECLARADA em
`comparar_pathbuilder.py`: do lado dele toda escolha de pericia continua
pendente e ele conta como alcancavel; nos avaliamos o estado ATUAL e marcamos.

As 5 no sentido contrario (`wb=True pb=False`) sao principio zero funcionando:
`Ulfen Guard Dedication` exige "member of the Ulfen Guard",
`Familiar Sage` exige "You have a familiar", `Red Mantis Assassin` exige
"deity is Achaekek". Prosa narrativa que o motor nao avalia -- fica visivel em
`requires_residuo` e nao bloqueia. O Pathbuilder barra; nos mostramos marcado.

## 5. Recorte de fonte -- os 3 que so nos temos

`Chelaxian Scion Dedication` (AP #223), `Knight Vigilant` (Character Guide),
`Venture-Gossip Dedication` (Paizo Blog). Ja identificados na 1a rodada: sao
obras que o Pathbuilder nao carrega. Nao e defeito de nenhum dos dois.

`Lightning Snares` e `Wild Empathy` foram investigados na mesma rodada, e os
dois sao **recorte de edicao**, nao defeito de ninguem:

- **`Lightning Snares`** existe DUAS vezes no AoN: `feat-527` (Core Rulebook,
  trait `Ranger`, arquetipo Snarecrafter) e `feat-6418` (Player Core 2, trait
  `Archetype`, mesmo arquetipo). O remaster o RECLASSIFICOU de feat de classe do
  Ranger para feat de arquetipo puro. A nossa base carrega a versao remaster,
  entao ele nao entra na aba de Class Feats -- e certo. O Pathbuilder mostra a
  classificacao LEGADA porque a sonda liga "Allow outdated CRB and APG" de
  proposito (sem isso ele esconde metade do conteudo).
- **`Wild Empathy`** tem UMA entrada no AoN (`feat-499`, nivel 2, trait
  `Ranger`, arquetipos Beastmaster e Mammoth Lord). Pela fonte e feat de Ranger,
  e e assim que a nossa base o classifica. O Pathbuilder o trata como feat de
  arquetipo e nao o oferece na aba de classe. A fonte esta do nosso lado.

Nenhum dos dois vira trabalho.

---

## 6. Segunda leva da rodada: Wizard 16, Cleric 20, Rogue 8 / skill_feat

Rodada em terreno ainda mais novo -- nivel 16 e 20, e o slot de `skill_feat`
fora do Guerreiro. Deu **o defeito mais grave do dia**, e dois consertos de
parser.

### DEFEITO NOSSO, grave: `has` de class-feature era SEMPRE falso

O Clerigo 20 nao podia pegar `Martyr`, que exige `Divine Font` -- e ele tem
Divine Font desde o nivel 1.

`_termo_has` monta "o que eu tenho" com
`{f["id"] for f in self.features if f.get("raiz") != excluir}`. A guarda existe
para o feat nao satisfazer o proprio requisito. Mas feature vinda da PROGRESSAO
da classe nao tem `raiz` (e `None`), e `_avaliando` so e setado dentro de
`_checar_requisitos` -- em `candidatos()` ele **nunca** e setado. Entao
`None != None` dava `False` e toda class-feature era descartada.

Nao era caso de borda: era o caminho normal do app.

**139 clausulas `has` em 135 registros**: `spellstrike` 21, `arcane-cascade` 12,
`ki-spells` 12, `debilitating-strike` 8. Um Magus nunca podia pegar feat de
Spellstrike; um Monge, feat de Ki.

### DEFEITO DO COMPARADOR: 118 falsos positivos no skill feat

A aba "Class Feats" ja tinha a guarda `and "archetype" not in traits` -- os 11
feats de mascara do Wizard carregam `wizard` E `archetype` juntos. A aba "Skill
Feats" nao tinha. Resultado: 24 feats de Player Core 2 que carregam `archetype`
E `skill` (Linguist, Dandy, Acrobat, Vigilante...) apareciam como sobra nossa.

Nos os oferecemos no slot de pericia, e isso esta CERTO pelo RAW -- desde que
haja a dedicacao. Mas nao e o recorte da aba dele. **118 -> 7.**

### `master at Deception`

Uma preposicao. `RANK_RE` aceitava `in` e nao `at`, e `Doublespeak` caia inteiro
no residuo. Uma palavra na alternancia, e o Pathbuilder e nos passamos a
concordar. Residuo 598 -> 597.

### 2 pares novos de renomeacao (PFS Guide)

`Kreighton's Cognitive Crossover` -> `Cognitive Crossover` e `Fane's Escape` ->
`Card Sharp's Escape`. Kreighton e Fane sao personagens da Pathfinder Society.
A tabela foi a **35 pares**.

### O que sobrou, e nao e defeito

- **5 feats de Pathfinder #223: Hell's Destiny** so nossos -- AP que ele nao
  carrega.
- **`Automatic Knowledge` e `Dubious Knowledge`**: "expert in a skill with the
  Recall Knowledge action". E um QUANTIFICADOR ("alguma pericia que tenha tal
  acao") que o predicado nao sabe expressar. Fica no residuo; nos mostramos
  marcado e ele barra.
- **`Ravening's Desperation`**: exige `lore:zevgavizeb`, e a familia ja
  declarada de pericia pendente.
- **As dedicacoes `wb=True pb=False`** (Alkenstar Agent, Artillerist, Eldritch
  Archer, Marshal, Five-breath Vanguard): principio zero -- pre-requisito
  narrativo em `requires_residuo` nao bloqueia aqui e bloqueia la.

## O que fica para a proxima

- Slot de `general_feat` fora do Guerreiro.
- O quantificador "uma pericia que tenha a acao X", se aparecer mais vezes.

---

## 7. Terceira leva: Bard 7 / general_feat e Monk 10 -- ZERO defeitos nossos

Duas classes que nem estavam na bancada (`DEFAULT` do comparador so tinha
Fighter, Wizard, Cleric, Ranger, Rogue e Barbarian). Os boosts das duas foram
**medidos** com `sonda-estado-pathbuilder.mjs`, nao chutados -- o proprio
comparador ja avisava que chutar fabrica divergencia: Bard sai `STR +2 DEX +1
CON +1 CHA +1`, Monk sai `STR +3 DEX +1 CON +1`.

Resultado: **nenhum defeito nosso.** Tudo cai nas duas familias ja declaradas.

- **17 feats do Kingmaker AP** (trait `kingdom`) so nossos -- subsistema de reino
  que o Pathbuilder nao carrega. Recorte de fonte, como os 5 de Hell's Destiny.
- **`Advanced Qi Spells`** (`wb=False pb=True`): exige `has: wb:feat/qi-spells`,
  e o Monk 10 da bancada nao pegou esse feat. Ele conta a escolha PENDENTE como
  alcancavel; nos avaliamos o estado atual. Mesma familia da pericia.
- **`Sacred Ki`** (`wb=True pb=False`): exige "Ki Strike, you follow a deity",
  as duas em `requires_residuo`. Principio zero.
- **`Aurochs-Headed`**: feat de trait `skill` que ele lista tambem na aba de
  General Feats. Recorte de aba dele, 1 ponto.

Esta leva vale menos pelo que achou e mais pelo que NAO achou: depois dos tres
consertos das levas anteriores, duas classes novas e um slot novo passaram sem
defeito.

---

## 8. Quarta rodada: Barbaro 6 / class_feat -- terreno do conserto de hoje

Escolhido de proposito: o eixo `instinct` do Barbaro acabou de mudar (spec
`instinto-com-dois-ids`), e a sonda e o oraculo de comportamento que confirma.

| aba | so no PB | so no WB | discordam |
|---|---:|---:|---:|
| Class Feats (98 x 99) | 1 | 0 | 3 |
| Dedication Feats (226 x 224) | 0 | 3 | 16 |

**Nenhum defeito nosso.** Tudo cai nas familias ja declaradas:

- **`Raging Athlete`** exige `athletics >= expert` e temos `trained`: a familia da
  escolha de pericia pendente do lado dele.
- **`Exemplar Dedication`, `Mauler Dedication`** exigem STR >= 14 e o nosso tem
  12 -- os boosts do PB nao batem com os nossos, e o proprio comparador avisa que
  chutar boost fabrica divergencia.
- **`Aldori Duelist Dedication`** exige treino na espada de duelo Aldori, que um
  Barbaro nao tem. Nos estamos certos e ele e permissivo.
- **`Alkenstar Agent`, `Five-breath Vanguard`, `Pactbinder`** (`wb=True
  pb=False`): principio zero -- pre-requisito narrativo em `requires_residuo`.
- **`Nocturnal Senses`/`Supernatural Senses`** dependem de sentido/feat que o
  personagem da bancada nao tem.

### O achado, e ele nao estava na aba

**`Reckless Abandon` so no Pathbuilder.** Investigado: o feat do Barbaro foi
RENOMEADO para `Desperate Wrath` no Remaster (`feat-173` -> `feat-5868`), e nos
temos o novo. Recorte de edicao, como `Lightning Snares` na rodada 3.

Mas ao conferir apareceu outra coisa: **`Desperate Wrath` nao tinha o nome antigo
como alias**, e existe um feat GOBLIN homonimo de nivel 17. Quem digitasse
`Reckless Abandon` achava o goblin -- silenciosamente errado.

Em 30/07 esse buraco foi fechado para MAGIA (159 renomeacoes). Fora de magia
continuava aberto: **335 renomeacoes**, em equipment 217, weapon 57, feat 31,
heritage 12, ritual 9, armor 7 e ancestry 2. `Gnoll -> Kholo`,
`Grippli -> Tripkee`, `Choker-Arm Mutagen -> Bendy-Arm Mutagen`.

A rodada valeu menos pela aba e mais pelo que a investigacao de UM item
divergente destravou. Spec `2026-07-30-alias-legado-fora-de-magia.md`.
