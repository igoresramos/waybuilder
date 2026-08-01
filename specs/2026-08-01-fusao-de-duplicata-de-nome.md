---
spec: fusao-de-duplicata-de-nome
req: WB-075
project: waybuilder
version: 2
status: implementada
created: 2026-08-01
altera: [WB-002]
todo: 84
revisao: adversarial (fable, 2026-08-01) -- 10 mudancas obrigatorias incorporadas
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

## A regra que a triagem propos casa ZERO

A triagem propos, textualmente: *"quando dois candidatos tem MESMO
`book`+`page`+`level`+`traits` e o nome de um e o nome do outro +/-
'Dedication', tratar como o mesmo feat"*.

Rodada contra a base, essa regra casa **0 pares** -- inclusive os 7 que a
propria triagem documentou. A causa e um campo so: **o lado Foundry nunca tem
numero de pagina.** Medido: **0 de 1.073** registros so-foundry tem
`source.page` preenchido. Exigir igualdade de `page` entre um lado aon e um lado
foundry e exigir algo que nao pode acontecer.

## A medicao que decide o desenho

Varredura da base inteira (20.125 registros), exigindo que um lado tenha **so**
`xref.aon` e o outro **so** `xref.foundry`:

| filtro | pares |
|---|---:|
| bloco por `(kind, book, level)` + `traits` iguais + `page` compativel + nome quase-identico | 57 |
| -- com parenteses em algum dos lados | 5 |
| -- **fundiveis** (52 sem parenteses + 1 com parentese identico) | **53** |

O bloco por `(kind, book, level)` substitui o bloco por prefixo de 4 caracteres
da v1. Os filtros ja exigiam `book` e `level` iguais, entao o bloco novo nao
custa nada e captura pares que divergem no COMECO do nome, invisiveis para o
prefixo:

- `Lurching Chomp` / `Luring Chomp`
- `Eye of the Moonwarden` / `Eyes Of The Moonwarden`
- `Comandant's Scabbard` / `Commandant's Scabbard`
- `Fautless Defense` / `Faultless Defense`

Dois desses tem `grants` so no lado Foundry -- exatamente o defeito de mecanica
que esta spec existe para consertar.

**O bloco nao e detalhe de implementacao, e parte da regra.** Sem ele, a regra
literal (distancia de edicao <= 3) funde **8 divindades em `Norns`** -- Gorum,
Torag, Horus, Kols, Cong, Onos, Zohls e Lorris, todas de Divine Mysteries, todas
com `level: None` e `traits: []`, todas com `page` nula do lado Foundry. Nomes
curtos tornam a distancia 3 catastrofica.

A exclusao por parenteses protege os 318 irmaos que o `desmembrar_colisoes.py`
criou de proposito. Sem ela a regra funde `Silence the Profane` com
`(Avenger)` **e** com `(Vindicator)`. **Excecao:** quando o conteudo do
parentese e identico normalizado dos dois lados, o parentese nao esta
desambiguando nada -- e o caso de `Submersible Helm (Greater)` /
`Submersible Helmet (Greater)`, irmao graduado de um par que a regra ja funde.

## A regra

Dois registros sao o **mesmo registro real** quando, ao mesmo tempo:

1. mesmo `kind`, mesmo `source.book`, mesmo `level` (o bloco);
2. um tem so `xref.aon` e o outro tem so `xref.foundry`;
3. `traits` identicos;
4. `source.page` compativel -- iguais, ou pelo menos um dos dois nulo;
5. parenteses: nenhum dos dois nomes tem, **ou** os dois tem conteudo de
   parentese identico apos normalizacao;
6. os nomes normalizados diferem por **uma** destas formas:
   - so espaco/pontuacao (`Flash Forge` = `Flashforge`);
   - uma palavra a mais, e essa palavra e `the`, `of` ou `dedication`;
   - distancia de edicao <= 3.

### A guarda estrutural (contra o futuro, nao contra a base de hoje)

