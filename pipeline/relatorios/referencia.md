# Relatorio -- extrator `referencia.py` (trait, skill, deity, domain)

Gerado por `pipeline/extratores/referencia.py`. Saida: `pipeline/saida/referencia.json`
(1144 registros, 1,18 MB). Rodar: `python3 pipeline/extratores/referencia.py`.

## Contagem por kind

| kind   | bruto AoN | homonimos (legado x remaster) | registros finais |
|--------|-----------|--------------------------------|-------------------|
| trait  | 907       | 346                             | 561               |
| skill  | 50        | 17                               | 33                |
| deity  | 717       | 231                              | 486               |
| domain | 124       | 60                                | 64                |
| **total** |        |                                   | **1144**          |

Os numeros "907/50/717/124" batem exatamente com o volume medido antes da
tarefa. A diferenca pro registro final e dedup legado->remaster (mesmo
criterio de `feats.py`: quando um par tem `remaster_id`/sem ele, fica so a
versao remaster).

`skill` merece nota: dos 50 documentos brutos, 17 sao as pericias nucleares
(Acrobatics..Thievery, cada uma duplicada legado+remaster) e **16 sao
exemplos de Lore** (Agriculture, Boating, Warfare...) publicados no Kingmaker
Adventure Path como entradas catalogaveis -- nao sao pericias novas, sao
instancias de "Lore: <tema>". Ficam no registro com `"lore": true` e sem
`attribute`, distintas das 17 pericias nucleares (`"lore": false`).

## Traits: mecanica estruturada vs descritivo

**0 de 561 traits tem significado mecanico estruturado** nas fontes
consultadas. Verificado dois lugares:

1. **AoN** carrega os campos `resistance`/`weakness`/`speed`/`skill_mod` no
   schema compartilhado de todas as categorias do Elasticsearch -- mas para
   `category: trait` esses 4 campos vem `{}` em **100%** dos 907 documentos
   brutos. Confirmado por varredura completa, nao amostragem.
2. **Foundry** (`src/scripts/config/traits.ts`) e so um dicionario
   slug -> rotulo em ingles. Sem `publication`, sem rule element, sem
   predicado. Trait no Foundry e tag pura -- a mecanica mora em quem *tem* o
   trait (uma spell com trait `fire` que causa dano de fogo), nunca no
   registro do trait em si.

Isso e esperado e consistente com o Principio Zero: trait e vocabulario
compartilhado, nao unidade de execucao.

O que existe de estrutura e **taxonomia**, nao mecanica: 541/561 (96,4%)
trazem `trait_group` (ex.: "Ancestry", "Weapon", "Alignment", "Monster",
"Mechanics") -- serve pra agrupar/filtrar na UI, nao pra calcular nada. Fica
gravado como campo extra `trait_group` no registro, fora do envelope padrao.

## Cobertura de deity

| campo estruturado | cobertura |
|---|---|
| `divine_attribute` | 480/486 (98,8%) |
| `divine_font` | 479/486 (98,6%) |
| `domains` (primary+alternate) | 479/486 (98,6%) |
| `favored_weapon` | 479/486 (98,6%) |
| `sanctification` | 374/486 (77,0%) |
| **triplice completa** (attribute + font + domains, o minimo pro Clerigo/Campeao na criacao) | **476/486 (97,9%)** |
| `edict` / `anathema` (texto, nunca predicado) | 486/486 (100%) |

As ~10 deidades sem a triplice completa sao entradas de lore/NPC (deidades
menores, cultos, entidades sem clero jogavel) -- AoN as cataloga mas nao
preenche font/domain porque nao existe regra de Clerigo pra elas.
`sanctification` (holy/unholy) e o campo mais incompleto: falta em ~110
deidades, a maioria publicada antes do remaster introduzir o conceito.

`edict` e `anathema` ficam como **texto puro** no registro (`reg["edict"]`,
`reg["anathema"]`), nunca dentro de `requires`. Igual `alignment` e
`area_of_concern`. E o Principio Zero aplicado: contexto pro jogador, a mesa
resolve.

## `license`/`remaster`

Nenhuma das 4 categorias tem `license` direta no AoN nem item proprio no
Foundry com `publication` em volume -- a excecao e `packs/pf2e/deities/`
(so ~51 arquivos, mas casa por NOME exato, mais preciso que titulo de livro).

Estrategia em duas camadas:
1. **Deity por nome**: cross-referencia direta com `packs/pf2e/deities/*.json`
   -- 471/486 deidades pegaram license assim (`prov.source =
   "foundry(deities, por nome)"`).
