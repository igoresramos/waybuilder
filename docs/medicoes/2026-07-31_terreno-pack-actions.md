# Terreno do pack `actionspf2e` -- embasamento para o item 111

Medicao READ-ONLY (sem `./build.sh`, sem editar base/pipeline/motor/TODO). Todo
comando roda contra `pipeline/dados_brutos/` como esta em disco hoje.

Achado zero, antes de tudo: o pack chama-se `actionspf2e` no `system.pf2e.json`
do Foundry (`name: "actionspf2e", path: "packs/actions"`), mas no disco vive em
`packs/pf2e/actions/`. E o mesmo pack, so com o path achatado pelo clone.

```
python3 -c "
import json
d=json.load(open('pipeline/dados_brutos/foundry_repo/system.pf2e.json'))
for p in d['packs']:
    if 'action' in p.get('path','').lower():
        print(p['name'], p['path'])
"
```

---

## 1. Tamanho e forma

**557 documentos**, todos `type: "action"`, em 19 subpastas por origem (nao por
nivel):

```
find pipeline/dados_brutos/foundry_repo/packs/pf2e/actions -name "*.json" | wc -l   # 558 (- _folders.json = 557)
```

| subpasta | docs | subpasta | docs |
|---|---:|---|---:|
| class | 187 | basic | 30 |
| archetype | 134 | ancestry | 42 |
| skill | 54 | background | 27 |
| subsystems | 19 | heritage | 7 |
| exploration | 13 | equipment | 7 |
| spells | 11 | vehicles | 5 |
| downtime | 4 | campaign | 5 |
| stamina | 4 | aftermath | 5 |
| naval-combat | 1 | mythic | 1 |
| familiar | 1 | | |

Campos (uniao, medido nos 557):

- `system.actionType.value`: `action` 334, `reaction` 102, `passive` 74, `free` 47.
- `system.category`: `offensive` 288, `interaction` 178, `defensive` 74, ausente 17.
- `system.publication` (source): presente em **557/557** (100%).
- `system.traits.value`: presente (nao-vazio) em 470/557; ausente em 87 (as
  acoes basicas tipo Interact costumam nao ter trait).
- **Nao ha campo de nivel** em nenhum doc (nem `level`, nem em `system`). O
  nivel de uma deed/reacao vem de QUEM concede, nao da acao em si -- confirmado
  tambem em `classes/*.json`: nenhuma classe lista item de `actionspf2e` na
  sua progressao (`system.items`), zero ocorrencias.

Subgrupos claros por conteudo, nao so por pasta: `basic/` e o vocabulario RAW
(Stride, Interact, Aid...); `class/` e `archetype/` sao os concessores de
build (deeds, impulsos, reacoes de subclasse, dedicacoes); `skill/`,
`exploration/`, `downtime/` sao acoes de sistema/procedimento, nao escolha de
personagem; `subsystems/`, `vehicles/`, `naval-combat/`, `campaign/` sao
minigame, fora do escopo do construtor pelos 4 principios do README.

## 2. Quantas sao de construcao de personagem

Criterio direto (nao chute): uma acao E de construcao quando algum item de
pack de construcao a concede via `GrantItem`/`ActiveEffectLike` -- e a mesma
prova que o item 5 abaixo usa contra o portao 9. Medido nos packs
`class-features`, `feats`, `classes`, `heritages`, `ancestries`,
`backgrounds`, `deities`:

- **353 referencias estaticas** (`GrantItem` com `Compendium.pf2e.actionspf2e.Item.X` literal)
- apontando para **317 acoes-alvo distintas** de **557** (56,9%)
- de **322 donos distintos** (class-feature/feat/heritage/etc.)

```
grep -c '"key": "GrantItem"' pipeline/dados_brutos/foundry_repo/packs/pf2e/{class-features,feats,heritages,ancestries,backgrounds}/**/*.json
# + filtro python por "actionspf2e" no uuid -- script usado, nao emitido em arquivo (medicao descartavel)
```

Por pack de origem da referencia:

| pack | refs |
|---|---:|
| feats | 180 |
| class-features | 112 |
| heritages | 30 |
| backgrounds | 28 |
| ancestries | 3 |
| classes / deities | 0 |

Alem disso, **44 dessas 353** carregam `predicate` no proprio `GrantItem`
(balde dos 293 que o item 107 corrigido ja aponta -- `Justice -> Retributive
Strike` e `Liberation -> Liberating Step` estao nesses 44, gate
`{"or": ["class:champion", "feat:champions-reaction"]}`).

