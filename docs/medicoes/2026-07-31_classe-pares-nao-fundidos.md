# Item 110 -- Classe de defeito: pares AoN/Foundry nao fundidos

Medicao pura, sem conserto. Pergunta que decide: **8 pares ou 80?**

## Metodo e criterio de similaridade

Base: `pipeline/base/index.json` (19.606 registros). Varredura: agrupar por
`kind`, separar registros com `prov.name == "aon"` de `prov.name == "foundry"`
e comparar nome entre os dois grupos do mesmo `kind`. Cinco testes de
similaridade, cada um isolado para saber qual pegou o que:

1. **distancia de edicao pequena** (Levenshtein <= 2 e <= 15% do tamanho da
   string normalizada) -- pega troca/omissao de 1-2 letras.
2. **razao de sequencia solta** (`difflib.SequenceMatcher >= 0.85`) -- pega
   erro de 3 letras trocadas em bloco que a distancia de edicao estrita perde
   (`Automatic` x `Autonomic`: 3 substituicoes na mesma regiao).
3. **plural** -- despluraliza e compara.
4. **artigo** (`the`/`of`/`a`) -- remove e compara.
5. **espaco/hifen** -- remove e compara (`Flash Forge` x `Flashforge`).
6. **letra dobrada** -- colapsa repeticao e compara (`Vermillion` x
   `Vermilion`).
7. **sufixo `Dedication`** -- caso estreito, só `kind=feat`: nome A == nome B
   sem o sufixo. Motivo de existir: `Knight Vigilant` (aon) x `Knight Vigilant
   Dedication` (foundry) nao cai em nenhum dos cinco criterios acima (a
   diferenca e uma palavra inteira), mas e o par mais citado no item 84.
   Verificado que NAO e um padrao geral: so 1 dos 2 feats `foundry` terminados
   em "Dedication" tem homonimo aon sem o sufixo -- nao virou fonte de ruido.

**Filtro obrigatorio, sem o qual o criterio 2 explode**: se um nome e PREFIXO
do outro (`Bloodline` / `Bloodline: Fey`, `Greater Field Discovery` /
`... (Bomber)`), o par e descartado antes mesmo de virar candidato -- esse e o
padrao de nomeacao de sub-escolha/variante do proprio catalogo (subclass,
grau de item), nao divergencia de grafia da MESMA entidade. Exceto o caso 7
(dedication), que e a excecao documentada.

**Sinal de confianca decisivo, seguindo a instrucao da tarefa**: com
`prov.name` divergente e nome parecido, exigi tambem `source.book` E `level`
identicos nos dois lados antes de contar como par real. Isso separa direto os
falsos positivos por homonimo (ver abaixo) sem precisar ler prosa par a par
para a maioria dos casos -- e onde sobrou ambiguidade (familia
`wand-of-*-rank`), o match final foi por chave exata (nome-base + nivel +
livro), nao por similaridade solta, porque a similaridade solta sozinha
gerava falso match entre wands de nomes parecidos e ranks diferentes.

## Gabarito: os 8 pares do item 84

A varredura tinha que reencontrar os 8. Resultado: **7 de 8** caem neste
criterio (aon x foundry, mesmo livro, mesmo nivel, nome parecido). O 8o --
`deepest-wellspring` x `amp-focus` -- **nao e desse mecanismo**: os dois
lados tem `prov.name = aon` (nao aon/foundry), o vinculo e um `remaster_id`
explicito do AoN entre legado e remaster, e quem veta a fusao e
`fundir_renomeados.py`, nao a auscencia de casamento por nome. E o ALVO
SEPARADO da tarefa, medido em secao propria abaixo.

| par (item 84) | reencontrado aqui? |
|---|---|
| `armor-regiment-training` x `armored-regiment-training` | sim |
| `knight-vigilant` x `knight-vigilant-dedication` | sim (criterio 7) |
| `flash-forge` x `flashforge` | sim (criterio 5) |
| `voice-of-elements` x `voice-of-the-elements-kineticist` | sim |
| `automatic-psychic-action` x `autonomic-psychic-action` | sim (criterio 2) |
| `vermilion-threads` x `vermillion-threads` | sim (criterio 6) |
| `whisper-of-warning` x `whispers-of-warning` | sim |
| `deepest-wellspring` x `amp-focus` | **nao** -- outro mecanismo, ver secao da guarda |

