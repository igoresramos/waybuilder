---
projeto: waybuilder
tipo: auditoria
data: 2026-07-26
base_auditada: pipeline/base/index.json (18.176 registros, 21 kinds, 15,2 MB)
escopo: falhas sistematicas de modelagem visiveis na distribuicao, nao no caso a caso
---

# Auditoria ampla da base canonica

Pedido do Igor: "rever tudo, nao apenas o 20 e 21". Os dois achados ja conhecidos
(`traits` como precedencia, e colisao de identidade em `wb:<kind>/<slug>`) foram
lidos para calibragem e **nao** sao reencontrados aqui.

Metodo: perguntar de cada campo por que a distribuicao dele tem a forma que tem.
Toda afirmacao com numero saiu de query rodada sobre `index.json`, sobre os
`pipeline/saida/*.json` (estado pre-reconciliacao, onde os registros apagados
ainda existem), sobre o checkout do Foundry, ou sobre o Elasticsearch do
Archives of Nethys.

Ordenado por **impacto no dado emitido**.

---

## A1. A fusao Legacy<->Remaster apagou 597 registros, e ~65% deles eram entidades distintas

**Gravidade: critica. Perda de dado irrecuperavel a partir do artefato emitido.**

### O que e

`pipeline/fundir_renomeados.py` decide se dois registros sao "o mesmo conteudo
renomeado" comparando **apenas a prosa**: Jaccard de tokens >= 0,62 com pelo
menos 15 termos distintivos. Nenhum campo mecanico entra na decisao -- nem
`level`, nem `price_cp`, nem `damage`, nem `traits`. Quando casa, o registro
OGL e **removido da base** (`final = [r for r in base if r["id"] not in absorvidos]`,
linha 94) e do lado remaster sobra so o nome, em `aliases`.

O relatorio de fusao afirma "**Nada e descartado**". O que nao e descartado e o
*nome*. Todo o resto do registro legado e.

### Quanto afeta

Base entrou com 18.773 registros e saiu com 18.176. **597 registros deletados.**

Duas medicoes independentes do erro:

**Medicao 1 -- campos mecanicos.** Reconstruindo cada par a partir de
`pipeline/saida/*.json` (os 597 legados ainda estao la; 597/597 localizados):

| criterio | pares |
|---|---|
| `level` do legado != `level` do alvo | 301 |
| `price_cp` diferente | 373 |
| `damage` diferente | 32 |
| **pelo menos um dos tres diferente** | **393 de 597 (65,8%)** |

**Medicao 2 -- arbitragem contra o AoN.** O AoN publica `remaster_id` /
`legacy_id`, que e o mapa oficial de renomeacao (11.353 docs com `remaster_id`,
11.905 com `legacy_id`). Amostra aleatoria de 60 dos 597 pares (seed fixa),
consultando o doc do nome legado e resolvendo o `remaster_id` dele:

| resultado | n |
|---|---|
| AoN confirma o par (`remaster_id` aponta para o alvo) | 21 (35%) |
| AoN diz que o legado **nao tem** `remaster_id` -- nunca foi renomeado | 28 |
| AoN aponta para **outro** alvo (em geral, para ele mesmo) | 11 |
| **nao confirmadas** | **39 de 60 (65%)** |

Controle da query: `Power Attack -> Vicious Swing`, `Attack of Opportunity ->
Reactive Strike` e `Bag of Holding -> Spacious Pouch` retornaram confirmados,
entao a consulta esta correta e o vazio significa ausencia real.

As duas medicoes convergem em ~65%. Projetado sobre os 597: **em torno de 390
fusoes indevidas**.

### Evidencia concreta

**Colapso de familia inteira.** 81 registros absorveram 2 ou mais legados:

- `wb:equipment/aeon-stone` absorveu **24** Aeon Stones distintas. Confirmado no
  AoN que continuam sendo entradas separadas com preco proprio:
  `Aeon Stone (Clear Spindle)` nivel 7 / 32.500 cp, `Aeon Stone (Orange Prism)`
  nivel 16 / 975.000 cp. Na base sobrou um unico registro de nivel 1 sem preco.
- `wb:equipment/wayfinder`: 14 wayfinders distintos.
- `wb:equipment/magic-wand`: as 9 varas por rank de magia.
- `wb:weapon/slide-pistol`: 10 legados, incluindo `Axe Musket (Melee/Ranged)`,
  `Cane Pistol`, `Dagger Pistol`, `Rapier Pistol` -- todas armas combinadas
  distintas de Guns & Gears.
- `wb:equipment/fossil-fragment`: os 7 tipos de fossil.
- `wb:equipment/duskwood-buckler-high-grade`: 7 legados, misturando Buckler,
  Shield e Tower Shield.

**Casamento entre entidades sem relacao nenhuma.** Verificado no AoN que ambos
os lados seguem existindo, com preco e livro proprios:

