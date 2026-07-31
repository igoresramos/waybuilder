# Comparacao com o Pathbuilder -- 6a rodada (2026-07-31)

> **VERIFICADO E CORRIGIDO EM 2026-07-31.** O relatorio conclui UM defeito
> nosso (`wb:feat/incredible-familiar` com trait `animist` indevido). Conferido
> contra a fonte, **nao e defeito**: o proprio AoN publica
>
> ```
> Incredible Familiar | level 8 | traits ['Animist', 'Thaumaturge', 'Witch'] | src ['Player Core']
> Incredible Familiar | level 8 | traits ['Thaumaturge', 'Witch']            | src ['Dark Archive', "Advanced Player's Guide"]
> ```
>
> O trait `animist` vem do **Player Core**, e `prov.traits` do registro e
> `['aon', 'foundry']` -- as duas fontes concordam. O Pathbuilder e que carrega
> a lista pre-remaster (Dark Archive / APG). Pela regra do projeto de sempre
> seguir a versao mais recente, **nos estamos certos e ele esta atrasado**.
>
> Balde correto: **recorte de fonte**, nao defeito nosso. Resultado da rodada 6:
> **zero defeitos nossos** em 14 classes e 152 pontos triados -- o que e um
> resultado bom, e nao um resultado vazio.
>
> O que o relatorio acerta e vale guardar: as 6 classes que travam o Class Feat
> do nivel 1 atras de uma escolha de subclasse obrigatoria (Animist, Witch,
> Magus, Psychic, Oracle, Summoner), somadas a Druida e Feiticeiro ja
> conhecidas, e o limite do comparador -- `incredible-familiar` e
> `incredible-familiar-animist` colidem na normalizacao e o script conta como
> "casado", entao um par assim nunca apareceria no placar.


Item 84 do TODO. Terreno: as **14 classes que faltavam** em `DEFAULT` de
`motor/comparar_pathbuilder.py` -- Guardian, Exemplar, Commander, Gunslinger,
Inventor, Kineticist, Swashbuckler, Thaumaturge, Animist, Witch, Magus,
Psychic, Oracle, Summoner. Com as 13 ja cobertas (Fighter, Wizard, Cleric,
Ranger, Rogue, Barbarian, Bard, Monk, Champion, Druid, Sorcerer, Alchemist,
Investigator), fecha as **27** classes do jogo.

Restricao do item: `motor/comparar_pathbuilder.py` e `docs/comparacao/equivalencias-pathbuilder.json`
sao arquivos ja versionados e **nao foram editados**. A extensao de `DEFAULT`/`BOOSTS_DO_PATHBUILDER`
para as 14 classes novas foi feita por monkey-patch em memoria, num script auxiliar
que importa o modulo original e so altera os dicts em RAM antes de chamar
`comparar()` -- o arquivo em disco fica intocado. Script descartavel, nao versionado.

## 1. Os boosts, medidos -- nao chutados

`sonda-estado-pathbuilder.mjs` rodou nas 14 classes (Human/Barkeep, nivel 1).
Confirmado por medicao, nao suposto: para **toda** classe de chave-unica (nao
escolha), o Pathbuilder gasta os boosts livres sempre na mesma ordem -- STR,
STR, DEX, CON -- e a chave da classe entra por CIMA disso, sozinha se cair fora
de STR/DEX/CON, somada se cair dentro. Confirmado batendo o modificador final
contra a distribuicao em 11 classes seguidas, todas as chaves-unica do lote:

| classe | chave | modificador medido | boosts livres aplicados |
|---|---|---|---|
| Guardian | str (dentro) | STR+3 DEX+1 CON+1 | `str str dex con` (+ auto STR = 3) |
| Commander | int (fora) | STR+2 DEX+1 CON+1 INT+1 | `str str dex con` (+ auto INT) |
| Gunslinger | dex (dentro) | STR+2 DEX+2 CON+1 | `str str dex con` (+ auto DEX = 2) |
| Inventor | int (fora) | STR+2 DEX+1 CON+1 INT+1 | `str str dex con` (+ auto INT) |
| Kineticist | con (dentro) | STR+2 DEX+1 CON+2 | `str str dex con` (+ auto CON = 2) |
| Swashbuckler | dex (dentro) | STR+2 DEX+2 CON+1 | `str str dex con` (+ auto DEX = 2) |
| Thaumaturge | cha (fora) | STR+2 DEX+1 CON+1 CHA+1 | `str str dex con` (+ auto CHA) |
| Animist | wis (fora) | STR+2 DEX+1 CON+1 WIS+1 | `str str dex con` (+ auto WIS) |
| Witch | int (fora) | STR+2 DEX+1 CON+1 INT+1 | `str str dex con` (+ auto INT) |
| Oracle | cha (fora) | STR+2 DEX+1 CON+1 CHA+1 | `str str dex con` (+ auto CHA) |
| Summoner | cha (fora) | STR+2 DEX+1 CON+1 CHA+1 | `str str dex con` (+ auto CHA) |

O padrao bate com o que ja estava documentado para Wizard/Cleric/Rogue/Bard/
Druid/Sorcerer/Alchemist/Investigator (todas medidas em rodadas anteriores) --
nao e coincidencia, e o mesmo default do Pathbuilder aplicado de forma
identica independente de qual atributo e a chave.

Para as 3 classes de chave-ESCOLHA (dex/str ou int/cha), o Pathbuilder nao
aplica nada sozinho -- os 5 boosts saem todos explicitos:

| classe | chave | modificador medido | boosts |
|---|---|---|---|
| Exemplar | dex/str | STR+3 DEX+1 CON+1 | `str str str dex con` (identico a Fighter/Champion/Monk) |
| Magus | dex/str | STR+3 DEX+1 CON+1 | `str str str dex con` |
| Psychic | int/cha | STR+2 DEX+1 CON+1 INT+1 | `str str dex con int` (escolheu INT, nao CHA) |

## 2. As 6 classes sem Class Feat no nivel 1 -- medido no nivel 2, e informacao

Igual Druida/Feiticeiro (ja documentado): 6 das 14 classes tem uma escolha de
subclasse OBRIGATORIA antes do primeiro Class Feat, que so libera no nivel 2.
Confirmado no bloco de pendencias do nivel 1 de cada uma:

| classe | o que trava o nivel 1 |
|---|---|
| Animist | Select Animistic Practice |
| Witch | Select Patron |
| Magus | Select Hybrid Study |
| Psychic | Select Conscious Mind / Select Subconscious Mind |
| Oracle | Select Mystery |
| Summoner | Select Eidolon Type |

Todas as 6 rodaram no **nivel 2**. Nao e falha, e o mesmo comportamento do
Pathbuilder (ele tambem nao mostra Class Feat no nivel 1 dessas classes).

Nota a parte, fora do escopo do placar: o Summoner mostra um botao "Evolution
Feat" (nao "Class Feat") ja no nivel 1 -- e o slot dos feats de evolucao do
Eidolon, que a nossa base **nao modela** (`class.json` do Summoner nao tem
`feat_slot` desse tipo). Nao entrou na comparacao porque nao existe candidato
nosso pra comparar contra; fica registrado, nao investigado a fundo.

## 3. O placar

14 classes, `class_feat` no nivel correto + `Dedication Feats` (unica aba com
conteudo alcancavel nas classes sem arquetipo ainda declarado -- `Skill
Feats`/`General Feats` nao aplicam no nivel medido). **152 pontos brutos**,
triados abaixo.

