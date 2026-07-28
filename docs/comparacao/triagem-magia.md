# Triagem de divergências -- Magias e Rituais (vs. Archives of Nethys)

Fonte: `docs/comparacao/aon/magia.json` e `docs/comparacao/aon/ritual.json`, gerados por
`pipeline/comparar_com_aon.py` a partir de `pipeline/dados_brutos/aon_spells.json` /
`aon_rituals.json` contra `pipeline/base/index.json`.

Método: casamento por `remaster_id` no dump do AoN (campo que liga a entrada legado ->
entrada remaster), confirmado contra `pipeline/dados_brutos/foundry/packs/pf2e/spells/**`
quando havia conflito de raridade. Nenhum arquivo do pipeline foi alterado.

## 1. Resumo

### Magias

| Categoria | Qtde |
|---|---:|
| F-RENAME-REMASTER | 149 |
| F-VARIANTE (fusão de magias legado em uma remaster) | 9 |
| C-CAMPO (raridade divergente) | 5 |
| A-FALTA-REAL | 0 |
| **Total analisado (faltam_em_nos + raridade_divergente)** | **163** |

### Rituais

| Categoria | Qtde |
|---|---:|
| F-RENAME-REMASTER | 10 |
| F-VARIANTE | 0 |
| A-FALTA-REAL | 0 |
| C-CAMPO (nosso, ausente no dump AoN -- provável lacuna de coleta) | 6 |
| **Total analisado** | **16** |

**Achado central: nenhuma das 158 magias e 10 rituais listados como "faltando" está
realmente ausente.** Todos são o Remaster trocando nome (ORC/licenciamento), e todos
existem na nossa base sob o nome novo. O relatório `faltam_em_nos` do comparador está
tecnicamente correto (o nome antigo não existe na nossa base), mas a categoria é
enganosa sem essa checagem -- não há gap de conteúdo aqui.

---

## 2. F-RENAME-REMASTER (magia, 149 itens)

Veredito para todos: **existe sob o nome novo**, confirmado via campo `remaster_id` da
entrada legado no dump AoN (`aon_spells.json`), que aponta para o id da entrada
remaster -- e essa entrada remaster bate com um nome presente em
`pipeline/base/index.json` (kind=spell). Ação: nenhuma, falso positivo do comparador
por nome. Nenhuma tem tradição/nível "sem uso" porque a entrada remaster é a que está
na base -- a legado é só o nome antigo da mesma magia.

