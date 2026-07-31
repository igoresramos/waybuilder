---
spec: fonte-divina-escolhida
project: waybuilder
version: 1
status: aprovada
created: 2026-07-30
todo: 98
---

# Spec -- a fonte divina deixa de ser ambigua nas 137

## O que ficou pendente

A spec `divindade-na-ficha` fechou o eixo de divindade e declarou o limite:

> A sub-escolha da fonte NAO vira sub-escolha nesta versao. Para 342 das 479
> divindades a resposta ja esta determinada; para as 137 que permitem as duas,
> o motor **nao reprova** -- ele nao sabe qual o jogador escolheu.

O desenho que faltava chegou com `santificacao-escolhida`: opcao com `requires`
proprio, avaliada por `candidatos()`, marcada e nunca escondida. Esta spec
aplica o mesmo, e o Foundry declara o eixo do mesmo jeito -- `Divine Font` tem
um `ChoiceSet` com duas opcoes, cada uma condicionada a `deity:primary:font:*`.

## A decisao, e o cuidado que ela exige

**Dois termos, nao um.** Usar `deity_font` tanto no `requires` da opcao quanto
na pergunta do feat seria circular: a opcao `heal` exigiria que a fonte ja
fosse `heal`.

| termo | pergunta | quem usa |
|---|---|---|
| `deity_font_permitido` | a DIVINDADE permite esta fonte? | o `requires` das duas opcoes |
| `deity_font` | a fonte do PERSONAGEM e esta? | as 13 clausulas de feat |

`deity_font` passa a olhar a escolha **quando ela existe**. Sem escolha, ele
mantem o comportamento de hoje: responde pela permissao da divindade e nao
reprova quando ela permite as duas. O principio zero continua valendo para
quem ainda nao escolheu.

**So o Clerigo.** O eixo e derivado de quem cita
`wb:class-feature/divine-font`, e so a classe dele cita. O Campeao escolhe
santificacao, nao fonte -- e por isso os dois eixos sao separados.

## O que muda na pratica

Um Clerigo de Aakriti (permite heal e harm) que escolha `harm`:

- `Harming Hands` (exige `harmful font`) ATENDE;
- `Healing Hands` (exige `healing font`) passa a NAO atender, com o motivo
  dizendo que a fonte escolhida foi `harm`.

Antes desta spec os dois atendiam, porque a divindade permitia as duas.

## O que esta spec NAO resolve, e declara

- **`Versatile Font`** existe justamente para ter as duas, e o feat continua em
  `requires_residuo` com `deity that allows clerics to have both fonts`. Ele
  pediria um termo que responde "a divindade permite AS DUAS", que e a
  conjuncao das duas permissoes -- cabe, mas so faz sentido depois que o feat
  passar a CONCEDER a segunda fonte, e concessao de escolha e outra familia.
- **O efeito** (quantos usos de heal/harm por dia, e o slot extra) segue fora:
  e mecanica de recurso, nao de construcao.

## Como se prova que funciona

1. O Clerigo abre o eixo `divine-font` com duas opcoes; o Campeao nao.
2. Com Pharasma (so `heal`): `heal` atende, `harm` aparece MARCADA.
3. Com Aakriti (as duas): as duas atendem.
4. Escolhida `harm` com Aakriti, `Healing Hands` deixa de atender e o motivo
   cita a fonte escolhida.
5. Sem escolha de fonte, o comportamento de hoje nao muda -- e a assercao que
   protege as 342 divindades que ja respondiam certo.
6. Quatro camadas verdes.
