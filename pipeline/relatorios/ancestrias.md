# Relatorio -- Ancestrias, Heranças e Backgrounds (PF2e)

Extrator: `pipeline/extratores/ancestrias.py`. Fontes: Foundry pf2e (commit `87f9e5028baaa10b70fdc766260b7886def17e04`), AoN (dump Elasticsearch), pf2etools (branch dev, terceira opiniao).

## Contagem por kind

| kind | registros emitidos | boosts estruturados | flaw/skill_training estruturados |
|---|---|---|---|
| ancestry | 50 | 50/50 | 34/50 (flaw) |
| heritage | 326 | n/a | 70/326 totalmente mecanizados (`mechanized=true`) |
| background | 514 | 514/514 | 481/514 (skill_training) |

Nenhum registro emitido veio so de prosa: todos os 890 registros sao enumerados a partir do Foundry, que sempre traz os campos estruturados em campo proprio (boosts/flaw/hp/speed/skill_training). "Ausente" acima significa RAW genuino (ex.: Human sem flaw, Amnesiac sem skill_training), nao falha de parsing -- ver secao de campos nao mapeados.

## Mapa Legacy -> Remaster (fonte: AoN, conjunto completo)

AoN tem 94 docs de ancestry, 436 de heritage e 612 de background (Legacy + Remaster somados). Cruzamento via `remaster_id`/`legacy_id`.

### Ancestrias

- Renomeados (par Legacy->Remaster com nome diferente, via `remaster_id`): 4

  - Gnoll (ancestry-44) -> Kholo (ancestry-79)

  - Grippli (ancestry-46) -> Tripkee (ancestry-84)

  - Half-Elf (ancestry-7) -> Aiuvarin (ancestry-69)

  - Half-Orc (ancestry-8) -> Dromaar (ancestry-70)

- Legacy sem substituto (era pre-remaster, sem `remaster_id`, e o nome nao aparece no Foundry -- ou seja, saiu de circulacao): 9

  - Aphorite (Ancestry Guide, 2021-02-24) -- `ancestry-28`

  - Beastkin (Ancestry Guide, 2021-02-24) -- `ancestry-29`

  - Ifrit (Ancestry Guide, 2021-02-24) -- `ancestry-33`

  - Oread (Ancestry Guide, 2021-02-24) -- `ancestry-34`

  - Suli (Ancestry Guide, 2021-02-24) -- `ancestry-35`

  - Sylph (Ancestry Guide, 2021-02-24) -- `ancestry-36`

  - Undine (Ancestry Guide, 2021-02-24) -- `ancestry-37`

  - Ardande (Rage of Elements, 2023-08-02) -- `ancestry-57`

  - Talos (Rage of Elements, 2023-08-02) -- `ancestry-58`


### Heranças

- Renomeados (par Legacy->Remaster com nome diferente, via `remaster_id`): 12

  - Ant Gnoll (heritage-166) -> Ant Kholo (heritage-326)

  - Great Gnoll (heritage-167) -> Great Kholo (heritage-329)

  - Sweetbreath Gnoll (heritage-168) -> Sweetbreath Kholo (heritage-330)

  - Witch Gnoll (heritage-169) -> Witch Kholo (heritage-332)

  - Poisonhide Grippli (heritage-175) -> Poisonhide Tripkee (heritage-361)

  - Snaptongue Grippli (heritage-176) -> Snaptongue Tripkee (heritage-363)

  - Stickytoe Grippli (heritage-177) -> Stickytoe Tripkee (heritage-364)

  - Windweb Grippli (heritage-178) -> Windweb Tripkee (heritage-366)

  - Skilled Heritage (heritage-28) -> Skilled Human (heritage-261)

  - Versatile Heritage (heritage-29) -> Versatile Human (heritage-262)

  - Cavern Kobold (heritage-63) -> Cavernstalker Kobold (heritage-333)

  - Spellscale Kobold (heritage-65) -> Spellhorn Kobold (heritage-336)

