# Portoes de qualidade -- fase `pre-fusao`

- registros avaliados: **19896**

## Portao 1 -- prov por campo preenchido

**PASSOU** -- 0 ocorrencia(s).


## Portao 2 -- level divergente sem conflito

**PASSOU** -- 0 ocorrencia(s).


## Portao 3 -- requires citando id inexistente

NAO SE APLICA nesta fase.

## Portao 4 -- cobertura caindo vs build anterior

NAO SE APLICA nesta fase.

## Portao 5 -- license ausente

**FALHOU** -- 3 ocorrencia(s).

- `wb:armor/heavy-power-suit`
- `wb:weapon/nine-ring-sword`
- `wb:weapon/wind-and-fire-wheel`

## Portao 6 -- traits disjunto apos uniao

**FALHOU** -- 1 ocorrencia(s).

- `wb:weapon/leiomano`: [['fatal-d10', 'versatile-s'], ['fatal', 'uncommon', 'versatile']]

## Portao 7 -- homonimo no mesmo kind

**FALHOU** -- 13 ocorrencia(s).

- **COLISAO** `wb:feat/know-it-all` casou com `feat-4607` mas o AoN tem 2 entidades: feat-197(nv8,Bard,Thaumaturge); feat-2664(nv10,Archetype)
- **COLISAO** `wb:feat/spell-mastery` casou com `feat-5055` mas o AoN tem 2 entidades: feat-1169(nv20,Uncommon,Wizard); feat-1843(nv20,Wizard)
- **COLISAO** `wb:feat/tusks` casou com `feat-4519` mas o AoN tem 2 entidades: feat-963(nv1,Half-Orc,Dromaar); feat-1286(nv1,Orc)
- **COLISAO** `wb:feat/ultimate-flexibility` casou com `feat-4858` mas o AoN tem 2 entidades: feat-1171(nv20,Fighter,Uncommon); feat-1732(nv20,Fighter)
- **COLISAO** `wb:feat/unstoppable-juggernaut` casou com `feat-5880` mas o AoN tem 2 entidades: feat-1167(nv20,Barbarian,Uncommon); feat-1631(nv20,Barbarian)
- **COLISAO** `wb:feat/watch-your-back` casou com `feat-4948` mas o AoN tem 2 entidades: feat-1794(nv6,Emotion,Fear,Mental,Rogue); feat-8845(nv14,Archetype,Auditory,Linguisti)
- **COLISAO** `wb:feat/water-step` casou com `feat-6007` mas o AoN tem 2 entidades: feat-455(nv6,Monk); feat-4351(nv8,Archetype)
- **COLISAO** `wb:spell/object-reading` casou com `spell-2012` mas o AoN tem 2 entidades: spell-553(nv1,Divination,Uncommon); spell-705(nv1,Divination)
- **COLISAO** `wb:spell/practice-makes-perfect` casou com `spell-2417` mas o AoN tem 2 entidades: spell-559(nv1,Cleric,Divination,Uncommon,F); spell-1346(nv1,Focus,Manipulate,Uncommon)
- **COLISAO** `wb:spell/tireless-worker` casou com `spell-2418` mas o AoN tem 2 entidades: spell-560(nv4,Healing,Necromancy,Focus); spell-1347(nv4,Concentrate,Focus,Healing,Ma)
- **COLISAO** `wb:spell/imprint-message` casou com `spell-2003` mas o AoN tem 2 entidades: spell-551(nv1,Divination,Uncommon); spell-698(nv1,Divination)
- **COLISAO** `wb:equipment/brimstone-fumes` casou com `equipment-3327` mas o AoN tem 2 entidades: equipment-109(nv16,Alchemical,Consumable,Evil,I); equipment-2895(nv16,Alchemical,Consumable,Inhale)
- **COLISAO** `wb:equipment/lethargy-poison` casou com `equipment-3340` mas o AoN tem 2 entidades: equipment-120(nv2,Alchemical,Consumable,Incapa); equipment-2902(nv2,Alchemical,Consumable,Incapa)
- 
- _Alem disso, 435 casos de mesmo level e mesmos traits -- par legacy/remaster que o AoN nao declarou via `remaster_id`. Fusao legitima, nao bloqueia o build._
- - `wb:feat/advanced-monastic-weaponry` casou com `feat-7108` mas o AoN tem 2 entidades: feat-5997(nv6,Monk); feat-7108(nv6,Monk)
- - `wb:feat/banshee-cry-display` casou com `feat-8533` mas o AoN tem 2 entidades: feat-3250(nv12,Archetype); feat-8533(nv12,Archetype)
- - `wb:feat/coughing-dragon-display` casou com `feat-8529` mas o AoN tem 2 entidades: feat-3246(nv4,Archetype); feat-8529(nv4,Archetype)
- - `wb:feat/cross-the-final-horizon` casou com `feat-2205` mas o AoN tem 2 entidades: feat-2205(nv20,Archetype,Electricity,Evocat); feat-8811(nv20,Archetype,Electricity,Evocat)
- - `wb:feat/expert-fireworks-crafter` casou com `feat-8530` mas o AoN tem 2 entidades: feat-3247(nv6,Archetype); feat-8530(nv6,Archetype)
- - `wb:feat/firework-technician-dedication` casou com `feat-8528` mas o AoN tem 2 entidades: feat-3245(nv2,Archetype,Dedication,Uncommo); feat-8528(nv2,Archetype,Dedication,Uncommo)
- - `wb:feat/form-lock` casou com `feat-6031` mas o AoN tem 2 entidades: feat-1753(nv14,Attack,Monk); feat-6031(nv14,Attack,Monk)
- - `wb:feat/goblin-jubilee-display` casou com `feat-8532` mas o AoN tem 2 entidades: feat-3249(nv10,Archetype); feat-8532(nv10,Archetype)
- - `wb:feat/heavens-thunder` casou com `feat-2199` mas o AoN tem 2 entidades: feat-2199(nv6,Archetype,Electricity,Evocat); feat-8806(nv6,Archetype,Electricity,Evocat)
- - `wb:feat/jalmeri-heavenseeker-dedication` casou com `feat-2198` mas o AoN tem 2 entidades: feat-2198(nv4,Archetype,Dedication,Uncommo); feat-8805(nv4,Archetype,Dedication,Uncommo)
- - `wb:feat/jumping-jenny-display` casou com `feat-8531` mas o AoN tem 2 entidades: feat-3248(nv8,Archetype); feat-8531(nv8,Archetype)
- - `wb:feat/keep-pace` casou com `feat-3427` mas o AoN tem 2 entidades: feat-1917(nv6,Archetype); feat-3427(nv6,Archetype)
- - `wb:feat/master-spotter` casou com `feat-3124` mas o AoN tem 2 entidades: feat-3124(nv12,Archetype); feat-6209(nv12,Archetype)
- - `wb:feat/necromantic-resistance` casou com `feat-3477` mas o AoN tem 2 entidades: feat-884(nv4,Archetype); feat-3477(nv4,Archetype)
- - `wb:feat/sky-and-heaven-stance` casou com `feat-2200` mas o AoN tem 2 entidades: feat-2200(nv6,Archetype,Stance); feat-8807(nv6,Archetype,Stance)

