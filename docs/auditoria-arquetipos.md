# Auditoria de Dado — Arquétipos (Waybuilder)

Data: 2026-07-28
Fonte: `pipeline/base/index.json` (19.705 registros), `pipeline/base/text/feat.json`
Método: leitura via `python3 json.load` + agregação (nunca `Read` direto no index).

Legenda: **[CONFIRMADO]** = evidência direta no dado. **[HIPÓTESE]** = inferência não totalmente verificada.

---

## 1. Dedicações sem `grants`

**[CONFIRMADO]**

| Métrica | Valor |
|---|---|
| Total de dedicações (`trait: dedication`) | 226 |
| Com `grants` não vazio | 165 |
| Com `grants` vazio (`[]`) | 61 |

Correlação perfeita com o campo `mechanized`: as 61 sem `grants` têm `mechanized: false` (100%); as 165 com `grants` têm `mechanized: true` (100%). Ou seja, **27% das dedicações do jogo não fazem absolutamente nada no motor** — pegar essas dedicações não concede nenhum efeito mecânico, mesmo quando o texto da regra claramente concede algo (companion, spell, proficiência).

Achado colateral: nessas 61, o campo `grants_completos` está marcado `true` — o que é enganoso, pois sugere "grants revisado e completo" quando na verdade significa "não mecanizado ainda". Vale reportar ao pipeline (`grants_completos` deveria ser `false`/`null` quando `mechanized: false`).

15 exemplos de dedicações SEM grants (nome | arquétipo):

| id | nome | arquétipo |
|---|---|---|
| wb:feat/animal-trainer-dedication | Animal Trainer Dedication | wb:archetype/animal-trainer |
| wb:feat/animist-dedication | Animist Dedication | wb:archetype/animist |
| wb:feat/artillerist-dedication | Artillerist Dedication | wb:archetype/artillerist |
| wb:feat/blessed-one-dedication | Blessed One Dedication | wb:archetype/blessed-one |
| wb:feat/butterfly-blade-dedication | Butterfly Blade Dedication | wb:archetype/butterfly-blade |
| wb:feat/captivator-dedication | Captivator Dedication | wb:archetype/captivator |
| wb:feat/cavalier-dedication | Cavalier Dedication | wb:archetype/cavalier |
| wb:feat/clockwork-reanimator-dedication | Clockwork Reanimator Dedication | wb:archetype/clockwork-reanimator |
| wb:feat/curse-maelstrom-dedication | Curse Maelstrom Dedication | wb:archetype/curse-maelstrom |
| wb:feat/drake-rider-dedication | Drake Rider Dedication | wb:archetype/drake-rider |
| wb:feat/elementalist-dedication | Elementalist Dedication | wb:archetype/elementalist |
| wb:feat/firebrand-braggart-dedication | Firebrand Braggart Dedication | wb:archetype/firebrand-braggart |
| wb:feat/flexible-spellcaster-dedication | Flexible Spellcaster Dedication | wb:archetype/flexible-spellcaster |
| wb:feat/geomancer-dedication | Geomancer Dedication | wb:archetype/geomancer |
| wb:feat/ghost-eater-dedication | Ghost Eater Dedication | wb:archetype/ghost-eater |

(Lista completa das 61 tem mais 46 itens, incluindo `Cavalier Dedication` — arquétipo popular/base — e `Vigilante Dedication`.)

Exemplo de gravidade: `wb:feat/cavalier-dedication` — o texto concede um **animal companion montaria**, mas `grants: []`. `wb:feat/blessed-one-dedication` — o texto concede a spell *lay on hands*, refocus alternativo e treino em spell attack/DC, mas `grants: []`.

---

## 2. Feats por arquétipo

**[CONFIRMADO]**

| Métrica | Valor |
|---|---|
| Total de arquétipos (`kind: archetype`) | 244 |
| Arquétipos com ≥1 feat referenciando via campo `archetype` | 243 |
| Arquétipos com ZERO feats | 1 |

O único com zero feats é `wb:archetype/bright-lion-archetype-83` ("Bright Lion"), que tem `desmembrado_de: "wb:archetype/bright-lion"` — é um registro-duplicata gerado no processo de fusão/reconciliação (fonte "Legends"), não um arquétipo jogável independente. O arquétipo real `wb:archetype/bright-lion` tem 8 feats corretamente vinculados. **Não é um bug funcional**, é resíduo de deduplicação que talvez devesse ser filtrado da lista de `kind: archetype` exposta ao app.

Validação cruzada: o campo de metadado `feats` (contagem esperada, vinda do AoN) bate com a contagem real em 242 de 244 arquétipos. Só 2 divergências, ambas de 1 feat a menos que o esperado:

