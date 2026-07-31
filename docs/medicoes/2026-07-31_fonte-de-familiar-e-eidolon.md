# Fonte das estatisticas de familiar e eidolon (item 43)

Medicao contra `pipeline/dados_brutos/` (dumps em disco) e `pipeline/base/index.json`
(base construida). Somente leitura -- nenhum arquivo do repo foi alterado.

## Resposta direta

**A fonte existe em disco, para os dois casos, mas nao e uma tabela -- e uma
FORMULA.** Familiar e eidolon nao tem "stat block" no sentido de companion
(numeros fixos por registro). Em PF2e os dois derivam de calculo em cima do
mestre/invocador, e essa formula esta publicada pela Paizo e capturada no
dump do AoN em `pipeline/dados_brutos/aon_dump/rules.json`, so' que sob
paginas de REGRA (categoria `rules`), nao sob a entidade (`eidolon`,
`familiar-specific`). O extrator (`pipeline/extratores/companheiros.py`) le
so a entidade, nunca essas paginas de regra -- por isso a base fica sem
numero.

## 1. Familiar -- formula completa, achada em `rules.json`

Arquivo: `pipeline/dados_brutos/aon_dump/rules.json` (3.645 registros).

### Legado (Core Rulebook)

| id | name | pg | texto |
|---|---|---|---|
| `rules-161` | Modifiers and AC | 217 | "Your familiar's save modifiers and AC are equal to yours before applying circumstance or status bonuses or penalties. Its Perception, Acrobatics, and Stealth modifiers are equal to your level plus your spellcasting ability modifier ... If it attempts an attack roll or other skill check, it uses your level as its modifier." |
| `rules-162` | Hit Points | 217 | "Your familiar has 5 Hit Points for each of your levels." |
| `rules-163` | Size | 218 | "Your familiar is Tiny." |
| `rules-164` | Senses | 218 | "Your familiar has low-light vision..." |
| `rules-165` | Movement | 218 | "Your familiar has either a Speed of 25 feet or a swim Speed of 25 feet..." |
| `rules-166` | Familiar and Master Abilities | 218 | escolha diaria de 2 habilidades (familiar ou master) |

### Remaster (Player Core) -- familiar virou "Pet + habilidades"

`rules-2121` ("Familiars", Player Core pg. 212): "You gain the **Pet**
general feat, except that your pet has special abilities." O statblock
completo hoje mora no feat geral **Pet** (Player Core pg. 259), presente em
`pipeline/dados_brutos/aon_feats.json` (busca por `name == "Pet"`, nivel 1):

```
Level: Your pet's level is equal to yours.
Modifiers and AC: Your pet's save modifiers and AC are equal to yours
  before applying circumstance or status bonuses or penalties. It uses
  3 + your level as its modifier for Perception, Acrobatics, and Stealth,
  and just your level as its modifier for other skill checks.
Hit Points: Your pet has 5 Hit Points per level.
Senses: low-light vision (+ pet abilities)
Speed: 25 feet (ou aquatico: swim 25 feet)
```

Ajuste do familiar sobre o Pet-base, em `rules-2122` (Modifiers and AC, pg.
212): "For Perception, Acrobatics, and Stealth, you can have your familiar
use your spellcasting attribute modifier + your level instead of 3 + your
level if it's higher." -- ou seja, o unico delta do familiar remaster sobre
o Pet e trocar `3` por `mod de conjuracao` nessas 3 pericias, se for melhor.

`rules-2125` (Familiar Abilities, pg. 212) lista as 10 pet abilities
reaproveitadas (amphibious, burrower, climber, darkvision, echolocation,
fast movement, flier, manual dexterity, scent, tough) com efeito textual --
"Tough" e a unica que mexe em HP ("+2 max HP per level").

**Conclusao familiar**: formula fechada, sem ambiguidade, sem tabela por
nivel -- e so' aritmetica sobre os atributos do mestre (nivel, mod de
conjuracao, AC/saves do mestre antes de circunstancia/status). Nao ha nada
a inventar: os 6 campos (AC, saves, Perception/Acrobatics/Stealth, HP,
Speed, Size) tem regra publicada e capturada em disco.

## 2. Eidolon -- formula + arrays por tipo, achados em `rules.json` e `eidolon.json`

### Formula geral (`rules.json`, fonte Secrets of Magic pg. 58)

| id | name | texto |
|---|---|---|
| `rules-1582` | Proficiencies | "Your eidolon's level is equal to yours. It begins with expert proficiency in Fortitude and Will saves and trained proficiency in Reflex saves and Perception... trained in unarmed attacks and unarmored defense. It shares your skill proficiencies." |
| `rules-1583` | Ability Scores | "An eidolon's ability scores depend on which array you choose... gets boosts to its ability scores at the same time you do. It also increases one score by 2 when it gains its transcendence ability." |
| `rules-1584` | Unarmed Attacks | 4 opcoes de dado pro ataque primario + secundario fixo (1d6 agile finesse) |
| `rules-1586` | Reading an Eidolon Entry | explica os campos de cada entrada de tipo (array define atributos + item bonus a AC + Dex cap) |

