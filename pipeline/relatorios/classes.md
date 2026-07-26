# Relatorio -- extrator de classes e class-features

Pin do Foundry: `87f9e5028baaa10b70fdc766260b7886def17e04`

## Contagens

- Classes no Foundry (packs/pf2e/classes): **27**
- Arquivos de class-feature no Foundry (packs/pf2e/class-features): **826** (827 arquivos no diretorio, 1 e `_folders.json` -- metadado de pasta do compendio, descartado)
- Registros `class` emitidos: **27**
- Registros `class-feature` emitidos: **986**
- Total de registros emitidos: **1013**
- Features compartilhadas por mais de uma classe (Weapon Specialization, Shield Block etc.): **27** nomes, expandidos em **187** registros (1 por par feature+classe dona, porque o nivel de concessao difere por classe -- ver secao 'Problemas mais serios')
- Features sem dono no `items{}` de nenhuma classe (instintos, doutrinas, bloodlines, edges de cacador etc.) recuperadas via trait: **418** (`prov.class = "foundry (inferido de traits)"`, distinto do caso direto)

## Campo-fonte -> campo-canonico, por fonte

### Foundry (`packs/pf2e/classes/*.json`)

| Campo Foundry | Campo canonico | Quirk |
|---|---|---|
| `system.hp` | `grants[].hp_per_level` | int direto |
| `system.perception` | `grants[].proficiency.perception` | rank 0-4 -> palavra |
| `system.savingThrows.{fortitude,reflex,will}` | `grants[].proficiency.*` | rank 0-4 -> palavra |
| `system.attacks.{simple,martial,advanced,unarmed}` | `grants[].proficiency.*` | rank 0-4 -> palavra |
| `system.attacks.other.{name,rank}` | `grants[].proficiency.<name>` | so incluido se `name` nao vazio |
| `system.defenses.{light,medium,heavy,unarmored}` | `grants[].proficiency.*` | rank 0-4 -> palavra |
| `system.trainedSkills.{value,additional}` | `grants[].skill_training.{auto,free}` | `value` quase sempre vazio nas 27 classes |
| `system.{classFeatLevels,skillFeatLevels,generalFeatLevels,ancestryFeatLevels}.value` | `grants[].feat_slot.{kind,levels}` | 4 grants, um por kind |
| `system.skillIncreaseLevels.value` | `grants[].skill_increase.levels` | **extensao ao vocabulario do schema** -- nao ha verbo pronto na spec pra isso |
| `system.keyAbility.value` | `key_ability` (fora de `grants`) | **campo extra**, nao esta no envelope generico |
| `system.spellcasting` | `spellcasting` (bool, fora de `grants`) | so a FLAG (0/1); a tabela de slots/tradicao real fica em rule elements, nao decodificados nesta passada |
| `system.publication.{license,remaster}` | `source.{license,remaster}` | unica fonte confiavel pra license (AoN nao expoe) |
| `system.publication.title` | `source.book` (fallback) | usado so quando AoN nao bate |
| `system.items{}` (nome+nivel+uuid) | indice de ownership feature->classe(s)+nivel | chave do problema de features compartilhadas |
| `system.rules[]` (classe) | determina `mechanized` | nao decodificado; presenca de rules != [] -> `mechanized:false` |

### Foundry (`packs/pf2e/class-features/*.json`)

| Campo Foundry | Campo canonico | Quirk |
|---|---|---|
| `system.level.value` | `level` | por (feature, classe dona) quando compartilhada |
| `system.traits.value` | `traits` (fallback) | AoN nao expoe traits pra class-feature |
| `system.traits.rarity` | `rarity` (fallback) | AoN normalmente tem, usado como primario |
| `system.subfeatures.proficiencies.<cat>.rank` | `grants[].proficiency.<cat>` | dict `{categoria: {rank:0..4}}`, tratado |
| `system.subfeatures.{senses,languages,keyOptions,suppressedFeatures}` | **nao mapeado** | contribui pra `mechanized:false` -- ver secao de gaps |
| `system.rules[]` (nao-vazio) | **nao mapeado** | contribui pra `mechanized:false` -- ~40 tipos de rule element, fora de escopo desta passada (custo maior do projeto, ver PROJECT.md) |
| `system.prerequisites.value` (prosa) | **nao mapeado pra `requires`** | so 4 features tem; prosa livre, sem marcacao -- ver gaps |
| `system.publication.{license,remaster,title}` | `source.*` | igual ao de classe |

