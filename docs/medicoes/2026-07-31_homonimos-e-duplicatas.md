# Itens 100 e 102 -- Homonimos, Arquetipo Vazio e Divindade Duplicada

> **VERIFICADO E CORRIGIDO EM 2026-07-31.** Este relatorio saiu de uma medicao
> automatizada e DUAS das quatro conclusoes nao sobreviveram a conferencia.
> As tabelas abaixo ficam como estao, para rastreabilidade; o que vale e esta
> correcao.
>
> | medicao | relatado | verificado |
> |---|---|---|
> | 1. homonimo classe x arquetipo | 40 ocorrencias | **12** (3 em `requires`, 9 em `grants`), 11 registros de origem |
> | 2. `archetype` vazio | 73 | **73 -- confere** |
> | 3. arquetipo sem porta | 18 | **18 -- confere** |
> | 4. referencias a `wb:deity/maat-ln` | 0, "seguro fundir" | **2**, e NAO e seguro |
>
> **Medicao 1 -- por que 40 estava inflado.** O filtro contou todo `wb:feat/X`
> que tem `wb:class-feature/X` de mesmo nome, sem checar se o feat citado e
> mesmo de ARQUETIPO. Os dois maiores blocos nao sao: `wb:feat/shield-block`
> tem trait `general` (12 citacoes) e `wb:feat/reactive-strike` tem trait de
> classe (5). Existir feat e class-feature de mesmo nome ai e RAW correto --
> Shield Block e feat geral que qualquer um compra E feature que o Guerreiro
> ganha de graca.
>
> E mesmo esses o motor **ja resolve**: um Guerreiro 2 que tem
> `wb:class-feature/shield-block` responde `True` a `{"has":
> "wb:feat/shield-block"}`, porque `_termo_has` compara pelo id canonico depois
> de resolver alias. Testado.
>
> O defeito real do item 100 sao as **12** em que o alvo e de fato feat de
> arquetipo: `quick-alchemy` (6), `advanced-alchemy` (2), `champions-reaction`
> (2), `keen-recollection` (1), `surprise-attack` (1).
>
> **Medicao 4 -- por que "seguro fundir" e falso.** `wb:deity/maat-ln` E
> referenciado, por `wb:class/champion` e `wb:class/cleric`: ele esta no eixo
> `deity` das duas classes. Fundir sem tratar essas duas listas quebra o eixo.
> Era exatamente o risco que a medicao devia ter achado.

Medicoes reproduziveis e dados brutos para o TODO.md.

## Resumo executivo

| medicao | achados | gravidade |
|---|---|---|
| 1. Homonimo classe x arquetipo | 40 registros (21 em requires, 19 em grants) | média |
| 2. Arquetipo vazio (campo ausente) | 73 feats; 49 ancoravel auto, 24 nao | baixa |
| 3. Arquetipo sem porta de entrada | 18 arquetipos; nenhum tem dedicacao de nome similar | baixa |
| 4. Divindade duplicada (Maat) | 1 par (maat/maat-ln); nenhuma referencia ao legacy | baixa |

---

## MEDICAO 1 -- Homonimo classe x arquetipo

**Problema**: registros cujo `requires` ou `grants` aponta para um `wb:feat/<x>` que
e feat de ARQUETIPO, embora exista um `wb:class-feature/<x>` de MESMO NOME na base.
O alvo certo seria a class-feature.

### Ocorrencias em `requires`

**Total: 21**

