# Portoes de qualidade -- fase `pre-fusao`

- registros avaliados: **18773**

## Portao 1 -- prov por campo preenchido

**FALHOU** -- 2703 ocorrencia(s).

- `text`: 2703 sem prov (ex.: wb:class/alchemist, wb:class/animist, wb:class/barbarian, wb:class/bard, wb:class/champion)

## Portao 2 -- level divergente sem conflito

**PASSOU** -- 0 ocorrencia(s).


## Portao 3 -- requires citando id inexistente

NAO SE APLICA nesta fase.

## Portao 4 -- cobertura caindo vs build anterior

NAO SE APLICA nesta fase.

## Portao 5 -- license ausente

**FALHOU** -- 6 ocorrencia(s).

- `wb:armor/heavy-power-suit`
- `wb:armor/hide`
- `wb:armor/leather`
- `wb:armor/studded-leather`
- `wb:weapon/nine-ring-sword`
- `wb:weapon/wind-and-fire-wheel`

## Portao 6 -- traits disjunto apos uniao

**PASSOU** -- 0 ocorrencia(s).


## Portao 7 -- homonimo no mesmo kind

**FALHOU** -- 159 ocorrencia(s).

- **COLISAO** `wb:feat/breath-of-the-dragon` casou com `feat-1945` mas o AoN tem 2 entidades: feat-1945(nv8,Archetype); feat-5730(nv1,Dragonblood,Magical)
- **COLISAO** `wb:feat/current-spell` casou com `feat-4344` mas o AoN tem 2 entidades: feat-1714(nv6,Abjuration,Concentrate,Druid); feat-4344(nv6,Archetype,Concentrate,Spells)
- **COLISAO** `wb:feat/daywalker` casou com `feat-2352` mas o AoN tem 2 entidades: feat-2352(nv13,Dhampir); feat-3549(nv6,Abjuration,Archetype,Divine)
- **COLISAO** `wb:feat/death-from-above` casou com `feat-7380` mas o AoN tem 2 entidades: feat-7380(nv16,Mythic); feat-7610(nv8,Archetype,Uncommon)
- **COLISAO** `wb:feat/draconic-scent` casou com `feat-5737` mas o AoN tem 2 entidades: feat-1942(nv4,Archetype); feat-5737(nv5,Dragonblood)
- **COLISAO** `wb:feat/even-the-odds` casou com `feat-7675` mas o AoN tem 2 entidades: feat-6145(nv4,Swashbuckler); feat-7675(nv14,Archetype,Fortune)
- **COLISAO** `wb:feat/hellknight-dedication` casou com `feat-8812` mas o AoN tem 2 entidades: feat-1078(nv6,Archetype,Dedication,Uncommo); feat-8812(nv2,Archetype,Dedication,Uncommo)
- **COLISAO** `wb:feat/jellyfish-stance` casou com `feat-4077` mas o AoN tem 2 entidades: feat-2729(nv6,Monk,Stance,Uncommon); feat-4077(nv8,Monk,Stance,Uncommon)
- **COLISAO** `wb:feat/know-it-all` casou com `feat-4607` mas o AoN tem 2 entidades: feat-197(nv8,Bard,Thaumaturge); feat-2664(nv10,Archetype)
- **COLISAO** `wb:feat/many-guises` casou com `feat-6883` mas o AoN tem 2 entidades: feat-2091(nv8,Archetype); feat-6883(nv9,Kitsune)
- **COLISAO** `wb:feat/master-of-many-styles` casou com `feat-4850` mas o AoN tem 2 entidades: feat-480(nv16,Monk); feat-4850(nv16,Fighter,Monk)
- **COLISAO** `wb:feat/play-to-the-crowd` casou com `feat-7637` mas o AoN tem 2 entidades: feat-1978(nv4,Archetype,Concentrate); feat-7637(nv12,Archetype,Skill,Uncommon)
- **COLISAO** `wb:feat/rain-of-embers-stance` casou com `feat-2269` mas o AoN tem 2 entidades: feat-936(nv1,Monk,Rare,Stance); feat-2269(nv1,Fire,Monk,Rare,Stance)
- **COLISAO** `wb:feat/rallying-charge` casou com `feat-7750` mas o AoN tem 2 entidades: feat-2011(nv6,Archetype,Open,Visual); feat-7750(nv16,Archetype)
- **COLISAO** `wb:feat/riptide` casou com `feat-2679` mas o AoN tem 2 entidades: feat-2679(nv9,Azarketi); feat-8923(nv8,Archetype,Attack,Manipulate)
- **COLISAO** `wb:feat/sixth-pillar-mastery` casou com `feat-4078` mas o AoN tem 2 entidades: feat-2742(nv16,Archetype); feat-4078(nv14,Archetype)
- **COLISAO** `wb:feat/spell-mastery` casou com `feat-5055` mas o AoN tem 2 entidades: feat-1169(nv20,Uncommon,Wizard); feat-1843(nv20,Wizard)
- **COLISAO** `wb:feat/touch-focus` casou com `feat-4079` mas o AoN tem 2 entidades: feat-2743(nv14,Archetype,Manipulate,Metamag); feat-4079(nv16,Archetype,Manipulate,Metamag)
- **COLISAO** `wb:feat/tusks` casou com `feat-4519` mas o AoN tem 2 entidades: feat-963(nv1,Half-Orc,Dromaar); feat-1286(nv1,Orc)
- **COLISAO** `wb:feat/ultimate-flexibility` casou com `feat-4858` mas o AoN tem 2 entidades: feat-1171(nv20,Fighter,Uncommon); feat-1732(nv20,Fighter)
- **COLISAO** `wb:feat/unstoppable-juggernaut` casou com `feat-5880` mas o AoN tem 2 entidades: feat-1167(nv20,Barbarian,Uncommon); feat-1631(nv20,Barbarian)
- **COLISAO** `wb:feat/voice-of-the-elements` casou com `feat-8082` mas o AoN tem 2 entidades: feat-4188(nv2,Kineticist); feat-8082(nv5,Dragonblood)
- **COLISAO** `wb:feat/watch-your-back` casou com `feat-4948` mas o AoN tem 2 entidades: feat-1794(nv6,Emotion,Fear,Mental,Rogue); feat-8845(nv14,Archetype,Auditory,Linguisti)
- **COLISAO** `wb:feat/water-step` casou com `feat-6007` mas o AoN tem 2 entidades: feat-455(nv6,Monk); feat-4351(nv8,Archetype)
- **COLISAO** `wb:spell/object-reading` casou com `spell-2012` mas o AoN tem 2 entidades: spell-553(nv1,Divination,Uncommon); spell-705(nv1,Divination)
- **COLISAO** `wb:spell/pillar-of-water` casou com `spell-1394` mas o AoN tem 2 entidades: spell-646(nv3,Evocation,Uncommon,Water); spell-1394(nv3,Concentrate,Manipulate,Water)
- **COLISAO** `wb:spell/powerful-inhalation` casou com `spell-1305` mas o AoN tem 2 entidades: spell-1054(nv3,Air,Druid,Evocation,Uncommon); spell-1305(nv3,Air,Concentrate,Druid,Focus,)
- **COLISAO** `wb:spell/practice-makes-perfect` casou com `spell-2417` mas o AoN tem 2 entidades: spell-559(nv1,Cleric,Divination,Uncommon,F); spell-1346(nv1,Focus,Manipulate,Uncommon)
- **COLISAO** `wb:spell/pulverizing-cascade` casou com `spell-1311` mas o AoN tem 2 entidades: spell-1055(nv3,Druid,Evocation,Uncommon,Wat); spell-1311(nv3,Concentrate,Druid,Focus,Mani)
- **COLISAO** `wb:spell/rising-surf` casou com `spell-1310` mas o AoN tem 2 entidades: spell-1056(nv1,Conjuration,Druid,Move,Uncom); spell-1310(nv1,Druid,Focus,Manipulate,Move,)
- **COLISAO** `wb:spell/stone-lance` casou com `spell-1307` mas o AoN tem 2 entidades: spell-1057(nv3,Attack,Druid,Earth,Evocation); spell-1307(nv3,Attack,Concentrate,Druid,Ear)
- **COLISAO** `wb:spell/time-beacon` casou com `spell-2609` mas o AoN tem 2 entidades: spell-592(nv7,Divination); spell-2609(nv7,Manipulate)
- **COLISAO** `wb:spell/tireless-worker` casou com `spell-2418` mas o AoN tem 2 entidades: spell-560(nv4,Healing,Necromancy,Focus); spell-1347(nv4,Concentrate,Focus,Healing,Ma)
- **COLISAO** `wb:spell/updraft` casou com `spell-1304` mas o AoN tem 2 entidades: spell-1058(nv1,Air,Druid,Evocation,Uncommon); spell-1304(nv1,Air,Concentrate,Druid,Focus,)
- **COLISAO** `wb:spell/verdant-sprout` casou com `spell-1413` mas o AoN tem 2 entidades: spell-641(nv1,Conjuration,Plant,Uncommon); spell-1413(nv1,Concentrate,Manipulate,Plant)
- **COLISAO** `wb:spell/wildfire` casou com `spell-1308` mas o AoN tem 2 entidades: spell-1059(nv1,Conjuration,Druid,Fire,Uncom); spell-1308(nv1,Concentrate,Druid,Fire,Focus)
- **COLISAO** `wb:spell/combustion` casou com `spell-1309` mas o AoN tem 2 entidades: spell-1052(nv3,Druid,Evocation,Fire,Uncommo); spell-1309(nv3,Concentrate,Druid,Fire,Focus)
- **COLISAO** `wb:spell/crushing-ground` casou com `spell-1306` mas o AoN tem 2 entidades: spell-1053(nv1,Druid,Earth,Transmutation,Un); spell-1306(nv1,Concentrate,Druid,Earth,Focu)
- **COLISAO** `wb:spell/imprint-message` casou com `spell-2003` mas o AoN tem 2 entidades: spell-551(nv1,Divination,Uncommon); spell-698(nv1,Divination)
- **COLISAO** `wb:equipment/alchemist-goggles` casou com `equipment-3431` mas o AoN tem 3 entidades: equipment-408(nv0,Invested,Magical,Transmutati); equipment-3431(nv4,Invested,Magical); equipment-3431-3299(nv4,Invested,Magical)
- 
- _Alem disso, 417 casos de mesmo level e mesmos traits -- par legacy/remaster que o AoN nao declarou via `remaster_id`. Fusao legitima, nao bloqueia o build._
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

