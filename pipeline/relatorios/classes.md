# Relatorio -- extrator de classes e class-features

Pin do Foundry: `87f9e5028baaa10b70fdc766260b7886def17e04`

Este extrator foi reescrito em 2026-07-26 pra corrigir um defeito de modelagem: a versao anterior duplicava o registro de uma class-feature compartilhada por (feature, classe dona), porque tratava `level` como campo escalar da feature. Ver spec, secao 'Nivel de class-feature pertence a classe, nao a feature'. Esta secao inicial documenta o antes/depois; o resto do relatorio segue o formato de sempre.

## Antes x depois (fix de modelagem)

- Registros `class-feature` **antes** (1 por par feature+classe dona): **986**
- Registros `class-feature` **depois** (1 por arquivo do Foundry, sem `level`): **826**
- Reducao por deduplicacao: **160** registros (**16.2%**)
- Total de registros emitidos: antes **1013**, depois **853**

## Contagens

- Classes no Foundry (packs/pf2e/classes): **27**
- Arquivos de class-feature no Foundry (packs/pf2e/class-features): **826** (827 arquivos no diretorio, 1 e `_folders.json` -- metadado de pasta do compendio, descartado)
- Registros `class` emitidos: **27**
- Registros `class-feature` emitidos: **826** (1:1 com arquivos do Foundry)
- Total de registros emitidos: **853**
- Features com **2 ou mais** classes donas (compartilhadas de fato -- Weapon Specialization, Shield Block etc.): **27**, cada uma emitida como **1 registro** com N entradas de `progressao` (uma por classe), em vez dos N registros duplicados de antes
- Features sem dono direto no `items{}` de nenhuma classe (instintos, doutrinas, bloodlines, edges de cacador etc.) recuperadas via trait unico: **414** (`prov.class = "foundry (inferido de traits)"`)
- Vinculos classe->feature resolvidos via sufixo do `uuid` do Foundry (o `name` cacheado em `items{}` estava desatualizado -- achado real, ver secao 'Casamento de ownership'): **14**
- Vinculos classe->feature que ficaram sem match (nem por nome nem por uuid): **0**

### Distribuicao de N classes donas por feature

| N classes donas | Quantas features |
|---|---|
| 0 | 62 |
| 1 | 737 |
| 2 | 3 |
| 3 | 2 |
| 4 | 6 |
| 5 | 1 |
| 6 | 2 |
| 7 | 3 |
| 8 | 1 |
| 9 | 1 |
| 10 | 3 |
| 12 | 2 |
| 13 | 1 |
| 14 | 1 |
| 25 | 1 |

## Casamento de ownership (items{} -> arquivo de feature)

`system.items{}` de uma classe guarda um `name` cacheado no momento em que o item foi vinculado ao compendio. Achado real: esse cache fica desatualizado em alguns casos -- ex. Ranger referencia corretamente `"Weapon Mastery"`, mas Cleric ainda cacheia `"Deity"` pro item que hoje se chama `"Deity (Cleric)"`. O casamento tenta primeiro o `name` cacheado; quando falha, cai pro sufixo do `uuid` (que referencia por nome tambem, mas pode estar desatualizado na direcao oposta -- por isso so e tentado depois do `name` direto). Sem essa 2a tentativa, **14** vinculos ficariam invisiveis e as classes correspondentes sairiam com `progressao` incompleta.

## Progressao por classe

`progressao` de uma classe mistura 2 origens: entradas **diretas** (vieram do `items{}` da propria classe -- feat de nivel fixo) e entradas **inferidas** (a feature nao tem slot de nivel fixo, foi recuperada via trait unico -- tipicamente escolha de subclasse: instinto, doutrina, bloodline etc.). Cobertura so faz sentido medida contra a parte direta; a parte inferida e um extra legitimo, nao uma duplicata (por isso um total de `progressao` MAIOR que `items{}` e esperado e normal, nao e sinal de erro).

- Classes com `progressao` direta cobrindo 100% das entradas de `items{}`: **27** / 27

Todas as 27 classes tem `progressao` direta completa em relacao ao `items{}` do Foundry (depois do fallback por uuid).

