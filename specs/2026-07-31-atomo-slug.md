---
spec: atomo-slug
project: waybuilder
version: 1
status: aprovada
created: 2026-07-31
todo: 105
---

# Spec -- `item:slug`, e o que ele NAO alcanca

## A premissa do item nao se sustentou

O item 105 registrava: "`item:slug`, 74 usos, ainda ignorado no
`_atomo_de_filtro`". Medido, sao **79 ocorrencias** em **71 formas distintas**
-- as 74 do registro anterior sairam de um regex que cortava em espaco, e ha
uma ocorrencia com espaco no meio (ver abaixo).

E, principalmente: **implementar `item:slug` no `_atomo_de_filtro` nao mudaria
nada em ficha nenhuma.** O atomo nao e avaliado ali. Onde ele vive:

| onde vive | atomos | avaliado hoje? |
|---|---:|---|
| `grants/choice/filtro`, `tipo: spell` (10 blocos, 11 registros) | 60 | **nao** |
| `grants/choice/filtro`, `tipo: ancestry` / `heritage` | 4 | **nao** |
| `grants/weapon_proficiency/definicao` -- alvos de ARMADURA | 3 | avaliado, sem efeito |
| `grants/weapon_proficiency/definicao` -- alvos de ARMA | **2** | avaliado, e **errado** |
| referencia dinamica de ator (`{actor\|...}`) | 2 | `None`, correto |

**Por que os 60 nao sao avaliados:** `slots_concedidos` so coleta
`ch.get("tipo") == "feat"` (43 blocos). Os 10 blocos de `tipo: spell` nunca
viram slot, entao seu filtro nunca e consultado. `Dragon Spit`, `Hag Magic`,
`Arcane Tattoos` e as outras 8 escolhas de truque simplesmente nao sao
perguntadas ao jogador.

**E nao adianta coletar:** a ficha nao modela QUAIS magias o personagem sabe.
`_conjuracao` entrega capacidade -- slots por rank, tradicao, DC, rank efetivo
da houserule -- e nao ha campo de magia conhecida em nenhum dos dois motores.
Um slot de escolha de magia nao teria onde pousar. E a situacao do item 96:
falta o consumidor, nao o atomo.

**Os 3 de armadura:** `Armiger's Protection` remapeia
`hellknight-breastplate`, `-half-plate` e `-plate`. Os tres sao `wb:armor/*`, e
`_remaps_de_arma()` so roda dentro de `_rank_da_arma`. Nao existe caminho de
remap de ARMADURA. Implementar `slug` nao os alcanca.

## Os 2 que sobram sao reais, e entregam numero errado

`wb:feat/sister-of-the-golden-erinys-dedication`:

```json
{"igual_a": "simple", "definicao": [{"or": ["item:slug:asp-coil",
                                            "item:slug:scourge"]}]}
```

Os dois existem na base e os dois sao **`martial`**. A dedicacao diz: trate-os
como **simples**. Hoje `_arma_casa` conhece `base`, `category`, `trait` e
`group`, e `slug` cai no `return False` final -- o remap nunca aplica.

Efeito: um Clerigo (treinado em simples, nao em marciais) com essa dedicacao le
**untrained** nas duas armas, onde o RAW da trained. Erra o bonus de ataque e,
por tabela, o grau que alimenta `Weapon Specialization` no dano.

E dedicacao de arquetipo, e a regra 2 mantem Free Archetype sempre ligada --
entao e alcancavel por qualquer personagem, nao um canto raro.

## O conserto

Uma linha em cada motor. `slug` tem, na nossa representacao, exatamente a
semantica que `base` ja tem -- o sufixo do id:

```python
if seletor in ("base", "slug"):
    return norm_slug(arma.get("id", "").split("/")[-1]) == valor
```

`norm_slug` ja resolve o defeito de fonte `item:slug:dispel magic` (com
espaco), que aparece em `wb:feat/methodical-magic` -- mas essa ocorrencia esta
no ramo de magia, que nao e avaliado. Fica registrada, nao consertada.

## A decisao: `_atomo_de_filtro` NAO recebe `slug`

Seria codigo morto nas 64 ocorrencias que passam por la, e o projeto proibe
abstracao prematura. Quando o slot de escolha de magia existir -- e ele depende
de a ficha modelar magia conhecida --, o atomo entra junto, com consumidor.

O que ficou medido para quem voltar aqui: os 69 atomos estaticos resolvem
**100%** contra a base, 55 pelo sufixo do id e 14 por alias. Os 5 que nao
casavam por id (`acid-splash`, `ghost-sound`, `ray-of-frost`, `produce-flame`,
`dispel`) sao nomes pre-remaster, e quatro ja sao alias do registro remasterizado
(`caustic-blast`, `figment`, `frostbite`, `ignition`). Nenhum aponta para o
vazio. A ambiguidade que o item temia ("o slug do Foundry nem sempre e o nosso
id, entao errar ali aponta para o registro ERRADO") **nao existe**: o atomo
TESTA o candidato, nao aponta para registro, e os 9 slugs que casam com mais de
um id (`shield`, `lock`, `charm`...) casam com exatamente um dentro do `tipo` do
slot.

## Como se prova que funciona

1. Um Clerigo 1 com `Sister of the Golden Erinys Dedication` le **trained** em
   `asp-coil` e em `scourge`; sem a dedicacao, le untrained.
2. O melhor rank continua vencendo: um Guerreiro (expert em marcial) com a
   dedicacao NAO cai para trained -- e a licao ja travada na spec de
   proficiencia de arma nomeada.
3. Nenhuma outra arma muda de rank.
4. Paridade Python/TS, diff de fixture LIDO.
5. Quatro camadas verdes.
