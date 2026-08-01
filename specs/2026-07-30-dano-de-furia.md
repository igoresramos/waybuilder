---
spec: dano-decomposto
req: WB-032
project: waybuilder
version: 2
status: implementada
created: 2026-07-30
todo: 42
---

# Spec -- o dano da ficha vira parcelas, e o dano de furia e uma delas

> **v2, 2026-07-30.** A v1 propunha so uma linha de dano de furia. O Igor
> corrigiu o escopo: *"entra como um adicional do dano, n precisa integrar,
> gostaria que o dano sempre fosse decomposto, dano da arma adicional do dano,
> habilidades e tal"*. O entregavel deixa de ser um numero e passa a ser a
> **decomposicao**.

## O que a ficha faz hoje

`self.ataques` monta o dano como **string ja concatenada**:

```python
"dano": f"{dados}{dano.get('dado','')}{mod_dano:+d}"      # -> "2d8+4"
```

O ATAQUE tem `detalhe` ("nivel 15 + prof 6 (master) + FOR +4"). O DANO nao tem
nada: e uma string opaca, e nao da para saber de onde saiu o `+4`.

E ela esta **incompleta**, nao so opaca. Sao duas parcelas faltando, as duas
deterministas.

## Lacuna 1 -- Weapon Specialization, em 26 das 27 classes

`wb:class-feature/weapon-specialization` tem **`grants: []`** na base.

O Foundry declara em `FlatModifier` + dois `AdjustModifier`, sobre
`unarmed-damage` e `weapon-damage`, com o predicado no rank **da arma**:

| rank da arma | Weapon Spec | com Greater Weapon Spec |
|---|---:|---:|
| expert | +2 | +4 |
| master | +3 | +6 |
| legendary | +4 | +8 |

`Greater Weapon Specialization` e `AdjustModifier mode: multiply, value: 2` --
dobra, nao soma.

**26 das 27 classes** concedem (todas menos o Exemplar). Ou seja: hoje **todo
personagem do jogo a partir do nivel 7 tem o dano errado na ficha**, faltando
de 2 a 8. Esta e a maior das duas lacunas, e ela nao e sobre o Barbaro.

O motor ja tem tudo para calcular: `self.ataques` ja resolve o rank daquela
arma (`_rank_de_arma`), e `_termo_has` ja enxerga class-feature vinda da
progressao.

## Lacuna 2 -- dano de furia, o item 42 propriamente

A premissa do item 42 (*"o que sobra e mecanica CONDICIONAL"*) nao se sustenta
na medicao. `AdjustModifier` com `slug: "rage"` sao **37 regras em 15
registros**, e nada mais na base usa esse slug. Hoje os nove instintos tem
`grants: []`: escolher instinto nao muda um numero sequer.

| instinto | grau 1 | grau 2 (Weapon Spec) | grau 3 (Greater) | condicao |
|---|---:|---:|---:|---|
| Fury | 3 | 7 | 13 | -- |
| Elemental | 4 | 6 | 12 | -- |
| Superstition | 3 | 7 | 13 | -- |
| Animal | -- | 5 | 12 | -- |
| Bloodrager | 2 | 4 | 8 | -- |
| Giant | 6 | 10 | 18 | arma `oversized` |
| Dragon | 4 | 8 | 16 | `draconic-rage` |
| Spirit | 3 | 7 | 13 | `spirit-rage` |
| Ligneous | 6 | 10 | 18 | `wooden-rage` |
| Decay | 6 | 10 | 18 | `rotting-rage` |

Base de todos: **+2**, do proprio `Rage`. `mode: upgrade` = **maior vence**, nao
soma -- o instinto substitui o +2. Animal nao tem grau 1: do nivel 1 ao 6 vale
o +2, e isso e RAW (o instinto Animal paga em golpe desarmado).

## O formato: parcelas, nao string

`ataques[].dano` deixa de ser string e vira lista. O total continua existindo,
derivado dela -- ninguem perde o numero, mas ele para de ser a unica coisa.

```json
"dano": {
  "parcelas": [
    {"tipo": "dados",     "texto": "2d8", "origem": "Longsword (+1 striking)"},
    {"tipo": "atributo",  "valor": 4,     "origem": "FOR"},
    {"tipo": "weapon_specialization", "valor": 4,
     "origem": "Greater Weapon Specialization (master)"},
    {"tipo": "rage",      "valor": 7,     "origem": "Fury Instinct"}
  ],
  "total": "2d8+15",
  "condicionais": [
    {"valor": 8, "origem": "Dragon Instinct", "condicao": "draconic rage"}
  ]
}
```

