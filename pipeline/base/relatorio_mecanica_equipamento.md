# Mecanica de equipamento recuperada

Nao era falta de fonte -- era falha de matching. Duas causas: o Foundry escreve `Leather Armor` onde o AoN escreve `Leather`, e as armas universais (`Fist`, `Shield Bash`) nao existem como arquivo no Foundry, so no dump do AoN.

- registros curados por fonte: **67**
- herdados do item base (`Base Armor X` no texto): **0**
- ainda sem o campo critico: **67**

## Herdados

| id | nome | kind | herda de | campos |
|---|---|---|---|---|

## Curados

| id | nome | kind | fonte | campos |
|---|---|---|---|---|
| `wb:armor/hide` | Hide | armor | foundry | ac_bonus, dex_cap, check_penalty, speed_penalty, strength, armor_category, group |
| `wb:armor/leather` | Leather | armor | foundry | ac_bonus, dex_cap, check_penalty, speed_penalty, strength, armor_category, group |
| `wb:armor/studded-leather` | Studded Leather | armor | foundry | ac_bonus, dex_cap, check_penalty, speed_penalty, strength, armor_category, group |
| `wb:armor/unarmored` | Unarmored | armor | definicao | ac_bonus, armor_category |
| `wb:weapon/alchemical-bomb` | Alchemical Bomb | weapon | aon | weapon_category |
| `wb:weapon/aldori-dueling-sword-nv1` | Aldori Dueling Sword | weapon | foundry | damage, weapon_category, group |
| `wb:weapon/axe-musket-melee` | Axe Musket (Melee) | weapon | aon | damage, weapon_category |
| `wb:weapon/axe-musket-ranged` | Axe Musket (Ranged) | weapon | aon | damage, weapon_category |
| `wb:weapon/black-powder-knuckle-dusters-melee` | Black Powder Knuckle Dusters (Melee) | weapon | aon | damage, weapon_category |
| `wb:weapon/black-powder-knuckle-dusters-ranged` | Black Powder Knuckle Dusters (Ranged) | weapon | aon | damage, weapon_category |
| `wb:weapon/bola-nv0` | Bola | weapon | foundry | damage, weapon_category, group |
| `wb:weapon/bola-nv0-weapon-123` | Bola | weapon | foundry | damage, weapon_category, group |
| `wb:weapon/bola-nv0-weapon-331` | Bola | weapon | foundry | damage, weapon_category, group |
| `wb:weapon/bolts-phalanx-piercer` | Bolts (Phalanx Piercer) | weapon | aon | weapon_category |
| `wb:weapon/bow-staff-melee` | Bow Staff (Melee) | weapon | aon | damage, weapon_category |
| `wb:weapon/bow-staff-ranged` | Bow Staff (Ranged) | weapon | aon | damage, weapon_category |
| `wb:weapon/butterfly-sword-nv0` | Butterfly Sword | weapon | foundry | damage, weapon_category, group |
| `wb:weapon/cane-pistol-melee` | Cane Pistol (Melee) | weapon | aon | damage, weapon_category |
| `wb:weapon/cane-pistol-ranged` | Cane Pistol (Ranged) | weapon | aon | damage, weapon_category |
| `wb:weapon/chakri-recovery` | Chakri | weapon | foundry | damage, weapon_category, group |
| `wb:weapon/crescent-cross-melee` | Crescent Cross (Melee) | weapon | aon | damage, weapon_category |
| `wb:weapon/crescent-cross-ranged` | Crescent Cross (Ranged) | weapon | aon | damage, weapon_category |
| `wb:weapon/dagger-pistol-melee` | Dagger Pistol (Melee) | weapon | aon | damage, weapon_category |
| `wb:weapon/dagger-pistol-ranged` | Dagger Pistol (Ranged) | weapon | aon | damage, weapon_category |
| `wb:weapon/dwarven-waraxe` | Dwarven Waraxe | weapon | foundry | damage, weapon_category, group |
| `wb:weapon/explosive-dogslicer-melee` | Explosive Dogslicer (Melee) | weapon | aon | damage, weapon_category |
| `wb:weapon/explosive-dogslicer-ranged` | Explosive Dogslicer (Ranged) | weapon | aon | damage, weapon_category |
| `wb:weapon/firearm-ammunition-10-rounds` | Firearm Ammunition (10 rounds) | weapon | aon | weapon_category |
| `wb:weapon/firearm-ammunition-5-rounds` | Firearm Ammunition (5 rounds) | weapon | aon | weapon_category |
| `wb:weapon/fist` | Fist | weapon | aon | damage, weapon_category |
| `wb:weapon/gnome-amalgam-musket-melee` | Gnome Amalgam Musket (Melee) | weapon | aon | damage, weapon_category |
| `wb:weapon/gnome-amalgam-musket-ranged` | Gnome Amalgam Musket (Ranged) | weapon | aon | damage, weapon_category |
| `wb:weapon/gun-sword-melee` | Gun Sword (Melee) | weapon | aon | damage, weapon_category |
| `wb:weapon/gun-sword-ranged` | Gun Sword (Ranged) | weapon | aon | damage, weapon_category |
| `wb:weapon/hammer-gun-melee` | Hammer Gun (Melee) | weapon | aon | damage, weapon_category |
| `wb:weapon/hammer-gun-ranged` | Hammer Gun (Ranged) | weapon | aon | damage, weapon_category |
| `wb:weapon/jiu-huan-dao-disarm` | Jiu Huan Dao | weapon | foundry | damage, weapon_category, group |
| `wb:weapon/khakkara` | Khakkara | weapon | aon | damage, weapon_category |
| `wb:weapon/kursarigama` | Kursarigama | weapon | aon | damage, weapon_category |
| `wb:weapon/lancer-melee` | Lancer (Melee) | weapon | aon | damage, weapon_category |
| `wb:weapon/lancer-ranged` | Lancer (Ranged) | weapon | aon | damage, weapon_category |
| `wb:weapon/leiomano-deadly` | Leiomano | weapon | foundry | damage, weapon_category, group |
| `wb:weapon/mace-multipistol-melee` | Mace Multipistol (Melee) | weapon | aon | damage, weapon_category |
| `wb:weapon/mace-multipistol-ranged` | Mace Multipistol (Ranged) | weapon | aon | damage, weapon_category |
| `wb:weapon/magazine-air-repeater` | Magazine (Air Repeater) | weapon | aon | weapon_category |
| `wb:weapon/magazine-long-air-repeater` | Magazine (Long Air Repeater) | weapon | aon | weapon_category |
| `wb:weapon/mikazuki-melee` | Mikazuki (Melee) | weapon | aon | damage, weapon_category |
| `wb:weapon/mikazuki-ranged` | Mikazuki (Ranged) | weapon | aon | damage, weapon_category |
| `wb:weapon/mithral-tree` | Mithral Tree | weapon | aon | damage, weapon_category |
| `wb:weapon/piercing-wind-melee` | Piercing Wind (Melee) | weapon | aon | damage, weapon_category |
| `wb:weapon/piercing-wind-ranged` | Piercing Wind (Ranged) | weapon | aon | damage, weapon_category |
| `wb:weapon/rapier-pistol-melee` | Rapier Pistol (Melee) | weapon | aon | damage, weapon_category |
| `wb:weapon/rapier-pistol-ranged` | Rapier Pistol (Ranged) | weapon | aon | damage, weapon_category |
| `wb:weapon/reinforced-frame` | Reinforced Frame | weapon | aon | damage, weapon_category |
| `wb:weapon/repeating-hand-crossbow-nv0` | Repeating Hand Crossbow | weapon | foundry | damage, weapon_category, group |
| `wb:weapon/repeating-hand-crossbow-nv1` | Repeating Hand Crossbow | weapon | foundry | damage, weapon_category, group |
| `wb:weapon/rungu` | Rungu | weapon | aon | damage, weapon_category |
| `wb:weapon/shield-bash` | Shield Bash | weapon | aon | damage, weapon_category |
| `wb:weapon/spray-pellet` | Spray Pellet | weapon | aon | weapon_category |
| `wb:weapon/tekko-kagi-trip` | Tekko-kagi | weapon | foundry | damage, weapon_category, group |
| `wb:weapon/three-peaked-tree-melee` | Three Peaked Tree (Melee) | weapon | aon | damage, weapon_category |
| `wb:weapon/three-peaked-tree-ranged` | Three Peaked Tree (Ranged) | weapon | aon | damage, weapon_category |
| `wb:weapon/throwing-knife-uncommon` | Throwing Knife | weapon | foundry | damage, weapon_category, group |
| `wb:weapon/triggerbrand-melee` | Triggerbrand (Melee) | weapon | aon | damage, weapon_category |
| `wb:weapon/triggerbrand-ranged` | Triggerbrand (Ranged) | weapon | aon | damage, weapon_category |
| `wb:weapon/wrecker-melee` | Wrecker (Melee) | weapon | aon | damage, weapon_category |
| `wb:weapon/wrecker-ranged` | Wrecker (Ranged) | weapon | aon | damage, weapon_category |