2. **Todo o resto por titulo de livro**: tabela `livro -> (license, remaster)`
   construida varrendo `feats`, `spells`, `equipment`, `deities`, `hazards`,
   `actions`, `class-features`, `ancestries`, `backgrounds` do Foundry (195
   titulos distintos). Achei e corrigi uma armadilha de normalizacao: o
   Foundry prefixa titulo com "Pathfinder " (`"Pathfinder Player Core"`), o
   AoN nao (`"Player Core"`) -- sem strip do prefixo, 1109/1144 registros
   ficavam sem license; com o strip, caiu pra **135/1144 (11,8%)**.

Os 135 restantes sao livros de nicho que nenhum dos packs varridos cobre:
Kingmaker Adventure Path (44, majoritariamente os exemplos de Lore),
Divine Mysteries (27, parcial -- so a parte sem match no pack `deities`),
Bestiary 3 (10), Dark Archives Remastered (9), Ancestry Guide (8), Tian Xia
Character Guide (7), The Mwangi Expanse (5), Season of Ghosts (5), Gods &
Magic (5), e uma cauda longa de 1-3 registros cada. Portao de qualidade #5 da
spec (`license` ausente derruba o build) vai falhar pra esses 135 ate
alguem varrer mais packs do Foundry ou aceitar `license: null` como
gap conhecido.

## Traits orfaos

**0 traits orfaos.** Cruzei os 282 slugs de trait citados pelos extratores
irmaos ja rodados (`feats.json`, `magias.json`, `ancestrias.json`,
`classes.json`, `conjuracao.json` -- `equipamento.json` e `companheiros.json`
ainda nao existiam no momento desta extracao, entao nao entraram na
contagem) contra os 561 slugs desta extracao: **todos os 282 resolvem**.
Sinal de que a cobertura de trait do AoN e suficiente pro que ja foi
extraido. Vale rerodar essa checagem quando `equipamento.py` e
`companheiros.py` terminarem.

## pf2etools (terceira opiniao)

Nao contribuiu campo nenhum -- pela tabela de precedencia da spec,
name/traits/rarity/source/text ja sao AoN, e nenhuma das 4 categorias tem
`requires` (papel do pf2etools) nem rule element proprio (papel do
Foundry). Usado so pra checagem cruzada de nomes:

| kind   | nomes no pf2etools | so no pf2etools | so no nosso (AoN) |
|--------|---------------------|-------------------|---------------------|
| trait  | 471                 | 34                | 124                 |
| skill  | 18                  | 1                 | 16                  |
| domain | 61                  | 0                 | 3                   |
| deity  | 272                 | 7                 | 221                 |

pf2etools e sistematicamente menos completo (esperado -- e projeto
comunitario, nao a fonte oficial). Os "so pf2etools" (34 traits, 7 deities)
nao foram investigados nome a nome por tempo -- ficam como pendencia, mas
sao poucos o suficiente pra nao mudar a decisao de nao mergear.

## O que nao consegui mapear

1. **`license` em 135/1144 registros (11,8%)** -- livros de nicho fora dos
   packs Foundry varridos (ver secao acima). Nao tentei mais packs
   (bestiaries especificos de AP, por exemplo) por tempo.
2. **34 traits e 7 deities exclusivos do pf2etools** -- nomes nao
   cruzados individualmente contra o AoN; podem ser variantes de grafia ou
   conteudo genuinamente ausente no AoN.
3. **`domain_spells`, `favored_weapon`, `cleric_spell` como `wb:spell/*` e
   `wb:equipment/*`** -- gerados por slugificacao do nome, **sem validar**
   se o id resolve contra `magias.json`/`equipamento.json` (equipamento
   ainda nem existia). Essa validacao e o portao de qualidade #3 da spec
   ("um `requires` cita `wb:` id que nao existe") e cabe rodar depois que
   todos os extratores irmaos tiverem terminado.
4. **Mecanica propria de trait**: decisao consciente de nao inventar, ver
   secao "Traits: mecanica estruturada vs descritivo".

## `conflitos`

Zero registros com `conflitos`. Nao e por falta de checagem -- e porque as
4 categorias colapsam pra fonte unica (AoN) em todo campo de conteudo pela
propria tabela de precedencia da spec; Foundry/pf2etools so entraram pra
completar `license` (que e um preenchimento de lacuna, nao uma segunda fonte
de conteudo divergente).
