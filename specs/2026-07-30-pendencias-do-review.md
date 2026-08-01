---
spec: pendencias-do-review
req: WB-041
project: waybuilder
version: 1
status: implementada
created: 2026-07-30
todo: 73
---

# Spec -- as duas pendencias menores do review adversarial de 27/07

A parte (a) saiu em `2026-07-30-escolha-de-nivel-futuro.md`. Aqui ficam (b) e
(c), que sao pequenas e independentes uma da outra.

## (b) `em: "criacao"` desligava a checagem em vez de reprova-la

`_higiene_de_slot` so checava o nivel quando `em` era inteiro:

```python
if isinstance(em, int) and em not in niveis:
```

A intencao era dispensar ancestria e background, que de fato nascem na criacao.
O efeito foi outro: um **feat** posto em `"criacao"` por engano passava calado --
a guarda que existia para dispensar o que nao tem nivel dispensava tambem o que
tem nivel e esta errado.

**As cinco cadencias do laco sao todas por nivel** (`class_feat`, `skill_feat`,
`general_feat`, `ancestry_feat`, `free_archetype`); nenhuma delas nasce na
criacao. Entao ali a string nao e dispensa, e erro, e passa a avisar.

O slot `feat_concedido` (spec `slot-de-feat-concedido`), que legitimamente nasce
em `"criacao"` quando quem concede e uma heranca, **nao e cadencia** e nao passa
por este laco -- a correcao nao o alcanca.

## (c) `_subclasse_de` dependia da ordem do documento

`_subclasse_de` devolve a primeira escolha de `subclasse` cujo valor pertenca a
alguma opcao da classe. Mas uma classe tem VARIOS eixos: o Mago tem
`arcane-school`, `arcane-thesis` e `outras-opcoes`. Com dois eixos preenchidos,
o resultado dependia de qual escolha vinha antes no array:

```
ordem [abjuration, experimental-spellshaping] -> wb:arcane-school/abjuration
ordem [experimental-spellshaping, abjuration] -> wb:class-feature/experimental-spellshaping
```

Mesma ficha, mesmas escolhas, resposta diferente. Era a ultima dependencia de
ordem que sobrou depois do conserto de `ordem_de_classe`, e ela alimenta
`_dc_de_conjuracao`.

**A ordem passa a ser a da FONTE**: os eixos sao percorridos na ordem em que a
classe os declara em `subclasses`, e dentro de cada eixo procura-se a escolha.
O documento deixa de ter voto. Nao ha decisao de qual eixo "vale mais" -- ha uma
ordem estavel, que e a que a fonte publica.

## O que esta spec NAO resolve, e declara

- **Qual eixo DEVERIA responder** quando ha mais de um. Hoje o consumidor
  (`_dc_de_conjuracao`) so usa o resultado para texto. Se um dia precisar do
  eixo certo, e o consumidor que tem de pedir o eixo pelo nome, e nao esta
  funcao adivinhar.

## Como se prova que funciona

1. Um `class_feat` com `em: "criacao"` gera aviso; ancestria e background nao.
2. O slot `feat_concedido` nascido em `"criacao"` continua sem aviso.
3. `_subclasse_de` devolve o MESMO valor para os dois arranjos do array.
4. E o valor devolvido e o do primeiro eixo declarado pela classe.
5. Nenhum fixture muda.
6. Quatro camadas verdes.
