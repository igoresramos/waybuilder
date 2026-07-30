---
spec: segundo-ator
project: waybuilder
version: 1
status: aprovada
created: 2026-07-30
todo: 47
---

# Spec -- dois companheiros na mesma ficha: quando o livro deixa

## A pergunta que estava aberta

O item 47(c) estava marcado como **decisao do Igor**:

> a regra 23 (exclusao mutua) deve bloquear qualquer arquetipo que duplique
> concessao ja dada por nivel de classe -- ex: Beastmaster Dedication num Ranger
> que ja tem companheiro?

Nao e decisao. **A fonte responde**, e responde contra o bloqueio:

> Beastmaster Dedication: "You gain the service of a young animal companion...
> **Contrary to the usual rules for animal companions, this feat can grant you a
> second animal companion.** If you ever have more than one animal companion,
> you gain the Call Companion action."

Bloquear o Beastmaster num Ranger seria reprovar o que o livro autoriza por
escrito, e no paragrafo que existe exatamente para isso.

## O que a medicao mostrou

Dos **30 registros que concedem ator**, **6 trazem a excecao na prosa**:

| registro | tipo | frase |
|---|---|---|
| Beastmaster Dedication | companheiro | "second animal companion" |
| Mammoth Lord Dedication | companheiro | "second animal companion" |
| Drake Rider Dedication | companheiro | "another animal companion" |
| Faithful Steed | companheiro | "another animal companion" |
| Emissary Familiar | familiar | "additional familiar" |
| Familiar (Witch) | familiar | "additional familiar" |

Os outros 24 caem na regra geral, que tambem esta na fonte -- a pagina
`Familiars` do AoN: *"You can have only one familiar at a time."*

## As decisoes

1. **A marca sai da PROSA, nao de lista escrita a mao.** `grant_actor` ganha
   `adicional: true` quando o texto do proprio registro declara a excecao. Lista
   a mao ja errou tres vezes neste projeto.
2. **A rota da progressao tambem le a prosa.** `Familiar (Witch)` entra na base
   pelo caminho estruturado (`class.progressao`), que nao passava por regex --
   mas o texto dele diz "additional familiar" e a marca tem de sair de la
   tambem, senao o mesmo dado responde diferente conforme a rota.
3. **AVISO, e nao bloqueio.** Ter dois companheiros sem nenhuma fonte
   `adicional` vira um aviso nomeado, com as origens. Bloquear apagaria uma
   escolha ja feita pelo jogador, e o projeto nao esconde nem remove: marca. E a
   mesma postura de `fora_do_requisito`, que mostra o que nao atende em vez de
   sumir com ele.

## O que esta spec NAO resolve, e declara

- **A parte (a) do item 47** (teto de invocacao em slot de dedicacao de
  arquetipo) segue com o default adotado no plano de 2026-07-29: sim, vale.
  Continua reversivel num `if`.
- **A acao `Call Companion`**, que o Beastmaster concede junto. E acao de mesa,
  nao numero de ficha.
- **Contar quantos atores o livro permite no total.** O aviso diz "ha mais de um
  e nenhuma fonte autoriza"; nao tenta calcular um teto.

## Como se prova que funciona

1. `Beastmaster Dedication`, `Mammoth Lord`, `Drake Rider`, `Faithful Steed`,
   `Emissary Familiar` e `Familiar (Witch)` respondem `adicional: true` -- os
   seis, incluindo o que vem pela progressao.
2. Os outros 24 concessores NAO respondem.
3. Um Ranger com companheiro de classe que pega Beastmaster fica com dois
   companheiros e **sem aviso**.
4. Uma ficha com dois companheiros em que nenhuma fonte e `adicional` ganha um
   aviso que nomeia as duas origens.
5. Nenhuma ficha e bloqueada, e nenhum numero muda.
6. Quatro camadas verdes e os 10 portoes.