| origem | aponta para (feat) | deveria apontar para (class-feature) |
|---|---|---|
| wb:feat/aegis-of-arnisant | wb:feat/shield-block | wb:class-feature/shield-block |
| wb:feat/bastion-dedication | wb:feat/shield-block | wb:class-feature/shield-block |
| wb:feat/channeling-block | wb:feat/shield-block | wb:class-feature/shield-block |
| wb:feat/crack-retort | wb:feat/reactive-strike | wb:class-feature/reactive-strike |
| wb:feat/disorienting-opening | wb:feat/reactive-strike | wb:class-feature/reactive-strike |
| wb:feat/efficient-alchemy | wb:feat/advanced-alchemy | wb:class-feature/advanced-alchemy |
| wb:feat/fortify-shield | wb:feat/shield-block | wb:class-feature/shield-block |
| wb:feat/immediate-rebuke | wb:feat/reactive-strike | wb:class-feature/reactive-strike |
| wb:feat/impassable-wall-stance | wb:feat/reactive-strike | wb:class-feature/reactive-strike |
| wb:feat/lastwall-sentry-dedication | wb:feat/shield-block | wb:class-feature/shield-block |
| wb:feat/lunging-stance | wb:feat/reactive-strike | wb:class-feature/reactive-strike |
| wb:feat/potent-poisoner | wb:feat/powerful-alchemy | wb:class-feature/powerful-alchemy |
| wb:feat/quick-shield-block | wb:feat/shield-block | wb:class-feature/shield-block |
| wb:feat/repositioning-block | wb:feat/shield-block | wb:class-feature/shield-block |
| wb:feat/shield-of-reckoning | wb:feat/champions-reaction | wb:class-feature/champions-reaction |
| wb:feat/shield-warden | wb:feat/shield-block | wb:class-feature/shield-block |
| wb:feat/swift-retribution | wb:feat/champions-reaction | wb:class-feature/champions-reaction |
| wb:feat/tunnel-wall | wb:feat/shield-block | wb:class-feature/shield-block |
| wb:feat/vigils-walls-rise-anew | wb:feat/shield-block | wb:class-feature/shield-block |
| wb:archetype/bastion | wb:feat/shield-block | wb:class-feature/shield-block |
| wb:archetype/lastwall-sentry | wb:feat/shield-block | wb:class-feature/shield-block |

### Ocorrencias em `grants`

**Total: 19**

| origem | aponta para (feat) | deveria apontar para (class-feature) |
|---|---|---|
| wb:class-feature/alchemy | wb:feat/quick-alchemy | wb:class-feature/quick-alchemy |
| wb:class-feature/alchemy | wb:feat/advanced-alchemy | wb:class-feature/advanced-alchemy |
| wb:class-feature/first-doctrine-warpriest | wb:feat/shield-block | wb:class-feature/shield-block |
| wb:class-feature/initiate-benefit-shield | wb:feat/shield-block | wb:class-feature/shield-block |
| wb:class-feature/moderate-creed | wb:feat/reactive-strike | wb:class-feature/reactive-strike |
| wb:class-feature/quick-alchemy | wb:feat/quick-alchemy | wb:class-feature/quick-alchemy |
| wb:class-feature/reactive-strike | wb:feat/reactive-strike | wb:class-feature/reactive-strike |
| wb:class-feature/shield-block | wb:feat/shield-block | wb:class-feature/shield-block |
| wb:class-feature/sparkling-targe | wb:feat/shield-block | wb:class-feature/shield-block |
| wb:class-feature/war-magic | wb:feat/shield-block | wb:class-feature/shield-block |
| wb:feat/alchemist-dedication | wb:feat/quick-alchemy | wb:class-feature/quick-alchemy |
| wb:feat/firework-technician-dedication | wb:feat/quick-alchemy | wb:class-feature/quick-alchemy |
| wb:feat/keen-recollection | wb:feat/keen-recollection | wb:class-feature/keen-recollection |
| wb:feat/munitions-machinist | wb:feat/quick-alchemy | wb:class-feature/quick-alchemy |
| wb:feat/reactive-striker | wb:feat/reactive-strike | wb:class-feature/reactive-strike |
| wb:feat/rogue-dedication | wb:feat/surprise-attack | wb:class-feature/surprise-attack |
| wb:feat/viking-shieldbearer | wb:feat/shield-block | wb:class-feature/shield-block |
| wb:feat/viking-weapon-familiarity | wb:feat/shield-block | wb:class-feature/shield-block |
| wb:feat/wandering-chef-dedication | wb:feat/quick-alchemy | wb:class-feature/quick-alchemy |

### Classificacao de origem

**Em `requires` (21)**:
- Feats de classe (defeito claro): 8 (shield-block/reactive-strike pattern)
- Feat de arquetipo: 13
- Arquetipos: 2

**Em `grants` (19)**:
- Class-features: 10
- Feats de classe/arquetipo/dedicacao: 9

O padrao emerge: **shield-block** (12 ocorrencias em requires, 8 em grants),
**reactive-strike** (6 em requires, 3 em grants), **quick-alchemy** (2 em grants),
**advanced-alchemy** (1 em requires, 1 em grants), **champions-reaction** (2 em requires).