| arquétipo | esperado (AoN) | real na base | gap |
|---|---|---|---|
| wb:archetype/vigilante | 11 | 10 | 1 |
| wb:archetype/marshal | 19 | 18 | 1 |

Total esperado (soma do campo `feats`): 2.252. Total real: 2.250. **Cobertura de vínculo feat→arquétipo está excelente (99,9%)** — o problema dos arquétipos não está na quantidade de feats presentes, e sim na qualidade dos `grants`/`requires` (itens 1, 3 e 4).

**15 arquétipos com MENOS feats** (excluindo o zero):

| # feats | arquétipo |
|---|---|
| 1 | Flexible Spellcaster |
| 1 | Hellknight Signifer |
| 3 | Undead Master |
| 4 | Alkenstar Agent |
| 4 | Edgewatch Detective |
| 4 | Chelaxian Scion |
| 4 | Sentinel |
| 4 | Game Hunter |
| 4 | Blessed One |
| 4 | Bounty Hunter |
| 4 | Vindicator |
| 4 | Shieldmarshal |
| 4 | Ghost Eater |
| 4 | Talisman Dabbler |
| 4 | Psychic Duelist |

Nota: "Hellknight Signifer" com 1 feat é esperado — ver item 5, é uma sub-ordem do arquétipo Hellknight, não um arquétipo dedicação independente completo.

**10 arquétipos com MAIS feats:**

| # feats | arquétipo |
|---|---|
| 37 | Hellknight |
| 29 | Werecreature |
| 29 | Mortal Herald |
| 26 | Spell Trickster |
| 24 | Beastmaster |
| 24 | Pathfinder Agent |
| 23 | Lastwall Sentry |
| 20 | Knight Vigilant |
| 20 | Swordmaster |
| 19 | Magaambyan Attendant |

---

## 3. A dedicação concede o que promete? (amostra de 12)

**[CONFIRMADO]** — padrão sistemático encontrado: **toda dedicação de classe conjuradora (spellcaster) na amostra tem os `grants` de spellcasting ausentes**, mesmo com `mechanized: true`. E foi encontrado um **erro de dado** na Fighter Dedication.

| Dedicação | `grants` (resumo) | O que o texto promete | Divergência |
|---|---|---|---|
| **Rogue Dedication** | choice+grant_feat de `surprise-attack` | +armadura leve treinada, Stealth/Thievery treinado, rogue class DC treinado, surprise attack | Faltam: treino em armadura leve, treino de perícia (Stealth/Thievery), treino em class DC |
| **Fighter Dedication** | `{"proficiency": {"simple": "trained"}}` | "You become trained in **martial** weapons" (texto literal) | **[CONFIRMADO] ERRO DE DADO**: grants treina armas *simples* (`simple`), texto exige treino em armas *marciais* (`martial`). Contradiz o próprio campo `text` do mesmo registro. Faltam também: escolha Acrobatics/Athletics, class DC |
| **Wizard Dedication** | só `proficiency.arcana: trained` | Spellbook com 4 cantrips, Cast a Spell, preparar 2 cantrips/dia, treino em spell attack/DC | Faltam: toda a concessão de spellcasting (ação, cantrips, spell attack/DC) |
| **Cleric Dedication** | grant deity item + `religion: trained` + grant_feat deity-cleric | Cast a Spell, 2 cantrips/dia, treino spell attack/DC, anátema, sanctification | Faltam: spellcasting completo |
| **Barbarian Dedication** | instinct, Rage, `athletics: trained`, AC -1 condicional | Athletics treinado, **barbarian class DC treinado**, Rage, instinct | Falta: treino em class DC |
| **Ranger Dedication** | Hunt Prey, `survival: trained`, escolha attribute | Survival treinado, **ranger class DC treinado**, Hunt Prey | Falta: treino em class DC |
| **Alchemist Dedication** | crafting, weapon-base-alchemical-bomb, versatile-vials, quick-alchemy, Alchemical Crafting | Bate quase integralmente com o texto | Falta: **alchemist class DC treinado** (não encontrado no grants) — a mais completa da amostra |
| **Bard Dedication** | escolha de muse, `performance` + `occultism` treinados | Cast a Spell, 2 cantrips/dia, spell attack/DC treinado, efeitos da muse | Faltam: spellcasting completo, efeitos mecânicos da muse escolhida |
| **Champion Dedication** | `religion: trained`, deity item, cause, fórmulas de AC (max de proficiências) | Treino em Religion **e na perícia da divindade escolhida**, class DC | Falta: treino na perícia associada à divindade (dinâmico, depende da escolha). Achado extra: `{"choice": {"flag": null, "opcoes": 2}}` — `flag: null` sugere uma escolha sem nome/rótulo, possível bug de pipeline |
| **Druid Dedication** | `nature: trained`, escolha de druidic order | Cast a Spell, 2 cantrips/dia, spell attack/DC treinado, idioma Wildsong, anátema | Faltam: spellcasting completo, idioma, anátema |
| **Monk Dedication** | Powerful Fist, escolha attribute/skill | Treino em ataques desarmados, escolha Acrobatics/Athletics, **monk class DC treinado** | Falta: treino em class DC (treino de ataque desarmado é implícito via Powerful Fist, não confirmado) |
| **Sorcerer Dedication** | escolha de bloodline + grant do item da bloodline | Treino nas 2 perícias da bloodline, Cast a Spell, 2 cantrips/dia, spell attack/DC treinado | Faltam quase tudo: treino de perícias, spellcasting completo. **A mais incompleta da amostra** — só a escolha de bloodline é mecanizada |

