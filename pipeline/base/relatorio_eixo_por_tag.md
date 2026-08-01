# Tags e eixos por query

- registros que ganharam `tags`: **581** (eram **0**)
- por kind: {'class-feature': 310, 'equipment': 123, 'feat': 79, 'tactic': 32, 'action': 32, 'weapon': 5}

`item:tag` era usado 54 vezes nos filtros da base e o motor o IGNORAVA -- e atomo ignorado conta como SATISFEITO. Isso e certo para estreitar slot de feat e destrutivo para definir eixo, que e por isso que a tag entra antes do eixo.

- eixos criados: **9**
- pulados pela guarda anti-duplicata: **19**

O eixo NAO e lista a mao: sai de toda class-feature de PROGRESSAO com `ChoiceSet` de `filter`. A guarda so deixa nascer o eixo cujo filtro alcanca registro hoje INALCANCAVEL -- sem ela, o eidolon do Summoner ganharia um eixo duplicando o slot de ator.

| classe | eixo | nivel | escolhe | casam | inalcancaveis |
|---|---|---:|---:|---:|---:|
| `wb:class/commander` | `expert-tactician` | 7 | 2 | 42 | 42 |
| `wb:class/kineticist` | `fourth-gates-threshold` | 17 | 2 | 6 | 6 |
| `wb:class/kineticist` | `gates-threshold` | 5 | 2 | 6 | 6 |
| `wb:class/kineticist` | `kinetic-gate` | 1 | 2 | 6 | 6 |
| `wb:class/commander` | `legendary-tactician` | 19 | 2 | 62 | 62 |
| `wb:class/commander` | `master-tactician` | 15 | 2 | 52 | 52 |
| `wb:class/kineticist` | `second-gates-threshold` | 9 | 2 | 6 | 6 |
| `wb:class/commander` | `tactics` | 1 | 5 | 28 | 28 |
| `wb:class/kineticist` | `third-gates-threshold` | 13 | 2 | 6 | 6 |

### Pulados

| classe | eixo | motivo |
|---|---|---|
| `wb:class/animist` | `animistic-practice` | nada inalcancavel |
| `wb:class/champion` | `blessing-of-the-devoted` | nada inalcancavel |
| `wb:class/sorcerer` | `bloodline` | ja ha eixo no nivel |
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

## O balaio nomeado pela tag

- blocos de balaio que ganharam nome: **11**
- opcoes cobertas: **91**

O balaio ja funcionava como eixo -- as opcoes certas, no nivel certo, com `escolhe: 1`. Faltava o NOME, e ele estava na `tags` dos registros. Nada muda de conteudo; o bloco passa a ter identidade. Um balaio pode se partir em mais de um eixo: o do Animista carrega dois.

| classe | eixo | nivel | opcoes |
|---|---|---:|---:|
| `wb:class/animist` | `animist-apparition` | 1 | 13 |
| `wb:class/animist` | `animistic-practice` | 1 | 4 |
| `wb:class/barbarian` | `barbarian-instinct` | 1 | 9 |
| `wb:class/champion` | `blessing-of-the-devoted` | 1 | 2 |
| `wb:class/druid` | `druid-order` | 1 | 9 |
| `wb:class/exemplar` | `exemplar-root-epithet` | 3 | 6 |
| `wb:class/exemplar` | `exemplar-dominion-epithet` | 7 | 8 |
| `wb:class/exemplar` | `exemplar-sovereignty-epithet` | 15 | 4 |
| `wb:class/investigator` | `investigator-methodology` | 1 | 5 |
| `wb:class/sorcerer` | `sorcerer-bloodline` | 1 | 18 |
| `wb:class/summoner` | `summoner-eidolon` | 1 | 13 |