## Casos de mesmo nome, conteudo diferente (mantidos separados)

Grupos onde a base do nome (antes do sufixo parentizado) se repete, mas o conteudo e diferente por classe/variante -- **mantidos como registros distintos**, com `id`/slug proprios (nunca colapsados em nome): **22** grupos, **98** registros no total.

| Nome-base | Variantes distintas | N |
|---|---|---|
| Adept Benefit | Adept Benefit (Amulet), Adept Benefit (Bell), Adept Benefit (Chalice), Adept Benefit (Lantern), Adept Benefit (Mirror), Adept Benefit (Regalia), Adept Benefit (Shield), Adept Benefit (Tome), Adept Benefit (Wand), Adept Benefit (Weapon) | 10 |
| Initiate Benefit | Initiate Benefit (Amulet), Initiate Benefit (Bell), Initiate Benefit (Chalice), Initiate Benefit (Lantern), Initiate Benefit (Mirror), Initiate Benefit (Regalia), Initiate Benefit (Shield), Initiate Benefit (Tome), Initiate Benefit (Wand), Initiate Benefit (Weapon) | 10 |
| Paragon Benefit | Paragon Benefit (Amulet), Paragon Benefit (Bell), Paragon Benefit (Chalice), Paragon Benefit (Lantern), Paragon Benefit (Mirror), Paragon Benefit (Regalia), Paragon Benefit (Shield), Paragon Benefit (Tome), Paragon Benefit (Wand), Paragon Benefit (Weapon) | 10 |
| Spell Repertoire | Spell Repertoire, Spell Repertoire (Bard), Spell Repertoire (Oracle), Spell Repertoire (Psychic), Spell Repertoire (Sorcerer), Spell Repertoire (Summoner) | 6 |
| Advanced Vials | Advanced Vials, Advanced Vials (Bomber), Advanced Vials (Chirurgeon), Advanced Vials (Mutagenist), Advanced Vials (Toxicologist) | 5 |
| Field Discovery | Field Discovery, Field Discovery (Bomber), Field Discovery (Chirurgeon), Field Discovery (Mutagenist), Field Discovery (Toxicologist) | 5 |
| Greater Field Discovery | Greater Field Discovery, Greater Field Discovery (Bomber), Greater Field Discovery (Chirurgeon), Greater Field Discovery (Mutagenist), Greater Field Discovery (Toxicologist) | 5 |
| Perpetual Infusions | Perpetual Infusions, Perpetual Infusions (Bomber), Perpetual Infusions (Chirurgeon), Perpetual Infusions (Mutagenist), Perpetual Infusions (Toxicologist) | 5 |
| Perpetual Perfection | Perpetual Perfection, Perpetual Perfection (Bomber), Perpetual Perfection (Chirurgeon), Perpetual Perfection (Mutagenist), Perpetual Perfection (Toxicologist) | 5 |
| Perpetual Potency | Perpetual Potency, Perpetual Potency (Bomber), Perpetual Potency (Chirurgeon), Perpetual Potency (Mutagenist), Perpetual Potency (Toxicologist) | 5 |
| Masterful Hunter | Masterful Hunter, Masterful Hunter (Flurry), Masterful Hunter (Outwit), Masterful Hunter (Precision) | 4 |
| Fifth Doctrine | Fifth Doctrine, Fifth Doctrine (Cloistered Cleric), Fifth Doctrine (Warpriest) | 3 |
| Final Doctrine | Final Doctrine, Final Doctrine (Cloistered Cleric), Final Doctrine (Warpriest) | 3 |
| First Doctrine | First Doctrine, First Doctrine (Cloistered Cleric), First Doctrine (Warpriest) | 3 |
| Fourth Doctrine | Fourth Doctrine, Fourth Doctrine (Cloistered Cleric), Fourth Doctrine (Warpriest) | 3 |
| Second Doctrine | Second Doctrine, Second Doctrine (Cloistered Cleric), Second Doctrine (Warpriest) | 3 |
| Third Doctrine | Third Doctrine, Third Doctrine (Cloistered Cleric), Third Doctrine (Warpriest) | 3 |
| Anathema | Anathema (Cleric), Anathema (Druid) | 2 |
| Deity | Deity (Champion), Deity (Cleric) | 2 |
| Greater Weapon Specialization | Greater Weapon Specialization, Greater Weapon Specialization (Barbarian) | 2 |
| ... | mais 2 grupos | |