### pf2etools (`data/class/class-<slug>[-pc1].json`)

| Campo pf2etools | Campo canonico | Quirk |
|---|---|---|
| `class[0].hp`, `.remaster`, `.source` | usado so pra decidir geracao (legado/remaster) do arquivo | nao sobrescreve nenhum campo do Foundry nesta passada |
| `classFeature[].level` (por classe) | cross-check contra `level` do Foundry | so quando o arquivo da classe dona foi resolvido |
| `subclassFeature[].level` | mesmo cross-check, pra feature de subclasse | mesclado com `classFeature` na busca por nome |
| `classFeatures[]` (string `Nome|Classe|Fonte|Nivel`) | **nao usado diretamente** | preferi o array `classFeature` (tem `.level` como int, sem parsear string) |

### Archives of Nethys (`elasticsearch.aonprd.com/aon/_search`)

| Campo AoN | Campo canonico | Quirk |
|---|---|---|
| `name` | `name` (primario) | `match_phrase`, nunca `terms`/`term` em campo de texto (retorna zero, armadilha documentada na spec) |
| `rarity` | `rarity` (primario) | presente em class e class-feature |
| `primary_source` | `source.book` (primario) | |
| `primary_source_raw` ("Player Core pg. 136") | `source.page` | parse por regex `pg\.\s*(\d+)` |
| `legacy_id` / `remaster_id` | ponte legado<->remaster, usada pra escolher a geracao certa do hit | doc com `remaster_id` preenchido = e o LEGADO; doc com `legacy_id` preenchido = e o REMASTER |
| `class` (so em class-feature) | usado pra desambiguar quando a feature e compartilhada | ex.: "Weapon Specialization" tem um doc por classe dona, nao um doc so |
| `traits` | **ausente** em class e class-feature | confirmado por amostragem; `traits` cai pro Foundry sempre |
| `license` | **ausente** | AoN nao expoe OGL/ORC; `source.license` vem sempre do Foundry |

## Campos que NAO consegui mapear

- **`requires` (pre-requisito) em class-feature.** So 4 dos 826 arquivos tem `system.prerequisites.value` preenchido (Way of the Spellshot, Flexible Spell Preparation, Elemental Magic, Wellspring Magic), e e prosa livre sem marcacao `{@feat}`/`{@skill}` -- o pf2etools (fonte vencedora pra `requires`) nao guarda prerequisites estruturados no nivel de class-feature (isso existe pra `feat`, que e outro extrator). Traduzir a prosa pra `all`/`any`/`class_level` exigiria parsing de linguagem natural -- decidi deixar `requires` ausente nesses 4 casos em vez de inventar estrutura. Nomes: Elemental Magic, Flexible Spell Preparation, Way of the Spellshot, Wellspring Magic.

- **`system.subfeatures.{senses,languages,keyOptions,suppressedFeatures}`.** 245 features tem `proficiencies` (traduzido pra `grants[].proficiency`), mas 81 tem `senses`, 85 `suppressedFeatures`, 15 `languages`, 9 `keyOptions` -- nenhum desses quatro foi traduzido pra `grants` nesta passada. Contribuem pra `mechanized:false`.

- **`system.rules[]` (rule elements) em geral.** 593/826 features tem pelo menos 1 rule element nao-trivial (ChoiceSet, GrantItem, FlatModifier, MartialProficiency, CriticalSpecialization etc.). Decidir decodificar isso e o item de maior custo do projeto (ja registrado assim em PROJECT.md) -- fora de escopo desta entrega. Essas features saem com `mechanized:false` e `grants` parcial (so a parte de `subfeatures.proficiencies`, quando existe).

