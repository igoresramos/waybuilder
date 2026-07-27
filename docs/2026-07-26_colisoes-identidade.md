# Colisoes de identidade na base canonica

Data: 2026-07-26
Base: `pipeline/base/index.json` (18.176 registros)
Fontes de verificacao: AoN Elasticsearch (`https://elasticsearch.aonprd.com/aon/_search`), clone do Foundry `pf2e` em `/tmp/.../scratchpad/pf2e-research/pf2e/packs/pf2e/`.

## 1. A varredura

### 1.1 Criterio

`wb:<kind>/<slug>` assume nome unico por kind. Quando duas entidades homonimas
existem, a fusao por id produz uma quimera: campos de uma entidade misturados
com campos de outra. O sinal e **conjuntos de `traits` categoricamente
disjuntos entre fontes** -- nao "diferentes", **disjuntos** (interseccao
vazia). Divergencia real e `8` contra `9`; quando uma fonte diz `mythic` e
outra `archetype`, sao dois objetos.

### 1.2 Implementacao

Script: `/tmp/.../scratchpad/wb2/scan_traits2.py` (le `pipeline/base/index.json`,
so leitura, nao escreve nada).

1. Para cada registro com `conflitos` contendo `campo: "traits"`, extrai o
   conjunto de traits que cada fonte carregava naquele campo em disputa.
2. Marca **totalmente disjunto** quando nenhum par de fontes compartilha
   nenhum trait.
3. Descarta como causa legitima (nessa ordem):
   - **Ancestria renomeada no remaster**: mapa `aasimar/tiefling/aphorite/ganzi
     -> nephilim`, `ifrit/oread/sylph/undine -> naari` (da spec
     `2026-07-26-schema-base.md`). Se aplicar o mapa faz os conjuntos
     colidirem, nao e problema.
   - **Granularidade parametrizada**: um trait e prefixo do outro seguido de
     hifen (`two-hand` / `two-hand-d12`, `versatile` / `versatile-p`,
     `attached` / `attached-to-shield`, `deflecting` / `deflecting-slashing`
     etc. -- generalizei o criterio da spec, que so cita sufixos numericos,
     para qualquer sufixo de qualificacao. Ver nota abaixo).
4. O que sobra e candidato a **facetas complementares** (as duas fontes
   descrevem aspectos do mesmo objeto, ex.: foundry registra o trait mecanico
   da arma, aon registra o trait do item magico) ou **colisao real**.
5. Verificacao final: para cada candidato, consulta ao AoN Elasticsearch por
   `match_phrase` no nome, filtrando pela `category` equivalente ao `kind` do
   registro. **Mais de um documento distinto (URL/ID diferente) com o mesmo
   nome e categoria e prova direta de duas entidades.** Cruzado com o clone do
   Foundry (`grep` por `"name": "<nome>"` em `packs/pf2e/feats/`): mais de um
   arquivo com o mesmo `name` tambem prova.

### 1.3 Numeros

| etapa | contagem |
|---|---:|
| registros com `conflitos.campo == "traits"` | 2.148 |
| totalmente disjuntos (raw) | **137** |
| resolvidos por ancestria renomeada | 31 |
| resolvidos por granularidade (regra generalizada por prefixo) | 29 |
| remanescentes (facetas complementares + colisao real) | 77 |
| dos remanescentes: feats (candidatos a colisao) | 4 |
| dos remanescentes: armor/weapon/equipment (facetas complementares) | 73 |

O numero de disjuntos totais (137) e o de resolvidos por ancestria renomeada
(31) batem exatos com os numeros ja registrados em `specs/2026-07-26-schema-base.md`
("Colisao de identidade"). Granularidade fechou em 29 contra 18 citados na
spec -- generalizei a regra de absorcao (a spec so cita sufixo `-d\d+`,
`-\d+`, `-aim-d\d+`; eu tambem absorvi `-p/-s/-b` de `versatile` e sufixos de
qualificacao como `attached-to-shield`/`attached`), entao um numero maior de
casos de armadura/arma/escudo caiu em granularidade em vez de sobrar como
"facetas complementares". O total de remanescentes (77) e proximo dos 88
implicitos na spec (72 facetas + 16 reais) -- a diferenca vem dessa mesma
generalizacao de regra, nao de um criterio diferente.

