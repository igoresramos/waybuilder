# Portoes de qualidade

Base: **19418** registros, 24 kinds.
Todos os portoes sao reportados, inclusive os que passam --
portao ausente e portao aprovado nao podem parecer a mesma coisa.

### Portao 1 -- prov por campo, vocabulario fechado: **PASSA**

0 campos preenchidos sem prov valido

### Portao 2 -- level/rank divergente sem conflito, e espelho rank==level em spell: **PASSA**

0 divergencias silenciadas, 0 spells com espelho quebrado

### Portao 3 -- requires/grants/progressao citando id inexistente: **PASSA**

0 citacoes para 0 ids inexistentes nao declarados; 2 declarados sem sucessor conhecido

- `wb:class-feature/universalist-wizard` (2x, ex. em `wb:feat/hand-of-the-apprentice`)
- `wb:feat/underworld-connections` (1x, ex. em `wb:feat/quick-contacts`)
- declarado: `wb:class-feature/universalist-wizard` -- escola Universalist do Legacy. O remaster trocou as escolas do Mago por outras dez (School of Ars Grammatica, Battle Magic, Civic Wizardry, Gates, Kalistrade, Magical Technologies, Mentalism, Protean Form, Rooted Wisdom, Unified Magical Theory) e nenhuma e sucessora direta. Fica quebrada ate a decisao de modelagem
- declarado: `wb:feat/underworld-connections` -- feat do Advanced Player's Guide citado por wb:feat/quick-contacts. Zero ocorrencias no dump do AoN e no checkout do Foundry -- e ausencia das fontes, nao do pipeline

### Portao 4 -- queda de cobertura contra o build anterior: **PASSA**

0 kinds encolheram

### Portao 5 -- license presente e xref nao vazio: **PASSA**

0 registros

### Portao 6 -- traits disjuntos ou salto de level sobrando depois da uniao: **PASSA**

0 grupos ainda fundidos num id so; 0 com salto de level >= 8 em kind de escolha; 1 ja desmembrados

- `wb:feat/know-it-all`: ['archetype'] x ['bard', 'thaumaturge']

### Portao 7 -- deteccao de colisao de identidade rodou antes da fusao (em reconciliar.py): **PASSA**

2 registros marcados com `desmembrado_de`

### Portao 8 -- kind com 2+ fontes e zero divergencia registrada: **PASSA**

0 kinds sem instrumentacao de conflito

### Portao 9 -- cobertura por kind contra o censo do AoN: **PASSA**

0 kinds abaixo do piso

- `ancestry`: base 50 / censo 68 [tolerancia 30%: o AoN conta heranca versatil dentro de ancestry]
- `animal-companion`: base 113 / censo 96 [tolerancia 20%: especializacao e avanco ficam fora por decisao de escopo]
- `archetype`: base 247 / censo 244
- `background`: base 514 / censo 499
- `class-feature`: base 841 / censo 721 [tolerancia 10%: o AoN indexa escolha de subclasse em categoria propria (mystery, patron, instinct, doctrine)]
- `deity`: base 490 / censo 484
- `domain`: base 64 / censo 63
- `familiar-ability`: base 171 / censo 142
- `feat`: base 6411 / censo 6085
- `heritage`: base 346 / censo 335 [tolerancia 3%: o AoN indexa heranca versatil como ancestry]
- `language`: base 117 / censo 117
- `relic`: base 122 / censo 122
- `ritual`: base 151 / censo 145
- `skill`: base 33 / censo 33
- `spell`: base 1642 / censo 1661
- `trait`: base 561 / censo 556

