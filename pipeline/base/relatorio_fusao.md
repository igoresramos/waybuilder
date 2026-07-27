# Fusao de renomeados

Chave: `remaster_id`/`legacy_id` do AoN. Prosa **nao** cria par --
entra so para desempatar sucessor multiplo. Campo estruturado
divergente veta a fusao.

- pares declarados pelo AoN: **604**
- fundidos: **0**
- vetados por divergencia estrutural: **604**
- desempatados por prosa: **55**
- base: 19738 -> **19738** registros
- registros com alias: **294**

## Vetados -- par declarado, conteudo divergente

O AoN liga os dois, mas um campo estruturado discorda. Revisar a mao;
fundir aqui apagaria dado.

- `wb:archetype/hellknight-signifer` x `wb:archetype/hellknight` -- level: 6 != 2
- `wb:class-feature/ability-boosts` x `wb:class/alchemist` -- kind: 'class-feature' != 'class'
- `wb:class-feature/stubborn` x `wb:class/gunslinger` -- kind: 'class-feature' != 'class'
- `wb:class-feature/evasion` x `wb:class/gunslinger` -- kind: 'class-feature' != 'class'
- `wb:class-feature/iron-will` x `wb:class/alchemist` -- kind: 'class-feature' != 'class'
- `wb:class-feature/druid-weapon-expertise` x `wb:class/druid` -- kind: 'class-feature' != 'class'
- `wb:class-feature/perpetual-infusions-bomber` x `wb:class/alchemist` -- kind: 'class-feature' != 'class'
- `wb:class-feature/alertness` x `wb:class/alchemist` -- kind: 'class-feature' != 'class'
- `wb:class-feature/perpetual-potency-bomber` x `wb:class/alchemist` -- kind: 'class-feature' != 'class'
- `wb:class-feature/improved-evasion` x `wb:class/ranger` -- kind: 'class-feature' != 'class'
- `wb:class-feature/second-skin` x `wb:class/ranger` -- kind: 'class-feature' != 'class'
- `wb:class-feature/alchemical-alacrity` x `wb:class/alchemist` -- kind: 'class-feature' != 'class'
- `wb:class-feature/perpetual-perfection-bomber` x `wb:class/alchemist` -- kind: 'class-feature' != 'class'
- `wb:class-feature/arcane-spellcasting-magus` x `wb:class/wizard` -- kind: 'class-feature' != 'class'
- `wb:class-feature/wizard-weapon-expertise` x `wb:class/wizard` -- kind: 'class-feature' != 'class'
- `wb:class-feature/greater-resolve` x `wb:class/investigator` -- kind: 'class-feature' != 'class'
- `wb:class-feature/swashbuckler-s-style` x `wb:class/swashbuckler` -- kind: 'class-feature' != 'class'
- `wb:class-feature/formula-book` x `wb:class/alchemist` -- kind: 'class-feature' != 'class'
- `wb:class-feature/heightened-senses` x `wb:class/barbarian` -- kind: 'class-feature' != 'class'
- `wb:class-feature/armor-of-fury` x `wb:class/barbarian` -- kind: 'class-feature' != 'class'
- `wb:class-feature/spell-repertoire-psychic` x `wb:class/psychic` -- kind: 'class-feature' != 'class'
- `wb:class-feature/occult-spellcasting` x `wb:class/bard` -- kind: 'class-feature' != 'class'
- `wb:class-feature/second-implement` x `wb:class/thaumaturge` -- kind: 'class-feature' != 'class'
- `wb:class-feature/spell-repertoire-summoner` x `wb:class/bard` -- kind: 'class-feature' != 'class'
- `wb:class-feature/resolve` x `wb:class/bard` -- kind: 'class-feature' != 'class'
- `wb:class-feature/deific-weapon` x `wb:class/champion` -- kind: 'class-feature' != 'class'
- `wb:class-feature/champion-s-reaction` x `wb:class/champion` -- kind: 'class-feature' != 'class'
- `wb:equipment/winter-wolf-elixir` x `wb:equipment/witchwarg-elixir` -- level: '4+' != 4
- `wb:equipment/winter-wolf-elixir-moderate` x `wb:equipment/witchwarg-elixir` -- level: 12 != 4
- `wb:equipment/winter-wolf-elixir-greater` x `wb:equipment/witchwarg-elixir` -- level: 16 != 4
- `wb:equipment/smokestick` x `wb:equipment/smoke-ball` -- level: '1+' != 1
- `wb:equipment/smokestick-greater` x `wb:equipment/smoke-ball` -- level: 7 != 1
- `wb:equipment/darkwood-armor` x `wb:equipment/duskwood-armor` -- level: '12+' != 12
- `wb:equipment/darkwood-armor-high-grade` x `wb:equipment/duskwood-armor` -- level: 19 != 12
- `wb:equipment/mithral-armor` x `wb:equipment/dawnsilver-armor` -- level: '12+' != 12
- `wb:equipment/mithral-armor-high-grade` x `wb:equipment/dawnsilver-armor` -- level: 19 != 12
- `wb:equipment/breastplate-of-command` x `wb:armor/warleaders-bulwark` -- kind: 'equipment' != 'armor'
- `wb:equipment/breastplate-of-command-greater` x `wb:armor/warleaders-bulwark` -- level: 18 != 10; price_cp: 2200000 != 100000; kind: 'equipment' != 'armor'
- `wb:equipment/celestial-armor` x `wb:armor/holy-chain` -- kind: 'equipment' != 'armor'
- `wb:equipment/demon-armor` x `wb:armor/unholy-plate` -- kind: 'equipment' != 'armor'
- `wb:armor/plate-armor-of-the-deep` x `wb:armor/tideplate` -- level: 15 != 10; price_cp: 650000 != 100000
- `wb:equipment/rhino-hide` x `wb:armor/onslaught-hide` -- kind: 'equipment' != 'armor'
- `wb:equipment/cloak-of-thirsty-fronds-transmutation` x `wb:equipment/cloak-of-gnawing-leaves` -- level: 7 != 3
- `wb:equipment/cloak-of-devouring-thorns-transmutation` x `wb:equipment/cloak-of-gnawing-leaves` -- level: 12 != 3
- `wb:equipment/stalk-goggles-greater` x `wb:equipment/stalk-goggles` -- level: 3 != 1; price_cp: 6000 != 2000
- `wb:equipment/stalk-goggles-major` x `wb:equipment/stalk-goggles` -- level: 8 != 1; price_cp: 45000 != 2000
- `wb:equipment/dragons-breath-potion` x `wb:equipment/energy-breath-potion` -- level: '7+' != 7
- `wb:equipment/dragons-breath-potion-adult` x `wb:equipment/energy-breath-potion` -- level: 12 != 7
- `wb:equipment/dragons-breath-potion-wyrm` x `wb:equipment/energy-breath-potion` -- level: 17 != 7
- `wb:equipment/pickled-demon-tongue-greater` x `wb:equipment/pickled-demon-tongue` -- level: 8 != 3; price_cp: 46000 != 6000
- `wb:equipment/pickled-demon-tongue-major` x `wb:equipment/pickled-demon-tongue` -- level: 12 != 3; price_cp: 175000 != 6000
- `wb:equipment/polished-demon-horn-greater` x `wb:equipment/polished-demon-horn` -- level: 8 != 3; price_cp: 45000 != 5500
- `wb:equipment/polished-demon-horn-major` x `wb:equipment/polished-demon-horn` -- level: 12 != 3; price_cp: 175000 != 5500
- `wb:equipment/aether-marble` x `wb:equipment/aether-marbles` -- level: 4 != '4+'
- `wb:equipment/aether-marble-lesser` x `wb:equipment/aether-marbles` -- level: 4 != '4+'
- `wb:equipment/aether-marble-moderate` x `wb:equipment/aether-marbles` -- level: 12 != '4+'
- `wb:equipment/aether-marble-greater` x `wb:equipment/aether-marbles` -- level: 18 != '4+'
- `wb:equipment/feather-token` x `wb:equipment/marvelous-miniature` -- level: '1+' != 1
- `wb:equipment/feather-token-chest` x `wb:equipment/marvelous-miniature` -- level: 3 != 1
- `wb:equipment/feather-token-swan-boat` x `wb:equipment/marvelous-miniature` -- level: 8 != 1

