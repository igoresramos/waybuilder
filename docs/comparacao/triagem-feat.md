# Triagem de divergencias -- FEATS (Waybuilder vs Archives of Nethys)

Fonte: `docs/comparacao/aon/feat.json` (cruzamento offline gerado por `pipeline/comparar_com_aon.py`).
Metodo: `python3` via Bash sobre `pipeline/base/index.json`, `pipeline/dados_brutos/aon_feats.json` e `pipeline/dados_brutos/foundry/packs/pf2e/feats/**`, sem despejar JSON grande. Nenhum arquivo do pipeline foi alterado -- diagnostico puro.

## 1. Tabela-resumo

| Categoria | Qtde | Onde |
|---|---|---|
| F-RENAME | 142 | 116 em `faltam_em_nos` + 26 em `so_nosso` |
| F-VARIANTE | 101 | 42 em `faltam_em_nos` + 59 em `so_nosso` |
| A-FALTA-REAL | 5 | `faltam_em_nos` (conteudo nao-canonico, exclusao correta) |
| B-SOBRA-NOVA | 30 | `so_nosso` |
| C-CAMPO (nivel/raridade) | 27 | 21 `nivel_divergente` + 6 `raridade_divergente` |
| INDECISO | 1 | `so_nosso` ("Stance Savant") |
| **Total triado** | **306** | 163 + 116 + 21 + 6 |

Achado central: **nenhum dos 163 itens de `faltam_em_nos` e uma lacuna real de conteudo.** Todos os 163 se explicam por rename/merge ja rastreado via `legado_de`/`aliases`/`historico`, ou sao conteudo nao-canonico (April Fools) que a base corretamente nao inclui. O problema esta no comparador (`comparar_com_aon.py`), que casa por `norm(name)` puro e ignora `legado_de`/`aliases` -- fonte de praticamente todo falso-positivo encontrado nas 4 listas, inclusive nos 21+6 itens de `nivel`/`raridade` divergente (15 dos 27 sao artefato do mesmo bug: colisao de nome faz o dict em Python sobrescrever silenciosamente qual registro AoN entra na comparacao).

## 2. `faltam_em_nos` (163) -- AoN tem, nossa base "nao tem"

### 2.1 F-RENAME (116) -- existe sob outro nome

Evidencia: o `id` do AoN (extraido do proprio dump) aparece no campo `legado_de` (ou, num caso, em `aliases`/`historico`) da nossa entrada atual -- ligacao por id, nao por heuristica de nome.