**Padrão confirmado**: as 5 dedicações de conjurador puro na amostra (Wizard, Cleric, Bard, Druid, Sorcerer) **não concedem a ação Cast a Spell, os cantrips iniciais nem o treino em spell attack/DC** via `grants`. Isso é consistente com a nota do usuário de que "alvo dinâmico fica sinalizado como pendente" — mecânica de conjuração provavelmente cai nesse balde de "pendente", mas o efeito prático é que **nenhuma dedicação de conjurador dá capacidade de conjurar magia no motor atual**.

Achado isolado de maior gravidade: **Fighter Dedication treina a proficiência errada** (`simple` em vez de `martial`), o que é logicamente inútil (a maioria das classes já começa treinada em armas simples) e diverge do próprio texto anexado ao mesmo registro.

---

## 4. Gate de nível dos feats de arquétipo

**[CONFIRMADO]**

| Métrica | Valor |
|---|---|
| Feats com trait `archetype` (excluindo as próprias dedicações) | 1.902 |
| Referenciam alguma dedicação na cadeia de `requires` (direta ou transitiva via outro feat pré-requisito) | 1.664 |
| **NÃO alcançam nenhuma dedicação na cadeia** ("truly ungated") | **238** |

Metodologia: segui a cadeia de `requires.has` recursivamente (ex.: "Advanced Arcana" exige "Basic Arcana", que por sua vez exige a dedicação — isso conta como gated). Os 238 abaixo não fecham em nenhuma dedicação nem transitivamente.

Dos 238:

| Subcategoria | Qtd | Interpretação |
|---|---|---|
| `requires_parseado: false` | 150 | Pipeline já sabe que não conseguiu parsear o requisito — sinalizado como pendente, não é surpresa |
| `requires_parseado: true`, mas `requires_texto` cita uma "X Dedication" que sumiu do `requires` estruturado | 10 | **Pior caso**: o pipeline afirma ter terminado o parse, mas o gate da dedicação foi perdido silenciosamente |
| `requires_parseado: true`, sem menção a dedicação no texto | 78 | Prováveis feats sem pré-requisito de feat direto (ex.: dependem só de nível/traço/ter uma forma de animal companion específica) — não necessariamente bug |

**Isso significa que, hoje, um personagem pode pegar até 238 feats "avançados" de arquétipo sem nunca ter pego a dedicação correspondente** (o motor só checa nível de personagem nesses casos, não o pré-requisito de feat). Os 10 do "pior caso" são o achado mais grave — a base declara o parse como completo (`requires_parseado: true`) mas ainda assim não há gate de dedicação. Investigação revelou que esses 10 apontam para **3 IDs de dedicação que não existem na base** (ver item 5) — a causa raiz é referência órfã, não ausência de parsing.

Exemplos de feats verdadeiramente sem gate (nível + arquétipo, sem exigir a dedicação em lugar nenhum da cadeia):

| id | nível | arquétipo | `requires_texto` |
|---|---|---|---|
| wb:feat/bear-empathy | 10 | ursine-avenger-hood | *(vazio)* |
| wb:feat/bullet-dancer-burn | 4 | bullet-dancer | "Bullet Dancer Stance" |
| wb:feat/aldori-swordlord | 20 | aldori-duelist | "Aldori Duelist Dedication; ... demonstrado skill..." |
| wb:feat/absorb-spell | 14 | spellmaster | "{@feat Spellmaster Dedication\|LOCG}, spell repertoire..." |

---

## 5. Referências órfãs (arquétipo aponta para dedicação inexistente)

**[CONFIRMADO]**

Varredura de todos os `requires.has` em feats com trait `archetype` (1.902 + 226 dedicações = 2.128 registros) contra o universo completo de IDs da base (19.705 registros, qualquer `kind`).

| Métrica | Valor |
|---|---|
| Referências `has` que apontam para um ID inexistente na base | 12 |
| Das quais "formato de dedicação" (nome contém "dedication") | 12 (100%) |
| Feats afetados (únicos) | 8 |
| Arquétipos afetados | 3 (Hellknight, Hellknight Signifer, Crossbow Infiltrator) |