## Sucessor multiplo, desempatado por prosa

- `equipment-148` -> ['equipment-3277', 'equipment-3277-3115'] escolheu `equipment-3277` (0.805)
- `equipment-640` -> ['equipment-2962', 'equipment-2962-2826', 'equipment-2962-2827', 'equipment-2962-2828', 'equipment-2962-2829', 'equipment-2962-2830', 'equipment-2962-2831', 'equipment-2962-2832', 'equipment-2962-2833', 'equipment-2962-2834', 'equipment-2962-2835'] escolheu `equipment-2962` (0.206)
- `equipment-2416` -> ['equipment-4032', 'equipment-4032-3716', 'equipment-4032-3717', 'equipment-4032-3718'] escolheu `equipment-4032` (0.869)
- `equipment-406` -> ['equipment-3013', 'equipment-3013-2868', 'equipment-3013-2869'] escolheu `equipment-3013` (0.932)
- `equipment-4441` -> ['equipment-1908', 'equipment-1908-1662'] escolheu `equipment-1908` (0.6)
- `equipment-413` -> ['equipment-3056', 'equipment-3056-2981'] escolheu `equipment-3056` (0.291)
- `equipment-249` -> ['equipment-3032', 'equipment-3032-2890', 'equipment-3032-2891', 'equipment-3032-2892', 'equipment-3032-2893'] escolheu `equipment-3032` (0.909)
- `equipment-416` -> ['equipment-3058', 'equipment-3058-2985', 'equipment-3058-2986'] escolheu `equipment-3058` (0.373)
- `equipment-4491` -> ['equipment-1958', 'equipment-1958-1727', 'equipment-1958-1728', 'equipment-1958-1729', 'equipment-1958-1730'] escolheu `equipment-1958` (0.897)
- `equipment-79` -> ['equipment-3288', 'equipment-3288-3126', 'equipment-3288-3127', 'equipment-3288-3128', 'equipment-3288-3129'] escolheu `equipment-3288` (0.897)
- `equipment-689` -> ['equipment-3299', 'equipment-3299-3167', 'equipment-3299-3168', 'equipment-3299-3169', 'equipment-3299-3170', 'equipment-3299-3171'] escolheu `equipment-3299` (0.39)
- `equipment-4554` -> ['equipment-2021', 'equipment-2021-1782'] escolheu `equipment-2021` (0.836)
- `equipment-4602` -> ['equipment-2069', 'equipment-2069-1826'] escolheu `equipment-2069` (0.759)
- `equipment-440` -> ['equipment-3064', 'equipment-3064-2992'] escolheu `equipment-3064` (0.096)
- `equipment-455` -> ['equipment-3065', 'equipment-3065-2994', 'equipment-3065-2995'] escolheu `equipment-3065` (0.6)
- `equipment-98` -> ['equipment-3304', 'equipment-3304-3180', 'equipment-3304-3181', 'equipment-3304-3182'] escolheu `equipment-3304` (0.706)
- `equipment-273` -> ['equipment-2918', 'equipment-2918-2774', 'equipment-2918-2775', 'equipment-2918-2776', 'equipment-2918-2777'] escolheu `equipment-2918` (0.911)
- `equipment-141` -> ['equipment-2800', 'equipment-2800-2599', 'equipment-2800-2600'] escolheu `equipment-2800` (0.854)
- `equipment-312` -> ['equipment-2815', 'equipment-2815-2637', 'equipment-2815-2638', 'equipment-2815-2639', 'equipment-2815-2640', 'equipment-2815-2641', 'equipment-2815-2642'] escolheu `equipment-2815` (0.867)
- `equipment-376` -> ['equipment-2858', 'equipment-2858-2692', 'equipment-2858-2693'] escolheu `equipment-2858` (0.903)
- `equipment-275` -> ['equipment-2917', 'equipment-2917-2770', 'equipment-2917-2771', 'equipment-2917-2772', 'equipment-2917-2773'] escolheu `equipment-2917` (0.915)
- `equipment-144` -> ['equipment-2799', 'equipment-2799-2597', 'equipment-2799-2598'] escolheu `equipment-2799` (0.844)
- `equipment-377` -> ['equipment-2857', 'equipment-2857-2690', 'equipment-2857-2691'] escolheu `equipment-2857` (0.893)
- `equipment-294` -> ['equipment-2852', 'equipment-2852-2684'] escolheu `equipment-2852` (0.5)
- `equipment-185` -> ['equipment-2941', 'equipment-2941-2809', 'equipment-2941-2810', 'equipment-2941-2811'] escolheu `equipment-2941` (0.385)
- `equipment-4618` -> ['equipment-2085', 'equipment-2085-1842', 'equipment-2085-1843', 'equipment-2085-1844'] escolheu `equipment-2085` (0.732)
- `equipment-244` -> ['equipment-3002', 'equipment-3002-2860', 'equipment-3002-2862', 'equipment-3002-2864'] escolheu `equipment-3002` (0.291)
- `equipment-386` -> ['equipment-2870', 'equipment-2870-2705'] escolheu `equipment-2870` (0.699)
- `equipment-78` -> ['equipment-3295', 'equipment-3295-3153', 'equipment-3295-3154', 'equipment-3295-3155', 'equipment-3295-3156'] escolheu `equipment-3295` (0.786)
- `equipment-361` -> ['equipment-3038', 'equipment-3038-2907', 'equipment-3038-2908'] escolheu `equipment-3038` (0.389)
- `equipment-738` -> ['equipment-3434', 'equipment-3434-3305'] escolheu `equipment-3434` (0.658)
- `equipment-4910` -> ['equipment-2381', 'equipment-2381-2209'] escolheu `equipment-2381` (0.865)
- `equipment-443` -> ['equipment-3094', 'equipment-3094-3034'] escolheu `equipment-3094` (0.577)
- `equipment-4869` -> ['equipment-2337', 'equipment-2337-2188'] escolheu `equipment-2337` (0.869)
- `equipment-449-548` -> ['equipment-3000', 'equipment-3020'] escolheu `equipment-3000` (0.254)
- `equipment-449-549` -> ['equipment-3000', 'equipment-3020'] escolheu `equipment-3000` (0.254)
- `equipment-449-550` -> ['equipment-3000', 'equipment-3020'] escolheu `equipment-3000` (0.254)
- `equipment-449-551` -> ['equipment-3000', 'equipment-3020'] escolheu `equipment-3000` (0.254)
- `equipment-449-552` -> ['equipment-3000', 'equipment-3020'] escolheu `equipment-3000` (0.254)
- `equipment-449-553` -> ['equipment-3000', 'equipment-3020'] escolheu `equipment-3000` (0.254)

## Fusoes aplicadas

