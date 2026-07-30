---
spec: proficiencia-de-arma-nomeada
project: waybuilder
version: 1
status: aprovada
created: 2026-07-30
todo: [75, 95]
---

# Spec -- remap de categoria de arma, curinga `weapon:*` e a guarda morta no TS

## Os tres defeitos, medidos no dado real

### 1. `weapon_proficiency` nunca foi lido -- 91 ocorrencias, 54 registros

Feats de familiaridade com arma nao concedem treino: eles **remapeiam
categoria**. O RAW do `Archer Dedication` diz "For the purposes of proficiency,
treat any of these that are martial weapons as simple weapons". A base ja
representa isso:

```json
{"weapon_proficiency": {"definicao": ["item:category:martial",
                                      {"or": ["item:group:bow", "item:group:crossbow"]}],
                        "igual_a": "simple", "rank": null}}
```

`grep weapon_proficiency motor/motor.py` da **um hit, dentro de um docstring**.
O grant nunca e lido. Reproduzido:

```
mago8 + Archer Dedication, weapon:longbow >= trained  ->  (False, 'tem untrained')
```

O Mago e `simple: trained`, o arco longo e `martial`, e o feat existe
exatamente para ligar os dois.

### 2. `weapon:*` reprova sempre -- 5 feats inalcancaveis

`lore:*` responde o MELHOR rank de qualquer Lore (linha 1977). `weapon:*` nao
tem tratamento nenhum: `_rank_de_arma` tenta resolver `wb:weapon/*`, nao acha,
devolve `None`, e a chave literal `weapon:*` cai em `_rank_sem`, que devolve
`untrained`. Reproduzido:

```
guerreiro8 (simple/martial/unarmed = expert)
  weapon:* >= expert  ->  (False, 'tem untrained')
```

Sao 5 feats que **nenhum personagem pode satisfazer**:
`advanced-firearm-familiarity`, `cut-them-down-burn-them-out`,
`diverse-weapon-expert`, `performance-weapon-expert`, `reaper-of-repose`.

### 3. Guarda morta no TypeScript (item 95)

`personagem.ts` usa `Object.hasOwn(this.proficiencias, chave)` e
`this.proficiencias` e um `Map` -- sempre `false`. No Python
(`if chave in self.proficiencias`) funciona. Varrido o arquivo inteiro: sao 13
usos de `Object.hasOwn` e **so este** opera sobre um `Map`.

## O que da para avaliar, medido

A gramatica de `definicao` **nao sao dois padroes: sao 28 formas estruturais**.
Mas os seletores sao poucos, e quatro deles cobrem quase tudo:

| seletor | usos | resolve contra |
|---|---:|---|
| `item:base` | 120 | slug do registro (`wb:weapon/<slug>`) |
| `item:category` | 74 | `weapon_category` |
| `item:trait` | 57 | `traits` |
| `item:group` | 35 | `group` |
| `item:slug` | 5 | -- |
| `item:usage` | 3 | -- |
| `item:melee` | 2 | -- (vem sem valor) |
| `item:id` | 2 | -- |
| `item:type` | 1 | -- |

Operadores: `or` (54), `and` (15), `not` (6).

**Com `base`/`category`/`trait`/`group` + `or`/`and`/`not`, 76 das 91
ocorrencias (83,5%) ficam inteiramente avaliaveis.** As 15 restantes: 8 com
placeholder dinamico (`{item|flags.system.rulesSelections.weapon}`, que depende
de escolha nao feita -- territorio do ChoiceSet), 3 `slug`, 3 `usage`/`melee`,
1 `type`.

Os valores citados existem na base: `category` 3 de 3, `group` 13 de 13,
`trait` 26 de 30, `base` 61 de 64. Os que faltam (traits `athamaru`, `centaur`,
`merfolk`, `two-hand-d6`; armas `dueling-cape`, `khakkara`, `wakazashi`) fazem
a clausula nao casar -- o feat nao concede o remap, e ninguem recebe numero
errado.

## As decisoes

