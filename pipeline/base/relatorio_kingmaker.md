# Remocao do conteudo de Kingmaker

Removidos: **125** registros. Criterio: `source.book` na lista fechada de tres livros de Kingmaker.

Decisao do Igor em 2026-08-01, UNICA excecao ao principio 4 do README ("nada e descartado"). Ver `specs/2026-08-01-remover-kingmaker.md` antes de reverter.

Este relatorio existe porque **contagem sozinha nao prova nada**: 125 remocoes ERRADAS tambem batem 125. A lista abaixo e nominal.

- por kind: {'background': 7, 'equipment': 23, 'feat': 31, 'ritual': 1, 'skill': 16, 'spell': 10, 'trait': 31, 'weapon': 6}
- por livro: {'kingmaker adventure path': 80, 'kingmaker companion guide': 41, 'pathfinder kingmaker': 4}
- entradas de prosa removidas de `base/text/*.json`: **125**
- citacoes orfas (semantica do portao 3): 0 antes, 0 depois

## Efeito no portao 9 (censo do AoN)

- background: 7 ausencia(s), 7 id(s) aceito(s)
- equipment: 30 ausencia(s), 30 id(s) aceito(s)
- feat: 29 ausencia(s), 29 id(s) aceito(s)  <- FUNDIR POR UNIAO: a categoria ja existe no censo curado
- ritual: 1 ausencia(s), 1 id(s) aceito(s)
- skill: 14 ausencia(s), 16 id(s) aceito(s)
- spell: 10 ausencia(s), 10 id(s) aceito(s)
- trait: 31 ausencia(s), 31 id(s) aceito(s)

Fragmento pronto em `base/_kingmaker_ausencias.json` -- fundir a mao em `pipeline/censo_ausencias.json`.

## Vocabulario generico que sai junto (spec, secao 3)

O AoN atribui estes traits a Kingmaker porque o hardcover reimprime o glossario e o dump registra a pagina do hardcover como fonte unica. Nao ha segunda entrada para canonizar. Uso medido antes da remocao: zero, exceto `tech`, usado so pelas duas armas de Kingmaker removidas no mesmo ato.

| id | o que e |
|---|---|
| `wb:trait/shapechanger` | trait de criatura (Monster) |
| `wb:trait/tech` | trait de item tecnologico (Mechanics) |
| `wb:trait/weather` | trait de perigo ambiental (Hazard) |
| `wb:trait/wild-hunt` | trait de familia de criatura (Monster) |

## background (7)

| id | nome | livro | pag. | doc do AoN |
|---|---|---|---|---|
| `wb:background/borderlands-pioneer` | Borderlands Pioneer | Kingmaker Adventure Path | 12 | background-337 |
| `wb:background/brevic-noble` | Brevic Noble | Kingmaker Adventure Path | 12 | background-338 |
| `wb:background/brevic-outcast` | Brevic Outcast | Kingmaker Adventure Path | 12 | background-339 |
| `wb:background/issian-patriot` | Issian Patriot | Kingmaker Adventure Path | 13 | background-340 |
| `wb:background/local-brigand` | Local Brigand | Kingmaker Adventure Path | 13 | background-341 |
| `wb:background/rostlander` | Rostlander | Kingmaker Adventure Path | 13 | background-342 |
| `wb:background/sword-scion` | Sword Scion | Kingmaker Adventure Path | 13 | background-343 |

## equipment (23)