Exemplo do proprio criterio da spec: `Field Discovery` do Alchemist tem a versao generica (nivel 5, escolhida antes de definir o campo de pesquisa) mais 4 variantes por campo de pesquisa (Bomber/Chirurgeon/Mutagenist/Toxicologist), cada uma com `grants` proprio -- 5 registros. `Deity` tem 2 variantes (`Deity (Champion)`, `Deity (Cleric)`) porque a mecanica de escolher divindade difere por classe. Nenhum desses foi fundido.

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
| `system.items{}` (nome+nivel+uuid) | `progressao[].{nivel,concede}` da classe | **campo novo** -- nivel de class-feature agora mora aqui, nao na feature |
| `system.rules[]` (classe) | determina `mechanized` | nao decodificado; presenca de rules != [] -> `mechanized:false` |

### Foundry (`packs/pf2e/class-features/*.json`)

| Campo Foundry | Campo canonico | Quirk |
|---|---|---|
| `system.level.value` | **nao emitido na feature** | vira `progressao[].nivel` na(s) classe(s) dona(s), ver acima |
| `system.traits.value` | `traits` (fallback) | AoN nao expoe traits pra class-feature; sem filtragem por dono (feature compartilhada tem trait de todas as classes de fato) |
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
| `classFeature[].level` (por classe) | cross-check contra `progressao[].nivel` dessa classe | so quando o arquivo da classe dona foi resolvido; conflito vira `conflitos[]` na FEATURE (campo `progressao.nivel`), com `classe` anotada |
| `subclassFeature[].level` | mesmo cross-check, pra feature de subclasse | mesclado com `classFeature` na busca por nome |
| `classFeatures[]` (string `Nome|Classe|Fonte|Nivel`) | **nao usado diretamente** | preferi o array `classFeature` (tem `.level` como int, sem parsear string) |

### Archives of Nethys (`elasticsearch.aonprd.com/aon/_search`)

| Campo AoN | Campo canonico | Quirk |
|---|---|---|
| `name` | `name` (primario) | so aceito quando bate EXATO com o nome do Foundry -- AoN indexa 1 doc por classe dona (as vezes com nome distinto, ex. `"Martial Weapon Mastery"` = nome legado de Ranger pro que hoje e `"Weapon Mastery"`); um match aproximado nunca sobrescreve `name` (ver `escolher_hit_aon_feature`) |
| `rarity`, `primary_source`, `primary_source_raw` | `rarity`/`source.book`/`source.page` | aceito com match exato OU aproximado (nome-base sem parenteses); representa 1 classe dona escolhida deterministicamente (a 1a em ordem alfabetica com hit), nao a media/uniao de todas -- ver 'Problemas que restam' |
| `legacy_id` / `remaster_id` | ponte legado<->remaster, usada pra escolher a geracao certa do hit | doc com `remaster_id` preenchido = e o LEGADO; doc com `legacy_id` preenchido = e o REMASTER |
| `class` (so em class-feature) | usado pra escolher o hit quando a feature e compartilhada | ex.: "Weapon Mastery" tem ate 13 docs (1 por classe dona) so pra geracao remaster |
| `traits` | **ausente** em class e class-feature | confirmado por amostragem; `traits` cai pro Foundry sempre |
| `license` | **ausente** | AoN nao expoe OGL/ORC; `source.license` vem sempre do Foundry |

## Cobertura de `grants` (mechanized true/false)

- Antes: `mechanized:true` **312** / 1013 (**30.8%**)
- Depois: `mechanized:true` **255** / 853 (**29.9%**)

A logica de traducao pra `grants` (subfeatures.proficiencies + presenca de `rules`) **nao mudou** -- e a mesma formula de antes, aplicada por arquivo do Foundry. A cobertura *proporcional* (percentual) fica estatisticamente equivalente; o que mudou foi so o denominador, porque antes cada feature compartilhada inflava tanto o numerador quanto o denominador N vezes (1 por classe dona, todas com o mesmo `mechanized`). A leitura correta: **cobertura de grants nao melhorou nem piorou em essencia -- so parou de ser contada em duplicidade.**

