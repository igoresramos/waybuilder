---
spec: avatar-do-personagem
project: waybuilder
status: mudou-de-repo
created: 2026-08-01
movida_em: 2026-08-01
---

# Spec -- o avatar do personagem (ponteiro)

**A spec canonica vive em
[`igoresramos/waybuilder-avatar`](https://github.com/igoresramos/waybuilder-avatar/blob/main/specs/2026-08-01-avatar-do-personagem.md),
em `@3`.** Este arquivo e so um ponteiro: nao editar o conteudo aqui, para nao
criar duas fontes de verdade que divergem.

## Por que a spec saiu daqui

O acervo de sprites -- build, fontes, atlas, catalogo, creditos -- foi extraido
para repo proprio por subtree split, com o commit de origem preservado. A spec
foi junto porque o unico passo ja implementado (o passo de build) mora la.

## O que ainda compete a ESTE repo

A separacao vale para o acervo, nao para a interface. Da ordem de 7 passos da
spec, seguem aqui:

| passo | o que e |
|---|---|
| 2 | renderer, como modulo puro testavel sem UI |
| 3 | rota de dev com a grade e as setinhas |
| 4 | campo no documento e migracao de esquema `@2 -> @3` |
| 5 | promocao a modal |
| 6 | tela de creditos |
| 7 | sugestao por ancestralidade e equipamento (opcional) |

A decisao 10 da spec continua de pe no ponto que importa: **a tela mora junto do
app**. Prototipo de interface em projeto separado e modo de perda conhecido
nesta casa.

## Pendencia que este repo herda

Como o acervo saiu, o build da Vercel daqui nao enxerga mais `saida/`. Isso
**nao quebra nada hoje** -- nao ha import nem linha no `vercel.json` que o
consuma. A ponte (submodule, pacote npm ou fetch no build) se decide junto do
passo 2, e esta registrada no item 2 de "Aberto" da spec canonica.
