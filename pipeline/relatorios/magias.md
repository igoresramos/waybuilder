# Relatorio -- Extracao de Magias (kind=spell)

- Total de magias no registro canonico: **1667**
- Casadas com foundry (`xref.foundry` presente, dados criticos disponiveis): **1651**
- Sem match no foundry (indefinidas): **16**
- Escopo: AoN `category=spell` (2.461 docs brutos, legado+remaster) deduplicados por `remaster_id`/`legacy_id` -> 1667 conceitos canonicos.
- Foundry: `packs/pf2e/spells/{spells,focus}` -- rituais (`packs/pf2e/spells/rituals`) fora do escopo (categoria separada na AoN: `ritual`, 201 docs).

## heightened

- Estruturado (`heightened` com pelo menos 1 entrada): **525**
- So em prosa (texto menciona "Heightened (" mas o foundry nao tem `system.heightening`): **452**
- Sem elevacao nenhuma (nem estrutura, nem prosa): **690**

`heightened_so_prosa=true` normalmente cai em magias sem match no foundry, ou em overlays
de foco/variante onde a elevacao vive num overlay que este extrator nao le (fora de escopo).

## defesa

| Tipo | Quantidade |
|---|---|
| save:will | 275 |
| save:fortitude | 223 |
| save:reflex | 185 |
| ataque | 62 |
| nenhuma | 922 |
| **indefinida (sem match foundry)** | **16** |

(`nenhuma` inclui as 16 indefinidas -- ver abaixo -- porque sem dado do foundry
o campo fica `null` por ausencia de fonte, nao por ser genuinamente sem defesa.)

### Magias com defesa indefinida (16, sem match no foundry)

- Detect Alignment
- Discomfiting Whisper
- Dragon Claws
- Dread Aura
- Efficient Apport
- Glyph of Warding
- Litany Against Wrath
- Litany against Sloth
- Litany of Depravity
- Litany of Righteousness
- Litany of Self-Interest
- Misdirection
- Touch of Corruption
- Undetectable Alignment
- Vindicator's Judgement
- Wish

## Divergencia: foundry diz "sem defesa", AoN tem `saving_throw` preenchido

7 casos onde `system.defense` do foundry e nulo mas a AoN registra
uma saving throw estruturada. Precedencia mantém foundry (regra do schema), mas fica
registrado em `conflitos` de cada registro -- nao e descartavel:

- **Boots on the Ground** (rank 6) -- AoN diz saving throw = `Will`
- **Burning Blossoms** (rank 8) -- AoN diz saving throw = `Will`
- **Manifest Will** (rank 1) -- AoN diz saving throw = `basic  Reflex`
- **Overwhelming Memory** (rank 3) -- AoN diz saving throw = `Will`
- **Positive Attunement** (rank 3) -- AoN diz saving throw = `Will`
- **Summon Warden of the Wild** (rank 8) -- AoN diz saving throw = `see text`
- **Cinder Swarm** (rank 4) -- AoN diz saving throw = `Fortitude or  basic  Reflex (see text)`

## Escalonamento de dano sem nenhuma defesa (achado de balanceamento)

Filtrado por `defesa=null` (real, ja excluindo indefinidas e o override de cura-pura)
e ordenado por ganho medio de dano por rank de elevacao (media de dado, `NdM+K` -> `N*(M+1)/2+K`).

### Dano real sem defesa nenhuma (30 magias) -- top 20

Estas causam dano (nao cura) sem que o alvo role NADA contra elas -- nem save, nem
o atacante rola ataque. E a lista que mais importa pra houserule de elevacao: cada
uma delas escala dano garantido, sem chance de mitigacao.