| Nome no AoN | Nosso nome atual | Nosso id | Id AoN (evidencia) |
|---|---|---|---|
| Aasimar's Mercy | Celestial Mercy | `wb:feat/celestial-mercy` | `feat-1362` |
| Alchemical Savant | Alchemical Assessment | `wb:feat/alchemical-assessment` | `feat-93` |
| Align Armament | Sanctify Armament | `wb:feat/sanctify-armament` | `feat-286` |
| Align Ki | Align Qi | `wb:feat/align-qi` | `feat-1740` |
| Anchoring Aura | Aura of Righteousness | `wb:feat/aura-of-righteousness` | `feat-249` |
| Armiger's Mobility | Hellknight Mobility | `wb:feat/hellknight-mobility` | `feat-911` |
| Arrow Snatching | Projectile Snatching | `wb:feat/projectile-snatching` | `feat-458` |
| Arrow of Death | Fatal Shot | `wb:feat/fatal-shot` | `feat-1968` |
| Attack of Opportunity | Reactive Strike | `wb:feat/reactive-strike` | `feat-145` |
| Bespell Weapon | Bespell Strikes | `wb:feat/bespell-strikes` | `feat-610` |
| Blessed Blood (Aasimar) | Blessed Blood (Nephilim) | `wb:feat/blessed-blood-nephilim` | `feat-1354` |
| Bone Rider | Fossil Rider | `wb:feat/fossil-rider` | `feat-2845` |
| Buckler Expertise | Elegant Buckler | `wb:feat/elegant-buckler` | `feat-1512` |
| Call Bonded Item | Call Wizardly Tools | `wb:feat/call-wizardly-tools` | `feat-1836` |
| Channeled Succor | Restorative Channel | `wb:feat/restorative-channel` | `feat-287` |
| Combat Reflexes | Tactical Reflexes | `wb:feat/tactical-reflexes` | `feat-398` |
| Courageous Opportunity | Reflexive Courage | `wb:feat/reflexive-courage` | `feat-1646` |
| Critical Debilitations | Critical Debilitation | `wb:feat/critical-debilitation` | `feat-582` |
| Crystalline Cloud | Extraplanar Cloud | `wb:feat/extraplanar-cloud` | `feat-2485` |
| Crystalline Dust | Extraplanar Haze | `wb:feat/extraplanar-haze` | `feat-2480` |
| Deflect Arrow | Deflect Projectile | `wb:feat/deflect-projectile` | `feat-443` |
| Disrupt Ki | Disrupt Qi | `wb:feat/disrupt-qi` | `feat-469` |
| Divine Ally | Devout Blessing | `wb:feat/devout-blessing` | `feat-692` |
| Diviner Sense | Keen Magical Detection | `wb:feat/keen-magical-detection` | `feat-1840` |
| Drow Shootist Dedication | Crossbow Infiltrator Dedication | `wb:feat/crossbow-infiltrator-dedication` | `feat-2683` |
| Dueling Parry (Swashbuckler) | Extravagant Parry | `wb:feat/extravagant-parry` | `feat-1514` |
| Efficient Alchemy (Alchemist) | Efficient Alchemy | `wb:feat/efficient-alchemy` | `feat-100` |
| Enchanting Arrow | Enchanting Shot | `wb:feat/enchanting-shot` | `feat-1962` |
| Evasiveness (Swashbuckler) | Evasiveness | `wb:feat/evasiveness` | `feat-1865` |
| Expanded Luck | Lucky Break | `wb:feat/lucky-break` | `feat-1259` |
| Expert Disassembler | Expert Disassembly | `wb:feat/expert-disassembly` | `feat-2061` |
| Extend Armament Alignment | Lasting Armament | `wb:feat/lasting-armament` | `feat-299` |
| Exude Abyssal Corruption | Exude Demonic Corruption | `wb:feat/exude-demonic-corruption` | `feat-3818` |
| Eyes of the Night | Eyes of Night | `wb:feat/eyes-of-night` | `feat-1335` |
| Favored Enemy | Favored Prey | `wb:feat/favored-prey` | `feat-503` |
| Feral Mutagen | Mutant Physique | `wb:feat/mutant-physique` | `feat-105` |
| Fiend's Door | Slip Sideways | `wb:feat/slip-sideways` | `feat-1392` |
| Firearm Expert | Advanced Firearm Familiarity | `wb:feat/advanced-firearm-familiarity` | `feat-8726` |
| Flicker | Flickering Twirl | `wb:feat/flickering-twirl` | `feat-922` |
| Forge-Blessd Shot | Forge-Blessed Shot | `wb:feat/forge-blessed-shot` | `feat-8797` |
| Form Lock (Wrestler) | Form Lock | `wb:feat/form-lock` | `feat-3405` |
| Glib Mutagen | Mutant Innervation | `wb:feat/mutant-innervation` | `feat-116` |
| Gnoll Lore | Kholo Lore | `wb:feat/kholo-lore` | `feat-2791` |
| Gnoll Weapon Familiarity | Kholo Weapon Familiarity | `wb:feat/kholo-weapon-familiarity` | `feat-2792` |
| Grippli Weapon Familiarity | Tripkee Weapon Familiarity | `wb:feat/tripkee-weapon-familiarity` | `feat-2818` |
| Harbinger's Caw | Harbinger's Claw | `wb:feat/harbingers-claw` | `feat-2442` |
| Healing Touch | Devout Magic | `wb:feat/devout-magic` | `feat-689` |
| Hellknight Armiger Dedication | Hellknight Dedication | `wb:feat/hellknight-dedication` | `feat-907` |
| Hellknight Order Cross-Training | Order Cross-Training | `wb:feat/order-cross-training` | `feat-1077` |
| Hellknight Signifer Dedication | Hellknight Signifer Preferment | `wb:feat/hellknight-signifer-preferment` | `feat-1082` |
| Holy Castigation | Divine Castigation | `wb:feat/divine-castigation` | `feat-268` |
| Impose Order (Aphorite) | Impose Order | `wb:feat/impose-order` | `feat-2487` |
| Improved Knockdown | Crashing Slam | `wb:feat/crashing-slam` | `feat-403` |
| Inspirational Performance | Anthemic Performance | `wb:feat/anthemic-performance` | `feat-682` |
| Inspire Competence | Uplifting Overture | `wb:feat/uplifting-overture` | `feat-185` |
| Inspire Defense | Rallying Anthem | `wb:feat/rallying-anthem` | `feat-188` |
| Inspire Heroics | Fortissimo Composition | `wb:feat/fortissimo-composition` | `feat-196` |
| Intercorporate | Resilient Physiology | `wb:feat/resilient-physiology` | `feat-2481` |
| Internal Cohesion | Aeonbound | `wb:feat/aeonbound` | `feat-2477` |
| Ki Center | Qi Center | `wb:feat/qi-center` | `feat-1759` |
| Knockdown | Slam Down | `wb:feat/slam-down` | `feat-372` |
| Laughing Gnoll | Laughing Kholo | `wb:feat/laughing-kholo` | `feat-2802` |
| Leech-Clipper | Leech-Clip | `wb:feat/leech-clip` | `feat-1027` |
| Light from Darkness | Divine Countermeasures | `wb:feat/divine-countermeasures` | `feat-1391` |
| Magic Arrow | Magic Ammunition | `wb:feat/magic-ammunition` | `feat-1963` |
| Metamagic Channel | Spellshape Channel | `wb:feat/spellshape-channel` | `feat-310` |
| Metamagic Mastery | Spellshape Mastery | `wb:feat/spellshape-mastery` | `feat-632` |
| Nocturnal Sense | Nocturnal Senses | `wb:feat/nocturnal-senses` | `feat-1611` |
| Opportunist | Reactive Striker | `wb:feat/reactive-striker` | `feat-712` |
| Phase Arrow | Incorporeal Shot | `wb:feat/incorporeal-shot` | `feat-1967` |
| Pirate Weapon Training | Pirate Combat Training | `wb:feat/pirate-combat-training` | `feat-2033` |
| Point-Blank Shot | Point Blank Stance | `wb:feat/point-blank-stance` | `feat-358` |
| Power Attack | Vicious Swing | `wb:feat/vicious-swing` | `feat-359` |
| Precious Arrow | Precious Ammunition | `wb:feat/precious-ammunition` | `feat-1964` |
| Quick Stow (Ratfolk) | Quick Stow | `wb:feat/quick-stow` | `feat-1304` |
| Radiant Blade Master | Armament Paragon | `wb:feat/armament-paragon` | `feat-262` |
| Radiant Blade Spirit | Radiant Armament | `wb:feat/radiant-armament` | `feat-240` |
| Radiant Infusion | Divine Infusion | `wb:feat/divine-infusion` | `feat-1699` |
| Ranged Reprisal | Nimble Reprisal | `wb:feat/nimble-reprisal` | `feat-215` |
| Ratfolk Growth | Greater than the Sum | `wb:feat/greater-than-the-sum` | `feat-2433` |
| Scattering Shot | Shattering Shot | `wb:feat/shattering-shot` | `feat-8699` |
| Scroll Savant | Scroll Adept | `wb:feat/scroll-adept` | `feat-652` |
| Second Ally | Second Blessing | `wb:feat/second-blessing` | `feat-235` |
| Second Chance Spell | Second Thoughts | `wb:feat/second-thoughts` | `feat-1842` |
| Seeker Arrow | Homing Shot | `wb:feat/homing-shot` | `feat-1966` |
| Sense Chaos | Sense Iniquity | `wb:feat/sense-iniquity` | `feat-1079` |
| Sense Evil | Sense Unholiness | `wb:feat/sense-unholiness` | `feat-236` |
| Sense Good | Sense Holiness | `wb:feat/sense-holiness` | `feat-1679` |
| Shared Luck (Catfolk) | Luck of the Clowder | `wb:feat/luck-of-the-clowder` | `feat-1263` |
| Skill Mastery (Investigator) | Skill Mastery | `wb:feat/skill-mastery` | `feat-1849` |
| Skillful Tail (Ganzi) | Skillful Tail | `wb:feat/skillful-tail` | `feat-2538` |
| Snap Out of It! (Marshal) | Snap Out of It! | `wb:feat/snap-out-of-it` | `feat-2008` |
| Sneak Savant | Sneak Adept | `wb:feat/sneak-adept` | `feat-579` |
| Solar Rejuvenation (Leshy) | Solar Rejuvenation | `wb:feat/solar-rejuvenation` | `feat-1049` |
| Spell Penetration | Irresistible Magic | `wb:feat/irresistible-magic` | `feat-645` |
| Spirit Strikes | Quietus Strikes | `wb:feat/quietus-strikes` | `feat-1374` |
| Spring Attack | Dashing Strike | `wb:feat/dashing-strike` | `feat-413` |
| Stance Savant (Fighter) | Opening Stance (Fighter) | `wb:feat/opening-stance-fighter` | `feat-419` |
| Stance Savant (Monk) | Reflexive Stance | `wb:feat/reflexive-stance` | `feat-472` |
| Startling Appearance (Vigilante) | Startling Appearance | `wb:feat/startling-appearance` | `feat-2088` |
| Stonecunning | Stonemason's Eye | `wb:feat/stonemasons-eye` | `feat-4` |
| Stunning Fist | Stunning Blows | `wb:feat/stunning-blows` | `feat-442` |
| Subtle Delivery | Blowgun Poisoner | `wb:feat/blowgun-poisoner` | `feat-1593` |
| Temporary Potions | Double, Double | `wb:feat/double-double` | `feat-1580` |
| Thousand Faces | Anthropomorphic Shape | `wb:feat/anthropomorphic-shape` | `feat-324` |
| Timeless Body | Peerless Form | `wb:feat/peerless-form` | `feat-476` |
| Tree Climber (Elf) | Tree Climber | `wb:feat/tree-climber` | `feat-1413` |
| Turn Undead | Panic the Dead | `wb:feat/panic-the-dead` | `feat-274` |
| Vanth's Weapon Familiarity | Duskwalker Weapon Familiarity | `wb:feat/duskwalker-weapon-familiarity` | `feat-2357` |
| Vengeful Hatred | Mountain Strategy | `wb:feat/mountain-strategy` | `feat-6` |
| Vengeful Oath | Oath of The Avenger | `wb:feat/oath-of-the-avenger` | `feat-222` |
| Vigorous Inspiration | Vigorous Anthem | `wb:feat/vigorous-anthem` | `feat-1657` |
| Wholeness of Body | Harmonize Self | `wb:feat/harmonize-self` | `feat-448` |
| Wild Shape | Untamed Form | `wb:feat/untamed-form` | `feat-316` |
| Woodland Stride | Forest Passage | `wb:feat/forest-passage` | `feat-325` |
| Master Spotter (Investigator) | Master Spotter | `wb:feat/master-spotter-investigator` | `feat-1850` (via `aliases`+`historico`, ja anotado na base como "sucessor ausente da base") |