## Tabela completa -- pares CONFIRMADOS (grafia divergente aon/foundry)

Veredito: todo par abaixo tem `source.book` e `level` IDENTICOS nos dois
lados, nenhum tem `equivale_a`/`aliases` ligando os dois, e o nome diverge por
um dos sete criterios. Sao a MESMA entidade, sem vinculo na base.

### `feat` (27 pares) e `background` (2 pares)

| aon | foundry | nivel | livro | grants (a/b) | traits divergem? | veredito |
|---|---|---|---|---|---|---|
| `armor-regiment-training` | `armored-regiment-training` | 1 | Battlecry! | 0/0 | nao | CONFIRMADO |
| `automatic-psychic-action` | `autonomic-psychic-action` | 20 | Dark Archives (Remastered) | 0/1 | nao | CONFIRMADO -- grants partido |
| `camoflage-coat` | `camouflage-coat` | 13 | Howl of the Wild | 0/0 | nao | CONFIRMADO |
| `ceremony-of-the-strengthened-hand` | `ceremony-of-strengthened-hand` | 9 | The Mwangi Expanse | 0/0 | nao | CONFIRMADO |
| `certain-strategem` | `certain-stratagem` | 2 | Player Core 2 | 0/0 | nao | CONFIRMADO |
| `decree-of-banisment` | `decree-of-banishment` | 14 | War of Immortals | 0/0 | sim (1 trait a mais no lado aon) | CONFIRMADO |
| `deepvision` | `deep-vision` | 1 | Ancestry Guide | 0/0 | nao | CONFIRMADO |
| `embolded-with-glorious-purpose` | `emboldened-with-glorious-purpose` | 18 | Divine Mysteries | 0/0 | nao | CONFIRMADO |
| `exemplar-resilency` | `exemplar-resiliency` | 4 | War of Immortals | 0/1 | nao | CONFIRMADO -- grants partido |
| `fautless-defense` | `faultless-defense` | 14 | War of Immortals | 0/1 | nao | CONFIRMADO -- grants partido |
| `flash-forge` | `flashforge` | 1 | Rage of Elements | 0/0 | nao | CONFIRMADO |
| `flash-of-omipotence` | `flash-of-omnipotence` | 20 | Divine Mysteries | 0/0 | nao | CONFIRMADO |
| `fracture-time-flow` | `fracture-timeflow` | 18 | PF Adv. Path #219 | 0/0 | nao | CONFIRMADO |
| `heatwave` | `heat-wave` | 5 | Ancestry Guide | 0/0 | nao | CONFIRMADO |
| `judgment-of-the-monolith` | `judgement-of-the-monolith` | 12 | World Guide | 0/0 | nao | CONFIRMADO |
| `knight-vigilant` | `knight-vigilant-dedication` | 6 | Character Guide | 1/1 | nao | CONFIRMADO |
| `lurching-chomp` | `luring-chomp` | 13 | Draconic Codex | 0/0 | nao | CONFIRMADO |
| `master-summoner-spellcasting` | `master-summoning-spellcasting` | 18 | Secrets of Magic | 0/0 | nao | CONFIRMADO |
| `orators-fillibuster` | `orators-filibuster` | 8 | Battlecry! | 0/0 | nao | CONFIRMADO |
| `pass-vengeful-judgement` | `pass-vengeful-judgment` | 18 | War of Immortals | 0/0 | nao | CONFIRMADO |
| `remember-thy-names` | `remember-their-names` | 16 | War of Immortals | 0/0 | nao | CONFIRMADO |
| `repulse-the-wicken` | `repulse-the-wicked` | 6 | Knights of Lastwall | 0/0 | nao | CONFIRMADO |
| `vengful-remnant` | `vengeful-remnant` | 14 | Shining Kingdoms | 0/0 | nao | CONFIRMADO |
| `vermilion-threads` | `vermillion-threads` | 10 | Tian Xia Character Guide | 0/0 | nao | CONFIRMADO |
| `vindicators-judgement` | `vindicators-judgment` | 10 | War of Immortals | 0/0 | nao | CONFIRMADO |
| `whisper-of-warning` | `whispers-of-warning` | 12 | War of Immortals | 0/0 | nao | CONFIRMADO |
| `voice-of-the-elements-kineticist` | `voice-of-elements` | 2 | Rage of Elements | **0/7** | nao | CONFIRMADO -- **conteudo PARTIDO** (item 84) |
| `reclaimed-investigator` (background) | `reclaimer-investigator` (background) | -- | Knights of Lastwall | 2/4 | nao | CONFIRMADO -- grants partido |
| `historical-reeanactor` (background) | `historical-reenactor` (background) | -- | Sky King's Tomb PG | 0/3 | nao | CONFIRMADO -- grants partido |