Nenhum dos 53 pares de hoje e falso positivo -- conferi um a um contra o dump do
AoN, e em todos o nome do lado Foundry **nao existe** no AoN. Mas a seguranca e
acidental: medidos no dump, existem **39 pares de entidades DISTINTAS** que
passariam em todos os filtros acima, entre eles `Goblin Lore` / `Goblin Song`,
`Basic Devotion` / `Basic Deduction`, `Quick Climb` / `Quick Swim` e -- o pior --
**`Eagle Eye` / `Eagle Eyes`** (`feat-8725` e `feat-8770`, dois feats reais que o
plural distingue). Hoje nenhum esta no estado so-aon/so-foundry, por isso a regra
nao erra. Como isto vira etapa permanente do `build.sh`, uma re-extracao futura
basta para armar a mina.

**Guarda:** vetar a fusao se o nome do lado Foundry existir como doc DISTINTO no
dump do AoN da mesma categoria. Se o AoN conhece os dois nomes, sao duas coisas.

## A politica de fusao

Nenhum lado e descartado inteiro -- principio 4 ("nada e descartado").

| campo | destino |
|---|---|
| `name` canonico | ver "o voto de terceira fonte", abaixo |
| `aliases` | recebe o nome perdedor **e** os `aliases` preexistentes dos dois |
| `xref` | uniao |
| `grants` | do lado que tiver; se so um tem, herda dele |
| `text` | do canonico; **a prosa do perdedor vai para `conflitos`** |
| `requires` | do canonico; se divergirem, o do perdedor vai para `conflitos` |
| `rarity`, `source.remaster` | do canonico; divergencia registrada em `conflitos` |
| `prov` | vira lista com as duas proveniencias |
| `historico` | concatenado |
| `id` | slug do nome canonico |

### Re-apontamento -- sem isso a fusao QUEBRA a base

O id perdedor nao pode simplesmente sumir. `wb:feat/knight-vigilant-dedication`
e citado em `requires` por **23 registros** (`wb:feat/aegis-of-arnisant`,
`wb:feat/body-barrier`, `wb:feat/divine-healing`, `wb:feat/emissary-of-peace`,
...). Apagar sem re-apontar cria 23 `requires` orfaos novos e regride o portao 3
de 23 para 46.

**Toda citacao do id perdedor em `requires` e `grants` de qualquer registro passa
a citar o canonico.** A fusao so e valida se, apos o passo, a contagem de
referencias orfas nao subir.

### Grants dos dois lados

Medido: **3 pares** tem `grants` nos dois lados. Um e identico (`knight-vigilant`,
trivial). Os outros dois sao backgrounds onde divergem de verdade
(`post-guard-of-all-trade`, `reclaimed-investigator`: o lado Foundry tem
`ability_boost` que o lado AoN nao tem) -- e para background o `ability_boost` e
a mecanica inteira do registro. **Regra: uniao dos grants; se a uniao produzir
duas entradas do mesmo tipo com valor diferente, ficam as duas e o par vai para
`conflitos` marcado `REVISAR`.** Nao arbitrar em silencio.

### O voto de terceira fonte -- o nome canonico NAO e sempre o do AoN

A v1 dizia "canonico = nome do lado AoN, porque bate com a Paizo". **Falso numa
fracao relevante:** o dump do AoN carrega typo em `Exemplar Resilency`,
`Historical Reeanactor`, `Camoflage Coat`, `Certain Strategem`,
`Repulse the Wicken`, `Flash of Omipotence`, `Vengful Remnant`,
`Orator's Fillibuster`, `Mythic Resilent`, `Sack of Hyrdra's Teeth` -- cerca de
10 dos 53. Canonizar o AoN nesses casos promove o typo e manda a grafia correta
para alias. A propria tabela da triagem chama o lado Foundry de "nome certo" em
tres deles.

**Regra de desempate, nesta ordem:**

1. se `pf2etools` conhece um dos dois nomes e o outro nao, **o nome que ele
   conhece vence** (terceira fonte independente);
2. se pf2etools nao desempata, vence o nome do lado **AoN**;
3. o perdedor sempre vira alias -- a grafia errada continua buscavel.

Correcao de fato da v1: dos 5 pares em que so um lado tem mecanica, **os 5 tem a
mecanica no lado Foundry**, nao 2. Escolher um lado inteiro perderia mecanica em
5 casos.

## A familia separada -- Legacy <-> Remaster com nivel divergente

O oitavo defeito (`Deepest Wellspring` -> `Amp Focus`) nao e desta familia. E
fusao Legacy/Remaster que a AoN declara (`remaster_id`/`legacy_id`) e que
`fundir_renomeados.py` vetou porque o `level` diverge (18 x 12).