Acao proposta: nenhuma na base -- os dados ja estao corretos. Ajustar o comparador para casar tambem por `legado_de`/`aliases`/`historico` antes de reportar `faltam_em_nos` (ver secao 5).

### 2.2 F-VARIANTE (42) -- merge: AoN tinha entradas separadas, nos consolidamos

Evidencia: multiplos ids legados do AoN (`legado_de`) convergem para a MESMA entrada nossa -- normalmente consolidacao do remaster (ex.: variantes por ancestralidade Aasimar/Tiefling/Ganzi viraram uma unica entrada "Nephilim X"; "Smite Evil"+"Smite Good" -> "Smite"; Ki->Qi).

| Nosso alvo consolidado | Nomes legados no AoN (id) |
|---|---|
| Advanced Qi Spells (`wb:feat/advanced-qi-spells`) | Abundant Step (`feat-449`), Ki Blast (`feat-452`) |
| Bestial Manifestation (`wb:feat/bestial-manifestation`) | Form of the Fiend (`feat-1379`), Smashing Tail (`feat-2535`) |
| Celestial Magic (`wb:feat/celestial-magic`) | Angelic Magic (`feat-1357`), Archon Magic (`feat-1358`), Empyreal Blessing (`feat-1356`) |
| Divine Declaration (`wb:feat/divine-declaration`) | Celestial Word (`feat-1365`), Fiendish Word (`feat-1395`) |
| Divine Wings (`wb:feat/divine-wings`) | Celestial Wings (`feat-1360`), Fiendish Wings (`feat-1390`) |
| Eternal Wings (`wb:feat/eternal-wings`) | Eternal Wings (Aasimar) (`feat-1366`), Relentless Wings (`feat-1396`) |
| Extraplanar Supplication (`wb:feat/extraplanar-supplication`) | Empyreal Blessing (`feat-1356`), Malicious Bane (`feat-1385`) |
| Fiendish Magic (`wb:feat/fiendish-magic`) | Daemon Magic (`feat-1387`), Demon Magic (`feat-1388`), Devil Magic (`feat-1389`) |
| Iruxi Armaments (`wb:feat/iruxi-armaments`) | Razor Claws (`feat-1053`), Sharp Fangs (`feat-1055`), Tail Whip (`feat-1056`) |
| Leverage Connections (`wb:feat/leverage-connections`) | Connections (`feat-770`), Criminal Connections (`feat-2119`), Quick Contacts (`feat-2144`) |
| Nephilim Eyes (`wb:feat/nephilim-eyes`) | Celestial Eyes (`feat-1349`), Fiendish Eyes (`feat-1377`), Ganzi Gaze (`feat-2533`), Lemma of Vision (`feat-2479`) |
| Nephilim Lore (`wb:feat/nephilim-lore`) | Celestial Lore (`feat-1350`), Fiendish Lore (`feat-1378`) |
| Nephilim Resistance (`wb:feat/nephilim-resistance`) | Celestial Resistance (`feat-1355`), Fiendish Resistance (`feat-1384`) |
| Oath of The Slayer (`wb:feat/oath-of-the-slayer`) | Dragonslayer Oath (`feat-219`), Esoteric Oath (`feat-1669`), Fiendsbane Oath (`feat-220`), Lightslayer Oath (`feat-1670`), Shining Oath (`feat-221`) |
| Qi Spells (`wb:feat/qi-spells`) | Ki Rush (`feat-432`), Ki Strike (`feat-433`) |
| Smite (`wb:feat/smite`) | Smite Evil (`feat-230`), Smite Good (`feat-1676`) |
| Summon Nephilim Kin (`wb:feat/summon-nephilim-kin`) | Summon Celestial Kin (`feat-1364`), Summon Fiendish Kin (`feat-1394`) |