| Motivo (mechanized:false) | Ocorrencias |
|---|---|
| rule-elements-nao-traduzidos | 569 |
| subfeatures-nao-traduzidas | 94 |
| class:rules-nao-traduzidas(1) | 2 |
| class:rules-nao-traduzidas(2) | 1 |
| class:rules-nao-traduzidas(3) | 1 |
| class:rules-nao-traduzidas(4) | 1 |

## Campos que NAO consegui mapear

- **`requires` (pre-requisito) em class-feature.** So 4 dos 826 arquivos tem `system.prerequisites.value` preenchido (Way of the Spellshot, Flexible Spell Preparation, Elemental Magic, Wellspring Magic), e e prosa livre sem marcacao `{@feat}`/`{@skill}` -- o pf2etools (fonte vencedora pra `requires`) nao guarda prerequisites estruturados no nivel de class-feature (isso existe pra `feat`, que e outro extrator). Traduzir a prosa pra `all`/`any`/`class_level` exigiria parsing de linguagem natural -- decidi deixar `requires` ausente nesses 4 casos em vez de inventar estrutura. Nomes: Elemental Magic, Flexible Spell Preparation, Way of the Spellshot, Wellspring Magic.

- **`system.subfeatures.{senses,languages,keyOptions,suppressedFeatures}`.** Nenhum desses quatro foi traduzido pra `grants` nesta passada -- contribuem pra `mechanized:false` (ver tabela de motivos acima).

- **`system.rules[]` (rule elements) em geral.** Maioria das 826 features tem pelo menos 1 rule element nao-trivial (ChoiceSet, GrantItem, FlatModifier, MartialProficiency, CriticalSpecialization etc.). Decidir decodificar isso e o item de maior custo do projeto (ja registrado assim em PROJECT.md) -- fora de escopo desta entrega. Essas features saem com `mechanized:false` e `grants` parcial (so a parte de `subfeatures.proficiencies`, quando existe).

- **Tabela de spellcasting (slots por nivel, tradicao).** `system.spellcasting` no arquivo de classe e so uma flag 0/1 dizendo se a classe conjura. A tabela real (progressao de slots, foco, preparado x repertorio) vive espalhada em rule elements de class-features especificas (ex.: "Arcane Spellcasting"), nao decodificada. `spellcasting` sai como bool solto, sem `spell_slots`.

- **4 classes sem nenhum arquivo no pf2etools:** Animist, Commander, Exemplar, Guardian -- Animist, Commander, Exemplar e Guardian sao classes recentes (War of Immortals / Battlecry!) que o branch `dev` do pf2etools ainda nao portou em `data/class/`. Cross-check de nivel pulado pra elas; `xref.pf2etools` fica `null`.

- **`source.page` ausente por falta de match no AoN:** 0 classes, 431 class-features (ver listas de nomes sem match na secao seguinte).

- **`source.page`/`source.book` de uma feature compartilhada representa 1 classe dona, nao todas.** Quando N classes tem a mesma feature, cada uma pode ter sido publicada numa pagina diferente do livro daquela classe (ex.: Weapon Mastery pg. 104 no capitulo do Champion, pg. 166 no do Ranger). O registro unico so guarda uma pagina (a 1a classe dona em ordem alfabetica com hit exato no AoN) -- perda de informacao aceita conscientemente em troca de nao duplicar o registro. Se isso importar pro builder, a pagina por classe teria que virar parte da `progressao`, nao do registro da feature -- decisao de spec, nao de implementacao.

## Divergencias reais encontradas

### 1. Nivel divergente entre Foundry e pf2etools (por classe dona)

| Feature | Classe | Foundry | pf2etools |
|---|---|---|---|
| Evasion | Gunslinger | 7 | 11 |

### 2. Geracao (legado x remaster) divergente entre Foundry e pf2etools
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

## Sem match no AoN