| id | nome | livro | pag. | doc do AoN |
|---|---|---|---|---|
| `wb:equipment/admirers-bouquet` | Admirer's Bouquet | Kingmaker Companion Guide | 84 | equipment-1758 |
| `wb:equipment/azure-lily-pollen` | Azure Lily Pollen | Kingmaker Adventure Path | 584 | equipment-1742 |
| `wb:equipment/basic-ingredient` | Basic Ingredient | Pathfinder Kingmaker | -- | -- |
| `wb:equipment/deathdrinking` | Deathdrinking | Kingmaker Companion Guide | 96 | equipment-1762 |
| `wb:equipment/energy-absorbing` | Energy-Absorbing | Kingmaker Companion Guide | 104 | equipment-1763 |
| `wb:equipment/energy-absorbing-greater` | Energy-Absorbing (Greater) | Kingmaker Companion Guide | 104 | equipment-1763-1559 |
| `wb:equipment/feyfoul` | Feyfoul | Kingmaker Companion Guide | 35 | equipment-1757 |
| `wb:equipment/feyfoul-greater` | Feyfoul (Greater) | Kingmaker Companion Guide | 35 | equipment-1757-1557 |
| `wb:equipment/feyfoul-lesser` | Feyfoul (Lesser) | Kingmaker Companion Guide | 35 | equipment-1757-1555 |
| `wb:equipment/feyfoul-moderate` | Feyfoul (Moderate) | Kingmaker Companion Guide | 35 | equipment-1757-1556 |
| `wb:equipment/giant-killing` | Giant-Killing | Kingmaker Companion Guide | 24 | equipment-1756 |
| `wb:equipment/giant-killing-greater` | Giant-Killing (Greater) | Kingmaker Companion Guide | 24 | equipment-1756-1554 |
| `wb:equipment/hooked` | Hooked | Kingmaker Companion Guide | 24 | equipment-1755 |
| `wb:equipment/lovers-knot` | Lover's Knot | Kingmaker Adventure Path | 586 | equipment-1744 |
| `wb:equipment/moon-radish-soup` | Moon Radish Soup | Kingmaker Adventure Path | 587 | equipment-1746 |
| `wb:equipment/oculus-of-abaddon` | Oculus of Abaddon | Kingmaker Adventure Path | 587 | equipment-1747 |
| `wb:equipment/palette-of-masterstrokes` | Palette of Masterstrokes | Kingmaker Companion Guide | 84 | equipment-1759 |
| `wb:equipment/ring-of-bestial-friendship` | Ring of Bestial Friendship | Kingmaker Adventure Path | 588 | equipment-1749 |
| `wb:equipment/ring-of-the-tiger` | Ring of the Tiger | Kingmaker Adventure Path | 589 | equipment-1750 |
| `wb:equipment/ring-of-the-tiger-greater` | Ring of the Tiger (Greater) | Kingmaker Adventure Path | 589 | equipment-1750-1552 |
| `wb:equipment/special-ingredient` | Special Ingredient | Pathfinder Kingmaker | -- | -- |
| `wb:equipment/stags-helm` | Stag's Helm | Kingmaker Adventure Path | 589 | equipment-1752 |
| `wb:equipment/tripline-arrow` | Tripline Arrow | Kingmaker Companion Guide | 24 | equipment-1754 |

## feat (31)

| id | nome | livro | pag. | doc do AoN |
|---|---|---|---|---|
| `wb:feat/ambush-tactics` | Ambush Tactics | Kingmaker Companion Guide | 35 | feat-3905 |
| `wb:feat/civil-service` | Civil Service | Kingmaker Adventure Path | 531 | feat-3908 |
| `wb:feat/cooperative-leadership` | Cooperative Leadership | Kingmaker Adventure Path | 531 | feat-3909 |
| `wb:feat/crush-dissent` | Crush Dissent | Kingmaker Adventure Path | 531 | feat-3910 |
| `wb:feat/efficient-explorer` | Efficient Explorer | Kingmaker Companion Guide | 35 | feat-3906 |
| `wb:feat/endure-anarchy` | Endure Anarchy | Kingmaker Adventure Path | 531 | feat-3911 |
| `wb:feat/fame-and-fortune` | Fame and Fortune | Kingmaker Adventure Path | 531 | feat-3912 |
| `wb:feat/fortified-fiefs` | Fortified Fiefs | Kingmaker Adventure Path | 531 | feat-3913 |
| `wb:feat/free-and-fair` | Free and Fair | Kingmaker Adventure Path | 531 | feat-3914 |
| `wb:feat/giant-hunter` | Giant Hunter | Kingmaker Companion Guide | 23 | feat-3900 |
| `wb:feat/giant-slayer` | Giant Slayer | Kingmaker Companion Guide | 24 | feat-3904 |
| `wb:feat/hamstringing-strike` | Hamstringing Strike | Kingmaker Companion Guide | 23 | feat-3902 |
| `wb:feat/insider-trading` | Insider Trading | Kingmaker Adventure Path | 531 | feat-3915 |
| `wb:feat/inspiring-entertainment` | Inspiring Entertainment | Kingmaker Adventure Path | 532 | feat-3916 |
| `wb:feat/kingdom-assurance` | Kingdom Assurance | Kingmaker Adventure Path | 532 | feat-3917 |
| `wb:feat/liquidate-resources` | Liquidate Resources | Kingmaker Adventure Path | 532 | feat-3918 |
| `wb:feat/muddle-through` | Muddle Through | Kingmaker Adventure Path | 532 | feat-3919 |
| `wb:feat/practical-magic` | Practical Magic | Kingmaker Adventure Path | 532 | feat-3920 |
| `wb:feat/predict-weather` | Predict Weather | Kingmaker Companion Guide | 121 | feat-3907 |
| `wb:feat/pull-together` | Pull Together | Kingmaker Adventure Path | 532 | feat-3921 |
| `wb:feat/quality-of-life` | Quality of Life | Kingmaker Adventure Path | 532 | feat-3922 |
| `wb:feat/quick-recovery-kingdom` | Quick Recovery (Kingdom) | Kingmaker Adventure Path | 532 | feat-3923 |
| `wb:feat/roll-with-it-kingmaker` | Roll with it (Kingmaker) | Pathfinder Kingmaker | -- | -- |
| `wb:feat/roll-with-it-ranger` | Roll with It (Ranger) | Kingmaker Companion Guide | 23 | feat-3903 |
| `wb:feat/say-that-again` | Say that Again! | Kingmaker Companion Guide | 9 | feat-3898 |
| `wb:feat/skill-training-kingdom` | Skill Training (Kingdom) | Kingmaker Adventure Path | 532 | feat-3924 |
| `wb:feat/thats-not-natural` | That's Not Natural! | Kingmaker Companion Guide | 9 | feat-3897 |
| `wb:feat/the-harder-they-fall-kingmaker` | The Harder They Fall (Kingmaker) | Pathfinder Kingmaker | -- | -- |
| `wb:feat/the-harder-they-fall-ranger` | The Harder They Fall (Ranger) | Kingmaker Companion Guide | 23 | feat-3901 |
| `wb:feat/too-angry-to-die` | Too Angry to Die | Kingmaker Companion Guide | 9 | feat-3899 |
| `wb:feat/triumphant-boast` | Triumphant Boast | Kingmaker Companion Guide | 9 | feat-3896 |

