# Triagem do balde "so no Waybuilder" -- 14 classes novas (2026-07-31)

Item 84 do TODO. Terreno: os pontos "so no Waybuilder" (feats que oferecemos e o
Pathbuilder nao) das 14 classes que a rodada 6 mediu (Guardian, Exemplar,
Commander, Gunslinger, Inventor, Kineticist, Swashbuckler, Thaumaturge, Animist,
Witch, Magus, Psychic, Oracle, Summoner). O item 84 chama esse balde de "quase
todos dedicacoes -- recorte de fonte" mas marca como **o unico que pode
esconder defeito novo**. Esta triagem confirma a suspeita: **esconde, sim** --
8 defeitos novos, nunca vistos nas 6 rodadas anteriores.

## 0. Antes de triar: os dados e a contagem

`docs/comparacao/*.json` foi **regenerado** rodando
`python3 motor/comparar_pathbuilder.py docs/comparacao/pathbuilder-*.json` de
ponta a ponta (o `DEFAULT`/`BOOSTS_DO_PATHBUILDER` do arquivo em disco ja cobre
as 27 classes -- a extensao que o item 69 fez por monkey-patch foi
posteriormente commitada nele mesmo, entao rodar direto ja usa as 27). `git
status` depois do run: **zero diff** -- os arquivos em disco batem exatamente
com o que o comparador produz agora. Os dados nao estao desatualizados.

**Divergencia de contagem, registrada sem esconder:** somando a coluna "so no
WB" do placar da rodada 6 (Class Feats + Dedication Feats, as duas abas que a
propria rodada 6 tabulou) dá **56**, nao 57. Recontei direto dos
`comparacao-*.json` regenerados, linha por linha: **56**. Nao encontrei o
57o ponto em nenhuma leitura -- nem incluindo a aba Skill Feats (que rodou em
nivel diferente e nunca entrou nesse placar), nem provavelmente um erro de
soma de quem escreveu o item 84. Fica como nota, nao bloqueia a triagem: os 56
existentes foram todos triados.

## 1. O metodo

Para cada um dos 56, con feri contra:
- `pipeline/base/index.json` (o registro nosso: `name`, `level`, `source`,
  `requires`, `grants`, `xref`, `prov`);
- `pipeline/dados_brutos/aon_dump/feat.json` (nome e nivel oficiais Paizo,
  `remaster_id`/`legacy_id` quando existem);
- o JSON bruto da sonda em `docs/comparacao/pathbuilder-<classe>-*.json` (a
  lista **completa** que a tela do Pathbuilder mostra, todas as abas, nao so o
  resumo impresso) -- pra achar variante de nome que o comparador nao pegou.

A pergunta feita em CADA item: "o Pathbuilder realmente nao tem isso, ou tem
sob um nome que o `norm()`/`equivalencias-pathbuilder.json` nao casa?" Essa
pergunta e o que a rodada 6 nao fez sistematicamente -- ela leu o placar
resumido (que trunca em 12 itens e nunca mostra nivel) e nao foi atras da
lista bruta da sonda linha a linha.

## 2. O placar final

| balde | pontos | % |
|---|---:|---:|
| (a) DEFEITO NOSSO | **21** | 37,5% |
| (b) RECORTE DE FONTE | **31** | 55,4% |
| (c) DIFERENCA DE MODELO JA DECLARADA | 0 | -- |
| (d) LIMITE DO COMPARADOR | **4** | 7,1% |
| **total** | **56** | 100% |

O balde (a) 21 pontos vem de **8 defeitos-raiz distintos** (um deles,
`Knight Vigilant`, se repete 14x -- uma vez por classe, porque a aba
Dedication Feats e compartilhada entre todas). Contando por defeito-raiz, nao
por ocorrencia: **8 defeitos novos**.

## 3. A tabela dos 56

