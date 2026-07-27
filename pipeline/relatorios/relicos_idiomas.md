# Relatorio -- extrator `relicos_idiomas.py` (relic, language)

Gerado por `pipeline/extratores/relicos_idiomas.py`. Saida:
`pipeline/saida/relicos_idiomas.json` (239 registros). Rodar:
`python3 pipeline/extratores/relicos_idiomas.py`.

Os dois kinds entraram na spec v2 pela mesma porta (ver
`docs/2026-07-26_auditoria-ampla.md`, secao A4): omissao ao escrever a lista
original de "Kinds em escopo", nao falha de extrator anterior. Zero registros
em 18.176 antes deste extrator.

## Contagem por kind contra o censo do AoN

Censo = docs de `category=<kind>` no Elasticsearch do AoN **descontando os
que tem `remaster_id`** (metodo da auditoria A4 -- e o unico que achou os dois
buracos em primeiro lugar).

| kind | censo AoN vigente | registros emitidos | delta |
|---|---|---|---|
| `relic` | **122** | **122** | 0 |
| `language` | **117** | **117** | 0 |
| **total** | **239** | **239** | **0** |

Bate exato nos dois. Query de censo (mesma da auditoria, reexecutavel):

```json
{"size":0,"track_total_hits":true,
 "query":{"bool":{"must":[{"term":{"category":"relic"}}],
                  "must_not":[{"exists":{"field":"remaster_id"}}]}}}
```
(trocar `"relic"` por `"language"` pra segunda contagem; header `User-Agent`
obrigatorio, senao a resposta do elasticsearch.aonprd.com trava.)

Como os dados ja estao em disco (`pipeline/dados_brutos/aon_relics.json`,
219 docs; `aon_languages.json`, 155 docs), a mesma contagem foi feita local
sem rede: `len([d for d in docs if not d.get("remaster_id")])` -- 122 e 117,
identico ao numero publicado na spec e na auditoria.

## Estrutura descoberta na extracao: um doc AoN = um gift, nao um relic completo

A hipotese inicial (relic = artefato completo com os tres graus Minor/Major/
Grand embutidos) estava errada. Confirmado cruzando nome contra grau:

- 219 docs brutos = 108 Minor Gift + 74 Major Gift + 37 Grand Gift.
- 122 vigentes = **122 nomes unicos** -- zero doc com mais de um grau sob o
  mesmo nome. Cada doc de `category=relic` e um gift individual, amarrado a
  um **aspecto** (tema, ex.: "Air", "Luck", "Time" -- 21 aspectos distintos,
  20 elementais/tematicos + o aspecto especial "Intelligent Relic").

A trilha de progressao da spec ("gift/aspect: minor/major/grand") virou campo
proprio `relic.aspect` (lista -- alguns gifts combinam 2-3 aspectos, ex.
"Elements of Creation" = Air+Earth+Water) e `relic.grade` (`minor`/`major`/
`grand`, derivado do campo `type` do AoN). Distribuicao:

| grade | n |
|---|---|
| minor | 60 |
| major | 41 |
| grand | 21 |

Nenhum grade nulo -- os 3 valores de `type` ("Relic Minor/Major/Grand Gift")
resolveram em 122/122.

Campos extras do bloco `relic`, so quando presentes na fonte:

| campo | cobertura | nota |
|---|---|---|
| `element` | 32/122 | subtipo elemental do gift (ex. Fire, Air) -- so preenchido pra aspectos elementais, list |
| `school` | 19/122 | escola de magia legado (conjuration, evocation...). **Achado**: a AoN ainda popula esse campo em docs *vigentes* (sem `remaster_id`) mesmo apos o remaster ter eliminado a taxonomia de escola pra spell de jogador (so `illusion` sobreviveu, per `normalizacao_traits.json`). Passado como leitura direta, sem tentar reconciliar com a remocao -- fora de escopo pra este extrator, registrado aqui pra quem for mexer depois. |

## `language`: sem prosa real, so a linha de fonte

Achado na extracao: a AoN **nao tem descricao pra idioma**. O campo `text`
bruto e sempre so `"<Nome> Source <Livro> pg. N"` -- confirmado por
varredura completa (117/117), comprimento maximo 79 caracteres, mediana 34.
Nao ha campo alternativo (`summary` tambem vazio em todos).

