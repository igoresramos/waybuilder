# Mecanica de equipamento recuperada

Nao era falta de fonte -- era falha de matching. Duas causas: o Foundry escreve `Leather Armor` onde o AoN escreve `Leather`, e as armas universais (`Fist`, `Shield Bash`) nao existem como arquivo no Foundry, so no dump do AoN.

- registros curados por fonte: **1**
- herdados do item base (`Base Armor X` no texto): **10**
- ainda sem o campo critico: **64**

## Herdados

| id | nome | kind | herda de | campos |
|---|---|---|---|---|
| `wb:armor/breastplate-of-command` | Breastplate of Command | armor | Breastplate | bulk, price_cp, base_item, armor_category, group, ac_bonus, dex_cap, check_penalty, speed_penalty, strength |
| `wb:armor/celestial-armor` | Celestial Armor | armor | Chain Mail | bulk, price_cp, base_item, armor_category, group, ac_bonus, dex_cap, check_penalty, speed_penalty, strength |
| `wb:armor/demon-armor` | Demon Armor | armor | Full Plate | bulk, price_cp, base_item, armor_category, group, ac_bonus, dex_cap, check_penalty, speed_penalty, strength |
| `wb:armor/remorhaz-armor` | Remorhaz Armor | armor | Niyaháat | bulk, price_cp, base_item, armor_category, group, ac_bonus, dex_cap, check_penalty, speed_penalty, strength, conflitos |
| `wb:armor/rhino-hide` | Rhino Hide | armor | Hide | ac_bonus, dex_cap, check_penalty, speed_penalty, strength, armor_category, group |
| `wb:shield/highhelm-war-shield` | Highhelm War Shield | shield | Razor Disc | bulk, price_cp, base_item, ac_bonus, hardness, hp, bt, speed_penalty |
| `wb:shield/sturdy-shield` | Sturdy Shield | shield | Steel Shield | bulk, price_cp, base_item, ac_bonus, hardness, hp, bt, speed_penalty |
| `wb:weapon/dagger-of-venom` | Dagger of Venom | weapon | Dagger | bulk, price_cp, usage, base_item, weapon_category, group, damage, hands |
| `wb:weapon/flame-tongue` | Flame Tongue | weapon | Longsword | bulk, price_cp, usage, base_item, weapon_category, group, damage, hands |
| `wb:weapon/holy-avenger` | Holy Avenger | weapon | Longsword | bulk, price_cp, usage, base_item, weapon_category, group, damage, hands |

## Curados

| id | nome | kind | fonte | campos |
|---|---|---|---|---|
| `wb:armor/unarmored` | Unarmored | armor | definicao | ac_bonus, armor_category |

## Ainda sem

