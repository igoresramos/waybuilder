---
title: Normalizacao de traits -- legado/remaster e familias parametrizadas
data: 2026-07-26
status: parcial
---

# Normalizacao de traits

Mapas produzidos para a regra "`traits` e uniao, nao precedencia"
(`specs/2026-07-26-schema-base.md`). Saida em
`pipeline/normalizacao_traits.json`.

Fontes usadas: base propria (561 registros `kind:"trait"` em `index.json`),
Archives of Nethys via Elasticsearch (`https://elasticsearch.aonprd.com/aon/_search`,
com `User-Agent` e `track_total_hits`), busca web para confirmar casos sem
link estrutural no AoN, e o clone do Foundry pf2e travado no commit
`87f9e5028baaa10b70fdc766260b7886def17e04` (mesmo commit fixado na spec),
arquivo `src/scripts/config/traits.ts`.

## Resumo

| Mapa | Entradas confirmadas |
|---|---|
| `renomeados` | 17 |
| `removidos_sem_sucessor` | 9 |
| `familias_parametrizadas` | 18 |

## `renomeados` -- legado -> remaster

| Legado | Remaster | Registros afetados (traits atuais) | Prova |
|---|---|---|---|
| aasimar | nephilim | 25 | aon: pagina Nephilim (Player Core pg.78) -- trait nephilim "interchangeable" com aasimar |
| tiefling | nephilim | 29 | idem, "interchangeable" com tiefling |
| aphorite | nephilim | 7 | aon: "Other nephilim sometimes earn the names of aphorite or ganzi" |
| ganzi | nephilim | 4 | idem |
| ifrit | naari | 23 | aon: trait-870 (Naari, Monster Core 2, "descended from efreet") == descricao literal do antigo trait-301 (Ifrit, Bestiary 2) |
| metamagic | spellshape | 130 | aon: `remaster_id` trait-107 -> trait-513 |
| negative | void | 112 | aon: `remaster_id` trait-118 -> trait-510 |
| positive | vitality | 124 | aon: `remaster_id` trait-128 -> trait-509 |
| gnoll | kholo | 28 | aon: `remaster_id` trait-219 -> trait-758 |
| couatl | coatl | 0 | aon: `remaster_id` trait-298 -> trait-748 |
| petitioner | shade | 0 | aon: `remaster_id` trait-305 -> trait-692 |
| locathah | athamaru | 31 | aon: `remaster_id` trait-356 -> trait-741 |
| duergar | hryngar | 0 | aon: `remaster_id` trait-53 -> trait-626 |
| half-elf | aiuvarin | 7 | aon: `remaster_id` trait-85 -> trait-515 |
| half-orc | dromaar | 3 | aon: `remaster_id` trait-86 -> trait-516 |
| good | holy | 34 | web: guia oficial PFS de remaster (Lorespire/Paizo) -- "good... may now have the holy... trait" |
| evil | unholy | 20 | web: idem -- "evil traits may now have the... unholy trait" |

Os 10 pares com link `remaster_id`/`legacy_id` direto no AoN sao os unicos
achados por essa via em toda a varredura dos 907 registros `category:trait`
do AoN -- ou seja, a varredura estrutural completa so revelou 10 renomeacoes
"limpas". O resto (nephilim, naari, holy/unholy) veio de leitura de texto,
nao de campo estruturado.

**Correcao ao ponto de partida:** `good -> holy` e `evil -> unholy` sao
recomendacao de tema ("at a GM's discretion... may now have"), nao renomeacao
mecanica automatica 1:1 como as outras. Documentado assim mesmo porque e a
melhor correspondencia disponivel e bate com o objetivo da uniao (nao perder
o conceito legado).

## `removidos_sem_sucessor`

| Trait | Registros afetados | Prova |
|---|---|---|
| abjuration | 219 | aon: 124 spells com o trait, todas Core Rulebook (2019); zero em livro remaster |
| conjuration | 247 | aon: 140 spells, todas Core Rulebook; zero remaster |
| divination | 222 | aon: 159 spells, todas Core Rulebook; zero remaster |
| enchantment | 183 | aon: 162 spells, todas Core Rulebook; zero remaster |
| evocation | 368 | aon: 253 spells, todas Core Rulebook; zero remaster |
| necromancy | 240 | aon: 193 spells, todas Core Rulebook; zero remaster |
| transmutation | 307 | aon: 166 spells, todas Core Rulebook; zero remaster |
| lawful | 5 | web: guia PFS remaster -- alinhamento removido, sem trait sucessor citado (so good/evil viram holy/unholy) |
| chaotic | 6 | idem |