Acao proposta: nenhuma -- consolidacao correta e ja documentada via `legado_de`. Mesmo ajuste de comparador da secao 2.1 resolve o falso-positivo.

### 2.3 A-FALTA-REAL (5) -- conteudo nao-canonico, ausencia correta

Evidencia: sem `id_hits`, `alias_hits`, `hist_hits`, partial ou fuzzy match. Busca no dump bruto do AoN mostra `primary_source: "Fools Aplenty"`, `release_date: 2026-04-01` -- pegadinha de April Fools do blog da Paizo, marcada no proprio texto do AoN como `Nethys Note: This is a part of the April Fool's content`.

| Nome | Id AoN | Nivel | Fonte AoN |
|---|---|---|---|
| Dad Joke | `feat-8803` | 1 | Fools Aplenty |
| GGGHhhjjjJJK | `feat-8804` | 1 | Fools Aplenty |
| Wombat Bastion | `feat-8799` | 6 | Fools Aplenty |
| Wombat Burrow | `feat-8801` | 10 | Fools Aplenty |
| Wombat Style | `feat-8798` | 1 | Fools Aplenty |

Acao proposta: nenhuma na base. Se quiser blindar o comparador contra ruido futuro do mesmo tipo, adicionar filtro por `primary_source == "Fools Aplenty"` (ou por `release_date` == 1o de abril) em `carregar_aon()`.

## 3. `so_nosso` (116) -- nos temos, o dump do AoN "nao tem"

### 3.1 F-VARIANTE -- split por classe/arquetipo (36)

Evidencia: nossa entrada tem sufixo `(Classe)`; a base sem sufixo existe no AoN sob o MESMO id normalizado do sufixo removido, com 2+ registros do AoN (ids diferentes) compartilhando o nome-base -- ou seja, o AoN diferencia por pre-requisito/arquetipo no corpo do texto, nao no campo `name`, e o comparador (que so olha `name`) colapsa os dois num so. Nossa base separa em entradas com nome distinto, o que e mais correto para catalogo, so nao bate 1:1 com o dump.