| Nome (AoN legado) | Nome atual (remaster, já na nossa base) | Evidência (aon id, fonte legado) |
|---|---|---|
| Abundant Step | Shrink the Span | spell-482, Core Rulebook |
| Abyssal Wrath | Chthonian Wrath | spell-492, Core Rulebook |
| Acid Arrow | Acid Grip | spell-2, Core Rulebook |
| Acid Splash | Caustic Blast | spell-3, Core Rulebook |
| Animate Dead | Summon Undead | spell-666, Advanced Player's Guide |
| Augment Summoning | Fortify Summoning | spell-521, Core Rulebook |
| Baleful Polymorph | Cursed Metamorphosis | spell-17, Core Rulebook |
| Barkskin | Oaken Resilience | spell-20, Core Rulebook |
| Bind Soul | Seize Soul | spell-21, Core Rulebook |
| Black Tentacles | Slither | spell-23, Core Rulebook |
| Blade Barrier | Blessed Boundary | spell-24, Core Rulebook |
| Blind Ambition | Ignite Ambition | spell-404, Core Rulebook |
| Blink | Flicker | spell-27, Core Rulebook |
| Burning Hands | Breathe Fire | spell-30, Core Rulebook |
| Call of the Grave | Scramble Body | spell-522, Core Rulebook |
| Calm Emotions | Calm | spell-31, Core Rulebook |
| Charming Words | Charming Push | spell-523, Core Rulebook |
| Chill Touch | Void Warp | spell-35, Core Rulebook |
| Cloudkill | Toxic Cloud | spell-42, Core Rulebook |
| Color Spray | Dizzying Colors | spell-44, Core Rulebook |
| Comprehend Language | Translate | spell-46, Core Rulebook |
| Cone of Cold | Howling Blizzard | spell-47, Core Rulebook |
| Continual Flame | Everlight | spell-50, Core Rulebook |
| Crushing Despair | Wave of Despair | spell-57, Core Rulebook |
| Dancing Lights | Light | spell-58, Core Rulebook |
| Darkened Eyes | Darkened Sight | spell-411, Core Rulebook |
| Dimension Door | Translocate | spell-69, Core Rulebook |
| Dimensional Anchor | Planar Tether | spell-70, Core Rulebook |
| Dimensional Lock | Planar Seal | spell-71, Core Rulebook |
| Discern Location | Pinpoint | spell-75, Core Rulebook |
| Disjunction | Detonate Magic | spell-77, Core Rulebook |
| Disrupt Undead | Vitality Lash | spell-79, Core Rulebook |
| Disrupting Weapons | Infuse Vitality | spell-80, Core Rulebook |
| Empty Body | Embrace Nothingness | spell-483, Core Rulebook |
| Endure Elements | Environmental Endurance | spell-99, Core Rulebook |
| Enervation | Whispers of the Void | spell-687, Advanced Player's Guide |
| Entangle | Entangling Flora | spell-103, Core Rulebook |
| False Life | False Vitality | spell-108, Core Rulebook |
| Feather Fall | Gentle Landing | spell-111, Core Rulebook |
| Feeblemind | Never Mind | spell-112, Core Rulebook |
| Finger of Death | Execute | spell-116, Core Rulebook |
| Fire Seeds | Tree of Seasons | spell-117, Core Rulebook |
| Flame Strike | Divine Immolation | spell-120, Core Rulebook |
| Flaming Sphere | Floating Flame | spell-121, Core Rulebook |
| Flesh to Stone | Petrify | spell-123, Core Rulebook |
| Floating Disk | Carryall | spell-124, Core Rulebook |
| Force Cage | Lifewood Cage | spell-690, Advanced Player's Guide |
| Forced Quiet | Whispering Quiet | spell-424, Core Rulebook |
| Freedom of Movement | Unfettered Movement | spell-128, Core Rulebook |
| Gaseous Form | Vapor Form | spell-129, Core Rulebook |
| Gentle Repose | Peaceful Rest | spell-131, Core Rulebook |
| Ghost Sound | Figment | spell-132, Core Rulebook |
| Glibness | Honeyed Words | spell-135, Core Rulebook |
| Globe of Invulnerability | Dispelling Globe | spell-137, Core Rulebook |
| Glutton's Jaw | Glutton's Jaws | spell-511, Core Rulebook |
| Goodberry | Cornucopia | spell-473, Core Rulebook |
| Hallucinatory Terrain | Mirage | spell-145, Core Rulebook |
| Hideous Laughter | Laughing Fit | spell-150, Core Rulebook |
| Horrid Wilting | Desiccate | spell-152, Core Rulebook |
| Hyperfocus | Clouded Focus | spell-600, Gods & Magic |
| Hypnotic Pattern | Hypnotize | spell-157, Core Rulebook |
| Inspire Competence | Uplifting Overture | spell-385, Core Rulebook |
| Inspire Courage | Courageous Anthem | spell-386, Core Rulebook |
| Inspire Defense | Rallying Anthem | spell-387, Core Rulebook |
| Inspire Heroics | Fortissimo Composition | spell-388, Core Rulebook |
| Invisibility Sphere | Shared Invisibility | spell-165, Core Rulebook |
| Ki Blast | Qi Blast | spell-484, Core Rulebook |
| Ki Form | Qi Form | spell-738, Advanced Player's Guide |
| Ki Rush | Qi Rush | spell-485, Core Rulebook |
| Ki Strike | Inner Upheaval | spell-486, Core Rulebook |
| Know Direction | Know the Way | spell-169, Core Rulebook |
| Longstrider | Tailwind | spell-175, Core Rulebook |
| Mage Armor | Mystic Armor | spell-176, Core Rulebook |
| Mage Hand | Telekinetic Hand | spell-177, Core Rulebook |
| Magic Aura | Disguise Magic | spell-178, Core Rulebook |
| Magic Fang | Runic Body | spell-179, Core Rulebook |
| Magic Missile | Force Barrage | spell-180, Core Rulebook |
| Magic Mouth | Embed Message | spell-181, Core Rulebook |
| Magic Weapon | Runic Weapon | spell-182, Core Rulebook |
| Magnificent Mansion | Planar Palace | spell-183, Core Rulebook |
| Maze | Quandary | spell-187, Core Rulebook |
| Meld into Stone | One with Stone | spell-188, Core Rulebook |
| Meteor Swarm | Falling Stars | spell-191, Core Rulebook |
| Mind Blank | Hidden Mind | spell-192, Core Rulebook |
| Modify Memory | Rewrite Memory | spell-200, Core Rulebook |
| Nondetection | Veil of Privacy | spell-209, Core Rulebook |
| Obscuring Mist | Mist | spell-210, Core Rulebook |
| Pass Without Trace | Vanishing Tracks | spell-215, Core Rulebook |
| Passwall | Magic Passage | spell-216, Core Rulebook |
| Perfected Form | Perfected Body | spell-437, Core Rulebook |
| Phantasmal Killer | Vision of Death | spell-219, Core Rulebook |
| Phantom Steed | Marvelous Mount | spell-221, Core Rulebook |
| Plane Shift | Interplanar Teleport | spell-222, Core Rulebook |
| Polar Ray | Arctic Rift | spell-224, Core Rulebook |
| Positive Luminance | Vital Luminance | spell-439, Core Rulebook |
| Private Sanctum | Peaceful Bubble | spell-235, Core Rulebook |
| Produce Flame | Ignition | spell-236, Core Rulebook |
| Protective Ward | Protective Wards | spell-534, Core Rulebook |
| Prying Eye | Scouting Eye | spell-239, Core Rulebook |
| Pulse of the City | Pulse of Civilization | spell-443, Core Rulebook |
| Purify Food and Drink | Cleanse Cuisine | spell-241, Core Rulebook |
| Quivering Palm | Touch of Death | spell-487, Core Rulebook |
| Ray of Enfeeblement | Enfeeble | spell-244, Core Rulebook |
| Ray of Frost | Frostbite | spell-245, Core Rulebook |
| Remove Fear | Clear Mind | spell-252, Core Rulebook |
| Remove Paralysis | Sure Footing | spell-253, Core Rulebook |
| Resilient Sphere | Containment | spell-255, Core Rulebook |
| Restore Senses | Sound Body | spell-259, Core Rulebook |
| Righteous Might | Sacred Form | spell-263, Core Rulebook |
| Roar of the Wyrm | Roar of the Dragon | spell-629, Gods & Magic |
| Rope Trick | Liminal Doorway | spell-264, Core Rulebook |
| Sanctified Ground | Anointed Ground | spell-265, Core Rulebook |
| Scintillating Pattern | Confusing Colors | spell-267, Core Rulebook |
| Scorching Ray | Blazing Bolt | spell-992, Secrets of Magic |
| Searing Light | Holy Light | spell-269, Core Rulebook |
| Secret Chest | Imaginary Lockbox | spell-716, Advanced Player's Guide |
| See Invisibility | See the Unseen | spell-271, Core Rulebook |
| Shadow Walk | Umbral Journey | spell-275, Core Rulebook |
| Shapechange | Metamorphosis | spell-278, Core Rulebook |
| Shield Other | Share Life | spell-281, Core Rulebook |
| Shocking Grasp | Thunderstrike | spell-283, Core Rulebook |
| Sound Burst | Noise Blast | spell-292, Core Rulebook |
| Spectral Hand | Ghostly Carrier | spell-295, Core Rulebook |
| Spell Turning | Spell Riposte | spell-297, Core Rulebook |
| Spider Climb | Gecko Grip | spell-299, Core Rulebook |
| Spiritual Weapon | Spiritual Armament | spell-306, Core Rulebook |
| Splash of Art | Creative Splash | spell-453, Core Rulebook |
| Stone Tell | Speak with Stones | spell-310, Core Rulebook |
| Stoneskin | Mountain Resilience | spell-312, Core Rulebook |
| Storm of Vengeance | Wrathful Storm | spell-313, Core Rulebook |
| Tanglefoot | Tangle Vine | spell-330, Core Rulebook |
| Time Stop | Freeze Time | spell-339, Core Rulebook |
| Tongues | Truespeech | spell-340, Core Rulebook |
| Touch of Idiocy | Stupefy | spell-341, Core Rulebook |
| Tree Shape | One with Plants | spell-342, Core Rulebook |
| Tree Stride | Nature's Pathway | spell-343, Core Rulebook |
| True Seeing | Truesight | spell-344, Core Rulebook |
| True Strike | Sure Strike | spell-345, Core Rulebook |
| Unseen Servant | Phantasmal Minion | spell-352, Core Rulebook |
| Vampiric Touch | Vampiric Feast | spell-354, Core Rulebook |
| Veil | Illusory Disguise | spell-355, Core Rulebook |
| Vigilant Eye | Rune of Observation | spell-536, Core Rulebook |
| Wail of the Banshee | Wails of the Damned | spell-361, Core Rulebook |
| Weird | Phantasmagoria | spell-375, Core Rulebook |
| Wholeness of Body | Harmonize Self | spell-488, Core Rulebook |
| Wild Morph | Untamed Shift | spell-480, Core Rulebook |
| Wild Shape | Untamed Form | spell-481, Core Rulebook |
| Wind Walk | Migration | spell-376, Core Rulebook |
| Zone of Truth | Ring of Truth | spell-379, Core Rulebook |