| id | nome | kind |
|---|---|---|
| `wb:armor/elven-chain` | Elven Chain | armor |
| `wb:armor/grisantian-pelt-armor` | Grisantian Pelt Armor | armor |
| `wb:armor/heavy-power-suit` | Heavy Power Suit | armor |
| `wb:armor/lions-pelt` | Lion's Pelt | armor |
| `wb:armor/sovereign-steel-armor` | Sovereign Steel Armor | armor |
| `wb:shield/dragonhide-shield` | Dragonhide Shield | shield |
| `wb:shield/mithral-shield` | Mithral Shield | shield |
| `wb:shield/noqual-shield` | Noqual Shield | shield |
| `wb:shield/orichalcum-shield` | Orichalcum Shield | shield |
| `wb:shield/siccatite-shield` | Siccatite Shield | shield |
| `wb:weapon/acid-flask-greater` | Acid Flask (Greater) | weapon |
| `wb:weapon/acid-flask-lesser` | Acid Flask (Lesser) | weapon |
| `wb:weapon/acid-flask-major` | Acid Flask (Major) | weapon |
| `wb:weapon/acid-flask-moderate` | Acid Flask (Moderate) | weapon |
| `wb:weapon/alchemical-bomb` | Alchemical Bomb | weapon |
| `wb:weapon/atrophy-bomb-greater` | Atrophy Bomb (Greater) | weapon |
| `wb:weapon/atrophy-bomb-lesser` | Atrophy Bomb (Lesser) | weapon |
| `wb:weapon/atrophy-bomb-major` | Atrophy Bomb (Major) | weapon |
| `wb:weapon/atrophy-bomb-moderate` | Atrophy Bomb (Moderate) | weapon |
| `wb:weapon/bioluminescence-bomb` | Bioluminescence Bomb | weapon |
| `wb:weapon/blood-bomb-greater` | Blood Bomb (Greater) | weapon |
| `wb:weapon/blood-bomb-lesser` | Blood Bomb (Lesser) | weapon |
| `wb:weapon/blood-bomb-major` | Blood Bomb (Major) | weapon |
| `wb:weapon/blood-bomb-moderate` | Blood Bomb (Moderate) | weapon |
| `wb:weapon/blowgun` | Blowgun | weapon |
| `wb:weapon/bolts-phalanx-piercer` | Bolts (Phalanx Piercer) | weapon |
| `wb:weapon/dart-umbrella` | Dart Umbrella | weapon |
| `wb:weapon/drake-rifle` | Drake Rifle | weapon |
| `wb:weapon/firearm-ammunition-10-rounds` | Firearm Ammunition (10 rounds) | weapon |
| `wb:weapon/firearm-ammunition-5-rounds` | Firearm Ammunition (5 rounds) | weapon |
| `wb:weapon/glue-bomb-greater` | Glue Bomb (Greater) | weapon |
| `wb:weapon/glue-bomb-lesser` | Glue Bomb (Lesser) | weapon |
| `wb:weapon/glue-bomb-major` | Glue Bomb (Major) | weapon |
| `wb:weapon/glue-bomb-moderate` | Glue Bomb (Moderate) | weapon |
| `wb:weapon/magazine-air-repeater` | Magazine (Air Repeater) | weapon |
| `wb:weapon/magazine-long-air-repeater` | Magazine (Long Air Repeater) | weapon |
| `wb:weapon/nine-ring-sword` | Nine-Ring Sword | weapon |
| `wb:weapon/orichalcum-weapon` | Orichalcum Weapon | weapon |
| `wb:weapon/pernicious-spore-bomb-greater` | Pernicious Spore Bomb (Greater) | weapon |
| `wb:weapon/pernicious-spore-bomb-lesser` | Pernicious Spore Bomb (Lesser) | weapon |
| `wb:weapon/pernicious-spore-bomb-major` | Pernicious Spore Bomb (Major) | weapon |
| `wb:weapon/pernicious-spore-bomb-moderate` | Pernicious Spore Bomb (Moderate) | weapon |
| `wb:weapon/redpitch-bomb-greater` | Redpitch Bomb (Greater) | weapon |
| `wb:weapon/redpitch-bomb-lesser` | Redpitch Bomb (Lesser) | weapon |
| `wb:weapon/redpitch-bomb-major` | Redpitch Bomb (Major) | weapon |
| `wb:weapon/redpitch-bomb-moderate` | Redpitch Bomb (Moderate) | weapon |
| `wb:weapon/silver-orb-greater` | Silver Orb (Greater) | weapon |
| `wb:weapon/silver-orb-lesser` | Silver Orb (Lesser) | weapon |
| `wb:weapon/silver-orb-powder` | Silver Orb (Powder) | weapon |
| `wb:weapon/spider-satchel-greater` | Spider Satchel (Greater) | weapon |
| `wb:weapon/spider-satchel-lesser` | Spider Satchel (Lesser) | weapon |
| `wb:weapon/spider-satchel-major` | Spider Satchel (Major) | weapon |
| `wb:weapon/spider-satchel-moderate` | Spider Satchel (Moderate) | weapon |
| `wb:weapon/spray-pellet` | Spray Pellet | weapon |
| `wb:weapon/steelscour-greater` | Steelscour (greater) | weapon |
| `wb:weapon/steelscour-lesser` | Steelscour (lesser) | weapon |
| `wb:weapon/steelscour-major` | Steelscour (major) | weapon |
| `wb:weapon/steelscour-moderate` | Steelscour (moderate) | weapon |
| `wb:weapon/tallow-bomb-greater` | Tallow Bomb (Greater) | weapon |
| `wb:weapon/tallow-bomb-lesser` | Tallow Bomb (Lesser) | weapon |
| `wb:weapon/tallow-bomb-major` | Tallow Bomb (Major) | weapon |
| `wb:weapon/tallow-bomb-moderate` | Tallow Bomb (Moderate) | weapon |
| `wb:weapon/water-bomb-lesser` | Water Bomb (Lesser) | weapon |
| `wb:weapon/wind-and-fire-wheel` | Wind and Fire Wheel | weapon |