1. **O remap SOMA, nunca subtrai.** O rank da arma nomeada passa a ser o MELHOR
   entre a categoria nativa e a categoria remapeada. Ler o RAW ao pe da letra
   ("trate como simples") faria um Guerreiro expert em marcial *perder* rank ao
   pegar `Archer Dedication`, porque ele e so trained em simples. Esses feats
   existem para dar acesso, nao para tirar; e a regra geral do PF2e quando duas
   proficiencias se aplicam e usar a melhor. Decisao registrada aqui porque e
   interpretacao, nao leitura.

2. **Clausula que o motor nao sabe avaliar nao casa, e nao reprova.** Seletor
   desconhecido, valor dinamico ou arma inexistente devolvem "nao casou" -- o
   personagem simplesmente nao ganha aquele remap. Como o remap so ADICIONA, o
   principio zero fica intacto por construcao: o que o motor nao entende nunca
   vira reprovacao.

3. **`weapon:*` responde o melhor rank entre as categorias de arma**
   (`simple`, `martial`, `advanced`, `unarmed`), incluindo o que veio de remap.
   Mesmo tratamento de `lore:*`, e pela mesma razao: o curinga pergunta "voce e
   expert em ALGUMA arma?".

4. **`igual_a: null` e ignorado** -- sao 4 ocorrencias, 2 delas em
   `armigers-protection`, cujo `definicao` cita `item:slug:hellknight-plate`:
   e remap de ARMADURA carregado na chave de arma. Anomalia de dado, anotada
   como divida, nao tratada aqui.

5. **A guarda do TS vira `this.proficiencias.has(chave)`**, e sai da divida
   dormente: o remap nao escreve chave `weapon:` (ele resolve na leitura), mas o
   requisito `weapon:aldori-dueling-sword` ja existe na base e a guarda passa a
   ter caminho de teste.

Nos dois motores. Nao ha linha de `switch` a acrescentar -- isto e leitura
dentro de `_rank_de_arma`, nao termo novo.

## O que esta spec NAO resolve, e declara

- **Os 8 `definicao` com placeholder dinamico.** Dependem de uma escolha que o
  motor ainda nao modela; mesmo caminho do `grant_item` dinamico e do ChoiceSet.
- **`item:slug`, `item:usage`, `item:melee`, `item:type`** -- 7 ocorrencias.
  Entram quando houver caso que pague o seletor.
- **A class-feature compartilhada `weapon-expertise` (item 75c).** 14 classes
  apontam para ela e ela concede so `simple: expert` e `unarmed: expert`; 7
  dessas classes comecam treinadas em marcial e deveriam subir marcial tambem.
  Fica ABERTA como item proprio, com o caminho medido: a tabela HTML do AoN nao
  traz proficiencia, mas a prosa da feature traz ("Your proficiency ranks for
  simple weapons, martial weapons, and unarmed attacks increase to expert"),
  entao e extrator de texto novo, nao campo pronto.

## Como se prova que funciona

1. Mago 8 (simple trained, martial untrained) com `Archer Dedication` responde
   `weapon:longbow >= trained` -- hoje responde untrained.
2. E responde `weapon:longsword` ainda untrained: o remap do Archer so alcanca
   arco e besta, nao toda arma marcial.
3. Guerreiro 8 (martial expert) com `Archer Dedication` continua expert em
   `weapon:longbow` -- o remap nao rebaixa para trained.
4. Guerreiro 8 responde `weapon:* >= expert` -- hoje responde untrained.
5. Mago 8 nao responde `weapon:* >= expert`.
6. `wb:feat/reaper-of-repose` deixa de citar "weapon:* untrained" como motivo
   num personagem que e master em alguma categoria.
7. Um `definicao` com placeholder dinamico nao casa e nao derruba a derivacao.
8. As sete afirmacoes valem identicas no porte TypeScript, e a guarda de
   `_rank_de_arma` passa a disparar la tambem.
9. Quatro camadas verdes, fixtures regenerados e o diff LIDO.