Isso ainda satisfaz o contrato ("`text` sempre preenchido") porque o valor
nao e vazio -- so pobre. `prov.text` nao foi setado no envelope porque o
proprio `texto` nao carrega conteudo substantivo alem do que ja esta em
`name`/`source` (decisao: nao duplicar prov pra um campo que so repete outros
dois já com prov proprio). Registrado aqui como gap de fonte, nao de
extrator: nem Foundry nem pf2etools tem alternativa (ver secao Fontes).

## `relic`: `prerequisite` em 17/122, nunca convertido pra `requires`

| tipo de prerequisito | n |
|---|---|
| propriedade do item ("The relic is a worn item.", "...is a weapon.", "...is Nth level or higher.") | 11 |
| depende de outro gift ja escolhido (ex. "creative spark gift") | 6 |
| **total com `prerequisite`** | **17** |

Nenhum dos dois tipos parseia pra `requires` formal: a linguagem de predicado
da spec (`class_level`, `character_level`, `ability`, `proficiency`, `has`,
`trait`, `spellcasting_tradition`) descreve o **personagem**, nao propriedade
do **item**/relic ("e uma arma", "e nivel 5+"). Os 6 casos de "depende de
outro gift" poderiam em tese reusar o operador `has` apontando pro
`wb:relic/<slug>` do gift citado (confirmado: os 6 nomes citados --
"creative spark", "form of fury", "living death", "death gaze", "fervor",
mais um -- todos resolvem contra os 122 slugs emitidos) -- **nao foi
tentado**. Decisao consciente: `has` no exemplo da spec e sobre o personagem
ter um feat, nao sobre um relic ja ter desbloqueado outro gift; estender o
operador pra essa semantica e decisao de spec, nao de extrator. Fica
documentado, `requires_texto` preserva o texto cru nos 17, `requires_parseado
=false` neles (vs. `true` vacuo nos outros 105).

## `grants_completos`

| kind | valor | n | motivo |
|---|---|---|---|
| `language` | `null` | 117/117 | esta em `KINDS_SEM_GRANTS` (comum.py) -- idioma nao concede nada que o builder calcule |
| `relic` | `false` | 122/122 | todo gift TEM mecanica (efeito de "Activate" com dano/beneficio -- ex. "1d12 electricity damage", "you gain 50 additional Hit Points"), mas a linguagem de `grants` da spec (`proficiency`/`ability_boost`/`feat_slot`/`skill_training`/`hp_per_level`/`spell_slots`/`focus_pool`/`flat_modifier`) nao cobre "ativar uma habilidade tipo magia com efeito arbitrario", e nao ha rule element do Foundry pra converter (Foundry nao modela relic, ver secao Fontes). Conversao nunca tentada -> `false` em 100%, nao em silencio. |

