---
spec: acesso-por-filiacao
project: waybuilder
version: 1
status: aprovada
created: 2026-07-30
todo: 22
---

# Spec -- a condicao de acesso que a base nao carrega

## O problema

Centenas de registros incomuns so estao disponiveis para quem tem certa
filiacao: "Member of the Pathfinder Society", "Knights of Lastwall have access
to this feat", "Tian Xia origin", "You're from Hermea". Isso e o que o PF2e
chama de **Access**, e e a razao de a raridade ser `uncommon`.

A base **nao carrega nada disso**. Zero registros tem o campo.

## O que a medicao mudou no item

O item 22 propunha varrer a PROSA atras da linha `Access` e montar "~20-25 stubs
leves + termo novo no predicado". A varredura de prosa e ruim: buscar a palavra
`access` traz **716 registros**, e boa parte e ruido -- `wb:class/oracle` casa
por "Your mystery offers you strange **access** to spells", que nao e filiacao
nenhuma.

Nao precisa de prosa: **o AoN publica `access` como CAMPO**, em 1.010
documentos. E lacuna de leitura, a mesma classe do `alvos`/`salvaguarda` do item
79 -- o dado sempre esteve la, estruturado, e ninguem lia.

Casando por `xref.aon`, **728 registros nossos** ganham o campo:

| kind | registros |
|---|---:|
| equipment | 309 |
| feat | 250 |
| weapon | 89 |
| archetype | 46 |
| armor | 10 |
| animal-companion | 10 |
| background | 6 |
| familiar-specific | 6 |

E as formas se repetem, o que torna a estruturacao futura viavel: 102 "The
following regions have access to firearms...", 102 "Due to the use of
technology, all gadgets...", 80 "Member of the Pathfinder Society.", 73 "Knights
of Lastwall have access to this feat.", 72 "Characters from Absalom, New
Thassilon...", 55 "Second-mark members of the Firebrands...", 28 "Tian Xia
origin", 27 "You're from Hermea".

## As decisoes

1. **`acesso` passa a existir, em TEXTO, lido do AoN.** Verbatim, sem parse --
   mesma decisao do `alvos` e da `salvaguarda`: o campo e para LER na ficha, e
   transformar em estrutura e outra decisao, que precisa de um consumidor.
2. **Um passo de build, e nao cinco extratores.** Os 728 registros vem de oito
   kinds e de pelo menos cinco extratores diferentes; o join e por `xref.aon`,
   que so existe depois da reconciliacao. `aplicar_acesso.py` roda com os outros
   `derivar_*`/`aplicar_*`.
3. **Nao vira requisito.** Principio zero: filiacao SUGERE, nunca bloqueia --
   quem joga numa mesa de Golarion pode ser da Pathfinder Society, e o
   construtor nao tem como saber. O campo informa; nao entra em `requires`.

## O que esta spec NAO resolve, e declara

- **Os stubs de filiacao e o termo do predicado**, que eram a proposta original
  do item. Sao passo dois, e so fazem sentido depois que houver um consumidor:
  hoje nada no motor pergunta "de que organizacao voce e". A estruturacao ja
  esta viabilizada pela repeticao das formas, e o texto fica no registro
  enquanto isso.
- **As 282 diferencas** entre os 1.010 docs do AoN com `access` e os 728 que
  casam: sao docs sem par na nossa base (kind fora de escopo, conteudo que o
  Foundry nao tem). Nao e perda nossa.

## Como se prova que funciona

1. `acesso` sai preenchido em ~728 registros; hoje sao 0.
2. `wb:feat/acupuncturist` responde `acesso: "Tian Xia origin"`.
3. `wb:class/oracle` NAO ganha o campo -- ele casava so pela prosa, e a prosa
   nao e a fonte aqui.
4. `prov.acesso` diz `aon` em todos.
5. Nenhum campo existente muda de valor.
6. O passo e idempotente e os 10 portoes seguem verdes -- inclusive o portao 1,
   que cobra `prov` de todo campo preenchido.
