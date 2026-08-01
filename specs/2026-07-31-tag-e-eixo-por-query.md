---
spec: tag-e-eixo-por-query
req: WB-071
project: waybuilder
version: 1
status: implementada
created: 2026-07-31
todo: 99
---

# Spec -- `item:tag` deixa de ser ignorado, e dois eixos nascem dele

## O item 99 estava dimensionado errado, em tres premissas

Medido em `docs/medicoes/2026-07-31_dimensionar-avaliador-de-query.md` e
conferido contra o codigo:

1. *"exige um avaliador de query, que e trabalho e risco novos"* -- **ele ja
   existe**: `_casa_filtro` (`motor/motor.py`, `personagem.ts`), com
   `or`/`and`/`not`/`nor`/`xor`/`lte`, ja em producao.
2. *"povoariam `Exemplar.Ikon` (22)"* -- **o eixo ja existe** com 21 opcoes e
   `escolhe: 3`. O "22" era contagem de REGRAS, nao de opcoes.
3. *"as 74 literais cobrem zero do balaio"* -- cobrem **59**.

## A divida viva, que ninguem tinha contado

`_atomo_de_filtro` entende `trait`, `level`, `category` e `rarity`. Os filtros
da base usam **`item:tag` 54 vezes** e **`item:slug` 74** -- e atomo
desconhecido **conta como satisfeito**.

Esse default e **certo** para ESTREITAR slot de feat: o principio zero manda
nao esvaziar em silencio. E **destrutivo** para DEFINIR eixo, porque o eixo sai
com tudo dentro. Medido: sobra mediana de **16.383** itens, com **67 listas
erradas por excesso** contra **3 vazias**.

Dai a ordem desta spec: **ensinar `item:tag` ANTES de usar filtro para definir
eixo.**

## O que esta spec faz

**1. `tags` na base.** O Foundry publica `system.traits.otherTags` em **604**
registros (310 class-features, 129 equipment, 32 commander). Nenhum extrator
lia. Vira campo `tags`.

**2. `item:tag` no `_atomo_de_filtro`.** Um atomo novo, nos dois motores. Com
ele, os 54 usos deixam de ser ignorados.

**3. Dois eixos que nascem disso.** As duas classes com **zero** bloco de
subclasse hoje:

| classe | filtro do `ChoiceSet` | vira |
|---|---|---|
| Kineticist | `item:tag:kineticist-kinetic-gate` | eixo `kinetic-gate` |
| Commander | `item:trait:tactic` + (`commander-mobility-tactic` ou `commander-offensive-tactic`) | eixo `tactic` |

Os dois filtros sao **copiados verbatim do Foundry** para o bloco, e avaliados
por `_casa_filtro` -- nao ha lista escrita a mao.

## As decisoes

1. **O bloco guarda o FILTRO, nao a lista.** Congelar a lista no build
   dessincroniza na primeira mudanca de fonte. `candidatos()` ja avalia filtro.
2. **`escolhe` sai do numero de `ChoiceSet` irmaos.** O Commander tem cinco
   `flag` distintas (`firstTactic`..`fifthTactic`) no mesmo registro: sao cinco
   escolhas, e nao uma. O Kineticist tem `elementOne` e `elementTwo`.
3. **Nada de lista a mao**, nem para as tags: elas saem de `otherTags`.
4. **`item:slug` fica de fora**, com numero: sao 74 usos, mas todos apontam para
   registro especifico por slug, e o slug do Foundry nem sempre e o nosso id --
   resolver isso e outro trabalho, e errar ali aponta para o registro errado.

## O que esta spec NAO resolve, e declara

- **`item:slug`** (74 usos) -- acima.
- **As fatias 2 a 4** do dimensionamento: somam 20 queries exatas e **zero**
  opcao nova. Valem por correcao de nivel, nao por volume.
- **120 das 256 opcoes do balaio** continuam sem explicacao, concentradas em
  Alchemist (33), Thaumaturge (30), Cleric (18), Animist (13), Oracle (12). O
  avaliador chega a 53% e para -- item 69 continua aberto.
- **A Fatia 0** (ler as 109 referencias literais por nome) e trabalho de
  pipeline sem avaliador; fica para item proprio.

## Como se prova que funciona

1. `tags` existe na base em ~604 registros; hoje sao 0.
2. `_atomo_de_filtro` responde `item:tag:X` -- e o contador
   `filtro_ignorado` deixa de registrar `item:tag`.
3. O Kineticist ganha eixo `kinetic-gate`, e ele lista os gates elementais --
   nao os 19.604 registros da base.
4. O Commander ganha eixo `tactic` com `escolhe` maior que 1.
5. Nenhuma das duas listas sai vazia, e nenhuma sai com a base inteira.
6. Classes que ja tinham eixo nao ganham bloco novo nem perdem opcao.
7. Paridade Python/TS, diff de fixture LIDO.
8. Quatro camadas verdes.
