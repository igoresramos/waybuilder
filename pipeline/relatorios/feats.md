---
relatorio: feats
project: waybuilder
extrator: pipeline/extratores/feats.py
saida: pipeline/saida/feats.json
executado: 2026-07-26
---

# Extrator de feats e arquetipos -- execucao real

Todos os numeros abaixo saem da execucao de `python3 pipeline/extratores/feats.py`
sobre os dados fixados. Nada foi estimado.

## Fontes na execucao

| Fonte | Pin | Registros lidos |
|---|---|---|
| Foundry `packs/pf2e/feats` | commit `87f9e5028baaa10b70fdc766260b7886def17e04` | 6.044 feats (6.045 arquivos, 30 MB), 841 class-features, 27 classes, 244 pastas de arquetipo |
| pf2etools `data/feats/*` | branch `dev`, snapshot 2026-07-26 | 5.326 feats em 67 arquivos |
| AoN Elasticsearch `aon` | dump 2026-07-26 | 8.460 `category:feat`, 336 `category:archetype` |

O dump do AoN esta em `pipeline/dados_brutos/aon_feats.json` e
`aon_archetypes.json`; o script de coleta e `_wb_dump_feats.py` (particionado por
`level` porque a consulta com `search_after` leva ~19 s por pagina e estoura o
timeout em serie).

## Saida

`pipeline/saida/feats.json` -- 6.669 registros, 5,76 MB sem gzip.

| | |
|---|---|
| feats | 6.421 |
| arquetipos | 248 |
| com pre-requisito em prosa | 4.263 |
| com `requires` estruturado | 3.609 |
| com `conflitos` | 543 |
| com ponte legado/remaster (`legado_de`/`remaster_de`) | 2.262 / 321 |

Sobreposicao das tres fontes por registro (F=foundry, T=pf2etools, A=aon):

| combinacao | registros |
|---|---|
| F+T+A | 4.047 |
| F+A | 1.878 |
| T+A | 270 |
| F | 100 |
| A | 90 |
| F+T | 18 |
| T | 18 |

3.118 registros homonimos foram colapsados na uniao (mesma feat aparecendo em
linha legada e remaster, ou reimpressa). A regra de desempate e sempre o
registro remaster -- no AoN, o que **nao** tem `remaster_id` apontando para
fora; no Foundry e no pf2etools, o que tem a marca `remaster`.

---

## 1. Taxa de parsing de pre-requisito

**3.609 / 4.263 = 84,7 %.** 654 pre-requisitos ficaram sem predicado.

Fonte vencedora do texto de pre-requisito, por registro:

| fonte | usos |
|---|---|
| pf2etools | 2.615 |
| aon (feat) | 1.350 |
| aon (arquetipo) | 203 |
| foundry | 95 |

O parser e tudo-ou-nada por registro: se um atomo nao resolve, o registro sai
com `requires: null`, `mechanized: false` e o texto preservado em
`requires_texto`. Nao existe predicado parcial na base -- predicado meio certo
e pior que predicado ausente para um construtor que valida escolha.

Como as falhas ocorrem uma por registro (o parser corta no primeiro atomo que
nao resolve), a contagem de padroes abaixo e tambem a contagem de registros
afetados.

### Os 15 padroes nao cobertos mais frequentes

| n | padrao (assinatura normalizada) | exemplo real |
|---:|---|---|
| 20 | `tenets of good` | `tenets of good` |
| 13 | `tenets of evil` | `tenets of evil` |
| 11 | `low-light vision` | `low-light vision` |
| 10 | `member of the gray gardeners` | `{@feat Harsh Judgment\|NGD}, {@feat Vigilante Dedication\|APG}, member of the Gray Gardeners` |
| 10 | `focus pool` | `{@action Arcane Cascade\|SoM}, focus pool` |
| 8 | `zoophonia muse` | `zoophonia muse` |
| 8 | `harmful font` | `harmful font or healing font` |
| 7 | `{action}` | `{@action Envenom\|LOIL}` |
| 6 | `class granting no more hit points per level than n + your constitution modifier` | `{@feat Barbarian Dedication}, class granting no more Hit Points per level than 10 + your Constitution modifier` |
| 6 | `an animal companion` | `an animal companion` |
| 6 | `ability to cast focus spells` | `ability to cast focus spells, divine spells` |
| 5 | `devotion spell ({spell})` | `devotion spell ({@spell lay on hands})` |
| 5 | `healing font` | `healing font` |
| 5 | `evil alignment` | `Trained in Religion; evil alignment` |
| 5 | `a familiar` | `a familiar, you follow a good-aligned deity or patron` |