**Correcao ao ponto de partida:** das 8 escolas de magia listadas por Igor,
**`illusion` sobreviveu ao remaster** -- nao foi eliminada. Confirmado via
`aon:remaster_id` trait-92 (Illusion, Core Rulebook) -> trait-629 (Illusion,
Player Core pg.457, mesmo nome) e via busca de spells: `Illusory Disguise` e
`Veil` carregam o trait Illusion, e a pagina do trait remaster explica a
mecanica de disbelief ainda em vigor. So as outras 7 escolas
(abjuration/conjuration/divination/enchantment/evocation/necromancy/
transmutation) foram eliminadas sem sucessor.

`lawful`/`chaotic` tem uma excecao pontual: o relic "Azata's Grace"
(*Pathfinder #200*, 2024-03-27) ainda carrega o trait Chaotic mesmo pos-
remaster. Provavelmente conteudo de relic (mecanica narrativa a parte) nao
seguiu a limpeza padrao. Nao muda a conclusao geral -- mantido como
"sem sucessor".

## `familias_parametrizadas`

Derivadas por **casamento de prefixo contra a lista de 561 traits base**
(nunca por regex de remocao de sufixo -- ver spec). Fonte: Foundry
`traits.ts`, objetos `weaponTraits`, `shieldTraits` e `armorTraits`.

| Familia | Tipo | Variantes confirmadas |
|---|---|---|
| two-hand | dado | d6, d8, d10, d12 |
| fatal | dado | d8, d10, d12 |
| fatal-aim | dado | d10, d12 |
| deadly | dado | d4, d6, d8, d10, d12 |
| jousting | dado | d4, d6, d8, d10 |
| volley | numero | 20, 30, 50, 60 |
| scatter | numero | 5, 10, 15, 20 |
| capacity | numero | 2, 3, 4, 5 |
| hefty | numero | 2 (unica variante conhecida) |
| thrown | numero | 10, 15, 20, 25, 30, 40, 50, 60, 80, 100, 200 |
| shield-throw | numero | 20, 30 |
| reload | misto | 0, 1, 2, "1-min" |
| versatile | palavra | p, s, b, acid, cold, electricity, fire, force, mental, poison, sonic, spirit, vitality, void |
| integrated | composto | 1d6-b, 1d6-p, 1d6-s, 1d6-s-versatile-p |
| deflecting | palavra | bludgeoning, piercing, slashing, physical-ranged |
| attached | palavra | to-shield, to-crossbow-or-firearm |
| entrench | palavra | melee, ranged |
| launching | palavra | dart |

`versatile-p/s/b` confirmados tambem por uso real no AoN (Dagger, Morningstar,
Greatsword etc. carregam "Versatile" puro -- o AoN nao guarda o parametro no
proprio campo `trait`, so o Foundry guarda; e exatamente o motivo da regra de
absorcao existir). As variantes de energia de `versatile` (acid/cold/.../void)
so tem confirmacao via Foundry, nao apareceram em nenhuma busca de peca de
equipamento no AoN dentro do escopo verificado.

## Nao confirmado

### Renomeacoes hipotetizadas e derrubadas pela pesquisa

- **`oread`, `sylph`, `undine` NAO viram `naari`.** A hipotese inicial
  ("ifrit, oread, sylph, undine -> naari") estava parcialmente errada.
  Confirmado via `aon:MonsterFamilies.aspx?ID=595` (familia Geniekin,
  Monster Core 2, pg. 250): a familia lista **cinco membros irmaos**
  distintos -- Naari, Oread, Suli, Sylph, Undine -- cada um com nome
  proprio. `oread` e `suli` ate ganharam pagina de trait nova no Monster
  Core 2 (`remaster_id`/`legacy_id` linkado), mas **sob o mesmo nome**
  (nao houve troca). `sylph` e `undine` nem isso -- seguem usando o
  registro de trait antigo (Bestiary 2), sem pagina remaster propria, mas
  aparecem ativamente em "Sylph Sneak" e "Undine Hydromancer" (criaturas do
  Monster Core 2). So `ifrit` de fato trocou de nome para `naari`.

### Traits legado (remaster=false na base) sem sucessor confirmado

54 traits marcados `remaster: false` nos 561 registros `kind:"trait"` da
base nao tem `remaster_id`/`legacy_id` no AoN nem foram verificados
individualmente por falta de tempo/escopo. Nao entraram no mapa -- nem como
renomeados, nem como removidos -- porque incluir qualquer um dos dois lados
sem prova seria inventar:

```
anugobu, brutal, certain-kill, charau-ka, charm, circus, class, complex,
contingency, drow, drug, eidolon, evolution, formian, fulu, ghul, golem,
grimoire, grippli, hantu, harrow-court, herald, ikeshti, inevitable, kaiju,
legacy, litany, magus, morlock, oath, open, pervasive-magic, radiation,
range, saggorak, sea-devil, seugathi, shoony, skulk, social, spellheart,
sporeborn, spriggan, stamina, summoner, tandem, tattoo, telepathy,
true-name, universal-ancestry, vocal
```

Risco pratico baixo: o comportamento padrao do algoritmo de uniao (uniao
simples, sem essas entradas no mapa 1) trata cada um como trait valido
autonomo -- o que e o caso mais provavel (muitos, como `eidolon`, `drow`,
`magus`, `summoner`, seguem mecanicamente ativos hoje; a flag
`remaster:false` no registro parece refletir so que a *pagina* daquele
trait especifico nunca foi reemitida, nao que o conceito sumiu -- o mesmo
padrao visto em `sylph`/`undine`). Recomendo tratar como "nao mapeado =
mantido como esta" e so investigar sob demanda se aparecer conflito
categorico real (gate de qualidade 6 da spec vai pegar isso sozinho).

### Familias parametrizadas encontradas no Foundry mas fora do mapa

Presentes em `traits.ts` mas **nao confirmadas como traits pf2e catalogados**
(o repo clonado e compartilhado entre os sistemas Foundry `pf2e` e `sf2e` --
Starfinder 2e -- no mesmo arquivo de configuracao):

- `persona-*`, `professional-*`, `xenometric-android`, `entu-colony`,
  `gap-touched`, `solarian`, `witchwarper` -- claramente exclusivos de sf2e.
- `critical-corrosive/cryo/flame/plasma/shock/brawling/knife/mental/sonic`
  -- padrao de nomenclatura de armas de energia tipico de sf2e; so
  `critical-fusion` foi confirmado como trait pf2e real (kineticist,
  Rage of Elements, `aon:trait-402`).
- `boost-1dX`, `expend-N`, `resilient-N`, `tracking-N`, `area-burst-N` --
  sem pagina de trait correspondente no AoN (busca por nome no category
  `trait` nao retornou correspondencia limpa); podem ser tags internas de
  automacao do Foundry (ex.: `resilient-N` provavelmente auto-adicionado
  quando uma runa de resiliencia e aplicada) em vez de traits catalogados.
- `deadly-2d4/3d4/4d4/2d6/.../4d12` -- variantes de dado multiplicado, sem
  paralelo em arma pf2e conhecida (pf2e so usa `deadly-dN` simples); mesma
  suspeita de exclusividade sf2e.
- `reach-0/10/15/.../1000` -- busca no AoN por armas com trait "Reach"
  retornou so a forma pura (`Longspear`, `Glaive`, `Bo Staff`), nunca
  parametrizada. Nao incluido.
- `splash-10` -- ocorrencia unica no arquivo Foundry; busca por 265 itens
  com trait Splash no AoN so retornou a forma pura. Provavelmente excecao
  isolada, nao familia real. Nao incluido.

## Proximos passos sugeridos

1. Igor revisar a lista de 54 traits nao confirmados e decidir se algum
   precisa de investigacao dedicada antes do build rodar.
2. Se o build encontrar `traits` categoricamente disjunto (gate 6 da spec)
   envolvendo algum desses 54, isso e sinal de que a entrada precisa entrar
   no mapa -- tratar como descoberta guiada por dado real, nao suposicao.
