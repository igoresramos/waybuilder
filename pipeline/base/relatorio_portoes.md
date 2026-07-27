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

### Portao 8 -- kind com 2+ fontes e zero divergencia registrada: **FALHA**

1 kinds sem instrumentacao de conflito

- `shield`: 112 registros com 2+ fontes, 0 conflitos

### Portao 9 -- cobertura por kind contra o censo do AoN: **FALHA**

3 kinds abaixo do piso, 0 categorias do censo sem kind mapeado

- `equipment`: base 6099 / censo 6304 -- abaixo do piso (6178) [tolerancia: a base emite variante por grau/runa que o AoN indexa como uma entrada so, entao o excesso e esperado]
- `tactic`: base 0 / censo 37 -- abaixo do piso (36)
- `class-kit`: base 0 / censo 32 -- abaixo do piso (31)
- `feat`: base 6411 / censo 6085
- `spell`: base 1642 / censo 1661
- `class-feature`: base 841 / censo 721 [tolerancia 10%: o AoN indexa escolha de subclasse em categoria propria (mystery, patron, instinct, doctrine)]
- `trait`: base 561 / censo 556
- `background`: base 514 / censo 499
- `deity`: base 490 / censo 484
- `weapon`: base 1031 / censo 372 [tolerancia 2%: idem equipment]
- `heritage`: base 346 / censo 335 [tolerancia 3%: o AoN indexa heranca versatil como ancestry]
- `archetype`: base 247 / censo 244
- `ritual`: base 151 / censo 145
- `familiar-ability`: base 171 / censo 142
- `relic`: base 122 / censo 122
- `language`: base 117 / censo 117
- `animal-companion`: base 113 / censo 96 [tolerancia 20%: especializacao e avanco ficam fora por decisao de escopo]
- `ancestry`: base 50 / censo 68 [tolerancia 30%: o AoN conta heranca versatil dentro de ancestry]
- `domain`: base 64 / censo 63
- `armor`: base 204 / censo 42 [tolerancia 2%: idem equipment]
- `familiar-specific`: base 39 / censo 38
- `skill`: base 33 / censo 33
- `class`: base 27 / censo 27
- `arcane-school` (23) coberta por trait (22 de 23: as escolas do Legacy sao traits; a base segue a taxonomia remaster)
- `ikon` (21) coberta por class-feature (21 de 21 conferidos por nome: as ikons do Exemplar sao class-features na base)

### Portao 10 -- todo registro emitido tem prosa: **PASSA**

168 registros sem `text` (0 em kind nao isento)

- `armor`: 3
- `equipment`: 165
- isencao declarada: `equipment` -- objeto de tesouro (gema, obra de arte) nao tem texto de regra em fonte nenhuma -- so nome, nivel e preco
- isencao declarada: `armor` -- barding de montaria segue a tabela da armadura base, sem texto proprio

