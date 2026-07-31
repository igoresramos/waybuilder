---
spec: arquetipo-do-feat
project: waybuilder
version: 1
status: aprovada
created: 2026-07-31
todo: 100
---

# Spec -- feat de arquetipo sem arquetipo

> **Esta spec foi escrita DEPOIS do codigo, e isso e um erro.** O passo
> `derivar_arquetipo_do_feat.py` foi ao ar citando um arquivo que nao existia;
> quem pegou foi o **portao 8** ("artefato citado que sumiu do disco"), e como
> ele falha o build, o passo 9 nao emitiu o payload do app e a paridade
> TS/Python quebrou em seguida. A regra do projeto e spec primeiro, e o portao
> existe justamente porque a regra e violavel.

## O problema

**73** feats tem o trait `archetype` e o campo `archetype` **vazio**. Sem o
campo, o feat nao pertence a arquetipo nenhum: nao entra na lista dele, nao
recebe o gate de `derivar_gate_arquetipo.py` ("so com a dedicacao") e a
medicao do item 46 quase o contou como orfao de outra coisa.

## A ancora esta no proprio `requires`

Feat de arquetipo exige a dedicacao do arquetipo, e a dedicacao carrega o
campo. Entao o dado necessario ja esta na base -- e leitura, nao chute.

| | quantos |
|---|---:|
| feats com trait `archetype` e campo vazio | **73** |
| com UMA dedicacao no `requires` -> re-ancorados | **37** |
| com MAIS DE UMA -> recusados | 12 |
| sem dedicacao no `requires` -> sem ancora | 24 |

**Uma medicao automatizada previu 49 re-ancoraveis.** Sao 37. Os 12 de
diferenca citam DUAS dedicacoes -- `Skill Mastery` aceita Rogue **ou**
Investigator -- e ancorar num dos dois seria escolher. Poe o feat na lista
ERRADA, que e pior que deixa-lo sem lista.

## A segunda metade mudou de natureza ao ser testada

O item 100 falava em "homonimo classe x arquetipo": registros cujo
`requires`/`grants` aponta para o feat de ARQUETIPO tendo o `class-feature` de
mesmo nome ao lado. Sao **12** ocorrencias reais.

**Nao sao defeito de numero.** Testado: um Alquimista 5 responde `True` a
`{"has": "wb:feat/advanced-alchemy"}`, porque `wb:class-feature/alchemy`
**concede** o feat de arquetipo. A cadeia funciona e `efficient-alchemy`
atende corretamente.

O que esta errado e **qual registro chega a ficha**: o do arquetipo (nivel 4,
fonte de arquetipo) em vez do `class-feature` de mesmo nome -- que existe na
base e fica **inalcancavel** (`wb:class-feature/advanced-alchemy` e
`wb:class-feature/quick-alchemy` respondem `False` ao `has`).

E cosmetico de um lado (familia do item 55) e inalcancavel do outro (familia do
item 97).

**E o conserto obvio seria errado.** Trocar o alvo do `grants` para o
`class-feature` QUEBRARIA a cadeia que hoje funciona. O caminho e `equivale_a`
entre o par, como foi feito nos gemeos de instinto -- assim os dois ids
resolvem. Fica registrado, nao feito.

## Cuidado com a contagem: 40 nao eram 40

Uma medicao automatizada contou **40** homonimos porque olhou todo `wb:feat/X`
com `wb:class-feature/X` de mesmo nome, **sem checar se o feat citado era de
arquetipo**. Os dois maiores blocos nao sao: `wb:feat/shield-block` tem trait
`general` (12 citacoes) e `wb:feat/reactive-strike` tem trait de classe (5).

Feat e feature de mesmo nome ali e **RAW correto** -- Shield Block e feat geral
que qualquer um compra E feature que o Guerreiro ganha de graca. E o motor ja os
resolve por alias: um Guerreiro 2 com `wb:class-feature/shield-block` responde
`True` a `{"has": "wb:feat/shield-block"}`.

## Como se prova que funciona

1. 37 feats ganham `archetype`, com `prov` dizendo de onde veio.
2. Nenhum feat com duas dedicacoes no `requires` e ancorado.
3. Os 24 sem dedicacao continuam sem o campo.
4. O relatorio lista as 12 ocorrencias reais de homonimo, e nao 40.
5. Quatro camadas verdes.
