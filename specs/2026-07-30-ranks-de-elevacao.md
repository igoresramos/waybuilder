---
spec: ranks-de-elevacao
project: waybuilder
version: 1
status: aprovada
created: 2026-07-30
todo: 79
---

# Spec -- em que ranks a magia cabe, e a diferenca entre "nao eleva" e "nao sei"

## O problema, na forma do item

O item 79(d) diz: "`heightened` estruturado cobre 31% dos spells e 42% nao tem
nem dado nem a flag `heightened_so_prosa`, entao **nao da para separar 'sem
elevacao' de 'lacuna'**".

A queixa esta certa e e a parte importante: uma chave vazia que significa duas
coisas diferentes nao informa nada.

## A medicao responde a pergunta

O AoN publica `heighten_level` em **todos os 2.461** docs de magia -- a lista de
ranks que a magia ocupa. Cruzando com a base:

| situacao | magias |
|---|---:|
| o AoN diz que **NAO eleva** (`heighten_level` com um rank so) | **664** |
| o AoN diz que eleva, e nos ja temos estruturado | **511** |
| o AoN diz que eleva, e nos **nao temos** | **461** |
| nos temos, e o AoN diz que nao eleva | 2 |

Ou seja: das 1.125 chaves vazias, **664 estao certas** -- a magia realmente nao
eleva -- e **461 sao lacuna de verdade**. A ambiguidade que o item aponta
desaparece assim que o campo do AoN e lido.

E o padrao se repete pela quarta vez hoje: o item tratava como lacuna de FONTE
o que era lacuna de LEITURA.

## As decisoes

1. **`ranks` passa a existir**, lido de `heighten_level`, verbatim: a lista de
   ranks em que a magia pode ser preparada ou lancada. E o que um construtor
   precisa para dizer "esta magia cabe neste slot".
2. **A ausencia deixa de ser ambigua.** Com `ranks` presente, `len(ranks) == 1`
   diz "so no rank proprio" e `len(ranks) > 1` diz "eleva". Nao e preciso
   inventar flag: a lista responde as duas perguntas.
3. **`heightened` (o QUE muda a cada degrau) continua como esta.** O AoN publica
   os degraus (`heighten`: `["+2"]`, `["3rd","5th"]`) mas **nao publica o efeito
   de cada degrau** -- o `efeito` dos nossos 511 vem do Foundry. Preencher os
   461 com degrau sem efeito trocaria uma lacuna honesta por um campo
   meio-cheio, e o campo ja tem consumidor. Fica declarado.

## O que esta spec NAO resolve, e declara

- **Os 461 sem `heightened` estruturado.** Eles ganham `ranks` (onde cabem) e
  seguem sem `efeito` (o que muda). Sao coisas diferentes, e so a segunda
  depende de fonte que nao temos por magia.
- **As 2 magias em que nos temos estrutura e o AoN diz que nao eleva.** Sao
  poucas e podem ser par legacy/remaster mal casado; ficam contadas no
  relatorio para revisao, e o dado NAO e apagado -- apagar estrutura por
  divergencia de uma fonte seria pior que a divergencia.
- **Ritual.** Nao tem elevacao no PF2e.

## Como se prova que funciona

1. `ranks` sai preenchido em ~1.636 magias (todas as que casam com o AoN).
2. `wb:spell/acid-arrow` responde `ranks: [2, 4, 6, 8, 10]`.
3. Uma magia que nao eleva responde `ranks` com um unico rank, e nao lista
   vazia -- vazia voltaria a ser ambigua.
4. As 461 lacunas ficam identificaveis: tem `ranks` com mais de um valor e
   `heightened` vazio.
5. `prov.ranks` diz `aon`.
6. Nenhum campo existente muda de valor, e os 10 portoes seguem verdes.
