---
spec: pericia-de-lore
req: WB-013
project: waybuilder
version: 1
status: implementada
created: 2026-07-29
todo: 88
---

# Spec -- a pericia de Lore, dos dois lados

## O problema

A comparacao com o Pathbuilder, rodada de novo depois que o predicado subiu para
92,0%, acusou `Seasoned` como divergencia: **nos barramos e ele libera**, com o
motivo `exige lore:alcohol >= trained; tem untrained`. O personagem de
comparacao e Human / **Barkeep** / Fighter -- e Barkeep concede, em RAW, treino
em Diplomacy e em **Alcohol Lore**.

A ficha tem o treino. Medido:

```
'diplomacy'          = trained
'lore:Alcohol Lore'  = trained
```

O requisito pede `lore:alcohol`. **As duas chaves falam da mesma pericia e nunca
se encontram.**

Nao ha normalizacao em lugar nenhum: `lore:` e escotilha opaca nos dois motores,
por decisao anterior (o comentario em `motor.py:486` e
`personagem.ts:517` diz "Lore e aberto por definicao", e esta certo -- o erro nao
foi deixar aberto, foi deixar **duas convencoes** para o aberto).

| lado | quem escreve | convencao | exemplo |
|---|---|---|---|
| predicado | `extratores/feats.py:528` | slug do nome **sem** o sufixo ` Lore` | `lore:alcohol` |
| ficha | `motor.py:427` / `personagem.ts:452` | nome verbatim da fonte, **com** o sufixo | `lore:Alcohol Lore` |

Tamanho: **26 chaves distintas** de predicado contra **185 nomes distintos** de
treino, em 860 registros que treinam alguma Lore.

## Os tres defeitos, que sao distintos

**44 registros** exigem Lore. Eles se dividem em tres causas, e cada uma pede um
conserto diferente:

### 1. Convencao divergente -- 35 registros

`lore:elven`, `lore:warfare`, `lore:mercantile`. O requisito e legitimo, o dado
de treino existe, e o casamento nunca acontece. **Requisito de Lore nomeada e
insatisfazivel por construcao hoje** -- nenhum personagem, com nenhuma escolha,
atende a qualquer um dos 35.

### 2. `lore:*` -- 6 registros

`Scrollmaster` pede `{"proficiency": {"lore:*": {">=": "expert"}}}`, que le-se
"expert em **alguma** pericia de Lore". O parser ja emite o curinga de proposito
(`feats.py:529-531` mapeia `a lore skill`, `any lore`, `one lore skill`), e o
motor trata `*` como se fosse o nome literal de uma Lore chamada asterisco.
Tambem insatisfazivel.

### 3. Rank vazado para dentro do nome -- 5 registros

O parser engoliu a frase de rank no nome da pericia:

| registro | chave emitida | o que deveria ser |
|---|---|---|
| `wb:feat/demon-hunter` | `lore:expert-in-demon` | `lore:demon` com `>= expert` |
| `wb:feat/devil-you-know` | `lore:expert-in-hellknight` | `lore:hellknight` com `>= expert` |
| `wb:feat/myth-hunter` | `lore:trained-in-legendary-beast` | `lore:legendary-beast` com `>= trained` |
| `wb:archetype/worm-caller` | `lore:trained-in-cave-worm` | `lore:cave-worm` com `>= trained` |
| `wb:feat/worm-caller-dedication` | `lore:trained-in-cave-worm` | idem |

Esses cinco erram **duas** coisas: a chave nao casa (defeito 1) e o rank exigido
foi perdido -- o predicado pede `>= trained` onde o livro pede `>= expert`.

## A decisao

**Ponte na comparacao, nao reescrita da ficha.** A ficha continua guardando o
nome humano (`lore:Alcohol Lore`), porque e o que o jogador le na tela; quem se
adapta e o momento da comparacao.

E o mesmo desenho de `_rank_de_arma`, de mais cedo hoje: o requisito fala em
arma NOMEADA (`weapon:aldori-dueling-sword`) e a ficha guarda rank por
CATEGORIA, e a ponte traduz no `_termo_proficiency` sem mexer em como a ficha
grava. Um segundo caso da mesma forma confirma que o lugar certo do conserto e
esse.

