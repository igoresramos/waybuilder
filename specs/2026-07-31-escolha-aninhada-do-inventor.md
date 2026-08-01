---
spec: escolha-aninhada-do-inventor
req: WB-059
project: waybuilder
version: 1
status: implementada
created: 2026-07-31
todo: 105
---

# Spec -- o balaio do Inventor era escolha ANINHADA, nao lista solta

## O que a medicao mostrou

O Inventor e a unica classe **sem eixo nenhum**: tres blocos `outras-opcoes`,
nos niveis 1, 7 e 15, com 22, 15 e 15 opcoes. Escolher qualquer coisa ali nao
significa nada, porque o balaio nao e eixo -- e o que sobra.

Lido o conteudo, o nivel 1 mistura **duas coisas de naturezas diferentes**:

| natureza | quantas | exemplos |
|---|---:|---|
| INOVACAO (a escolha de identidade) | 4 | Weapon, Armor, Construct, Light Mortar Innovation |
| MODIFICACAO da inovacao | 18 | Advanced Design, Blunt Shot, Razor Prongs, Speed Boosters |

E os niveis 7 e 15 sao **tiers de modificacao**, nao features soltas. O Foundry
declara isso explicitamente, em `ChoiceSet` de lista literal:

| dono | flag | opcoes |
|---|---|---:|
| `Weapon Innovation` | `initialModification` | 11 |
| `Armor Innovation` | `armorInnovation` | 2 |
| `Breakthrough Innovation` | `breakthroughModification` | 32 |
| `Revolutionary Innovation` | `revolutionaryModification` | 46 |
| `Manifold Modifications` (feat nv 8) | `modification` | 17 |

O mesmo vale para o Mago, em escala menor: `School of Thassilonian Rune Magic`
lista 7 pecados e `School of Rooted Wisdom` lista 5 ramos -- sub-escolhas de uma
escola, que hoje estao soltas no balaio dele.

## O tamanho, medido

Varrendo o Foundry inteiro: **1.012** `ChoiceSet` de lista literal, com **529**
referencias `Compendium.*.Item.<Nome>`, **395** distintas, das quais **362**
resolvem por nome na base e **zero** sao ambiguas. Resolucao por nome e segura
aqui.

Cruzando com o balaio: **66** das 265 opcoes sao explicadas por serem opcao de
um `ChoiceSet`. Delas, **59** sao legitimas (Inventor 47, Wizard 12); as outras
**7** sao ruido -- 5 instintos do Barbaro e 2 do Campeao, cujo "dono" e um
registro `Effect:` do VTT e nao uma escolha de construcao. Ficam de fora.

## O desenho

**Nao e bloco condicional.** A opcao carrega o proprio `requires`, e
`candidatos()` ja o avalia -- e o mesmo desenho da santificacao, ja provado:
filtrar e MARCAR.

1. O eixo `innovation` nasce com as 4 inovacoes, `escolhe: 1`, nivel 1.
2. Os eixos de modificacao nascem por tier: `initial-modification` (nivel 1),
   `breakthrough-modification` (7) e `revolutionary-modification` (15).
3. Cada opcao de modificacao INICIAL ganha
   `requires: {subclass: {inventor: <a inovacao que a lista>}}`. Um Inventor de
   armadura ve as de arma **marcadas**, com o motivo escrito -- nunca escondidas.
4. As opcoes que saem do balaio saem de la: o balaio e o que sobra, e o que foi
   explicado nao sobra mais.

## As decisoes

1. **`Manifold Modifications` fica de fora do eixo.** E feat de nivel 8, nao
   progressao de classe -- entra pela familia de slot concedido por feat, que e
   outra. Suas 17 opcoes continuam alcancaveis pelos outros tiers.
2. **Os 7 do ruido ficam no balaio**, com o numero registrado. Mover opcao
   porque um item de EFEITO do VTT a cita seria confundir efeito com escolha.
3. **Resolucao por nome, e so porque e inequivoca**: 0 ambiguas em 395. Se
   aparecer ambiguidade, o registro fica onde esta.
4. **Nada de lista a mao**: o mapa dono->opcoes sai do `ChoiceSet` do Foundry.

## O que esta spec NAO resolve, e declara

- **199 das 265 opcoes do balaio** continuam sem explicacao, concentradas em
  Alchemist (33), Thaumaturge (30), Cleric (18), Animist (13), Oracle (12).
  Este e o item 69, e ele nao fecha aqui.
- **`item:slug`** (74 usos) segue ignorado no `_atomo_de_filtro` -- item 105.
- **O efeito mecanico de cada modificacao** (o que `Razor Prongs` faz no dano)
  e mecanica condicional, familia ja recusada com numero.

## Como se prova que funciona

1. O Inventor ganha eixo `innovation` com as 4 inovacoes -- hoje tem zero eixo.
2. E tres eixos de modificacao, nos niveis 1, 7 e 15.
3. O balaio do Inventor cai de 22/15/15 para o que sobrou de verdade.
4. Um Inventor de `Weapon Innovation` ATENDE as 11 modificacoes de arma; um de
   `Armor Innovation` NAO atende, e o motivo diz qual inovacao falta.
5. As opcoes que nao atendem continuam na lista, MARCADAS.
6. O Mago ganha as sub-escolhas de escola, e seu balaio cai de 14.
7. Nenhuma outra classe muda.
8. Paridade Python/TS, diff de fixture LIDO.
9. Quatro camadas verdes.