São 403 assinaturas distintas para 654 falhas, e 282 delas aparecem **uma unica
vez**. A cauda e literalmente prosa artesanal, nao um punhado de formas
sistematicas que valha a pena continuar caçando.

### A cauda por natureza do problema

| natureza | registros | tratavel? |
|---|---:|---|
| capacidade/feature de classe cujo nome nao existe no indice do Foundry (`tenets of good`, `harmful font`, `zoophonia muse`, `focus pool`, `devotion spell`, `an animal companion`) | ~140 | **sim**, quando o extrator de `class-feature` entrar. Sao nomes legados ou features que o Foundry nomeia diferente |
| condicao narrativa / de campanha (`member of the Gray Gardeners`, `you died and returned as a ghost`, `at least 100 years old`, `exposure to the Well of Axuma`) | ~68 | **nao**. Nao e predicado mecanico, e ficcao. Fica `mechanized: false` por design |
| conjuracao especifica (`ability to cast focus spells`, `bloodline spell`, `X sorcerer bloodline spell`) | ~39 | parcial -- exigiria termo de predicado novo (`focus_spells`) |
| quantificador vago (`trained in at least one skill`, `a feat granting access to ...`, `any nephilim lineage feat`) | ~35 | parcial -- exige quantificador existencial sobre conjunto filtrado, que a linguagem nao tem |
| alinhamento legado pre-remaster (`evil alignment`, `tenets of good/evil`) | ~19 | **nao**. Alinhamento saiu do sistema no remaster; o predicado nao deve ganhar termo para isso |
| sentido especial (`low-light vision`, `darkvision`, `precise scent`) | ~18 | **sim** com um termo `sense` novo, hoje fora do vocabulario da spec |
| `{@action}` sem entidade correspondente (acao concedida por outra coisa) | ~8 | parcial |
| prosa unica, nao classificavel | ~334 | nao |

**Recomendacao:** o unico ganho grande restante (~140 registros, ~3 pontos
percentuais) vem de graca quando o extrator de `class-feature` existir e
alimentar o indice de nomes. Nao vale escrever mais regex.

### O que o parser resolve

O exemplo canonico do briefing sai correto:

```
"expert in {@skill Society|PC1}, and either {@feat Courtly Graces|PC1} or {@feat Streetwise|PC1}"
->
{"all": [
  {"proficiency": {"society": {">=": "expert"}}},
  {"any": [{"has": "wb:feat/courtly-graces"}, {"has": "wb:feat/streetwise"}]}
]}
```

Gramatica implementada, em ordem de tentativa:

1. `;` no topo -> `all`
2. **clausula de rank com lista propria** -- `expert in Acrobatics, Athletics, or Stealth`.
   Tentada antes da quebra por virgula, e so aceita se **todo** item da lista for
   alvo de proficiencia valido. E isso que impede `trained in Crafting, expert in
   Society` de virar uma lista de pericias errada, e que resolve a distribuicao do
   rank sobre a lista (`trained in Occultism or Religion` -> dois predicados, nao
   um predicado e um lixo)
3. virgulas -- conector deduzido da palavra que lidera o **ultimo** item
   (`, and` -> `all`; `, or` sem nenhum `and` -> `any`; virgula seca -> `all`)
4. `either ... or ...` -> `any`
5. ` or ` -> `any`; ` and ` -> `all`
6. atomo

As tags do pf2etools sao trocadas por marcas opacas **antes** de qualquer quebra.
Sem isso, `{@feat Sniping Duo Dedication|G&G}` seria cortado no `&`, e nomes com
virgula quebrariam a lista.