### `_rank_de_lore(chave, excluir)`

Chamada de `_termo_proficiency`, antes de cair no `_rank_sem`:

- chave que **nao** comeca com `lore:` -> devolve nulo, nada muda;
- `lore:*` -> devolve o **melhor** rank entre todas as Lores da ficha;
- `lore:<slug>` -> devolve o rank da Lore da ficha cujo nome, slugado e sem o
  sufixo ` Lore`, seja igual a `<slug>`.

O slug e o mesmo do parser: minusculas, nao-alfanumerico vira hifen, sufixo
` Lore` removido antes. `Alcohol Lore` -> `alcohol`; `Cave Worm Lore` ->
`cave-worm`; `Tian Xia Lore` -> `tian-xia`.

A ponte respeita `excluir` como as outras, pelo requisito circular: uma Lore que
o proprio feat concede nao pode satisfazer o pre-requisito dele.

### O parser, para os 5 do defeito 3

Em `extratores/feats.py`, a frase de rank e reconhecida **antes** do nome da
pericia, de modo que `expert in Demon Lore` emita `{"lore:demon": {">=":
"expert"}}`. Isso exige reemitir a base (`WB_REEXTRAIR=1`), entao vai depois dos
dois consertos de motor, que nao exigem.

## O que esta spec NAO resolve, e declara

- **`lore:*` com quantidade.** Nenhum registro pede hoje "duas Lores
  diferentes", entao o curinga responde presenca e nao contagem. Se aparecer,
  vira termo proprio.
- **Higiene do lado da fonte.** Entre os 185 nomes de treino ha dois
  malformados: `**Boneyard Lore (with Additional Lore perks)` e `Art Lore and
  Underworld Lore` (dois nomes numa string so). Sao defeito de extracao de
  background, fora do escopo daqui -- anotados, nao consertados, porque o
  conserto e no extrator de ancestria/background e nao muda nenhum dos 44.

## Como se prova que funciona

1. Um personagem de background **Barkeep** atende `{"proficiency": {"lore:alcohol":
   {">=": "trained"}}}`; hoje nao atende.
2. Esse mesmo personagem **nao** atende `lore:zevgavizeb` -- a ponte casa por
   nome, nao libera geral.
3. Um personagem com qualquer Lore treinada atende `{"lore:*": {">=":
   "trained"}}`; um sem nenhuma, nao.
4. `Scrollmaster` (`lore:*` com `>= expert`) continua barrado para quem so tem
   Lore trained -- o curinga compara rank, nao so presenca.
5. Uma Lore concedida pelo PROPRIO feat nao satisfaz o requisito dele.
6. Depois da reemissao, `demon-hunter` pede `lore:demon >= expert`, e nao mais
   `lore:expert-in-demon >= trained`.
7. As fichas derivam identicas nas duas linguagens.
8. Na comparacao com o Pathbuilder, `Seasoned` sai da lista de divergencia.

## Resultado medido (2026-07-29)

Consertos 1 e 2 (ponte + curinga) aplicados nos dois motores; o 3 (parser)
fica para a proxima reemissao da base.

| | antes | depois |
|---|---:|---:|
| divergencia de disponibilidade, total | 89 | **85** |
| familia lore | 6 | **2** |
| pontos a olhar no relatorio | 254 | **250** |

Os 2 que sobram sao a mesma `Ravening's Desperation` em dois slots, e ela e
**comportamento correto nosso**: pede `lore:zevgavizeb`, que o personagem
realmente nao tem. O Pathbuilder libera porque conta as 3 escolhas de pericia
ainda pendentes como alcancaveis; nos avaliamos o estado atual e MARCAMOS, que e
o que o principio zero pede.

`Seasoned` e `Experienced Professional` sairam da lista -- as provas 1, 3 e 8.

## Armadilha conhecida do porte

Termo despachado por convencao no Python e por `switch` no TS ja custou 14
fichas hoje. Esta spec **nao cria termo novo** -- muda o miolo de
`_termo_proficiency`, que ja existe nos dois lados --, entao a armadilha do
`switch` nao se aplica. A que se aplica e outra: o slug precisa ser o **mesmo**
nas duas linguagens, senao o TS casa o que o Python nao casa e a divergencia
aparece como ordem de lista de candidatos.