| absorvido | virou | veredito AoN |
|---|---|---|
| `Poi` (20 gp, PF #151) | `Shield Bash` | duas armas vivas, sem `remaster_id` |
| `Kris` (70 gp, Tian Xia CG) | `Main-gauche` (50 gp, Player Core) | idem |
| `Tonfa` (10 gp, TXCG) | `Shuan Ji` (300 gp, TXCG) | **mesmo livro**, sem vinculo |
| `Kalis` (300 gp, TXCG) | `Aldori Dueling Sword` | idem |
| `Thorn Whip` (60 gp), `Rhoka Sword` (400 gp), `Thundermace` (20 gp), `Spray Pellet`, `Bolts (Phalanx Piercer)`, `Exquisite Sword Cane Sheath` | `Gaff` (100 gp, Battlecry!) | seis armas distintas em uma |
| `Wooden Taws` (10 gp, Ancestry Guide) | `8-Round Magazine` (20 gp, TV) | similaridade 0,961 |
| `Atlatl` | `Blowgun` | ambos vivos |
| `Gada`, `Dandpatta`, `Elven Branched Spear`, `Talwar`, `Broadspear`, `Visap`, `Rungu` | armas do Player Core | todos vivos |
| `Clever Shadow`, `Cunning Hair`, `Skillful Tail (Ganzi)` | `Flexible Tail` | tres feats de nivel 5 do Ancestry Guide, distintos |
| `Evasion` (class-feature) | `Blast Dodger` | AoN lista 6 docs `Evasion` vivos |

Varios "legados" saem de livros **posteriores ao Remaster** -- Tian Xia
Character Guide (2024), Battlecry! (2025), Monster Core 2. Nao podem ser nome
antigo de nada.

**Variante de grau tratada como renomeacao.** `Universal Solvent (Greater/Major/
Moderate)` -> `Absolute Solvent`; `Camouflage Dye` -> `Camouflage Dye (Greater)`;
`Cryomister (Major)` -> `Cryomister (Lesser)`; `Soothing Powder` -> `Soothing
Powder (Greater)`; `Wind-up Wings` -> `Wind-up Wings (Flutterback)`. Aqui a
prosa e identica por construcao e o unico discriminante e o numero -- exatamente
o campo que o criterio ignora.

**Variante por classe tratada como renomeacao.** `Improved Familiar` (nv 4) ->
`Improved Familiar (Familiar Master)` (nv 6), similaridade 1,0. `Guardian's
Deflection` (nv 6) -> `Guardian's Deflection (Swashbuckler)` (nv 4). `Efficient
Alchemy` (nv 20) -> `Efficient Alchemy (Alchemist)` (nv 4). `Dueling Parry
(Fighter)` -> `Dueling Parry`. E o mesmo erro do achado 21, por outro caminho.

### Dano colateral rastreado

- **8 entradas de `progressao` de classe apontam para id inexistente**, e 5
  delas sao features destruidas por esta fusao: `wb:class-feature/evasion`,
  `greater-resolve`, `resolve`, `eidolon-weapon-specialization`,
  `armor-of-fury`. O grafo de progressao da classe quebrou.
- **597 chaves de prosa em `base/text/` ficaram orfas** -- o texto de
  `Aeon Stone (Dusty Rose Prism)` esta no arquivo e nenhum registro aponta para
  ele.
- 4 arquetipos (`cathartic-mage`, `dragon-disciple`, `magus`, `summoner`)
  perderam exatamente 1 feat cada em relacao a contagem do AoN, por absorcao.

### Recomendacao

**Reconciliador.** Trocar o criterio inteiro. O AoN ja publica o par
(`remaster_id`/`legacy_id`), e a propria spec escolhe o AoN para `source`
justamente por isso (linha 118 do schema). Fundir **so** com vinculo declarado
pela fonte. Prosa pode entrar como confirmacao, nunca como decisor. Enquanto
isso, tres guardas baratos que sozinhos matam a maior parte dos 393:

1. Bloquear fusao quando `level`, `price_cp` ou `damage` diferem.
2. Bloquear fusao N->1 (um alvo absorvendo 2+ legados).
3. Bloquear quando o legado sai de livro publicado depois do Remaster.

E parar de deletar o absorvido: manter o registro com `superseded_by`.

---

## A2. `mechanized` significa quatro coisas diferentes e nao significa o que a spec diz

**Gravidade: alta. Afeta 12.742 registros (70,1% da base).**

### O que e

A spec define: `mechanized: true` = "o app calcula pelos `grants`"; `false` = "so
exibe o texto". Medido na base:

| situacao | n | % da base |
|---|---|---|
| `mechanized: true` **e** `grants` vazio | **12.742** | 70,1% |
| `mechanized: false` **e** `grants` preenchido | **370** | 2,0% |

Ou seja: em 72% da base o campo contradiz a definicao. Um cliente que use
`mechanized` como a spec manda vai tentar calcular 12.742 registros que nao tem
o que calcular.

### Por que -- a distribuicao denuncia

O `false` nao esta distribuido por registro, esta distribuido por **kind
inteiro**: `trait` 561/561, `deity` 484/484, `animal-companion` 113/113,
`domain` 64/64, `familiar-specific` 38/38, `skill` 33/33, `apparition` 14/14,
`eidolon` 13/13 -- todos 100%. E `heritage` 79,1%, `class-feature` 72,1%.

Rastreado nos extratores, cada um calcula o campo com uma regra propria:

| extrator | regra usada |
|---|---|
| `feats.py:1264` | `requires_ok and not perdeu` (pre-requisito parseado + nenhum rule element fora do mapa) |
| `ancestrias.py:467,662` | literal `True` para background e ancestry |
| `ancestrias.py:542` | `(not rules) or all(k in mapped_keys ...)` |
| `companheiros.py:335` | literal `False` para todo animal-companion |
| `magias.py` / `_gerar_saida_magias.py` | "casou com o foundry" |
| `conjuracao.py:838` | declara explicitamente "nao aplicavel a este arquivo" |

Amostra de `feat` com `mechanized: false`: `wb:feat/absorb-spell`,
`absorb-toxin`, `accelerating-touch` -- todos com `requires` vazio e `grants`
vazio. Ali `false` quer dizer "nao consegui parsear o pre-requisito", que e uma
afirmacao sobre o **parser**, nao sobre o registro.

### Recomendacao

**Spec.** O campo esta carregando duas perguntas diferentes que precisam ser
dois campos: `grants_completos` (a mecanica de efeito foi convertida por
inteiro) e `requires_parseado` (o pre-requisito virou predicado). Um kind que
nunca produz `grants` -- trait, deity, skill -- nao deveria responder a primeira
pergunta com `false`, e sim com "nao se aplica". Depois disso, **extratores**:
todos passam a preencher os campos novos com a mesma definicao.

---

## A3. Divergencia entre fontes e silenciada em 6 kinds inteiros

**Gravidade: alta. 1.618 registros com 2+ fontes e zero divergencia registrada.**

### O que e

A spec: "`conflitos` so aparece quando as fontes discordam. Divergencia e
registrada, **nunca silenciada**." Medido, cruzando "quantos registros tem 2+
fontes reais em `xref`" contra "quantos tem `conflitos`":

| kind | com 2+ fontes | com `conflitos` | % |
|---|---|---|---|
| weapon | 896 | 654 | 73,0% |
| armor | 179 | 84 | 46,9% |
| shield | 111 | 47 | 42,3% |
| equipment | 3.552 | 916 | 25,8% |
| feat | 6.124 | 543 | 8,9% |
| spell | 1.637 | 53 | 3,2% |
| **class-feature** | **817** | **0** | **0,0%** |
| **background** | **330** | **0** | **0,0%** |
| **heritage** | **322** | **0** | **0,0%** |
| **familiar-ability** | **72** | **0** | **0,0%** |
| **ancestry** | **50** | **0** | **0,0%** |
| **class** | **27** | **0** | **0,0%** |

Zero exato em seis kinds nao e "essas fontes concordam". Feats saem das mesmas
tres fontes e divergem em 8,9% dos casos.

### Confirmado, nao so estatistico

Comparando `source.book` da base contra `system.publication.title` do Foundry,
depois de normalizar prefixo "Pathfinder", "Lost Omens" e variacao de grafia
(usando o proprio `normalizar_livro()` do pipeline):

| kind | divergencias reais de `source.book` | `conflitos` registrados |
|---|---|---|
| class-feature | 64 | 0 |
| background | 62 | 0 |
| heritage | 14 | 0 |
| ancestry | 3 | 0 |
| class | 2 | 0 |
| **total** | **145** | **0** |

Exemplos: `wb:class-feature/ability-boosts` -- Foundry diz Secrets of Magic, a
base emitiu Core Rulebook. `wb:class-feature/armor-expertise` -- Foundry Player
Core, base Player Core 2. `wb:class-feature/battle` -- Foundry Player Core 2,
base Player Core. `wb:ancestry/azarketi` -- Foundry "Absalom, City of Lost
Omens", base "Azarketi Ancestry Web Supplement".

### Causa

`reconciliar.py` so gera `conflitos` quando **dois arquivos de saida diferentes
colidem no mesmo id** (75 casos no build). A comparacao entre fontes acontece
dentro de cada extrator, e os extratores de `classes.py`, `ancestrias.py` e
`companheiros.py` escolhem sem registrar. Ha `conflitos` no codigo deles (grep:
11, 8 e 1 ocorrencias) mas nao para esses campos.

### Recomendacao

**Extratores.** A logica de escolha por precedencia + registro de divergencia
tem de sair de cada extrator e virar uma funcao unica compartilhada. Enquanto
estiver replicada em 7 arquivos, "nunca silenciada" nao e verificavel. Um portao
barato no reconciliador: se um kind tem >100 registros com 2+ fontes e **zero**
conflitos, falhar o build por suspeita de instrumentacao ausente.

---

## A4. Buracos de cobertura por kind, medidos contra o censo do AoN

**Gravidade: alta. Somando os quatro buracos: ~510 registros faltando.**

Censo por `category` no AoN (43.686 docs), descontando os que tem `remaster_id`
(ou seja: so o que ainda e a versao vigente), contra o tamanho do kind na base:

| kind | AoN vigente | base | delta |
|---|---|---|---|
| `ritual` | 145 | **0** | **-145** |
| `background` | 499 | 332 | **-167** |
| `relic` | 122 | 0 | **-116** (kind inexistente) |
| `language` | 117 | 0 | **-85** (kind inexistente) |
| `familiar-ability` | 142 | 132 | -10 |
| `spell` | 1.661 | 1.639 | -22 |
| `heritage` | 335 | 326 | -8 |
| deity / skill / class / eidolon / familiar-specific | 484 / 33 / 27 / 13 / 38 | identicos | 0 |
| domain / archetype / trait | 63 / 244 / 556 | 64 / 245 / 561 | +1 / +1 / +5 |

### background: -167 (33% do kind)

Confirmado por duas fontes independentes. O pack `backgrounds` do Foundry tem
514 arquivos; a base tem 332; 182 nomes do Foundry nao aparecem na base nem como
`aliases`. O AoN diz 168 ausentes, com a mesma assinatura: sao backgrounds de
Player's Guide de adventure path (Agents of Edgewatch 10, Age of Ashes 9,
Extinction Curse 9, Curtain Call 8, Seven Dooms for Sandpoint 8, Abomination
Vaults 7, Kingmaker 7...). Amostra: `Aerialist`, `Animal Wrangler`, `Barker`,
`Blow-In`, `Butcher`, `Dragon Scholar`, `Emancipated`, `Hellknight Historian`.

