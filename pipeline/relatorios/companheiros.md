# Extrator de companheiros -- relatorio

Fonte: `pipeline/extratores/companheiros.py`. Saida: `pipeline/saida/companheiros.json`
(312 registros, 0 ids duplicados). Dump bruto: `pipeline/dump_aon.py`
-> `pipeline/dados_brutos/aon_companheiros.json` (405 docs, elasticsearch `aon`).
O script ad-hoc original (`_wb_dump_companheiros.py`) foi substituido por ele.

## Contagem por kind

| kind | subtype | AoN bruto (legado+remaster) | apos dedup nome | emitidos |
|---|---|---:|---:|---:|
| `animal-companion` | especie | 114 | 96 | 96 |
| `animal-companion` | especializacao | 17 | 11 | 11 |
| `animal-companion` | avancado | 8 | 5 | 5 |
| `animal-companion` | unico | 1 | 1 | 1 |
| `familiar-ability` | -- | 191 | 133 | 133 |
| `familiar-specific` | -- | 47 | 39 | 39 |
| `eidolon` | -- | 13 | 13 | 13 |
| `apparition` | -- | 14 | 14 | 14 |
| **total** | | **405** | **312** | **312** |

O numero "volume esperado" do briefing (114/191/47/13) e a contagem **bruta** do
AoN, que mistura entradas legado e remaster do mesmo bicho/habilidade sob nomes
identicos (ex.: "Badger" aparece 2x -- Core Rulebook legado + Player Core
remaster). Segui o mesmo padrao de `feats.py`: dedup por `chave(nome)`,
vencedor e quem **nao** tem `remaster_id` (nao foi substituido = versao
corrente); o perdedor vira `legado_de` no registro vencedor. 93 homonimos
deduplicados no total.

## Familias descobertas alem da lista do briefing

Busquei nas categorias do elasticsearch AoN e no trait `Minion` (agregacao por
`category`, ver script de sondagem descartado do scratchpad -- nao ficou no
projeto). Achados:

- **`animal-companion-specialization`** (Ambusher, Bully, Daredevil, Racer,
  Tracker, Wrecker, Shade, Deep Diver, Steadfast Strider, Wildfire Scorcher,
  Wind Chaser) -- o tipo de treino que o companheiro recebe (Core Rulebook
  pg. 217/Player Core). Nao e especie nova: qualquer especie pode receber
  qualquer especializacao compativel. Modelado como `subtype: especializacao`
  dentro do MESMO kind `animal-companion` -- nenhuma regra do jogo mira
  "especializacao" sem mirar "companheiro animal" tambem, entao nao viram
  kind proprio (mesmo raciocinio de `class-feature` variar por classe sem
  virar kind por classe).
- **`animal-companion-advanced`** (Nimble, Savage, Indomitable, Genie-Touched,
  Unseen) -- o proximo degrau depois de mature. Mesmo argumento, `subtype:
  avancado`.
- **`animal-companion-unique`** (Fiery Leopard, de uma aventura especifica) --
  1 registro, `subtype: unico`.
- **`apparition`** (14) -- espirito do Animist. **Esta sim e kind proprio**:
  feat/pericia de Animist fala do espirito e nenhum outro companheiro fala
  dele (mesmo teste que separa eidolon de companheiro animal na spec). Traz
  `pericias` (Lores concedidas) e `magias` (a lista de magias do repertorio do
  espirito por rank).
- **Eidolon "Swarm"** (Battlecry!) confirma que a lista de tipos de eidolon
  (13) ja inclui o que voce citou como duvida -- nao precisou de kind
  separado, e so mais um tipo dentro de `eidolon` (Angel, Beast, Construct,
  Demon, Dragon, Elemental, Fey, Plant, Psychopomp, Swarm, Undead, Anger
  Phantom, Devotion Phantom).

O que **procurei e nao achei como familia separada**:

- **Companheiro de constructo (Inventor)**: nao existe. Os feats que cheiram a
  isso ("Prototype Companion", "It's Alive!", "Advanced/Incredible/Paragon
  Construct Companion", linha do "Clockwork Reanimator") **reusam o mesmo
  `animal-companion`** -- a especie base concedida e reflavorizada como
  constructo/morto-vivo pelo feat, nao e um statblock proprio. Ja aparece na
  lista de especies: "Gray Bladeling" (traits Construct+Undead), "Skeletal
  Mount"/"Zombie Mount"/"Skeletal Servant" (Undead), os 6 elementais
  (Rage of Elements). Confirma a regra do briefing na pratica: nenhum feat
  fala "seu constructo" e nao "seu companheiro animal" -- e sempre companheiro
  animal por baixo.
- **Montaria/steed avulsa, esquadrao (Battlecry!)**: nao existem como
  categoria propria no AoN. "Squad" so aparece em `creature` (bestiario, fora
  de escopo pela spec-base) e `feat` (Squad Tactics). Steed idem (so
  criatura/spell/feat). Se Battlecry! define companheiro de esquadrao como
  mecanica propria, nao esta indexado como categoria separada no AoN hoje --
  ficaria para uma extracao futura se/quando aparecer.

## Fontes

O aviso do briefing se confirmou por inteiro: o Foundry pinado **so** tem
`familiar-abilities` como Item de primeira classe (`packs/pf2e/
familiar-abilities/`, 111 arquivos `type: action` com `system.rules`).
Animal companion, especializacoes/avancados/unicos, familiar-specific,
eidolon e apparition **nao existem no Foundry pinado** -- confirmado por
`find ... -iname "*compan*"` e `-iname "*eidolon*"` sem resultado.
Logo:

- **AoN e a fonte de 100% de `name`/`traits`/`rarity`/`text`/`level`/`stats`**
  em toda a familia. Sem segunda fonte independente, `conflitos` fica sempre
  vazio aqui (nao ha divergencia possivel com fonte unica -- registrado
  como `conflitos_totais: 0`, nao e ausencia de checagem, e ausencia de
  segunda fonte).
- **`familiar-ability` e a unica com `grants` mecanico**: casei por
  `chave(nome)` contra os 111 itens do Foundry. 73 de 133 casaram (55%);
  os 60 sem match sao habilidades de livros mais novos que nao estao no
  compendio do Foundry pinado (ex.: "Elemental Diplomat", "Sorcerous
  Sweets", "Aeon Stone Reservoir") -- gap de cobertura do pin, nao bug do
  matching. Das 73 casadas, 72 converteram limpo (`mechanized: true`); so 2
  `ActiveEffectLike` e 1 `Note` cairam fora do vocabulario pequeno que
  escrevi pra essa familia (subset de `RE_CONVERTIDOS` do `feats.py`).
  `license`/`remaster` de `familiar-ability` tambem vem do Foundry
  (`publication`) quando casa.
- **`license`/`remaster` do resto da familia** (animal-companion, eidolon,
  apparition, familiar-specific, e familiar-ability sem match) usa a
  **mesma heuristica que `feats.py` ja usa como fallback**: sem
  `remaster_id` -> versao corrente -> ORC/remaster; com `remaster_id` ->
  foi substituida -> OGL/legado. Diferenca importante: em `feats.py` essa
  heuristica e um *fallback* atras de uma tabela livro->licenca cruzada
  com o Foundry. Aqui **e a unica fonte**, entao fica marcada em
  `prov.source = "aon(heuristica:remaster_id)"` -- nao e a mesma confianca
  de quando ha cruzamento real. Pra confirmar de verdade precisaria de uma
  segunda fonte com `publication.license` explicito, que essa familia nao
  tem no Foundry.

## Como modelei a progressao do companheiro animal

O texto do AoN category=`rules` ("Young Animal Companions", "Mature Animal
Companions", Core Rulebook pg. 214) confirma a cadeia **young -> mature ->
(nimble | savage | indomitable | genie-touched | unseen) -> incredible ->
specialized**, mas **nao virou registro proprio**: e a mesma criatura
avancando, nao uma nova identidade. Modelagem escolhida:

- **`especie`** carrega o statblock **jovem** (e o unico publicado -- "the
  first animal companion most characters get"): atributos (modificadores
  Str/Dex/Con/Int/Wis/Cha), tamanho, velocidade, sentidos, pericia inicial,
  HP, ataques (parseados do texto: 96/96 = 100% dos ataques Melee casaram
  com o regex), Support Benefit e Advanced Maneuver.
- **`mature`/`incredible`/`specialized`** **nao tem entrada propria no AoN**
  (nao sao categoria, sao regra de avanco embutida no texto de "Mature
  Animal Companions" e nos feats gerais Incredible/Specialized Companion).
  Nao materializei essas etapas como registro -- ficou faltando (ver secao
  "nao consegui estruturar"). O texto da regra "Mature" foi lido mas nao
  emitido em nenhum arquivo (so serviu pra confirmar a cadeia).
- **`nimble`/`savage`/`indomitable`/`genie-touched`/`unseen`** SAO categoria
  propria no AoN (`animal-companion-advanced`, subtype `avancado`) --
  emitidos com o texto completo do que cada um modifica (ex.: Nimble = "+2
  Dex mod, +1 Str/Con/Wis mod, dano desarmado +2 dado, Acrobatics vira
  expert, ataques ficam magicos").
- **`ambusher`/`bully`/`daredevil`/... (especializacoes de tipo)** idem,
  subtype `especializacao`.

A logica de "e o mesmo Ator avancando" bate com a spec-personagem: o app
aplica esses registros como modificadores sequenciais sobre o statblock
`especie`, nao como uma nova escolha de Ator.

## O que escala com nivel, e de qual nivel

Dois "nivel" **diferentes** aparecem nesta familia -- vale a mesma discussao
de multiclasse da spec de regras:

1. **`level` do registro `animal-companion:especie`** = nivel MINIMO de
   personagem pra poder escolher aquela especie (gate de raridade/poder, nao
   de progressao). 84 das 96 especies tem `level: 1` (disponivel desde o
   inicio); as outras 12 sao exoticas com gate mais alto -- ex.: Giant Eel/
   Hippocampus nivel 4, Riding Tarantula/Giant Frog/Orca nivel 6, Wyvern
   nivel 10, Roc/Umbrella Mushroom/Giant Wasp/Griffon/Hippogriff/
   Thruneosaurus Rex nivel 14-16. Esse "nivel" e sempre **character_level**
   de quem esta escolhendo o feat que concede o companheiro (Animal
   Companion / Hunt Prey / etc) -- nao ha versao "class_level" disso, porque
   a escolha de especie e feita uma vez, no feat, nao repetida por classe.
2. **O avanco young -> mature -> ... -> specialized** escala com "o nivel do
   seu companheiro", e a regra do Core Rulebook e explicita: *"A companion
   has the same level you do."* Ou seja, **companion level == o nivel de
   quem concedeu o companheiro** -- normalmente `class_level` da classe que
   deu o feat/class-feature Animal Companion (Ranger, Druid com Animal
   Order, ou o arquetipo Beastmaster), nao necessariamente `character_level`
   total do personagem em multiclasse. Isso e dado de regra (nao fica no
   registro do companheiro -- fica na progressao da classe/arquetipo que
   concede o companheiro, fora do escopo desta extracao) mas e importante
   registrar aqui: **o predicado certo pro motor e `class_level` da classe
   doadora**, nunca `character_level` cru, exatamente pelo motivo que a
   spec de multiclasse ja levantou.
3. **`familiar-ability`/`familiar-specific`/`eidolon`/`apparition` nao tem
   `level` intrinseco** -- sao escolhidas por slot, nao por nivel do item.
   O que escala com nivel e a **quantidade de slots**, que e regra da CLASSE
   (Witch/Summoner/Animist), fora do escopo desta extracao. Uma pista que
   confirmei no AoN (`rules`, "Familiar and Master Abilities", Core
   Rulebook pg. 218): a base e "channel your magic into **two** abilities"
   por dia -- a tabela completa de quantas abilidades por nivel de mestre
   nao foi extraida aqui (ficaria em `class-feature`/`class`, nao em
   `familiar-ability`).

## O que nao consegui estruturar

- **Etapas `mature`/`incredible`/`specialized` da progressao do companheiro
  animal**: sem entrada propria no AoN, so texto de regra solta. Precisa de
  decisao de modelagem (virar registro sintetico "wb:animal-companion/
  mature" com texto fixo da regra? ou ficar so como constante no motor?)
  antes de implementar -- SDD pede spec primeiro, entao deixei de fora.
- **Atributos por build do eidolon** ("Brutal Beast" vs a build alternativa,
  cada uma com Str/Dex/.../AC/saves proprios): o texto do AoN tem essas
  duas tabelas por tipo de eidolon, mas so extrai a lista `Suggested
  Attacks` (13/13 ok). O bloco de atributos por build ficou como parte do
  `text` (prosa, nao estruturado) -- precisaria de parser dedicado por nao
  ter campo estruturado equivalente ao que `animal-companion` tem.
  `mechanized` de eidolon fica `false` por causa disso.
- **14 habilidades de `familiar-specific` sem resolucao pra
  `familiar-ability`** (ex.: "Skilled (choice of skill)", "Resistance
  (poison)", "Elemental (air only)"): sao variantes parametrizadas de uma
  habilidade base com o parametro dentro do nome; o indice por `chave(nome)`
  exato nao casa. Ficaram marcadas com sufixo `?nao-resolvido` no id pra
  serem visiveis, em vez de silenciosamente descartadas.
- **`grants` de `animal-companion`/`eidolon`/`apparition`**: fica vazio
  (`mechanized: false`) em toda a familia exceto `familiar-ability`, porque
  nao ha rule elements de origem (Foundry nao modela isso) nem uma
  linguagem de `grants` definida pra "statblock de Ator secundario" -- o
  schema-base atual so cobre `grants` como efeito sobre o personagem
  principal. Os dados estruturados (atributos, ataques, velocidade, HP)
  ficam num campo de extensao `stats` no registro (mesmo padrao de
  `feats.py` usar campos extras alem do envelope, ex. `archetype`,
  `feat_category`).
- **Licenca/remaster fora de `familiar-ability`**: heuristica, nao
  confirmada por segunda fonte (ver secao Fontes acima).
- **Kinds novos nao estao na lista "Kinds em escopo" do schema-base**
  (`familiar-specific`, `eidolon`, `apparition` nao aparecem la, so
  `familiar-ability`/`animal-companion`). Precisa dessa spec ser atualizada
  pra incluir os 3 kinds novos -- nao editei o arquivo porque a instrucao
  foi pra nao tocar em mais nada alem dos 3 entregaveis.
