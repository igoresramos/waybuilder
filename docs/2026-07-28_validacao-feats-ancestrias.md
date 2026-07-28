# Validacao: kinds de personagem (feat, ancestry, heritage, background, archetype, class, class-feature)

Data: 2026-07-28. Escopo: `pipeline/base/index.json` (base re-emitida hoje,
commit `f98b4b4e5`), cruzamento com os dumps canonicos do AoN em
`pipeline/dados_brutos/aon_ancestries.json`, `aon_heritages.json`,
`aon_backgrounds.json`, `aon_archetypes.json`, `aon_feats.json` e
`aon_censo.json`. Trabalho de MEDICAO -- nenhum `.py` do pipeline/motor foi
alterado.

Metodo: toda contagem saiu de scripts Python rodados contra os arquivos reais
(sem estimativa). Scripts descartaveis em
`/tmp/claude-1000/.../scratchpad/validar.py`, `scan_refs.py`,
`item71_e_prosa.py` (fora do repo, nao commitados).

**Nota metodologica importante:** minha primeira leitura do campo
`remaster_id` dos dumps AoN estava invertida (tratei o alvo apontado como
"superado" quando na verdade e o contrario -- entrada com `remaster_id`
preenchido = versao LEGADA que aponta pra frente pra sua substituta atual;
entrada com `remaster_id=None` = versao atual). Corrigido e validado contra
`aon_censo.json`, que bate exato pros 5 kinds (ancestry 68, heritage 335,
background 499, archetype 244, feat 6085 = contagem canonica do AoN).

**Correcao de contagem:** a tarefa citava feat 6.412, background 637,
heritage 346, archetype 247. Os numeros reais medidos hoje em `index.json`
sao **feat 6.273**, **background 524**, **heritage 334**, **archetype 244**
(ancestry 50 e class-feature 841 bateram exato). A re-emissao de hoje reduziu
esses 4 kinds. Os arquivos de prosa em `pipeline/base/text/` ainda tem mais
chaves do que os registros atuais referenciam (feat 6432, background 637,
heritage 346, archetype 248 chaves -- os numeros antigos da tarefa) --
sao sobras orfas da emissao anterior, nao apagadas na re-emissao. Nao e erro
funcional (nenhum registro atual aponta pra chave ausente), so lixo de prosa.

---

## RESUMO EXECUTIVO

**Cobertura de raridade (o que o dono mais quer saber): muito melhor do que
os numeros brutos sugerem.**

- **ancestry: cobertura PERFEITA.** 50/50 batem nome-a-nome com o AoN
  (tipo "Ancestry", excluindo "Versatile Heritage" que o AoN cataloga junto
  mas que a base corretamente modela como `heritage`). Distribuicao de
  raridade identica: `{rare: 22, uncommon: 20, common: 8}` nos dois lados.
- **heritage: cobertura quase total.** 334/339 nomes esperados; as 5
  faltantes sao todas `common` (heritages de Azarketi de um unico livro).
  Nenhum incomum/raro faltando.
- **background: cobertura PERFEITA por id.** 0 backgrounds canonicos do AoN
  ausentes da base.