## ritual (1)

| id | nome | livro | pag. | doc do AoN |
|---|---|---|---|---|
| `wb:ritual/incarnate-ancestry` | Incarnate Ancestry | Kingmaker Companion Guide | 81 | ritual-97 |

## skill (16)

| id | nome | livro | pag. | doc do AoN |
|---|---|---|---|---|
| `wb:skill/agriculture` | Agriculture | Kingmaker Adventure Path | 522 | skill-18 |
| `wb:skill/arts` | Arts | Kingmaker Adventure Path | 522 | skill-19 |
| `wb:skill/boating` | Boating | Kingmaker Adventure Path | 522 | skill-20 |
| `wb:skill/defense` | Defense | Kingmaker Adventure Path | 522 | skill-21 |
| `wb:skill/engineering` | Engineering | Kingmaker Adventure Path | 523 | skill-22 |
| `wb:skill/exploration` | Exploration | Kingmaker Adventure Path | 524 | skill-23 |
| `wb:skill/folklore` | Folklore | Kingmaker Adventure Path | 524 | skill-24 |
| `wb:skill/industry` | Industry | Kingmaker Adventure Path | 525 | skill-25 |
| `wb:skill/intrigue` | Intrigue | Kingmaker Adventure Path | 526 | skill-26 |
| `wb:skill/magic` | Magic | Kingmaker Adventure Path | 526 | skill-27 |
| `wb:skill/politics` | Politics | Kingmaker Adventure Path | 527 | skill-28 |
| `wb:skill/scholarship` | Scholarship | Kingmaker Adventure Path | 527 | skill-29 |
| `wb:skill/statecraft` | Statecraft | Kingmaker Adventure Path | 528 | skill-30 |
| `wb:skill/trade` | Trade | Kingmaker Adventure Path | 529 | skill-31 |
| `wb:skill/warfare` | Warfare | Kingmaker Adventure Path | 530 | skill-32 |
| `wb:skill/wilderness` | Wilderness | Kingmaker Adventure Path | 530 | skill-33 |

## spell (10)

| id | nome | livro | pag. | doc do AoN |
|---|---|---|---|---|
| `wb:spell/aqueous-blast` | Aqueous Blast | Kingmaker Companion Guide | 99 | spell-1236 |
| `wb:spell/blazing-blade` | Blazing Blade | Kingmaker Companion Guide | 71 | spell-1233 |
| `wb:spell/dawnflowers-light` | Dawnflower's Light | Kingmaker Companion Guide | 71 | spell-1234 |
| `wb:spell/infectious-ennui` | Infectious Ennui | Kingmaker Companion Guide | 95 | spell-1235 |
| `wb:spell/inkshot` | Inkshot | Kingmaker Companion Guide | 46 | spell-1229 |
| `wb:spell/phantasmal-protagonist` | Phantasmal Protagonist | Kingmaker Companion Guide | 46 | spell-1230 |
| `wb:spell/scorching-blast` | Scorching Blast | Kingmaker Companion Guide | 99 | spell-1237 |
| `wb:spell/transcribe-conflict` | Transcribe Conflict | Kingmaker Companion Guide | 46 | spell-1231 |
| `wb:spell/vision-of-beauty` | Vision of Beauty | Kingmaker Companion Guide | 103 | spell-1238 |
| `wb:spell/word-of-revision` | Word of Revision | Kingmaker Companion Guide | 47 | spell-1232 |

