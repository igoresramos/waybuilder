---
spec: categoria-de-feat-por-trait
req: WB-029
project: waybuilder
version: 1
status: implementada
created: 2026-07-30
altera: [WB-002]
todo: 34
---

# Spec -- os 164 feats sem categoria

## O problema

`feat_category` ordena a lista do picker: feat de classe no slot de classe,
de ancestria no slot de ancestria. **164 feats de 6.265 estavam sem ela** --
sem categoria, o feat nao tem slot natural.

## A causa, e sao duas

`extratores/feats.py` ja deriva a categoria e fechou 378 registros em 29/07.
O que sobrou nao sobrou por um motivo so:

| quantos | por que |
|---:|---|
| 94 | tem trait de CLASSE (`druid`, `commander`, `psychic`) e a regra do extrator nao olha trait de classe -- ela pergunta ao campo `class` do doc do AoN, que feat nao casado nao tem |
| 51 | idem, com trait de ancestria |
| 11 | trait de HERANCA versatil (`nephilim`, `naari`) -- feat de linhagem e feat de ancestria |
| 8 | nasceram DEPOIS do extrator, em `desmembrar_colisoes.py` (`know-it-all-archetype`, `rallying-charge-visual`) |

O quarto grupo e o mais revelador: `wb:feat/rallying-charge` tem
`feat_category: "class"` e `wb:feat/rallying-charge-visual` tem `null`, com o
MESMO trait `archetype`. Mesma prosa, mesma regra, e um caiu fora so por ordem
de execucao.

## A decisao: um passo tardio, e nao mais uma condicao no extrator

O passo roda sobre a base inteira, depois de todos os registros existirem.
Assim ele alcanca tanto o feat que nao casou com o AoN quanto o que nasceu do
desmembramento -- e a regra fica num lugar so.

Nao sobrescreve categoria existente: so preenche vazio. Quem ja respondeu,
respondeu.

Ordem de desempate, a mesma que o extrator ja usava: `mythic`, `skill`,
`general`, `archetype`, depois trait de classe, de ancestria e de heranca.
`archetype` vem antes de trait de classe de proposito -- feat de arquetipo de
multiclasse carrega os dois traits, e ele e feat de classe pela rota do
arquetipo.

## O que esta spec NAO resolve, e declara

Os dois outros residuos do item 34 foram MEDIDOS e nao sao defeito:

- **`source.page` ausente em 1.596 registros.** Dos quais **1.519 nao tem xref
  do AoN nenhum**: sao registros so do Foundry/pf2etools, e essas fontes nao
  publicam pagina. E lacuna de FONTE, nao de leitura -- e por isso o numero
  cresce quando a base cresce (1.506 -> 1.598 -> 1.596), o que o item lia como
  "PIOROU". Dos 77 restantes, o AoN nao traz pagina em 71 e traz em 6.
  Recuperar por NOME chegaria a 260 registros, mas 213 deles sao
  class-feature, que e justamente o kind com colisao de nome em massa (95 no
  portao 7 pre-fusao) -- casar por nome ali entregaria a pagina do homonimo. A
  regra do item e "nunca por chute", entao fica declarado.
- **`prov.class` "foundry (inferido de traits)" em 414 de 847.** Isso nao e um
  nao-resposta: e a procedencia dizendo COMO o valor foi obtido, que e a
  funcao dela. Diferente de `"desconhecida"`, que foi corrigido no item 52.

## Como se prova que funciona

1. Nenhum feat da base fica com `feat_category` nulo ou ausente.
2. `wb:feat/rallying-charge-visual` responde `class`, igual ao gemeo.
3. `wb:feat/azata-magic` (trait `nephilim`) responde `ancestry`.
4. Nenhum feat que ja tinha categoria muda de valor.
5. `prov.feat_category` diz de onde veio (`derivado:trait-de-classe` etc).
6. Quatro camadas verdes.