## Ainda sem

| id | nome | kind |
|---|---|---|
| `wb:armor/breastplate-of-command` | Breastplate of Command | armor |
| `wb:armor/celestial-armor` | Celestial Armor | armor |
| `wb:armor/demon-armor` | Demon Armor | armor |
| `wb:armor/elven-chain` | Elven Chain | armor |
| `wb:armor/grisantian-pelt-armor` | Grisantian Pelt Armor | armor |
| `wb:armor/heavy-power-suit` | Heavy Power Suit | armor |
| `wb:armor/lions-pelt` | Lion's Pelt | armor |
| `wb:armor/remorhaz-armor` | Remorhaz Armor | armor |
| `wb:armor/rhino-hide` | Rhino Hide | armor |
| `wb:armor/sovereign-steel-armor` | Sovereign Steel Armor | armor |
| `wb:shield/dragonhide-shield` | Dragonhide Shield | shield |
| `wb:shield/highhelm-war-shield` | Highhelm War Shield | shield |
| `wb:shield/mithral-shield` | Mithral Shield | shield |
| `wb:shield/noqual-shield` | Noqual Shield | shield |
| `wb:shield/orichalcum-shield` | Orichalcum Shield | shield |
| `wb:shield/siccatite-shield` | Siccatite Shield | shield |
| `wb:shield/sturdy-shield` | Sturdy Shield | shield |
| `wb:weapon/acid-flask-greater` | Acid Flask (Greater) | weapon |
| `wb:weapon/acid-flask-lesser` | Acid Flask (Lesser) | weapon |
| `wb:weapon/acid-flask-major` | Acid Flask (Major) | weapon |
| `wb:weapon/acid-flask-moderate` | Acid Flask (Moderate) | weapon |
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
| `wb:weapon/dagger-of-venom` | Dagger of Venom | weapon |
| `wb:weapon/dart-umbrella` | Dart Umbrella | weapon |
| `wb:weapon/drake-rifle` | Drake Rifle | weapon |
| `wb:weapon/flame-tongue` | Flame Tongue | weapon |
| `wb:weapon/glue-bomb-greater` | Glue Bomb (Greater) | weapon |
| `wb:weapon/glue-bomb-lesser` | Glue Bomb (Lesser) | weapon |
| `wb:weapon/glue-bomb-major` | Glue Bomb (Major) | weapon |
| `wb:weapon/glue-bomb-moderate` | Glue Bomb (Moderate) | weapon |
| `wb:weapon/holy-avenger` | Holy Avenger | weapon |
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
