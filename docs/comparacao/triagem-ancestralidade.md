# Triagem — Ancestralidade, Heranca, Arquetipo, Divindade, Background

Metodo: leitura via `python3` (Bash) sobre `pipeline/base/index.json`, `pipeline/dados_brutos/aon_*.json` e
`pipeline/dados_brutos/foundry/packs/pf2e/**`. Nenhum arquivo de pipeline foi alterado; somente este documento
foi escrito.

## 1. Tabela-resumo

| Kind | Faltam em nos | Veredito | So nosso | Veredito |
|---|---|---|---|---|
| `ancestry` | 2 | F-RENAME (2) | 0 | — |
| `heritage` | 12 | F-RENAME (12) | 4 | B-SOBRA-NOVA (4) |
| `archetype` | 4 | F-RENAME (3) + A-FALTA-REAL (1) | 0 | — |
| `deity` | 3 | A-FALTA-REAL (3) | 6 | B-SOBRA-NOVA (5) + INDECISO (1) |
| `background` | 0 | — | 25 | B-SOBRA-NOVA (25) |

Nenhum item de `nivel_divergente` ou `raridade_divergente` foi reportado pelos comparadores desta frente.

O achado mais relevante nao aparece nessas tabelas: **causas do Campeao e patronos da Bruxa existem
na base, com texto completo, mas as classes `champion`/`witch` referenciam ids antigos que a fusao de
remaster ja aposentou.** Ver secao 3.

---

## 2. Ancestralidade (`ancestry`) — 2 faltando

Remaster renomeou as duas ancestrias inteiras. Confirmado em `pipeline/dados_brutos/aon_ancestries.json`
(traz as 4 formas: Gnoll, Grippli, Kholo, Tripkee) e em `pipeline/base/index.json`.

| AoN | Veredito | Nosso id | Evidencia |
|---|---|---|---|
| Gnoll | F-RENAME | `wb:ancestry/kholo` | Kholo existe na base; **falta** `aliases`/`historico` apontando pra "Gnoll" (o padrao usado em `cause` nao foi replicado aqui) |
| Grippli | F-RENAME | `wb:ancestry/tripkee` | Idem — Tripkee existe, sem alias/historico pro nome legado |

Acao: nenhuma extracao pendente. Sugestao cosmetica de baixa prioridade: preencher `aliases: ["Gnoll"]` /
`aliases: ["Grippli"]` nos dois registros de ancestria, seguindo o padrao ja usado em `cause` e na maioria
das heranças Kholo/Tripkee (ver secao 3, mesma classe de gap).

---

## 3. Heranca (`heritage`) — 12 faltando, 4 so nosso

### 12 "faltando" — todas F-RENAME, ja resolvidas na base

Todas sao heranças de Gnoll/Grippli/Kobold renomeadas para Kholo/Tripkee/Kobold(remaster), ou as
heranças humanas genericas "Skilled/Versatile" que ganharam nome proprio remasterizado.

| AoN (nome antigo) | Nosso id | Alias presente? |
|---|---|---|
| Ant Gnoll | `wb:heritage/ant-kholo` | sim (`Ant Gnoll`) |
| Great Gnoll | `wb:heritage/great-kholo` | sim |
| Sweetbreath Gnoll | `wb:heritage/sweetbreath-kholo` | sim |
| Witch Gnoll | `wb:heritage/witch-kholo` | sim |
| Poisonhide Grippli | `wb:heritage/poisonhide-tripkee` | sim |
| Snaptongue Grippli | `wb:heritage/snaptongue-tripkee` | sim |
| Stickytoe Grippli | `wb:heritage/stickytoe-tripkee` | sim |
| Windweb Grippli | `wb:heritage/windweb-tripkee` | sim |
| Cavern Kobold | `wb:heritage/cavernstalker-kobold` | sim (`Cavern Kobold`) |
| Spellscale Kobold | `wb:heritage/spellhorn-kobold` | sim (`Spellscale Kobold`) |
| Skilled Heritage | `wb:heritage/skilled-human` | sim (`Skilled Heritage`) |
| Versatile Heritage | `wb:heritage/versatile-human` | sim (`Versatile Heritage`) |