Atomos reconhecidos: rank de pericia/Lore/arma/armadura/salvaguarda/Perception,
valor de atributo (`Charisma 14`) **e** modificador do Foundry (`Charisma +2`,
convertido para `>= 14`), nivel de personagem, tradicao de conjuracao,
`{@feat}`, `{@class}` com e sem subclasse, `{@classFeature}`, `{@action}`,
`{@trait}`, `{@ancestry}` com heranca, `{@spell}`, `{@deity}`, `{@item}`,
`{@archetype}`, sufixos `X heritage` e `X trait`, e nome nu resolvido contra o
indice de feats/class-features/classes.

---

## 2. Rule elements do Foundry -> `grants`

2.639 grants emitidos em 1.553 feats.

### Convertidos

| rule element | vira | ocorrencias no grants |
|---|---|---|
| `GrantItem` | `grant_item` | 620 |
| `FlatModifier` | `flat_modifier` | 592 |
| `ActiveEffectLike` (caminhos de ficha) | `proficiency`, `skill_training`, `focus_pool`, `hp`, `languages`, `reach`, `dying_*`, `bulk_*`, `familiar_abilities`, ... | 342 `proficiency` + 47 `skill_training` + ~60 outros |
| `ChoiceSet` | `choice` | 288 |
| `DamageDice` | `damage_dice` | 133 |
| `Resistance` | `resistance` | 126 |
| `BaseSpeed` | `speed` | 123 |
| `MartialProficiency` | `weapon_proficiency` | 91 |
| `CriticalSpecialization` | `critical_specialization` | 59 |
| `Sense` | `sense` | 38 |
| `ActorTraits` | `actor_traits` | 37 |
| `CraftingAbility` | `crafting_ability` | 18 |
| `CreatureSize` | `size` | 11 |
| `Weakness` | `weakness` | 9 |
| `Immunity` | `immunity` | 7 |
| `DexterityModifierCap` | `dex_cap` | 6 |
| `SpecialResource` | `special_resource` | 4 |
| `FastHealing` | `fast_healing` | 4 |
| `MultipleAttackPenalty` | `map_modifier` | 3 |
| `SpecialStatistic` | `special_statistic` | 2 |
| `TempHP` | `temp_hp` | 1 |

Rank numerico do Foundry (0-4) e traduzido para palavra
(`untrained|trained|expert|master|legendary`) na entrada, como a spec exige.

### Ignorados de proposito (nao penalizam `mechanized`)

Sao automacao de rolagem em mesa, nao construcao de ficha. Um construtor de
personagem nao precisa deles para montar a ficha correta:

| rule element | ocorrencias |
|---|---|
| `ItemAlteration` | 949 |
| `RollOption` | 546 |
| `Note` | 269 |
| `AdjustDegreeOfSuccess` | 135 |
| `Strike` | 116 |
| `AdjustModifier` | 93 |
| `AdjustStrike` | 49 |
| `DamageAlteration` | 49 |
| `Aura` | 23 |
| `EphemeralEffect` | 22 |
| `RollTwice`, `SubstituteRoll`, `TokenLight`, `TokenEffectIcon` | 18 |

Mais 206 `ActiveEffectLike` em `flags.*` -- contadores internos do Foundry
(`flags.system.hellknightArchetype.featCount`), sem correspondente em ficha.

### Nao modelados -- estes sim derrubam `mechanized`

Apenas **27 feats**, distribuidos em ~30 caminhos distintos de
`ActiveEffectLike`, quase todos com 1 ou 2 ocorrencias:
`system.crafting.entries.*.maxSlots` (snarecrafter, talismanDabbler, cauldron,
gadgetSpecialist), `system.proficiencies.classDCs.<classe>.attribute`,
`system.details.ancestry.adopted`/`countsAs`,
`system.resources.investiture.max`, `system.attributes.hp.negativeHealing`, e
caminhos totalmente dinamicos do tipo
`{item|flags.system.rulesSelections.cannyAcumen}`.

Nenhuma chave de rule element ficou desconhecida: os 36 tipos presentes nos
feats do commit fixado estao todos classificados.

---

## 3. Vinculo feat -> arquetipo

**A fonte usada e o diretorio do Foundry**, `packs/pf2e/feats/archetype/<slug>/`
-- 244 pastas, 2.266 feats. E campo exato: a pasta e a chave, nao ha casamento
textual envolvido.

O campo `archetype` do AoN **nao** foi usado para o vinculo, e a medicao mostra
por que:

| | |
|---|---|
| feats que so o AoN atribui a um arquetipo | **538** |
| feats que so o diretorio do Foundry atribui | 77 |
| arquetipos com concordancia perfeita entre as duas fontes | 106 / 244 |

Inspecionando os 538: o campo `archetype` do AoN significa *"acessivel por meio
deste arquetipo"*, nao *"pertence a este arquetipo"*. Exemplos verificados:

- `martial-artist`: 9 feats na pasta do Foundry, 32 no campo do AoN. Os 23 a
  mais sao feats de Monge (`Crane Stance`, `Dragon Roar`, `Brawling Focus`) com
  `trait: ["Monk"]` -- o arquetipo Martial Artist da acesso a elas, elas nao sao
  dele.
- `blessed-one`: os 10 a mais sao mercies de Campeao (`Greater Mercy`,
  `Affliction Mercy`), todas com `trait: ["Champion"]`.
- `archer`: os 12 a mais sao feats de Guerreiro/Patrulheiro (`Double Shot`,
  `Crossbow Ace`).

Usar o campo do AoN colocaria 538 feats de classe dentro das listas de arquetipo
do construtor. E exatamente a contaminacao prevista no briefing, medida.

Os 77 do outro lado sao, na maioria, falha de casamento de nome entre as fontes
(`Define "Report"` com aspas curvas no AoN) e nao arquetipos ausentes.

### Validacao cruzada independente

Usando o traco `archetype` do proprio AoN como terceira testemunha:

| | |
|---|---|
| feats com traco `archetype` | 2.150 |
| destas, com vinculo pelo diretorio | 2.067 (96,1 %) |
| **sem** vinculo | 83 |
| com vinculo mas sem o traco no AoN | 199 |

Os 83 sem vinculo sao feats que existem no AoN/pf2etools e nao estao na arvore
de arquetipo do Foundry (`Advanced Bow Training`, `Cascade Bearers Flexibility`)
-- conteudo majoritariamente legado. Os 199 do outro lado sao feats de arquetipo
cujo traco no AoN traz a classe em vez de `Archetype` (`Abjure Harm`,
`Apocalypse Rider Dedication`).

Arquetipos emitidos: 248 = 247 nomes distintos no AoN (de 336 documentos, o
resto e par legado/remaster) unidos as 244 pastas do Foundry. 244 tem pelo menos
uma feat associada.

---

## 4. Divergencias entre fontes

### Registradas em `conflitos` (543 registros)

| campo | registros | leitura |
|---|---:|---|
| `traits` | 503 | quase todo o volume e o AoN carregando tracos que o Foundry guarda em outro campo (`general`, `skill`) ou nome de ancestralidade legado vs remaster (`gnoll`/`kholo`, `grippli`/`tripkee`). A raridade, que o AoN tambem mistura em `trait`, ja e removida na normalizacao -- so isso derrubou os conflitos de 1.334 para 503 |
| `level` | 46 | divergencia real de nivel. Ex.: `Animal Elocutionist` foundry 1 / pf2etools 5 / aon 5; `Chemical Contagion` foundry 18 / outros 16. Vence o Foundry conforme a spec, e o conflito fica no registro. Portao de qualidade 2 satisfeito |
| `rarity` | 7 | ruido |

### Divergencia no texto de pre-requisito (nao vira `conflitos`, e informativa)

2.866 feats tem pre-requisito nas duas fontes com texto. Depois de remover as
tags e a pontuacao, **85,1 % sao equivalentes**. As 428 diferencas caem em
padroes claros:

| tipo | exemplo |
|---|---|
| Foundry escreve modificador, pf2etools escreve valor | `Strength +2` vs `Strength 14` (o parser converte: `+N` -> `>= 10+2N`) |
| pf2etools esta mais atualizado | `Ruffian Rogue` (Foundry) vs `ruffian racket` (pf2etools) |
| o Foundry perde a marcacao de Lore | `trained in Elven Lore or Society` vs `{@skill Lore\|\|Elven Lore}` |
| conteudo genuinamente diferente entre edicoes | `Jalmeri Heavenseeker Dedication`: Foundry pede `Student of Perfection Dedication`, pf2etools pede `expert in unarmed attacks` |

48 feats tem pre-requisito so no Foundry, 33 so no pf2etools.