O resto (240 dos 557, 43,1%) e o vocabulario RAW/procedimento: `basic/`
inteiro (Stride, Strike, Interact...), a maior parte de `skill/`,
`exploration/`, `downtime/`, `subsystems/`, `vehicles/`. **Corte proposto**:
uma acao entra na base como conteudo de construcao quando tem pelo menos um
`GrantItem`/`ActiveEffectLike` de um pack de construcao apontando pra ela
(317) OU quando ela e a acao-gatilho de uma classe/arquetipo sem concessor
formal mas citada por nome no `requires` de outra entrada (nao medido aqui,
provavelvemente pequeno -- ver secao "decisoes em aberto"). As 240 restantes
seguem o principio 4 ("nada e descartado") mas nao bloqueiam nada hoje: nenhum
item do TODO cita `Stride` como pre-requisito.

## 3. Quem as referencia (estatico + dinamico)

**353 estaticas** (secao 2) + **2 leitores dinamicos de escopo `actor`**
apontando para o mesmo pack:

```
feats  Practiced Reloads   -> {actor|flags.system.gunslinger.slingersReload}
feats  Slinger's Readiness -> {actor|flags.system.gunslinger.initialDeed}
```

Essas 2 flags sao escritas por 5 `ActiveEffectLike` (as 5 subclasses
"Way of X" do Gunslinger), **10 pares**, batendo exatamente com os "10 pares
Gunslinger" do spec `2026-07-31-grant-condicional.md`. Achado que a spec nao
tinha: **os 10 alvos JA tem, cada um, um `GrantItem` ESTATICO direto da
propria "Way of X"** (`Way of the Vanguard -> Clear a Path`, `Way of the
Vanguard -> Living Fortification`, etc. -- todos os 10 aparecem na lista da
secao 2). Ou seja: a via primaria (subclasse concede a propria deed) ja e
GrantItem estatico comum, sem precisar do mecanismo `se`/flag -- so
`Slinger's Readiness`/`Practiced Reloads` (2 feats que perguntam "qual e a
MINHA deed inicial", fora da propria Way) precisam do vocabulario condicional
da spec.

Confirma tambem o texto do item 111: **hoje, sem kind `action`, 9 das 10
deeds nao pousam em lugar nenhum** -- exceto `Into the Fray`, que **colide por
nome** com `feats/archetype/viking/into-the-fray.json` (um feat real do
arquetipo Viking). Quem resolve `GrantItem` por nome quando o pack de origem
nao e lido (o mesmo defeito do item 100/106, "por_nome prefere feat") acerta o
alvo ERRADO -- `Into the Fray` "funciona" hoje por acidente de homonimo, nao
porque a deed existe.

`Retributive Strike`/`Liberating Step` (Campeao): confirmado, `Justice` e
`Liberation` (ambos `class-features`) tem `GrantItem` **estatico** com
`predicate` -- bate com a correcao do item 107 (nao e UUID dinamico, e o balde
de `predicate`).

## 4. Cobertura pelas outras fontes

**AoN** (`pipeline/dados_brutos/aon_dump/action.json`): 3.979 documentos,
categoria `"category": "action"` uniforme, **974 nomes distintos**. Os 11
alvos (9 deeds + 2 reacoes) existem todos, tipicamente em par Legacy/Remaster
ligado por `remaster_id`/`legacy_id` (ex. `Ten Paces`: `action-3680` (Guns &
Gears) <-> `action-911` (Guns & Gears Remastered)). **Mas a categoria `action`
do AoN nao e a mesma populacao do pack Foundry**: os maiores contribuintes de
fonte sao `Treasure Vault`/`Treasure Vault (Remastered)`/`Grand Bazaar` (918
citacoes so esses tres) -- sao acoes de **ativar item magico**, que no Foundry
vivem embutidas na descricao do proprio equipamento, nao como doc separado em
`actionspf2e`. Contagem bruta do AoN nao serve de baseline 1:1 sem filtrar essa
categoria por fonte.

```
python3 -c "
import json,collections
d=json.load(open('pipeline/dados_brutos/aon_dump/action.json'))
print(len(d), len({x['name'] for x in d}))
print(collections.Counter(s for x in d for s in x.get('source',[])).most_common(10))
"
```

**Pf2eTools** (`pipeline/dados_brutos/pf2etools_repo/data/actions.json`):
chave unica `"action"`, **442 docs**, sem duplicacao Legacy/Remaster
aparente (schema mais raso, so o vigente). Os 11 alvos existem, 1 ocorrencia
cada, limpo.

Conclusao de cobertura: as 3 fontes tem os 11 alvos. Pf2eTools (442) e o mais
proximo em forma do Foundry (557) -- ambos "so acao de jogador", sem ruido de
item magico. **O extrator deve ler o Foundry como fonte primaria** (e a unica
com `license`/ORC e com o campo estruturado que alimenta `GrantItem` --
mesmo padrao ja adotado em `tactic`, que TAMBEM vive dentro deste pack), com
AoN/Pf2eTools so para prosa/traducao de nome como o resto da base ja faz.

## 5. `action` vira kind proprio ou entra como `class-feature`

**Precedente direto: `tactic`.** `taticas_kits.py` ja mostrou que uma FATIA do
proprio pack `actionspf2e` -- as 37 taticas do Commander, em
`actions/class/commander/*.json` -- virou kind `tactic` em vez de
`class-feature`, com o Foundry usado so para `license`/xref por nome (o
registro em si vem do dump AoN `aon_tactics.json`). O motivo documentado la:
"a spec nao tem vocabulario de `grants` para ativar efeito de banner/aura",
entao `tactic` ficou com campo proprio (`tactic.type/actions/frequency`) e
`grants_completos=False`.

**Portao 9 (censo do AoN por categoria)**: `action` esta hoje em
`FORA_DE_ESCOPO` (`pipeline/portoes.py`, junto com `creature`,
`creature-ability`, `npc`, `spell-effect`, `vehicle` etc.) -- decisao
deliberada de nao cobrar o censo desta categoria. Essa entrada foi tomada
quando "action" parecia ser so ruido de monstro/NPC/procedimento; a medicao
desta tarefa mostra que **317 delas sao referenciadas por packs de
construcao**, o que muda o calculo. Se `action` virar kind, `FORA_DE_ESCOPO`
precisa perder essa linha (ou o censo vai contar 974 nomes do AoN contra 0 na
base, disparando o portao com um alarme que ja tem resposta).

```
grep -n "FORA_DE_ESCOPO" -A 8 pipeline/portoes.py
```

**Argumento por kind proprio:**
- Acao tem forma propria que `class-feature` nao modela: `actionType`
  (action/reaction/free/passive), `category` (offensive/defensive/
  interaction), sem nivel embutido. Forcar em `class-feature` exigiria
  inventar esses 3 campos la ou descartar -- contra o principio 2 (flavor nao
  se perde).
- `candidatos()` (motor/motor.py:3648) ja filtra por `kind` vindo de
  `feat_slot.kind`, e o item 106 mediu **4 blocos de `ChoiceSet` com
  `itemType=action`** que o motor ignora hoje porque nao ha kind pra casar
  (so `feat` era tratado). Um kind `action` destrava esses 4 blocos de graca,
  sem mudanca de motor.
- `tactic`/`class-kit` sao o precedente de "kind novo achado pelo portao 9,
  nao falha de extrator" -- mesma classe de omissao da spec original.

**Argumento por `class-feature`:**
- Menos um vocabulario novo pro app entender (a UI ja sabe renderizar
  `class-feature`).
- A maioria das 317 e "concedida uma vez, no nivel da mae, sem escolha
  propria" -- comportamento identico a uma sub-feature comum (o padrao que o
  item 100/107 ja resolveu para `Advanced Alchemy` etc., que SAO
  `class-feature`).