Todas com `ancestry` apontando pra `wb:ancestry/kholo` / `wb:ancestry/tripkee` / `wb:ancestry/kobold` /
`wb:ancestry/human` corretamente. O comparador provavelmente so compara por nome exato e nao consulta
`aliases`, por isso aparecem como "faltando" — nao ha gap real de dado.

Acao: nenhuma. Opcional: ensinar o script de comparacao a checar `aliases` antes de marcar como faltante
(evita falso positivo recorrente a cada rodada de comparacao).

### 4 "so nosso" — todas B-SOBRA-NOVA

| Nome | Fonte | Motivo provavel de ausencia no dump AoN |
|---|---|---|
| Ambitious Human | Pathfinder Beginner Box: Secrets of the Unlit Star | produto recente/nicho, dump AoN nao indexa ou foi capturado antes do lancamento |
| Battle-Trained Human (BB) | idem | idem |
| Warden Human (BB) | Pathfinder Beginner Box | idem, licenca OGL (nao-remaster) |
| Naari | Ancestry Guide (OGL, nao-remaster) | heranca "livre" com `ancestry: null` — nao vinculada a uma ancestria especifica; provavel que o dump AoN filtre heranças por pagina-de-ancestria e essa fique fora |

Todos os 4 tem `xref.foundry` valido (id de compendio real), i.e. sao dados legitimos extraidos do Foundry,
nao lixo de parser. Nao ha acao — sao superavit correto da nossa base sobre o dump de comparacao.

---

## 4. Arquetipo (`archetype`) — 4 faltando

