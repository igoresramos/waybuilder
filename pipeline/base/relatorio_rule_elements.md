# Rule Elements convertidos

Das 176 opcoes de sub-escolha de classe, 175 nao tinham efeito
estruturado -- escolher a subclasse nao mudava numero nenhum. O dado
existia nos Rule Elements do Foundry.

Convertido apenas o **declarativo**: `ActiveEffectLike` com path de
rank e sem `predicate`. O resto depende do interpretador do Foundry
(`item:trait:finesse`, `self:effect:rage`, `@actor.flags`) e fica como
prosa -- que pelo principio zero **nao e lacuna**.

- registros que ganharam efeito: **99**
- grants adicionados: **123**

## Nao convertidos

- FlatModifier: precisa do interpretador: 1793
- ItemAlteration: precisa do interpretador: 1497
- GrantItem: precisa do interpretador: 1120
- RollOption: precisa do interpretador: 1079
- ActiveEffectLike sem path de rank: 604
- ChoiceSet: precisa do interpretador: 568
- Note: precisa do interpretador: 540
- Resistance: precisa do interpretador: 338
- ActiveEffectLike com predicate: 263
- DamageDice: precisa do interpretador: 254
- AdjustDegreeOfSuccess: precisa do interpretador: 239
- AdjustModifier: precisa do interpretador: 227
- Strike: precisa do interpretador: 201
- BaseSpeed: precisa do interpretador: 172
- Aura: precisa do interpretador: 126
- Sense: precisa do interpretador: 109
- MartialProficiency: precisa do interpretador: 108
- CriticalSpecialization: precisa do interpretador: 99
- TokenLight: precisa do interpretador: 98
- AdjustStrike: precisa do interpretador: 94
- DamageAlteration: precisa do interpretador: 87
- ActorTraits: precisa do interpretador: 59
- valor de rank nao literal: 58
- TokenEffectIcon: precisa do interpretador: 47
- EphemeralEffect: precisa do interpretador: 29
- CreatureSize: precisa do interpretador: 24
- CraftingAbility: precisa do interpretador: 21
- Immunity: precisa do interpretador: 21
- Weakness: precisa do interpretador: 19
- SpecialStatistic: precisa do interpretador: 12
- DexterityModifierCap: precisa do interpretador: 12
- SubstituteRoll: precisa do interpretador: 8
- MultipleAttackPenalty: precisa do interpretador: 7
- RollTwice: precisa do interpretador: 7
- SpecialResource: precisa do interpretador: 6
- FastHealing: precisa do interpretador: 5
- TempHP: precisa do interpretador: 2

## Exemplos

- `wb:class/alchemist` (Alchemist): `[{"proficiency": {"weapon-base-alchemical-bomb": "trained"}}]`
- `wb:class-feature/alchemical-sciences-methodology` (Alchemical Sciences Methodology): `[{"proficiency": {"crafting": "trained"}}]`
- `wb:class-feature/alchemical-weapon-expertise` (Alchemical Weapon Expertise): `[{"proficiency": {"weapon-base-alchemical-bomb": "expert"}}]`
- `wb:class-feature/alchemical-weapon-mastery` (Alchemical Weapon Mastery): `[{"proficiency": {"weapon-base-alchemical-bomb": "master"}}]`
- `wb:class-feature/ancestors` (Ancestors): `[{"proficiency": {"society": "trained"}}]`
- `wb:class-feature/angel-eidolon` (Angel Eidolon): `[{"proficiency": {"diplomacy": "trained"}}, {"proficiency": {"religion": "trained"}}]`
- `wb:class-feature/anger-phantom-eidolon` (Anger Phantom Eidolon): `[{"proficiency": {"intimidation": "trained"}}, {"proficiency": {"occultism": "trained"}}]`
- `wb:class-feature/ashes` (Ashes): `[{"proficiency": {"occultism": "trained"}}]`
