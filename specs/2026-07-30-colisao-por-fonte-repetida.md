---
spec: colisao-por-fonte-repetida
req: WB-031
project: waybuilder
version: 1
status: implementada
created: 2026-07-30
altera: [WB-002]
todo: 79
---

# Spec -- os 102 irmaos fantasmas que o desmembrador criou

## O problema, na forma em que o item o descreve

O item 79(e) fala de "17 spells zumbi (`desmembrado_de`) com rank/tradicoes
ausentes, duplicatas orfas de fusao -- o canonico existe completo com outro id".

Confere. `wb:spell/object-reading-uncommon` tem `traits: ["uncommon"]`, nenhuma
tradicao e nenhum par no Foundry; `wb:spell/object-reading` tem traits de acao,
tradicao Occult e xref completo nas tres fontes. Sao a MESMA magia.

## A causa

`desmembrar_colisoes.py` cria um irmao quando o AoN tem dois documentos com o
mesmo `(kind, nome)` e assinaturas diferentes. A assinatura e
`(level, traits ordenados)`, e existe um comentario declarando a intencao:
`if len(assinaturas) < 2: continue  # mesma entidade em duas edicoes`.

A assinatura nao basta. Para `Object Reading` o AoN tem TRES docs:

| doc | fontes | traits |
|---|---|---|
| `spell-2012` | Player Core 2, Pathfinder #147 | concentrate, manipulate |
| `spell-705` | Advanced Player's Guide | (legado, declarado via `remaster_id`) |
| `spell-553` | Pathfinder #147, Player Core 2 | uncommon |

`spell-705` e filtrado, porque declara `remaster_id`. Mas `spell-553` e
`spell-2012` **sao o mesmo feitico**, com o mesmo conjunto de fontes em ordem
diferente e traits de edicoes diferentes -- e o AoN nao declara o par. A
assinatura acusa diferenca e o desmembrador cria o irmao.

## A decisao

A guarda ganha um segundo criterio, que e a mesma intencao escrita melhor:
**se todos os grupos tem o MESMO conjunto de fontes, e a mesma entidade** --
conjunto, nao lista, porque a ordem varia entre os docs do AoN.

Medido na base: isso alcanca **102 dos 131** desmembramentos (equipment 68,
spell 17, feat 13, weapon 3, archetype 1). Os outros 29 tem conjuntos de fontes
diferentes e continuam desmembrados -- entre eles os 6 `class-feature` e os 9
`weapon`, que sao colisao de verdade.

## Por que 102 e seguro, e como isso foi verificado

**Nenhum dos 102 e citado por nenhum registro da base.** Medido: zero
ocorrencias do id de qualquer um deles fora do proprio registro. Sao alcancaveis
so por id direto -- ninguem depende deles, e o canonico existe completo.

Se algum fosse citado, ele nao entraria nesta spec: sumir com registro citado e
criar orfa, que e o que o portao 3 existe para pegar.

## O que esta spec NAO resolve, e declara

- **Os 29 desmembramentos restantes do detector.** Tem fontes diferentes, e
  diferenca de fonte e o sinal mais forte de que sao entidades distintas. Mais
  os 5 curados a mao, que a curadoria protege de proposito.
- **A queda de cobertura** que isso provoca no portao 4 e INTENCIONAL, e entra
  pela flag `--aceitar-queda`, que existe para exatamente este caso
  ("consolidar duplicata", diz o proprio comentario do portao).

## Como se prova que funciona

1. `wb:spell/object-reading-uncommon` deixa de existir; `wb:spell/object-reading`
   continua, completo.
2. Os registros com `desmembrado_de` caem de 131 para **34**: os 29 que o
   detector automatico mantem (fontes diferentes) mais os **5 curados a mao**
   em `colisoes_identidade.json`, que sao conferidos doc a doc contra o AoN e
   nao passam pelo detector.
3. Nenhuma referencia quebra -- o portao 3 continua em zero.
4. O portao 7 (homonimo no mesmo kind) nao piora.
5. Nenhum fixture muda de valor: nada citava os 102.
6. Quatro camadas verdes.
