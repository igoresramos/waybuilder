---
spec: escolha-multipla-e-ikons
req: WB-035
project: waybuilder
version: 1
status: implementada
created: 2026-07-30
altera: [WB-002]
todo: 97
---

# Spec -- "Select three ikons", e o eixo que so sabia escolher uma

## O problema, e ele e maior do que o item 97 dizia

O item falava em "48 class-features inalcancaveis". Re-medido: os kinds `ikon`
(21 registros) e `mythic-calling` (15) sao **inteiros** inalcancaveis, com par
em class-feature ou sem. Fundir os pares nao resolveria nada -- tiraria a
duplicidade e os dois lados continuariam sem ser citados em lugar nenhum.

A causa esta na classe. O Exemplar concede `divine-spark-and-ikons` no nivel 1,
e a prosa oficial e literal:

> Select three ikons.

E a classe **nao tem eixo de ikon**. Os tres eixos que ela tem sao os epithets
(nivel 3, 7 e 15), que ja funcionam. Nao ha lacuna de conteudo: o AoN publica
exatamente 21 ikons e a base tem os 21.

## O bloqueio real: `escolhe: N`

O campo `escolhe` existe no schema desde sempre e **os 52 blocos da base usam
`1`**. O motor nem le o campo: ele faz

```python
escolha = next((o for o in bloco["opcoes"] if o in escolhidas), None)
```

-- uma escolha por bloco, e ponto. Um bloco de tres ikons devolveria o primeiro
e perderia os outros dois em silencio, que e o pior desfecho possivel.

## As decisoes

1. **O motor passa a ler `escolhe`.** `slots_de_subclasse` ganha `escolhe` e
   `escolhidos` (lista). `escolhido` continua existindo, valendo o primeiro --
   os 52 blocos de `escolhe: 1` nao mudam de comportamento, e nada que ja
   consumia o campo precisa saber que o mundo mudou.
2. **`_termo_subclass` passa a olhar a LISTA.** Hoje ele compara com uma
   escolha so. Com N escolhas, um requisito que cite qualquer uma delas tem de
   ser atendido. Esse metodo ja produziu uma regressao pega pela paridade em
   30/07, entao a mudanca e minima e vem com assercao propria.
3. **Escolha demais VIRA AVISO, nao correcao.** Se a ficha tiver quatro ikons
   num eixo de tres, o motor nao apaga nada: ele diz. Apagar escolha do jogador
   e o oposto do que este projeto faz -- ver a licao de `Base.opcional` e alias.
4. **O eixo oferece o lado `wb:ikon/*`**, e o gemeo `class-feature` ganha
   `equivale_a` nos dois sentidos. Mesmo tratamento do instinto do Barbaro
   (spec `instinto-com-dois-ids`): dois ids para o mesmo conceito, ligados em
   vez de fundidos.
5. **Tres, e so tres.** A prosa diz tres no nivel 1 e a progressao do Exemplar
   nao tem outra linha de ikon. `wb:feat/additional-ikon` concede um quarto,
   mas isso e slot aberto POR FEAT -- a mesma familia do `feat_concedido` e do
   `grant_actor` -- e nao entra aqui.

## O que esta spec NAO resolve, e declara

- **`wb:feat/additional-ikon`** (o quarto ikon). A maquinaria de "feat abre
  slot" ja existe; o que falta e o feat declarar isso, e nenhum campo da fonte
  diz. Fica medido e por fazer.
- **`mythic-calling` (15 registros)** continua inalcancavel. Ele pertence as
  regras miticas, que a ficha nao modela -- ausencia declarada, nao esquecida.
- **Os 22 sem gemeo** do item 97: 6 gates do Kineticist, `elemental-school`,
  `advanced-vials-toxicologist` (gap de progressao de verdade), 7
  `deviant-classification` (tem primo por NOME, nao por slug) e 4 stubs
  genericos. Cada um pede curadoria propria.
- **Os ikons nao concedem mecanica.** `grants` esta vazio nos 21, dos dois
  lados do par. A escolha passa a EXISTIR e a aparecer na ficha; o efeito de
  immanence/transcendence e prosa, como o principio zero manda.

## Como se prova que funciona

1. Um Exemplar 1 acusa `falta escolher ikon (3 de 3)` e `slots_abertos()` traz
   o slot com `escolhe: 3`.
2. Escolhido UM ikon, o aviso passa a `2 de 3` e o slot continua aberto com
   `escolhe: 2`.
3. Escolhidos os tres, o slot fecha e as tres features entram em `features`.
4. Um quarto ikon vira AVISO e nenhuma escolha e descartada.
5. Os 52 blocos de `escolhe: 1` nao mudam: zero diff de fixture fora do
   Exemplar.
6. `wb:ikon/gleaming-blade` e `wb:class-feature/gleaming-blade` respondem
   `equivale_a` um ao outro.
7. Quatro camadas verdes, e a tela deixa escolher os tres.
