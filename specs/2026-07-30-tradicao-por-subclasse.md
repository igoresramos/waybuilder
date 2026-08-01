---
spec: tradicao-por-subclasse
req: WB-053
project: waybuilder
version: 1
status: implementada
created: 2026-07-30
altera: [WB-002]
todo: 78
---

# Spec -- a tradicao de conjuracao vem da subclasse, e nunca chegava na ficha

## O problema

Tres classes nao tem tradicao fixa: quem a define e a subclasse escolhida.

| classe | eixo | `spellcasting.tradition` na base |
|---|---|---|
| Sorcerer | bloodline | `"variavel (definida pela escolha de bloodline; nao ha tradicao fixa na class-feature)"` |
| Witch | patron | `"variavel (definida pela escolha de patron; ...)"` |
| Summoner | eidolon | `"variavel (definida pela escolha de eidolon; ...)"` |

Essa string de prosa vai crua para a ficha. `motor.py:1036` faz
`"tradicao": sc.get("tradition")` e pronto -- a tradicao NUNCA e resolvida na
rota nativa. Consequencia: o campo que filtra **quais magias o personagem pode
aprender** sai como uma frase em portugues. DC e slots continuam certos; o
defeito e isolado a este campo, e e o campo que mais importa para escolher magia.

O resolvedor `_tradicao_por_escolha` **ja existe** (motor.py:1104) e ja le
exatamente o campo certo (`escolhido.get("tradition")`), mas so esta ligado em
`_conjuracao_de_arquetipo`, na rota de dedicacao.

## As duas medicoes que definem o desenho

### 1. A fonte tem o dado ESTRUTURADO -- nao e parse de prosa

O dump do AoN traz `tradition` como campo, nao como texto:

| dump | registros | com `tradition` |
|---|---:|---:|
| `bloodline.json` | 28 | 27 |
| `patron.json` | 27 | 27 |
| `eidolon.json` | 13 | 13 |
| `draconic-exemplar.json` | 44 | 44 |
| `mystery.json` | 22 | **0** |

`mystery` com zero nao e lacuna: o Oraculo tem tradicao FIXA (`divine`) na
propria classe, e mystery so varia tema. Confirma que o item 78 acerta ao citar
tres eixos e nao quatro.

### 2. O registro que o jogador PEGA nao e o que tem a tradicao

Este e o achado que muda tudo. A opcao viva no eixo de subclasse e a
`class-feature`, nao o registro do kind dedicado:

```
wb:class/sorcerer -> subclasses[].opcoes = ["wb:class-feature/bloodline-genie", ...]
                                            19 opcoes, 19 do kind class-feature
```

E a `class-feature` **nao tem a tradicao nem tem como chegar nela**:
`wb:class-feature/bloodline-genie` sai com `xref.aon: None`, e o dump
`aon_class_features.json` (1.254 registros) tem `tradition` em **zero** deles.
O dado so existe do lado `wb:bloodline/*`, que e um catalogo paralelo que
ninguem escolhe.

Ou seja: emitir `tradition` em `wb:bloodline/*` resolveria nada sozinho. E
preciso LEVAR o campo para o irmao vivo.

A ponte, medida com trava pela classe dona:

| eixo | classe | casam | ambiguo | sem par |
|---|---|---:|---:|---:|
| bloodline | Sorcerer | 18 | 0 | 0 |
| patron | Witch | 17 | 0 | 0 |
| eidolon | Summoner | 13 | 0 | 0 |

A trava por classe nao e enfeite: `psychopomp` existe como bloodline E como
eidolon. Sem ela, `wb:eidolon/psychopomp` casaria com a class-feature do
Feiticeiro.

### 3. Draconic e o unico que nao resolve, e a fonte concorda

Casando por NOME eu media 18/18 com tradicao -- e estava errado. `Draconic`
existe duas vezes no dump: a legada (`bloodline-5`, `Arcane`) e a remaster
(`bloodline-23`, `tradition: None`). A base carrega a REMASTER. Casar por nome
atribuia a tradicao da versao aposentada a versao vigente -- exatamente o tipo
de numero errado que esta spec existe para evitar.