Isso confirma a precedencia da spec: pf2etools vence em `requires`, e nao so
pela marcacao -- vence tambem em atualidade.

---

## 5. `mechanized`

`mechanized = requires_ok AND nenhum rule element relevante para ficha ficou de fora`

| kind | true | false |
|---|---:|---:|
| feat | 5.808 | 613 |
| archetype | 181 | 67 |
| **total** | **5.989** | **680** |

Motivo dos 613 feats nao mecanizados:

| motivo | registros |
|---|---:|
| pre-requisito nao parseado | 594 |
| rule element nao modelado | 27 |

(a soma passa de 613 porque 8 feats tem os dois problemas)

Ou seja: **97 % do que impede mecanizacao e pre-requisito em prosa, nao efeito**.
O lado dos efeitos ja esta praticamente resolvido pelo Foundry.

---

## 6. Portoes de qualidade da spec

| portao | estado |
|---|---|
| 1. `prov` para todo campo preenchido | **passa** -- 0 campos sem proveniencia |
| 2. `level` divergente sem entrada em `conflitos` | **passa** -- 46 divergencias, 46 registradas |
| 3. `requires` cita `wb:` inexistente | **pendente por dependencia**: dos 3.256 `has` emitidos, 2.789 apontam para `wb:feat/*` que existe nesta saida; 2 nao existem (feat citada por outra que so aparece em fonte que ficou de fora da uniao). Os demais apontam para kinds que ainda nao tem extrator: 335 `wb:class-feature/*`, 101 `wb:heritage/*`, 28 `wb:spell/*`, 1 `wb:archetype/*`. O portao so pode ser avaliado com a base completa |
| 4. cobertura menor que o build anterior | n/a -- primeiro build |
| 5. `license` ausente | **10 registros**, todos arquetipos sem feat de Dedication no Foundry e cujo livro nao aparece na tabela livro->licenca (`Hellknight Armiger`, `Gray Gardener`, `Gelid Shard`, `Splinter of Finality`, `Drow Shootist`, ...). Os outros 6.659 tem licenca: 4.378 ORC, 2.281 OGL |

A tabela livro -> licenca **nao** foi escrita a mao: e deduzida do proprio
Foundry (`publication.title` -> `publication.license`) e, para as siglas do
pf2etools (`PC1`, `LOCG`, `CRB`), por cruzamento -- a mesma feat presente nas
duas fontes vota na licenca da sigla. Isso reduziu os registros sem licenca de
266 para 10.

---

## 7. Decisoes tomadas neste extrator

1. **Predicado e tudo-ou-nada.** Um `requires` parcialmente correto engana o
   construtor pior do que um `requires` ausente com o texto do lado.
2. **Nenhum `wb:` id inventado para nome nao resolvido.** `tenets of good` fica
   sem predicado em vez de virar `wb:class-feature/tenets-of-good`, que
   quebraria o portao 3 silenciosamente.
3. **Vinculo de arquetipo sai de estrutura de diretorio, nao de campo textual.**
   Medido: a alternativa contamina 538 feats.
4. **Rule element de mesa nao conta contra `mechanized`.** `RollOption` e
   `AdjustDegreeOfSuccess` nao mudam a ficha. Contar como perda esconderia os 27
   casos que sao perda de verdade.
5. **`+N` do Foundry vira valor de atributo.** `Strength +2` e `Strength 14` sao
   o mesmo pre-requisito escrito por fontes diferentes; a base guarda um so.
6. **Raridade sai da lista de tracos do AoN.** E campo proprio no schema;
   mante-la nos dois lugares gerava 831 conflitos falsos.
7. **Homonimo resolve pelo remaster.** Coerente com a regra de slug da spec.

## 8. Como reexecutar

```bash
cd /home/igor0/Tartarus/Projetos/pessoal/waybuilder
python3 pipeline/extratores/feats.py
```

O modulo e stdlib pura. Localiza os packs do Foundry em, nesta ordem:
`$WB_FOUNDRY_PACKS`, `pipeline/dados_brutos/foundry/packs/pf2e`, e o clone fixado
do ambiente de pesquisa. pf2etools e AoN saem de `pipeline/dados_brutos/`.
`extrair()` devolve a lista de registros; `main()` grava
`saida/feats.json` e `saida/_feats_estatisticas.json`.
