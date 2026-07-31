# Tags e eixos por query

- registros que ganharam `tags`: **549** (eram **0**)
- por kind: {'class-feature': 310, 'equipment': 123, 'feat': 79, 'tactic': 32, 'weapon': 5}

`item:tag` era usado 54 vezes nos filtros da base e o motor o IGNORAVA -- e atomo ignorado conta como SATISFEITO. Isso e certo para estreitar slot de feat e destrutivo para definir eixo, que e por isso que a tag entra antes do eixo.

- eixos criados: **9**
- pulados pela guarda anti-duplicata: **19**

O eixo NAO e lista a mao: sai de toda class-feature de PROGRESSAO com `ChoiceSet` de `filter`. A guarda so deixa nascer o eixo cujo filtro alcanca registro hoje INALCANCAVEL -- sem ela, o eidolon do Summoner ganharia um eixo duplicando o slot de ator.

| classe | eixo | nivel | escolhe | casam | inalcancaveis |
|---|---|---:|---:|---:|---:|
| `wb:class/commander` | `expert-tactician` | 7 | 2 | 21 | 21 |
| `wb:class/kineticist` | `fourth-gates-threshold` | 17 | 2 | 6 | 6 |
| `wb:class/kineticist` | `gates-threshold` | 5 | 2 | 6 | 6 |
| `wb:class/kineticist` | `kinetic-gate` | 1 | 2 | 6 | 6 |
| `wb:class/commander` | `legendary-tactician` | 19 | 2 | 31 | 31 |
| `wb:class/commander` | `master-tactician` | 15 | 2 | 26 | 26 |
| `wb:class/kineticist` | `second-gates-threshold` | 9 | 2 | 6 | 6 |
| `wb:class/commander` | `tactics` | 1 | 5 | 14 | 14 |
| `wb:class/kineticist` | `third-gates-threshold` | 13 | 2 | 6 | 6 |

### Pulados

| classe | eixo | motivo |
|---|---|---|
| `wb:class/animist` | `animistic-practice` | nada inalcancavel |
| `wb:class/champion` | `blessing-of-the-devoted` | nada inalcancavel |
| `wb:class/sorcerer` | `bloodline` | nada inalcancavel |
| `wb:class/champion` | `deity-champion` | ja ha eixo no nivel |
| `wb:class/exemplar` | `divine-spark-and-ikons` | ja ha eixo no nivel |
| `wb:class/exemplar` | `dominion-epithet` | nada inalcancavel |
| `wb:class/druid` | `druidic-order` | nada inalcancavel |
| `wb:class/summoner` | `eidolon` | nada inalcancavel |
| `wb:class/summoner` | `evolution-feat` | nada inalcancavel |
| `wb:class/thaumaturge` | `first-implement-and-esoterica` | ja ha eixo no nivel |
| `wb:class/gunslinger` | `gunslingers-way` | ja ha eixo no nivel |
| `wb:class/investigator` | `methodology` | nada inalcancavel |
| `wb:class/bard` | `muses` | ja ha eixo no nivel |
| `wb:class/rogue` | `rogues-racket` | ja ha eixo no nivel |
| `wb:class/exemplar` | `root-epithet` | nada inalcancavel |
| `wb:class/thaumaturge` | `second-implement` | nada inalcancavel |
| `wb:class/exemplar` | `sovereignty-epithet` | nada inalcancavel |
| `wb:class/swashbuckler` | `swashbucklers-style` | ja ha eixo no nivel |
| `wb:class/thaumaturge` | `third-implement` | nada inalcancavel |

O bloco guarda o FILTRO, nunca a lista: `candidatos()` avalia com `_casa_filtro`, que ja existia e ja rodava.