---

## MEDICAO 2 -- Atribuicao de arquetipo vazia

**Problema**: feats com trait `archetype` no campo traits, mas campo `archetype`
ausente ou vazio. Eles nao podem ser filtrados por arquetipo.

**Total: 73 feats**

### Que podem ser re-ancorados automaticamente (49)

Todos citam uma dedicacao no `requires`, cujo campo `archetype` e conhecido.

| feat | via dedicacao | arquetipo |
|---|---|---|
| wb:feat/advanced-bow-training | wb:feat/archer-dedication | wb:archetype/archer |
| wb:feat/breath-of-the-dragon | wb:feat/dragon-disciple-dedication | wb:archetype/dragon-disciple |
| wb:feat/costume-change | wb:feat/celebrity-dedication | wb:archetype/celebrity |
| wb:feat/current-spell | wb:feat/elementalist-dedication | wb:archetype/elementalist |
| wb:feat/cutting-flattery | wb:feat/dandy-dedication | wb:archetype/dandy |
| wb:feat/elemental-familiar-elementalist | wb:feat/elementalist-dedication | wb:archetype/elementalist |
| wb:feat/empathetic-envoy | wb:feat/twilight-speaker-dedication | wb:archetype/twilight-speaker |
| wb:feat/evasiveness | wb:feat/rogue-dedication | wb:archetype/rogue |
| wb:feat/evasiveness-rogue | wb:feat/rogue-dedication | wb:archetype/rogue |
| wb:feat/exemplar-resilency | wb:feat/exemplar-dedication | wb:archetype/exemplar |
| wb:feat/expert-alchemy | wb:feat/alchemist-dedication | wb:archetype/alchemist |
| wb:feat/expert-herbalism | wb:feat/herbalist-dedication | wb:archetype/herbalist |
| wb:feat/expert-poisoner | wb:feat/poisoner-dedication | wb:archetype/poisoner |
| wb:feat/festering-wound | wb:feat/zombie-dedication | wb:archetype/zombie |
| wb:feat/fight-choreography | wb:feat/gladiator-dedication | wb:archetype/gladiator |
| wb:feat/fit-for-the-role | wb:feat/dandy-dedication | wb:archetype/dandy |
| wb:feat/flash-of-omipotence | wb:feat/mortal-herald-dedication | wb:archetype/mortal-herald |
| wb:feat/fused-polearm | wb:feat/runelord-dedication | wb:archetype/runelord |
| wb:feat/ghostly-grasp-ghost | wb:feat/ghost-dedication | wb:archetype/ghost |
| wb:feat/golem-dynamo | wb:feat/sterling-dynamo-dedication | wb:archetype/sterling-dynamo |
| wb:feat/high-quality-scrounger | wb:feat/scrounger-dedication | wb:archetype/scrounger |
| wb:feat/improved-familiar | wb:feat/familiar-master-dedication | wb:archetype/familiar-master |
| wb:feat/innate-magic-intuition | wb:feat/scrollmaster-dedication | wb:archetype/scrollmaster |
| wb:feat/its-not-over | wb:feat/celebrity-dedication | wb:archetype/celebrity |
| wb:feat/mighty-bulwark | wb:feat/sentinel-dedication | wb:archetype/sentinel |
| wb:feat/more-real-than-real | wb:feat/celebrity-dedication | wb:archetype/celebrity |
| wb:feat/operatic-adventurer | wb:feat/celebrity-dedication | wb:archetype/celebrity |
| wb:feat/oppurtune-trickster | wb:feat/hellbreaker-dedication | wb:archetype/hellbreaker |
| wb:feat/orators-fillibuster | wb:feat/field-propagandist-dedication | wb:archetype/field-propagandist |
| wb:feat/perfect-pitch | wb:feat/celebrity-dedication | wb:archetype/celebrity |
| wb:feat/polearm-tricks | wb:feat/runelord-dedication | wb:archetype/runelord |
| wb:feat/quick-alchemy | wb:feat/alchemist-dedication | wb:archetype/alchemist |
| wb:feat/rallying-charge | wb:feat/knight-vigilant-dedication | wb:archetype/knight-vigilant |
| wb:feat/recycled-cogwheel | wb:feat/trapsmith-dedication | wb:archetype/trapsmith |
| wb:feat/repulse-the-wicken | wb:feat/lastwall-sentry-dedication | wb:archetype/lastwall-sentry |
| wb:feat/school-counterspell | wb:feat/runelord-dedication | wb:archetype/runelord |
| wb:feat/shield-salvation | wb:feat/bastion-dedication | wb:archetype/bastion |
| wb:feat/silence-the-profane-avenger | wb:feat/avenger-dedication | wb:archetype/avenger |
| wb:feat/silence-the-profane-vindicator | wb:feat/vindicator-dedication | wb:archetype/vindicator |
| wb:feat/skill-mastery | wb:feat/investigator-dedication | wb:archetype/investigator |
| wb:feat/skill-mastery-rogue | wb:feat/rogue-dedication | wb:archetype/rogue |
| wb:feat/snap-out-of-it | wb:feat/marshal-dedication | wb:archetype/marshal |
| wb:feat/stalwart-standard | wb:feat/knight-vigilant-dedication | wb:archetype/knight-vigilant |
| wb:feat/startling-appearance | wb:feat/vigilante-dedication | wb:archetype/vigilante |
| wb:feat/tempo-shift | wb:feat/celebrity-dedication | wb:archetype/celebrity |
| wb:feat/tragic-lament | wb:feat/celebrity-dedication | wb:archetype/celebrity |
| wb:feat/vindicators-judgement | wb:feat/vindicator-dedication | wb:archetype/vindicator |
| wb:feat/warding-rune | wb:feat/runescarred-dedication | wb:archetype/runescarred |
| wb:feat/watch-this | wb:feat/pirate-dedication | wb:archetype/pirate |

