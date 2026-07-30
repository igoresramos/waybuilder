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

## O que fica para a proxima

- Niveis 16 e 20, que a rodada nao alcancou.
- Slot de `skill_feat` e `general_feat` em classe que nao seja Guerreiro.
