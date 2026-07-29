---
spec: termos-de-predicado
project: waybuilder
version: 1
status: aprovada
created: 2026-07-29
todo: 87
---

# Spec -- termos novos de predicado

## O problema

Depois do parse parcial (`2026-07-29-requisito-parcial.md`), 593 registros
carregam `requires_residuo` -- 644 clausulas, 454 distintas. Parte e narrativa e
**tem de ficar assim** pelo principio zero. A outra parte e mecanica e so nao
era respondida porque faltava termo no schema de predicado.

Medido em 2026-07-29, top do residuo:

| clausula | ocorrencias | tem dado na base? |
|---|---:|---|
| `focus pool` | 10 | **sim** -- o motor ja calcula `focus_pool` |
| `low-light vision` | 8 | **sim** -- `grants.sense`, 81 registros |
| `evil alignment` | 7 | **nao, e nao vai ter** -- ver abaixo |
| `ability to cast focus spells` | 6 | **sim** -- mesmo `focus_pool` |
| `an animal companion` | 5 | **sim** -- `grant_actor`, desde 2026-07-29 |
| `a familiar` | 5 | **nao** -- nao ha paralelo do `grant_actor` |
| `tenets of good` / `of evil` | 4 + 4 | **nao, e nao vai ter** |
| `healing font` / `harmful font` | 4 + 3 | parcial -- `divine_font` existe em `deity`, mas diz o que a DIVINDADE permite, nao o que o personagem escolheu |
| `member of the Gray Gardeners` e afins | 10 + 5 + 3 | narrativo, fica |

## A decisao

**Tres termos novos, e so onde a base ja responde.** Termo que precisaria de
dado inventado nao entra -- ele viraria uma resposta errada com cara de certa,
que e pior que a clausula visivel em `requires_residuo`.

### 1. `sense`

```json
{"sense": "low-light vision"}
```

O personagem enxerga assim? A fonte e `grants.sense`, que existia em **81
registros e ninguem lia** -- mesmo padrao do companheiro: o dado estava la, o
consumidor nao.

O campo tem **tres formas** na base, e o termo aceita as tres:

| forma | onde | exemplo |
|---|---|---|
| dict | maioria | `{"tipo": "darkvision", "acuidade": null, "alcance": null}` |
| string crua | parte dos feats | `"low_light"` |
| booleano no topo | `senses` de 37 ancestrias | `{"low_light": true}` |

E `low_light` normaliza para `low-light-vision`: a fonte escreve de um jeito e o
pre-requisito, de outro.

De quebra, a ficha ganha `visao().sentidos` -- ela nao dizia o que o personagem
enxerga.

### 2. `focus_pool`

```json
{"focus_pool": {">=": 1}}
```

Responde `focus pool` e `ability to cast focus spells`. O motor **ja calcula**
o pool (regra 22: unico, teto 3); faltava expor como termo.

### 3. `has_actor`

```json
{"has_actor": "companheiro"}
```

Responde `an animal companion`. A fonte e `concessoes_de_ator`, derivada do
`grant_actor` que entrou hoje -- e a resposta e "alguma coisa na ficha concede
um companheiro", nao "existe um ator escrito no documento": o pre-requisito fala
de ter direito ao bicho, nao de ja ter escolhido a especie.

`a familiar` **nao entra**: nao ha paralelo do `grant_actor` para familiar. O
feat que concede usa `grant_item` apontando para um compendio do Foundry, e
`familiar_abilities` conta habilidades extras, nao presenca. Fica no residuo,
declarado.

## O que NAO vira termo, e por que isso e resposta e nao divida

**Alinhamento -- `evil alignment` (7), `tenets of good` (4), `tenets of evil`
(4), `any good alignment` (3).**

O conceito **nao existe na base** e nao e descuido: no Remaster a Paizo aboliu
alinhamento de personagem. Na nossa base `alignment` so aparece em `deity` (33
registros), como caracteristica da divindade. Nao ha o que consultar numa ficha.

Modelar isso exigiria criar um campo de alinhamento **que o sistema atual nao
tem** -- inventar estado para responder pergunta de edicao anterior. Essas 18
clausulas ficam em `requires_residuo`, visiveis como requisito de mesa, que e
exatamente onde uma regra aposentada deve morar.

Mesma logica para `healing font` / `harmful font`: `divine_font` existe em 479
divindades e diz o que a divindade PERMITE; qual fonte o Clerigo escolheu e uma
sub-escolha que a base nao modela hoje. Enquanto nao modelar, nao respondemos.

## Como se prova que funciona

1. Um Anao atende `{"sense": "darkvision"}`; um Humano nao.
2. Uma ancestria que so tem `senses: {"low_light": true}` no topo atende
   `{"sense": "low-light vision"}` -- a forma booleana conta.
3. Um Clerigo 1 atende `{"focus_pool": {">=": 1}}`; um Guerreiro 1 nao.
4. Quem pegou `Animal Companion` atende `{"has_actor": "companheiro"}` **antes**
   de escolher a especie.
5. O parser emite os tres termos, e o total de predicados parseados sobe.
6. Nenhuma clausula de alinhamento vira predicado -- as 18 continuam em
   `requires_residuo`.
7. As 22 fichas derivam identicas nas duas linguagens.


## Resultado medido (2026-07-29)

| | antes dos termos | depois |
|---|---:|---:|
| predicado parseado | 3.889 (91,3%) | **3.919 (92,0%)** |
| frase rejeitada inteira | 372 | **342** |
| registros com residuo | 593 | **591** |

E um ganho pequeno em numero e grande em natureza: os padroes que sobraram
agora ou sao narrativos, ou dependem de dado que a base nao tem -- nenhum e mais
"o schema nao sabia falar disso".

## Uma armadilha do porte, que custou 14 fichas

O Python despacha termo por **convencao** (`getattr(self, f"_termo_{termo}")`):
metodo novo ja fica ativo. O TypeScript despacha por **`switch` explicito**, e
esquecer a linha faz o termo ser IGNORADO em silencio -- o que nao reprova nada
(pelo principio zero, termo desconhecido nao arbitra) e portanto **nao levanta
erro**: so muda a ORDEM da lista de candidatos.

Foi assim que 14 fichas divergiram do gabarito com uma mensagem obscura
(`candidatos.free_archetype@2[31]`: um feat no lugar de outro). O teste de
paridade pegou; nenhum teste de motor pegaria, porque os dois lados estavam
"certos" separadamente.

**Consequencia para a proxima vez:** termo novo mexe em TRES lugares -- o metodo
no Python, o metodo no TS e a linha do `switch`. A terceira e a que se esquece.
