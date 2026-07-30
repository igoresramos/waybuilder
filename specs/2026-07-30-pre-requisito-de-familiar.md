---
spec: pre-requisito-de-familiar
project: waybuilder
version: 1
status: aprovada
created: 2026-07-30
todo: 87
---

# Spec -- `a familiar` deixou de ser prosa solta

## O que mudou desde que o item foi escrito

O item 87 declarou, em 29/07: *"`a familiar` (5) -- nao ha paralelo do
`grant_actor` para familiar"*. Isso deixou de ser verdade no dia seguinte: a
spec `familiares-e-eidolons-concedidos` derivou a concessao, e hoje a base tem
**16 registros** com `grant_actor.tipo` de bicho que nao e companheiro animal:

| tipo | registros | exemplo |
|---|---:|---|
| `familiar` | 16 | `wb:class-feature/familiar-witch`, `wb:feat/alchemical-familiar` |
| `eidolon` | 2 | `wb:class-feature/eidolon`, `wb:feat/summoner-dedication` |

O termo `has_actor` ja existe nos dois motores e ja le essas concessoes. O que
faltava era **uma linha no extrator**: `ATOR_RE` so casava
`an? (animal companion|companion)`, entao `a familiar` caia inteiro em
`requires_residuo`.

## O tamanho, medido

**6 clausulas**, em 6 feats: `divine-emissary`, `enhanced-familiar`,
`familiar-sage-dedication`, `familiars-eyes`, `familiars-language`,
`fearsome-familiar`.

Seis ocorrencias e o mesmo numero que ja fez RECUSAR `strike-damage` em 30/07.
A diferenca e o custo, que e o criterio usado nas duas recusas anteriores
(ItemAlteration, RollOption): la faltava um subsistema inteiro de mecanica
condicional; aqui a maquinaria ja esta pronta dos dois lados e o que falta e
ampliar uma expressao regular. Custo por ocorrencia, nao ocorrencia.

## O que esta spec RECUSA, com numero

**Nao vai haver quebra de clausula por virgula.** Ela recuperaria pouco e
estragaria muito:

- `,` cru: 70 clausulas de residuo tem virgula, e a esmagadora maioria e LISTA
  dentro de um conceito unico -- `Angelkin, Lawbringer, Musetouched, or another
  lineage feat`. Quebrar produz fragmentos sem sentido.
- `, and `: 8 clausulas, e so **uma** (`wb:archetype/familiar-sage`) quebraria
  limpo. As outras 7 sao prosa com lista entre parenteses (`including the
  desecration, iniquity, and obedience causes`).
- tag completa seguida de virgula (`{@feat X|Fonte}, <prosa>`): dos **28**
  registros que tem residuo e NENHUM `requires`, exatamente **zero** casam esse
  formato. O ganho seria em registros que ja tem gate de nivel.

E o residuo nao e lixo: ele vai para a TELA como requisito de mesa. Trocar uma
frase legivel por tres fragmentos piora o que o jogador le.

## Como se prova que funciona

1. `wb:feat/fearsome-familiar` responde `requires` com `{"has_actor":
   "familiar"}` e `requires_residuo` vazio.
2. Uma Bruxa de nivel 1 (que ganha `familiar-witch` pela progressao) ATENDE
   `fearsome-familiar`.
3. Um Guerreiro de nivel 1 NAO atende, e o motivo dito e `exige ter familiar`.
4. `an animal companion` continua respondendo `companheiro` -- a extensao nao
   troca o que ja funcionava.
5. Quatro camadas verdes e o diff de fixtures lido.