**Homonimo descartado desta lista, nao par**: `wb:feat/voice-of-the-elements`
(Draconic Codex, nivel 5, pre-requisito Primal Dragonblood) tem o MESMO nome
de `voice-of-elements`/`voice-of-the-elements-kineticist`, mas e outro feat --
bloodline draconica, nao Kineticist. Confirmado no texto do dump AoN: dois
docs "Voice of the Elements" completamente diferentes. Livro e nivel
diferentes (Draconic Codex/5 x Rage of Elements/2) descartam o par
automaticamente pelo criterio de confianca. Exatamente o padrao "colisao de
identidade" ja documentado no `README.md`/`LESSONS.md` (`Death from Above`).

### `equipment` -- pares unicos (15)

| aon | foundry | nivel | livro | veredito |
|---|---|---|---|---|
| `cipher-of-the-elemental-planes` | `cipher-of-elemental-planes` | 16 | Rage of Elements | CONFIRMADO |
| `comandants-scabbard` | `commandants-scabbard` | 17 | Battlecry! | CONFIRMADO -- grants 0/1 |
| `eyes-of-the-moonwarden` | `eye-of-the-moonwarden` | 9 | PF #208 | CONFIRMADO |
| `feather-of-the-unfounded-bravado` | `feather-of-unfounded-bravado` | 2 | Battlecry! | CONFIRMADO |
| `fingerprinting-kit` | `fingerprint-kit` | 3 | PF #157 | CONFIRMADO |
| `fulus-of-concealment` | `fulu-of-concealment` | 6 | Secrets of Magic | CONFIRMADO |
| `green-gut` | `greengut` | 17 | PF #155 | CONFIRMADO |
| `ladder-10-ft` | `ladder-10-foot` | 0 | Player Core | CONFIRMADO |
| `mythic-resilent` | `mythic-resilient` | 20 | War of Immortals | CONFIRMADO |
| `nap-gas-disperser` | `nap-gas-dispenser` | 7 | PF #215 | CONFIRMADO |
| `sack-of-hyrdras-teeth` | `sack-of-hydras-teeth` | 12 | Battlecry! | CONFIRMADO |
| `submersible-helm-greater` | `submersible-helmet-greater` | 13 | Treasure Vault (Remastered) | CONFIRMADO -- grants 0/1 |
| `treats-standard` | `treat-standard` | 0 | Travel Guide | CONFIRMADO |
| `treats-unique` | `treat-unique` | 0 | Travel Guide | CONFIRMADO |
| `world-forge` | `worldforge` | 25 | War of Immortals | CONFIRMADO |

### `equipment` -- familia "Wand of X (Nth-Rank)" (58 pares)

Achado que NAO estava no item 84: uma familia inteira de varinhas de gasto
unico (Treasure Vault Remastered) onde o AoN nomeia o rank
`(Nth-Rank Spell)` e o Foundry nomeia `(Nth-rank)`. Verificado no dump AoN
que cada rank e um item de PRECO E NIVEL proprios (nao e generico) -- texto
identico entre os dois docs do mesmo rank, so a fonte do nome muda. Match por
chave exata (nome-base + nivel + livro), 100% de acerto: 58 registros `aon`
com esse padrao, 58 registros `foundry`, 58 casaram 1:1.

9 varinhas-base, 58 ranks-instancia: Chromatic Burst, Clinging Rime, Dazzling
Rays, Dumbfounding Doom, Hawthorn, Hybrid Form, Legerdemain, Mental
Purification, Mercy.