Background e escolha obrigatoria de ficha. Um terco do catalogo esta fora.

### ritual: 145, nao 31

TODO 17 registra "31 rituals confirmados ausentes (18 Player Core + 13 Player
Core 2)". O censo do AoN da **145 rituals vigentes**, 142 dos quais nao existem
na base sob nenhum nome. Player Core 17, Secrets of Magic 16, Player Core 2 13,
War of Immortals 13, Battlecry! 10. O escopo do item esta subdimensionado por
4,7x.

### relic e language: kinds que nao existem na spec

Aplicando a propria regra da spec ("se alguma regra do jogo consegue falar de um
e nao do outro, sao tipos diferentes"):

- **`relic`** (122 vigentes, 116 ausentes): item de jogador com trilha de
  progressao propria (gift/aspect). GM Core 70, Treasure Vault 23, Secrets of
  Magic 10. Nao entra em `equipment` -- tem estrutura distinta.
- **`language`** (117 vigentes, 85 ausentes): a ficha tem linha de idiomas.
  Hoje idioma so existe como string dentro do campo `languages` das 50
  ancestrias; nao ha entidade `language` para o personagem referenciar. Player
  Core 17, GM Core 9.

Mesma classe do achado do `ritual`: omissao ao escrever a lista de kinds.

### Recomendacao

**Spec** primeiro (adicionar `relic` e `language` a lista de kinds; corrigir o
numero de rituals no TODO 17), depois **extratores**. E adotar como pratica o
censo por `category` do AoN descontado de `remaster_id` -- foi o que achou tudo
isto em uma query; contar por `source.book` nao acharia nada (licao ja
registrada).

---

## A5. `source.book` sai da base com duas grafias para a mesma obra

**Gravidade: media-alta. 10.723 registros (59% da base) em livro de grafia ambigua.**

O TODO 11 aponta que `normalizar_livro()` roda depois da comparacao. O efeito
e maior do que isso: **o dado emitido carrega as duas grafias**. 250 valores
distintos de `source.book` colapsam para 223 chaves normalizadas; 26 obras
aparecem com 2 grafias:

| obra | grafias na base |
|---|---|
| Player Core | `Player Core` 2.032 / `Pathfinder Player Core` 83 |
| Player Core 2 | 1.772 / 91 |
| Treasure Vault (Remastered) | 1.145 / 132 |
| GM Core | 706 / 192 |
| Secrets of Magic | 609 / 39 |
| Battlecry! | 577 / 67 |
| War of Immortals | 441 / 77 |
| Dark Archive(s) (Remastered) | `Dark Archives (Remastered)` 397 / `Pathfinder Dark Archive (Remastered)` 61 |
| Guns & Gears | `Pathfinder Guns & Gears` 124 / `Guns & Gears` 17 |

Alem disso, **160 registros tem `\r\n` literal dentro de `source.book`** --
`'Pathfinder #218: Titanbane\r\n'` (39), `'Pathfinder #217: Death Sails a
Wine-Dark Sea\r\n'` (10) e outros. Isso e whitespace bruto do AoN vazando para
o artefato final.

Consequencia: qualquer agrupamento por livro no cliente (filtro "so Player
Core", contagem de cobertura, triagem de licenca) da numero errado. E foi
exatamente o que produziu boa parte dos 72 conflitos de `source`.

**Recomendacao:** reconciliador. Aplicar `normalizar_livro()` (e `.strip()`) na
**escrita** de `source.book`, guardando a grafia original em `source.book_raw`
se quiser rastreabilidade.

---

## A6. Dos 7 portoes de qualidade da spec, so 1 esta implementado -- e 2 falhariam hoje

**Gravidade: media-alta. E o que permitiu A1 a A5 passarem despercebidos.**

`reconciliar.py` (linhas 166-179) verifica exatamente tres coisas: `prov` nao
vazio, `license` presente, `id` com prefixo `wb:`. O relatorio emitido lista
apenas "FALHA sem license: 6". Confronto com a spec:

| # | portao | implementado | estado real medido |
|---|---|---|---|
| 1 | `prov` para todo campo preenchido | parcial (so "tem `prov`?") | **falharia: 2.694 registros com `text` preenchido e sem `prov.text`** (class-feature 817, trait 561, deity 484, background 332, heritage 326, domain 64, ancestry 50, skill 33, class 27) |
| 2 | `level` divergente sem `conflitos` | nao | nao medido -- ver A3 |
| 3 | `requires` citando `wb:` inexistente | nao | **falharia: 111 registros, 61 ids quebrados** |
| 4 | queda de cobertura sem justificativa | nao | -- |
| 5 | `license` ausente | **sim** | falha com 6 (ver A7) |
| 6 | `traits` disjunto pos-uniao | nao | uniao ainda nao implementada (achado 20) |
| 7 | nome duplicado no mesmo kind | nao | **tautologico** -- ver abaixo |

### Portao 3, os ids quebrados

61 ids distintos citados por `requires` e inexistentes, em 111 registros. Os
mais citados: `wb:class-feature/maestro-muse` (10), `enigma-muse` (7),
`warrior-muse` (7), `polymath-muse` (6) -- as musas do Bardo, que a base tem
como um unico `wb:class-feature/muses` generico. Idem
`wb:class-feature/ruffian-racket`, `mastermind-racket`, `scoundrel-racket`
contra o unico `wb:class-feature/rogue-s-racket`. Isso e o TODO 2 (grafo de dois
niveis) visto pelo outro lado: o parser de pre-requisito **ja sabe** que a
sub-escolha existe e a base nao a modela.

Ha tambem lixo de parser virando id: `wb:heritage/you-have-a-versatile` (2
citacoes) veio de prosa, nao de entidade.

Por contraste, `grants` tem **0** referencias quebradas, e `progressao` tem 8
(ver A1).

### Portao 7 nunca pode disparar

Medido: 0 grupos de nome normalizado duplicado dentro do mesmo kind. Mas isso e
consequencia de como o id e construido -- `wb:<kind>/<slug>` deriva do nome, e
`reconciliar.py` funde qualquer colisao de id antes de qualquer verificacao (75
fusoes neste build). O portao pergunta se existe duplicata **depois** de a
duplicata ter sido eliminada. Foi por essa fresta que o `death-from-above`
passou. O detector util e o que a spec descreve em "Colisao de identidade"
(valores categoricamente disjuntos), e ele precisa rodar **antes** de `fundir()`,
sobre as 75 colisoes de id.

**Recomendacao:** reconciliador. Implementar 1, 2, 3, 6 e mover 7 para antes da
fusao. Emitir o resultado de cada portao no relatorio mesmo quando passa -- hoje
o relatorio lista so as falhas, o que faz portao ausente e portao aprovado
parecerem a mesma coisa.

---

## A7. 22 registros vindos so do pf2etools sao duplicatas de registros que ja existem

**Gravidade: media. Explica os 6 sem `license`, os 23 sem `rarity` e 16 dos 907 sem prosa.**

22 registros tem `xref` contendo apenas `pf2etools`. Nao sao conteudo exclusivo:
sao o mesmo item com o nome-base, que nunca casou com a versao sufixada das
outras duas fontes.

**Os 6 do portao 5** (`license` ausente) sao todos deste grupo e todos com
`source: {}` -- sem livro, sem pagina, sem licenca:

| id | gemeo ja existente na base |
|---|---|
| `wb:armor/hide` | `wb:armor/hide-armor` |
| `wb:armor/leather` | `wb:armor/leather-armor` |
| `wb:armor/studded-leather` | `wb:armor/studded-leather-armor` |
| `wb:armor/heavy-power-suit` | `wb:armor/power-suit` |
| `wb:weapon/nine-ring-sword` | -- |
| `wb:weapon/wind-and-fire-wheel` | -- |

Hide, Leather e Studded Leather sao armaduras do Player Core. A base tem cada
uma duas vezes: uma completa e uma casca vazia. O portao 5 nao esta detectando
"falta licenca", esta detectando **falha de casamento** -- o sintoma foi lido no
nivel errado.

Os outros 16 sao feats: `wb:feat/dueling-dance` convive com
`wb:feat/dueling-dance-fighter`; `wb:feat/incredible-companion` com
`-druid` e `-ranger`; `wb:feat/stance-savant` com `-fighter` e `-monk`. Sao
tambem os 16 feats sem prosa e 16 dos 23 sem `rarity`.

Os 23 sem `rarity` = esses 16 feats + os 6 acima + `wb:archetype/venture-gossip`,
que e o unico registro da base com **`xref` completamente vazio** -- nao tem
fonte nenhuma.

**Recomendacao:** extrator de equipamento e de feats. Duas coisas distintas:
(a) o casamento tem de tentar o nome-base contra os sufixados antes de emitir
registro novo; (b) registro sem nenhuma fonte identificavel (`xref` vazio,
`source` vazio) nao deve ser emitido -- deve falhar o build.

---

## A8. 907 registros sem prosa, e o relatorio diz 100%

**Gravidade: media.**

`base/relatorio_textos.md` afirma "referencias resolvidas: **17866/17866**
(100.0%)" e "sem prosa: 0". O que ele mede e: *das referencias que existem,
quantas resolvem*. **907 registros (5,0%) tem o campo `text` nulo** e portanto
nao entram no denominador:

| kind | sem prosa | % do kind |
|---|---|---|
| equipment | 768 | 13,5% |
| weapon | 87 | 8,7% |
| armor | 29 | 14,0% |
| feat | 16 | 0,3% |
| shield | 6 | 5,1% |
| archetype | 1 | 0,4% |

Todos os 768 de equipment sao registros so-Foundry (o Foundry contribui 768
registros exclusivos de equipment). A metrica correta e `com_prosa / total_base`
= 17.269/18.176 = **95,0%**.

Somando: 907 registros sem prosa + 597 chaves de prosa orfas (A1) = a camada de
texto tem 1.504 registros desalinhados.

Verificado como OK: **0** referencias `text` apontando para chave inexistente e
**0** prosas vazias entre as que resolvem. 194 prosas com menos de 60 caracteres,
concentradas em trait (67), deity (57) e domain (52) -- plausivel para essas
familias.

**Recomendacao:** `emitir_textos.py` -- mudar o denominador da metrica para o
total da base. E extratores: emitir `text` sempre, mesmo apontando para prosa
derivada do Foundry.

---

## A9. `spell` nao usa `level`, usa `rank` -- e sai do envelope da spec

**Gravidade: media. 1.639 registros.**

A spec diz explicitamente: "`level` escalar continua valendo para `feat`,
`spell` e tudo que tem nivel intrinseco. So class-feature muda."

Medido: **0 dos 1.639 spells tem `level`**; todos os 1.639 tem `rank` (1-10).
`rank` nao aparece no envelope da spec nem na tabela de precedencia (embora
apareca em `prov`, com valores `foundry` 1.624 / `aon` 15).

Consequencia direta: um filtro de `level` no cliente -- "o que posso pegar no
nivel 5" -- descarta silenciosamente todas as magias. O nome remaster do campo
e de fato `rank`, entao a decisao pode estar certa; o que esta errado e a spec
nao registrar isso, e nenhum outro kind seguir a mesma convencao.

Junto disso, na mesma familia: **513 dos 1.639 spells nao tem `tradicoes`**
(31,3%). 463 sao focus spells (aceitavel se a tradicao for derivada da classe
que concede) mas **50 nao sao** -- `wb:spell/allegro`, `rallying-anthem`,
`song-of-marching`, `song-of-strength` (composicoes de Bardo),
`wb:spell/boost-eidolon`, `reinforce-eidolon` (Summoner), varios cantrips de
Witch e Psychic. Tradicao e o que decide quem pode aprender a magia.

**Recomendacao:** spec -- declarar `rank` no envelope e dizer que para `spell`
ele substitui `level` (ou emitir os dois). Extrator de magias -- fechar as 50
tradicoes ausentes fora de focus.

---

## A10. 3.033 registros repousam em uma unica fonte, sem cross-check possivel

**Gravidade: media. 16,7% da base.**

Distribuicao de fontes em `xref` (contando so `foundry`/`aon`/`pf2etools`):

| combinacao | n |
|---|---|
| aon + foundry | 6.939 |
| aon + foundry + pf2etools | 5.435 |
| **so aon** | **3.033** |
| **so foundry** | **1.349** |
| aon + pf2etools | 208 |
| foundry + pf2etools | 43 |
| **so pf2etools** | **22** |
| **nenhuma** | **1** |

Kinds que sao 100% mono-fonte AoN: `trait` (561), `deity` (484),
`animal-companion` (113), `domain` (64), `skill` (33), `apparition` (14),
`eidolon` (13), e `archetype` (242 de 245). Total 1.524 registros.

Isso e **declarado** -- `extratores/referencia.py` diz na docstring que
pf2etools "nao contribui campo nenhum" para trait/skill/deity/domain, e o
Foundry so entra para `license` de deity. Nao e bug acidental. Mas tem duas
consequencias que valem registrar:

1. **A materia-prima esta em disco e nao e usada.** `dados_brutos/pf2etools/`
   tem `traits.json` (471), `deities.json` (309), `domains.json` (98),
   `skills.json` (36). O checkout do Foundry tem `deities/` (480 arquivos) e
   `familiar-abilities/` (111).
2. **O proprio pipeline ja mediu a falta e ninguem agiu.**
   `saida/_referencia_estatisticas.json`, campo `pf2etools_crosscheck`, registra
   `so_pf2etools`: **trait 34, deity 7, skill 1** -- 42 nomes que existem no
   pf2etools e nao existem na base. O numero esta gravado desde o build.

Cruzando o checkout do Foundry por nome normalizado (incluindo `aliases` e
nomes legados), tambem faltam: **6 deities** (`Alocer`, `Chinostes`, `Norns`,
`Atheists and Free Agents`, `Lissala (The Order of Virtue)`, `The Curtain
Call`), **38 familiar-abilities** (incluindo as seis `Elemental Familiar
(Air/Earth/Fire/Metal/Water/Wood)` e ~20 `Familiar of ...` de Divine
Mysteries) e **15 class-features** do padrao `X's Calling`.

**Recomendacao:** extrator `referencia.py` e `companheiros.py`. Nao precisa
virar precedencia completa: basta usar a segunda fonte como **cobertura**
(o que existe la e nao aqui) e como cross-check de `name`/`source`. O
`pf2etools_crosscheck` ja calcula a lista; falta consumi-la.

---

## A11. Um diretorio de organizacao do Foundry virou id de arquetipo

**Gravidade: baixa. 14 feats.**

14 feats tem `archetype: "wb:archetype/shared-archetype-feats"`, e nao existe
registro `wb:archetype/shared-archetype-feats`. E o unico id de arquetipo citado
por feats sem registro correspondente. `packs/pf2e/feats/archetype/shared/` (ou
equivalente) e uma pasta de organizacao do repo, nao um arquetipo.

Mesma classe do `e_artefato()` que `reconciliar.py` ja implementa para descartar
pasta-virou-registro -- so que aqui o artefato virou **referencia**, nao
registro, entao o filtro nao pega.

Fora isso, o vinculo feat<->arquetipo esta em boa forma (ver secao de
verificados).

---

## A12. `prov` incompleto e proveniencia heuristica nao sinalizada como risco

**Gravidade: baixa a media.**

- **2.694 registros com `text` preenchido e sem `prov.text`** (ver A6, portao 1).
- **1.440 registros com `source.license` inferida do nome do livro**
  (`prov["source.license"] = "inferida:livro"`), pela heuristica
  `remaster==True or livro in LIVROS_ORC -> ORC, senao OGL`. Nao ha sinal no
  registro emitido de que a licenca e derivada e nao lida da fonte; so em `prov`.
  Considerando o item 16 do TODO (licenciamento antes de publicar), 1.440
  licencas inferidas e a base do build publico.
- **Proveniencia com sufixo heuristico em 3 campos**: `prov.source` inclui
  `"foundry(deities, por nome)"` (469), `"aon(heuristica:remaster_id)"` (238+72);
  `prov.rarity` inclui `"aon (nome aproximado)"` (54); `prov.class` inclui
  `"foundry (inferido de traits)"` em **409 de 817 class-features** -- metade do
  vinculo feature->classe e inferido de trait, nao lido do `items{}` da classe.
  61 class-features tem `prov.class: null`.
- **`prov` com valor `"desconhecida"`** em 152 pontos: `grants` 47, `requires`
  41, `area` 21, `escalonamento_de_dano` 14, `duracao` 12, `legado_de` 10,
  `traits` 2, `level` 2, `feat_category` 2, `area_of_concern` 1. Sao os casos que
  `fundir()` produz na linha 90 quando o registro absorvido nao trouxe `prov`.

Verificado OK: com excecao de `text`, **nenhum outro campo do envelope** aparece
preenchido sem `prov`.

**Recomendacao:** spec -- `prov` deveria distinguir "lido da fonte X" de
"inferido por heuristica H". Hoje isso vive numa string livre com 8 formatos
diferentes, que nenhum consumidor consegue parsear.

---

## A13. Achados menores, com numero

- **Representacao do vazio inconsistente em `traits`**: 65 registros com `null`
  (class 27, class-feature 38) contra 3.036 com `[]`. Cliente que testar
  `traits.length` quebra nos 65.
- **256 feats sem `feat_category`** (4,1% do kind), e 3 com o valor
  `"classfeature"` -- valor bruto do Foundry que escapou da normalizacao (os
  outros valores sao `class` 4.064, `ancestry` 1.563, `skill` 336, `general` 40,
  `bonus` 14).
- **567 feats com `requires_texto` preenchido e `requires` vazio** -- a cauda
  conhecida do parser (84,7%), aqui contada por registro.
- **1.506 registros sem `source.page`** (8,3%), concentrados em equipment (796)
  e class-feature (430 de 817, 52,6%).
- **141 registros sem `source.remaster`** (True 12.032 / False 6.003 / ausente
  141).
- **Traits orfaos: 16 distintos, 40 citacoes** -- todos parametrizados
  (`fatal-d10` 7, `fatal-d8` 6, `two-hand-d8` 6, `deadly-d8` 3, `thrown-20` 3...).
  Isto encerra o TODO 5: nao ha erro de normalizacao generico, e so o caso
  parametrizado do achado 20. A estatistica do proprio extrator
  (`traits_orfaos_total: 0`) da zero porque so olha a propria familia.
- **Escala real da perda por trait parametrizado** (quantificacao do achado 20,
  nao achado novo): entre as 997 armas, carregam o trait **sem** parametro --
  `deadly` 42, `thrown` 36, `fatal` 32, `two-hand` 15, `scatter` 7, `volley` 6,
  `fatal-aim` 3, `jousting` 2. Sao ~143 armas com trait mecanicamente
  incompleto, contra os 18 casos de conflito totalmente disjunto que a
  investigacao anterior contou. `wb:weapon/bastard-sword` traz `two-hand` com
  `damage: d8`; `wb:weapon/arquebus` traz `fatal` sem dado.

---

## O que foi verificado e estava certo

Delimita o que ja foi coberto por esta auditoria e nao precisa ser reexaminado.

| verificacao | resultado |
|---|---|
| Referencias `wb:` dentro de `grants` | **0 quebradas** em 3.773 registros com `grants` |
| Referencias `text` -> `base/text/` | **0** apontando para chave inexistente, **0** prosa vazia |
| Ids duplicados apos a reconciliacao | 0 |
| Ids fora do padrao `wb:` | 0 |
| Vinculo feat<->arquetipo | 2.262 feats apontam para 244 arquetipos; **so 4 arquetipos** divergem da contagem do AoN, todos por 1 unidade, e **todos os 4 causados por A1**. O metodo do diretorio do Foundry (licao ja registrada) esta validado |
| Arquetipos sem nenhum feat | 2 (`drow-shootist`, `hellknight-armiger`) -- ambos plausiveis |
| `traits` de background vazio em 325/332 | **correto**. Os 332 backgrounds do Foundry tem `traits.value` vazio; background no PF2e nao carrega trait alem de raridade. Nao ha perda |
| `traits` de heritage / deity / archetype vazio | idem -- confirmado contra o Foundry, sem perda |
| `level` das armas | **nao** e default: 263 de 997 no nivel 0 (armas base), o resto distribuido de 1 a 28. Sem valor de preenchimento |
| Heranças versateis (`Nephilim`, `Aiuvarin`, `Dromaar`, `Dhampir`, `Dragonblood`, `Beastkin`, `Changeling`, `Talos`, `Ardande`, `Suli`, `Naari`) | **presentes** como `heritage`. O delta de -18 em `ancestry` contra o AoN e categorizacao do AoN (ele indexa heranca versatil como `ancestry`), nao ausencia |
| Contagem de `deity`, `skill`, `class`, `eidolon`, `familiar-specific` | **identica** ao censo do AoN vigente (484 / 33 / 27 / 13 / 38) |
| `feat` e `equipment` do Foundry ausentes da base | **0** em ambos, comparando por nome normalizado com `aliases` e nomes legados |
| `heritage` do Foundry ausente da base | 0 |
| Distribuicao de `rarity` | common 12.564 / uncommon 3.965 / rare 1.360 / unique 264 / ausente 23. Sem fallback suspeito -- os 23 ausentes sao explicados por A7 |
| `level` ausente por kind | 4.564, e todos por motivo declarado na spec (class-feature por decisao, spell usa `rank`, e kinds sem nivel intrinseco). Nenhum caso de nivel perdido por falha de extracao |
| Campos do envelope preenchidos sem `prov` | so `text` (A6). Todos os demais cobertos |
| 61 class-features sem classe dona | confirmado igual ao TODO 2 (escolhas de segundo nivel), nao regrediu |

---

## Recomendacoes agrupadas por onde a correcao mora

**Reconciliador** (`reconciliar.py`, `fundir_renomeados.py`)
- A1: trocar o criterio de fusao por `remaster_id`/`legacy_id` do AoN; guardas
  de `level`/`price_cp`/`damage`, N->1 e data de publicacao; parar de deletar o
  absorvido.
- A5: normalizar e `strip()` `source.book` na escrita.
- A6: implementar os portoes 1, 2, 3 e 6; mover o 7 para antes de `fundir()`;
  reportar todos os portoes, nao so os que falham.
- A3: portao novo -- kind grande com 2+ fontes e zero `conflitos` falha o build.

**Extratores**
- A2: preencher `grants_completos` e `requires_parseado` com definicao unica.
- A3: extrair a logica de precedencia + registro de divergencia para funcao
  compartilhada.
- A4: extratores novos de `ritual`, `relic`, `language`; fechar os 167
  backgrounds.
- A7: casar nome-base contra sufixado antes de emitir; recusar registro com
  `xref` vazio.
- A8: emitir `text` sempre; corrigir o denominador da metrica.
- A9: fechar as 50 tradicoes de magia nao-focus.
- A10: consumir o `pf2etools_crosscheck` que o pipeline ja calcula; puxar
  deities e familiar-abilities do checkout do Foundry.
- A11: filtrar diretorio organizacional tambem quando ele vira **referencia**.
- A13: normalizar `feat_category`; padronizar `[]` para `traits` vazio.

**Spec** (`specs/2026-07-26-schema-base.md`)
- A2: separar `mechanized` em dois campos com semantica declarada, e prever
  "nao se aplica" para kind sem `grants`.
- A4: adicionar `relic` e `language` a lista de kinds; corrigir o numero de
  rituals no TODO 17 (145, nao 31).
- A9: declarar `rank` no envelope e sua relacao com `level`.
- A12: `prov` precisa distinguir leitura de fonte e inferencia heuristica, com
  vocabulario fechado.

---

## Nota de metodo

Os quatro achados de maior impacto (A1 a A4) sairam da mesma pergunta:
**por que este numero e exatamente esse?**

- A1: por que 597 fusoes com criterio que nao olha numero nenhum?
- A2: por que `mechanized: false` cai em 100% de oito kinds inteiros?
- A3: por que `conflitos` e exatamente zero em seis kinds que tem tres fontes?
- A4: por que `background` tem 332 se o Foundry tem 514?

Nenhum deles apareceria verificando registro por registro -- cada registro
isolado parece plausivel. `wb:equipment/aeon-stone` e um registro valido de uma
pedra aeon; so a distribuicao mostra que ele engoliu outras 23.

Ferramenta que se provou decisiva: o censo por `category` do AoN descontando
`remaster_id`. Uma query, e ela sozinha entregou A4 inteiro. Consulta usada:

```json
{"size":0,"track_total_hits":true,
 "query":{"bool":{"must":[{"term":{"category":"<cat>"}}],
                  "must_not":[{"exists":{"field":"remaster_id"}}]}}}
```

com header `User-Agent` obrigatorio. Controle de query sempre rodado antes de
concluir ausencia (`Loremaster` retornou 2; `Power Attack -> Vicious Swing`
retornou confirmado).