- **archetype: cobertura quase total.** Falta so 1 (Jalmeri Heavenseeker,
  uncommon, Pathfinder #158) dos 244 canonicos.
- **feat: cobertura quase total.** Faltam 32 de 6.085 canonicos, dos quais
  so 2 sao uncommon (nenhum rare/unique faltando) -- e os 2 sao dedicacoes
  de arquetipos de aventura-caminho especificos (Jalmeri Heavenseeker,
  Firework Technician).

Ou seja: **a cobertura de incomum/raro que o dono pediu explicitamente esta,
na pratica, completa** para os 7 kinds. O problema real nao e cobertura de
conteudo -- e integridade de vinculo (abaixo).

**Vinculos quebrados reais (excluindo `historico.id_legado`, que e trilha de
auditoria intencional de fusao/renomeacao, nunca lida pelo motor):**

| Origem (kind.campo) | Quebrados | Causa confirmada |
|---|---|---|
| `class.subclasses` (opcoes/so_catalogo) | 46 | ids `-legacy` (pre-remaster) deixados no catalogo de opcoes de barbarian/champion/oracle/witch |
| `feat.requires` | 44 | pre-requisito referenciando slug PRE-remaster de outro feat que foi renomeado (ex.: `wb:feat/stunning-fist` deveria ser `wb:feat/stunning-blows`) |
| `feat.conflitos` | 1 | mesma causa |
| *(fora do escopo dos 7 kinds, mas achado pela varredura pedida)* `deity.favored_weapon` | 509 | prefixo errado: `wb:equipment/x` em vez de `wb:weapon/x` (480 resolveriam so trocando o prefixo) |

**Defeitos ja conhecidos -- status apos re-emissao:**

- **Item 70 (grant_feat nao resolvido em background): NAO MUDOU. Ainda 476**,
  exatamente como reportado (400 dict serializado como string + 76 nome cru).
- **Item 71 (gate `any` multi-classe): CONFIRMADO CONSERTADO.**
  `wb:feat/reach-spell` tem `any` com as 7 classes esperadas. Medindo a base
  inteira: dos 130 feats com 2+ traits de classe, **0 estao travados de
  verdade** numa classe so -- os 53 que pareciam travados numa checagem
  superficial (`all` no topo) na verdade tem um bloco `any` aninhado correto
  (seja por `class_level` seja por `has:` dedicacao). O conserto do item 71
  generalizou bem.

**O que esta certo (nao e defeito, apesar de parecer):**

- As 25 `heritage` "sem campo `ancestry`" (Aasimar, Tiefling, Half-Elf,
  Half-Orc, Ifrit, Changeling, Dhampir etc.) sao **versatile heritages**
  de verdade -- no PF2e remaster elas se aplicam a qualquer ancestria
  qualificada, nao tem vinculo fixo. Confirmado contra o AoN (`type:
  "Versatile Heritage"`). Modelagem correta.
- Prosa: **100% de cobertura** nos 7 kinds, 0 registros com prosa vazia
  (detalhe abaixo).

---

## 1. Raridade e cobertura vs AoN (medido)

### ancestry (50 registros)

```
base:  {rare: 22, uncommon: 20, common: 8}
AoN (type=Ancestry, canonico): {rare: 22, uncommon: 20, common: 8}
```
Match perfeito nome-a-nome (0 faltando de cada lado). As 18 entradas que o
AoN cataloga em `/Ancestries.aspx` mas com `type: "Versatile Heritage"`
(Aphorite, Beastkin, Ifrit, Oread, Suli, Sylph, Undine, Ardande, Talos,
Changeling, Nephilim, Aiuvarin, Dromaar, Dhampir, Dragonblood, Duskwalker,
Hungerseed, Reflection) estao **todas** presentes na base como `heritage`,
o que e o certo.

### heritage (334 registros)

```
base: {common: 300, uncommon: 32, rare: 2}
AoN canonico (335): {common: 302, uncommon: 31, rare: 2}
```
5 ausentes, todas `common`, todas da mesma familia/livro:

- Ancient Scale Azarketi, Benthic Azarketi, Mistbreath Azarketi,
  River Azarketi, Thalassic Azarketi -- `Absalom, City of Lost Omens`
  (heritage-193 a heritage-197)

Nenhum incomum/raro faltando.

### background (524 registros)

```
base: {common: 300, uncommon: 87, rare: 137}
AoN canonico (499): {common: 283, uncommon: 86, rare: 130}
```
**0 backgrounds canonicos do AoN ausentes da base** (comparado por
`xref.aon`). A base tem MAIS registros que o canonico do AoN (524 vs 499)
porque inclui variantes/conflitos de fonte que o AoN considera duplicatas
history-wise -- nao e perda, e sobra controlada.

### archetype (244 registros)

```
base: {common: 101, uncommon: 116, rare: 26, None: 1}
AoN canonico (244): {common: 102, uncommon: 116, rare: 26}
```
1 ausente: **Jalmeri Heavenseeker** (uncommon, Pathfinder #158: Sixty Feet
Under, archetype-86). Ha tambem 1 registro na base com `rarity: None` --
merece checagem de quem esta escrevendo o pipeline (nao investigado a
fundo, fora do escopo de "raridade ausente do AoN").

### feat (6.273 registros)

```
base: {common: 5434, uncommon: 616, rare: 207, None: 16}
AoN canonico (6.085): {common: 5271, uncommon: 616, rare: 198}
```
32 ausentes de 6.085 canonicos. So 2 sao uncommon (0 rare/unique):

- Jalmeri Heavenseeker Dedication (uncommon, feat-8805) -- consequencia
  direta do archetype ausente acima
- Firework Technician Dedication (uncommon, feat-3245, Guns & Gears
  Remastered)

Os outros 30 ausentes sao `common`: 11 sao artigos de humor/paginas nao-
mecanicas ("Dad Joke", "GGGHhhjjjJJK", "Speedrun Strats" -- de "Foolish
Housekeeping and Other Articles" / "Fools Aplenty", conteudo de humor do
1 de abril do site, corretamente descartavel); os demais sao feats reais
de fontes recentes (Player Core 2, World Guide, APG) que vale confirmar
depois com o time do pipeline. Ha tambem 16 feats com `rarity: None` na
base -- mesmo padrao do archetype acima.

**16 feats na base tem `rarity: None`** (nem common/uncommon/rare/unique).
Vale investigar -- pode ser o mesmo bug do archetype com `rarity: None`.

---

## 2. Integridade por kind

### feat (6.273)

- `level`: 100% preenchido (0 faltando).
- `traits`: 11 com lista vazia.
- `requires`: ok pra feats de nivel > 1 (nao contabilizado como faltando em
  massa -- a maioria dos gates de nivel 1 legitimamente nao tem requires).
- Feats de arquetipo (trait `archetype` ou `dedication`): 2.251. Desses,
  so **1** sem o campo `archetype` preenchido: `wb:feat/knight-vigilant`
  (traits `archetype, dedication`, mas sem `archetype: wb:archetype/...`
  apontando pra ninguem). Praticamente 100% linkado (2.250/2.251).

### ancestry (50)

Todos os 7 campos essenciais tem cobertura **100%**: `hp`, `size`, `speed`,
`boosts`, `flaw`, `languages` -- nenhum faltando. `senses` e `{}` vazio em
13 ancestrias (anadi, awakened-animal, conrasu, goloma, halfling, human,
kashrishi, lizardfolk, sarangay, skeleton, tanuki, vanara, yaoguai) -- isso
e esperado, sao ancestrias sem sentido especial no PF2e (nao e defeito).
**50/50 ancestrias completas.**

### heritage (334)

Vinculo com ancestria: 309/334 tem `ancestry` direto. As outras 25 sao
versatile heritages de verdade (ver Resumo Executivo) -- **0 heritages
verdadeiramente orfas**. Nenhum `ancestry` aponta pra id inexistente.

### background (524)

- `boosts` (esperado: 2, um dirigido + um livre): 508/524 tem exatamente 2.
  - **10 tem ZERO boosts** apesar do campo bruto `attribute` estar
    preenchido (ex.: `wb:background/refugee`, `attribute: [Constitution,
    Wisdom]`, `boosts: []`) -- bug de derivacao, nao falta de dado fonte.
  - **4 tem so 1 boost** (falta o boost livre): feral-child,
    magical-experiment, seer-of-the-dead, song-of-the-deep.
  - **2 tem 3 boosts** (amnesiac, discarded-duplicate) -- **isso e
    CORRETO**, essas 2 backgrounds concedem 3 boosts livres por regra
    (Amnesiac da APG realmente da "three free ability boosts"). Nao e
    defeito.
  - **Os mesmos 10 registros com boosts=0 tambem sao os 10 sem
    `skill_training`** (post-guard-of-all-trade, reclaimed-investigator,
    muesellos-student, historical-reeanactor, refugee-fop,
    driver-background-451, refugee, saboteur-background-457,
    wishes-for-riches, archdevil-apostate-background-642) -- confirma que
    e o MESMO bug de derivacao afetando os dois campos nesses 10
    registros especificos, nao dois problemas distintos.
- `grant_feat`: 70/524 sem grant_feat nos `grants`. Nesses 70 o campo bruto
  `feat` tambem esta `None` (dado ausente ja na fonte, nao na derivacao) --
  a maioria e background raro/narrativo (Amnesiac, Cursed, Haunted,
  Royalty, Returned etc.) que trocam o feat de background por uma
  habilidade narrativa especial, o que e correto por regra. Nao
  investigado registro a registro se todos os 70 sao legitimos.
- **444/524 (85%) completos** (2 boosts + skill_training + grant_feat).

**Item 70 confirmado sem mudanca: 476 alvos de `grant_feat` nao resolvidos**,
todos em `background`:
- 400 dict serializado como string (ex.: `"{'name': 'Arcane Sense',
  'foundry_uuid': '...'}"`)
- 76 nome cru (ex.: `"Assurance"`)
- Apenas 25 `grant_feat` resolvem corretamente pra `wb:feat/...`

### archetype (244)

Vinculo com dedicacao (feat com `archetype` apontando + trait `dedication`):
**19 arquetipos sem dedicacao na base**: Apocalypse Rider, Archfiend,
Ascended Celestial, Avenging Runelord, Beast Lord, Broken Chain, Eternal
Legend, Gelid Shard, Godling, Gray Gardener, Hellknight Signifer, Heroic
Scion, Prophesied Monarch, Splinter of Finality, Timewracked, Ursine
Avenger Hood, Warshard Warrior, Wildspell, Bright Lion.

A maioria desses e arquetipo **Mythic** (War of Immortals) -- que no PF2e
remaster nao usa feat de dedicacao tradicional, usa "Mythic Calling"
concedida por trilha mitica, entao pode ser modelagem correta e nao falta
de dado. Nao confirmado individualmente pra cada um dos 19; merece
checagem pontual antes de tratar como bug.

### class-feature (841)

Varredura completa (toda a arvore de todo registro da base, nao so
`progressao`/`subclasses` de `class`): **791/841 citadas em algum lugar,
50 orfas de verdade.** Quebra das 50:

- **19 com trait `ikon`** (+ 2 `extradimensional, ikon`) -- upgrades de
  arma mitica de War of Immortals (Gaze Sharp as Steel, Gleaming Blade,
  Mirrored Aegis, Titan's Breaker etc.). O kind `ikon` (21 registros)
  tem `grants: []` em todos -- **nao referencia nenhuma dessas
  class-features**. Gap de modelagem no kind `ikon`, fora do escopo dos
  7 kinds mas explica 21 das 50 orfas.
- **10 com traits `calling, mythic`** -- mesma historia: o kind
  `mythic-calling` (15 registros) tambem tem `grants: []` em todos,
  nao referencia essas class-features.
- **6 "Gate" elementais** (Air/Earth/Fire/Metal/Water/Wood Gate, Rage of
  Elements) + **1 "Elemental School"** -- o kind `element` (6 registros)
  tambem tem `grants: []`, mesmo padrao.
- **6 "Deviant Classification"** (Blight Soul, Dragon, Flicker, Leech,
  Troll, Verdant Core, Wraith -- Dark Archives/Gatewalkers) -- confirmado:
  o kind `deviant-ability-classification` (10 registros) tambem tem
  `grants: []` em 100% dos registros, mesmo padrao dos outros 3 kinds.
- **3 genuinamente sem lar aparente**: `Focus Spells` (Core Rulebook),
  `Improved Evasion` (Core Rulebook p.166), `Iron Will` (Core Rulebook
  p.66), `Martial Weapon Mastery` (Player Core p.152) -- conferido:
  **nenhuma classe** tem esses ids em `progressao`. Sao features reais
  de regra (Iron Will e a expertise de Vontade nivel 3 do Ranger, por
  exemplo) que existem como registro mas nunca sao concedidas por
  nenhuma classe da base. Bug real de progressao, nao modelagem
  intencional.
- **1 caso**: `wb:class-feature/advanced-vials-toxicologist` -- confirmado
  que o subclasses do Alchemist lista `advanced-vials-bomber`,
  `-chirurgeon`, `-mutagenist` mas **nao** `-toxicologist` no eixo de
  nivel 11 (buraco pontual na lista de opcoes).

---

## 3. Vinculos quebrados (varredura da base inteira)

Varri toda a arvore de todo registro (`id`, `text` excluidos) procurando
strings que casam com o padrao `wb:<kind>/<slug>` e verificando se o alvo
existe no index. **18.497 referencias `wb:` encontradas, 1.319 quebradas.**

Descontando `historico.id_legado`/`historico.chave` (670 ocorrencias -- e
trilha de auditoria de fusao/renomeacao gravada por
`pipeline/fundir_renomeados.py`; **nao existe leitura desse campo em
`motor/*.py`**, confirmado por grep -- e provenance intencional, nunca
resolvido em runtime), sobram **649 referencias questionaveis**:

| kind origem | campo | quebrados | dentro do escopo dos 7 kinds? |
|---|---|---|---|
| deity | favored_weapon | 509 | nao |
| feat | requires | 44 | **sim** |
| class | subclasses (opcoes/so_catalogo) | 46 | **sim** |
| deity | cleric_spell | 25 | nao |
| domain | deities | 16 | nao |
| deity | domains | 5 | nao |
| deity / feat | conflitos | 4 | 1 e feat |

### 3.1 `class.subclasses` -- 46 quebrados, causa confirmada

Barbarian, Champion, Oracle e Witch tem ids `-legacy` (pre-remaster) ainda
listados em `subclasses[].opcoes` e `subclasses[].so_catalogo`, mas o kind
`instinct`/`cause`/`mystery`/`lesson`/`patron` correspondente **so tem a
versao atual**. Exemplo (`wb:class/barbarian`):

```
opcoes: [..., "wb:instinct/animal", "wb:instinct/animal-legacy", ...]
```
`wb:instinct/animal` existe; `wb:instinct/animal-legacy` nao existe em
lugar nenhum da base. Se a UI tentar renderizar essa opcao, quebra. Achados
em: barbarian (instinct, 6 pares), champion (cause, 6 pares), oracle
(mystery, 1), witch (lesson 1 + patron, 8 pares) -- confere com os 46.

### 3.2 `feat.requires` -- 44 quebrados, causa confirmada

Pre-requisito de feat referenciando o **slug pre-remaster** de outro feat
que foi renomeado no remaster, em vez do slug atual. Confirmado nome-a-nome
contra `aon_feats.json` (campo `remaster_id`):

| pre-requisito (quebrado, na base) | deveria ser |
|---|---|
| `wb:feat/stunning-fist` | `wb:feat/stunning-blows` |
| `wb:feat/wild-shape` | `wb:feat/untamed-form` |
| `wb:feat/divine-ally` | `wb:feat/devout-blessing` |
| `wb:feat/attack-of-opportunity` | `wb:feat/reactive-strike` |
| `wb:feat/hellknight-armiger-dedication` | `wb:feat/hellknight-dedication` |
| `wb:feat/drow-shootist-dedication` | `wb:feat/crossbow-infiltrator-dedication` |
| (mais ~15 outros pares, mesmo padrao -- lista completa no script) | |

Isso afeta o **gate de pre-requisito de feats reais e comuns**
(Return Fire, Triangle Shot, Impassable Wall Stance etc. -- todos feats
`common` de classes centrais), diferente do resto dos achados que sao
conteudo raro/de nicho. E o achado de maior impacto pratico desta
validacao: um personagem tentando pegar esses ~30 feats via pre-requisito
"tem Stunning Fist" nunca vai satisfazer o gate, porque o feat-alvo tem
outro nome na base.

2 dos 44 sao `requires.all.nao_modelavel` (`wb:heritage/versatile`,
`wb:heritage/you-have-a-versatile`) -- **auto-sinalizados pelo pipeline
como nao-modelaveis**, ja veem com a bandeira de "nao resolvo isso", entao
nao contam como falha silenciosa.

---

## 4. Prosa (`pipeline/base/text/<kind>.json`)

**100% de cobertura nos 7 kinds -- todo registro atual tem prosa, nenhuma
prosa vazia:**

| kind | registros | com ponteiro `text` | resolve na tabela | prosa vazia |
|---|---|---|---|---|
| feat | 6.273 | 6.273 | 6.273 | 0 |
| ancestry | 50 | 50 | 50 | 0 |
| heritage | 334 | 334 | 334 | 0 |
| background | 524 | 524 | 524 | 0 |
| archetype | 244 | 244 | 244 | 0 |
| class | 27 | 27 | 27 | 0 |
| class-feature | 841 | 841 | 841 | 0 |

As tabelas de texto tem chaves extras nao usadas por nenhum registro atual
(feat: 6.432 chaves pra 6.273 registros = 159 orfas; background: 637 pra
524 = 113 orfas; heritage: 346 pra 334 = 12 orfas; archetype: 248 pra 244 =
4 orfas) -- sao sobras da emissao anterior a de hoje, sem impacto funcional
(nenhum registro atual referencia uma chave ausente), so peso morto no
arquivo.

---

## Achados novos (nao estavam na lista de defeitos conhecidos)

1. **`feat.requires` com slugs pre-remaster mortos (44 casos, ~30 feats
   comuns de classes centrais afetados)** -- maior achado desta validacao.
   Ver secao 3.2.
2. **`class.subclasses` com ids `-legacy` dangling (46 casos em 4
   classes)** -- ver secao 3.1.
3. **10 backgrounds com bug de derivacao identico em `boosts` E
   `skill_training` ao mesmo tempo** (dado bruto presente, campo derivado
   vazio) -- lista completa na secao 2/background.
4. **4 backgrounds com `boosts` faltando o boost livre** (feral-child,
   magical-experiment, seer-of-the-dead, song-of-the-deep).
5. **`Focus Spells`, `Improved Evasion`, `Iron Will`,
   `Martial Weapon Mastery`** (class-feature) nao aparecem em nenhuma
   `progressao` de classe -- feature real de regra, sem lar na base.
6. **Kinds `ikon`, `mythic-calling`, `element` e
   `deviant-ability-classification` tem `grants: []` em 100% dos
   registros** (confirmado nos 4) -- nenhum vincula suas class-features
   associadas (37 das 50 class-features orfas vem desses 4 kinds). Fora do
   escopo dos 7 kinds pedidos, mas e o mesmo tipo de gap de vinculo -- vale um
   passe futuro se esses kinds entrarem em uso na ficha.
7. **`deity.favored_weapon` usa prefixo `wb:equipment/` em vez de
   `wb:weapon/`** (509 ocorrencias, 480 resolveriam so trocando o
   prefixo). Fora do escopo dos 7 kinds, mas achado pela varredura de
   vinculos pedida no item 3 da tarefa.
8. **16 feats e 1 archetype com `rarity: None`** -- nem
   common/uncommon/rare/unique. Nao investigado a fundo.
9. **1 feat de arquetipo sem campo `archetype`**: `wb:feat/knight-vigilant`.

## O que esta confirmado certo

- **Cobertura de raro/incomum nos 7 kinds: essencialmente completa**
  (ancestry 100% exato, background 100% por id, heritage e archetype
  faltando so 1 item cada de raridade relevante, feat faltando 2 uncommon
  de nicho). Isso responde diretamente a prioridade do dono.
- **Item 71 (gate `any` multi-classe) generalizou bem**: 0 feats
  travados numa classe so entre os 130 com 2+ traits de classe.
- **Prosa 100% presente** nos 7 kinds, 0 vazias.
- **Ancestry 100% completa** nos 7 campos essenciais (hp, size, speed,
  boosts, flaw, languages, senses-quando-aplicavel).
- **`ancestry.heritages` -> `heritage.ancestry`**: 0 referencias
  quebradas nessa direcao.
- **Item 70 nao regrediu** (nem melhorou) -- 476 confirmados, numero
  estavel desde antes da re-emissao.

---

Arquivos de trabalho (descartaveis, fora do repo):
`/tmp/claude-1000/-mnt-c-Users-igor0/cf4835ec-3dd1-442c-ad27-6284421f280d/scratchpad/{validar.py,scan_refs.py,item71_e_prosa.py,broken_refs.json,missing_*.json}`