## trait (31)

| id | nome | livro | pag. | doc do AoN |
|---|---|---|---|---|
| `wb:trait/army` | Army | Kingmaker Adventure Path | -- | trait-454 |
| `wb:trait/beneficial` | Beneficial | Kingmaker Adventure Path | 553 | trait-449 |
| `wb:trait/building` | Building | Kingmaker Adventure Path | 543 | trait-442 |
| `wb:trait/camping` | Camping | Kingmaker Companion Guide | -- | trait-465 |
| `wb:trait/cavalry` | Cavalry | Kingmaker Adventure Path | 569 | trait-458 |
| `wb:trait/civic` | Civic | Kingmaker Adventure Path | 517 | trait-436 |
| `wb:trait/commerce` | Commerce | Kingmaker Adventure Path | 517 | trait-437 |
| `wb:trait/continuous` | Continuous | Kingmaker Adventure Path | 553 | trait-451 |
| `wb:trait/dangerous` | Dangerous | Kingmaker Adventure Path | 553 | trait-450 |
| `wb:trait/edifice` | Edifice | Kingmaker Adventure Path | 543 | trait-445 |
| `wb:trait/famous` | Famous | Kingmaker Adventure Path | 543 | trait-447 |
| `wb:trait/hex-km` | Hex-KM | Kingmaker Adventure Path | 553 | trait-452 |
| `wb:trait/infamous` | Infamous | Kingmaker Adventure Path | 543 | trait-448 |
| `wb:trait/infantry` | Infantry | Kingmaker Adventure Path | 569 | trait-455 |
| `wb:trait/infrastructure` | Infrastructure | Kingmaker Adventure Path | 543 | trait-444 |
| `wb:trait/kingdom` | Kingdom | Kingmaker Adventure Path | 531 | trait-438 |
| `wb:trait/leadership` | Leadership | Kingmaker Adventure Path | 517 | trait-439 |
| `wb:trait/maneuver` | Maneuver | Kingmaker Adventure Path | 570 | trait-459 |
| `wb:trait/meal` | Meal | Kingmaker Companion Guide | -- | trait-466 |
| `wb:trait/morale` | Morale | Kingmaker Adventure Path | 570 | trait-460 |
| `wb:trait/region` | Region | Kingmaker Adventure Path | 517 | trait-440 |
| `wb:trait/residential` | Residential | Kingmaker Adventure Path | 543 | trait-446 |
| `wb:trait/settlement` | Settlement | Kingmaker Adventure Path | 553 | trait-453 |
| `wb:trait/shapechanger` | Shapechanger | Kingmaker Adventure Path | 385 | trait-461 |
| `wb:trait/siege` | Siege | Kingmaker Adventure Path | 569 | trait-457 |
| `wb:trait/skirmisher` | Skirmisher | Kingmaker Adventure Path | 569 | trait-456 |
| `wb:trait/tech` | Tech | Kingmaker Adventure Path | 596 | trait-434 |
| `wb:trait/upkeep` | Upkeep | Kingmaker Adventure Path | 517 | trait-441 |
| `wb:trait/weather` | Weather | Kingmaker Companion Guide | 123 | trait-464 |
| `wb:trait/wild-hunt` | Wild Hunt | Kingmaker Adventure Path | 616 | trait-435 |
| `wb:trait/yard` | Yard | Kingmaker Adventure Path | 543 | trait-443 |

## weapon (6)

| id | nome | livro | pag. | doc do AoN |
|---|---|---|---|---|
| `wb:weapon/briar` | Briar | Kingmaker Adventure Path | 584 | equipment-1743 |
| `wb:weapon/grisly-scythe` | Grisly Scythe | Kingmaker Companion Guide | 93 | equipment-1761 |
| `wb:weapon/mindrender-baton` | Mindrender Baton | Kingmaker Adventure Path | 586 | equipment-1753 |
| `wb:weapon/ovinrbaane` | Ovinrbaane | Kingmaker Adventure Path | 587 | equipment-1748 |
| `wb:weapon/rod-of-razors` | Rod of Razors | Kingmaker Adventure Path | 589 | equipment-1751 |
| `wb:weapon/songbirds-brush` | Songbird's Brush | Kingmaker Companion Guide | 84 | equipment-1760 |