- **Tabela de spellcasting (slots por nivel, tradicao).** `system.spellcasting` no arquivo de classe e so uma flag 0/1 dizendo se a classe conjura. A tabela real (progressao de slots, foco, preparado x repertorio) vive espalhada em rule elements de class-features especificas (ex.: "Arcane Spellcasting"), nao decodificada. `spellcasting` sai como bool solto, sem `spell_slots`.

- **4 classes sem nenhum arquivo no pf2etools:** Animist, Commander, Exemplar, Guardian -- Animist, Commander, Exemplar e Guardian sao classes recentes (War of Immortals / Battlecry!) que o branch `dev` do pf2etools ainda nao portou em `data/class/`. Cross-check de nivel pulado pra elas; `xref.pf2etools` fica `null`.

- **`source.page` ausente por falta de match no AoN:** 0 classes, 444 class-features (ver listas de nomes sem match na secao seguinte).

## Divergencias reais encontradas

### 1. Modelo de dados diferente para features compartilhadas
O Foundry guarda **um arquivo por class-feature**, referenciado (nome+nivel+uuid) pelas classes que a concedem -- ex. `Weapon Specialization.json` e um arquivo so, listado no `items{}` de 25 classes diferentes, cada uma com um `level` proprio (Fighter recebe no 7, Wizard no 13). O AoN, ao contrario, indexa **um documento por classe dona** (`class-feature-167` = Fighter Weapon Specialization nivel 7, `class-feature-300` = Wizard Weapon Specialization nivel 13, etc. -- 72 hits so pro nome "Weapon Specialization"). O pf2etools segue o mesmo padrao do AoN (nivel dentro do array `classFeature` de cada classe). Resolvido expandindo o registro canonico em 1-por-(feature,classe) quando o nivel diverge entre classes donas -- 27 nomes, 187 registros expandidos. Ver 'Problemas mais serios' abaixo -- isso deveria estar na spec.

### 2. Nivel divergente entre Foundry e pf2etools

| Feature | Classe | Foundry | pf2etools |
|---|---|---|---|
| Evasion | Gunslinger | 7 | 11 |

### 3. Geracao (legado x remaster) divergente entre Foundry e pf2etools
Classes onde o Foundry considera o conteudo remasterizado (`publication.remaster: true`, licenca ORC) mas o arquivo disponivel no pf2etools ainda e o legado (pre-remaster, licenca OGL/CRB/APG original):

| Classe | Arquivo pf2etools usado | Nota |
|---|---|---|
| Alchemist | class-alchemist.json | arquivo class-alchemist.json e geracao legado, Foundry e remaster -- geracoes divergentes, cross-check de nivel ainda tentado (numero de nivel raramente muda entre geracoes) |
| Barbarian | class-barbarian.json | arquivo class-barbarian.json e geracao legado, Foundry e remaster -- geracoes divergentes, cross-check de nivel ainda tentado (numero de nivel raramente muda entre geracoes) |
| Champion | class-champion.json | arquivo class-champion.json e geracao legado, Foundry e remaster -- geracoes divergentes, cross-check de nivel ainda tentado (numero de nivel raramente muda entre geracoes) |
| Gunslinger | class-gunslinger.json | arquivo class-gunslinger.json e geracao legado, Foundry e remaster -- geracoes divergentes, cross-check de nivel ainda tentado (numero de nivel raramente muda entre geracoes) |
| Inventor | class-inventor.json | arquivo class-inventor.json e geracao legado, Foundry e remaster -- geracoes divergentes, cross-check de nivel ainda tentado (numero de nivel raramente muda entre geracoes) |
| Investigator | class-investigator.json | arquivo class-investigator.json e geracao legado, Foundry e remaster -- geracoes divergentes, cross-check de nivel ainda tentado (numero de nivel raramente muda entre geracoes) |
| Monk | class-monk.json | arquivo class-monk.json e geracao legado, Foundry e remaster -- geracoes divergentes, cross-check de nivel ainda tentado (numero de nivel raramente muda entre geracoes) |
| Oracle | class-oracle.json | arquivo class-oracle.json e geracao legado, Foundry e remaster -- geracoes divergentes, cross-check de nivel ainda tentado (numero de nivel raramente muda entre geracoes) |
| Psychic | class-psychic.json | arquivo class-psychic.json e geracao legado, Foundry e remaster -- geracoes divergentes, cross-check de nivel ainda tentado (numero de nivel raramente muda entre geracoes) |
| Sorcerer | class-sorcerer.json | arquivo class-sorcerer.json e geracao legado, Foundry e remaster -- geracoes divergentes, cross-check de nivel ainda tentado (numero de nivel raramente muda entre geracoes) |
| Swashbuckler | class-swashbuckler.json | arquivo class-swashbuckler.json e geracao legado, Foundry e remaster -- geracoes divergentes, cross-check de nivel ainda tentado (numero de nivel raramente muda entre geracoes) |
| Thaumaturge | class-thaumaturge.json | arquivo class-thaumaturge.json e geracao legado, Foundry e remaster -- geracoes divergentes, cross-check de nivel ainda tentado (numero de nivel raramente muda entre geracoes) |