| aon | foundry | nivel |
|---|---|---|
| `wand-of-chromatic-burst-4th-rank-spell` | `wand-of-chromatic-burst-4th-rank` | 10 |
| `wand-of-chromatic-burst-7th-rank-spell` | `wand-of-chromatic-burst-7th-rank` | 16 |
| `wand-of-clinging-rime-7th-rank-spell` | `wand-of-clinging-rime-7th-rank` | 16 |
| `wand-of-clinging-rime-8th-rank-spell` | `wand-of-clinging-rime-8th-rank` | 18 |
| `wand-of-clinging-rime-9th-rank-spell` | `wand-of-clinging-rime-9th-rank` | 20 |
| `wand-of-dazzling-rays-3rd-rank-spell` | `wand-of-dazzling-rays-3rd-rank` | 8 |
| `wand-of-dazzling-rays-4th-rank-spell` | `wand-of-dazzling-rays-4th-rank` | 10 |
| `wand-of-dazzling-rays-5th-rank-spell` | `wand-of-dazzling-rays-5th-rank` | 12 |
| `wand-of-dazzling-rays-6th-rank-spell` | `wand-of-dazzling-rays-6th-rank` | 14 |
| `wand-of-dazzling-rays-7th-rank-spell` | `wand-of-dazzling-rays-7th-rank` | 16 |
| `wand-of-dazzling-rays-8th-rank-spell` | `wand-of-dazzling-rays-8th-rank` | 18 |
| `wand-of-dazzling-rays-9th-rank-spell` | `wand-of-dazzling-rays-9th-rank` | 20 |
| `wand-of-dumbfounding-doom-3rd-rank-spell` | `wand-of-dumbfounding-doom-3rd-rank` | 8 |
| `wand-of-dumbfounding-doom-4th-rank-spell` | `wand-of-dumbfounding-doom-4th-rank` | 10 |
| `wand-of-dumbfounding-doom-5th-rank-spell` | `wand-of-dumbfounding-doom-5th-rank` | 12 |
| `wand-of-dumbfounding-doom-6th-rank-spell` | `wand-of-dumbfounding-doom-6th-rank` | 14 |
| `wand-of-dumbfounding-doom-7th-rank-spell` | `wand-of-dumbfounding-doom-7th-rank` | 16 |
| `wand-of-dumbfounding-doom-8th-rank-spell` | `wand-of-dumbfounding-doom-8th-rank` | 18 |
| `wand-of-dumbfounding-doom-9th-rank-spell` | `wand-of-dumbfounding-doom-9th-rank` | 20 |
| `wand-of-hawthorn-2nd-rank-spell` | `wand-of-hawthorn-2nd-rank` | 6 |
| `wand-of-hawthorn-4th-rank-spell` | `wand-of-hawthorn-4th-rank` | 10 |
| `wand-of-hawthorn-6th-rank-spell` | `wand-of-hawthorn-6th-rank` | 14 |
| `wand-of-hawthorn-8th-rank-spell` | `wand-of-hawthorn-8th-rank` | 18 |
| `wand-of-hybrid-form-2nd-rank-spell` | `wand-of-hybrid-form-2nd-rank` | 6 |
| `wand-of-hybrid-form-3rd-rank-spell` | `wand-of-hybrid-form-3rd-rank` | 8 |
| `wand-of-hybrid-form-4th-rank-spell` | `wand-of-hybrid-form-4th-rank` | 10 |
| `wand-of-hybrid-form-5th-rank-spell` | `wand-of-hybrid-form-5th-rank` | 12 |
| `wand-of-hybrid-form-6th-rank-spell` | `wand-of-hybrid-form-6th-rank` | 14 |
| `wand-of-hybrid-form-7th-rank-spell` | `wand-of-hybrid-form-7th-rank` | 16 |
| `wand-of-hybrid-form-8th-rank-spell` | `wand-of-hybrid-form-8th-rank` | 18 |
| `wand-of-hybrid-form-9th-rank-spell` | `wand-of-hybrid-form-9th-rank` | 20 |
| `wand-of-legerdemain-1st-rank-spell` | `wand-of-legerdemain-1st-rank` | 4 |
| `wand-of-legerdemain-2nd-rank-spell` | `wand-of-legerdemain-2nd-rank` | 6 |
| `wand-of-legerdemain-3rd-rank-spell` | `wand-of-legerdemain-3rd-rank` | 8 |
| `wand-of-legerdemain-4th-rank-spell` | `wand-of-legerdemain-4th-rank` | 10 |
| `wand-of-legerdemain-5th-rank-spell` | `wand-of-legerdemain-5th-rank` | 12 |
| `wand-of-legerdemain-6th-rank-spell` | `wand-of-legerdemain-6th-rank` | 14 |
| `wand-of-legerdemain-7th-rank-spell` | `wand-of-legerdemain-7th-rank` | 16 |
| `wand-of-legerdemain-8th-rank-spell` | `wand-of-legerdemain-8th-rank` | 18 |
| `wand-of-legerdemain-9th-rank-spell` | `wand-of-legerdemain-9th-rank` | 20 |
| `wand-of-mental-purification-1st-rank-spell` | `wand-of-mental-purification-1st-rank` | 4 |
| `wand-of-mental-purification-2nd-rank-spell` | `wand-of-mental-purification-2nd-rank` | 6 |
| `wand-of-mental-purification-3rd-rank-spell` | `wand-of-mental-purification-3rd-rank` | 8 |
| `wand-of-mental-purification-4th-rank-spell` | `wand-of-mental-purification-4th-rank` | 10 |
| `wand-of-mental-purification-5th-rank-spell` | `wand-of-mental-purification-5th-rank` | 12 |
| `wand-of-mental-purification-6th-rank-spell` | `wand-of-mental-purification-6th-rank` | 14 |
| `wand-of-mental-purification-7th-rank-spell` | `wand-of-mental-purification-7th-rank` | 16 |
| `wand-of-mental-purification-8th-rank-spell` | `wand-of-mental-purification-8th-rank` | 18 |
| `wand-of-mental-purification-9th-rank-spell` | `wand-of-mental-purification-9th-rank` | 20 |
| `wand-of-mercy-1st-rank-spell` | `wand-of-mercy-1st-rank` | 4 |
| `wand-of-mercy-2nd-rank-spell` | `wand-of-mercy-2nd-rank` | 6 |
| `wand-of-mercy-3rd-rank-spell` | `wand-of-mercy-3rd-rank` | 8 |
| `wand-of-mercy-4th-rank-spell` | `wand-of-mercy-4th-rank` | 10 |
| `wand-of-mercy-5th-rank-spell` | `wand-of-mercy-5th-rank` | 12 |
| `wand-of-mercy-6th-rank-spell` | `wand-of-mercy-6th-rank` | 14 |
| `wand-of-mercy-7th-rank-spell` | `wand-of-mercy-7th-rank` | 16 |
| `wand-of-mercy-8th-rank-spell` | `wand-of-mercy-8th-rank` | 18 |
| `wand-of-mercy-9th-rank-spell` | `wand-of-mercy-9th-rank` | 20 |