| AoN | Veredito | Nosso id | Evidencia |
|---|---|---|---|
| Artillerst | F-RENAME (typo-fix) | `wb:archetype/artillerist` | O proprio AoN tem as duas formas: "Artillerst" (Guns & Gears, nao-remaster) e "Artillerist" (Guns & Gears Remastered) — erro de digitacao corrigido no remaster. Nossa base ja tem `Artillerist` com `aliases: ["Artillerst"]` |
| Firework Technican | F-RENAME (typo-fix) | `wb:archetype/firework-technician` | Mesmo padrao: AoN tem "Firework Technican" (nao-remaster, com erro) e "Firework Technician" (remaster). Nossa base tem a forma correta com alias |
| Hellknight Armiger | F-RENAME | `wb:archetype/hellknight` | AoN reestruturou: existe uma entrada nova unificada "Hellknight" (fonte *Hellfire Dispatches*, `archetype-372`) com `legacy_id: [archetype-25, archetype-20, archetype-26]` e `legacy_name: ["Hellknight Armiger", "Hellknight Signifer"]` — as 3 archetypes antigas (Armiger, Hellknight-por-ordem, Signifer) foram fundidas em uma so. Nossa base ja tem `wb:archetype/hellknight` com `aliases: ["Hellknight Armiger"]` e `historico` apontando pro id legado |
| Drow Shootist | **A-FALTA-REAL** | — | AoN tem a entrada completa (`archetype-90`, *Pathfinder #165: Eyes of Empty Death*, uncommon, Combat Style). Busquei em `pipeline/dados_brutos/foundry/packs/pf2e/feats/archetype/**` — **nao existe pasta nem feat de dedicacao pra esse arquetipo no dump Foundry**. So aparecem residuos soltos (`shootists-draw.json` em adventure-specific-actions, `shootists-edge.json` em class-features, `shootist-bandolier.json` em equipment, e um statblock de NPC em `abomination-vaults-bestiary/`) — nenhum e a feat de dedicacao do arquetipo em si |

**Nota lateral (fora do escopo, nao rastreado nas listas):** `wb:archetype/hellknight-signifer` continua
como entrada separada, nao fundida em `wb:archetype/hellknight`, apesar do AoN indicar que devia ter sido
absorvida junto (`legacy_name` inclui "Hellknight Signifer"). Nao esta em `faltam_em_nos`/`so_nosso`
desta frente, mas fica registrado pra quem for revisar arquetipos depois.

Acao: **Drow Shootist** precisa vir do AoN (scrape/markdown), pois o Foundry nao tem a feat de dedicacao no
dump local. Baixa prioridade — conteudo de AP, uncommon, nicho (crossbow de mao + drow).

---

## 5. Divindade (`deity`) — 3 faltando, 6 so nosso

### 3 faltando — A-FALTA-REAL

| AoN | Fonte | Evidencia |
|---|---|---|
| Dwarven Pantheon | — | Existe em `aon_deities.json`, ausente em `index.json` (kind `deity`, 488 entradas, nenhuma bate) |
| Elven Pantheon | — | Idem |
| The Prismatic Ray | — | Idem |

Sao paginas de "pantheon"/organizacao divina, nao uma divindade individual — pode ser que o extrator
Foundry/AoN atual do pipeline tenha excluido deliberadamente esse tipo de entrada (panteao != deidade
unica) em vez de nao ter encontrado. Recomendo checar se `kind: deity` no pipeline exige `domains`/`edicts`
individuais antes de aceitar, o que descartaria panteões por design. Se for esse o caso, o veredito correto
e "fora de escopo do kind" e nao um gap; nao consegui confirmar a regra de filtro sem ver o script de
extracao, entao fica **INDECISO quanto a causa**, mas o dado em si e **A-FALTA-REAL** (falta extrair, se
o pipeline decidir que panteões contam).

### 6 "so nosso"

| Nome | Fonte | Veredito | Evidencia |
|---|---|---|---|
| Alocer | Pathfinder One-Shot #2: Dinner at Lionlodge (OGL, nao-remaster) | B-SOBRA-NOVA | Ausente em `aon_deities.json` (717 entradas). `xref.foundry` valido — produto de nicho que o dump AoN nao cobre |
| Atheists and Free Agents | Divine Mysteries | B-SOBRA-NOVA | Ausente no dump AoN. `xref.foundry` valido |
| Norns | Divine Mysteries | B-SOBRA-NOVA | Idem |
| The Curtain Call | Curtain Call Player's Guide | B-SOBRA-NOVA | Idem |
| Lissala (The Order of Virtue) | Divine Mysteries | B-SOBRA-NOVA | AoN so tem "Lissala" pura; a variante de culto "(The Order of Virtue)" e conteudo do *Divine Mysteries* que o dump nao cobre |
| Chinostes | Pathfinder #216: The Acropolis Pyre | **INDECISO** (provavel duplicata) | AoN so tem `Chinostes (Nightwarden)` e `Chinostes (Redeemer)` — as duas variantes de alinhamento, que **ja existem** na nossa base (`wb:deity/chinostes-nightwarden`, `wb:deity/chinostes-redeemer`, ambas com `xref.aon`). Alem dessas duas, a base tem uma TERCEIRA entrada `wb:deity/chinostes` (so `xref.foundry`, sem `xref.aon`), com texto parecido mas nao identico ("In a Sylirican raid..." vs "Raised a saddle-maker..."). Parece o registro generico que o Foundry publica ao lado das duas variantes de alinhamento da AoN. Precisa de revisao manual pra decidir se e conteudo complementar legitimo ou duplicata a mesclar/remover — nao decidi sozinho por falta de contexto de intencao editorial |

---

## 6. Background (`background`) — 0 faltando, 25 so nosso

Todas as 25 sao B-SOBRA-NOVA. Confirmado uma a uma contra `pipeline/dados_brutos/aon_backgrounds.json`
(496 nomes) — nenhuma bate. Origem: quase todas vem de Player's Guides de Adventure Path/Society
(*Pathfinder Society Clockwork Mystery Player's Guide*, *Bastion of Blasphemies Player's Guide*, *Sky
King's Tomb Player's Guide*, *Agents of Edgewatch Player's Guide*, *Knights of Lastwall*, *Gatewalkers
Player's Guide*), produtos que o dump AoN aparentemente nao indexa (ou o crawl e anterior ao lancamento
deles). Uma vem do proprio *Player Core 2*: `Refugee (PC2)`, coexistindo com `Refugee (Fall of
Plaguestone)` — a base ja desambiguou corretamente dois backgrounds homonimos de fontes diferentes.

Acao: nenhuma. Superavit correto.

---

## 7. Achado central — causas do Campeao e patronos da Bruxa

**A premissa "nao existem na base" esta parcialmente incorreta: o dado existe, completo, para as 6 causas
e para os 8 patronos legados da Bruxa. O problema real e outro: a definicao de subclasse de `champion` e
`witch` referencia ids antigos que a propria fusao de remaster do pipeline ja aposentou — e o pipeline
ja tem, em `relatorio_fusao.md`, a tabela exata de qual id velho virou qual id novo.**

### 3.1 Causas do Campeao

`kind: cause` tem **7 entradas** em `index.json` (nao 0), todas com texto completo (edicts/anathema/fonte)
em `pipeline/base/text/cause.json`:

| Nome novo (canonico) | id | alias (nome legado) |
|---|---|---|
| Justice | `wb:cause/justice` | Paladin |
| Redemption | `wb:cause/redemption` | Redeemer |
| Liberation | `wb:cause/liberation` | Liberator |
| Obedience | `wb:cause/obedience` | Tyrant |
| Desecration | `wb:cause/desecration` | Desecrator |
| Iniquity | `wb:cause/iniquity` | Antipaladin |
| Grandeur | `wb:cause/grandeur` | (sem alias — nao tinha nome pre-remaster) |

Cada uma tambem tem `historico[].id_legado` apontando pro id antigo (ex.: `wb:cause/justice` <-
`wb:cause/paladin`). Ha ainda mecanica real em `kind: class-feature` (Champion's Reaction, `@UUID` do
Foundry) para as mesmas 7, em `pipeline/base/text/class-feature.json`.

**O bug:** `wb:class/champion.subclasses[].opcoes` (eixo `cause`) lista:
```
["wb:cause/antipaladin", "wb:cause/desecrator", "wb:cause/liberator",
 "wb:cause/paladin", "wb:cause/redeemer", "wb:cause/tyrant",
 "wb:class-feature/desecration", "wb:class-feature/grandeur", "wb:class-feature/iniquity",
 "wb:class-feature/justice", "wb:class-feature/liberation", "wb:class-feature/obedience",
 "wb:class-feature/redemption"]
```
Os 6 primeiros ids (`wb:cause/paladin`, `wb:cause/antipaladin`, etc.) **nao existem em `index.json`** —
confirmei buscando cada um: `NAO EXISTE NO INDEX`. Sao exatamente os ids que a fusao renomeou. O proprio
pipeline ja sabe disso: `relatorio_subclasses.md` reporta "Champion: `cause` (13 opcoes no nivel 1: 7 com
mecanica, **6 so catalogo**)" e `relatorio_fusao.md` documenta a tabela completa Paladin->Justice,
Redeemer->Redemption, Liberator->Liberation, Tyrant->Obedience, Desecrator->Desecration,
Antipaladin->Iniquity.

