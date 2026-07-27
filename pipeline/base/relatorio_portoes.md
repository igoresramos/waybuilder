# Portoes de qualidade

Base: **19359** registros, 24 kinds.
Todos os portoes sao reportados, inclusive os que passam --
portao ausente e portao aprovado nao podem parecer a mesma coisa.

### Portao 1 -- prov por campo, vocabulario fechado: **PASSA**

0 campos preenchidos sem prov valido

### Portao 2 -- level/rank divergente sem conflito, e espelho rank==level em spell: **PASSA**

0 divergencias silenciadas, 0 spells com espelho quebrado

### Portao 3 -- requires/grants/progressao citando id inexistente: **FALHA**

12 citacoes para 10 ids inexistentes

- `wb:class-feature/universalist-wizard` (2x, ex. em `wb:feat/hand-of-the-apprentice`)
- `wb:class-feature/guardians-calling` (2x, ex. em `wb:feat/repel-assault`)
- `wb:class-feature/caretakers-calling` (1x, ex. em `wb:feat/call-from-deaths-door`)
- `wb:class-feature/demagogues-calling` (1x, ex. em `wb:feat/cutting-rebuke`)
- `wb:class-feature/thespians-calling` (1x, ex. em `wb:feat/cutting-rebuke`)
- `wb:class-feature/acrobats-calling` (1x, ex. em `wb:feat/feet-that-stride-the-sky`)
- `wb:class-feature/thiefs-calling` (1x, ex. em `wb:feat/hands-that-unweave-disaster`)
- `wb:class-feature/artisans-calling` (1x, ex. em `wb:feat/mythic-containment`)
- `wb:feat/underworld-connections` (1x, ex. em `wb:feat/quick-contacts`)
- `wb:class-feature/hunters-calling` (1x, ex. em `wb:feat/read-the-wind`)

### Portao 4 -- queda de cobertura contra o build anterior: **PASSA**

0 kinds encolheram

### Portao 5 -- license presente e xref nao vazio: **PASSA**

0 registros

### Portao 6 -- traits disjuntos sobrando depois da uniao: **PASSA**

0 grupos ainda fundidos num id so; 1 ja desmembrados

- `wb:feat/know-it-all`: ['archetype'] x ['bard', 'thaumaturge']

### Portao 7 -- deteccao de colisao de identidade rodou antes da fusao (em reconciliar.py): **PASSA**

2 registros marcados com `desmembrado_de`

### Portao 8 -- kind com 2+ fontes e zero divergencia registrada: **FALHA**

3 kinds sem instrumentacao de conflito

- `archetype`: 242 registros com 2+ fontes, 0 conflitos
- `class`: 27 registros com 2+ fontes, 0 conflitos
- `familiar-ability`: 73 registros com 2+ fontes, 0 conflitos

### Portao 9 -- cobertura por kind contra o censo do AoN: **FALHA**

1 kinds abaixo do piso

- `familiar-ability`: base 133 / censo 142 -- abaixo do piso (135)
- `ancestry`: base 50 / censo 68 [tolerancia 30%: o AoN conta heranca versatil dentro de ancestry]
- `animal-companion`: base 113 / censo 96 [tolerancia 20%: especializacao e avanco ficam fora por decisao de escopo]
- `archetype`: base 247 / censo 244
- `background`: base 514 / censo 499
- `class-feature`: base 826 / censo 721 [tolerancia 10%: o AoN indexa escolha de subclasse em categoria propria (mystery, patron, instinct, doctrine)]
- `deity`: base 484 / censo 484
- `domain`: base 64 / censo 63
- `feat`: base 6411 / censo 6085
- `heritage`: base 346 / censo 335 [tolerancia 3%: o AoN indexa heranca versatil como ancestry]
- `language`: base 117 / censo 117
- `relic`: base 122 / censo 122
- `ritual`: base 151 / censo 145
- `skill`: base 33 / censo 33
- `spell`: base 1642 / censo 1661
- `trait`: base 561 / censo 556