Todos 58: veredito CONFIRMADO, `grants` 0/0 dos dois lados (item, nao feat --
nao ha o que "conceder"), nenhum `equivale_a`/`aliases` ligando os pares.

## Falsos positivos descartados

Candidatos que a varredura por similaridade solta encontrou e que **NAO**
sao a mesma entidade dividida -- sao diferenca de MODELAGEM (cardinalidade),
nao de grafia. Confirmado lendo o texto no dump do AoN (`equipment.json`):

| familia aon (generica) | familia foundry (especifica) | motivo |
|---|---|---|
| `Potion of Resistance (Grade)` -- 3 registros | `Potion of {Acid,Cold,Fire,Sonic} Resistance (Grade)` -- 12 | texto AoN: "grants resistance against a single damage type **of your choice**" -- 1 doc generico no AoN, Foundry precisa de 1 item concreto por elemento pra jogar |
| `Potion of Retaliation (Grade)` -- 5 | `Potion of {Acid,Cold,Fire} Retaliation (Grade)` -- 15 | mesmo padrao: "available in four varieties" |
| `Energy Breath Potion (Grade)` -- 3 | `Energy Breath Potion ({Acid,Cold,Fire,Sonic}, Grade)` -- 12 | mesmo padrao |
| `Elemental Ammunition (Grade)` -- 3 | `Elemental Ammunition (Grade, {Acid,Cold,Fire,Poison})` -- 12 | texto AoN: "acid, cold, electricity, fire, or poison" num doc so |

**~54 candidatos descartados** por esta familia (a similaridade solta
gerava ate 4 linhas por item generico, uma por elemento). Fundir qualquer um
desses pares apagaria a granularidade que o Foundry modela corretamente --
nao e o defeito do item 110.