| registro | classe | nivel | aba | balde | prova |
|---|---|---:|---|:---:|---|
| Chelaxian Scion Dedication | Guardian | 1 | Dedication | b | AP #223 Hell's Destiny; 0 hits na base do PB |
| Knight Vigilant | Guardian | 1 | Dedication | a | duplicado aon/foundry, PB usa nome foundry |
| Venture-Gossip Dedication | Guardian | 1 | Dedication | b | Paizo Blog article; 0 hits na base do PB |
| Chelaxian Scion Dedication | Exemplar | 1 | Dedication | b | idem Guardian |
| Knight Vigilant | Exemplar | 1 | Dedication | a | idem Guardian |
| Venture-Gossip Dedication | Exemplar | 1 | Dedication | b | idem Guardian |
| Armor Regiment Training | Commander | 1 | Class Feat | a | duplicado aon/foundry ("Armored..."), PB usa nome foundry, atende=True |
| Chelaxian Scion Dedication | Commander | 1 | Dedication | b | idem Guardian |
| Knight Vigilant | Commander | 1 | Dedication | a | idem Guardian |
| Venture-Gossip Dedication | Commander | 1 | Dedication | b | idem Guardian |
| Chelaxian Scion Dedication | Gunslinger | 1 | Dedication | b | idem Guardian |
| Knight Vigilant | Gunslinger | 1 | Dedication | a | idem Guardian |
| Venture-Gossip Dedication | Gunslinger | 1 | Dedication | b | idem Guardian |
| Chelaxian Scion Dedication | Inventor | 1 | Dedication | b | idem Guardian |
| Knight Vigilant | Inventor | 1 | Dedication | a | idem Guardian |
| Venture-Gossip Dedication | Inventor | 1 | Dedication | b | idem Guardian |
| Burning Demand | Kineticist | 1 | Class Feat | b | Pathfinder #223 Hell's Destiny; 0 hits nos 130+355 itens do PB |
| Drowning Mist | Kineticist | 1 | Class Feat | b | Pathfinder #223 Hell's Destiny; idem |
| Flash Forge | Kineticist | 1 | Class Feat | a | duplicado aon/foundry ("Flashforge"), PB usa nome foundry |
| Liberating Dive | Kineticist | 1 | Class Feat | b | Pathfinder #223 Hell's Destiny; idem |
| Voice of the Elements | Kineticist | 1 | Class Feat | a | duplicado aon/foundry ("Voice of Elements", sem "the"), PB usa nome foundry |
| Chelaxian Scion Dedication | Kineticist | 1 | Dedication | b | idem Guardian |
| Knight Vigilant | Kineticist | 1 | Dedication | a | idem Guardian |
| Venture-Gossip Dedication | Kineticist | 1 | Dedication | b | idem Guardian |
| Chelaxian Scion Dedication | Swashbuckler | 1 | Dedication | b | idem Guardian |
| Knight Vigilant | Swashbuckler | 1 | Dedication | a | idem Guardian |
| Venture-Gossip Dedication | Swashbuckler | 1 | Dedication | b | idem Guardian |
| Chelaxian Scion Dedication | Thaumaturge | 1 | Dedication | b | idem Guardian |
| Knight Vigilant | Thaumaturge | 1 | Dedication | a | idem Guardian |
| Venture-Gossip Dedication | Thaumaturge | 1 | Dedication | b | idem Guardian |
| Whisper of Warning | Animist | 2 | Class Feat | a | duplicado aon/foundry ("Whispers...", plural), PB usa nome foundry |
| Chelaxian Scion Dedication | Animist | 2 | Dedication | b | idem Guardian |
| Knight Vigilant | Animist | 2 | Dedication | a | idem Guardian |
| Venture-Gossip Dedication | Animist | 2 | Dedication | b | idem Guardian |
| Major Lesson | Witch | 2 | Class Feat | d | PB representa como 3 entradas (I/II/III); nos temos 1 registro |
| Syu Tak-Nwa's Deadly Hair | Witch | 2 | Class Feat | d | AoN so tem o nome com prefixo; PB usa "Deadly Hair" -- par de equivalencia faltando |
| Syu Tak-Nwa's Hexed Locks | Witch | 2 | Class Feat | d | idem, PB usa "Hexed Locks" |
| Syu Tak-Nwa's Skillful Tresses | Witch | 2 | Class Feat | d | idem, PB usa "Skillful Tresses" |
| Chelaxian Scion Dedication | Witch | 2 | Dedication | b | idem Guardian |
| Knight Vigilant | Witch | 2 | Dedication | a | idem Guardian |
| Venture-Gossip Dedication | Witch | 2 | Dedication | b | idem Guardian |
| Vermillion Threads | Magus | 2 | Class Feat | a | duplicado + grafia errada: AoN "Vermilion" (1 L) x nosso registro foundry "Vermillion" (2 L) |
| Chelaxian Scion Dedication | Magus | 2 | Dedication | b | idem Guardian |
| Knight Vigilant | Magus | 2 | Dedication | a | idem Guardian |
| Venture-Gossip Dedication | Magus | 2 | Dedication | b | idem Guardian |
| Automatic Psychic Action | Psychic | 2 | Class Feat | a | duplicado aon/foundry ("Autonomic..."), PB usa nome foundry |
| Deepest Wellspring | Psychic | 2 | Class Feat | a | fusao Legacy<->Remaster perdida (remaster_id aponta pra Amp Focus, nv12) |
| Chelaxian Scion Dedication | Psychic | 2 | Dedication | b | idem Guardian |
| Knight Vigilant | Psychic | 2 | Dedication | a | idem Guardian |
| Venture-Gossip Dedication | Psychic | 2 | Dedication | b | idem Guardian |
| Chelaxian Scion Dedication | Oracle | 2 | Dedication | b | idem Guardian |
| Knight Vigilant | Oracle | 2 | Dedication | a | idem Guardian |
| Venture-Gossip Dedication | Oracle | 2 | Dedication | b | idem Guardian |
| Chelaxian Scion Dedication | Summoner | 2 | Dedication | b | idem Guardian |
| Knight Vigilant | Summoner | 2 | Dedication | a | idem Guardian |
| Venture-Gossip Dedication | Summoner | 2 | Dedication | b | idem Guardian |