## 3. F-VARIANTE (magia, 9 itens -- fusão de legado em uma única remaster)

O Remaster uniu várias magias legado antigas na mesma nova magia. Evidência: todas as
entradas legado apontam (via `remaster_id`) para o mesmo id remaster. Nossa base já
tem só a versão unificada, com o histórico registrado em `historico` (só para
"Manifestation" isso já estava explícito na base; para "Revealing Light" e "Cleanse
Affliction" o merge existe no AoN mas não estava documentado em `historico` -- ver ação
recomendada).

| Nome (AoN legado) | Unificada em | Evidência |
|---|---|---|
| Alter Reality | Manifestation | spell-8 -> remaster_id de Manifestation |
| Miracle | Manifestation | spell-196 -> remaster_id de Manifestation |
| Primal Phenomenon | Manifestation | spell-231 -> remaster_id de Manifestation |
| Wish | Manifestation | spell-377 -> remaster_id de Manifestation |
| Faerie Fire | Revealing Light | spell-107 -> remaster_id de Revealing Light |
| Glitterdust | Revealing Light | spell-136 -> remaster_id de Revealing Light |
| Neutralize Poison | Cleanse Affliction | spell-207 -> remaster_id de Cleanse Affliction |
| Remove Curse | Cleanse Affliction | spell-250 -> remaster_id de Cleanse Affliction |
| Remove Disease | Cleanse Affliction | spell-251 -> remaster_id de Cleanse Affliction |

