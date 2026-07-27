# Portoes de qualidade -- fase `final`

- registros avaliados: **19738**

## Portao 1 -- prov por campo preenchido

**PASSOU** -- 0 ocorrencia(s).


## Portao 2 -- level divergente sem conflito

**PASSOU** -- 0 ocorrencia(s).


## Portao 3 -- requires citando id inexistente

**PASSOU** -- 0 ocorrencia(s).


## Portao 4 -- cobertura caindo vs build anterior

**PASSOU** -- 0 ocorrencia(s).


## Portao 5 -- license ausente

**PASSOU** -- 0 ocorrencia(s).


## Portao 6 -- traits disjunto apos uniao

**PASSOU** -- 0 ocorrencia(s).


## Portao 7 -- homonimo no mesmo kind

NAO SE APLICA nesta fase.

## Portao 8 -- artefato citado que sumiu do disco

**PASSOU** -- 0 ocorrencia(s).


## Portao 9 -- kind ausente vs censo do AoN

**PASSOU** -- 0 ocorrencia(s).

- 
_Ausencias ja decididas (5 categorias) -- visiveis, nao bloqueiam:_
- - `class-feature`: 163 de 531 vigentes do AoN nao estao na base -- Alchemist Feats, Ancestry Feat, Ancestry Feats, Ancestry Feats, Ancestry Feats, Ancestry Feats -- 159 dos 163 sao LINHA DE TABELA DE PROGRESSAO, nao conteudo: 'Attribute Boosts' (20x, uma por classe), 'Initial Proficiencies' (20x), 'Skill Feats' (20x), 'Skill Increases' (20x), 'Ancestry and Background' (19x), 'General Feats' (19x), 'Ancestry Feats' (19x) e '<Classe> Feats'. A base modela isso dentro de `class.progressao`, nao como registro proprio -- ausencia por design. Os 4 restantes sao class-features de verdade e estao no TODO 55: Incredible Senses, Lightning Reflexes, Premonition's Reflexes, Vigilant Senses
- - `class-kit`: 32 de 32 vigentes do AoN nao estao na base -- Alchemist Kit, Alchemist Kit, Barbarian Kit, Barbarian Kit, Bard Kit, Bard Kit -- kind nunca extraido -- os 32 kits de equipamento inicial do AoN. Trabalho real, TODO 54
- - `feat`: 5 de 6085 vigentes do AoN nao estao na base -- Dad Joke, GGGHhhjjjJJK, Wombat Bastion, Wombat Burrow, Wombat Style -- entradas de piada do proprio AoN (Dad Joke, GGGHhhjjjJJK, Wombat Bastion/Burrow/Style). Nao sao conteudo de jogo
- - `heritage`: 3 de 335 vigentes do AoN nao estao na base -- Half-Elf, Half-Orc, Three Kobolds in a Trench Coat -- Half-Elf e Half-Orc sao os nomes legado de Aiuvarin e Dromaar, que estao na base com o nome remaster e o AoN nao ligou por remaster_id. 'Three Kobolds in a Trench Coat' e ausencia real, TODO 55
- - `tactic`: 35 de 37 vigentes do AoN nao estao na base -- Alley-oop, Bloody Guillotine, Buckle-cut blitz, Coordinating Maneuvers, Corpse Crenellation, Cry Havoc! -- kind nunca extraido -- as 37 tacticas do Commander (Battlecry!). Trabalho real, TODO 54. Duas ja aparecem por homonimo com outro kind, entao o portao lista 35