## mechanized: true x false

- `mechanized: true`: **312** / 1013
- `mechanized: false`: **701** / 1013

Uma class-feature sai `mechanized:true` só quando `system.rules` está vazio **e** `system.subfeatures` só contém `proficiencies` (ou está vazio). Motivos de `mechanized:false` mais comuns:

| Motivo | Ocorrencias |
|---|---|
| rule-elements-nao-traduzidos | 569 |
| subfeatures-nao-traduzidas | 94 |
| class:rules-nao-traduzidas(1) | 2 |
| class:rules-nao-traduzidas(2) | 1 |
| class:rules-nao-traduzidas(3) | 1 |
| class:rules-nao-traduzidas(4) | 1 |

## Sem match no AoN

- Classes sem nenhum hit: (nenhuma)
- Class-features sem nenhum hit (431): Adept Benefit (Amulet), Adept Benefit (Bell), Adept Benefit (Chalice), Adept Benefit (Lantern), Adept Benefit (Mirror), Adept Benefit (Regalia), Adept Benefit (Shield), Adept Benefit (Tome), Adept Benefit (Wand), Adept Benefit (Weapon), Advanced Alchemy, Advanced Design, Advanced Rangefinder, Aerodynamic Construction, Air Gate, Alchemical Sciences Methodology, Alchemist Armor Expertise (Level 13), Alchemist Armor Mastery (Level 19), All-Consuming Hunger, Aloof Firmament, Amulet, Ancestors, Angel Eidolon, Anger Phantom Eidolon, Animal Instinct, Animal Order, Antimagic Plating, Anvil's Hardness, Armor Innovation, Ashes, Attack Refiner, Automated Impediments, Avenger, Baba Yaga, Bands of Imprisonment, Barrow's Edge, Battle Creed, Battledancer, Beast Eidolon, Bell...

Investiguei uma amostra manual dessas ~431 (52% dos 826 arquivos). A causa dominante nao e falha de busca: o AoN usa **categorias proprias pras escolhas de subclasse**, diferentes de `class-feature` -- ex. "Ancestors" (misterio de Oraculo) vive em `category:mystery`, "Baba Yaga" (patrona de Bruxa) em `category:patron`. Confirmado por amostragem: `bloodline`/`instinct`/`doctrine`/`order`/`mystery`/`patron` sao categorias reais e distintas no indice `aon`. Um segundo grupo (ex. "Angel Eidolon", boons de eidolon do Summoner) parece **nao ter doc proprio no AoN em nenhuma categoria** -- fica so descrito dentro da pagina da classe. Decidi NAO adicionar uma cascata de categorias alternativas nesta passada: o teste que fiz com `category:feat` como fallback (antes de restringir a cascata so a `class-feature`) causou colisao real -- "Advanced Alchemy" existe como class-feature nativa do Alchemist E como feat de arquetipo (Alchemist Dedication), duas entidades diferentes com o mesmo nome. Uma cascata de categorias (`mystery`, `patron`, `instinct`, `doctrine`, `order`...) e viavel e recuperaria boa parte dos 431, mas cada categoria precisa ser validada campo-a-campo antes de confiar nela pra `source`/`rarity` -- fica pra uma proxima passada.