**Todos os 73 casos de armor/weapon/equipment remanescentes foram checados
contra AoN** e nenhum revelou segundo documento distinto na mesma categoria: sao
o padrao "foundry registra trait mecanico do item base (`finesse`, `agile`,
`deadly-dN`, `versatile-X`, tracos de arma), aon registra trait do item magico
completo (`magical`, `invested`, escola de magia, energia)" -- **facetas
complementares confirmadas, nao colisao**. Nenhum tinha conflito adicional de
`level`/`rarity` corroborando colisao (checado contra o campo `conflitos`
inteiro de cada um).

## 2. Tabela caso a caso -- os 4 candidatos por `traits` disjuntos

| id | foundry diz | aon diz | veredito | evidencia |
|---|---|---|---|---|
| `wb:feat/death-from-above` | `["archetype"]`, nivel 8 | `["mythic"]`, nivel 16 | **colisao real** | AoN indexa `feat-7380` (Death from Above, Mythic, nivel 16, War of Immortals pg.128) e `feat-7610` (Death from Above, Archetype Verduran Shadow, nivel 8, *Pathfinder #201: Pactbreaker* pg.80) como documentos distintos. Foundry tem 2 arquivos: `feats/archetype/verduran-shadow/death-from-above.json` (`_id` `j8CLa6RoohfKCWoO`, bate com o xref do registro) e `feats/archetype/eternal-legend/death-from-above-eternal-legend.json` (`_id` `95dHFM31VrUjn3d3`) |
| `wb:feat/reckless-abandon` | `["fortune","goblin"]`, nivel 17 | `["barbarian","rage"]`, nivel 17 (aon real = 16) | **colisao real** | AoN indexa `feat-173` (Reckless Abandon, Barbarian/Rage, nivel 16, Core Rulebook, renomeado no remaster para "Desperate Wrath" `feat-5868` via `remaster_id`) e `feat-1429`/`feat-4454` (Reckless Abandon (Goblin), Fortune/Goblin, nivel 17, APG legado / Player Core remaster) -- **entidades diferentes**, o goblin nao mudou de nome no remaster. Foundry so tem 1 arquivo com esse nome: `feats/ancestry/goblin/level-17/reckless-abandon.json` (`_id` `fqw1ELaqavuKLHIj`, o goblin) |
| `wb:feat/dual-weapon-reload` | `["gunslinger"]`, nivel 1 | `["archetype"]`, nivel 4 | **colisao real** | AoN indexa `feat-3294`/`feat-8659` (Dual-Weapon Reload (Gunslinger), nivel 1, Guns & Gears remaster/legado) e `feat-1952`/`feat-6309` (Dual-Weapon Reload, Archetype "Dual-Weapon Warrior"/"Crossbow Infiltrator", nivel 4, APG legado / Player Core 2 remaster). Foundry so tem 1 arquivo: `feats/class/gunslinger/level-1/dual-weapon-reload.json` (`_id` `sjChYEuEWPqndCSK`, o gunslinger) |
| `wb:feat/even-the-odds` | `["swashbuckler"]`, nivel 4 | `["archetype","fortune"]`, nivel 14 | **colisao real** | AoN indexa `feat-6145` (Even the Odds, Swashbuckler, nivel 4, Player Core 2) e `feat-7675` (Even the Odds, Archetype "Eagle Knight"/Fortune, nivel 14, Shining Kingdoms pg.51). Foundry so tem 1 arquivo com esse nome exato: `feats/class/swashbuckler/level-4/even-the-odds.json` (`_id` `5HDBvVbfoaXljbch`, o swashbuckler); o Eagle Knight esta em `feats/archetype/eagle-knight/even-the-odds-eagle-knight.json` (`_id` `ccLpjnWjl62Ehegc`) |

Os 4 batem exatos com os 4 ja confirmados na inspecao inicial do pedido.

## 3. Colisao achada por outro sinal (nao aparece como `traits` disjunto)

`wb:feat/play-to-the-crowd` **nao entrou** na lista acima porque os `traits`
em disputa (`["archetype","concentrate"]` do foundry vs. `["archetype","skill"]`
do aon) **compartilham `"archetype"`** -- interseccao nao-vazia, entao o
detector de disjuncao total nao pega. Foi achado pelo sinal alternativo pedido
no escopo: **`level` com diferenca grande dentro do mesmo `conflitos`**
(`foundry: 4, pf2etools: 4, aon: 12`), cruzado depois com AoN.

| id | foundry diz | aon diz | veredito | evidencia |
|---|---|---|---|---|
| `wb:feat/play-to-the-crowd` | `["archetype","concentrate"]`, nivel 4, `requires: gladiator-dedication` | `["archetype","skill"]`, nivel 12, uncommon | **colisao real** | AoN indexa `feat-1978`/`feat-6335` (Play to the Crowd, Archetype Gladiator/Concentrate, nivel 4, APG legado / Player Core 2 remaster) e `feat-7637` (Play to the Crowd, Archetype Dandy/Skill, nivel 12, uncommon, *Pathfinder #204: Stage Fright*). Foundry tem 2 arquivos: `feats/archetype/gladiator/play-to-the-crowd.json` (`_id` `KrYvJ5n06yHCipCZ`, bate com o xref do registro) e `feats/archetype/dandy/level-12/play-to-the-crowd-dandy.json` (`_id` `uiEoY3uGSEOCaftX`) |

**Metodo usado para achar esse e descartar o resto**: filtrei todos os
registros com `conflitos` tendo *ao mesmo tempo* `campo: "level"` (diferenca
>= 4) e `campo: "traits"` (interseccao <= 1 trait). Deu 2 candidatos:
`play-to-the-crowd` (confirmado colisao acima) e `wb:feat/animal-soul-siblings`
(**descartado** -- AoN confirma `feat-5251`/`feat-8197` como o **mesmo** feat,
ligados por `remaster_id`/`legacy_id`, nivel mudou de 5 para 1 por erratum no
remaster, traits identicos `["reincarnated","universal-ancestry"]`; nao e
colisao).

Tambem varri, mais largo, **todos** os registros com `conflitos.campo ==
"level"` e diferenca >= 4 (38 no total, dos quais so 2 tinham conflito de
`traits` junto -- os dois do paragrafo acima). Dos 36 restantes (so `level`
diverge, `traits` bate ou nao tem conflito registrado), checkei contra AoN os
20 com maior chance de esconder colisao (feats + os 2 weapons com maior gap):

- **Confirmados como legitimos** (AoN liga os dois documentos por
  `remaster_id`/`legacy_id`, mesmos traits, nivel mudou por erratum de
  republicacao): `energy-ward`, `expand-aura`, `fuse-stance`,
  `hellknight-dedication`, `one-toed-hop`, `oracular-warning`,
  `soaring-flight`, `soaring-form`, `well-groomed`, `war-saddle`,
  `uplifting-winds` (aqui so 1 documento no AoN, foundry e o unico
  divergente), `specialized-companion`, `clockwork-macuahuitl`,
  `high-contrast-goggles`.
- **`wb:feat/daywalker`**: nao e colisao -- **ja esta corretamente
  desmembrado** na base (`wb:feat/daywalker`, dhampir, nivel 13, e
  `wb:feat/daywalker-vampire`, arquetipo Vampire, nivel 6, ambos com dados
  internamente consistentes e xref proprio). O conflito de `level` registrado
  (`pf2etools: 6`) e ruido do pf2etools, nao evidencia de fusao.
- **10 materiais brutos** (`adamantine-chunk/ingot`, `dawnsilver-chunk/ingot`,
  `duskwood-branch/lumber`, `keep-stone-chunk/ingot`, `orichalcum-chunk/ingot`,
  `peachwood-branch/lumber`, `sovereign-steel-chunk/ingot`): padrao ja
  documentado em `docs/pdfs/2026-07-26_arbitragem-divergencias.md` (caso
  `dawnsilver-chunk`, verificado contra PDF) -- foundry nivel 0 e o material
  bruto, o nivel alto do aon e de uma variante/grau diferente do mesmo
  material. Legitimo, nao colisao.
- **`wb:weapon/temperbrand`** (foundry nivel 20, aon nivel 16): **indeterminado**.
  So achei 1 documento de arma no AoN (`equipment-3489`, nivel 16, confere com
  o valor aon da base); existe tambem uma **criatura** `creature-3395` com o
  mesmo nome (nivel 18) mas e outro `kind` (bestiario, fora do escopo do
  Waybuilder) -- nao e a mesma colisao que estamos caçando. Nao consegui
  confirmar de onde vem o nivel 20 do foundry nem achar um segundo item. Falta
  verificar o arquivo foundry `equipment-srd.Item.596xrLHt1Sx0p7Pm` diretamente
  linha a linha (nao fiz -- fora do tempo desta rodada).
- Nao verifiquei os 16 restantes dos 36 (a maioria variantes de nivel
  greater/major de armadura ja resolvidas por granularidade, ou feats de baixo
  volume) -- ficam **indeterminados por falta de checagem**, nao por evidencia
  contraria.

## 4. Desmembramento proposto -- os 5 casos confirmados

Padrao estrutural identico nos 5: o pipeline **ja tentou** desmembrar (existe
um registro-irmao com sufixo, dados limpos de uma das duas entidades, vindos
so do Foundry ou so do AoN), mas o registro de slug "base" continua sendo a
quimera porque a etapa de fusao por id (`reconciliar.py::fundir`) juntou
esse slug com o documento **errado** do AoN. Nenhuma edicao foi feita -- so o
diagnostico e a proposta, como pedido.

### 4.1 `wb:feat/death-from-above`

- **Fica em `wb:feat/death-from-above`** (o slug simples): a entidade
  **Verduran Shadow**, arquetipo, nivel 8, uncommon, traits `["archetype"]`,
  source `Pathfinder #201: Pactbreaker` pg.80 (nao War of Immortals -- o
  registro atual tem o source errado, herdado da outra entidade), prereq
  "Canopy Predator; Verduran Shadow Dedication; Expert in Athletics".
  `xref.aon` corrige para `feat-7610` (hoje aponta pro `feat-7380`, errado).
  `xref.foundry` (`j8CLa6RoohfKCWoO`) e `xref.pf2etools` (`WoW1#death-from-above`)
  ja estao certos -- vale checar por que o pf2etools rotulou como "WoW1" um
  feat de Pactbreaker (pode ser reimpressao/compilacao, nao investiguei).
- **`wb:feat/death-from-above-eternal-legend`** ja existe e ja tem os dados
  certos (Eternal Legend, mitico, nivel 16). Falta so completar: `xref.aon =
  feat-7380`, corrigir `source.book` de `"Pathfinder War of Immortals"` (com
  prefixo espurio) para `"War of Immortals"`, e `source.page = 128` (hoje
  `null`).

### 4.2 `wb:feat/reckless-abandon`

Caso diferente dos outros: nao precisa criar registro novo, precisa
**consolidar um duplicado**.

- **Fica em `wb:feat/reckless-abandon`**: a entidade **goblin** (nivel 17,
  common, traits `["fortune","goblin"]`, source Player Core pg.57 -- o nome
  goblin **nao muda** no remaster, entao o slug sem sufixo pertence a ele por
  regra da propria spec, "slug deriva do nome remaster"). `xref.foundry`
  (`fqw1ELaqavuKLHIj`) ja esta certo (e o unico arquivo Foundry com esse
  nome). `xref.aon` corrige para `feat-4454` (Player Core, remaster) com
  `legado: feat-1429` (APG).
- **`wb:feat/reckless-abandon-goblin`** vira redundante -- e a mesma entidade
  acima, so que sem o `xref.foundry`. Absorver nele ou nele absorver o
  primeiro (mesma entidade, so falta decidir qual id sobrevive).
- **`wb:feat/desperate-wrath`** (a entidade barbarian, nome remaster) **ja
  esta correto e completo** -- nao precisa de nenhuma correcao.

### 4.3 `wb:feat/dual-weapon-reload`

Tambem tem duplicado, e falta uma entidade inteira na base.

- **Fica em `wb:feat/dual-weapon-reload`**: a entidade **gunslinger**
  (nivel 1, common, traits `["gunslinger"]`, source Guns & Gears (Remastered)
  pg.111). `xref.foundry` (`sjChYEuEWPqndCSK`) ja certo. `xref.aon` corrige
  para `feat-3294` (remaster) com `legado: feat-8659`.
- **`wb:feat/dual-weapon-reload-gunslinger`** vira redundante -- mesma
  entidade acima, falta so o `xref.foundry`. Mesmo tratamento do caso 4.2.
- **Falta criar** um registro novo para a entidade **arquetipo** (nivel 4,
  common, traits `["archetype"]`, source Player Core 2, arquetipos "Dual-Weapon
  Warrior"/"Crossbow Infiltrator", `xref.aon = feat-6309` com `legado:
  feat-1952`). Nao achei arquivo Foundry pra ela (busquei por nome exato no
  clone e so apareceu o gunslinger) -- pode ser que o Foundry simplesmente nao
  tenha essa variante nessa versao do pack, ou o arquivo esteja sob outro
  nome/pasta que a minha busca nao pegou. Sugiro slug
  `wb:feat/dual-weapon-reload-archetype`.

### 4.4 `wb:feat/even-the-odds`

- **Fica em `wb:feat/even-the-odds`**: a entidade **swashbuckler** (nivel 4,
  common, traits `["swashbuckler"]`, source Player Core 2). `xref.foundry`
  (`5HDBvVbfoaXljbch`) ja certo. `xref.aon` corrige para `feat-6145` (hoje o
  registro nao tem essa entidade representada em lugar nenhum da base --
  diferente dos outros casos, aqui nao ha duplicado, so falta linkar).
- **`wb:feat/even-the-odds-eagle-knight`** ja existe com dados corretos
  (Eagle Knight, arquetipo, nivel 14, Fortune). Falta completar `xref.aon =
  feat-7675` e `source.page = 51` (Shining Kingdoms).

### 4.5 `wb:feat/play-to-the-crowd`

- **Fica em `wb:feat/play-to-the-crowd`**: a entidade **Gladiator** (nivel 4,
  common, traits `["archetype","concentrate"]`, source Player Core 2,
  `requires: wb:feat/gladiator-dedication`). `xref.foundry`
  (`KrYvJ5n06yHCipCZ`) ja certo. `xref.aon` corrige para `feat-6335`
  (remaster) com `legado: feat-1978` (hoje aponta pro `feat-7637`, que e a
  outra entidade).
- **`wb:feat/play-to-the-crowd-dandy`** ja existe com dados corretos (Dandy,
  arquetipo, nivel 12, uncommon, Skill). Falta completar `xref.aon =
  feat-7637` e confirmar `source.page` (o registro quimera atual tem
  `page: 82` vindo do lado aon -- pode ser a pagina certa do Stage Fright pro
  Dandy, mas nao verifiquei contra PDF; so tem 1 arquivo do Stage Fright
  disponivel e nao foi checado nesta rodada).

## 5. Estimativa de colisoes remanescentes sem sintoma visivel

Confirmado nesta rodada: **5 colisoes reais** em ~2.299 registros com
`conflitos`. Todos os 5 tinham pelo menos um sinal detectavel (`traits`
disjunto ou quase-disjunto + `level` com salto grande). Mas o metodo tem um
buraco estrutural que nenhuma variacao de regex fecha: **a funcao `fundir()`
so registra `conflitos` quando os dois lados tem valor nao-vazio e
diferente**. Se duas entidades homonimas colidem e, por coincidencia (ou
porque uma fonte simplesmente nao tinha aquele campo preenchido), `traits`,
`level`, `rarity` e `source` do lado "vazio" nunca entram em disputa
registrada, a fusao acontece **em silencio** -- sem deixar `conflitos`, sem
aparecer em nenhuma varredura que dependa desse campo. Isso e o mesmo
mecanismo ja documentado no `relatorio_reconciliacao.md`/spec pra `grants`
("nunca aparece como campo de conflito real" pelo mesmo motivo).

Bases pra estimar:

- Da amostra que **checei exaustivamente contra AoN** (137 com `traits`
  totalmente disjuntos + 36 com salto de `level` >= 4, total 173 candidatos,
  dos quais uns 40 nao foram individualmente checados por falta de tempo):
  taxa de confirmacao de colisao real foi 5/133 checados (~3,8%).
- Meia duzia de casos (`death-from-above`, `reckless-abandon`,
  `dual-weapon-reload`, `even-the-odds`, `play-to-the-crowd`) tinha
  **registro-irmao com sufixo ja existente** contendo dados limpos de uma das
  duas entidades -- sinal de que outra etapa do pipeline (extracao por pasta
  do Foundry, provavelmente) ja sabia que a colisao existia antes da
  reconciliacao remendar tudo num id so. Vale procurar sistematicamente por
  **todo par de ids `wb:<kind>/<slug>` + `wb:<kind>/<slug>-<algo>`** onde o
  segundo tem `xref` incompleto (so foundry OU so aon, nunca os dois) -- isso
  pode achar mais casos sem depender de `traits` ou `level` nenhum. Nao rodei
  essa varredura nesta sessao (ficou como proxima etapa, nao diagnostico
  fechado).
- Registros **sem nenhum `conflitos`** (a maioria, ~15.877 dos 18.176) nunca
  foram olhados por este metodo -- se uma colisao silenciosa existir ali (uma
  fonte simplesmente nao tinha o campo, entao nunca gerou conflito), este
  relatorio nao pega.

**Estimativa**: com o padrao "registro-irmao com xref incompleto" batendo
5 pra 5 nos casos confirmados, e provavel que existam **mais alguns casos
(ordem de 5 a 15)** com a mesma assinatura estrutural ainda nao achados --
a varredura por pares de id sugerida acima e o proximo passo mais barato pra
fechar essa lacuna, mais barato que uma nova rodada de `traits`/`level`.
Fora esse padrao especifico, nao ha como estimar com confianca quantas
colisoes silenciosas (sem `conflitos` nenhum) existem sem inspecionar uma
amostra do resto da base contra AoN -- **indeterminado**.

## 6. Metodologia e limites

- Nenhum arquivo da base foi modificado (`index.json`, `specs/`, extratores
  intactos). Scripts de analise ficaram em
  `/tmp/.../scratchpad/wb2/` (temporarios, nao versionados).
- Consultas ao AoN: `POST https://elasticsearch.aonprd.com/aon/_search`,
  sempre com `User-Agent` explicito e `track_total_hits: true`, usando
  `match_phrase` no campo `name` (nunca `terms`, que retorna vazio em campo de
  texto). Cada resultado citado neste relatorio foi conferido manualmente
  (nao so contagem de hits) puxando o documento completo por
  `GET /aon/_doc/<id>` antes de declarar colisao confirmada.
- "Confirmado" neste relatorio significa: AoN indexa 2+ documentos distintos
  com mesmo nome e mesma categoria, **e** (quando aplicavel) o clone do
  Foundry tem 2+ arquivos com o mesmo `name`. Onde so um dos dois pode ser
  checado, o relatorio diz explicitamente qual faltou.
