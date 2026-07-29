---
spec: pericias-livres
project: waybuilder
version: 1
status: aprovada
created: 2026-07-29
todo: 92
---

# Spec -- as pericias livres, que o motor conta e ninguem gasta

## O problema

Achado ao alinhar a bancada de comparacao com o Pathbuilder (item 90): o
personagem-base do Waybuilder sai com **nenhuma pericia treinada por escolha**,
enquanto o do Pathbuilder tem Acrobatics, Athletics, Stealth e Thievery.

A causa nao e a bancada. E que **o motor nao tem onde receber a escolha**.

`_orcamento_de_pericia` (motor.py:503) calcula quantas pericias livres o
personagem tem direito -- e o numero aparece na ficha como
`pericias_livres: 3` -- mas **nada no motor le uma escolha de pericia**. Os
unicos slots de escolha que o motor consome sao quatro:

```
_escolhas("boosts_livres")   _escolhas("nivel_de_classe")
_escolhas("skill_increase")  _escolhas("subclasse")
```

Nao ha `_escolhas("pericias_livres")`. O orcamento e calculado e **nunca gasto**.

Medido nas 27 classes -- todas dao de 2 a 7 pericias livres, nenhuma gastavel:

| classe | livres | classe | livres |
|---|---:|---|---:|
| Rogue | 7 | Fighter, Alchemist, Barbarian, Guardian | 3 |
| Bard, Investigator, Monk, Ranger, Swashbuckler | 4 | Cleric, Champion, Druid, Wizard, Magus, Sorcerer, Animist, Commander | 2 |

Para um construtor de personagem isso nao e detalhe: escolher as pericias
treinadas e uma das primeiras coisas que o jogador faz na mesa. Hoje a ficha
mostra "3" e o jogador nao tem onde por.

Efeito colateral medido: **18 pontos de divergencia** com o Pathbuilder na
familia de pericia (`exige survival >= trained; tem untrained`) sao, em parte,
isto -- e nao defeito de predicado.

## A decisao

**Slot novo `pericias_livres`**, no mesmo formato de `boosts_livres`, que ja e
lista:

```json
{"em": "criacao", "slot": "pericias_livres",
 "pega": ["acrobatics", "athletics", "stealth", "thievery"]}
```

Tres partes, espelhando o que `boosts_livres` ja faz:

1. **Aplicar** -- cada pericia escolhida entra como `trained`, com origem
   "escolha do jogador", pela mesma funcao `aplicar` que ja trata treino de
   classe e de background. Rank melhor ja existente vence (regra 4), entao
   escolher uma pericia que a classe ja deu nao rebaixa nada.
2. **Higiene** -- confrontar DIREITO com DECLARADO e avisar, exatamente como
   `_orcamento_de_boost` faz desde hoje: *"pericias livres: 2 declarada(s) de 3
   a que o personagem tem direito -- falta 1"*. Declarar a MAIS tambem avisa.
3. **Slot aberto** -- `slots_abertos()` passa a listar `pericias_livres` com
   quantas faltam, para a tela ter onde renderizar o picker.

### Escolher o que ja se tem: avisa, nao reprova

Se o jogador declara `athletics` num Barbaro -- que ja recebe Athletics
automatica pela regra 9 --, o motor **aplica e avisa** que a escolha foi
desperdicada. Nao reprova: o principio zero vale tambem para a escolha do
jogador, e reprovar aqui seria arbitrar uma regra de mesa (na mesa, o mestre
manda escolher outra).

## O que esta spec NAO resolve, e declara

**O modificador de INT nao entra no orcamento.** Em RAW o personagem recebe
`livres + mod(INT)` pericias treinadas. O motor nao soma isso hoje, e esta spec
nao muda: `_proficiencias()` roda **antes** de `_atributos()` na derivacao
(motor.py:191-192), entao o INT ainda nao existe quando o orcamento e calculado.
Somar exigiria reordenar a derivacao, que e mudanca de risco maior que o ganho e
merece medicao propria.

Consequencia declarada: um personagem de INT alto tera direito a mais pericias
do que o motor oferece, e a higiene vai cobrar menos do que deveria. Fica
registrado como item proprio.

## Como se prova que funciona

1. Um Guerreiro 2 que declara `["acrobatics", "athletics", "stealth"]` sai com as
   tres `trained`.
2. O mesmo Guerreiro **sem** declarar nada avisa que faltam 3.
3. Declarando 4 num orcamento de 3, avisa que sobrou 1.
4. Um Barbaro que declara `athletics` -- ja automatica pela classe -- avisa
   desperdicio, e a pericia continua `trained` (nao rebaixa).
5. `slots_abertos()` lista `pericias_livres` com o que falta, e para de listar
   quando o orcamento e cumprido.
6. As 22 fichas derivam identicas nas duas linguagens.
7. A bancada de comparacao passa a espelhar o Pathbuilder, e a familia de
   pericia encolhe.

## A armadilha do porte

Nao e termo de predicado, entao nao ha linha de `switch`. Mas o slot novo mexe
em TRES lugares nos dois motores: aplicar em `_proficiencias`, avisar na higiene,
e listar em `slots_abertos`. Esquecer o terceiro nao quebra teste nenhum -- so
faz a tela nunca oferecer o picker.
