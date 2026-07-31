# Tags e eixos por query

- registros que ganharam `tags`: **549** (eram **0**)
- por kind: {'class-feature': 310, 'equipment': 123, 'feat': 79, 'tactic': 32, 'weapon': 5}

`item:tag` era usado 54 vezes nos filtros da base e o motor o IGNORAVA -- e atomo ignorado conta como SATISFEITO. Isso e certo para estreitar slot de feat e destrutivo para definir eixo, que e por isso que a tag entra antes do eixo.

- eixos criados: **2**

| classe | eixo | escolhe | filtro |
|---|---|---:|---|
| `wb:class/kineticist` | `kinetic-gate` | 2 | `["item:tag:kineticist-kinetic-gate"]` |
| `wb:class/commander` | `tactic` | 5 | `["item:trait:tactic", {"or": ["item:tag:commander-mobility-tactic", "item:tag:commander-offensive-tactic"]}]` |

O bloco guarda o FILTRO, nunca a lista: `candidatos()` avalia com `_casa_filtro`, que ja existia e ja rodava.