- Contra: perderia `actionType`/`category`, que sao dado real da fonte
  (trigger de reacao, custo de acao) -- e olhando `ficha.py`, a acao PRECISA
  saber se e reacao pra imprimir o Retributive Strike da forma certa.

**Recomendacao com base no que a base ja fez duas vezes:** kind proprio
`action`. E o mesmo padrao de `tactic`/`class-kit`/`ritual`/`relic`/`language`
-- todos "achado pelo portao 9, nunca couberam limpo em kind existente" -- e
o motor ja tem o gancho (`candidatos()` por `kind` de `feat_slot`) esperando
por ele.

## 6. Efeito colateral: quem assume a lista de kinds

Locais que tratam `kind` como conjunto ja fechado ou quase:

- `motor/motor.py:134` -- `self._kinds = {r.get("kind") for r in ...}`: **e
  derivado do proprio index**, kind novo entra sozinho, sem mudanca de codigo.
- `motor/motor.py:3723` -- `candidatos()` casa `kinds_do_bloco` contra
  `self.base.kinds()`; ja tolera kind desconhecido (vira lista vazia, cai no
  bypass "sem kind = nao filtra"). Kind novo so amplia o que ja filtra
  corretamente -- sem quebra.
- `pipeline/portoes.py` -- `FORA_DE_ESCOPO` cita `action` explicitamente
  (secao 5); e o UNICO lugar do pipeline que precisa de edicao de fato se
  `action` virar kind.