| Nome (nosso, com sufixo) |
|---|
| Animal Companion (Ranger) |
| Breath of the Dragon (Dragon Disciple) |
| Breath of the Dragon (Dragonblood) |
| Counterspell (Prepared) |
| Counterspell (Spontaneous) |
| Daywalker (Vampire) |
| Death from Above (Eternal Legend) |
| Draconic Scent (Dragon Disciple) |
| Elemental Familiar (Elementalist) |
| Eternal Wings (Nephilim) |
| Even the Odds (Eagle Knight) |
| Incredible Familiar (Animist) |
| Incredible Luck (Swashbuckler) |
| Inner Fire (Monk) |
| Inner Fire (Naari) |
| Irrepressible (Halfling) |
| Irrepressible (Nephilim) |
| Know It All (Eldritch Researcher) |
| Knowledge is Power (Wizard) |
| Magic Sense (Magus) |
| Many Guises (Kitsune) |
| Many Guises (Vigilante) |
| Necromantic Resistance (Undead Slayer) |
| Play to the Crowd (Dandy) |
| Rallying Charge (Knight Vigilant) |
| Rallying Charge (Marshal) |
| Riptide (Undersea Privateer) |
| Signature Spell Expansion (Psychic) |
| Soulsight (Bard) |
| Soulsight (Sorcerer) |
| Specialized Companion (Animal Trainer) |
| Stone Blood (Stonebound) |
| Trample (Sarangay) |
| Tusks (Half-Orc) |
| Tusks (Orc) |
| Watch Your Back (Golden Legionnaire) |

Acao proposta: nenhuma -- split legitimo. Nao mudar; se quiser, documentar a convencao no proprio pipeline (`legado_de`/comentario) para deixar claro que e decisao editorial, nao lacuna.

### 3.2 F-VARIANTE -- provavel duplicata bare + variantes por classe (23)

Evidencia mais forte que 3.1: para cada nome abaixo, a base tem uma entrada SEM sufixo (a que aparece em `so_nosso`) e TAMBEM 1-3 entradas `Nome (Classe)` com xref proprio para o AoN. A entrada sem sufixo geralmente nao tem `xref.aon` (so `xref.foundry`/`pf2etools`) e seu nivel bate exatamente com uma das variantes ja existentes -- ela e provavelmente resto do merge Foundry+AoN, nao conteudo adicional. Confirmado por amostragem: `wb:feat/animal-empathy` (nivel 1, so `xref.foundry`) duplica `wb:feat/animal-empathy-druid` (nivel 1, `xref.aon: feat-4709`); `wb:feat/dueling-parry` (nivel 2, so foundry) duplica `wb:feat/dueling-parry-fighter` (nivel 2, `aon: feat-4781`, `legado_de: feat-367`).

| Nome (base, sem sufixo) | Fonte | Nr de variantes `(Classe)` ja existentes na base |
|---|---|---|
| Animal Empathy | Player Core | 2 |
| Bear Hug | Treasure Vault (Remastered) | 2 |
| Blessed Blood | Player Core | 2 |
| Dueling Dance | Player Core | 2 |
| Dueling Parry | Player Core | 1 |
| Ghostly Grasp | Book of the Dead | 2 |
| Guarded Advance | Battlecry! | 2 |
| Improved Twin Riposte | Player Core | 2 |
| Incredible Companion | Player Core | 2 |
| Larger than Life | Tian Xia Character Guide | 2 |
| Mature Animal Companion | Player Core | 2 |
| Phalanx Formation | Battlecry! | 2 |
| Quick Recovery | Tian Xia Character Guide | 2 |
| Ricochet Stance | Player Core | 2 |
| Roll with It | Character Guide | 2 |
| Shared Luck | Advanced Player's Guide | 1 |
| Shattering Strike | Advanced Player's Guide | 2 |
| Side by Side | Player Core | 2 |
| Silence the Profane | War of Immortals | 2 |
| Spirit Familiar | Player Core | 2 |
| The Harder They Fall | Player Core | 3 |
| Tumble Behind | Player Core | 2 |
| Twinned Defense | Player Core | 2 |

Acao proposta: revisar cada uma das 23 entradas-base contra o texto real (Archives of Nethys ao vivo ou o livro) para decidir se e (a) generica de fato e deve ficar, so sem `xref.aon` valido, ou (b) duplicata morta que deveria ser removida/mesclada numa das variantes com sufixo. Prioridade media -- nao quebra nada hoje, mas infla a contagem de feats e pode confundir o usuario final vendo 3 "Dueling Parry" na lista.

### 3.3 F-RENAME por erro de grafia no dump do AoN (26)

Evidencia: nome nosso nao bate normalizado, mas bate por fuzzy match (>=82% similaridade) contra um registro do AoN com MESMO nivel e MESMO livro-fonte -- confirmado item a item. O padrao (letra faltando/trocada) e consistente com erro de digitacao no proprio texto indexado pelo AoN, nao no nosso lado -- nosso nome geralmente e a grafia correta em ingles.