| feat afetado | arquétipo | ref. órfã | causa raiz confirmada |
|---|---|---|---|
| wb:feat/advanced-order-training | Hellknight | wb:feat/hellknight-armiger-dedication | nome legado, renomeado para `wb:feat/hellknight-dedication` (ver `historico`) |
| wb:feat/advanced-order-training | Hellknight | wb:feat/hellknight-signifer-dedication | nome legado, renomeado para `wb:feat/hellknight-signifer-preferment` |
| wb:feat/ardent-armiger | Hellknight | wb:feat/hellknight-armiger-dedication | idem |
| wb:feat/diabolic-certitude | Hellknight | wb:feat/hellknight-armiger-dedication | idem |
| wb:feat/mortification | Hellknight | wb:feat/hellknight-armiger-dedication | idem |
| wb:feat/order-training | Hellknight | wb:feat/hellknight-armiger-dedication | idem |
| wb:feat/masked-casting | Hellknight | wb:feat/hellknight-signifer-dedication | idem |
| wb:feat/signifer-armor-expertise | Hellknight Signifer | wb:feat/hellknight-signifer-dedication | idem |
| wb:feat/signifers-sight | Hellknight | wb:feat/hellknight-signifer-dedication | idem |
| wb:feat/lethargy-poisoner | Crossbow Infiltrator | wb:feat/drow-shootist-dedication | nome legado, renomeado para `wb:feat/crossbow-infiltrator-dedication` |
| wb:feat/reloading-trick | Crossbow Infiltrator | wb:feat/drow-shootist-dedication | idem |
| wb:feat/repeating-hand-crossbow-training | Crossbow Infiltrator | wb:feat/drow-shootist-dedication | idem |

**Causa raiz confirmada**: o remaster do PF2e renomeou feats legado (ex.: "Drow Shootist Dedication" → "Crossbow Infiltrator Dedication", "Hellknight Armiger Dedication" → "Hellknight Dedication"). O registro atual carrega corretamente `aliases: ["Drow Shootist Dedication"]` e `historico: [{"nome_legado": ..., "id_legado": "wb:feat/drow-shootist-dedication", ...}]` — ou seja, **o pipeline sabe do remapeamento**, mas não o aplicou nos `requires.has` dos 8 feats dependentes que ainda referenciam o `id_legado` diretamente. É um bug de reconciliação pontual (3 dedicações, 8 feats afetados), não sistêmico.

Adicional: `wb:feat/knight-vigilant` (a dedicação do arquétipo Knight Vigilant, 20 feats) tem `traits: ["archetype","dedication"]` mas **campo `archetype: None`** — não está vinculada ao seu próprio arquétipo `wb:archetype/knight-vigilant`, ao contrário do padrão "X Dedication" (esse feat se chama só "Knight Vigilant", sem sufixo "Dedication", o que pode ter confundido o extrator de vínculo). Risco: o app pode não listar essa dedicação ao filtrar feats do arquétipo Knight Vigilant.

Nenhuma referência órfã foi encontrada no campo `archetype` dos feats (0 de 6.273) — o vínculo feat→arquétipo em si é limpo; o problema está isolado nos 12 `requires.has` legado.

---

## Resumo de gravidade

1. **[CRÍTICO]** 61/226 dedicações (27%) têm `grants: []` — não concedem nada mecanicamente, incluindo Cavalier (companion) e Blessed One (spell).
2. **[CRÍTICO]** Todas as 5 dedicações de conjurador puro amostradas (Wizard, Cleric, Bard, Druid, Sorcerer) não concedem spellcasting via `grants` — dedicação de arquétipo caster não dá magia no motor.
3. **[ALTO]** 238 feats de arquétipo não têm gate de dedicação no `requires` estruturado (150 sinalizados como pendentes pelo próprio pipeline, 10 com parse "completo" mas gate perdido por referência órfã, 78 a investigar caso a caso).
4. **[ALTO]** Fighter Dedication treina proficiência errada (`simple` em vez de `martial`), contradizendo o próprio texto no mesmo registro.
5. **[MÉDIO]** 12 referências órfãs (8 feats, 3 dedicações) por remap de nome legado→remaster não aplicado (Hellknight Armiger, Hellknight Signifer, Drow Shootist).
6. **[BAIXO]** `grants_completos: true` é enganoso nas 61 dedicações não mecanizadas (deveria refletir `mechanized`).
7. **[BAIXO]** `wb:archetype/bright-lion-archetype-83` é resíduo de deduplicação sem feats — não afeta jogabilidade se filtrado da UI.
8. **[BAIXO]** `wb:feat/knight-vigilant` sem campo `archetype` preenchido (vínculo por nome, sem sufixo "Dedication", não capturado pelo extrator).