Achado lateral relevante: **eidolon nao tem HP proprio**. Confirmado em
`pipeline/dados_brutos/aon/class-feature__eidolon.json` (pg. 51, feature
"Eidolon" da classe Summoner): "the connection between you and your eidolon
means you both share a single pool of Hit Points." Nao ha HP a derivar --
o pool e o do invocador.

AC do eidolon = formula padrao PF2e de defesa desarmada (10 + nivel +
proficiencia + mod de Destreza, limitado pelo Dex cap do array escolhido) +
item bonus do array -- o MESMO motor que ja calcula AC de PC (motor ja
suporta `unarmored defense`), so' precisa do Dex cap e do item bonus por
array, que sao dados por tipo (ver abaixo).

Progressao de proficiencia (Perception/Reflex/ataque desarmado/unarmored
defense/Fortitude/Will) esta espalhada nas class features do Summoner --
texto integral em `class.json` (`pipeline/dados_brutos/aon_dump/class.json`,
registro `name == "Summoner"`, campo `text`, 25.143 caracteres) e replicada
como registros individuais em `pipeline/dados_brutos/aon/`:
`class-feature__eidolon-defensive-expertise.json`,
`class-feature__eidolon-defensive-mastery.json`,
`class-feature__eidolon-unarmed-expertise.json`,
`class-feature__eidolon-unarmed-mastery.json`,
`class-feature__eidolon-weapon-specialization.json`,
`class-feature__eidolon-symbiosis.json`,
`class-feature__eidolon-transcendence.json`. Essas ja devem estar na base
como `kind: class-feature` (nao verificado aqui, fora do escopo do item 43,
mas e onde a progressao por nivel mora).

### Arrays de atributos por tipo -- em PROSA no AoN, ESTRUTURADO no pf2etools

`pipeline/dados_brutos/aon_dump/eidolon.json` (13 registros: Angel, Anger
Phantom, Beast, Construct, Demon, Devotion Phantom, Dragon, Elemental, Fey,
Plant, Psychopomp, Swarm, Undead) tem os arrays de atributos SO' dentro do
campo `text`, em prosa, ex. (Angel, primeiros 900 caracteres):

```
Angelic Avenger - Str 18 - Dex 14 - Con 16 - Int 8 - Wis 12 - Cha 10
  - +2 AC (+3 Dex cap)
Angelic Emissary - Str 12 - Dex 18 - Con 12 - Int 10 - Wis 12 - Cha 14
  - +1 AC (+4 Dex cap)
```

Campos estruturados desse registro (`speed`, `sense`, `skill`) tem so'
velocidade/sentidos/pericias -- confirma o que ja foi medido. Nenhum campo
numerico de atributo ou AC existe como coluna no documento AoN.

**Achado novo**: `pipeline/dados_brutos/pf2etools_repo/data/companionsfamiliars.json`
ja tem isso PARSEADO em JSON estruturado, chave `"eidolon"`, 12 dos 13
registros (falta "Swarm", eidolon mais recente, ainda nao versionado no
pf2etools). Exemplo (Elemental Eidolon):

```json
"stats": [
  {
    "name": "Adaptable Elemental",
    "abilityScores": {"str": 12, "dex": 18, "con": 16, "int": 10, "wis": 12, "cha": 10},
    "ac": {"number": 1, "dexCap": 4}
  },
  {
    "name": "Primordial Elemental",
    "abilityScores": {"str": 18, "dex": 14, "con": 16, "int": 8, "wis": 12, "cha": 10},
    "ac": {"number": 2, "dexCap": 3}
  }
]
```

Isso poupa parsear prosa: 12/13 arrays ja vem como numero pronto (`str`,
`dex`, `con`, `int`, `wis`, `cha`, `ac.number` = item bonus, `ac.dexCap`).
Falta so' extrair "Swarm" (unico sem par no pf2etools) direto da prosa do
AoN (mesmo padrao `Nome - Str N - Dex N - ...` confirmado acima).

O mesmo arquivo pf2etools tambem tem chave `"familiar"` (30 registros, os
"specific familiars" ilustrados com granted abilities ja resolvidas por
nome) e `"companion"` (61, com `abilityMods` em MODIFICADOR e `hp` -- ja no
formato que a base do waybuilder usa para animal-companion).

**Conclusao eidolon**: nao ha HP a derivar (pool compartilhado), AC/saves/
Perception/pericias/ataque desarmado seguem formula (10 + nivel +
proficiencia + mod, proficiencia sobe via class features ja mapeaveis),
faltam so os arrays de atributo + Dex cap + item bonus de AC por tipo --
esses existem em prosa no AoN (13/13) e ja estruturados no pf2etools
(12/13).

## 3. Por que animal-companion ja e modelado e os outros dois nao

`_wb_dump_companheiros.py` puxa as 8 categorias (`animal-companion`,
`animal-companion-specialization`, `animal-companion-advanced`,
`animal-companion-unique`, `familiar-ability`, `familiar-specific`,
`eidolon`, `apparition`) do MESMO endpoint Elasticsearch do AoN
(`https://elasticsearch.aonprd.com/aon/_search`). A diferenca nao e de
rota, e de SCHEMA que a Paizo/AoN da a cada categoria:

- `animal-companion`: documento AoN tem colunas numericas de primeira
  classe -- `strength`, `dexterity`, `constitution`, `intelligence`,
  `wisdom`, `charisma`, `hp` (confirmado em
  `pipeline/dados_brutos/aon_dump/animal-companion.json`, 114 registros).
  `pipeline/extratores/companheiros.py:381-382` le exatamente esses 6
  campos via `ATTR_CAMPOS` e monta `stats.atributos` (linhas 449-472).
- `eidolon` e `familiar-specific`: documento AoN NAO tem essas colunas.
  Os numeros existem, mas so' dentro do texto em prosa (`text`) ou em
  paginas de regra separadas (`rules.json`). O extrator nunca le
  `rules.json` nem faz parsing de prosa para atributos -- so tem
  `parse_ataques` e `parse_ataques_sugeridos` (linhas 241, 275), que
  extraem nome+tipo de dano de ataque, nao numero de atributo.

Confirmado contra a base construida (`pipeline/base/index.json`,
19.604 registros):

| kind | registros | campo `stats` |
|---|---|---|
| `animal-companion` | 113 | `atributos` (mod), `hp`, `velocidade`, `ataques` com dano -- completo |
| `eidolon` | 13 | so `tradicao`, `plano_natal`, `tamanho`, `velocidade`, `sentidos`, `pericias`, `ataques_sugeridos` (sem dano/tipo fixo) -- zero numero de atributo, zero AC, zero HP |
| `familiar-specific` | 38 | campo `stats` nem existe no registro; `mechanized: false` |

Ou seja: **nao e que falte fonte de familiar/eidolon -- falta o extrator ir
buscar em `rules.json` (formula) e/ou em `eidolon.json.text` ou no
pf2etools (arrays por tipo), em vez de olhar so' o documento da propria
entidade.**

## 4. Fontes descartadas ou de valor marginal

- **Foundry (`pipeline/dados_brutos/foundry_repo/`)**: so tem `packs/`
  (dados de compendio), sem o codigo TypeScript dos Rule Elements. Nao ha
  pack de `eidolon` nem `animal-companion` nem `familiar` (statblock); so
  existe `packs/pf2e/familiar-abilities` (habilidades avulsas, ja coberto
  por `familiar-ability`). Descartado para statblock -- o calculo de
  familiar/eidolon no sistema Foundry vive em codigo-fonte que este
  checkout nao clonou (so' o submodulo de dados).
- **PDFs**: a tabela/formula de familiar esta em *Player Core* pg. 259
  (feat Pet) e pg. 212 (Familiars); a de eidolon esta em *Secrets of Magic*
  pg. 58. Ambos os PDFs existem em
  `pipeline/dados_brutos/pdfs/PF2e/DM/` (`Player Core 2.pdf` esta la;
  `Player Core` 1 e `Secrets of Magic` NAO aparecem na listagem do diretorio
  de PDFs -- so' `Player Core 2`). Nao precisou ser aberto porque o AoN dump
  ja trouxe o texto completo dessas paginas via `rules.json`/`aon_feats.json`.
- **Pathbuilder (`docs/referencia-pathbuilder/app-local/assets/Pathbuilder2eWebRemastered108b.js`,
  3,9 MB minificado)**: so 18 ocorrencias de "familiar" e 10 de "eidolon"
  no bundle inteiro -- volume baixo demais pra sustentar um builder completo
  de summoner/witch com stat calculado; nao vale o esforco de
  desminificar dado que o AoN + pf2etools ja resolveram o formulario com
  fonte primaria (Paizo) em vez de engenharia reversa de app de terceiro.

## 5. Proximo passo (tamanho do trabalho)

Nao e preciso pedir dump novo nem PDF novo -- os dois estao em disco.
Trabalho de pipeline (fora do escopo desta medicao, so' para dimensionar):

1. **Familiar**: implementar a formula (rules-161/162/163/164/165 legado,
   feat "Pet" + rules-2122 remaster) como CALCULO no motor, igual ja se
   calcula AC/saves/pericias de PC -- nao e extracao de dado, e regra nova
   no motor. `familiar-specific` continua so' concedendo habilidades (ja
   resolvido).
2. **Eidolon**: (a) extrair os 13 arrays de atributo + Dex cap + item bonus
   de AC -- 12/13 prontos no pf2etools (`companionsfamiliars.json`), 1/13
   (Swarm) via parsing da mesma prosa do AoN; (b) HP = pool do invocador,
   sem novo dado; (c) AC/saves/Perception/pericias via mesma formula de
   proficiencia de PC, com a progressao de proficiencia lida das class
   features do Summoner (ja possivelmente na base como `class-feature`,
   nao verificado aqui).

Nenhum dos dois pede tabela inventada: e formula publicada (Paizo, via AoN)
mais, no caso do eidolon, 12 arrays ja estruturados de terceiros
(pf2etools) e 1 array em prosa a parsear.