Nossa base já reflete corretamente a fusão (`Manifestation`, `Revealing Light`,
`Cleanse Affliction` existem; as 9 legado não). Ação: nenhuma correção de conteúdo --
só complementar `historico` de `Revealing Light` e `Cleanse Affliction` com as
entradas legado, no mesmo padrão já usado em `Manifestation` (melhoria de
rastreabilidade, não bug).

## 4. C-CAMPO -- raridade divergente (magia, 5 itens)

**Achado importante: o id que o comparador reportou está errado em 4 dos 5 casos.**
Causa raiz: `comparar_com_aon.py` casa por `norm(nome)` em um dict -- quando duas
magias diferentes têm o mesmo nome (comum em conteúdo de Adventure Path reimpresso),
tanto do lado do AoN quanto do lado da nossa base o dict fica com a última entrada
processada, então o par comparado nem sempre é o certo. Refiz o casamento usando
`xref.aon` (id direto) em vez de nome, o que revela o par real.

| Nome | Nosso id correto | Nossa raridade | AoN (fonte mais atual) | Foundry | Veredito | Ação |
|---|---|---|---|---|---|---|
| Object Reading | `wb:spell/object-reading` | uncommon | common (spell-2012, Player Core 2) | common (Player Core 2) | **AoN e Foundry concordam: common. Nossa base está errada.** | Corrigir `wb:spell/object-reading` para `common`. (O id reportado pelo comparador, `-uncommon`, é outra magia homônima da Pathfinder #147 e está correto como está.) |
| Pillar of Water | `wb:spell/pillar-of-water` | uncommon | common (spell-1394, Rage of Elements) | common (Rage of Elements) | **AoN e Foundry concordam: common. Nossa base está errada.** | Corrigir `wb:spell/pillar-of-water` para `common`. (id `-uncommon` é a homônima de Pathfinder #152, correta.) |
| Imprint Message | `wb:spell/imprint-message` | uncommon | common (spell-2003, Player Core 2) | common (Player Core 2) | **AoN e Foundry concordam: common. Nossa base está errada.** | Corrigir `wb:spell/imprint-message` para `common`. (id `-uncommon` é a homônima de Pathfinder #147, correta.) |
| Tireless Worker | `wb:spell/tireless-worker` | common | uncommon (spell-2418, Divine Mysteries 2025 -- reimpressão mais recente, mesmo texto de spell-1347 que era common em Rage of Elements) | uncommon (Divine Mysteries) | **AoN (edição mais recente) e Foundry concordam: uncommon. Nossa base está desatualizada (refletia a raridade pré-errata).** | Corrigir `wb:spell/tireless-worker` para `uncommon`. |
| Verdant Sprout | `wb:spell/verdant-sprout` | uncommon | common (spell-1413, Rage of Elements) -- mas conflita com o Foundry | **uncommon** (única entrada Foundry, ainda datada de Pathfinder #151, sem a reimpressão de Rage of Elements) | **Conflito real entre AoN e Foundry.** Desempatando pelo Foundry (critério pedido): uncommon. Nossa base já está certa. | Nenhuma correção -- mas vale checar manualmente a página do Verdant Sprout no AoN: é possível que a entrada spell-1413 (common) esteja com a raridade errada, ou que o Foundry ainda não tenha absorvido a reimpressão de Rage of Elements. |

Resumo de ação: **4 bugs reais de raridade na base** (Object Reading, Pillar of Water,
Imprint Message -> `common`; Tireless Worker -> `uncommon`), todos no id "sem sufixo"
(a versão reimpressa/atual da magia, não a homônima de AP). Verdant Sprout fica como
está.

## 5. A-FALTA-REAL (magia)

Nenhum. Todos os 158 itens de `faltam_em_nos` resolveram para F-RENAME-REMASTER ou
F-VARIANTE.

## 6. Rituais -- F-RENAME-REMASTER (10 itens)

Mesma mecânica: todas as 10 entradas de `faltam_em_nos` em `ritual.json` têm
`remaster_id` apontando para uma entrada que já existe na nossa base.

| Nome (AoN legado) | Nome atual (remaster, já na nossa base) | Evidência |
|---|---|---|
| Abyssal Pact | Demonic Pact | ritual-21 -> ritual-142, Bestiary |
| Commune with Nature | Commune | ritual-7 -> ritual-114, Core Rulebook |
| Heroes' Feast | Fortifying Brew | ritual-34 -> ritual-147, Advanced Player's Guide |
| Infernal Pact | Diabolic Pact | ritual-23 -> ritual-143, Bestiary |
| Legend Lore | Collective Memories | ritual-15 -> ritual-113, Core Rulebook |
| Planar Ally | Planar Servitor | ritual-16 -> ritual-120, Core Rulebook |
| Planar Binding | Binding Circle | ritual-17 -> ritual-110, Core Rulebook |
| Simulacrum | Shadow Double | ritual-37 -> ritual-154, Advanced Player's Guide |
| Unseen Custodians | Phantasmal Custodians | ritual-39 -> ritual-151, Advanced Player's Guide |
| Word of Recall | Gathering Call | ritual-41 -> ritual-148, Advanced Player's Guide |

Nenhum merge (cada legado aponta para um remaster distinto). Nenhum A-FALTA-REAL.

## 7. Rituais -- "só nosso" (6 itens)

Presentes só na nossa base, ausentes do dump `aon_rituals.json` -- inclusive por
busca de substring (`Mycoguardian`, `Mindscape`, `Cleansing Flame`, `Unfettered`,
`Aspirational`, `Anima Invocation` não aparecem em nenhuma entrada do dump). Não é
erro de casamento por nome -- é ausência real do dump.

| Nome | Fonte | Evidência |
|---|---|---|
| Anima Invocation (Modified) | Pathfinder #150: Broken Promises | `xref.foundry` presente, sem `xref.aon`; busca por substring no dump: 0 resultados |
| Aspirational State | PFS Scenario #2-22 | idem |
| Create Mycoguardian | Pathfinder #193: Mantle of Gold | idem |
| Destroy Mindscape | Pathfinder Season of Ghosts (compilação) | idem |
| Rite of Cleansing Flame | Pathfinder #216: The Acropolis Pyre | idem |
| Unfettered Mark | Pathfinder #161: Belly of the Black Whale | idem |

Veredito: **INDECISO quanto à causa, mas sem ação de conteúdo.** São rituais de nicho
(tie-in de Adventure Path / cenário de PFS), sourced via Foundry, corretos na nossa
base. A ausência no dump AoN provavelmente é lacuna de cobertura da coleta (esses
rituais tendem a estar em páginas de AP individuais, não na lista central de rituais
que o scraper provavelmente usou como fonte) -- não dá pra confirmar sem acessar o
AoN ao vivo, o que está fora do escopo desta triagem (dump offline). Não remover nem
sinalizar como problema da nossa base.

## 8. Ação recomendada para o pipeline

Prioridade decrescente:

1. **Corrigir 4 raridades divergentes na base** (`Object Reading`, `Pillar of Water`,
   `Imprint Message` -> `common`; `Tireless Worker` -> `uncommon`), usando os ids sem
   sufixo listados na seção 4. Bug de conteúdo real e pequeno (4 registros).
2. **Bug no comparador (`pipeline/comparar_com_aon.py`)**: `carregar_aon()` e o loop de
   `nossos` em `main()` indexam por `norm(nome)` num dict simples, então nomes
   duplicados (comuns em magias reimpressas em Adventure Paths, ex.: "Object Reading",
   "Pillar of Water", "Verdant Sprout", "Imprint Message", "Tireless Worker" -- cada uma
   tem 2-3 entradas homônimas não relacionadas no AoN) colapsam e o último processado
   vence silenciosamente. Isso já causou 4 atribuições de id erradas em
   `raridade_divergente`. Recomendo trocar a chave de casamento, quando existir
   `xref.aon`/`id` do AoN, para casar por id em vez de nome normalizado -- ou, no
   mínimo, when há colisão de nome, desambiguar por id/fonte antes de reportar.
3. **Documentar merges de Remaster** (`historico`) em `Revealing Light` (recebe Faerie
   Fire + Glitterdust) e `Cleanse Affliction` (recebe Neutralize Poison + Remove Curse
   + Remove Disease), no mesmo padrão já usado para `Manifestation`. Não é bug, é
   rastreabilidade -- melhora a UX de quem procurar pelo nome antigo.
4. **Não mexer** nas 149 magias e 10 rituais F-RENAME-REMASTER nem nos 6 rituais "só
   nosso": conteúdo já está correto, a única "falta" é de nome no relatório do
   comparador.
5. Opcional / baixa prioridade: confirmar ao vivo no site do AoN se os 6 rituais "só
   nosso" (seção 7) têm página própria -- se sim, vale reexecutar a coleta do dump de
   rituais para fechar essa lacuna de cobertura; se o dump já é o que existe, não há
   nada a fazer.
