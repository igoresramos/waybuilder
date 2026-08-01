---
spec: int-no-orcamento-de-pericia
req: WB-040
project: waybuilder
version: 1
status: implementada
created: 2026-07-30
altera: [WB-001]
todo: 92
---

# Spec -- o Mago de INT 18 tem direito a 6 pericias e o motor oferece 2

## O problema

A fonte e literal, e aparece na prosa de cada classe:

> "Trained in a number of additional skills equal to **3 plus your Intelligence
> modifier**"

O motor soma so o numero da classe (2 a 7, medido nas 27) e **ignora o INT**. Um
Mago de INT 18 deveria treinar 2 + 4 = 6 pericias e recebe 2. O personagem tem
direito a mais do que a tela oferece, e a higiene de slot cobra menos do que
deveria.

## A causa: ordem de derivacao

`_derivar` chama `_proficiencias()` **antes** de `_atributos()`
(motor.py:191-192). Quando `_orcamento_de_pericia` faz a conta, `self.atributos`
ainda esta vazio -- nao ha INT para somar.

Nao e caso de borda nem de dado faltando: e a ordem.

## A medicao que o proprio item pediu

O item dizia que o conserto "exige reordenar a derivacao, que e mudanca de risco
e merece medicao propria: conferir que nada em `_proficiencias` alimenta
`_atributos`". Conferido, nos dois sentidos:

| funcao | le | produz |
|---|---|---|
| `_atributos` | `ancestria`, `background`, `base`, `nivel`, `ordem_de_classe`, `primeira_classe`, `boosts*`, `origem_boost` | `atributos`, `modificadores` |
| `_orcamento_de_boost` | `nivel`, `boosts_*` | -- |
| `_proficiencias` | `background`, `base`, `features`, `ordem_de_classe`, feats efetivos | `proficiencias`, `origem_proficiencia`, `pericias_automaticas`, `pericias_livres` |

**Nenhuma das entradas de `_atributos` vem de `_proficiencias`**, e
`_proficiencias` nao le `atributos` nem `modificadores`. As duas dependem
apenas dos passos 1 a 4 (`_niveis_de_classe`, `_ancestria_e_background`,
`_features_de_classe`, `_grants_em_cadeia`), que continuam antes das duas.

Entao trocar a ordem e seguro, e nao ha ciclo a desatar.

## As decisoes

1. `_atributos()` passa a rodar **antes** de `_proficiencias()`.
2. `_orcamento_de_pericia` soma `modificadores["int"]` ao numero da classe.
3. **O modificador negativo REDUZ**, porque a prosa diz "plus your Intelligence
   modifier" sem piso. O que tem piso e o total, em zero: nao existe treinar um
   numero negativo de pericias. Isso e aritmetica, nao regra inventada.
4. O INT entra **uma vez por personagem**, e nao uma vez por classe. O orcamento
   por classe existe para multiclasse (regra 15), mas o modificador e do
   personagem: soma-lo em cada classe daria a um Mago 3/Ladino 3 o dobro do INT.
   Ele entra na PRIMEIRA classe, que e a que concede as pericias iniciais.

## O que esta spec NAO resolve, e declara

- **INT que muda depois da criacao** (boost de nivel 5, 10, 15, 20). Em RAW o
  numero de pericias treinadas nao aumenta retroativamente quando o INT sobe:
  a linha e das "starting skills". O motor usa o INT ATUAL, que e o unico que
  ele tem; declarado aqui como divergencia conhecida do RAW, e nao como
  descuido. Corrigir exigiria guardar o INT no momento da criacao, que e
  modelo novo.
- **Item que da INT** (`Headband of Intellect`). Cai na mesma frase acima.

## Como se prova que funciona

1. Mago de INT 18 tem orcamento 6, e nao 2.
2. Mago de INT 10 continua com 2 -- modificador zero nao muda nada.
3. Personagem de INT 8 tem orcamento reduzido em 1, e nunca negativo.
4. Mago 3 / Ladino 3 soma o INT **uma vez**, nao duas.
5. `pericias_livres_detalhe` mostra de onde veio cada parcela.
6. Nenhuma proficiencia ja escolhida se perde -- o orcamento sobe, e o `delta`
   e quem muda.
7. Quatro camadas verdes e os 10 portoes.
