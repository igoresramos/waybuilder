---
spec: requisito-parcial
project: waybuilder
version: 1
status: aprovada
created: 2026-07-29
todo: 86
---

# Spec -- requisito parcial, e o resto virando texto

## O problema, medido

A comparacao com o Pathbuilder (docs/2026-07-29_comparacao-pathbuilder.md) achou
42 dedicacoes que **nos liberamos e ele barra**. A causa e a mesma em todas: o
`requires` da nossa base tem so o nivel, enquanto a prosa diz mais.

    Godless Healing     requires: {character_level >= 2}
                        prosa:    "Trained in Medicine; Battle Medicine"

Na base inteira sao **178 feats** com `requires` so de nivel e prosa citando
pre-requisito. E a causa nao e falta de fonte:

| medicao | numero |
|---|---|
| feats com pre-requisito | 4.261 |
| predicado parseado | 3.609 (84,7%) |
| **parser rejeita a frase INTEIRA** | **635** |
| dos 178 alvos, achados no Foundry pelo nome | 166 |
| **desses, com `prerequisites` ja estruturado** | **158** |

O Foundry entrega o pre-requisito **em itens atomicos**, um por clausula:

    ["trained in Occultism", "you have been in a psychic duel"]

E a nossa prosa junta tudo numa string com `;`.

## A causa: tudo-ou-nada

`Parser._combinar` devolve `None` se **qualquer** parte falhar:

```python
for p in partes:
    r = self._expr(p, tags)
    if r is None:
        return None          # <- perde tambem o que tinha parseado
    saida.append(r)
```

Entao "Trained in Occultism; you have been in a psychic duel" perde as DUAS
coisas por causa da segunda. O `requires` sai vazio, e o passo
`derivar_gate_nivel.py` preenche com o nivel -- e por isso o sintoma final e
"requisito so de nivel", que nao parece perda, parece dado pobre.

Medido: dos 635 rejeitados inteiros, **274 tem ao menos um atomo aproveitavel**
(308 atomos no total).

## A decisao

**Emitir o que deu, e guardar por escrito o que nao deu.**

Isso nao e afrouxar o parser: e o principio zero aplicado ao pre-requisito.
"Trained in Occultism" ORDENA a lista; "you have been in a psychic duel" e
coisa que so a mesa resolve, e o lugar dela e na tela, ao lado do feat, nao no
lixo.

### Campo novo: `requires_residuo`

`requires_texto` **ja existia** e guarda a prosa INTEIRA do pre-requisito, como
referencia. O residuo e outra coisa -- so o pedaco que nao virou predicado --,
entao tem campo proprio em vez de sequestrar o nome.

```json
{
  "id": "wb:feat/psychic-duelist-dedication",
  "requires": {"all": [{"proficiency": {"occultism": {">=": "trained"}}},
                       {"character_level": {">=": 2}}]},
  "requires_texto": "Trained in Occultism; you have been in a psychic duel",
  "requires_residuo": ["you have been in a psychic duel"]
}
```

| | `requires` | `requires_residuo` |
|---|---|---|
| natureza | predicado avaliavel | prosa |
| quem le | motor (`avaliar`) | tela |
| efeito | ordena e marca | **informa, nada mais** |
| ausente quando | nao ha clausula mecanica | tudo parseou |

O motor **nunca** avalia `requires_residuo`. Ele nao entra em `atende`, nao entra
em `fora_do_requisito`, nao vira aviso. E dado para o jogador ler.

### Fonte preferida: a lista atomica do Foundry

Quando o Foundry tem `prereq_lista`, cada item e uma clausula ja separada pela
propria fonte -- melhor que quebrar string por `;` e `,`, que erra em
"Cel Rau, Straveika, Svetocher, or another lineage" (uma clausula so, com
virgulas dentro).

Ordem no fallback: `prereq_lista` do Foundry -> senao, a string da fonte
escolhida, quebrada por `;`.

**A fonte pode TROCAR no fallback, e o `prov` diz isso.** A precedencia normal
(pf2etools > aon > foundry) vale para a primeira tentativa. Quando ela nao
parseia inteira e o Foundry tem a lista atomica, ela ganha -- porque so ela tem
o dado na forma certa. Medido: usando so a fonte escolhida, o parse parcial
recupera 140; deixando o Foundry entrar, **251**.

## O que NAO entra

- **Nao inventar predicado para o narrativo.** "member of the Gray Gardeners"
  (10 ocorrencias), "you have died at least once", "exposure to the Well of
  Axuma" viram `requires_residuo` e ponto.
- **Nao mexer nos 3.609 que ja parseiam.** A mudanca so tem efeito onde hoje o
  resultado e `None`.
- **Nao modelar os padroes mecanicos que faltam** -- `tenets of good` (20),
  `low-light vision` (11), `focus pool` (10), `an animal companion` (6),
  `a familiar` (5). Cada um pede um termo novo no schema de predicado, e isso e
  outra spec. Eles ficam em `requires_residuo`, visiveis, em vez de invisiveis.

## Como se prova que funciona

1. `Psychic Duelist Dedication` passa a ter `occultism >= trained` em `requires`
   e `"you have been in a psychic duel"` em `requires_residuo`.
2. O total de predicados parseados sobe de **3.609 (84,7%) para 3.889 (91,3%)**
   e as falhas totais caem de 652 para 372. 251 registros parseiam SO EM PARTE
   -- e e justamente esse grupo que antes saia vazio.
3. Nenhum dos 3.609 ja parseados muda -- comparacao registro a registro contra
   o build anterior.
4. As 21 fichas de exemplo derivam identicas nas duas linguagens
   (`requires_residuo` nao entra em conta nenhuma).
5. Na comparacao com o Pathbuilder (Fighter 6, aba de dedicacao), as
   divergencias caem de **52 para 23**, e a familia "nos liberamos e ele barra"
   de **42 para 14** -- dois tercos. O que sobra tem nome e esta no relatorio.
6. O portao 1 continua verde, e passa a **cobrar `prov` de `requires_residuo`**
   -- campo preenchido sem procedencia e exatamente o que ele existe para pegar.

## Consequencia na tela

O detalhe do feat ganha uma linha de **requisito de mesa**, com o texto cru,
separada visualmente do requisito avaliado. Sem isso o jogador nao tem como
saber que o feat pede algo que o app nao checa -- e essa e a diferenca entre
informar e esconder.


## Resultado medido (2026-07-29)

| | antes | depois |
|---|---:|---:|
| predicado parseado | 3.609 (84,7%) | **3.889 (91,3%)** |
| parser rejeita a frase inteira | 652 | **372** |
| registros com residuo por escrito | 0 | **593** |
| divergencia com o Pathbuilder (Fighter 6, dedicacao) | 52 | **23** |
| dela, "nos liberamos e ele barra" | 42 | **14** |

Os 14 que restam nao sao mais "requisito vazio": sao clausulas mecanicas que o
schema de predicado ainda nao modela (`tenets of good`, `focus pool`,
`an animal companion`, `a familiar`). Elas estao em `requires_residuo`, com
nome, e cada uma pede um termo novo -- outra spec, com o custo a vista.