- `pipeline/emitir_app.py` -- corte por LISTA NEGRA de campo (`DESCARTAR`),
  nao de kind: kind novo entra no payload por padrao, sem mudanca. So a tupla
  `montar_ficha` (linha 128, o "nucleo pra montar ficha") precisaria GANHAR
  `"action"` -- senao a deed/reacao so carrega sob demanda, tarde demais pra
  montar a ficha do Gunslinger/Campeao na primeira tela.

**Custo em bytes**, medido contra o build ja gerado
(`pipeline/base/app/_manifesto.json`, sem re-rodar nada):

```
python3 -c "
import json
d=json.load(open('pipeline/base/app/_manifesto.json'))
print(d['por_kind']['tactic'])     # {'registros': 37, 'gzip_bytes': 1666}  -> 45 B/registro
print(d['por_kind']['class-feature'])  # {'registros': 847, 'gzip_bytes': 27583} -> 32.6 B/registro
"
```

Nucleo atual (`class, class-feature, feat, ancestry, heritage, background,
archetype, skill`) = **0,529 MB gzip** -- bate exato com o alvo de 0,53 MB do
README. Usando `tactic` como analogo mais proximo (mesmo pack de origem,
mesma forma compacta): **317 acoes de construcao x ~45 B/registro gzip ~=
14 KB**; mesmo no piso mais caro (peso de `feat`, ~70 B/registro): **~22 KB**.
Todos os 557 docs do pack, se um dia entrarem inteiros: **~25-39 KB**. Em
qualquer cenario, **< 5% de crescimento sobre o nucleo de 0,53 MB** -- o
alvo do README nao e ameacado por este kind.

---

## O que a spec vai precisar decidir

1. **`action` vira kind proprio ou entra como `class-feature`?**
   Evidencia a favor de kind proprio: precedente de `tactic`/`class-kit`
   (secao 5), forma propria (`actionType`/`category`/sem nivel, secao 1),
   gancho ja existente no motor para 4 blocos `ChoiceSet` tipo `action`
   (item 106). Evidencia a favor de `class-feature`: menos vocabulario novo,
   maioria dos casos e "concessao simples sem escolha propria" (secao 2).
   Recomendo kind proprio -- ver secao 5.

2. **Escopo do extrator: as 317 referenciadas, ou o pack inteiro (557)?**
   O principio 4 ("nada e descartado") empurra pro pack inteiro; o custo em
   bytes (secao 6) nao probe nenhum dos dois. Mas as 240 nao-referenciadas
   (basic/skill/exploration/downtime/subsystems) sao vocabulario de MESA
   (Stride, Interact, Aid), nao de FICHA -- o proprio principio 1 ("nao e
   sistema de jogo") sugere corte ali. Se cortar, `FORA_DE_ESCOPO` do portao 9
   precisa de uma sub-regra por categoria/pasta, nao so remover `action`
   inteiro (senao o portao cobra as 240 que a spec decidiu nao trazer).

3. **`FORA_DE_ESCOPO` do portao 9 precisa mudar junto**, e a mudanca depende
   da decisao 2: remover `action` inteiro (se o pack entrar por completo) ou
   trocar por um criterio mais fino (se so as referenciadas entrarem).

4. **`montar_ficha` em `emitir_app.py` precisa ganhar `"action"`** se o kind
   entrar -- caso contrario a deed/reacao carrega tarde demais pra montar a
   ficha do Gunslinger/Campeao na primeira tela (custo irrelevante, secao 6,
   entao nao ha razao pratica pra deixar de fora).

5. **Os 10 pares do Gunslinger tem DUAS vias**, achado nesta medicao (secao
   3): a primaria (`Way of X` concede a deed direto, estatica, sem
   condicional) e a secundaria (`Slinger's Readiness`/`Practiced Reloads` le
   a flag). A spec do grant condicional so precisa do vocabulario `se` pra
   via secundaria -- a primaria resolve sozinha assim que `action` existir
   como kind, sem esperar `derivar_grant_condicional.py`.

6. **`Into the Fray` e falso-positivo hoje** (secao 3): resolve por homonimo
   com um feat do arquetipo Viking. Quando `action` virar kind, o casamento
   por nome/pack (`PACK_PARA_KIND`, a regra do gemeo) precisa escolher o
   `actionspf2e` certo -- ou o Way of the Drifter continua concedendo o feat
   errado, so que agora em silencio (sem alarme, porque "funcionava antes").