### Que NAO podem ser re-ancorados automaticamente (24)

Nenhum campo `archetype` e visivel pela cadeia de `requires`.

| feat | motivo |
|---|---|
| wb:feat/advanced-red-mantis-magic | requires: outro feat sem archetype |
| wb:feat/bear-hug-ursine-avenger | requires: vazio |
| wb:feat/diverse-armor-expert | requires: vazio |
| wb:feat/embolded-with-glorious-purpose | requires: feat sem archetype |
| wb:feat/harsh-judgment | requires: vazio |
| wb:feat/judgment-of-the-monolith | requires: feat sem archetype |
| wb:feat/knight-vigilant | requires: vazio |
| wb:feat/lotus-above-the-mud | requires: feat sem archetype |
| wb:feat/master-alchemy | requires: feat sem archetype |
| wb:feat/master-summoner-spellcasting | requires: vazio |
| wb:feat/phalanx-formation-knight-vigilant | requires: feat sem archetype |
| wb:feat/shattering-strike | requires: feat sem archetype |
| wb:feat/specialized-companion | requires: feat sem archetype |
| wb:feat/speedy-rituals | requires: feat sem archetype |
| wb:feat/vengful-remnant | requires: vazio |
| wb:feat/viking-weapon-specialist | requires: feat sem archetype |
| wb:feat/dual-weapon-reload-archetype | requires: vazio |
| wb:feat/daywalker-archetype | requires: vazio |
| wb:feat/draconic-scent-archetype | requires: vazio |
| wb:feat/know-it-all-archetype | requires: vazio |
| wb:feat/many-guises-archetype | requires: vazio |
| wb:feat/rallying-charge-visual | requires: vazio |
| wb:feat/riptide-archetype | requires: vazio |
| wb:feat/watch-your-back-archetype | requires: vazio |

---

## MEDICAO 3 -- Arquetipo sem porta de entrada

**Problema**: arquetipos (`kind: archetype`) que nao tem nenhum feat com trait
`dedication` apontando para eles via campo `archetype`.

**Total: 18 de 243**

Nenhum deles tem um feat de dedicacao com nome similar (teste: procurar por
nome normalizado "{Nome Arquetipo} Dedication").

| arquetipo |
|---|
| wb:archetype/apocalypse-rider |
| wb:archetype/archfiend |
| wb:archetype/ascended-celestial |
| wb:archetype/avenging-runelord |
| wb:archetype/beast-lord |
| wb:archetype/broken-chain |
| wb:archetype/eternal-legend |
| wb:archetype/gelid-shard |
| wb:archetype/godling |
| wb:archetype/gray-gardener |
| wb:archetype/hellknight-signifer |
| wb:archetype/heroic-scion |
| wb:archetype/prophesied-monarch |
| wb:archetype/splinter-of-finality |
| wb:archetype/timewracked |
| wb:archetype/ursine-avenger-hood |
| wb:archetype/warshard-warrior |
| wb:archetype/wildspell |

