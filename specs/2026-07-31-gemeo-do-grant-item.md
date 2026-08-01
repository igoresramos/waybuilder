---
spec: gemeo-do-grant-item
req: WB-062
project: waybuilder
version: 1
status: implementada
created: 2026-07-31
altera: [WB-002]
todo: 107
---

# Spec -- o pack do UUID decide o kind, e o gemeo segura a ponte

> Terceira vez em 31/07 que o **portao 8** me pega citando spec inexistente. A
> regra e spec primeiro; o portao existe porque a regra e violavel.

## Como isto comecou

Investigando o item 107 (37 features "presas no balaio"), a hipotese era que
faltasse por-las na PROGRESSAO da classe. **Errada**: o Foundry nao as lista nas
`items` da classe -- o Ranger tem `Hunt Prey@1` e `Hunter's Edge@1`, sem
`Warden Spells`; o Alquimista tem `Alchemy@1`, sem `Advanced Alchemy`. Elas sao
**sub-features concedidas pela mae**, e a mae as declara:

```
Alchemy -> GrantItem Compendium.pf2e.classfeatures.Item.Formula Book
           GrantItem Compendium.pf2e.classfeatures.Item.Advanced Alchemy
           GrantItem Compendium.pf2e.classfeatures.Item.Versatile Vials
           GrantItem Compendium.pf2e.classfeatures.Item.Quick Alchemy
```

## O defeito, medido

`converter_rule_elements.py` resolvia o UUID **so por nome**, e o indice
`por_nome` PREFERE `feat` no desempate. Entao, com o Foundry dizendo
`classfeatures.Item.Advanced Alchemy`, a base gravava
`grant_feat: ["wb:feat/advanced-alchemy"]` -- o gemeo errado -- e o
class-feature ficava inalcancavel. E o achado do item 100, agora com a causa.

O outro caminho (`unificar_efeitos.resolver_grant_item`) **ja** usava o pack
para desempatar. Faltava so alinhar este.

| | |
|---|---:|
| `GrantItem` com pack conhecido | 548 |
| nomes que existem em dois kinds | 23 |
| **gravados no kind ERRADO** | **6** |

Os 6: `alchemy` -> advanced-alchemy e quick-alchemy; `rogue-dedication` ->
surprise-attack; `keen-recollection`; `inventor-dedication` e
`peerless-inventor` -> `wb:class/inventor` onde devia ser `wb:feat/inventor`.

## A quebra que o item 100 previu, e que aconteceu

Corrigido o alvo, `wb:feat/advanced-alchemy` deixou de ser satisfeito -- e
`efficient-alchemy` cita o FEAT. Um Alquimista 8 passou a NAO atender um feat
que atendia. O item 100 dizia, em 2026-07-31 de manha:

> trocar o alvo do `grants` sozinho QUEBRARIA a cadeia que hoje funciona. O
> caminho e `equivale_a` entre o par.

Era exatamente isso. O conserto e o prescrito la: **`equivale_a` entre os quatro
pares em que a correcao trocou o lado concedido**, e o `has` passa a aceitar o
gemeo nos dois sentidos -- como ja fazia para os gemeos de instinto.

## O indice de gemeos e CACHEADO na base

A primeira versao varria os 19.606 registros a cada `has`. Como `has` roda
milhares de vezes por ficha, o oraculo passou de segundos para **mais de seis
minutos** e estourou o timeout. O indice e o mesmo trabalho feito uma vez, na
`Base` -- que e onde todo cache derivado do catalogo vive, pela mesma razao
escrita no topo de `base.ts`.

## Como se prova que funciona

1. `wb:class-feature/alchemy` concede `wb:class-feature/advanced-alchemy` e
   `wb:class-feature/quick-alchemy` -- nao mais os feats homonimos.
2. Um Alquimista 5 responde `True` ao `has` dos QUATRO ids do par (os dois
   class-features e os dois feats).
3. `efficient-alchemy` volta a ser atendido por um Alquimista 8.
4. `Surprise Attack` chega ao Ladino com Rogue Dedication pelo class-feature.
5. O oraculo roda em segundos, nao em minutos.
6. Paridade Python/TS, 10 portoes.

## O que esta spec NAO resolve, e declara

Os outros **33** registros do item 107 continuam so no balaio: eles nao tem
gemeo concedido, e a mae que os concederia (`Cause`, do Campeao) usa
`GrantItem` com UUID **dinamico**
(`{item|flags.system.rulesSelections.cause}`) -- aponta para o que o jogador
escolheu, e o extrator pula os 163 casos assim, corretamente. Resolver isso pede
interpretar a escolha do jogador no build, que e outra familia.