Casando por `xref.aon`, que e a chave de identidade de verdade: **47 de 48
resolvem**, e o unico que fica e `wb:bloodline/draconic`, porque no remaster a
tradicao dele depende de uma SEGUNDA escolha, o `draconic-exemplar` (44
registros na base, todos com tradicao no dump).

## A decisao

1. **`aon_kinds.py` emite `tradition`** para os kinds cujo dump tem o campo --
   `bloodline`, `patron`, `eidolon` e `draconic-exemplar` --, em caixa baixa,
   lido do proprio documento que originou o registro (nao por nome). Registro
   sem o campo na fonte nao ganha a chave: ausencia e ausencia.

2. **Passo novo `derivar_tradicao_de_subclasse.py`** leva `tradition` do
   registro do kind dedicado para a `class-feature` irma, casando por nome
   normalizado **dentro da classe dona**. Roda depois de
   `colapsar_opcoes_irmas.py` (7d), que e quem ja resolve a duplicidade de
   identidade entre os dois lados. Nao apaga o lado de origem: os dois passam a
   responder a mesma coisa.

3. **`_conjuracao()` chama `_tradicao_por_escolha`** quando
   `sc["tradition"]` nao e uma das quatro palavras. Quando e, nada muda -- o
   Oraculo continua `divine` sem consultar escolha nenhuma.

4. **`_tradicao_por_escolha` passa a filtrar por CLASSE.** Hoje ela varre TODA
   escolha de slot `subclasse` e devolve a primeira com tradicao, ignorando o
   `eixo` que ela mesma le. Num Feiticeiro 5 / Bruxa 3 isso entrega a tradicao
   do bloodline para as duas linhas de conjuracao. O filtro e o campo `class`
   da class-feature escolhida.

Nos dois motores, Python e TypeScript. Nao ha linha de `switch` a acrescentar:
isto e resolucao nativa em `_conjuracao`, nao termo de predicado.

## O que esta spec NAO resolve, e declara

- **Draconic continua sem tradicao.** O `draconic-exemplar` existe na base (44
  registros) mas **nao esta ligado como eixo de escolha em classe nenhuma** --
  nenhuma `subclasses[].opcoes` o cita. Enquanto o jogador nao puder escolher o
  exemplar, nao ha de onde tirar a resposta. O motor AVISA e devolve `None`, que
  e o principio zero: nao arbitrar tradicao errada em silencio. Emitir
  `tradition` no kind ja fica feito, entao ligar o eixo depois e uma linha.
- **O eixo do Feiticeiro se chama `outras-opcoes`.** As 19 bloodlines vivem no
  balaio do item 69. Esta spec funciona assim mesmo, porque filtra pela CLASSE
  da opcao escolhida e nao pelo nome do eixo -- mas o item 69 continua aberto.
- **Sub-escolha de segundo nivel em geral.** Draconic e o unico caso hoje.

## Como se prova que funciona

1. `wb:bloodline/genie` responde `tradition: "arcane"`; `wb:patron/baba-yaga`,
   `occult`; `wb:eidolon/angel`, `divine`.
2. A class-feature irma responde o mesmo: `wb:class-feature/bloodline-genie`
   com `arcane`, e sao 47 registros no total.
3. Um Feiticeiro 5 com `wb:class-feature/bloodline-genie` escolhido sai com
   `conjuracao[0]["tradicao"] == "arcane"` -- hoje sai a frase em portugues.
4. Uma Bruxa 5 com patron Baba Yaga sai com `occult`.
5. Um Feiticeiro 5 / Bruxa 3 com as DUAS subclasses escolhidas sai com duas
   linhas de conjuracao, cada uma com a SUA tradicao -- e o teste que so passa
   com o filtro por classe.
6. Um Feiticeiro de bloodline Draconic sai com `tradicao: None` e um aviso
   dizendo por que; nao sai `arcane`.
7. Um Oraculo continua `divine` sem depender de escolha.
8. Paridade: as mesmas sete afirmacoes valem no porte TypeScript.
9. Os 10 portoes, o oraculo Python, os 113 testes do TS e a verificacao de
   navegador seguem verdes; fixtures regenerados e o diff LIDO.
