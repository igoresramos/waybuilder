# Arquetipo do feat

- feats re-ancorados pelo `requires`: **37**
- sem ancora (ficam como estao): **36**

Chutar arquetipo por semelhanca de nome poria o feat na lista ERRADA, que e pior que deixa-lo sem lista. `Skill Mastery` aceita Rogue OU Investigator -- ancorar num dos dois seria escolher.

| arquetipo | feats |
|---|---:|
| `wb:archetype/rogue` | 3 |
| `wb:archetype/runelord` | 3 |
| `wb:archetype/elementalist` | 2 |
| `wb:archetype/alchemist` | 2 |
| `wb:archetype/knight-vigilant` | 2 |
| `wb:archetype/vindicator` | 2 |
| `wb:archetype/archer` | 1 |
| `wb:archetype/dragon-disciple` | 1 |
| `wb:archetype/twilight-speaker` | 1 |
| `wb:archetype/exemplar` | 1 |
| `wb:archetype/herbalist` | 1 |
| `wb:archetype/poisoner` | 1 |
| `wb:archetype/zombie` | 1 |
| `wb:archetype/mortal-herald` | 1 |
| `wb:archetype/ghost` | 1 |
| `wb:archetype/sterling-dynamo` | 1 |
| `wb:archetype/scrounger` | 1 |
| `wb:archetype/familiar-master` | 1 |
| `wb:archetype/scrollmaster` | 1 |
| `wb:archetype/sentinel` | 1 |
| `wb:archetype/hellbreaker` | 1 |
| `wb:archetype/field-propagandist` | 1 |
| `wb:archetype/trapsmith` | 1 |
| `wb:archetype/lastwall-sentry` | 1 |
| `wb:archetype/bastion` | 1 |
| `wb:archetype/avenger` | 1 |
| `wb:archetype/marshal` | 1 |
| `wb:archetype/vigilante` | 1 |
| `wb:archetype/runescarred` | 1 |

## Homonimo classe x arquetipo (item 100)

- ocorrencias reais: **12**

So conta quando o alvo E de arquetipo. Uma medicao automatizada deu 40 porque nao checava isso: `shield-block` (trait `general`) e `reactive-strike` (trait de classe) tem class-feature homonima e **nao sao defeito** -- e RAW correto, e o motor ja resolve por alias.

| registro | campo | aponta para | class-feature homonima |
|---|---|---|---|
| `wb:class-feature/alchemy` | `grants` | `wb:feat/advanced-alchemy` | `wb:class-feature/advanced-alchemy` |
| `wb:class-feature/alchemy` | `grants` | `wb:feat/quick-alchemy` | `wb:class-feature/quick-alchemy` |
| `wb:class-feature/quick-alchemy` | `grants` | `wb:feat/quick-alchemy` | `wb:class-feature/quick-alchemy` |
| `wb:feat/alchemist-dedication` | `grants` | `wb:feat/quick-alchemy` | `wb:class-feature/quick-alchemy` |
| `wb:feat/efficient-alchemy` | `requires` | `wb:feat/advanced-alchemy` | `wb:class-feature/advanced-alchemy` |
| `wb:feat/firework-technician-dedication` | `grants` | `wb:feat/quick-alchemy` | `wb:class-feature/quick-alchemy` |
| `wb:feat/keen-recollection` | `grants` | `wb:feat/keen-recollection` | `wb:class-feature/keen-recollection` |
| `wb:feat/munitions-machinist` | `grants` | `wb:feat/quick-alchemy` | `wb:class-feature/quick-alchemy` |
| `wb:feat/rogue-dedication` | `grants` | `wb:feat/surprise-attack` | `wb:class-feature/surprise-attack` |
| `wb:feat/shield-of-reckoning` | `requires` | `wb:feat/champions-reaction` | `wb:class-feature/champions-reaction` |
| `wb:feat/swift-retribution` | `requires` | `wb:feat/champions-reaction` | `wb:class-feature/champions-reaction` |
| `wb:feat/wandering-chef-dedication` | `grants` | `wb:feat/quick-alchemy` | `wb:class-feature/quick-alchemy` |