`relic` uniforme em `false` e o MESMO padrao que a auditoria A2 flagrou como
suspeito em `mechanized` da v1 (kind inteiro com o mesmo valor). A diferenca:
aqui e um fato verificavel (nenhum gift teve `grants` convertido, porque o
DSL nao cobre o tipo de efeito), nao um artefato de "cada extrator calculando
diferente" -- o portao 8 da spec (`>100 registros de 2+ fontes e zero
conflitos`) nao se aplica aqui de qualquer forma, porque `relic`/`language`
sao mono-fonte (ver abaixo).

## Fontes: `relic` e `language` sao mono-AoN, confirmado por busca (nao por ausencia de tentativa)

**Foundry** -- nenhum item type `relic` nem `language` existe no checkout
pinado (`packs/pf2e/**`, commit `87f9e5028baaa10b70fdc766260b7886def17e04`):

```
$ grep -rl '"type": *"relic' pipeline/dados_brutos/foundry/packs/pf2e/   -> vazio
$ python3 -c "... Counter(tipos em packs/pf2e/equipment/*.json) ..."
Counter({'equipment': 2323, 'consumable': 1670, 'weapon': 980, 'ammo': 204,
         'armor': 202, 'treasure': 153, 'shield': 118, 'backpack': 46, 'kit': 2})
```
Sem `'relic'` na lista. Explicacao de regra: relic e construcao de GM sem
rule element executavel (o sistema pf2e nao simula a mecanica arbitraria de
cada gift); idioma no Foundry e so um `CONFIG.PF2E.languages` -- dicionario
slug -> rotulo, nunca um Item, o mesmo padrao que `referencia.py` ja achou
pra `trait`.

**pf2etools** -- sem `relics-*.json` nem `languages-*.json` em
`pipeline/dados_brutos/pf2etools/` (205 arquivos, nenhum bate). Grep por
`"relic"` em `baseitems.json` (candidato mais provavel) e por
`relic`/`language` em `_listing.json`: zero ocorrencias nos dois.

**Consequencia**: nao ha precedencia de campo pra aplicar (nada disputa) --
todo campo de conteudo vem direto do AoN com `prov` = `"aon"`.
`comum.escolher()` nao entra em jogo por falta de candidato concorrente.
**Zero `conflitos`** nos 239 registros -- esperado e nao e sinal de
instrumentacao ausente (portao 8 da spec nao se aplica a kind mono-fonte).

## Dedup legado/remaster e uma armadilha achada em `language`

Mesmo criterio dos extratores irmaos (doc com `legacy_id` = versao remaster,
doc com `remaster_id` = absorvido). Achado especifico: **4 docs de
`aon_languages.json`** (`Wayang`, `Tanuki`, `Iblydosi`, `Yaksha`) trazem
`"remaster_id": ["0"]` -- um sentinela de "removido no remaster sem
sucessor" (o id `"0"` nao existe no arquivo, nao e um vinculo real). A regra
usada aqui (`vigente = doc sem remaster_id`, aplicada literalmente) ja
exclui esses 4 corretamente -- é a mesma definicao do censo. Registrado
porque o dedupe generico de `rituais.py`
(`dedupe_aon_legacy_remaster`, que so consome um doc como "legado" quando o
`remaster_id` resolve pra outro doc do arquivo) **contaria esses 4 como
canonicos por engano** -- testado, dava 121 em vez de 117. Por isso este
extrator nao reusa aquela funcao (ver docstring do modulo) e aplica a regra
"sem remaster_id" direto, que e a definicao literal do censo da auditoria.

`legacy_id`/`legacy_name` (renomeacao com nome preservado em `aliases`):

| kind | com `legacy_id` (remaster de algo) | com `legacy_name` (nome mudou) |
|---|---|---|
| `relic` | 97/122 | 1/122 (`Sacred Glow` <- `Holy Light`) |
| `language` | 34/117 | 12/117 (ex. `Petran` <- `Terran`, `Pyric` <- `Ignan`) |

## `traits`: uniao ainda passa pelo mapa legado->remaster mesmo mono-fonte

`comum.uniao_traits()` foi usado de qualquer forma (nao so `prov_lido`
direto) porque a absorcao do mapa `normalizacao_traits.json` ainda se aplica
a fonte unica. Achado: `Azata's Grace` (relic) traz `trait: ["chaotic",
"conjuration", "divine", "uncommon"]` -- `uncommon` filtrado (raridade
duplicada dentro do array `trait`, mesmo padrao ja documentado em
`rituais.py`/`merge_traits`), `chaotic` e `conjuration` sao removidos sem
sucessor (escolas de magia e alinhamentos, ver
`normalizacao_traits.json:removidos_sem_sucessor`) -> viram
`aliases_traits`, ficam so `["divine"]` em `traits`. Comportamento correto,
nao bug.

| kind | com `traits` (pos-filtro) | exemplo do unico trait "mecanico" real |
|---|---|---|
| `relic` | 95/122 | -- |
| `language` | 1/117 | `Wildsong` -> `["secret"]` (`Secret` e trait real de PF2e, distinto de raridade -- confirmado: `rarity="common"` no mesmo doc) |

Language praticamente nao tem trait alem de raridade -- confirmado por
varredura: dos 103/117 docs com `trait` bruto no AoN, **102 sao so
raridade** (`uncommon`/`rare`) e 1 e `secret`. Sem perda: e o mesmo padrao ja
verificado pra `background`/`heritage`/`deity`/`archetype` na auditoria A4
("traits vazio... confirmado sem perda").

## `source.book`: limpo na escrita, achado de markdown vazando em `text`

`source.book` usa `comum.limpar_livro()` direto no extrator (nao so no
reconciliador) -- 0/239 com `\r\n` literal, confirmado por varredura.

Achado separado, no campo `texto` (nao `source.book`): **6/117 languages**
trazem link markdown cru dentro do `text` bruto do AoN, ex.:

```
' Aishmayar Source [Pathfinder #218: Titanbane ](/Sources.aspx?ID=274) pg. 72'
```
(as 5 languages de "Pathfinder #218: Titanbane", que citam a fonte com
`[titulo](url)` em vez de texto plano -- inconsistencia da propria AoN, so
nesse issue). Corrigido com a mesma regra de `emitir_textos.py:limpar()`
(`re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", t)`) aplicada no `texto` embutido
por este extrator -- 0/239 com link markdown cru na saida final. Nota: o
passo posterior `emitir_textos.py` reprocessa a prosa de novo a partir de
`dados_brutos` (nao le o `texto` deste arquivo), entao o build final ja
sairia limpo de qualquer jeito; a limpeza aqui e por consistencia do proprio
artefato emitido, igual aos extratores irmaos.

`page` ausente em 3/117 languages (`Muan`, `Talican`, `Orvian`, todas de
"Rage of Elements") -- confirmado que a propria fonte AoN nao cita pagina
pra essas 3, nao e falha de regex.

## `license`

Nao computada por este extrator -- `source.license` fica `null` nos 239
registros de proposito, e `source.remaster` (booleano, mesma regra de
`magias.py`/`rituais.py`: `bool(legacy_id)`) e emitido pra o reconciliador
inferir. Testado em sandbox (copia isolada do pipeline, no scratchpad, sem
tocar nos arquivos reais do projeto): `reconciliar.py` roda sobre os 239
registros e infere `license` via `LIVROS_ORC`/`remaster` pra 100% deles
(ex.: `Player Core` -> ORC, `Highhelm` -> OGL), com `prov.source.license =
"waybuilder~inferido:livro"` e `source.license_inferida: true` -- mesmo
caminho que os extratores irmaos ja usam.

## Verificacao de integracao (sandbox, nao afeta o repo real)

`pipeline/base/` ja existe no repo (build de outra sessao) -- por instrucao,
nao rodei `reconciliar.py` contra o repo real pra nao sobrescrever esse
artefato de outra pessoa. Copiei o pipeline inteiro pra
`/tmp/.../scratchpad/wb_dryrun/` e rodei la:

- `reconciliar.py` ja tem `"relicos_idiomas.json"` na lista `ENTRADA` (linha
  33) -- alguem ja cabeou o nome do arquivo esperado antes desta extracao
  rodar, confirma o nome de arquivo pedido.
- Com o pipeline completo (9 familias, 19.239 registros brutos), o
  reconciliador **crasha** em `fonte_do_campo` -> `comum.fonte_de()`
  recebendo uma lista em vez de string. Isolado: **bug pre-existente em
  `rituais.py`**, nao deste extrator -- `rituais.py` seta `prov["traits"] =
  traits_fontes` (uma LISTA, ex. `["foundry", "aon"]`, per spec:
  "`prov.traits` passa a registrar a lista de fontes que contribuiram") em
  108/150 registros, mas `reconciliar.fonte_do_campo()` espera sempre uma
  string e chama `.split("~")` nela sem checar tipo. Confirmado excluindo
  `rituais.json` da lista `ENTRADA` (so no sandbox): o reconciliador roda
  limpo, produz `base` com **122 relic + 117 language exatos** (bate com a
  saida deste extrator), 0 conflitos nos dois kinds, license inferida
  corretamente. **Nao mexi em `rituais.py` nem em `reconciliar.py`** -- fora
  do escopo autorizado desta tarefa; fica registrado aqui pra quem for
  resolver o bug do `rituais.json`.

## O que ficou faltando (resumo)

1. **`grants` de relic nunca convertido** (122/122 `grants_completos=false`)
   -- precisa de vocabulario novo no DSL de `grants` pra "ativar habilidade
   com efeito arbitrario", decisao de spec, nao de extrator.
2. **`requires` de relic nunca parseado** (17/122 com `requires_texto`,
   `requires_parseado=false`) -- 11 sao propriedade do item (fora da
   linguagem de predicado atual), 6 poderiam reusar `has` apontando pra
   outro `wb:relic/*` mas isso exigiria decisao de spec sobre o significado
   de `has` fora do contexto de personagem.
3. **`language` sem prosa real** -- gap da propria fonte AoN, sem
   alternativa em Foundry/pf2etools (ver secao dedicada acima).
4. **`school` do bloco `relic`** (19/122) e taxonomia legado que a AoN
   ainda expõe em doc vigente -- passado como leitura direta, sem tentar
   reconciliar com a remocao de escolas de magia no remaster.
5. **Bug pre-existente em `rituais.py` x `reconciliar.py`** (prov.traits
   como lista quebra `fonte_do_campo`) -- nao corrigido, fora do escopo
   autorizado, documentado acima pra quem for mexer no reconciliador ou no
   extrator de rituais depois.
