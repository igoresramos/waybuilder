---
spec: estatisticas-de-familiar-e-eidolon
req: WB-060
project: waybuilder
version: 1
status: implementada
created: 2026-07-31
todo: 43
---

# Spec -- familiar e eidolon ganham numero, e a fonte nunca faltou

## O item estava bloqueado por uma premissa falsa

O item 43 dizia: *"SOBRA SO O STAT BLOCK, e ele depende de FONTE que nao
temos... PROXIMO PASSO: conseguir a fonte das estatisticas"*.

A fonte esta em disco, e e a **decima primeira lacuna de leitura** -- a
primeira que nao e um campo, e um **arquivo inteiro**:
`pipeline/dados_brutos/aon_dump/rules.json` tem **3.645 registros** e nenhum
extrator o abre (grep em `pipeline/*.py` e `pipeline/extratores/*.py`: zero).

Familiar e eidolon nao tem "stat block" no sentido do companheiro animal
(numeros fixos por registro). Os dois **derivam do mestre**, e e por isso que
procurar tabela nao achava nada: o que existe e **formula**.

## Familiar -- formula fechada

Remaster: `rules-2121` diz que o familiar e o feat geral **Pet** com
habilidades especiais. O statblock esta no proprio `Pet` (Player Core pg. 259,
em `aon_feats.json`):

| campo | regra | fonte |
|---|---|---|
| nivel | igual ao do mestre | Pet |
| AC e saves | **iguais aos do mestre**, antes de circunstancia e status | Pet |
| Perception, Acrobatics, Stealth | `3 + nivel` | Pet |
| demais pericias | `nivel` apenas | Pet |
| HP | `5 x nivel` | Pet |
| Speed | 25 pes (ou swim 25, se aquatico) | Pet |
| tamanho | Tiny | Pet |
| sentidos | low-light vision | Pet |
| sem atributo proprio | "doesn't have or use its own attribute modifiers" | Pet |
| sem bonus de item | "can never benefit from item bonuses" | Pet |

Unico delta do familiar sobre o Pet, em `rules-2122` (Player Core pg. 212):
nas tres pericias, pode usar **`mod de conjuracao + nivel` se for maior** que
`3 + nivel`.

## Eidolon -- formula geral e arrays por tipo

`rules-1582` (Secrets of Magic pg. 58): nivel igual ao do invocador; **expert**
em Fortitude e Will, **trained** em Reflex e Perception, trained em ataque
desarmado e defesa desarmada; **compartilha as proficiencias de pericia do
invocador**.

**O eidolon nao tem HP proprio** -- compartilha o pool do invocador. Isso e
achado, nao lacuna: e por isso que `eidolon` na base so tinha velocidade.

Os arrays por tipo (atributos, cap de Dex, bonus de item na AC) estao
**estruturados** em `pipeline/dados_brutos/pf2etools_repo/data/companionsfamiliars.json`,
chave `eidolon`: **12 registros**, cada um com 1 ou 2 arrays
(`abilityScores`, `ac.number`, `ac.dexCap`), mais `skills` e `size`.

A base tem **13** registros de eidolon. O 13o e `Swarm`, que so existe em
prosa -- ele fica **sem array**, marcado, e a ficha diz por que.

## As decisoes

1. **Nada de numero escrito a mao no motor.** A formula vira registro na base
   (`wb:stat-formula/familiar` e `wb:stat-formula/eidolon`), lido do `Pet`, de
   `rules-2122` e de `rules-1582`. O passo **falha alto** se a prosa mudar e os
   valores esperados nao casarem -- e o padrao das assercoes deste projeto.
2. **AC e saves do familiar sao os do MESTRE.** Nao se recalcula: le-se
   `self.ac` e `self.salvas` da propria ficha. Se o mestre muda, o familiar
   muda junto, de graca.
3. **A regra 17b continua valendo** para o nivel: `cap_ator` ja limita
   companheiro, familiar e eidolon a `min(class_level + 2, nivel_de_personagem)`.
   Esta spec **nao mexe** nisso.
4. **`Swarm` sem array e marcado, nao escondido.** Principio zero.
5. **O array do eidolon e ESCOLHA do jogador** quando o tipo tem dois. Sem
   escolha, a ficha mostra o primeiro e diz que ha outro -- nao inventa.

## O que esta spec NAO resolve, e declara

- **As 10 habilidades de familiar** (`rules-2125`: amphibious, burrower,
  climber, darkvision, echolocation, fast movement, flier, manual dexterity,
  scent, tough). So `Tough` mexe em numero (`+2 HP por nivel`); as outras nove
  sao sentido e movimento. A ESCOLHA diaria de habilidades e outra familia
  (recurso por dia, nao construcao).
- **Os ataques desarmados do eidolon** (`rules-1584`: 4 dados possiveis para o
  primario, secundario fixo em 1d6 agile finesse). Depende do consumidor de
  ataque conceder Strike, que e a mesma familia dos 30 `Strike` do Animal
  Instinct ja recusada no item 101.
- **O boost de atributo do eidolon** ("gets boosts at the same time you do",
  `rules-1583`): pede o mesmo orcamento de boost do personagem, aplicado a
  outra ficha. Fica para item proprio.

## Como se prova que funciona

1. `wb:stat-formula/familiar` e `wb:stat-formula/eidolon` existem na base, com
   `prov` apontando para a fonte.
2. Os 12 tipos de eidolon ganham `stats`; `Swarm` fica sem, e so ele.
3. Um Bruxo 6 com familiar: HP **30**, AC e saves **iguais aos dele**,
   Perception `3 + 6 = 9`, velocidade 25, tamanho Tiny.
4. O mesmo Bruxo com CHA +4: Perception vira **10** (`4 + 6`), porque o mod de
   conjuracao e maior que 3.
5. Um Summoner 6 com eidolon Angel: **sem HP proprio**, Fortitude e Will
   expert, Reflex e Perception trained, atributos do array escolhido.
6. Eidolon `Swarm`: aparece com o aviso de que o array nao esta na fonte
   estruturada -- marcado, nao escondido.
7. A regra 17b nao muda: um Bruxo 1 / Guerreiro 5 tem familiar de nivel 3.
8. Paridade Python/TS, diff de fixture LIDO.
9. Quatro camadas verdes.