A triagem propos dispensar o veto de nivel sempre que o par vier de
`remaster_id` explicito. **Seria destrutivo:** em equipamento, `Tanglefoot Bag`,
`(Moderate)`, `(Greater)` e `(Major)` apontam **todos** para o mesmo
`Glue Bomb` nv1 -- fundir colapsaria quatro itens distintos num so.

**A excecao vale so para `kind: feat`.** Sao ~31 pares (a v1 dizia 34; refazer a
contagem com o script versionado e registrar o numero no relatorio).

**Segunda guarda, obrigatoria:** dispensar o veto de nivel **somente quando o
nivel de cada lado bate com o nivel do proprio doc do AoN que o `xref.aon`
aponta**. Em 4 pares isso nao acontece -- `guardians-deflection` (nossa base
nv6, doc `feat-6147` nv4), `improved-familiar` (nv4 x doc nv6),
`predictive-purchase` (nv8 x doc nv6), `implausible-purchase` (nv18 x doc nv16).
Nesses a divergencia de nivel e sintoma de **casamento contaminado** (familia do
portao 7), e o veto de hoje e o unico alarme que os expoe no
`relatorio_fusao.md`. Fundir por cima apagaria o alarme.

Os N->1 sao reais e ficam: `feat-6044 Grandmaster Qi Spells` declara
`legacy_name: ["Medusa's Wrath", "Quivering Palm"]`, `feat-4995 Witch's
Armaments` declara `["Living Hair", "Eldritch Nails"]`. Consolidacao da Paizo,
resolvida com **dois aliases no mesmo registro**.

## O que esta spec NAO resolve, e declara

- Os pares com parenteses DIFERENTES ficam como estao (desambiguacao
  deliberada).
- `equipment`, `spell` e afins na fusao Legacy/Remaster ficam fora; so `feat`
  ganha a excecao de nivel.
- **Os 12 orfaos so-Foundry** cujo nome e o prefixo de irmaos desmembrados
  (`wb:feat/animal-empathy` -> `animal-empathy-druid`, `wb:feat/dueling-parry` ->
  `dueling-parry-fighter`, ...) sao o mesmo defeito de dois botoes e **nao** sao
  tratados aqui: exigem casar contra um irmao, nao contra um gemeo. Vira item de
  TODO proprio.
- Os 4 pontos do balde (d) da triagem (`Major Lesson`, os 3 `Syu Tak-Nwa's`) sao
  limite do comparador -- entram em `equivalencias-pathbuilder.json`, arquivo
  que esta spec nao toca.
- Os 31 pontos de recorte de fonte (Hell's Destiny, blog da Paizo) nao sao
  defeito: o Pathbuilder nao carrega esses livros.

## Como se prova que funciona

1. **Lista nominal.** O passo emite `relatorio_duplicata_de_nome.md` com os N
   pares fundidos, nome a nome, vencedor e motivo do desempate. Contagem de
   registros sozinha nao prova nada -- 53 fusoes ERRADAS tambem mudam a
   contagem.
2. Os 7 defeitos nomeados pela triagem somem da bancada do Pathbuilder;
   `Knight Vigilant` deixa de aparecer nas 14 classes (era 14 dos 56 pontos).
3. `Voice of the Elements` e `Automatic Psychic Action` mantem os `grants` do
   lado Foundry (7 e 1). Falha se sairem com `grants: []`.
4. Busca por `Vermillion Threads` (grafia errada) continua achando o registro
   via `aliases` -- o comparador ja consulta `aliases`
   (`motor/comparar_pathbuilder.py:246`).
5. **Zero referencias orfas novas:** a contagem de `requires` apontando para id
   inexistente nao sobe. Especificamente, os 23 citadores de
   `knight-vigilant-dedication` passam a citar `knight-vigilant`.
6. **Portoes com baseline numerica.** `portoes.py` tem **11** portoes, e dois
   falham hoje. O criterio nao e "continuam passando", e: portao 3 **<= 23**,
   portao 6 **<= 1**, os outros nove passam.
7. Nenhum par com parentese DIFERENTE e tocado: `Silence the Profane`,
   `(Avenger)` e `(Vindicator)` seguem tres registros.
8. As 20 fichas de exemplo derivam identicas em Python e TS.