## Colisoes de id (achado real, nao teorico)

O pack `class-features` do Foundry ainda tem itens **orfaos** (nao referenciados no `items{}` de nenhuma classe) que sao duplicatas mortas de features que o remaster consolidou num item compartilhado -- ex. `Druid Weapon Expertise` (Core Rulebook, orfao) e a `Weapon Expertise` compartilhada (Player Core, referenciada por 25 classes) descrevem a mesma coisa pro Druid, e o slug de ambas colide (`slugify("Druid Weapon Expertise")` == `druid-` + `slugify("Weapon Expertise")`). Desambiguado com sufixo `-dupN` deterministico em vez de sobrescrever silenciosamente:

| Id original | Id novo | Nome | xref.foundry |
|---|---|---|---|
| `wb:class-feature/druid-weapon-expertise` | `wb:class-feature/druid-weapon-expertise-dup2` | Druid Weapon Expertise | Compendium.pf2e.classfeatures.Item.Ra32tlqBxHzT6fzN |
| `wb:class-feature/psychic-weapon-expertise` | `wb:class-feature/psychic-weapon-expertise-dup2` | Psychic Weapon Expertise | Compendium.pf2e.classfeatures.Item.kLschzVZFoe3U63C |
| `wb:class-feature/wizard-weapon-expertise` | `wb:class-feature/wizard-weapon-expertise-dup2` | Wizard Weapon Expertise | Compendium.pf2e.classfeatures.Item.GBsC2cARoFiqMi9V |

## Os 3 problemas mais serios

1. **O envelope da spec assume `level` escalar, mas ~27 features (187 pares feature+classe) tem nivel diferente por classe dona.** A spec precisa de uma decisao explicita: canonizar por (feature,classe) como fiz aqui (que muda a contagem total de ~29.236 registros estimados em PROJECT.md pra cima), ou manter 1 registro por feature com um `level` que vira dict `{classe: nivel}` em vez de int. Optei pela primeira porque bate com o proprio modelo do AoN e do pf2etools (eles ja tratam como entidades separadas), mas isso e uma decisao de arquitetura, nao um detalhe de implementacao -- deveria voltar pra spec.

2. **RAW de spellcasting nao esta neste extrator.** `spellcasting` sai como bool solto; a tabela de slots por nivel/tradicao (que faz Mago, Clerigo etc. funcionarem no builder) vive em rule elements de class-features especificas e nao foi decodificada. Sem isso as classes conjuradoras ficam com `mechanized:false` na pratica ainda que o registro da CLASSE em si saia `true` -- o builder vai calcular progressao de feat/proficiencia mas nao vai saber quantos slots de magia a classe tem.

3. **pf2etools no branch `dev`, no snapshot baixado agora, nao tem a geracao remaster pra 8 das 12 classes originarias do Player Core 2** (Alchemist, Barbarian, Champion, Investigator, Monk, Oracle, Sorcerer, Swashbuckler) nem arquivo nenhum pra 4 classes novas (Animist, Commander, Exemplar, Guardian). Isso significa que ~12/27 classes ficam sem cross-check de `level` confiavel contra a fonte que a spec desginou como autoridade pra isso -- o Foundry vira fonte unica de fato pra elas, contrariando a garantia de dupla-fonte que a spec pede ("ha duas fontes independentes -- divergencia e bug"). Se o pf2etools atualizar o branch dev depois, vale re-rodar.