| classe/nivel | so no PB | so no WB | discordam |
|---|---:|---:|---:|
| Guardian 1 | 2 | 3 | 0 |
| Exemplar 1 | 0 | 3 | 0 |
| Commander 1 | 0 | 4 | 0 |
| Gunslinger 1 | 0 | 3 | 0 |
| Inventor 1 | 0 | 3 | 1 |
| Kineticist 1 | 0 | 8 | 25 |
| Swashbuckler 1 | 1 | 3 | 0 |
| Thaumaturge 1 | 0 | 3 | 0 |
| Animist 2 | 0 | 4 | 9 |
| Witch 2 | 6 | 7 | 13 |
| Magus 2 | 0 | 4 | 10 |
| Psychic 2 | 0 | 5 | 8 |
| Oracle 2 | 0 | 3 | 10 |
| Summoner 2 | 0 | 3 | 11 |

## 4. DEFEITO NOSSO -- 1 registro, achado novo

| registro | o que `traits`/`requires` dizem hoje | o que deveria dizer | classes afetadas |
|---|---|---|---|
| `wb:feat/incredible-familiar` | `traits: [animist, thaumaturge, witch]`; `requires: class_level animist>=8 OR thaumaturge>=8 OR witch>=8` | `traits: [thaumaturge, witch]` (tirar `animist`); requires so com as duas | Animist |

**A prova.** `wb:feat/incredible-familiar` e o "Incredible Familiar" de
*Player Core* pg. 188 (feat de Bruxa/Taumaturgo, nivel 8). Existe TAMBEM
`wb:feat/incredible-familiar-animist`, de *War of Immortals*, nivel **10**,
com `traits: [animist]` -- a versao que o proprio Animist recebeu quando a
classe foi publicada. O Pathbuilder, pra Animist, lista **um unico**
"Incredible Familiar", no nivel 10 (conferido em
`docs/comparacao/pathbuilder-animist-class_feat-nv2.json`) -- o de War of
Immortals. Nosso motor oferece os **dois** pro Animist: o generico de nivel 8
(errado, o trait `animist` nele e importacao invasiva) e o correto de nivel
10.

Efeito na ficha: um Animist de nivel 8 ou 9 ve "Incredible Familiar"
disponivel dois niveis antes da hora, com o texto ERRADO (o generico fala
"bonus familiar abilities you gain for being a witch", que nao faz sentido
pra um Animist).

**Por que o comparador nao acusou isto sozinho.** `norm()` tira o sufixo de
desambiguacao entre parenteses -- por design, pra casar `Guardian's Deflection
(Fighter)` com o nome sem sufixo do Pathbuilder. Aqui os dois nomes da nossa
base ja saem SEM parenteses (`Incredible Familiar` e `Incredible Familiar
(Animist)` -- o segundo tem o sufixo no proprio campo `name`), entao os dois
colapsam pra chave `incredible familiar`, `nossos{}` guarda so o primeiro
(`setdefault`), e o placar mostra `41 nosso / 39 dele / 39 em comum` como se
tivesse batido 100% -- o item extra fica invisivel no placar, so aparece
investigando registro por registro. Achado por investigar o "Incredible
Familiar (Animist)" (nome ja com sufixo na base) contra o generico, nao pelo
placar. Vale registrar como limite do script de comparacao (nao mexido, por
regra deste item), nao como bug novo pra consertar nele.

## 5. DIFERENCA DE MODELO -- todas ja declaradas, so novas instancias

**5.0 -- Inventor, fora do grupo das 6.** `No! No! I Created You!`
(`wb=True pb=False`) tem `requires` so com `class_level inventor>=1`, mas o
texto real exige "construct companion" -- clausula narrativa que cai inteira
em `requires_residuo` (confirmado no proprio registro). Nenhum Inventor de
bancada tem companheiro construto. Mesma familia de principio zero da secao
5.1, so que numa classe que JA tem Class Feat no nivel 1 (nao faz parte do
grupo de escolha pendente).

