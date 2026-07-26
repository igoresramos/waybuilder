# Relatorio -- Ancestrias, Heranças e Backgrounds (PF2e)

Extrator: `pipeline/extratores/ancestrias.py`. Fontes: Foundry pf2e (commit `87f9e5028baaa10b70fdc766260b7886def17e04`), AoN (dump Elasticsearch), pf2etools (branch dev, terceira opiniao).

## Contagem por kind

| kind | registros emitidos | boosts estruturados | flaw/skill_training estruturados |
|---|---|---|---|
| ancestry | 50 | 50/50 | 34/50 (flaw) |
| heritage | 326 | n/a | 68/326 totalmente mecanizados (`mechanized=true`) |
| background | 332 | 332/332 | 312/332 (skill_training) |

Nenhum registro emitido veio so de prosa: todos os 708 registros sao enumerados a partir do Foundry, que sempre traz os campos estruturados em campo proprio (boosts/flaw/hp/speed/skill_training). "Ausente" acima significa RAW genuino (ex.: Human sem flaw, Amnesiac sem skill_training), nao falha de parsing -- ver secao de campos nao mapeados.

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

- Legacy sem substituto (era pre-remaster, sem `remaster_id`, e o nome nao aparece no Foundry -- ou seja, saiu de circulacao): 97

  - Aerialist (Extinction Curse Player's Guide, 2020-01-13) -- `background-134`

  - Animal Wrangler (Extinction Curse Player's Guide, 2020-01-13) -- `background-135`

  - Barker (Extinction Curse Player's Guide, 2020-01-13) -- `background-136`

  - Blow-In (Extinction Curse Player's Guide, 2020-01-13) -- `background-137`

  - Butcher (Extinction Curse Player's Guide, 2020-01-13) -- `background-138`

  - Circus Born (Extinction Curse Player's Guide, 2020-01-13) -- `background-139`

  - Clown (Extinction Curse Player's Guide, 2020-01-13) -- `background-140`

  - Mystic Seer (Extinction Curse Player's Guide, 2020-01-13) -- `background-141`

  - Rigger (Extinction Curse Player's Guide, 2020-01-13) -- `background-142`

  - Ex-Con Token Guard (Agents of Edgewatch Player's Guide, 2020-07-08) -- `background-190`

  - Godless Graycloak (Agents of Edgewatch Player's Guide, 2020-07-08) -- `background-191`

  - Grizzled Muckrucker (Agents of Edgewatch Player's Guide, 2020-07-08) -- `background-192`

  - Harbor Guard Moonlighter (Agents of Edgewatch Player's Guide, 2020-07-08) -- `background-193`

  - Learned Guard Prodigy (Agents of Edgewatch Player's Guide, 2020-07-08) -- `background-194`

  - Political Scion (Agents of Edgewatch Player's Guide, 2020-07-08) -- `background-195`

  - Post Guard of All Trade (Agents of Edgewatch Player's Guide, 2020-07-08) -- `background-196`

  - Sally Guard Neophyte (Agents of Edgewatch Player's Guide, 2020-07-08) -- `background-197`

  - Sleepless Suns Star (Agents of Edgewatch Player's Guide, 2020-07-08) -- `background-198`

  - Undercover Lotus Guard (Agents of Edgewatch Player's Guide, 2020-07-08) -- `background-199`

  - Archaeologist (PFS Guide, 2020-10-14) -- `background-202`

  - Pathfinder Recruiter (PFS Guide, 2020-10-14) -- `background-203`

  - Spell Seeker (PFS Guide, 2020-10-14) -- `background-204`

  - Trailblazer (PFS Guide, 2020-10-14) -- `background-205`

  - Translator (PFS Guide, 2020-10-14) -- `background-206`

  - Bibliophile (Abomination Vaults Player's Guide, 2021-01-15) -- `background-210`

  - Eldritch Anatomist (Abomination Vaults Player's Guide, 2021-01-15) -- `background-211`

  - Fogfen Tale-Teller (Abomination Vaults Player's Guide, 2021-01-15) -- `background-212`

  - Market Runner (Abomination Vaults Player's Guide, 2021-01-15) -- `background-213`

  - Ruin Delver (Abomination Vaults Player's Guide, 2021-01-15) -- `background-214`

  - Starwatcher (Abomination Vaults Player's Guide, 2021-01-15) -- `background-215`

  - Witchlight Follower (Abomination Vaults Player's Guide, 2021-01-15) -- `background-216`

  - Abadar's Avenger (Fists of the Ruby Phoenix Player's Guide, 2021-04-12) -- `background-217`

  - Attention Addict (Fists of the Ruby Phoenix Player's Guide, 2021-04-12) -- `background-218`

  - Newcomer in Need (Fists of the Ruby Phoenix Player's Guide, 2021-04-12) -- `background-219`

  - Ruby Phoenix Fanatic (Fists of the Ruby Phoenix Player's Guide, 2021-04-12) -- `background-220`

  - Second Chance Champion (Fists of the Ruby Phoenix Player's Guide, 2021-04-12) -- `background-221`

  - Undercover Contender (Fists of the Ruby Phoenix Player's Guide, 2021-04-12) -- `background-222`

  - Sponsored by Family (Strength of Thousands Player's Guide, 2021-07-26) -- `background-223`

  - Sponsored by Teacher Ot (Strength of Thousands Player's Guide, 2021-07-26) -- `background-224`

  - Sponsored by a Stranger (Strength of Thousands Player's Guide, 2021-07-26) -- `background-225`

  - Sponsored by a Village (Strength of Thousands Player's Guide, 2021-07-26) -- `background-226`

  - Unsponsored (Strength of Thousands Player's Guide, 2021-07-26) -- `background-227`

  - Broken Tusk Recruiter (Quest for the Frozen Flame Player's Guide, 2021-12-20) -- `background-289`

  - Ex-Mendevian Crusader (Quest for the Frozen Flame Player's Guide, 2021-12-20) -- `background-290`

  - Megafauna Hunter (Quest for the Frozen Flame Player's Guide, 2021-12-20) -- `background-291`

  - Mammoth Herder (Quest for the Frozen Flame Player's Guide, 2021-12-20) -- `background-292`

  - Northland Forager (Quest for the Frozen Flame Player's Guide, 2021-12-20) -- `background-293`

  - Songsinger in Training (Quest for the Frozen Flame Player's Guide, 2021-12-20) -- `background-294`

  - Banished Brighite (Outlaws of Alkenstar Player's Guide, 2022-03-28) -- `background-295`

  - Framed in Ferrous Quarter (Outlaws of Alkenstar Player's Guide, 2022-03-28) -- `background-296`

  - Inexplicably Expelled (Outlaws of Alkenstar Player's Guide, 2022-03-28) -- `background-297`

  - Ratted-Out Gun Runner (Outlaws of Alkenstar Player's Guide, 2022-03-28) -- `background-298`

  - Snubbed Out Stoolie (Outlaws of Alkenstar Player's Guide, 2022-03-28) -- `background-299`

  - Wanted Witness (Outlaws of Alkenstar Player's Guide, 2022-03-28) -- `background-300`

  - Reclaimed Investigator (Knights of Lastwall, 2022-05-25) -- `background-314`

  - Able Carter (Blood Lords Player's Guide, 2022-06-29) -- `background-318`

  - Construction Occultist (Blood Lords Player's Guide, 2022-06-29) -- `background-319`

  - Corpse Stitcher (Blood Lords Player's Guide, 2022-06-29) -- `background-320`

  - Food Trader (Blood Lords Player's Guide, 2022-06-29) -- `background-321`

  - Money Counter (Blood Lords Player's Guide, 2022-06-29) -- `background-322`

  - Propaganda Promoter (Blood Lords Player's Guide, 2022-06-29) -- `background-323`

  - Borderlands Pioneer (Kingmaker Adventure Path, 2022-10-26) -- `background-337`

  - Brevic Noble (Kingmaker Adventure Path, 2022-10-26) -- `background-338`

  - Brevic Outcast (Kingmaker Adventure Path, 2022-10-26) -- `background-339`

  - Issian Patriot (Kingmaker Adventure Path, 2022-10-26) -- `background-340`

  - Local Brigand (Kingmaker Adventure Path, 2022-10-26) -- `background-341`

  - Rostlander (Kingmaker Adventure Path, 2022-10-26) -- `background-342`

  - Sword Scion (Kingmaker Adventure Path, 2022-10-26) -- `background-343`

  - Muesello's Student (Pathfinder Society Year 4 Rule Updates, 2022-06-30) -- `background-350`

  - Bookish Providence (Stolen Fate Player's Guide, 2023-04-13) -- `background-364`

  - Crown of Chaos (Stolen Fate Player's Guide, 2023-04-13) -- `background-365`

  - Hammered by Fate (Stolen Fate Player's Guide, 2023-04-13) -- `background-366`

  - Keys to Destiny (Stolen Fate Player's Guide, 2023-04-13) -- `background-367`

  - Shielded Fortune (Stolen Fate Player's Guide, 2023-04-13) -- `background-368`

  - Writ in the Stars (Stolen Fate Player's Guide, 2023-04-13) -- `background-369`

  - Child of Notoriety (Sky King's Tomb Player's Guide, 2023-07-13) -- `background-387`

  - Clan Associate (Sky King's Tomb Player's Guide, 2023-07-13) -- `background-388`

  - Conservator (Sky King's Tomb Player's Guide, 2023-07-13) -- `background-389`

  - Dedicated Delver (Sky King's Tomb Player's Guide, 2023-07-13) -- `background-390`

  - Eclectic Scholar (Sky King's Tomb Player's Guide, 2023-07-13) -- `background-391`

  - Historical Reeanactor (Sky King's Tomb Player's Guide, 2023-07-13) -- `background-392`

  - Close Ties (Season of Ghosts Player's Guide, 2023-10-02) -- `background-393`

  - Folklore Enthusiast (Season of Ghosts Player's Guide, 2023-10-02) -- `background-394`

  - Northridge Scholar (Season of Ghosts Player's Guide, 2023-10-02) -- `background-395`

  - Outskirt Dweller (Season of Ghosts Player's Guide, 2023-10-02) -- `background-396`

  - Southbank Traditionalist (Season of Ghosts Player's Guide, 2023-10-02) -- `background-397`

  - Willowshore Urchin (Season of Ghosts Player's Guide, 2023-10-02) -- `background-398`

  - Refugee (FoP) (The Fall of Plaguestone, 2019-08-01) -- `background-40`

  - Dragon Scholar (Age of Ashes Player's Guide, 2019-08-01) -- `background-42`

  - Emancipated (Age of Ashes Player's Guide, 2019-08-01) -- `background-43`

  - Haunting Vision (Age of Ashes Player's Guide, 2019-08-01) -- `background-44`

  - Hellknight Historian (Age of Ashes Player's Guide, 2019-08-01) -- `background-45`

  - Local Scion (Age of Ashes Player's Guide, 2019-08-01) -- `background-46`

  - Out-of-Towner (Age of Ashes Player's Guide, 2019-08-01) -- `background-47`

  - Reputation Seeker (Age of Ashes Player's Guide, 2019-08-01) -- `background-48`

  - Returning Descendant (Age of Ashes Player's Guide, 2019-08-01) -- `background-49`

  - Truth Seeker (Age of Ashes Player's Guide, 2019-08-01) -- `background-50`


**Nota sobre Aasimar/Tiefling -> Nephilim:** o AoN nao tem `remaster_id` ligando Aasimar (`heritage-84`, Advanced Player's Guide) nem Tiefling (`heritage-86`, Advanced Player's Guide) a nada -- por isso aparecem acima em "sem substituto", nao em "renomeados". Confirmado por leitura direta: nenhuma das duas existe no Foundry (nem como heritage remaster nem legacy), e o texto de Nephilim (`heritage-280`, Player Core, presente no Foundry como versatile heritage) e mecanicamente identico ao template de Aasimar/Tiefling ("ganha o trait X, visao adicional, escolhe feats de X ou da ancestria"), so generalizado pra herança unica que cobre celestial/fiend/monitor. E fusao estrutural, nao substituicao 1:1 -- por isso o AoN nao registrou ponte automatica e o merge tem que ser manual.

## Campos nao mapeados

- **`ancestry.items`** (equipamento concedido, ex.: Clan Dagger do Dwarf, presente em 36/50 ancestrias do Foundry): fora do escopo pedido (hp/size/speed/boosts/flaw/languages/traits/senses/heritages). Nao emitido.

- **`heritage.grants` parcial**: o Foundry usa ~20 tipos de rule element distintos nas heranças (GrantItem, ActiveEffectLike, ItemAlteration, Sense, Resistance, AdjustDegreeOfSuccess, RollOption, Strike, BaseSpeed, ChoiceSet, Note, CreatureSize, ActorTraits, TokenLight, DamageDice, Aura, AdjustModifier, AdjustStrike, Weakness). So `FlatModifier` foi traduzido pra linguagem de efeito do schema (bate 1:1 com o exemplo do contrato). `mechanized=true` em 68/326 registros (41 deles por nao terem rule element nenhum -- heranças puramente narrativas). O resto precisa do interpretador de rule elements (item de trabalho proprio, ja registrado em LESSONS.md do projeto).

- **`background.feats_granted` como lista, nao campo singular**: 2 backgrounds (Hermean Heritor, Returned) concedem 2 feats, nao 1. Campo sai como lista em vez de objeto unico.

- **Ancestrias sem par no AoN**: 0 -- (nenhuma)

- **Heranças sem par no AoN**: 4

- Ambitious Human
- Battle-Trained Human (BB)
- Naari
- Warden Human (BB)

- **Backgrounds sem par no AoN**: 3

- Reclaimer Investigator
- Refugee (Fall of Plaguestone)
- Refugee (PC2)

- **Pareamento por nome normalizado (fallback)**: 2 registros so casaram com AoN depois de derrubar parenteses/hifen (grafia diverge entre Foundry e AoN, mesmo registro). Sem esse fallback, esses apareceriam como "sem par" ou, do lado do mapa Legacy->Remaster, como "removido":

- background: Foundry "Aspiring Free-Captain" ~ AoN "Aspiring Free Captain" (background-81)
- background: Foundry "Oenopion-Ooze Tender" ~ AoN "Oenopion Ooze-Tender" (background-92)

## Divergencias entre fontes

Conflitos formais (campo por campo, foundry vs aon) ficam no array `conflitos` de cada registro em `ancestrias.json`. Abaixo, divergencias encontradas contra a terceira fonte (pf2etools), que nao vence nenhum campo nesta kind mas serve de checagem:

- background/eidolon-contact: skills foundry=[] pf2etools=['arcana', 'nature', 'occultism', 'religion']
- background/feybound: skills foundry=[] pf2etools=['nature']
- background/harrow-led: skills foundry=[] pf2etools=['occultism', 'performance', 'society']
- background/herbalist: skills foundry=['nature'] pf2etools=['medicine', 'nature']
- background/hermit: skills foundry=[] pf2etools=['nature', 'occultism']
- background/magaambya-academic: skills foundry=[] pf2etools=['arcana', 'nature']
- background/martial-disciple: skills foundry=[] pf2etools=['acrobatics', 'athletics']
- background/mystic-tutor: skills foundry=[] pf2etools=['arcana', 'occultism']
- background/osprey-spellcaster: skills foundry=[] pf2etools=['arcana', 'nature', 'occultism', 'religion']
- background/pillar: skills foundry=[] pf2etools=['medicine', 'society', 'survival']
- background/raised-by-belief: skills foundry=[] pf2etools=['acrobatics', 'arcana', 'athletics', 'crafting', 'deception', 'diplomacy', 'intimidation', 'medicine', 'nature', 'occultism', 'performance', 'religion', 'society', 'stealth', 'survival', 'thievery']
- background/scholar: skills foundry=[] pf2etools=['arcana', 'nature', 'occultism', 'religion']
- background/student-of-magic: skills foundry=[] pf2etools=['arcana', 'nature', 'occultism', 'religion']
- background/surge-investigator: skills foundry=[] pf2etools=['nature', 'occultism']
- background/teacher: skills foundry=[] pf2etools=['performance', 'society']
- background/tech-reliant: skills foundry=['crafting', 'medicine'] pf2etools=['crafting']
- background/wildwood-local: skills foundry=['nature'] pf2etools=['medicine', 'nature']

## Casos RAW notaveis (nao sao bug do extrator)

- Human: dois boosts livres, zero flaw (RAW correto pos-remaster).
- Amnesiac (background, Player Core 2): 3 boosts livres, sem skill_training, sem feat -- background genuinamente atipico.
- Farmhand e outros ~60 backgrounds: sem feat concedido (`feats_granted=[]`) -- RAW, nao falha de extracao.
- Faction Opportunist (background): lore com string livre "or Mercantile Lore" dentro da lista -- dado cru do Foundry, mantido como veio (nao normalizado).
- 19/50 ancestrias e 121/326 heranças no Foundry ainda sao Legacy/OGL (`source.remaster=false`) -- nunca foram remasterizadas oficialmente (ex.: Android, Anadi, Kitsune, Sprite, Strix, Skeleton).

