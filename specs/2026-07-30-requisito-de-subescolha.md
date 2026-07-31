---
spec: requisito-de-subescolha
project: waybuilder
version: 1
status: aprovada
created: 2026-07-30
todo: 84
---

# Spec -- "grandeur cause" era prosa, e virou requisito

## Como apareceu

5a rodada de comparacao com o Pathbuilder, agora com as cinco classes que
faltavam (Campeao, Druida, Feiticeiro, Alquimista, Investigador). No Campeao 1,
**cinco** feats em que nos dizemos que atende e ele diz que nao:

```
Brilliant Flash        res=['grandeur cause']
Iron Repercussions     res=['obedience cause']
Nimble Reprisal        res=['justice cause']
Ongoing Selfishness    res=['desecration cause']
Vicious Vengeance      res=['iniquity cause']
```

O `requires` deles so tem `class_level >= 1`; a exigencia de CAUSA esta em
`requires_residuo`, como prosa. Ou seja: oferecemos a um Campeao de qualquer
causa um feat que so a causa `grandeur` destrava.

E o Pathbuilder acerta. Este e o tipo de defeito que a comparacao existe para
achar -- defeito de PREDICADO, o mais caro de encontrar por leitura.

## O tamanho, medido

A forma e sempre a mesma: `<nome da opcao> <nome do eixo>`. Aplicada a base
inteira, **26 clausulas em 26 registros**, em sete eixos:

| eixo | classe | exemplo |
|---|---|---|
| `cause` | Campeao | `grandeur cause` |
| `muse` | Bardo | `zoophonia muse` |
| `hybrid-study` | Magus | `laughing shadow hybrid study` |
| `subconscious-mind` | Psychic | `wandering reverie subconscious mind` |
| `racket` | Ladino | `eldritch trickster racket` |
| `mystery` | Oraculo | `time mystery` |
| `research-field` | Alquimista | `chirurgeon research field` |

Sao **179 chaves** possiveis (opcao x eixo) e apenas **3 ambiguas** -- as tres
do eixo `sanctification`, criado hoje, cujas opcoes sao os MESMOS ids em duas
classes. Ficam de fora.

## Onde o conserto mora, e por que nao no parser

O parser de `feats.py` roda na EXTRACAO, e os eixos so existem depois de
`aplicar_subclasses.py`. No momento em que a clausula e lida, nao ha com o que
casar.

Entao e um passo TARDIO sobre a base, como `aplicar_aliases_em_requires.py` ja
faz: monta o mapa `<opcao> <eixo>` -> `(classe, id)` a partir das proprias
`subclasses`, e o que casar sai de `requires_residuo` e entra em `requires`
como `{"subclass": {classe: id}}`.

## As decisoes

1. **So chave sem ambiguidade.** Uma chave que aponte para mais de uma classe
   e descartada -- mapear para a errada e pior que deixar em prosa.
2. **Fora o balaio `outras-opcoes` e o eixo `deity`.** O primeiro nao e eixo de
   verdade (item 69); o segundo tem 488 nomes e casaria por acidente.
3. **A clausula tem de casar POR INTEIRO**, sem sobra. `grandeur cause and you
   have X` nao casa -- prefixo nao basta.
4. **O `requires` existente e preservado**, combinado com `all`. Nenhum
   requisito e trocado; o novo termo se soma.

## O que esta spec NAO resolve, e declara

- **Os outros achados da 5a rodada** foram triados e nao sao defeito nosso:
  os 3 `so no Waybuilder` que aparecem em TODAS as classes (Chelaxian Scion,
  Knight Vigilant, Venture-Gossip Dedication) sao recorte de fonte, e os
  `wb=False pb=True` por pericia sao a diferenca de modelo ja declarada (ele
  conta escolha pendente como alcancavel; nos avaliamos o estado atual e
  marcamos).
- **`Chemical Contagion` e `Enhanced Fire`** (so no Pathbuilder, Alquimista)
  ficam por investigar em rodada propria.
- **Druida e Feiticeiro nao tem feat de classe no nivel 1** -- foram medidos no
  nivel 2, e isso e informacao, nao falha.

## Como se prova que funciona

1. `wb:feat/brilliant-flash` responde `requires` com
   `{"subclass": {"champion": "wb:class-feature/grandeur"}}` e
   `requires_residuo` vazio.
2. Um Campeao de causa `grandeur` ATENDE; um de `justice` NAO.
3. As 26 clausulas saem do residuo, e o total cai na mesma medida.
4. Nenhum registro perde `requires` que ja tinha.
5. As tres chaves de `sanctification` NAO sao usadas.
6. Quatro camadas verdes.