| Nosso nome | Nome no dump do AoN | Nivel (bate nos dois) |
|---|---|---|
| Certain Stratagem | Certain Strategem | 2 |
| Harsh Judgement | Harsh Judgment | 4 |
| Vindicator's Judgment | Vindicator's Judgement | 10 |
| Pass Vengeful Judgment | Pass Vengeful Judgement | 18 |
| Flash of Omnipotence | Flash of Omipotence | 20 |
| Remember Their Names | Remember thy Names | 16 |
| Repulse the Wicked | Repulse the Wicken | 6 |
| Empathic Envoy | Empathetic Envoy | 4 |
| Opportune Trickster | Oppurtune Trickster | 6 |
| Orator's Filibuster | Orator's Fillibuster | 8 |
| Exemplar Resiliency | Exemplar Resilency | 4 |
| Faultless Defense | Fautless Defense | 14 |
| Decree of Banishment | Decree of Banisment | 14 |
| Innate Magical Intuition | Innate Magic Intuition | 8 |
| Master Summoning Spellcasting | Master Summoner Spellcasting | 18 |
| Vengeful Remnant | Vengful Remnant | 14 |
| Vermillion Threads | Vermilion Threads | 10 |
| Voice of Elements | Voice of the Elements (Rage of Elements) | 2 |
| Whispers of Warning | Whisper of Warning | 12 |
| Ceremony of Strengthened Hand | Ceremony of the Strengthened Hand | 9 |
| Emboldened with Glorious Purpose | Embolded With Glorious Purpose | 18 |
| Judgement of the Monolith | Judgment of the Monolith | 12 |
| No Hands, No Problem | No Hands, No Problems | 5 |
| Recycled Cogwheels | Recycled Cogwheel | 8 |
| Lotus Above the Wind | Lotus Above the Mud | 6 |
| Luring Chomp | Lurching Chomp | 13 |

Acao proposta: nenhuma na base -- os dois ultimos ("Lotus Above the Wind"/"Mud", "Luring Chomp"/"Lurching Chomp") tem diferenca grande o suficiente pra valer conferencia manual contra o PDF do livro (Tian Xia Character Guide / Draconic Codex), so pra garantir que a nossa grafia e a oficial e nao um erro de transcricao nosso -- prioridade baixa, sem impacto mecanico.

### 3.4 B-SOBRA-NOVA -- conteudo real que o dump nao indexa como Feat (30)

**Grupo A -- "bonus feats" de ordem Hellknight (14).** Todas nivel 0, `feat_category: "bonus"`, `prov.name: "foundry"` (sem `xref.aon`), concedidas automaticamente por escolher uma Ordem Hellknight (ex.: `requires: has wb:class-feature/order-of-the-godclaw`). O AoN as descreve dentro do texto da propria feature de Ordem, nao como pagina de Feat separada -- por isso nunca vao aparecer no dump de feats.
Blessing of the Five, Dedication to the Five, Devil Allies, Disillusionment, Fear No Law, Fear No One, Locate Lawbreakers, Reveal Beasts, Righteous Resistance, Seek Injustice, Shackles of Law, Silence Heresy, Spiritual Disruption, Sturdy Bindings, Trailblazing Stride (todas `wb:archetype/hellknight`, Hellfire Dispatches).

**Grupo B -- boons de aventura (6).** `Avenger of {Envy, Gluttony, Greed, Lust, Sloth, Wrath}`, fonte "Pathfinder #220: Crypt of Runes" (Adventure Path). AoN normalmente nao indexa boons especificos de modulo como Feat pesquisavel.

**Grupo C -- feature de classe empacotada como feat pelo Foundry (2).** `Powerful Alchemy` (Core Rulebook, Alchemist) e `Invulnerable Juggernaut` -- ambas sem `feat_category` definido, sugerindo que sao beneficios automaticos de classe que o Foundry guarda como item tipo `feat` por conveniencia; o AoN provavelmente as modela como Class Feature, fora do dump de Feats.

**Grupo D -- Foundry-only sem correspondencia (6).** `Armored Regiment Training` (Battlecry!), `Autonomic Psychic Action` (Dark Archives Remastered), `Camouflage Coat` (Howl of the Wild), `Construct Dynamo` (Guns & Gears), `Festering Wounds` (Book of the Dead), `Knight Vigilant Dedication` (Character Guide) -- sem `xref.aon`, sem match parcial/fuzzy. Provavelmente o dump de feats esta desatualizado para esses livros especificos (nao para o livro inteiro -- os outros ~150 feats de Battlecry!/Hellfire Dispatches batem normalmente).

**Grupo E -- variante de modulo (2).** `Roll with it (Kingmaker)` e `The Harder They Fall (Kingmaker)` -- reaproveitam nome de feat existente mas sao boons especificos do modulo Pathfinder Kingmaker, texto proprio.

Acao proposta: nenhuma -- conteudo legitimo. Nao ha o que "consertar"; e limitacao do dump, nao da nossa base.

### 3.5 INDECISO (1)

**Stance Savant** (`wb:feat/stance-savant`, nivel 14, fonte Core Rulebook, so `xref.pf2etools: CRB#stance-savant`, sem `xref.aon`). O AoN tem duas entradas com nomes parecidos -- `feat-419` "Stance Savant (Fighter)" nivel 14 e `feat-472` "Stance Savant (Monk)" nivel 12 -- mas essas duas ja foram identificadas como F-RENAME em 2.1 (viraram "Opening Stance (Fighter)" e "Reflexive Stance", via `legado_de`). Nossa entrada base nao aponta pra nenhuma delas e nao tem par (Fighter)/(Monk) proprio na nossa base. Nao foi possivel confirmar se e uma terceira coisa legitima (feat geral pos-remaster que unificou as duas classes) ou resto morto de uma consolidacao anterior sem `legado_de` preenchido.

Acao proposta: checagem manual pontual -- olhar o texto de `wb:text/feat/stance-savant` e comparar com Reflexive Stance/Opening Stance (Fighter) pra decidir se e a mesma coisa (e devia virar so mais um `legado_de`) ou se e conteudo proprio.

