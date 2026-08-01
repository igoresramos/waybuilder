# Parcelas de dano

## Weapon Specialization

- registros tocados: **4**

Estava `grants: []` em todos. 26 das 27 classes concedem: todo personagem do nivel 7 pra cima tinha o dano errado na ficha.

| registro | efeito |
|---|---|
| `wb:class-feature/greater-weapon-specialization` | `{"multiplicador": 2}` |
| `wb:class-feature/greater-weapon-specialization-barbarian` | `{"multiplicador": 2}` |
| `wb:class-feature/psychic-weapon-specialization` | `{"por_rank": {"expert": 2, "master": 3, "legendary": 4}}` |
| `wb:class-feature/weapon-specialization` | `{"por_rank": {"expert": 2, "master": 3, "legendary": 4}}` |

## Dano de furia

- registros com `rage_damage`: **21**
- descartados: **7** (alvo do combate 3, Mighty Rage 1, Elemental Evolution 1, Guard's Fury 1, valor nao inteiro 1)

`mode: upgrade` = maior vence, nao soma: o instinto SUBSTITUI o +2 do Rage.

| registro | nome | condicao | graus |
|---|---|---|---|
| `wb:action/rage` | Rage | -- | 2 |
| `wb:class-feature/animal-instinct` | Animal Instinct | -- | 5, 12 |
| `wb:class-feature/bloodrager` | Bloodrager | -- | 2, 4, 8 |
| `wb:class-feature/decay-instinct` | Decay Instinct | rotting rage | 6, 10, 18 |
| `wb:class-feature/dragon-instinct` | Dragon Instinct | draconic rage | 4, 8, 16 |
| `wb:class-feature/elemental-instinct` | Elemental Instinct | -- | 4, 6, 12 |
| `wb:class-feature/fury-instinct` | Fury Instinct | -- | 3, 7, 13 |
| `wb:class-feature/giant-instinct` | Giant Instinct | arma oversized | 6, 10, 18 |
| `wb:class-feature/ligneous-instinct` | Ligneous Instinct | wooden rage | 6, 10, 18 |
| `wb:class-feature/rage` | Rage (base) | -- | 2 |
| `wb:class-feature/spirit-instinct` | Spirit Instinct | spirit rage | 3, 7, 13 |
| `wb:class-feature/superstition-instinct` | Superstition Instinct | -- | 3, 7, 13 |
