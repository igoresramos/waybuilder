---
spec: fusao-de-duplicata-de-nome
project: waybuilder
version: 1
status: rascunho
created: 2026-08-01
todo: 84
---

# Spec -- o mesmo registro da Paizo, duas grafias

## O que sobrou depois da triagem do item 84

A triagem dos 56 pontos "so no Waybuilder"
(`docs/medicoes/2026-07-31_triagem-57-so-nosso.md`) achou **8 defeitos-raiz** e
deixou os oito com "conserto proposto (nao aplicado)". Sete deles sao a mesma
causa:

> um extrator (AoN) e outro (Foundry) capturaram o **mesmo registro real da
> Paizo** com grafia de nome levemente diferente. `reconciliar.py` casa por slug
> do nome; como os slugs diferem, os dois nunca colidiram e **sobreviveram como
> registros independentes e independentemente selecionaveis**.

O efeito na ficha: o jogador ve DOIS botoes para a mesma coisa, e cada um ocupa
um slot de escolha, porque a base nao os declara mutuamente exclusivos.

A propria triagem declarou o que nao mediu (secao 8): "nao auditei a base
inteira atras de mais pares... e bem provavel que existam mais fora desta
amostra". Esta spec mede.

## A regra que a triagem propos casa ZERO

A triagem propos, textualmente: *"quando dois candidatos tem MESMO
`book`+`page`+`level`+`traits` e o nome de um e o nome do outro +/-
'Dedication', tratar como o mesmo feat"*.

Rodada contra a base, essa regra casa **0 pares** -- inclusive os 7 que a
propria triagem documentou. A causa e um campo so:

| campo | pares (de 394 candidatos) que batem |
|---|---:|
| `book` | 327 |
| `traits` | 301 |
| `level` | 294 |
| **`page`** | **0** |

**O lado Foundry nunca tem numero de pagina.** `wb:feat/knight-vigilant` (aon)
tem `page: 94`; `wb:feat/knight-vigilant-dedication` (foundry) tem `page: None`.
Exigir igualdade de `page` entre um lado aon e um lado foundry e exigir algo que
nao pode acontecer.

Segundo defeito da regra proposta: `+/- "Dedication"` cobre 1 dos 7 casos. Os
outros seis sao letra trocada (`Vermilion`/`Vermillion`), espaco
(`Flash Forge`/`Flashforge`), plural (`Whisper`/`Whispers of Warning`) e palavra
de ligacao (`Voice of (the) Elements`).

## A medicao que decide o desenho

Varredura da base inteira (20.125 registros), pareando por `kind` + 4 primeiros
caracteres do nome normalizado, exigindo que um lado tenha **so** `xref.aon` e o
outro **so** `xref.foundry`:

| filtro | pares | o que corta |
|---|---:|---|
| nome quase-identico (espaco, +/-1 palavra, distancia <= 3) | 394 | -- |
| + `book` e `level` iguais, `traits` iguais, `page` compativel | 200 | homonimo real de livro/nivel diferente |
| + nenhum dos dois lados tem parenteses | **40** | **desambiguacao deliberada** |

O terceiro filtro e o que mais importa. Sem ele a regra funde
`Silence the Profane` com `Silence the Profane (Avenger)` **e** com
`Silence the Profane (Vindicator)` -- o parentese ali e o desambiguador que o
`desmembrar_colisoes.py` criou de proposito (os 318 irmaos do README, item 3).
Fundir desfaria trabalho correto. Sao **160 dos 200** nessa condicao.

Os 40 seguros, por forma e por kind:

| forma | pares | exemplo |
|---|---:|---|
| letra trocada (d=1) | 22 | `Vermilion` / `Vermillion Threads` |
| espaco | 6 | `Flash Forge` / `Flashforge` |
| palavra de ligacao | 5 | `Voice of Elements` / `Voice of the Elements` |
| letra trocada (d=3) | 4 | `Automatic` / `Autonomic Psychic Action` |
| letra trocada (d=2) | 3 | `Armor` / `Armored Regiment Training` |

kind: `feat` 27, `equipment` 10, `background` 3.

**A regra pega os 7 defeitos conhecidos, e nenhum a menos.** Ela tambem mostra
que a ponta vista pela triagem (7, num recorte de 14 classes) era **um sexto** do
total: sao 40 na base inteira.

## A regra

Dois registros do mesmo `kind` sao o **mesmo registro real** quando, ao mesmo
tempo:

1. um tem so `xref.aon` e o outro tem so `xref.foundry`;
2. `source.book` identico e `level` identico e `traits` identicos;
3. `source.page` **compativel** -- iguais, ou pelo menos um dos dois nulo;
4. nenhum dos dois nomes contem parenteses;
5. os nomes normalizados (minuscula, sem pontuacao) diferem por **uma** destas
   formas:
   - so espaco/pontuacao (`Flash Forge` = `Flashforge`);
   - uma palavra a mais que e `the`, `of` ou `dedication`;
   - distancia de edicao <= 3.

## A politica de fusao

Nenhum dos dois lados e descartado inteiro -- principio 4 do projeto ("nada e
descartado"):

| campo | de onde vem |
|---|---|
| `name` canonico | do lado **AoN** (bate com a grafia da Paizo) |
| `aliases` | recebe o nome do lado Foundry |
| `xref` | **uniao** dos dois |
| `grants` | do lado que tiver; se so um tem, **herda dele** |
| `id` | o slug do nome canonico; o outro id e apagado |

A herança de `grants` nao e detalhe: em **5 dos 40** pares so um lado tem
mecanica, e em 3 deles e o lado de nome ERRADO que a tem.

| par | quem tem a mecanica |
|---|---|
| `Automatic` / `Autonomic Psychic Action` | o de nome errado (foundry, `Quickened`) |
| `Voice of Elements` / `Voice of the Elements` | o de nome errado (foundry, 7 grants) |
| `Exemplar Resilency` / `Exemplar Resiliency` | o de nome certo |
| `Historical Reenactor` / `Reeanactor` | o de nome certo |
| `Submersible Helm` / `Helmet` | o de nome certo |

Escolher um lado inteiro perderia mecanica em 2 casos e nome correto em 3.

## A familia separada -- Legacy <-> Remaster com nivel divergente

O oitavo defeito (`Deepest Wellspring` -> `Amp Focus`) **nao** e desta familia e
nao entra na regra acima. E fusao Legacy/Remaster que a AoN declara
explicitamente (`remaster_id`/`legacy_id`) e que `fundir_renomeados.py` vetou
porque o `level` diverge (18 x 12).

A triagem propos "permitir que `level` divirja quando o par vem de
`remaster_id` explicito". **Medido: isso atinge 269 pares, e seria destrutivo.**

| kind | pares com nivel divergente |
|---|---:|
| equipment | 208 |
| feat | 34 |
| item-bonus | 17 |
| spell | 7 |
| outros | 3 |

Os 208 de equipamento sao graduacao: `Tanglefoot Bag`, `(Moderate)`,
`(Greater)` e `(Major)` apontam **todos** para o mesmo `Glue Bomb` nv1. Fundir
colapsaria quatro itens distintos num so.

**Portanto a excecao vale so para `kind: feat`** -- 34 pares. Dentro deles, 5
destinos recebem mais de um legado (`Quivering Palm` e `Medusa's Wrath` viraram
ambos `Grandmaster Qi Spells`); isso e consolidacao real da Paizo e resolve-se
com **dois aliases no mesmo registro**, nao com dois registros.

## O que esta spec NAO resolve, e declara

- **Os 160 pares com parenteses** ficam como estao. Sao desambiguacao
  deliberada; se algum deles for duplicata de verdade, e outro item.
- **`item-bonus`, `spell` e `equipment` na fusao Legacy/Remaster** ficam fora.
  So `feat` ganha a excecao de nivel.
- **Os 4 pontos do balde (d) da triagem** (`Major Lesson`, os 3
  `Syu Tak-Nwa's`) sao limite do comparador, nao da base -- entram em
  `equivalencias-pathbuilder.json`, arquivo que esta spec nao toca.
- **Os 31 pontos de recorte de fonte** (Hell's Destiny, blog da Paizo) nao sao
  defeito: o Pathbuilder nao carrega esses livros.
- A varredura pareia por 4 primeiros caracteres. Par cuja divergencia esteja
  **nos 4 primeiros caracteres** escapa. Nao medi quantos seriam.

## Como se prova que funciona

1. Os 40 pares viram 40 registros; a base cai de 20.125 para **20.085**.
2. Os 7 defeitos nomeados pela triagem somem da bancada do Pathbuilder --
   `Knight Vigilant` deixa de aparecer nas 14 classes (era 14 dos 56 pontos).
3. `Voice of the Elements` e `Automatic Psychic Action` mantem os `grants` do
   lado Foundry (7 e 1, respectivamente) -- o teste falha se sairem com
   `grants: []`.
4. Busca por `Vermillion Threads` (grafia errada) continua achando o registro,
   via `aliases`.
5. Nenhum dos 160 pares com parenteses e tocado -- `Silence the Profane`,
   `(Avenger)` e `(Vindicator)` seguem tres registros.
6. Os nove portoes de `portoes.py` continuam passando.
7. As 20 fichas de exemplo derivam identicas em Python e TS.