- Classes sem nenhum hit: (nenhuma)
- Class-features com match de nome EXATO: **340**
- Class-features so com match APROXIMADO (nome-base, sem parenteses -- usado so pra rarity/source/page, nunca pra `name`): **55**
- Class-features sem nenhum hit (431): Adept Benefit (Amulet), Adept Benefit (Bell), Adept Benefit (Chalice), Adept Benefit (Lantern), Adept Benefit (Mirror), Adept Benefit (Regalia), Adept Benefit (Shield), Adept Benefit (Tome), Adept Benefit (Wand), Adept Benefit (Weapon), Advanced Alchemy, Advanced Design, Advanced Rangefinder, Aerodynamic Construction, Air Gate, Alchemical Sciences Methodology, Alchemist Armor Expertise (Level 13), Alchemist Armor Mastery (Level 19), All-Consuming Hunger, Aloof Firmament, Amulet, Ancestors, Angel Eidolon, Anger Phantom Eidolon, Animal Instinct, Animal Order, Antimagic Plating, Anvil's Hardness, Armor Innovation, Ashes, Attack Refiner, Automated Impediments, Avenger, Baba Yaga, Bands of Imprisonment, Barrow's Edge, Battle Creed, Battledancer, Beast Eidolon, Bell...

Investigacao da passada anterior (mantida valida): a causa dominante do 'sem match' nao e falha de busca -- o AoN usa **categorias proprias pras escolhas de subclasse**, diferentes de `class-feature` (`mystery`, `patron`, `instinct`, `doctrine`, `order` etc.). Uma cascata de categorias alternativas e viavel mas arriscada sem validacao campo-a-campo (colisao real testada com `category:feat` -- "Advanced Alchemy" existe como class-feature nativa do Alchemist E como feat de arquetipo, duas entidades diferentes com o mesmo nome) -- fica pra uma proxima passada, nao mexida nesta.

## Colisoes de id

Nenhuma. Com o fix de modelagem, o slug de uma class-feature nunca mais leva prefixo de classe (e sempre `slugify(name)` puro) -- as 3 colisoes da passada anterior (Druid/Psychic/Wizard Weapon Expertise colidindo com o slug prefixado `<classe>-weapon-expertise`) deixaram de ser possiveis por construcao: os 826 arquivos do Foundry tem 826 nomes distintos, confirmado por inspecao direta. `verificar_colisoes_de_id()` continua rodando como rede de seguranca (o build deve falhar de forma auditavel, nunca sobrescrever em silencio), mas nao encontrou nada pra desambiguar nesta rodada.

## Problemas que restam (nao resolvidos nesta passada)

1. **RAW de spellcasting nao esta neste extrator.** `spellcasting` sai como bool solto; a tabela de slots por nivel/tradicao (que faz Mago, Clerigo etc. funcionarem no builder) vive em rule elements de class-features especificas e nao foi decodificada. Sem isso as classes conjuradoras ficam com `mechanized:false` na pratica ainda que o registro da CLASSE em si saia `true` -- o builder vai calcular progressao de feat/proficiencia mas nao vai saber quantos slots de magia a classe tem.

2. **pf2etools no branch `dev`, no snapshot baixado agora, nao tem a geracao remaster pra 8 das 12 classes originarias do Player Core 2** (Alchemist, Barbarian, Champion, Investigator, Monk, Oracle, Sorcerer, Swashbuckler) nem arquivo nenhum pra 4 classes novas (Animist, Commander, Exemplar, Guardian). Isso significa que ~12/27 classes ficam sem cross-check de nivel confiavel contra a fonte que a spec designou como autoridade pra isso -- o Foundry vira fonte unica de fato pra elas, contrariando a garantia de dupla-fonte que a spec pede ("ha duas fontes independentes -- divergencia e bug"). Se o pf2etools atualizar o branch dev depois, vale re-rodar.

3. **`source.page`/`source.book` de feature compartilhada representa so 1 classe dona** (a 1a em ordem alfabetica com hit exato no AoN), nao a pagina real em cada capitulo de classe -- ver secao 'Campos que NAO consegui mapear'. Se o builder precisar mostrar "pg. X no capitulo do Fighter, pg. Y no do Wizard", isso e uma decisao de spec (page por entrada de `progressao`?), nao um bug deste extrator.