**Fix concreto:** em `wb:class/champion`, trocar os 6 ids legados na lista `opcoes` (e no array
`so_catalogo`) pelos ids canonicos (`wb:cause/paladin` -> `wb:cause/justice`, etc.), usando a mesma tabela
que ja existe em `relatorio_fusao.md`/`historico[].id_legado`. Nao precisa extrair nada — e reescrita de
referencia.

### 3.2 Patronos da Bruxa

`kind: patron` tem **17 entradas** em `index.json` (nao 0) — os patronos nomeados do remaster (Baba Yaga,
Faith's Flamekeeper, The Resentment, Silence in Snow, Spinner of Threads, Starless Shadow, Wilding
Steward, Devourer of Decay, Ripple in the Deep, Whisper of Wings, Cobyslarni, Choir Politic, Paradox of
Opposites, The Unseen Broker, Mosquito Witch + 1 duplicata `the-unseen-broker-patron-29`).

Os **8 patronos legados** (Curse, Fate, Fervor, Night, Pacts, Rune, Wild, Winter — temas genericos do
*Advanced Player's Guide* pg. 99, pre-remaster) **tem texto completo** em
`pipeline/base/text/patron.json` (27 chaves ao todo, incluindo esses 8), mas **nao tem entrada em
`kind: patron` no `index.json`**. Exemplo de conteudo ja extraido:

```
wb:text/patron/wild -> "Wild Source Advanced Player's Guide pg. 99 The wild places of the world feel
the touch of your patron. Spell List Primal Patron Skill Nature Hex Cantrip Wilding Word Granted Spell
your choice of summon animal or summon plant or fungus"
```

`relatorio_fusao.md` ja documenta o mapeamento 1:1 legado -> remaster (a fusao **rodou** pra causas mas
**nao criou catalogo** pros patronos legados):

| Legado (APG) | Remaster (ja existe como `kind: patron`) |
|---|---|
| Curse | The Resentment |
| Fate | Spinner of Threads |
| Fervor | Faith's Flamekeeper |
| Night | Starless Shadow |
| Pacts | The Unseen Broker |
| Rune | The Inscribed One |
| Wild | Wilding Steward |
| Winter | Silence in Snow |

**O bug (mesmo padrao do Champion):** `wb:class/witch.subclasses[].opcoes` (eixo `patron`) lista, junto
aos 16 ids `wb:class-feature/<nome-remaster>` (com mecanica), os 8 ids legados `wb:patron/curse`,
`wb:patron/fate`, `wb:patron/fervor`, `wb:patron/night`, `wb:patron/pacts`, `wb:patron/rune`,
`wb:patron/wild`, `wb:patron/winter` no bloco `so_catalogo` — e nenhum desses 8 ids tem entrada em
`index.json`. `relatorio_subclasses.md` confirma: "Witch: ... `patron` (24 opcoes no nivel 1: 16 com
mecanica, **8 so catalogo**)".

