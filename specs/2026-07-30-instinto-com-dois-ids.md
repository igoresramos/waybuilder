---
spec: instinto-com-dois-ids
project: waybuilder
version: 1
status: aprovada
created: 2026-07-30
todo: 42
---

# Spec -- o Barbaro escolhe o instinto e nenhum feat de instinto libera

## O problema

Um Barbaro 3 que escolhe `Animal` no eixo `instinct` continua sem poder pegar
**nenhum dos 25 feats que exigem instinto**. O motivo que o motor da e:

```
exige a sub-escolha Animal Instinct; tem Animal
```

Ele esta comparando duas coisas que sao a mesma.

## A causa

O instinto existe DUAS vezes na base, por dois caminhos que nunca se falaram --
a mesma causa do Campeao que originou `colapsar_opcoes_irmas.py`:

| id | nome | vem de | onde aparece |
|---|---|---|---|
| `wb:instinct/animal` | Animal | AoN (`instinct-8`) | eixo `instinct` |
| `wb:class-feature/animal-instinct` | Animal Instinct | Foundry | eixo `outras-opcoes` |

Os `requires` dos 25 feats citam o segundo. A tela oferece o primeiro. Os xrefs
sao disjuntos -- um so tem `aon`, o outro so tem `foundry` --, entao nao ha
chave comum, e os NOMES diferem pelo sufixo do eixo.

`colapsar_opcoes_irmas.py` nao os alcanca por dois motivos: ele casa por nome
IGUAL e olha uma opcao contra as outras do MESMO eixo.

## O tamanho, medido

Aplicando a regra "`<X>` e `<X> <eixo>` na mesma classe" em toda a base: **9
pares, todos no eixo `instinct` do Barbaro** -- animal, decay, dragon,
elemental, fury, giant, ligneous, spirit e superstition. A regra nao transborda
para nenhuma outra classe, o que era o risco.

## A decisao

**Declarar a equivalencia na base, e nao reformar os eixos.** Um passo emite
`equivale_a` nos dois registros do par, e `_termo_subclass` aceita o par.

Colapsar como o Campeao exigiria mover a opcao vencedora de um eixo para outro
-- os gemeos vivem em eixos DIFERENTES (`instinct` e `outras-opcoes`) --, e
reformar eixo e mais risco do que o defeito pede. `equivale_a` e explicito,
reversivel e cabe num campo.

`_termo_subclass` compara id cru hoje. O `_termo_has`, logo acima dele no mesmo
arquivo, ja resolve alias com um comentario descrevendo exatamente este tipo de
falha ("o motor comparava id cru e por isso 24 `requires` nunca eram
satisfeitos"). A licao existia e nao tinha sido aplicada aqui.

## O que esta spec NAO resolve, e declara

- **A duplicata na TELA.** O eixo `outras-opcoes` continua oferecendo os nove
  `class-feature`, e o eixo `instinct` os nove `instinct`. Escolher qualquer um
  agora satisfaz o requisito, mas a tela mostra os dois. Limpar o balaio
  `outras-opcoes` e o item 69, que tem medicao propria.
- **Os efeitos do instinto** (dano de rage e afins), que sao o item 42 e
  continuam sendo mecanica condicional.

## Como se prova que funciona

1. `wb:instinct/animal` responde `equivale_a: "wb:class-feature/animal-instinct"`
   e vice-versa.
2. Um Barbaro que escolhe `wb:instinct/animal` ATENDE um feat que exige
   `wb:class-feature/animal-instinct`.
3. E o inverso tambem: quem escolhe o `class-feature` atende requisito que cite
   o `instinct`.
4. Um Barbaro que escolheu `Giant` NAO atende feat que exige `Animal Instinct`
   -- a equivalencia e por par, nao um curinga.
5. Sao 9 pares e nenhum fora do eixo `instinct`.
6. Quatro camadas verdes.