**5.1 -- 6 classes sem escolha de subclasse feita.** A maioria dos 61
`discordam` das 6 classes de nivel 2 (Animist, Witch, Magus, Psychic, Oracle,
Summoner) cai em UMA das duas familias ja descritas no cabecalho do
comparador:

- **`wb=False pb=True`** (Bounty Hunter, Crossbow Infiltrator/Drow Shootist,
  Draconic Acolyte, Ghost Hunter, Scroll Trickster -- pericia): o Pathbuilder
  conta a escolha de pericia PENDENTE como alcancavel; nos avaliamos o estado
  atual (untrained) e marcamos. Familia identica a rodada 3.
- **`wb=True pb=False`** por pre-requisito NARRATIVO em `requires_residuo`
  (Alkenstar Agent, Seneschal Witch, Ulfen Guard, Pactbinder -- todos com
  `requires_residuo` preenchido: "member of the Ulfen Guard", "seneschal
  witch" etc.): principio zero, ja declarado.
- **`wb=True pb=False`** por CHOICE de subclasse ainda pendente (Magic
  Warrior, War Mage, Soulforger -- exigem "ability to cast focus spells" /
  "spellcasting class feature" / "Wisdom 14 or divine spells", os tres
  PARSEADOS corretamente e satisfeitos pela classe): aqui o motivo e o
  INVERSO da familia de pericia -- nosso motor sabe que Magus e sempre
  arcano e Oracle sempre tem foco, mas o Pathbuilder so resolve a tradicao
  de conjuracao do personagem DEPOIS que Hybrid Study/Mystery/Patron e
  escolhido na propria UI dele, e a bancada nunca faz essa escolha (e
  justamente a escolha que trava o nivel 1, secao 2). Mesma raiz da secao 2,
  so que aparecendo como "discorda" em vez de "sem Class Feat". Nao e
  defeito: o nosso e o comportamento mais correto (a classe JA determina a
  tradicao, a escolha de subclasse so refina).
- **`Witch's Armaments`** (Witch) e **`Whispers of Weakness`** (Oracle),
  ambos `wb=True pb=False`, mesma raiz: dependem do Patron/Mystery ainda nao
  escolhido.

**5.2 -- Kineticist confirma gap JA rastreado (TODO itens 97/99), nao e
achado novo.** Dos 33 pontos do Kineticist, 24 sao feats de impulso
(`Aerial Boomerang`, `Air Cushion`, `Burning Jet`, `Flashforge`...) com
`wb=True pb=False` e `motivos: []` -- o motor nao tem NENHUM predicado de
gate elemental (`requires` desses feats e so `class_level kineticist>=1`),
porque os 6 gates elementais do Kineticist estao **zero implementados**,
achado e medido no item 99 ("Kineticist (6 gates + impulsos)... hoje tem ZERO
bloco de subclasse"). O Pathbuilder bloqueia tudo que exige um elemento
porque a bancada nao escolheu gate nenhum; nos liberamos tudo, pelo mesmo
motivo de fundo. `Extended Kinesis` (`wb=False pb=True`, exige `has:
wb:feat/base-kinesis`) e a mesma raiz do outro lado -- feature basica do
Kineticist que a base tambem nao concede automaticamente. Esta rodada so
CONFIRMA o tamanho do buraco com outro instrumento (comparador em vez de
leitura de codigo); nao conta como defeito novo pro balde (a). Os outros 5
pontos de "so no Waybuilder" (`Burning Demand`, `Drowning Mist`, `Flash
Forge`, `Liberating Dive`, `Voice of the Elements`, niveis 5 a 14) sao a
mesma familia sempre benigna de candidato de nivel futuro que o Pathbuilder
nao mostra na janela do nivel medido -- ja vista nas rodadas anteriores.

**5.3 -- Recorte de aba (Guardian).** `Mighty Bulwark` e `Shield Salvation`
tem `traits: [archetype, guardian]` -- feats de nivel alto (8, 10) que exigem
`Sentinel Dedication`/`Bastion Dedication` mas TAMBEM carregam o trait da
classe. O Pathbuilder os lista na aba "Class Feats" do Guardian; a nossa aba
de comparacao os exclui por ter `archetype` no trait (mesma guarda que
resolveu o falso-positivo dos 11 feats de mascara do Wizard na rodada 3).
Continuam candidatos validos no slot base, so nao aparecem NESTA aba.

**5.4 -- `Major Lesson` (Witch), representacao de feat repetivel.** O texto
do feat diz "voce pode escolher este feat de novo no nivel 14, e de novo no
18". O Pathbuilder representa isso como TRES entradas na lista (`Major Lesson
I/II/III`); nossa base tem UM registro (nivel 10). Recorte de representacao,
nao numero errado -- o slot de nivel 10/14/18 ja permite pegar o mesmo feat
de novo por regra generica de repeticao (nao investigado aqui se essa
mecanica de "pode repetir" esta implementada; fica como nota, nao como
achado deste item).

## 6. RECORTE DE FONTE

- **`Chelaxian Scion Dedication`, `Knight Vigilant`, `Venture-Gossip
  Dedication`** -- os mesmos 3 de sempre (AP #223, Character Guide, Paizo
  Blog), aparecem em TODAS as 14 classes novas porque `Dedication Feats` e
  compartilhada entre classes. Ja identificados na 1a rodada.
- **`Armor Regiment Training`** (Commander, nivel 1, *Battlecry!* pg. 30) --
  confirmado ausente em TODAS as abas do Pathbuilder pra Commander, apesar
  dele carregar os outros 43 feats do mesmo livro. Falha pontual de
  importacao do lado dele, nao nosso.
- **`Vermillion Threads`** (Magus, nivel 10, *Tian Xia Character Guide*) --
  mesma familia dos feats do Kingmaker/Hell's Destiny ja descartados: obra
  que o Pathbuilder nao carrega.
- **`Automatic Psychic Action`** (nivel 20) e **`Deepest Wellspring`** (nivel
  18), ambos so nossos -- nao investigado a fundo (nivel alto, baixo
  impacto); nao aparecem em nenhuma aba do Pathbuilder pra Psychic. Fica
  como recorte de fonte nao confirmado a fundo, prioridade baixa.
- **3 pares novos de renomeacao** (Golarion -> generico, mesmo padrao das 35
  ja tabeladas em `equivalencias-pathbuilder.json`, arquivo NAO editado por
  regra deste item): `Syu Tak-Nwa's Deadly Hair` -> `Deadly Hair`,
  `Syu Tak-Nwa's Hexed Locks` -> `Hexed Locks`, `Syu Tak-Nwa's Skillful
  Tresses` -> `Skillful Tresses`. Confirmado: os 3 nomes com "Syu Tak-Nwa's"
  sao os nossos (corretos, nome proprio do feat conforme o Player Core), os
  3 genericos sao os do Pathbuilder. Fica anotado para quando o arquivo de
  equivalencias for atualizado (fora do escopo deste item).
- **`Twin Parry`** (Swashbuckler) -- feat de Fighter/Ranger que o Pathbuilder
  lista (em vermelho, `atende: false`) dentro da aba "Class Feats" do
  Swashbuckler, sem nenhum motivo aparente (nao tem trait `swashbuckler`).
  Parece anomalia do proprio Pathbuilder -- ele mesmo marca como
  indisponivel, entao nao muda o placar de "disponivel" nenhum dos dois
  lados. Nosso lado esta certo em nao oferecer.

## O que nao rodou

Nada falhou. As 14 classes mediram e compararam de ponta a ponta -- sondas,
estados e comparacoes todas produziram arquivo. `Skill Feats`/`General Feats`
nao entraram porque nenhuma das 14, no nivel medido (1 ou 2), tem esse slot
aberto ainda (mesma limitacao natural das rodadas anteriores com Fighter 1).