**Diferenca importante em relacao as causas:** para causas, a fusao criou a entrada canonica com
`aliases`/`historico` apontando pro legado — so a referencia em `champion.subclasses` ficou desatualizada.
Para patronos, a fusao **nao criou entrada de catalogo nenhuma** pros 8 legados (nem canonica nem
com alias) — o texto foi extraido mas o passo de materializar `kind: patron` pra eles nunca rodou.

**Fix concreto (2 partes):**
1. Criar as 8 entradas `kind: patron` legadas (`wb:patron/curse`, etc.) ou, preferencialmente, seguir o
   padrao das causas: seriam apenas *aliases* das 8 entradas remaster ja existentes (`wb:patron/the-resentment`
   ganha `aliases: ["Curse"]`, etc.), com `historico[].id_legado` apontando pra `wb:patron/curse`.
2. Trocar os 8 ids em `wb:class/witch.subclasses[].opcoes` (eixo `patron`) pelos ids canonicos
   correspondentes, usando a tabela acima (identica logica ao fix do Champion).

Se a escolha for nao manter os 8 ids legados como entidades proprias (so os aliases bastam), o passo 2
ainda e obrigatorio — hoje a witch aponta pra ids que nunca vao existir.

---

## 8. Acao recomendada para o pipeline (priorizada)

1. **[Alto impacto, baixo esforco] Corrigir referencias de subclasse de `champion` (`cause`) e `witch`
   (`patron`)** — trocar os 6 + 8 ids legados por ids canonicos em `subclasses[].opcoes`/`so_catalogo`,
   usando a tabela ja existente em `relatorio_fusao.md`. Isso sozinho faz `so_catalogo` cair de 6->0 no
   Champion e de 8->0 na Witch, sem extrair nada de novo.
2. **[Medio esforco] Materializar as 8 entradas `kind: patron` legadas** (Curse, Fate, Fervor, Night,
   Pacts, Rune, Wild, Winter) como aliases das remaster, espelhando o padrao ja usado em `cause`. Texto
   ja esta pronto em `pipeline/base/text/patron.json` — e so rodar o mesmo passo de materializacao que
   gerou os 7 `kind: cause`.
3. **[Baixo esforco] Extrair `Drow Shootist`** (`archetype`) via AoN — nao tem no dump Foundry local.
   Baixa prioridade (AP nicho).
4. **[Baixo esforco] Avaliar panteões (`Dwarven Pantheon`, `Elven Pantheon`, `The Prismatic Ray`)** — decidir
   se `kind: deity` deve aceitar entradas de panteao (sem `domains` individuais) e, se sim, extrair as 3.
5. **[Cosmetico] Preencher `aliases`/`historico` em `wb:ancestry/kholo` e `wb:ancestry/tripkee`** apontando
   pra "Gnoll"/"Grippli", igual ja e feito na maioria das heranças Kholo/Tripkee — evita falso-positivo
   recorrente no comparador.
6. **[Revisao manual] Resolver duplicata `wb:deity/chinostes`** vs `chinostes-nightwarden`/
   `chinostes-redeemer` — decidir se e conteudo complementar ou entrada a mesclar/remover.
7. **[Opcional, cosmetico] Ensinar o script de comparacao com AoN a checar o campo `aliases`** antes de
   marcar uma entrada como "faltando" — eliminaria os 12 falsos positivos de heranca e os 3 de arquetipo
   nesta rodada (e provavelmente casos parecidos nas outras frentes).