Regras do formato:

1. **Parcela nunca some.** Valor zero nao entra; valor calculado entra sempre,
   com `origem` escrita. A origem e o que faz a decomposicao valer.
2. **`condicionais` fica separado e nao entra no total.** E o principio zero:
   marca com a condicao nomeada, nunca esconde, nunca soma escondido.
3. **`total` e derivado**, nunca guardado -- cache, como o resto de `visao()`.

## A decisao que exige registro: qual "nivel" e o grau 2 da furia

O Foundry escreve o grau 2 de oito instintos como `{"gte": ["self:level", 7]}`,
e `self:level` la e **nivel de personagem**. Aqui os dois numeros diferem, entao
traduzir ao pe da letra seria escolher, nao ler.

**Adotado: o grau amarra na FEATURE, nao no numero** --
`wb:class-feature/weapon-specialization` (nivel 7 do Barbaro) e
`wb:class-feature/greater-weapon-specialization-barbarian` (nivel 15), lidos da
progressao do proprio Barbaro.

1. O proprio Foundry escreve assim no Elemental Instinct
   (`feature:weapon-specialization`). A forma esta no dado.
2. A regra 3 ja decidiu esta familia: *"o rank vem do nivel da classe que
   concede"*. Dano de furia e identidade de classe.
3. Amarrar na feature nao dessincroniza da progressao; amarrar no 7 pode.

## O que esta spec NAO resolve, e declara com numero

- **`item:trait:agile` corta pela metade** (2 regras, `mode: multiply 0.5`). E
  por arma, no momento do golpe.
- **`Effect: Share Rage`, `Guard's Fury`, `Mighty Rage`** -- 3 regras de efeito
  ativo ou acao gasta na rodada.
- **Os 22 `flat_modifier` condicionais em seletor de dano** (`sailfish-strike`,
  `oath-of-the-slayer`, `watch-this`...) entram em `condicionais`, marcados,
  **nao somados**. Os 2 incondicionais (`benefactors-strike` unarmed +1,
  `house-drake` jaws +1) entram como parcela normal.
- **Os 30 `Strike` do Animal Instinct.** Conceder ataque desarmado e outra
  familia, sem consumidor na ficha hoje.
- **`ragingResistance`** (`3 + con.mod`, `8 + con.mod` com Unstoppable
  Juggernaut) e o tipo resistido por instinto: mesmo achado, mas mexe em
  `_resistencias`, que tem gramatica propria. **Item proprio**, medicao pronta.
- **`target:caster` do Superstition** (4/8/16): alvo e do combate.

## Como se prova que funciona

1. Os dez registros de instinto ganham `rage_damage`; hoje sao dez `grants: []`.
2. `wb:class-feature/weapon-specialization` deixa de ter `grants: []`.
3. **Guerreiro 7** com longsword (rank expert): parcela
   `weapon_specialization: +2` com a origem escrita. Hoje nao aparece.
4. **Guerreiro 15** com longsword (master + Greater): `+6`, nao `+3`.
5. Barbaro 1 Fury: parcelas `dados`, `atributo`, `rage +3`. Sem condicional.
6. Barbaro 7 Fury: `rage +7`. Barbaro 15 Fury: `rage +13`.
7. Barbaro 1 Animal: **sem** parcela `rage` de instinto -- vale o +2 base.
8. Barbaro 7 Dragon: parcela `rage +2` e **condicional** `+8` com
   `draconic rage` escrito. O total NAO inclui o 8.
9. Barbaro 1 **sem instinto escolhido**: `rage +2`, sem aviso de erro.
10. Guerreiro 15 nao tem parcela `rage` nenhuma.
11. A ficha mostra as parcelas, nao so o total.
12. Paridade Python/TS no fixture, diff LIDO.
13. Quatro camadas verdes.

## Risco declarado

`ataques[].dano` muda de **string para objeto**. Quebra todo consumidor: o
`PainelDireito.tsx` em dois pontos (linhas 224 e 318), os fixtures de paridade e
o comparador do Pathbuilder. E mudanca de contrato, nao aditiva -- por isso esta
escrita aqui antes de qualquer codigo.