---

## MEDICAO 4 -- Duplicata de divindade (Maat)

**Problema**: existem dois registros para a mesma divindade, um remaster e um
legacy. O eixo `deity` do Campeao oferece os dois.

### (a) Confirmacao de unicidade

| criterio | resultado |
|---|---|
| Total divindades na base | 488 |
| Nomes de divindade que repetem | 1 (maat/ma'at, case-insensitive) |
| Divindades com sufixo -ln em id (alignment legacy) | **1** (wb:deity/maat-ln) |

**Sim, e o unico caso.**

### (b) Comparacao de campos

Os dois registros diferem em **quase tudo**. O remaster (wb:deity/maat) tem conteudo
completo; o legacy (wb:deity/maat-ln) tem apenas stub.

| campo | wb:deity/maat (remaster) | wb:deity/maat-ln (legacy) |
|---|---|---|
| alignment | LN | (vazio) |
| anathema | Deal unfairly... | (vazio) |
| area_of_concern | Justice, law, order, truth | (vazio) |
| cleric_spell | 3 spells | (vazio) |
| divine_attribute | int, wis | (vazio) |
| divine_font | heal | (vazio) |
| domains | 4 primary | (vazio) |
| edict | Defend civilization... | (vazio) |
| epithet | The Feather of Truth | (vazio) |
| favored_weapon | starknife | (vazio) |
| follower_alignment | LG, LN, N | (vazio) |
| sanctification | holy | (vazio) |
| source | Divine Mysteries, remaster | Gods & Magic, legacy |
| xref.aon | deity-518 | deity-55 |
| traits | [] | [ln] |
| desmembrado_de | (nenhum) | wb:deity/maat |

### (c) Referencias na base inteira

**Total de referencias a wb:deity/maat-ln em requires/grants: 0**

Seguro fundir: nenhum registro depende do legacy.

### (d) Por que escapou de fundir_renomeados.py?

**Causa 1: A ponte AoN esta invertida**

- `fundir_renomeados.py` olha `remaster_id` no doc legado e `legacy_id` no remaster.
- O registro legado (deity-55, Gods & Magic) nao virou maat-ln por nenhuma
  medicao anterior -- virou porque ele **nao se funde com nada no Foundry** e o
  extrator o salvou como-e, com o livro vindo do AoN legado.
- O registro remaster (deity-518, Divine Mysteries) entrou como wb:deity/maat.
- `remaster_id` e `legacy_id` do AoN precisarao ser verificados; se nao
  apontarem um pro outro, a fusao nao dispara. O script exige a chave para
  confiar, e sem ela caiu para prosa, que nao cobre divindades (texto muito
  generico).

**Causa 2: O sufixo -ln e criado depois da fusao**

`derivar_alias_legado.py` roda apos `fundir_renomeados.py`. Se a fusao
tivesse casado os dois, o resultado teria absorvido o legado. Como nao casou,
ficaram dois registros, e o legado ganhou sufixo -ln **apos o fato**.

---

## Parecer

**Medicao 1 (homonimos)**: 40 ocorrencias mensuraveis, pattern claro (shield-block,
reactive-strike), defeito derivado de ambiguidade nome-feat x class-feature.
Ajeitar via ID fixo na base.

**Medicao 2 (arquetipo vazio)**: 73 total, 49 automovel, 24 sem porta visivel.
A ancoracao automatica e segura -- todos os 49 citam uma dedicacao com archetype
conhecido. Os 24 precisam de curadoria.

**Medicao 3 (arquetipo sem porta)**: 18 arquetipos de verdade sem dedicacao.
Achado lateral do item 46; ja estava no relatorio de 2026-07-30. Nao tem
dedica com nome similar.

**Medicao 4 (maat)**: Par unico de divindade duplicada, legacy virou -ln,
remaster nao. Zero referencias ao legacy, seguro fundir e apontar alias.
Causa: a ponte AoN entre os dois precisaria de verificacao (ver
`remaster_id`/`legacy_id`); sem confirmacao dessa ponte, `fundir_renomeados.py`
nao toca.