| Ganho/rank | Magia | Rank | Dano base | Observacao |
|---|---|---|---|---|
| 5.50 | Shatter | 2 | 2d10 sonic | alvo e objeto, nao criatura |
| 5.50 | Shining Starlight Attack | 2 | 2d10 untyped |  |
| 5.50 | Weapon of Judgment | 9 | 4d10 untyped |  |
| 4.50 | Wall of Virtue | 3 | 1d8 vitality; 1d8 spirit |  |
| 3.50 | Burning Blossoms | 8 | 6d6 fire |  |
| 3.50 | Wall of Fire | 4 | 4d6 fire |  |
| 3.50 | Wall of Ice | 5 | 2d6 cold |  |
| 3.50 | Corrosive Body | 7 | 3d6 acid |  |
| 3.25 | Electrified Crystal Ward | 3 | 3d12 electricity |  |
| 2.75 | Sign of Conviction | 3 | 2d10 fire |  |
| 2.50 | Nettleskin | 1 | 1d4 piercing |  |
| 2.50 | Wall of Thorns | 3 | 3d4 piercing |  |
| 2.25 | Shadow Illusion | 6 | 2d8 untyped |  |
| 2.25 | Spiritual Guardian | 5 | 3d8 spirit |  |
| 2.25 | Warning Stripes | 3 | 2d8 poison |  |
| 1.75 | Unusual Anatomy | 5 | 2d6 acid |  |
| 1.75 | Dancing Blade | 5 | 3d6 bludgeoning |  |
| 1.75 | Defended By Spirits | 1 | 1d6 spirit |  |
| 1.75 | Dust Storm | 4 | 1d6 slashing |  |
| 1.75 | Fire Shield | 4 | 2d6 fire |  |

### Cura sem defesa (25 magias) -- esperado por design, nao e achado

Cura nunca rola contra nada no PF2e RAW -- listado por completude, nao e anomalia:

- 9.50/rank -- Soothe (rank 1, 1d10+4 untyped)
- 9.00/rank -- Shock to the System (rank 7, 8d8 untyped)
- 9.00/rank -- Soothing Spring (rank 4, 10d8 vitality)
- 8.50/rank -- Necromancer's Generosity (rank 1, 1d8+4 untyped)
- 8.00/rank -- Luminous Stardust Healing (rank 2, 16 untyped)
- 8.00/rank -- Harmonize Self (rank 2, 8 vitality)
- 6.00/rank -- Nature's Bounty (rank 4, 3d10+12 vitality)
- 5.50/rank -- Heal Companion (rank 1, 1d10 untyped)
- 5.50/rank -- Let not the Fallen Rest (rank 5, 4d10 untyped)
- 5.00/rank -- Gentle Breeze (rank 2, 10 vitality)
- ... e mais 15

## Divergencias entre fontes (`conflitos`)

- `rank` (foundry vs pf2etools/aon): **2**
  - Speak with Plants: {'campo': 'rank', 'foundry': 3, 'pf2etools': 4, 'aon': 3, 'escolhido': 'foundry'}
  - Enlarge Companion: {'campo': 'rank', 'foundry': 2, 'pf2etools': 4, 'aon': 2, 'escolhido': 'foundry'}
- `tradicoes` (foundry vs pf2etools): **20**
  - Befuddle: foundry=['arcane', 'occult'] pf2etools=['arcane']
  - Mindlink: foundry=['arcane', 'occult'] pf2etools=['occult']
  - Mushroom Patch: foundry=[] pf2etools=['primal']
  - Noise Blast: foundry=['arcane', 'divine', 'occult'] pf2etools=['divine', 'occult']
  - Rapid Adaptation: foundry=['primal'] pf2etools=['arcane', 'primal']
  - Retrocognition: foundry=['arcane', 'occult'] pf2etools=['occult']
  - Shape Wood: foundry=['arcane', 'primal'] pf2etools=['primal']
  - Speak with Plants: foundry=['divine', 'occult', 'primal'] pf2etools=['primal']
  - Spirit Song: foundry=['divine', 'occult'] pf2etools=['occult']
  - Summon Dragon: foundry=['arcane', 'divine', 'occult', 'primal'] pf2etools=['arcane']
  - Summon Instrument: foundry=['arcane', 'divine', 'occult'] pf2etools=['divine', 'occult']
  - Tangling Creepers: foundry=['arcane', 'primal'] pf2etools=['primal']
  - Wall of Thorns: foundry=['arcane', 'primal'] pf2etools=['primal']
  - Dominate: foundry=['arcane', 'divine', 'occult'] pf2etools=['arcane', 'occult']
  - Dragon Form: foundry=['arcane', 'divine', 'occult', 'primal'] pf2etools=['arcane', 'primal']
  - Drop Dead: foundry=['arcane', 'divine', 'occult'] pf2etools=['arcane', 'divine']
  - Fly: foundry=['arcane', 'divine', 'occult', 'primal'] pf2etools=['arcane', 'occult', 'primal']
  - Fungal Exhalation: foundry=[] pf2etools=['primal']
  - Hedge Prison: foundry=[] pf2etools=['primal']
  - Insect Form: foundry=['arcane', 'primal'] pf2etools=['primal']