## 4. DEFEITO NOSSO -- 8 achados, detalhados

Sete dos oito sao a MESMA familia de causa raiz: um extrator (AoN) e outro
(Foundry) capturaram o **mesmo feat real da Paizo** com uma grafia de nome
levemente diferente (palavra a mais/a menos, letra trocada, singular/plural).
`reconciliar.py` casa por slug do nome, e como os slugs diferem, os dois
nunca colidiram -- **os dois sobreviveram como registros independentes e
independentemente selecionaveis**. O comparador so acusa UM lado (o que nao
bate com o nome que o Pathbuilder usa); o outro lado silenciosamente "casa" e
esconde o par inteiro do placar -- exatamente o mesmo mecanismo que a rodada 6
already descreveu pra `Incredible Familiar` (secao 4 dela, "colisao de
normalizacao"), so que ali era colisao de DOIS registros NOSSOS querendo ser
UM; aqui e o OPOSTO -- dois registros nossos que deveriam ser UM continuam
DOIS.

O oitavo (`Deepest Wellspring`) e uma familia diferente: fusao Legacy<->Remaster
que a propria AoN documenta e que o pipeline nao aplicou.

### 4.1 -- `Knight Vigilant` / `Knight Vigilant Dedication` (Guardian, todas as 14 classes)

**A prova.** Dois registros, mesmo feat, Character Guide pg. 94, nivel 6:

| campo | `wb:feat/knight-vigilant` | `wb:feat/knight-vigilant-dedication` |
|---|---|---|
| `name` | Knight Vigilant | Knight Vigilant Dedication |
| `xref` | `aon: feat-1092` | `foundry: Compendium....1YFrl8I6ZGo7BIM9` |
| `prov.name` | aon | foundry |
| `requires` | identico | identico |
| `grants` | `[{proficiency.religion: expert}]` | `[{proficiency.religion: expert}]` |

AoN (`feat-1092`) chama o feat de "Knight Vigilant", sem sufixo -- e essa e a
convencao da Paizo pra feat de entrada de arquetipo. O compendio do Foundry
apelida com "Dedication" no fim, convencao DELE. O Pathbuilder usa a
convencao do Foundry ("Knight Vigilant Dedication", conferido em
`docs/comparacao/pathbuilder-guardian-class_feat-nv1.json`, aba Dedication
Feats, nivel 6, `atende: false`). Isso derruba a classificacao das rodadas
1/3/6, que chamavam este item de "recorte de fonte, ja identificado" -- **nao
e recorte de fonte**, o Pathbuilder TEM o feat, so com outro nome. E o mesmo
defeito 14 vezes (uma por classe) porque a aba Dedication e compartilhada.

**Efeito na ficha.** Um personagem membro dos Knights of Lastwall (`acesso`
satisfeito) veria DOIS botoes -- "Knight Vigilant" e "Knight Vigilant
Dedication" -- pra pegar o mesmo feat, e cada um teoricamente ocuparia um
slot de escolha independente (a base nao os declara mutuamente exclusivos).

**Conserto proposto (nao aplicado).** Fundir os dois num so registro. Manter
`wb:feat/knight-vigilant` como canonico (nome bate com a Paizo/AoN), anexar
`Knight Vigilant Dedication` em `aliases`, herdar `xref.foundry` do outro
lado, e apagar `wb:feat/knight-vigilant-dedication`. Regra geral pro
`reconciliar.py`: quando dois candidatos tem MESMO `book`+`page`+`level`+
`traits` (`archetype`+`dedication`) e o nome de um e o nome do outro **+/-
"Dedication"**, tratar como o mesmo feat antes de gerar slug.

### 4.2 -- `Armor Regiment Training` / `Armored Regiment Training` (Commander)

**A prova.** `feat-7792` no AoN e "Armor Regiment Training" -- unico resultado
pra "regiment training" no dump inteiro. Nossa base tem DOIS registros,
Battlecry! pg. 30, nivel 1:

| campo | `wb:feat/armor-regiment-training` | `wb:feat/armored-regiment-training` |
|---|---|---|
| `name` | Armor Regiment Training | Armored Regiment Training |
| `xref` | `aon: feat-7792` | `foundry: ...sebJQz7jABxL0pQS` |
| `source.remaster` | `false` | `true` (mas o feat nao existe com nome remasterizado no AoN) |

O Pathbuilder lista "Armored Regiment Training", nivel 1, **`atende: true`**
(conferido em `pathbuilder-commander-class_feat-nv1.json`) -- ele TEM o feat.
As rodadas anteriores (1/3/6) diziam "confirmado ausente em TODAS as abas do
Pathbuilder... falha de importacao do lado dele". **Estava errado**: nao e
falha de importacao dele, e duplicata nossa com nome torto.

**Conserto proposto.** Mesma fusao: manter `armor-regiment-training` (bate com
AoN), `Armored Regiment Training` vira alias, herdar `xref.foundry`, apagar o
duplicado. O flag `source.remaster: true` no registro que sera descartado
tambem estava errado -- nao ha versao remasterizada distinta no AoN.

### 4.3 -- `Flash Forge` / `Flashforge` (Kineticist)

**A prova.** AoN `feat-4251`: "Flash Forge" (duas palavras), Rage of Elements
pg. 30, nivel 1. Nossa base tem `wb:feat/flash-forge` (aon, "Flash Forge") e
`wb:feat/flashforge` (foundry, "Flashforge", uma palavra). O Pathbuilder lista
"Flashforge" (conferido na aba Class Feats de `pathbuilder-kineticist-*`,
nivel 1). Mesmo padrao dos dois anteriores.

**Conserto proposto.** Manter `flash-forge` (bate com AoN), `Flashforge` vira
alias, herdar `xref.foundry`+`xref.pf2etools`.

### 4.4 -- `Voice of the Elements` / `Voice of Elements` (Kineticist)

**A prova.** AoN `feat-4188`: "Voice of the Elements", Rage of Elements pg.
21, nivel 2, unico resultado no dump pra esse feat de Kineticist (existe
tambem um "Voice of the Elements" DIFERENTE, nivel 5, trait `dragonblood`,
Draconic Codex -- feat nao relacionado, so nome igual, ja desmembrado
corretamente). Nossa base tem:

| campo | `wb:feat/voice-of-the-elements-kineticist` | `wb:feat/voice-of-elements` |
|---|---|---|
| `name` | Voice of the Elements | Voice of Elements |
| `xref` | `aon: feat-4188` | `foundry: ...4TZNsGF9LNBxAWmS` |
| `grants` | `[]` (vazio, `mechanized: false`) | 6 linguas + bonus de Carisma (completo) |

Este e o unico dos sete pares onde o lado ERRADO no nome (`Voice of
Elements`, sem "the") e o lado com o MECANISMO implementado -- o AoN-side,
com nome certo, tem `grants: []`. O Pathbuilder usa "Voice of Elements" (sem
"the"), `atende: false` no nivel 1 (gate elemental nao escolhido).

**Conserto proposto.** Fundir mantendo o NOME do registro AoN ("Voice of the
Elements", correto) e os `grants` do registro Foundry (completo). Resultado:
um registro so, nome certo, efeito certo.

### 4.5 -- `Automatic Psychic Action` / `Autonomic Psychic Action` (Psychic)

**A prova.** AoN `feat-8352`: "Automatic Psychic Action", Dark Archives
(Remastered) pg. 29, nivel 20. Nossa base tem `wb:feat/automatic-psychic-action`
(aon, nome certo, `grants: []`) e `wb:feat/autonomic-psychic-action` (foundry,
"Autonomic", `grants: [{grant_item: Quickened}]`, completo). O Pathbuilder usa
"Autonomic Psychic Action" (typo que o proprio compendio do Foundry carrega --
nao e invencao do Pathbuilder, e herdado da mesma fonte errada que nos
tambem temos). Mesmo padrao de 4.4: nome certo sem efeito, nome errado com
efeito.

**Conserto proposto.** Fundir mantendo o nome AoN ("Automatic Psychic
Action") e os `grants` do registro Foundry (`Quickened`).

### 4.6 -- `Vermillion Threads` / `Vermilion Threads` (Magus)

**A prova.** AoN `feat-7083`: "**Vermilion** Threads" (uma letra L), Tian Xia
Character Guide pg. 113, nivel 10. Nossa base tem `wb:feat/vermilion-threads`
(aon, grafia certa, `xref.aon: feat-7083`) e `wb:feat/vermillion-threads`
(foundry, "**Vermillion**" com duas letras L, so `xref.foundry`, SEM
`xref.aon`). O Pathbuilder usa "Vermilion Threads" (uma L, `atende: false`,
pre-requisito de subclasse do Magus nao satisfeito) -- **ele carrega Tian Xia
Character Guide**, contradizendo a classificacao da rodada 6 ("obra que o
Pathbuilder nao carrega"). Os dois registros tem `requires` e `grants`
identicos (ambos `grants: []`, nenhum mecanizado), entao a fusao nao perde
nada de mecanica.

**Conserto proposto.** Manter `vermilion-threads` (uma L, bate com AoN e com o
Pathbuilder) como canonico, `Vermillion Threads` (duas L) vira alias
(a grafia errada e comum o bastante pra merecer ficar buscavel), herdar
`xref.foundry`, apagar o duplicado. Reclassificar a nota da rodada 6 (nao e
recorte de fonte).

### 4.7 -- `Deepest Wellspring` -> deveria ser `Amp Focus` (Psychic)

Familia DIFERENTE dos seis acima: nao e par aon/foundry com nome parecido, e
fusao Legacy<->Remaster que a **propria AoN ja declara** e que
`fundir_renomeados.py` nao aplicou.

**A prova.** `feat-3693` no AoN: "Deepest Wellspring", Dark Archive (legado)
pg. 29, nivel 18, campo **`remaster_id: [feat-8336]`**, **`remaster_name:
[Amp Focus]`**. `feat-8336`: "Amp Focus", Dark Archives (Remastered) pg. 28,
nivel **12**, campo **`legacy_id: [feat-3693]`**, **`legacy_name: [Deepest
Wellspring]`**. O texto mudou junto com o nome e o nivel: a versao legada
recupera 3 Focus Points no Refocus (se gastou >= 3 desde o ultimo), a
remasterizada simplesmente recupera TODOS os Focus Points no Refocus --
mecanica mais simples, nivel mais baixo (12 em vez de 18).

Nossa base tem **os dois como registros independentes**: `wb:feat/amp-focus`
(nivel 12) E `wb:feat/deepest-wellspring` (nivel 18) -- um Psychic de nivel 18
veria "Deepest Wellspring" como escolha valida, quando pelas regras atuais
esse feat **nao existe mais** (foi substituido por Amp Focus, dois niveis
antes). O Pathbuilder so mostra "Amp Focus" (conferido: nao aparece
"wellspring" na lista completa da sonda) -- ele segue o remaster
corretamente; somos nos que vazamos o legado como se fosse independente.

**Por que a fusao automatica nao pegou.** Por design (README, item 1),
"campo estruturado divergente veta a fusao" -- e o `level` diverge (18 x 12).
Essa guarda existe pra nao fundir coisas realmente diferentes por engano, mas
aqui ela produziu um falso negativo: quando `remaster_id`/`legacy_id` do AoN
**explicitamente** linkam os dois lados, a mudanca de nivel e um efeito
LEGITIMO do remaster (Paizo relevela feats na conversao), nao evidencia de
que sao feats diferentes.

**Conserto proposto.** Em `fundir_renomeados.py`, quando o par vem de
`remaster_id`/`legacy_id` explicito do AoN, permitir que `level` divirja sem
vetar a fusao (a mesma excecao ja poderia se aplicar a outros pares
remasterizados que mudaram de nivel -- vale conferir se ha mais casos assim
na base inteira, ver secao 6). Registro final: nome/nivel/mecanica da
REMASTERIZADA (Amp Focus, nv12), com "Deepest Wellspring" como alias
historico.

## 5. RECORTE DE FONTE -- 31 pontos, confirmados

**`Chelaxian Scion Dedication`** (14x, uma por classe) -- `feat-8971`,
Pathfinder #223: Hell's Destiny pg. 222. Busquei "chelaxian" na lista
COMPLETA da sonda do Pathbuilder (todas as abas, 355+ itens) para Guardian: 0
hits. Mesmo AP ja identificado na 1a rodada como nao carregado pelo
Pathbuilder.

**`Venture-Gossip Dedication`** (14x) -- `feat-7599`, fonte "Foolish
Housekeeping and Other Articles" (post de blog da Paizo, nao um livro).
Busca "venture"/"gossip" na sonda completa: 0 hits. Confirmado, mesmo padrao.

**`Burning Demand`, `Drowning Mist`, `Liberating Dive`** (Kineticist,
niveis 12/12/14) -- os tres sao **Pathfinder #223: Hell's Destiny**
(`feat-8977`, `feat-8978`, `feat-8979`), pg. 228-229. Busquei "burning
demand"/"drowning mist"/"liberating dive" (e variantes de palavra) na lista
COMPLETA de 355 itens da sonda (todas as abas): **0 hits** nos tres.
**Corrijo aqui a classificacao da rodada 6**, que atribuiu esses 3 a
"candidato de nivel futuro fora da janela" -- isso e FALSO: a mesma sonda tem
13 feats de nivel 12 e 8 de nivel 14 pro Kineticist (a lista do Pathbuilder
cobre os 20 niveis inteiros, marcados vermelho quando fora de alcance, nao so
a janela do nivel medido). A causa real, verificada agora, e mais simples e
mais forte: **mesmo AP dos outros 2 recortes ja confirmados** (Hell's
Destiny), o Pathbuilder simplesmente nao carrega o livro.

## 6. LIMITE DO COMPARADOR -- 4 pontos

**`Major Lesson`** (Witch, nivel 10) -- o texto do feat permite escolhe-lo de
novo nos niveis 14 e 18. O Pathbuilder representa isso como tres entradas na
lista ("Major Lesson I/II/III"); nossa base tem um registro. Familia ja
descrita na rodada 6 (secao 5.4): recorte de REPRESENTACAO, nao numero
errado.

**`Syu Tak-Nwa's Deadly Hair`, `Syu Tak-Nwa's Hexed Locks`, `Syu Tak-Nwa's
Skillful Tresses`** (Witch, niveis 6/8/4) -- `feat-2690`/`2691`/`2689`,
Pathfinder #166: Despair on Danger Island. Conferido no dump inteiro do AoN:
**nao existe** nenhuma entrada com os nomes genericos ("Deadly Hair", "Hexed
Locks", "Skillful Tresses") -- so os com o prefixo do NPC. O Pathbuilder usa
os genericos (confirmado na sonda). Mesmo mecanismo ja documentado e
tabulado em `equivalencias-pathbuilder.json` pra outros 35+ pares (`Jalmeri
Heavenseeker -> Heavenseeker`, etc.) -- essas 3 sao pares NOVOS que ainda nao
entraram na tabela. Nao e defeito: e o arquivo de equivalencias faltando 3
linhas, e ele esta fora do escopo deste item (nao editado).

## 7. O que confirma a suspeita do item 84

Achar 8 defeitos-raiz num balde de 56 pontos que a propria rodada 6 tinha
classificado como "zero defeitos" mostra exatamente o risco que o item 84
apontou: o balde "so nosso" e onde um registro que EXISTE mas esta com nome
torto se esconde -- o comparador so acusa o lado que nao bate, e o lado que
bate silenciosamente conta como "em comum", escondendo o par inteiro do
placar resumido. As rodadas 1, 3 e 6 leram o resumo impresso (truncado, sem
nivel) e nao foram atras da lista bruta linha a linha; foi so ao inspecionar
`pipeline/base/index.json` por nome aproximado que os pares apareceram.

## 8. O que nao rodou / nao conclusivo

- **Nao ha item "nao conclusivo"** -- todos os 56 fecharam em uma das 3
  classificacoes com prova direta (AoN dump + base + sonda bruta). Nenhum
  ficou em aberto.
- **Divergencia 57 vs 56** (secao 0): nao encontrei o 57o ponto. Registrado,
  nao investigado mais a fundo -- provavel erro de soma no texto do item 84,
  mas fica como duvida honesta, nao afirmacao.
- **Escopo NAO coberto por este item:** os sete pares aon/foundry
  encontrados (secao 4.1-4.6) sao a PONTA que apareceu no recorte de 56
  pontos das 14 classes novas. Nao auditei a base inteira (19.606 registros)
  atras de mais pares "nome A" / "nome A + sufixo" / "nome A sem uma
  palavra" -- é bem provavel que existam mais fora desta amostra. Vale um
  item de TODO proprio: uma varredura geral por pares de nome quase-identico
  entre registros do mesmo `kind`+`level`+`traits` com proveniencia
  `aon` de um lado e `foundry` do outro.
- **`fundir_renomeados.py` -- quantos outros pares `remaster_id`/`legacy_id`
  tem divergencia de nivel** como o caso do item 4.7 (`Deepest
  Wellspring`/`Amp Focus`)? Nao contei -- fica como escopo de auditoria
  futura, fora deste item (o item pede triagem do balde "so nosso", nao
  varredura da fusao Legacy/Remaster inteira).
- **Nenhum arquivo `motor/comparar_pathbuilder.py` ou
  `docs/comparacao/equivalencias-pathbuilder.json` foi editado**, por regra
  do item. Os `comparacao-*.json` foram REGERADOS (saida normal do script,
  nao alterei o script) e bateram byte a byte com o que ja estava versionado.
