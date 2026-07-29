---
spec: grant-item-por-nome
project: waybuilder
version: 1
status: aprovada
created: 2026-07-29
todo: 60
---

# Spec -- `grant_item` aponta para o Foundry e nao para a base

## O problema

619 concessoes de `grant_item` na base, e **nenhuma** aponta para um id `wb:`:

| forma | quantas |
|---|---:|
| UUID do Foundry | 533 |
| UUID dinamico (`{item\|flags...}`) | 86 |
| id `wb:` | **0** |

O motor so aplica alvo que comeca com `wb:`, entao **nenhuma delas entrega
nada**. E o mesmo defeito do item 70 (`grant_feat` de background), com outra
roupa.

## A medicao que define o desenho

O UUID termina com o **nome**, nao com o `_id`:

```
Compendium.pf2e.feats-srd.Item.Alchemical Crafting
Compendium.pf2e.actionspf2e.Item.Quick Alchemy
```

Por isso a ponte `xref.foundry` (que casa por `_id`) resolve **zero** dos 533.
Casando por nome normalizado contra a base:

| resultado | quantos |
|---|---:|
| resolve para exatamente um registro | **312** |
| ambiguo (nome em mais de um kind) | 21 |
| nao encontrado | 200 |

Os 21 ambiguos sao sempre o mesmo padrao -- `Quick Alchemy` existe como
`class-feature` e como `feat`, `Rage` como `class-feature` e como `trait`. **O
proprio UUID desempata**, porque o pack diz o kind:

| pack | kind |
|---|---|
| `feats-srd` | `feat` |
| `classfeatures` | `class-feature` |
| `equipment-srd` | `equipment` |
| `spells-srd` | `spell` |

Os 200 nao encontrados sao majoritariamente `actionspf2e` -- acoes como
`Absorb into the Aegis` e `Assume a Role`, que a base **nao modela como kind**.
Nao e falha de resolucao, e ausencia de escopo.

## A decisao

Resolver no pipeline, por nome, com o pack como desempate. Alvo que nao resolve
**mantem o UUID original** -- o motor continua avisando, e o relatorio do build
conta. Nao inventar id.

UUID dinamico (`{item|flags...}`) fica como esta: ele depende de escolha ainda
nao feita, e e o mesmo territorio do ChoiceSet.

## O que esta spec NAO resolve, e declara

- **As 200 acoes.** Enquanto `action` nao for um kind da base, esses
  `grant_item` nao tem para onde apontar. Vira item proprio se a ficha precisar
  listar acoes concedidas.
- **Os 86 UUID dinamicos.** Dependem da escolha do jogador; o caminho e o mesmo
  do `choice` (spec `2026-07-29-choiceset.md`).

## Como se prova que funciona

1. Depois de reemitir, `grant_item` com id `wb:` sobe de 0 para ~333.
2. `Quick Alchemy` vindo de `Compendium.pf2e.classfeatures.Item.Quick Alchemy`
   resolve para `wb:class-feature/quick-alchemy`, e nao para o feat homonimo.
3. Alvo de `actionspf2e` continua com o UUID original, e o motor segue avisando.
4. Um personagem que recebe um `grant_item` resolvido passa a ter o item em
   `concedidos`.
5. Os 10 portoes seguem verdes.
