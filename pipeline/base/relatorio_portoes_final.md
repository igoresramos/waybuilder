# Portoes de qualidade -- fase `final`

- registros avaliados: **19599**

## Portao 1 -- prov por campo preenchido

**PASSOU** -- 0 ocorrencia(s).


## Portao 2 -- level divergente sem conflito

**PASSOU** -- 0 ocorrencia(s).


## Portao 3 -- requires citando id inexistente

**PASSOU** -- 0 ocorrencia(s).

- por campo: {'favored_weapon': 1}
- `wb:weapon/light-crossbow` citado 1x
- toleradas (inconsistencia da fonte): ['wb:weapon/light-crossbow']

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
_Cobertura por raridade (AoN vigente em escopo):_
- - `common`: 12264 de 12491 na base (98.2%)
- - `uncommon`: 4212 de 4212 na base (100.0%)
- - `rare`: 1449 de 1449 na base (100.0%)
- - `unique`: 240 de 240 na base (100.0%)
- 
_Ausencias ja decididas (3 categorias) -- visiveis, nao bloqueiam:_
- - `class-feature`: 219 de 721 vigentes do AoN nao estao na base -- Alchemist Feats, Ancestry And Background, Ancestry And Background, Ancestry And Background, Ancestry Feat, Ancestry Feats -- 214 dos 219 sao LINHA DE TABELA DE PROGRESSAO, nao conteudo ('Attribute Boosts', 'Initial Proficiencies', 'Skill Feats', 'Skill Increases', 'Ancestry and Background', 'General Feats', '<Classe> Feats'), que a base modela dentro de `class.progressao`. Os 5 restantes sao class-features de verdade e estao no TODO 55: Incredible Senses, Lightning Reflexes (2 docs), Premonition's Reflexes, Vigilant Senses
- - `feat`: 5 de 6085 vigentes do AoN nao estao na base -- Dad Joke, GGGHhhjjjJJK, Wombat Bastion, Wombat Burrow, Wombat Style -- entradas de piada do proprio AoN (Dad Joke, GGGHhhjjjJJK, Wombat Bastion/Burrow/Style). Nao sao conteudo de jogo
- - `heritage`: 3 de 335 vigentes do AoN nao estao na base -- Half-Elf, Half-Orc, Three Kobolds in a Trench Coat -- As 3 sao herancas LEGADAS que o Remaster aposentou e que a fonte fixada do Foundry (pin 87f9e502) nao contem mais: Half-Elf virou Aiuvarin, Half-Orc virou Dromaar, e 'Three Kobolds in a Trench Coat' e piada de AP. O AoN ainda as lista como vigentes porque mantem o conteudo legado. Foram 20 registros de heranca legada que sairam da base em 2026-07-30, quando `extratores/ancestrias.py` voltou a ser rodado: a saida em disco estava parada em 27/07, de antes da fixacao da fonte, e carregava herancas que a fonte pinada nao produz. Terceira ocorrencia do mesmo padrao (taticas_kits fora do laco, magias.py no-op) e a que mais escondeu: a saida velha tambem mascarava que o extrator nunca migrou para o schema v2.

## Portao 10 -- cobertura de grants_completos

**PASSOU** -- 0 ocorrencia(s).

- registros SEM resposta de `grants_completos`: **0** de 19599 (0.0%)
- linha de base anterior: 0

