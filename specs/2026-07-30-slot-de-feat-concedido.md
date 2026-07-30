---
spec: slot-de-feat-concedido
project: waybuilder
version: 1
status: aprovada
created: 2026-07-30
todo: 94
---

# Spec -- o feat que da OUTRO feat, e o slot que nunca abre

## O problema, na frase do Igor

> tem algumas coisas tipo ancient elf q libera uma classe ou feat adicional

`Ancient Elf` diz, na prosa oficial:

> Choose a class other than your own. You gain the multiclass dedication feat
> for that class.

Hoje o app nao pergunta nada. O jogador escolhe `Ancient Elf` e nao recebe slot
nenhum -- a dedicacao simplesmente nao acontece.

## As duas familias, que e o que torna isso perigoso

Medido na prosa da base inteira, ha DUAS formas que se parecem e nao sao:

| familia | exemplo | o que faz |
|---|---|---|
| **A -- abre slot** | `Ancient Elf`: "You gain the multiclass dedication feat for that class" | concede um feat NOVO |
| **B -- alarga o pool** | `Aiuvarin`: "when you gain an ancestry feat, you can choose from aiuvarin feats" | nao da feat nenhum; so amplia o que o slot JA existente aceita |

Tratar B como A **da feat de graca**. A varredura de prosa por padrao de
linguagem acha A=142 e B=476 com **55 em comum** -- e o padrao "when/whenever you
gain X feat" e justamente o que separa: quem tem esse gatilho e B disfarcado de
A. Depois de filtrar, sobram ~89 candidatos de A, e uma revisao manual ainda
descarta ~14 ruidos ("choose a *different* deviant feat", "qualified you for
this feat").

**Esta spec nao usa a prosa.** A prosa serviu para entender as familias; a
implementacao usa dado estruturado, que nao tem essa ambiguidade -- o Foundry so
escreve o ChoiceSet na familia A.

## O dado existe, estruturado, e o extrator o joga fora

No dump do Foundry ha **101 ChoiceSet com `itemType: "feat"`** -- 95 em docs de
`feat` e 6 em docs de `heritage`. Cada um carrega o filtro do que o slot aceita.
`Ancient Elf`, verbatim da fonte:

```json
{"filter": ["item:category:class", "item:trait:dedication",
            "item:trait:multiclass"], "itemType": "feat"}
```

O extrator de feats (`extratores/feats.py:1019`) faz:

```python
elif isinstance(esc, dict):
    resumo["filtro"] = True          # <- a consulta inteira vira um booleano
    if esc.get("itemType"):
        resumo["tipo"] = esc["itemType"]
```

A base fica sabendo que **existe** uma escolha de feat e nao sabe **quais**. Sao
os 40 registros com `choice.tipo == "feat"` que ela tem hoje, todos com
`filtro: true`.

E o `Ancient Elf` nem esta entre os 40: `extratores/ancestrias.py:549-563`
converte **somente FlatModifier** para heranca. Todo o resto do rule element e
descartado, e por isso `wb:heritage/ancient-elf` sai com `grants: []` e 258 das
334 herancas estao `grants_completos: false`.

O caso canonico que o Igor levantou perde a mecanica por causa de um extrator
que implementa um rule element de uma lista de doze.

## A gramatica do filtro, medida nos 101

| operadores | ocorrencias |
|---|---:|
| `lte` | 59 |
| `not` | 37 |
| `or` | 28 |
| `and` | 16 |
| `xor` | 8 |
| `nor` | 2 |

| atomo | ocorrencias |
|---|---:|
| `item:trait:X` | 291 |
| `item:level:N` | 94 |
| `item:category:X` | 56 |
| `parent:granter:X` | 12 |
| `item:rarity:X` | 8 |
| cauda de flags de uma ocorrencia cada | ~25 |

**153 atomos carregam referencia dinamica** (`{actor|system.details.ancestry.trait}`),
e **35 dos 101 filtros sao lista de strings estaticas pura** -- sem operador e
sem referencia dinamica.

O motor ja tem avaliador de predicado com `or`/`and`/`not` (`predicado.py`).
Nao e um interpretador novo: e um vocabulario novo (`item:*`) e tres operadores
(`lte`, `xor`, `nor`) num avaliador que ja existe.

## As decisoes

1. **O filtro passa a ser guardado como esta na fonte**, lista e tudo, em vez de
   `true`. Nenhuma traducao na extracao: traduzir cedo e o que apagou a
   informacao da primeira vez.
2. **Heranca ganha a conversao de ChoiceSet**, e so ela. Sao 35 herancas com
   ChoiceSet. O resto do buraco da heranca fica DECLARADO e nao resolvido aqui:
   GrantItem 463, ActiveEffectLike 383, Sense 152, Resistance 112, BaseSpeed 83,
   RollOption 71, Strike 60, CreatureSize 44. E outro item, com outra medicao.
3. **O slot nasce do feat ESCOLHIDO**, e nao da classe. `_slots_de_feat` hoje so
   varre `entrada_da_classe`; passa a varrer tambem os feats efetivos e a
   injetar um slot por `choice` de tipo `feat` que eles carreguem.
4. **O filtro restringe `candidatos()` daquele slot.** Um slot de `Ancient Elf`
   que aceitasse qualquer feat seria pior que nao existir: entregaria escolha
   ilegal com cara de legal.
5. **Atomo que o avaliador nao conhece NAO reprova** -- principio zero. O
   candidato aparece com `atende: false` e o motivo no residuo, como em todo
   requisito nao avaliado. Referencia dinamica `{actor|...}` entra aqui ate ter
   medicao propria.

## O que esta spec NAO resolve, e declara

- **A familia B** (alargar o pool). Nao ha ChoiceSet nela -- o Foundry a
  modela de outro jeito, e trata-la aqui e que produziria feat de graca.
- **Os ~40 registros da familia A sem ChoiceSet nenhum na fonte** (13
  backgrounds, `wb:mystery/ancestors-legacy`, entre outros). Sem dado
  estruturado, so a prosa responde, e a prosa e ambigua. Ficam contados.
- **Referencia dinamica `{actor|...}`** nos 153 atomos: exige resolver caminho
  de ator do Foundry contra o nosso modelo. Medicao propria.
- **O resto dos rule elements da heranca**, com os numeros acima.

## Como se prova que funciona

1. `wb:heritage/ancient-elf` deixa de ter `grants: []` e passa a carregar o
   `choice` com o filtro de tres atomos da fonte.
2. Os registros com `choice.tipo == "feat"` sobem de 40 para perto de 75.
3. Nenhum registro perde grant: o diff da base so acrescenta.
4. Um personagem com `Ancient Elf` tem um slot aberto a mais do que o mesmo
   personagem sem ele.
5. `candidatos()` desse slot devolve SO feat de dedicacao multiclasse -- e
   `Fleet` (feat geral) nao aparece como `atende: true`.
6. Um personagem sem nenhum feat da familia A tem exatamente os mesmos slots de
   hoje -- o diff dos 27 fixtures prova.
7. Quatro camadas verdes e os 10 portoes.
