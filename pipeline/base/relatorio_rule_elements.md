# Rule Elements convertidos

Das 176 opcoes de sub-escolha de classe, 175 nao tinham efeito
estruturado -- escolher a subclasse nao mudava numero nenhum. O dado
existia nos Rule Elements do Foundry.

Convertido apenas o **declarativo**: `ActiveEffectLike` com path de
rank e sem `predicate`. O resto depende do interpretador do Foundry
(`item:trait:finesse`, `self:effect:rage`, `@actor.flags`) e fica como
prosa -- que pelo principio zero **nao e lacuna**.

- registros que ganharam efeito: **464**
- grants adicionados: **556**

## Nao convertidos

- FlatModifier: precisa do interpretador: 1823
- ItemAlteration: precisa do interpretador: 1497
- RollOption: precisa do interpretador: 1091
- ActiveEffectLike sem path de rank: 634
- ChoiceSet: precisa do interpretador: 623
- Note: precisa do interpretador: 543
- Resistance: precisa do interpretador: 341
- GrantItem com predicate: 293
- GrantItem sem alvo na base: 290
- ActiveEffectLike com predicate: 269
- DamageDice: precisa do interpretador: 255
- AdjustDegreeOfSuccess: precisa do interpretador: 240
- AdjustModifier: precisa do interpretador: 228
- Strike: precisa do interpretador: 201
- GrantItem com UUID dinamico (escolha do jogador): 184
- BaseSpeed: precisa do interpretador: 173
- Aura: precisa do interpretador: 126
- MartialProficiency: precisa do interpretador: 111
- Sense: precisa do interpretador: 110
- CriticalSpecialization: precisa do interpretador: 100
- TokenLight: precisa do interpretador: 100
- AdjustStrike: precisa do interpretador: 94
- DamageAlteration: precisa do interpretador: 88
- ActorTraits: precisa do interpretador: 65
- valor de rank nao literal: 58
- TokenEffectIcon: precisa do interpretador: 47
- EphemeralEffect: precisa do interpretador: 29
- CreatureSize: precisa do interpretador: 24
- CraftingAbility: precisa do interpretador: 21
- Immunity: precisa do interpretador: 21
- Weakness: precisa do interpretador: 19
- GrantItem de condicao de combate (fora de escopo): 17
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
- `wb:class-feature/alchemical-sciences-methodology` (Alchemical Sciences Methodology): `[{"proficiency": {"crafting": "trained"}}, {"grant_feat": ["wb:feat/alchemical-crafting"]}, {"grant_feat": ["wb:equipment/formula-book-blank"]}]`
- `wb:class-feature/alchemical-weapon-expertise` (Alchemical Weapon Expertise): `[{"proficiency": {"weapon-base-alchemical-bomb": "expert"}}]`
- `wb:class-feature/alchemical-weapon-mastery` (Alchemical Weapon Mastery): `[{"proficiency": {"weapon-base-alchemical-bomb": "master"}}]`
- `wb:class-feature/alchemy` (Alchemy): `[{"grant_feat": ["wb:feat/alchemical-crafting"]}, {"grant_feat": ["wb:class-feature/formula-book"]}, {"grant_feat": ["wb:class-feature/advanced-alchemy"]}, {"grant_feat": ["wb:class-feature/versatile-vials"]}, {"grant_feat": ["wb:class-feature/quick-alchemy"]}]`
- `wb:class-feature/aloof-firmament` (Aloof Firmament): `[{"grant_feat": ["wb:feat/cat-fall"]}]`
- `wb:class-feature/amulet` (Amulet): `[{"grant_feat": ["wb:equipment/amulet-implement"]}]`
- `wb:class-feature/ancestors` (Ancestors): `[{"proficiency": {"society": "trained"}}, {"grant_feat": ["wb:class-feature/curse-of-ancestral-meddling"]}]`