Tambem descartado: cruzamentos falsos DENTRO da propria familia
`wand-of-*-rank` (ex.: `wand-of-dazzling-rays-4th-rank-spell` casando por
similaridade solta com `wand-of-dumbfounding-doom-5th-rank`, so porque os
dois compartilham o sufixo `"(Nth-rank)"`). Resolvido descartando o match
solto e usando chave exata nome-base+nivel+livro (secao acima).

## Placar

| veredito | contagem |
|---|---|
| **CONFIRMADO** | **102** (27 feat + 2 background + 15 equipment-outros + 58 equipment-wand-rank) |
| PROVAVEL | 0 |
| FALSO POSITIVO | ~55 (1 homonimo `voice-of-the-elements`/`voice-of-the-elements` de bloodline + ~54 da familia generico-vs-especifico) |

Nenhum dos 102 tem `equivale_a` ou `aliases` ligando os dois lados entre si.

## Impacto na ficha

De 102 pares confirmados:

- **8 divergem em `grants`** (7,8%) -- conteudo PARTIDO, o jogador recebe
  coisas diferentes dependendo de qual dos dois lados escolhe:
  - `voice-of-the-elements-kineticist` (0) x `voice-of-elements` (7) -- o
    pior caso, ja citado no item 84.
  - `historical-reeanactor` (0) x `historical-reenactor` (3) -- background,
    3 concessoes inteiras faltando de um lado.
  - `reclaimed-investigator` (2) x `reclaimer-investigator` (4)
  - `automatic-psychic-action` (0) x `autonomic-psychic-action` (1)
  - `exemplar-resilency` (0) x `exemplar-resiliency` (1)
  - `fautless-defense` (0) x `faultless-defense` (1)
  - `comandants-scabbard` (0) x `commandants-scabbard` (1)
  - `submersible-helm-greater` (0) x `submersible-helmet-greater` (1)
- **0 divergem em `level`** -- por construcao do filtro (exigido igual para
  contar como par de alta confianca).
- **6 divergem em `traits`** (5,9%) -- divergencia pequena (1 trait a mais em
  um lado, ex. `decree-of-banisment` com `auditory` extra), nao categorica;
  nao muda a classificacao do par.

## A guarda de `fundir_renomeados.py` -- fusoes corretas vetadas

`CAMPOS_VETO = ("level", "price_cp", "damage", "kind")` (linha 50): qualquer
divergencia nesses campos entre um par que o AoN liga por
`remaster_id`/`legacy_id` **veta a fusao inteira**, incondicionalmente --
mesmo quando o vinculo da fonte e explicito e 1:1.

Reexecutei os passos 1-3 do script (candidatos -> resolvidos -> veto) sem a
etapa de escrita, direto contra a base atual:

- pares declarados pelo AoN (`remaster_id`/`legacy_id`): 384
- vetados por divergencia estrutural: 384 (100% -- a base atual ja passou
  por uma rodada de `fundir_renomeados.py`, entao so sobram os que falharam)
- desses, **63 sao `kind` != `kind`** (ex. `class-feature` linkado a
  `class` -- nao sao a mesma entidade por construcao, veto correto)
- **271 tem SO `level` divergente** -- candidatos a investigar

Dos 271, a maioria (249) e o MESMO alvo remaster recebendo VARIOS legados
diferentes (`aeon-stone` sozinho absorveria 5; `magic-wand` genérico
absorveria 9 ranks; `darkwood`/`mithral` viram `duskwood`/`dawnsilver` em 4
grades cada) -- isso e template generico N:1, fundir qualquer um desses
apagaria granularidade de rank/grade, **o veto e CORRETO** aqui tambem
(mesmo padrao dos falsos positivos de equipment acima).

**Os 22 restantes tem fan-in = 1** -- um legado, um remaster, vinculo unico e
explicito do AoN, e MESMO ASSIM vetados so por `level` ter mudado entre
edicoes (o remaster mudou o nivel de varios feats de proposito). **Estas SAO
fusoes corretas sendo vetadas hoje:**

