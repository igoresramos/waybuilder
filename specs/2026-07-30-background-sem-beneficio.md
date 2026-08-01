---
spec: background-sem-beneficio
req: WB-026
project: waybuilder
version: 1
status: implementada
created: 2026-07-30
todo: 83
---

# Spec -- os 10 backgrounds que nao dao nada

## O problema

Um background de PF2e da dois boosts de atributo (um escolhido entre dois, um
livre) e treina duas pericias. **Dez backgrounds da base nao dao nada**: `boosts`
e `skill_training` vazios nos dois.

Escolher `Refugee` na criacao nao muda um numero sequer da ficha.

## A causa, e ela e a mesma de hoje o dia inteiro

Os dez **nao existem no Foundry** -- verificado arquivo a arquivo. A enumeracao
da base vem do Foundry ("escopo cortado no que o construtor usa"), e esses
registros entraram pelo AoN, que e a fonte de `text`/`name`/`rarity`. O extrator
le do AoN os campos textuais e **nao le `attribute` nem `skill`**, que sao
justamente o beneficio.

Medido nos dez: o AoN tem `attribute` e `skill` em **nove**. Exemplos:

| background | `attribute` | `skill` |
|---|---|---|
| `reclaimed-investigator` | Intelligence, Wisdom | Occultism, Crimson Reclaimers Lore |
| `refugee-fop` | Constitution, Intelligence | Survival, Hunting Lore |
| `muesellos-student` | Dexterity, Intelligence | Crafting |

E a QUINTA lacuna de leitura encontrada hoje sob a aparencia de lacuna de fonte.

## As decisoes

1. **`boosts` e `skill_training` passam a ser lidos do AoN** quando estao
   vazios. So quando vazios: registro que veio do Foundry ja tem o dado
   estruturado e nao e tocado.
2. **A forma e a mesma que a base ja usa**, sem inventar variante:
   `boosts` = `[{ability_boost: {opcoes: [dois codigos], quantidade: 1}},
   {ability_boost: {livre: true, quantidade: 1}}]`. O segundo boost, livre, e
   regra do livro e nao vem da fonte -- todo background da um.
3. **`Lore` vai para `lore`, o resto para `skills`.** E o que o schema ja faz.
4. **"X Lore or Y Lore" NAO e um nome de pericia.** A entrada com ` or ` e uma
   ESCOLHA, e o schema nao tem forma para isso aqui. Fica de fora e CONTADA --
   inventar `lore: ["Driving Lore or Piloting Lore"]` criaria uma pericia que
   nao existe.

## O que esta spec NAO resolve, e declara

- **`historical-reeanactor`**, o unico dos dez sem `attribute` e sem `skill` no
  AoN tambem. Nao ha o que ler; continua vazio e contado.
- **A escolha entre duas Lore**, pelo motivo acima. Se aparecer com frequencia,
  vira modelo proprio.
- **Os outros achados do item 83**: as 4 class-features orfas de progressao
  (`focus-spells`, `improved-evasion`, `iron-will`, `martial-weapon-mastery`) e
  os 52 registros de `ikon`/`mythic-calling`/`element`/
  `deviant-ability-classification` com 100% de grants vazio. Sao outras
  medicoes, com outras causas.

## Como se prova que funciona

1. `wb:background/refugee-fop` responde `boosts` com `["con","int"]` e o livre.
2. E `skill_training` com `skills: ["survival"]` e `lore: ["Hunting Lore"]`.
3. Backgrounds que ja tinham o dado **nao mudam** -- o passo so preenche vazio.
4. `historical-reeanactor` continua vazio, e aparece no relatorio.
5. `prov.boosts` e `prov.skill_training` dizem `aon` nos preenchidos.
6. Os 10 portoes seguem verdes, inclusive o 1.