- `defesa` (foundry nulo vs AoN saving_throw): **7** (ver secao acima)

## Cobertura Remaster vs Legacy

- `source.remaster=true`: **1177** (71%)
- `source.remaster=false` (so legado, nunca remasterizado ou fora do foundry): **490** (29%)
- Registros com `xref.aon_legacy` (par legado encontrado na AoN): **789**

## Tradicoes

- arcane: 782
- occult: 641
- primal: 594
- divine: 446
- sem `tradicoes`: **526**, dos quais:
  - focus spells (aceitavel -- a tradicao vem da classe que concede): **477**
  - nao-focus, fechados via `tradicao_de_classe` (A9): **48** -- {'bard': 10, 'psychic': 18, 'summoner': 2, 'witch': 18}
  - nao-focus, ainda irresolviveis: **1**
    - Web of Influence (wb:spell/web-of-influence) -- traits=['detection', 'divination', 'uncommon'], sem tradicao no foundry nem na AoN, sem trait de classe pra derivar. Provavelmente magia de monstro/perigo (fora do escopo de PC), nao fica silenciada: listada aqui.

## `level` (espelho de `rank`, A9)

- Registros com `level == rank` (os dois emitidos, mesmo valor): **1667** / 1667
- `rank` continua canonico; `level` existe so pra nao quebrar filtro de nivel no cliente
  (spec v2, `prov.level = waybuilder~inferido:espelho-rank`).

## Rank (distribuicao)

- rank 1: 466
- rank 2: 213
- rank 3: 235
- rank 4: 259
- rank 5: 180
- rank 6: 103
- rank 7: 79
- rank 8: 55
- rank 9: 46
- rank 10: 31

## Cross-reference / cobertura de fontes

- Com xref pf2etools: **1450** / 1667
- Casadas com foundry: **1651** / 1667

## Portoes de qualidade (spec schema-base) -- status

1. `prov` por campo preenchido: aplicado (todo campo nao-nulo tem entrada em `prov`).
2. `rank` diverge foundry/pf2etools sem `conflitos`: 0 (todas as 2 divergencias tem entrada).
3. `requires` citando id inexistente: N/A (magias nao tem `requires` nesta extracao).
4. Cobertura vs build anterior: N/A (primeira extracao de magias).
5. `license` ausente: **16** registros (todos sem match foundry -- mesmos 16 indefinidos).
   - Litany against Sloth
   - Litany Against Wrath
   - Litany of Depravity
   - Litany of Righteousness
   - Litany of Self-Interest
   - Misdirection
   - Touch of Corruption
   - Undetectable Alignment
   - Vindicator's Judgement
   - Wish
   - Detect Alignment
   - Discomfiting Whisper
   - Dragon Claws
   - Dread Aura
   - Efficient Apport
   - Glyph of Warding

Este e um extrator de kind unico (magias); os portoes valem pro build completo
multi-kind (fora de escopo aqui). Reportados como metricas, nao bloqueiam a saida.

## Simplificacoes assumidas (ver LESSONS.md do projeto)

- `text`/`texto`: este extrator embute a prosa (`texto`) direto no registro, alem da
  referencia `text: wb:text/spell/<slug>` pedida pelo schema. O split fisico index/text
  e passo de um build multi-kind, fora do escopo de um extrator unico.
- `defesa` por cura pura (kind=["healing"] exclusivo): save do foundry e ignorado
  (ex: Heal tem `defense.save.fortitude` pro caso "dano a undead", mas o uso principal
  -- curar vivo -- nao rola nada). `prov` registra `foundry:heal-only-override`.
- `defesa` passiva contra AC (`defense.passive.statistic="ac"`, ex: paredes conjuradas)
  e tratada como `{"ataque": true}` -- e um ataque de efeito contra CA, nao um save.
- Overlays do foundry (variantes dentro do mesmo item, ex: Heal vs. undead/vivo,
  Telekinetic Projectile por tipo de dano) nao sao expandidos em registros separados;
  so a entrada base e lida.