## 4. `nivel_divergente` (21) e `raridade_divergente` (6) -- C-CAMPO

Metodo de desempate: para cada item, resolvi o `xref.aon` PROPRIO da nossa entrada (nao o nome normalizado) contra `pipeline/dados_brutos/aon_feats.json`, e cruzei com `pipeline/dados_brutos/foundry/packs/pf2e/feats/**` via `xref.foundry` quando existia.

### 4.1 Falso-positivo do comparador -- nao ha divergencia real (15)

Causa raiz: o comparador monta os dicionarios `aon[norm(nome)]` e `nossos[norm(nome)]` sobrescrevendo em caso de colisao de nome. Quando duas entradas (nossas ou do AoN) compartilham o nome normalizado -- por termos uma variante `-uncommon`/`-nv16` sem sufixo no `name`, ou porque o proprio AoN tem duas paginas historicas com o mesmo titulo -- a comparacao valida contra o registro ERRADO. Conferido registro a registro via o `xref.aon` proprio de cada id: em todos os 15 casos abaixo, o valor real do AoN (puxado pelo id certo) bate exatamente com o nosso.

| Nome | Nosso valor | Valor "AoN" reportado pelo comparador | Valor real do AoN (via xref proprio) | Causa da colisao |
|---|---|---|---|---|
| Reckless Abandon | 17 | 16 | 17 | nome duplicado em dois ids nossos/AoN |
| Twin Psyche | 18 | 20 | 18 | idem |
| Soaring Form | 9 | 17 | 9 | idem |
| Sixth Pillar Mastery | 16 | 14 | 16 | temos 2 entradas (`-nv16`); comparador usou a outra |
| Shield Salvation | 10 | 12 | 10 | nome duplicado |
| Fuse Stance | 16 | 20 | 16 | nome duplicado |
| Divine Health | 2 | 4 | 2 | nome duplicado |
| Whirlwind Toss | 18 (nivel) | 20 | 18 | AoN tem 2 feats homonimas de fontes diferentes |
| Scrutinizing Gaze | 13 | 17 | 13 | nome duplicado |
| Know-It-All | 10 | 8 | 10 | nome duplicado (arquetipo Eldritch Researcher x outro) |
| Hellknight Dedication | 2 | 6 | 2 | nome duplicado |
| Unstoppable Juggernaut | uncommon | common | uncommon | AoN tem 2 feats homonimas: geral (comum, CRB) e uma de Pathfinder #150 (uncommon) -- nossa entrada `-uncommon` bate certinho com a segunda |
| Whirlwind Toss | common (raridade) | uncommon | common | mesma colisao do item de nivel acima |
| Ultimate Flexibility | uncommon | common | uncommon | mesmo padrao de Unstoppable Juggernaut (Pathfinder #150) |
| Spell Mastery | uncommon | common | uncommon | mesmo padrao (Pathfinder #150: Broken Promises) |

Acao proposta: nenhuma na base -- valores corretos. Corrigir o comparador (secao 5) elimina os 15 falsos-positivos de uma vez.

### 4.2 Divergencia real, Foundry desempata a favor do nosso valor (4)

| Nome | Nosso | AoN (real, via xref proprio) | Foundry | Veredito |
|---|---|---|---|---|
| Devoted Focus | 10 | 12 | 10 | nosso correto -- Foundry concorda |
| Uplifting Winds | 12 | 16 | 12 | nosso correto -- Foundry concorda |
| Feathered Flechettes | 6 | 8 | 6 | nosso correto -- Foundry concorda |
| Animal Soul Siblings | 5 | 1 | 5 | nosso correto -- Foundry concorda (divergencia grande, possivel erro de digitacao no AoN) |

Acao proposta: nenhuma na base. Se quiser fechar o loop, reportar a divergencia pro AoN (sao dados deles, nao nossos) -- fora do escopo deste pipeline.

### 4.3 Divergencia real, AoN e Foundry concordam CONTRA o nosso valor -- fix recomendado (2)

Unico bloco onde a correcao provavel e do NOSSO lado.

| Nome | Id | Nosso valor | AoN | Foundry | Acao |
|---|---|---|---|---|---|
| Play to the Crowd | `wb:feat/play-to-the-crowd` | uncommon | common | common | **corrigir raridade para `common`** |
| Death from Above | `wb:feat/death-from-above` | common | uncommon | uncommon | **corrigir raridade para `uncommon`** |

Acao proposta: alterar `rarity` dessas 2 entradas em `pipeline/base/index.json` (via reprocessamento do pipeline, nao edicao manual do arquivo -- ver secao 5). Prioridade alta: e o unico grupo com bug confirmado do nosso lado em todo o feat.json.

### 4.4 Divergencia real, causa raiz = xref.aon suspeito de estar errado (6, INDECISO quanto ao valor certo)

Padrao: a entrada "base" (sem sufixo de classe) tem `xref.aon` apontando pra uma pagina do AoN que, na verdade, e a variante de OUTRA classe/arquetipo -- coincide com o mesmo padrao de duplicata da secao 3.2. O nivel da nossa entrada bate com uma das variantes-irma que JA existe separadamente na base; o `xref.aon` da entrada bare aponta pra uma segunda variante diferente. Sem o texto oficial da pagina certa nao da pra afirmar qual nivel/raridade e o "correto" pra essa entrada base especifica -- pode ser (a) o xref esta trocado e o nivel dela deveria ser o do alvo do xref, ou (b) a entrada bare e duplicata e deveria ser removida.

| Nome | Nosso nivel | AoN via xref proprio | O que o xref.aon realmente e | Variante-irma que bate com nosso nivel |
|---|---|---|---|---|
| Guardian's Deflection | 6 | 4 | `feat-6147` = pagina generica/Swashbuckler (nivel 4) | Guardian's Deflection (Fighter) = nivel 6 |
| Specialized Companion | 14 | 18 | `feat-1209` = "Specialized Companion (Animal Trainer)" (nivel 18) | Specialized Companion (Druid) = nivel 14 |
| Predictive Purchase | 8 | 6 | `feat-5953` = variante do arquetipo Twilight Talon (nivel 6) | Predictive Purchase (Rogue) = nivel 8 |
| Improved Familiar | 4 | 6 | `feat-6331` = "Improved Familiar (Familiar Master)" (nivel 6) | Improved Familiar (Witch) = nivel 4 |
| Implausible Purchase | 18 | 16 | `feat-5971` = variante do arquetipo Twilight Talon (nivel 16) | Implausible Purchase (Rogue) = nivel 18 |
| Trample | 16 | 17 | `feat-6929` = "Trample (Sarangay)" (nivel 17) | Trample (Summoner) = nivel 16 |

Acao proposta: mesma revisao manual da secao 3.2 (sao literalmente as mesmas 23 familias de feat) -- ao decidir o destino da entrada bare de cada familia, o `xref.aon` errado se resolve junto. Prioridade media, agrupar com 3.2 no mesmo trabalho de revisao.

## 5. Acao recomendada para o pipeline

Ordem de prioridade:

1. **Alta -- corrigir `pipeline/comparar_com_aon.py` (o proprio comparador).** Hoje ele monta `aon[norm(nome)]` e `nossos[norm(nome)]` como dict simples, sobrescrevendo em colisao de nome, e so casa por `name` -- ignora `legado_de`, `aliases` e `historico` que a base ja mantem. Isso gerou **100% dos 163 itens de `faltam_em_nos`** como falso-positivo e **15 dos 27** itens de `nivel_divergente`/`raridade_divergente`. Mudancas sugeridas em `carregar_aon()`/`main()`:

   - trocar os dicts por `dict[str, list]` (guardar todas as colisoes, nao so a ultima) e ao comparar nivel/raridade, escolher o registro cujo id bate com `xref.aon` da nossa entrada -- nao o ultimo da lista;
   - antes de marcar um nome do AoN como `faltam_em_nos`, checar se o `id` dele aparece em algum `legado_de`/`remaster_de`/`historico[].id_legado` da base (cobre os 157 casos de rename/merge da secao 2.1/2.2) e em `aliases` (cobre o caso do Master Spotter);
   - filtrar `primary_source == "Fools Aplenty"` (ou checar `release_date` em 1o de abril) na carga do AoN, pra nao contar conteudo de piada como gap.

2. **Alta -- corrigir raridade de 2 feats (secao 4.3):** `wb:feat/play-to-the-crowd` -> `common`, `wb:feat/death-from-above` -> `uncommon`. Unico bug confirmado do lado da nossa base neste levantamento inteiro. Como o pipeline deriva `rarity` do AoN (`prov.rarity: aon`), o fix certo e re-rodar a etapa de extracao pra essas duas entradas (ou investigar por que a extracao pegou o valor errado do AoN na epoca), nao editar `index.json` a mao.

3. **Media -- revisar as 23 familias "bare + variante(s) por classe" (secoes 3.2 e 4.4).** Lista completa: Animal Empathy, Bear Hug, Blessed Blood, Dueling Dance, Dueling Parry, Ghostly Grasp, Guarded Advance, Guardian's Deflection, Implausible Purchase, Improved Familiar, Improved Twin Riposte, Incredible Companion, Larger than Life, Mature Animal Companion, Phalanx Formation, Predictive Purchase, Quick Recovery, Ricochet Stance, Roll with It, Shared Luck, Shattering Strike, Side by Side, Silence the Profane, Specialized Companion, Spirit Familiar, The Harder They Fall, Trample, Tumble Behind, Twinned Defense. Pra cada uma, decidir contra o texto oficial: (a) a entrada bare e conteudo generico real -> so tirar/corrigir o `xref.aon` errado quando houver; (b) e duplicata morta de uma das variantes com sufixo -> mesclar/remover. Da pra rodar como uma tarefa dedicada, nao precisa de spec nova -- e triagem de dado, nao feature.

4. **Baixa -- conferir grafia de 2 nomes contra o livro fisico/PDF (secao 3.3):** "Lotus Above the Wind" (Tian Xia Character Guide) e "Luring Chomp" (Draconic Codex) -- diferenca de grafia grande o suficiente pra nao ser so erro de digitacao do AoN; vale bater contra a fonte oficial pra garantir que o erro nao esta do nosso lado.

5. **Baixa -- checar manualmente "Stance Savant" (secao 3.5)** contra Reflexive Stance / Opening Stance (Fighter) pra decidir se e F-RENAME sem `legado_de` preenchido ou conteudo proprio.

6. **Sem acao:** os 42 merges de remaster (2.2), os 5 itens de April Fools (2.3), os 36 splits por classe (3.1) e os 30 itens de conteudo legitimo fora do dump (3.4) -- ja estao corretos, so nao aparecem assim pro comparador atual.