- Legacy sem substituto (era pre-remaster, sem `remaster_id`, e o nome nao aparece no Foundry -- ou seja, saiu de circulacao): 7

  - Aphorite (Ancestry Guide, 2021-02-24) -- `heritage-118`

  - Ganzi (Ancestry Guide, 2021-02-24) -- `heritage-129`

  - Ifrit (Ancestry Guide, 2021-02-24) -- `heritage-130`

  - Half-Elf (Core Rulebook, 2019-08-01) -- `heritage-26`

  - Half-Orc (Core Rulebook, 2019-08-01) -- `heritage-27`

  - Aasimar (Advanced Player's Guide, 2020-07-30) -- `heritage-84`

  - Tiefling (Advanced Player's Guide, 2020-07-30) -- `heritage-86`


### Backgrounds

- Renomeados (par Legacy->Remaster com nome diferente, via `remaster_id`): 0

- Legacy sem substituto (era pre-remaster, sem `remaster_id`, e o nome nao aparece no Foundry -- ou seja, saiu de circulacao): 5

  - Post Guard of All Trade (Agents of Edgewatch Player's Guide, 2020-07-08) -- `background-196`

  - Reclaimed Investigator (Knights of Lastwall, 2022-05-25) -- `background-314`

  - Muesello's Student (Pathfinder Society Year 4 Rule Updates, 2022-06-30) -- `background-350`

  - Historical Reeanactor (Sky King's Tomb Player's Guide, 2023-07-13) -- `background-392`

  - Refugee (FoP) (The Fall of Plaguestone, 2019-08-01) -- `background-40`


**Nota sobre Aasimar/Tiefling -> Nephilim:** o AoN nao tem `remaster_id` ligando Aasimar (`heritage-84`, Advanced Player's Guide) nem Tiefling (`heritage-86`, Advanced Player's Guide) a nada -- por isso aparecem acima em "sem substituto", nao em "renomeados". Confirmado por leitura direta: nenhuma das duas existe no Foundry (nem como heritage remaster nem legacy), e o texto de Nephilim (`heritage-280`, Player Core, presente no Foundry como versatile heritage) e mecanicamente identico ao template de Aasimar/Tiefling ("ganha o trait X, visao adicional, escolhe feats de X ou da ancestria"), so generalizado pra herança unica que cobre celestial/fiend/monitor. E fusao estrutural, nao substituicao 1:1 -- por isso o AoN nao registrou ponte automatica e o merge tem que ser manual.

## Campos nao mapeados

- **`ancestry.items`** (equipamento concedido, ex.: Clan Dagger do Dwarf, presente em 36/50 ancestrias do Foundry): fora do escopo pedido (hp/size/speed/boosts/flaw/languages/traits/senses/heritages). Nao emitido.

- **`heritage.grants` parcial**: o Foundry usa ~20 tipos de rule element distintos nas heranças (GrantItem, ActiveEffectLike, ItemAlteration, Sense, Resistance, AdjustDegreeOfSuccess, RollOption, Strike, BaseSpeed, ChoiceSet, Note, CreatureSize, ActorTraits, TokenLight, DamageDice, Aura, AdjustModifier, AdjustStrike, Weakness). So `FlatModifier` foi traduzido pra linguagem de efeito do schema (bate 1:1 com o exemplo do contrato). `mechanized=true` em 70/326 registros (41 deles por nao terem rule element nenhum -- heranças puramente narrativas). O resto precisa do interpretador de rule elements (item de trabalho proprio, ja registrado em LESSONS.md do projeto).

- **`background.feats_granted` como lista, nao campo singular**: 2 backgrounds (Hermean Heritor, Returned) concedem 2 feats, nao 1. Campo sai como lista em vez de objeto unico.

- **Ancestrias sem par no AoN**: 0 -- (nenhuma)

- **Heranças sem par no AoN**: 4

- Ambitious Human
- Battle-Trained Human (BB)
- Naari
- Warden Human (BB)

- **Backgrounds sem par no AoN**: 25

- Archival Assistant
- Art 'Collector'
- Azlanti Researcher
- Battle's Spark
- Blooded by the Dead
- Boundless Wonder
- Clockwork Wonder
- Curse-Marked
- Envoy's Alliance
- Friend of a Friend
- Grand Archive
- Historical Reenactor
- Horizon Hunters
- Immortal Influence
- Once Possessed
- Post Guard of All Trades
- Radiant Oath
- Reclaimer Investigator
- Refugee (Fall of Plaguestone)
- Refugee (PC2)
- ... (+5)

- **Pareamento por nome normalizado (fallback)**: 2 registros so casaram com AoN depois de normalizar hifen/espaco (mesmo registro, pontuacao diverge entre Foundry e AoN). Sem esse fallback, esses apareceriam como "sem par" ou, do lado do mapa Legacy->Remaster, como "removido":

- background: Foundry "Aspiring Free-Captain" ~ AoN "Aspiring Free Captain" (background-81)
- background: Foundry "Oenopion-Ooze Tender" ~ AoN "Oenopion Ooze-Tender" (background-92)

## Divergencias entre fontes

Conflitos formais (campo por campo, foundry vs aon) ficam no array `conflitos` de cada registro em `ancestrias.json`. Abaixo, divergencias encontradas contra a terceira fonte (pf2etools), que nao vence nenhum campo nesta kind mas serve de checagem:

- background/able-carter: skills foundry=[] pf2etools=['deception', 'diplomacy']
- background/animal-wrangler: skills foundry=[] pf2etools=['athletics', 'nature']
- background/beast-seeker: skills foundry=[] pf2etools=['athletics', 'thievery']
- background/blow-in: skills foundry=[] pf2etools=['deception', 'thievery']
- background/child-of-notoriety: skills foundry=[] pf2etools=['diplomacy', 'intimidation']
- background/child-of-the-polis: skills foundry=[] pf2etools=['diplomacy', 'lore', 'society']
- background/conservator: skills foundry=[] pf2etools=['crafting', 'thievery']
- background/construction-occultist: skills foundry=[] pf2etools=['athletics', 'occultism']
- background/dedicated-delver: skills foundry=[] pf2etools=['athletics', 'survival']
- background/eidolon-contact: skills foundry=[] pf2etools=['arcana', 'nature', 'occultism', 'religion']
- background/feybound: skills foundry=[] pf2etools=['nature']
- background/fiendbreaking-pilgrim: skills foundry=['religion'] pf2etools=['perception', 'religion']
- background/food-trader: skills foundry=[] pf2etools=['crafting', 'society']
- background/glory-hound: skills foundry=[] pf2etools=['intimidation', 'performance']
- background/harrow-led: skills foundry=[] pf2etools=['occultism', 'performance', 'society']
- background/herbalist: skills foundry=['nature'] pf2etools=['medicine', 'nature']
- background/hermit: skills foundry=[] pf2etools=['nature', 'occultism']
- background/historical-reenactor: skills foundry=[] pf2etools=['performance', 'society']
- background/kartaji-epicurean: skills foundry=[] pf2etools=['crafting', 'society']
- background/learned-guard-prodigy: skills foundry=[] pf2etools=['arcana', 'occultism']
- background/magaambya-academic: skills foundry=[] pf2etools=['arcana', 'nature']
- background/martial-disciple: skills foundry=[] pf2etools=['acrobatics', 'athletics']
- background/money-counter: skills foundry=[] pf2etools=['society', 'thievery']
- background/mystic-tutor: skills foundry=[] pf2etools=['arcana', 'occultism']
- background/obari-wanderer: skills foundry=[] pf2etools=['acrobatics', 'survival']
- background/osprey-spellcaster: skills foundry=[] pf2etools=['arcana', 'nature', 'occultism', 'religion']
- background/pathfinder-recruiter: skills foundry=['diplomacy'] pf2etools=['diplomacy', 'society']
- background/pillar: skills foundry=[] pf2etools=['medicine', 'society', 'survival']
- background/propaganda-promoter: skills foundry=[] pf2etools=['acrobatics', 'performance']
- background/raised-by-belief: skills foundry=[] pf2etools=['acrobatics', 'arcana', 'athletics', 'crafting', 'deception', 'diplomacy', 'intimidation', 'medicine', 'nature', 'occultism', 'performance', 'religion', 'society', 'stealth', 'survival', 'thievery']
- background/scholar: skills foundry=[] pf2etools=['arcana', 'nature', 'occultism', 'religion']
- background/spell-seeker: skills foundry=[] pf2etools=['arcana', 'occultism']
- background/sponsored-by-a-stranger: skills foundry=[] pf2etools=['nature', 'occultism']
- background/sponsored-by-a-village: skills foundry=[] pf2etools=['crafting', 'survival']
- background/sponsored-by-family: skills foundry=[] pf2etools=['diplomacy', 'society']
- background/sponsored-by-teacher-ot: skills foundry=[] pf2etools=['performance', 'survival']
- background/stargazer: skills foundry=[] pf2etools=['arcana', 'nature', 'occultism']
- background/student-of-apotheosis: skills foundry=[] pf2etools=['occultism', 'religion']
- background/student-of-magic: skills foundry=[] pf2etools=['arcana', 'nature', 'occultism', 'religion']
- background/surge-investigator: skills foundry=[] pf2etools=['nature', 'occultism']
- ... (+4)

## Casos RAW notaveis (nao sao bug do extrator)

- Human: dois boosts livres, zero flaw (RAW correto pos-remaster).
- Amnesiac (background, Player Core 2): 3 boosts livres, sem skill_training, sem feat -- background genuinamente atipico.
- Farmhand e outros ~60 backgrounds: sem feat concedido (`feats_granted=[]`) -- RAW, nao falha de extracao.
- Faction Opportunist (background): lore com string livre "or Mercantile Lore" dentro da lista -- dado cru do Foundry, mantido como veio (nao normalizado).
- 19/50 ancestrias e 121/326 heranças no Foundry ainda sao Legacy/OGL (`source.remaster=false`) -- nunca foram remasterizadas oficialmente (ex.: Android, Anadi, Kitsune, Sprite, Strix, Skeleton).