| legado (nivel) | remaster (nivel) | livro |
|---|---|---|
| `hellknight-signifer` (6) | `hellknight` (2) | Character Guide / Hellfire Dispatches |
| `red-herring` (2) | `eliminate-red-herrings` (1) | Advanced Player's Guide / Player Core 2 |
| `predictive-purchase-investigator` (6) | `predictive-purchase` (8) | idem |
| `implausible-purchase-investigator` (16) | `implausible-purchase` (18) | idem |
| `vision-of-weakness` (4) | `whispers-of-weakness` (1) | idem |
| `guardians-deflection-swashbuckler` (4) | `guardians-deflection` (6) | idem |
| `hex-wellspring` (18) | `hex-focus` (12) | Advanced Player's Guide / Player Core |
| `wardens-wellspring` (18) | `wardens-focus` (12) | idem |
| `domain-wellspring` (18) | `domain-focus` (12) | Core Rulebook / Player Core |
| `primal-wellspring` (18) | `primal-focus` (12) | idem |
| **`deepest-wellspring` (18)** | **`amp-focus` (12)** | Dark Archive / Dark Archives (Remastered) -- **caso do item 84/110** |
| `safeguarded-spell` (8) | `safeguard-spell` (6) | Advanced Player's Guide / Player Core 2 |
| `improved-familiar-familiar-master` (6) | `improved-familiar` (4) | idem |
| `elven-weapon-elegance` (5) | `elven-weapon-familiarity` (1) | Core Rulebook / Player Core |
| `hatchling-flight` (13) | `winglet-flight` (9) | Ancestry Guide / Player Core 2 |
| `green-empathy` (6) | `plant-empathy` (1) | Core Rulebook / Player Core |
| `gnome-weapon-innovator` (5) | `gnome-weapon-familiarity` (1) | idem |
| `goblin-weapon-frenzy` (5) | `goblin-weapon-familiarity` (1) | idem |
| `wild-empathy` (2) | `animal-empathy-druid` (1) | idem |
| `halfling-weapon-trickster` (5) | `halfling-weapon-familiarity` (1) | idem |
| `dwarven-weapon-cunning` (5) | `dwarven-weapon-familiarity` (1) | idem |
| `orc-weapon-carnage` (5) | `orc-weapon-familiarity` (1) | idem |

**22 fusoes corretas vetadas hoje**, todas pelo mesmo motivo: o remaster
mudou o `level` do feat (reducao de pre-requisito e comum em feats de
ancestria/arma e nos "wellspring -> focus"), e a guarda trata QUALQUER
divergencia de `level` como prova de identidades distintas -- sem excecao
para quando o vinculo `remaster_id` e explicito, unico (fan-in=1) e a fonte.
Nota lateral: 5 desses 22 (a familia `*-wellspring`/`*-focus`) ja tem
`aliases` parcialmente povoado no lado remaster (nome legado salvo como
alias), mas o registro legado continua vivo como entidade separada -- alguma
etapa marcou o nome sem completar a fusao.

## O que isto implica para o conserto

**Nao e curadoria. E passo de fusao novo.** A pergunta era "8 pares ou 80?" --
a resposta e **102 confirmados so na classe "grafia divergente aon/foundry"**,
mais **22 fusoes corretas vetadas** por um mecanismo diferente (guarda de
`fundir_renomeados.py`), 124 no total. Curar 124 pares a mao repete o mesmo
erro que o item 84 ja apontou no item 85 (2 pares) -- so que agora numa
escala 15x maior.

Dois consertos distintos, dois pontos de entrada:

1. **Casamento por nome tolerante a ruido** para o par aon/foundry: normalizar
   (espaco/hifen, artigo, plural, letra dobrada) antes de comparar, com
   distancia de edicao pequena como rede de seguranca, sempre exigindo
   `source.book` e `level` iguais como guarda de seguranca contra homonimo
   (o caso `voice-of-the-elements` prova que o guarda e necessario). A
   familia `wand-of-*-rank` sozinha (58) justifica um passo dedicado: chave
   exata nome-base+rank+livro, não fuzzy geral.
2. **Guarda de `fundir_renomeados.py` (`CAMPOS_VETO`) precisa de excecao**:
   quando o vinculo `remaster_id`/`legacy_id` e 1:1 (fan-in = 1, sem
   ambiguidade de sucessor multiplo), divergencia de `level` sozinha nao
   deveria vetar -- deveria fundir adotando o nivel do remaster (mais
   recente), do jeito que a adocao de sucessor ja faz quando so o legado
   entrou na base (linhas 181-239 do proprio arquivo). Regra atual so
   protege contra `kind` e template N:1 (`price_cp`/`damage` continuam bons
   veto para esses).
