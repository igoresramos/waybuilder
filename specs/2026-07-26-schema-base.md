---
spec: schema-base
project: waybuilder
version: 2
status: aprovada
created: 2026-07-26
updated: 2026-07-27
---

# Schema da base canonica

> **v2 (2026-07-27)** -- reescrita das partes que a auditoria ampla de 26/07
> (`docs/2026-07-26_auditoria-ampla.md`) provou erradas ou ausentes. Mudou:
> fusao legado<->remaster passa a usar chave da fonte e nao apaga registro;
> `mechanized` vira dois campos; `rank` entra no envelope; `relic` e `language`
> entram nos kinds; `prov` ganha vocabulario fechado com marca de inferencia;
> `source.book` e normalizado na escrita; os portoes de qualidade ganham ordem
> de execucao declarada. O que a v1 dizia e continua valendo nao foi tocado.

Contrato unico que **todo** extrator obedece. Escrito antes de qualquer extracao
de proposito: sem isso, cada fonte produz um formato e a reconciliacao vira
retrabalho.

## Principio zero: isto nao e um sistema de jogo

O Waybuilder e um **construtor de personagem**, como o Pathbuilder. Ele nao roda
mecanica de jogo, nao arbitra e nao impede nada. Serve para montar, visualizar e
imprimir um personagem -- o resto acontece na mesa, na base da confianca.

Consequencia direta e mandatoria em todo o resto desta spec:

> **`requires` sugere, nunca bloqueia.** O predicado existe para ordenar e
> filtrar a lista de opcoes relevantes -- "estes feats combinam com o que voce
> tem" -- e para derivar estatistica. Ele **nunca** e usado para negar uma
> escolha ao jogador. Quem quiser pegar algo fora do requisito, pega, e o app
> mostra que esta fora.

Corolarios:

- `mechanized: false` nao e lacuna, e caso normal. O jogador le e resolve.
- Alinhamento, tenet, condicao narrativa ("you died and returned as a ghost"),
  filiacao a organizacao -- tudo isso e **contexto descritivo**, exibido para o
  jogador saber o que esta pegando. Nunca predicado.
- Conteudo cortado pela Paizo (alinhamento, Legacy sem sucessor) fica na base.
  Num jogo caseiro sem aquela restricao, continua valendo.

## Principio

A base e **auto-contida**. Depois de construida, nada nela depende de rede, de
API de terceiro ou de repo externo. As fontes sao *fixadas por commit/data*,
baixadas uma vez para `pipeline/dados_brutos/`, e o build roda offline.

## Fontes fixadas

| Fonte | Pin | Papel |
|---|---|---|
| `foundryvtt/pf2e` | commit `87f9e5028baaa10b70fdc766260b7886def17e04` | mecanica executavel, progressao, ranks numericos |
| `Pf2eToolsOrg/Pf2eTools` | branch `dev`, snapshot datado | pre-requisitos com referencias marcadas |
| Archives of Nethys | dump do Elasticsearch `aon`, datado | texto, cobertura, ponte legado/remaster |

Trocar de pin e uma decisao registrada no LOG, nunca um efeito colateral de
rodar o pipeline.

## Identidade

```
wb:<kind>/<slug>
```

Exemplo: `wb:class-feature/fighter-weapon-mastery`.

O slug e derivado do nome **remaster** quando existe; do legado quando nao.
Nunca do ID de nenhuma fonte -- IDs de terceiros vivem em `xref`.

## Envelope do registro

```json
{
  "id": "wb:class-feature/fighter-weapon-mastery",
  "kind": "class-feature",
  "name": "Fighter Weapon Mastery",
  "aliases": ["Weapon Mastery"],
  "level": 5,
  "traits": ["fighter"],
  "rarity": "common",
  "source": {
    "book": "Player Core", "book_raw": "Pathfinder Player Core", "page": 145,
    "license": "ORC", "remaster": true
  },
  "requires": { "...predicado..." },
  "grants":  [ "...efeitos..." ],
  "text": "wb:text/class-feature/fighter-weapon-mastery",
  "grants_completos": true,
  "requires_parseado": true,
  "xref": {
    "foundry":   "Compendium.pf2e.classfeatures.Item.xxxx",
    "aon":       "class-feature-156",
    "pf2etools": "class-fighter-pc1#WeaponMastery"
  },
  "prov": {
    "name": "aon", "level": "foundry", "grants": "foundry",
    "requires": "pf2etools", "text": "aon",
    "source.license": "waybuilder~inferido:livro"
  },
  "conflitos": [
    {"campo": "level", "foundry": 5, "aon": 5, "pf2etools": 5, "escolhido": "foundry"}
  ]
}
```

- **`prov`** e obrigatorio e por campo. Sem isso nao da para re-sincronizar so o
  que mudou nem auditar divergencia. Formato fechado na secao "Vocabulario de
  `prov`" -- `"aon"` e leitura direta, `"aon~inferido:<regra>"` e derivacao.
- **`conflitos`** so aparece quando as fontes discordam. Divergencia e registrada,
  nunca silenciada.
- **`grants_completos`** / **`requires_parseado`** substituem `mechanized` (ver
  secao proxima). Nunca travam o build.
- **`text`** e uma referencia, nao o texto. A prosa vive em arquivo separado
  (3,6 MB gzip) e carrega sob demanda. **Todo registro emitido tem `text`** --
  quando o AoN nao tem prosa, cai para a descricao do Foundry, e `prov.text`
  registra de quem veio.
- **`rank`** substitui `level` **so em `spell`** -- e o nome remaster do campo.
  Para nao quebrar filtro de nivel no cliente, `spell` emite os **dois**, com o
  mesmo valor; `rank` e o campo canonico e `level` e espelho declarado, escrito
  num ponto so da emissao, com `prov.level = "waybuilder~inferido:espelho-rank"`.
  O portao 2 falha o build se `rank != level` em algum spell -- sem invariante,
  os dois se soltam com o tempo e o filtro do cliente volta a mentir.
- **`aliases`** guarda todo nome pelo qual a entidade ja foi conhecida
  (renomeacao do remaster, nome de outra fonte). A busca resolve por qualquer um.

## `grants_completos` e `requires_parseado`

`mechanized` foi removido. Ele respondia a duas perguntas diferentes com um
booleano so, e cada extrator escolhia qual das duas:

> Medido na v1: **12.742 registros (70,1%)** tinham `mechanized: true` com
> `grants` vazio, e **370** tinham `false` com `grants` cheio -- 72% da base
> contradizendo a propria definicao. O `false` nao se distribuia por registro e
> sim por **kind inteiro** (`trait` 561/561, `deity` 484/484, `skill` 33/33...),
> o que denuncia propriedade do extrator, nao do dado. Em `feat`, `false`
> significava "nao consegui parsear o pre-requisito" -- afirmacao sobre o
> parser, nao sobre o registro.

| campo | pergunta | valores |
|---|---|---|
| `grants_completos` | a mecanica de efeito foi convertida por inteiro? | `true` / `false` / `null` |
| `requires_parseado` | o pre-requisito virou predicado? | `true` / `false` / `null` |

`null` e **"nao se aplica"**, e e o valor obrigatorio quando o kind nao produz
aquele campo por natureza -- `trait`, `skill`, `deity` e `domain` nao tem
`grants`, entao respondem `null`, nunca `false`. Registro sem pre-requisito em
fonte nenhuma tem `requires_parseado: true` com `requires` vazio: nada a parsear
e sucesso, nao falha.

Regra unica, valida para todos os extratores: `grants_completos` e `false`
somente quando a fonte **tinha** mecanica e a conversao perdeu parte dela
(rule element fora do mapa dos 21 convertidos). `requires_parseado` e `false`
somente quando ha `requires_texto` e o predicado saiu vazio ou parcial.

Quais kinds respondem `null`, para nao sobrar decisao por extrator:

| campo | `null` (nao se aplica) |
|---|---|
| `grants_completos` | `trait`, `skill`, `deity`, `domain`, `language`, `archetype` |
| `requires_parseado` | `trait`, `skill`, `language`, `domain`, `deity`, `spell`, `ancestry`, `background` -- exceto se o registro tiver `requires_texto`, e ai vale a regra normal |

`deity` responde `null` em `grants_completos` apesar de alimentar o build do
Clerigo: o que ele da (arma favorecida, fonte divina, dominios) sao **campos
proprios**, nao `grants`. Se algum dia virarem `grants`, o kind sai da lista --
e a mudanca fica registrada aqui, nao escondida num extrator.

Sem essa tabela, duas regras da spec colidiam no mesmo registro: "kind que nao
produz o campo responde `null`" e "registro sem pre-requisito responde `true`".

## Precedencia entre fontes

Por campo, nao por registro:

| Campo | Vence | Motivo |
|---|---|---|
| `grants` (efeito mecanico) | **foundry** | unica com rank numerico e rule elements -- ver nota |
| `requires` (pre-requisito) | **pf2etools** | unica com `{@feat}`/`{@skill}` marcados |
| `text`, `name`, `rarity` | **aon** | e a Paizo; mais completa e atual |
| `level` | foundry, conferido contra pf2etools | ha duas fontes independentes -- divergencia e bug |
| `rank` (so `spell`) | foundry, conferido contra aon | mesmo criterio de `level` |
| `source`, `remaster` | **aon** | tem `remaster_id`/`legacy_id` para a ponte |
| `traits` | **nenhuma -- ver abaixo** | e conjunto, nao valor escalar |

Quando a fonte vencedora nao tem o campo, cai para a proxima na ordem acima e
`prov` registra de quem veio.

> Nota sobre `grants`: a linha da tabela nunca e exercitada, porque **so o
> Foundry produz o campo** -- as outras duas fontes nao tem efeito mecanico
> estruturado. Isso e propriedade das fontes, nao regra morta: se algum dia
> outra fonte passar a emitir efeito, a precedencia ja esta escrita. Registrado
> aqui para nao voltar como "regra que nunca dispara, remover".

**A escolha por precedencia e o registro da divergencia sao a mesma operacao.**
Ela vive em **uma** funcao compartilhada (`pipeline/comum.py`), nao replicada por
extrator.

> Enquanto estava replicada em 7 arquivos, "divergencia nunca silenciada" nao era
> verificavel -- e de fato nao acontecia: 6 kinds (`class-feature`, `background`,
> `heritage`, `familiar-ability`, `ancestry`, `class`) tinham **1.618 registros
> com 2+ fontes e exatamente zero conflitos**, enquanto 145 divergencias reais de
> `source.book` contra o Foundry eram comprovaveis. Os numeros de conflito da v1
> sao **piso**, nao total.

### `source.book` e normalizado na escrita, nao so na comparacao

O valor emitido e a forma canonica; a grafia original fica em `source.book_raw`
quando difere. `strip()` obrigatorio -- inclusive de `\r\n` literal.

> Medido: **10.723 registros (59%)** ficaram com livro de grafia ambigua --
> 26 obras com duas grafias (`Player Core` 2.032 contra `Pathfinder Player Core`
> 83), mais 160 registros com `\r\n` dentro do nome do livro. Qualquer
> agrupamento por livro no cliente -- filtro, cobertura, triagem de licenca --
> dava numero errado.

## Vocabulario de `prov`

Valor de `prov[campo]` e uma string com gramatica fechada:

```
<fonte>                     leitura direta da fonte
<fonte>~inferido:<regra>    valor derivado, nao lido
```

`<fonte>` ∈ `aon | foundry | pf2etools | waybuilder`. `waybuilder` e o proprio
pipeline (valor calculado, nao vindo de fonte externa). `<regra>` vem de lista
fechada, registrada aqui quando nasce: `livro` (licenca inferida do nome do
livro), `remaster_id` (vinculo pela ponte do AoN), `traits` (classe dona inferida
de trait), `nome-aproximado` (casamento por nome normalizado), `diretorio`
(vinculo pelo caminho do pack do Foundry), `espelho-rank` (`level` copiado de
`rank` em `spell`).

Quem infere e quem e citado como fonte: **a inferencia e do pipeline**, entao
licenca derivada do nome do livro e `waybuilder~inferido:livro`, nao
`aon~inferido:livro`. `aon~inferido:<regra>` so quando o valor vem do AoN por
um caminho indireto (`aon~inferido:nome-aproximado`).

Regra: **nao existe `prov` com valor `"desconhecida"`**. Se a fusao nao sabe de
onde veio o campo, ela nao tem o direito de adotar o campo.

> Na v1, `prov` misturava 8 formatos livres (`"foundry(deities, por nome)"`,
> `"aon (nome aproximado)"`, `"aon(heuristica:remaster_id)"`) e 152 pontos com
> `"desconhecida"`, o que nenhum consumidor conseguia parsear. 1.440 licencas
> inferidas nao tinham sinal nenhum no registro emitido -- so em `prov` -- e sao
> justamente a base do build publico do item 16 do TODO.

## `traits` e uniao, nao precedencia

Precedencia so cabe quando as fontes **disputam o mesmo slot com valores
alternativos** -- um numero contra outro, uma grafia contra outra. `traits` nao
e isso: e um conjunto onde **cada fonte descreve uma faceta parcial** do mesmo
objeto. Escolher uma fonte joga fora o que a outra sabia.

> Medido: `traits` respondia por **88% dos 2.299 conflitos** da base, e quase
> nenhum era divergencia real. Dos 137 casos com conjuntos totalmente disjuntos:
> 72 eram facetas complementares (foundry lista o trait de arma, aon o de item
> magico), 31 eram ancestria renomeada no remaster, 18 eram granularidade
> diferente. So 16 eram problema de verdade -- e de outra natureza (ver
> "Colisao de identidade").
>
> A escolha estava destruindo dado: `bastard-sword` guardava `two-hand` no lugar
> de `two-hand-d12`, perdendo o dado de dano; e 31 registros carregavam o nome
> **legado** de ancestria (`tiefling`, `aasimar`, `ifrit`) numa base que se
> declara remaster-first.

Regra: `traits` e a **uniao das tres fontes**, aplicada nesta ordem:

1. **Mapa legado -> remaster.** Vive em `pipeline/normalizacao_traits.json`, com
   `prov` por entrada citando fonte e pagina -- entrada sem proveniencia nao
   entra. Hoje: **17 renomeados** (`aasimar`/`tiefling`/`aphorite`/`ganzi` ->
   `nephilim`, `ifrit` -> `naari`, `metamagic` -> `spellshape`, `negative` ->
   `void`, `positive` -> `vitality`, `good` -> `holy`, `evil` -> `unholy`,
   `gnoll` -> `kholo`, `duergar` -> `hryngar`, `half-elf` -> `aiuvarin`,
   `half-orc` -> `dromaar`, `locathah` -> `athamaru`, `couatl` -> `coatl`,
   `petitioner` -> `shade`) e **9 removidos sem sucessor**. O termo legado vai
   para `aliases_traits`, nunca some.

   > Duas correcoes ao rascunho inicial desta regra, ambas verificadas no AoN:
   > **`oread`, `sylph` e `undine` NAO viraram `naari`** -- so `ifrit` renomeou.
   > A familia Geniekin do Monster Core 2 lista Naari, Oread, Suli, Sylph e
   > Undine como cinco nomes irmaos distintos, nao um merge.
   > E **`illusion` sobreviveu ao remaster** (Player Core p.457): das oito
   > escolas de magia, sete foram eliminadas, essa nao.
2. **Absorcao por granularidade.** O trait parametrizado absorve o base:
   presentes `two-hand-d12` e `two-hand`, fica so `two-hand-d12`. A regra vale
   para todo sufixo de parametro (`-d\d+`, `-\d+`, `-aim-d\d+`).
3. **Uniao do que sobrar**, ordenada alfabeticamente.

`prov.traits` passa a registrar a **lista de fontes que contribuiram**, nao uma
vencedora: `"traits": ["foundry", "aon"]`.

## Fusao legado <-> remaster

Politica de conteudo (decidida pelo Igor, inalterada): **nome nao importa, regra
e conteudo importam.** `Power Attack` e `Vicious Swing` sao a mesma coisa e viram
um registro so, com todos os nomes em `aliases`.

O que mudou e o **criterio de decidir se sao a mesma coisa**:

> A v1 decidia por similaridade de prosa (Jaccard >= 0,62, >= 15 tokens
> distintivos). Auditado contra o `remaster_id` do AoN: **so 35% das 597 fusoes
> estavam certas**; 393 (65,8%) uniram registros com `level`, `price_cp` ou
> `damage` diferentes -- o dado ja dizia que eram entidades distintas.
> `wb:equipment/aeon-stone` engoliu 24 pedras distintas; `Poi` virou `Shield
> Bash`; `Tonfa` virou `Shuan Ji`, do **mesmo livro**. A causa e estrutural:
> itens de uma familia compartilham quase todo o texto e diferem numa linha.
> Prosa e o pior sinal possivel para distingui-los.

1. **A chave e da fonte.** Funde so quando o AoN declara o vinculo
   (`remaster_id` no doc legado apontando para o doc alvo, ou `legacy_id` no
   doc remaster). Prosa entra como **confirmacao**, nunca como decisor.
2. **Um unico veto: categoria diferente.** Legado e alvo tem de ser da mesma
   categoria no AoN e do mesmo `kind` na base.

   > Medido: **351 de 351** class-features com `remaster_id` apontam para um
   > doc de categoria `class` -- `Evasion` (class-feature-25) aponta para
   > `class-56`, que e o **Alchemist**. Sem este veto a feature seria absorvida
   > pela classe. Consequencia aceita: renomeacao real de class-feature
   > (`Armor of Fury` -> `Armor Mastery`) fica sem chave e tem de sair da
   > progressao da classe no Foundry, que esta spec ja elege como fonte do
   > vinculo classe->feature.

3. **O que muda entre legado e alvo e anotado, nao vetado.** `level`,
   `price_cp` ou `damage` divergentes, consolidacao N->1 e data de publicacao
   entram em `historico[].mudou` e no relatorio.

   > A versao anterior desta spec vetava esses tres casos. Medido na ponte do
   > AoN antes de escrever isto: os vetos barram **77,8%** dos pares que a
   > propria fonte declara, e por motivo legitimo. N->1 e o caso **normal** da
   > consolidacao do remaster -- 351 alvos recebem 2+ legados dentro da mesma
   > categoria (`Magic Wand` <- as 10 varas por rank de magia, `Bewitching
   > Bloom` <- as 10 flores). `level`/`price_cp` divergentes sao errata
   > (`Hand of the Mage` nv2 -> `Charlatan's Gloves` nv3). E a fronteira de
   > data e falsa: Rage of Elements e de 2023-08-02 e ha legado declarado
   > publicado em 2024.
   >
   > O que protegia contra o dano da auditoria (`aeon-stone` engolindo 24
   > pedras) nunca foi o guarda: **das 24 pedras, so 5 declaram `remaster_id`**.
   > Era a chave -- e o fato de nada ser deletado.

4. **Nada e deletado.** O registro absorvido permanece na base com
   `superseded_by: ["<id do alvo>"]` -- **lista**, porque 1->N declarado existe
   (`Wish` -> [`Wish`, `Manifestation`]) -- e **com a propria prosa**, que
   difere da do alvo. Some da lista de escolha do construtor, continua
   resolvivel por id e por busca.

5. **Homonimo declarado ocupa dois slots de `xref`.** 5.599 pares declarados
   tem o **mesmo nome** (`Tusks` feat-1286 -> `Tusks` feat-4519), caem no mesmo
   slug e chegam juntos na fusao de id, antes desta etapa. O vigente fica em
   `xref.aon` e o substituido em `xref.legado_aon` -- decidido pela ponte, nao
   pela ordem de leitura. Na v1 o segundo sobrescrevia o primeiro em silencio.

> A v1 deletava (`final = [r for r in base if r["id"] not in absorvidos]`), e o
> relatorio dizia "Nada e descartado" -- o que nao era descartado era o *nome*.
> Efeito colateral rastreado: 8 entradas de `progressao` de classe passaram a
> apontar para id inexistente e 597 chaves de prosa ficaram orfas.

E a metrica do relatorio muda junto: **"zero par nao unido" e recall sem
precisao** -- fundir tudo com tudo tambem daria zero. O relatorio reporta os
dois lados: pares unidos com chave, pares vetados por guarda, e legados sem
chave nenhuma.

## Colisao de identidade

`wb:<kind>/<slug>` assume que nome e unico por kind. **Nao e.** Ha homonimos
legitimos, as vezes no mesmo livro.

> `Death from Above` sao dois feats do War of Immortals: um de arquetipo no
> nivel 8 e um mitico no nivel 16 (p.128). O Foundry separa os dois; o AoN
> indexa so o mitico. A reconciliacao fundiu por slug e produziu uma quimera --
> nivel de um, nome/traits/raridade/texto do outro. `Reckless Abandon` e igual:
> feat de goblin e feat de barbaro nivel 16.

Detector, barato e confiavel:

> **Conflito com valores categoricamente disjuntos nao e divergencia de fonte --
> e sinal de que duas entidades foram fundidas.**

Divergencia real e `8` contra `9`, ou `"God's"` contra `"Gods'"`. Quando uma
fonte diz que o objeto e `archetype` e a outra `mythic`, sao dois objetos.

Quando detectado, o registro e **desmembrado**: cada entidade ganha slug proprio
com sufixo derivado do que as distingue (`wb:feat/death-from-above-mythic`), e
`xref` aponta so para o id da fonte correspondente.

**Ordem importa:** o detector roda **antes** de `fundir()`, sobre as colisoes de
id, e nao depois.

> O portao 7 da v1 ("nome duplicado no mesmo kind") media 0 e sempre mediria:
> `reconciliar.py` funde toda colisao de id **antes** de qualquer verificacao.
> Ele perguntava se existia duplicata depois de a duplicata ter sido eliminada.
> Foi por essa fresta que `death-from-above` passou.

Regra de sufixo, nesta ordem (primeira que distinguir, vence), para o sufixo ser
deterministico e nao depender da ordem de leitura das fontes:

1. trait de categoria que so um lado tem (`-mythic`, `-goblin`)
2. classe ou arquetipo dono (`-fighter`, `-familiar-master`)
3. livro (`-tian-xia-cg`)
4. nivel (`-nv16`)

**Falso positivo conhecido:** sufixo de grau em item (`-greater`, `-major`,
`-true`, `-lesser`) e variante legitima da mesma familia, nao colisao. Nao
desmembrar, nao fundir -- ja sao registros distintos e corretos.

## Nivel de class-feature pertence a classe, nao a feature

Uma class-feature e **um** registro, compartilhado. Quem diz em que nivel ela
entra e a **progressao da classe**, nao a feature.

```json
// wb:class/fighter
"progressao": [
  {"nivel": 7,  "concede": "wb:class-feature/weapon-specialization"},
  {"nivel": 13, "concede": "wb:class-feature/weapon-legend"}
]
// wb:class/wizard
"progressao": [
  {"nivel": 13, "concede": "wb:class-feature/weapon-specialization"}
]
```

O registro `wb:class-feature/weapon-specialization` **nao tem `level`**.

> Descoberto na extracao: o Foundry guarda 1 arquivo por feature referenciado
> por N classes com nivel proprio cada. Modelar `level` como escalar na feature
> obriga a duplicar o registro por classe -- 27 nomes viravam 187 registros com
> o texto repetido. Alem do desperdicio, quebra a identidade: `wb:class-feature/
> weapon-specialization` passaria a existir em varias versoes conflitantes.
>
> `level` escalar continua valendo para `feat`, `spell` e tudo que tem nivel
> intrinseco. So class-feature muda.

## Linguagem de predicado (`requires`)

E aqui que a houserule mora. Termo de nivel e **sempre explicito** -- nunca um
`level` ambiguo.

```json
{"all": [
  {"class_level":     {"fighter": {">=": 5}}},
  {"character_level": {">=": 8}},
  {"ability":         {"str": {">=": 14}}},
  {"proficiency":     {"athletics": {">=": "expert"}}},
  {"has":             "wb:feat/power-attack"}
]}
```

Operadores: `all`, `any`, `not`, `>=`, `<=`, `==`.
Termos: `class_level`, `character_level`, `ability`, `proficiency`, `has`,
`trait`, `spellcasting_tradition`.

No PF2e oficial `class_level` e `character_level` sao sempre o mesmo numero.
A base guarda os dois separados assim mesmo -- e o que permite o builder existir
sem migracao depois.

## Linguagem de efeito (`grants`)

```json
[
  {"proficiency": {"martial": "master", "simple": "master"}},
  {"ability_boost": {"key": true}},
  {"feat_slot": {"kind": "class", "levels": [1,2,4,6,8]}},
  {"skill_training": {"auto": ["athletics"], "free": 3}},
  {"hp_per_level": 10},
  {"spell_slots": {"tradition": "arcane", "table": "full"}},
  {"focus_pool": 1},
  {"flat_modifier": {"selector": "ac", "type": "item", "value": 1}}
]
```

Ranks sao **palavra** (`untrained|trained|expert|master|legendary`), nunca numero
solto. O numero do Foundry (0-4) e traduzido na entrada.

## Kinds em escopo

`class`, `class-feature`, `feat`, `ancestry`, `heritage`, `background`, `spell`,
`ritual`, `equipment`, `weapon`, `armor`, `shield`, `archetype`, `relic`,
`language`, `familiar-ability`, `familiar-specific`, `animal-companion`,
`eidolon`, `apparition`, `trait`, `skill`, `deity`, `domain`

> `ritual` entrou depois. Foi **omissao ao escrever esta lista**, nao falha de
> extrator: zero registros em 18.176, e a palavra nao aparecia uma vez sequer
> nesta spec. Ritual nao consome slot de escolha, mas o personagem sabe quais
> conhece, e o principio "nada e descartado" cobre o caso. O escopo real sao
> **145 rituals vigentes** no censo do AoN, nao os ~31 dos dois Player Core que
> a primeira contagem viu.

> `relic` (122 vigentes) e `language` (117 vigentes) entraram pela mesma porta,
> na auditoria de 26/07, e pelo mesmo motivo: omissao ao escrever a lista.
> `relic` tem trilha de progressao propria (gift/aspect) e por isso nao cabe
> dentro de `equipment`. `language` existia so como string solta dentro do campo
> `languages` das 50 ancestrias -- a ficha tem linha de idiomas e precisa de
> entidade para referenciar.

> **Como achar o proximo kind ausente:** censo por `category` do AoN
> descontando `remaster_id`, cruzado contra a contagem por kind da base.
> Contar registro por `source.book` nao acha nada -- um livro pode aparecer com
> 2.032 registros e ainda assim faltar uma categoria inteira.

> `eidolon` e `familiar-specific` entraram depois: sao categorias proprias no
> AoN (13 e 47 registros) que a primeira leitura do escopo nao pegou. O trait
> `Minion` marca 123 documentos e serve de rede de seguranca para achar o que
> escapar das categorias -- companheiro de constructo, montaria, morto-vivo.
>
> Regra que decide se algo ganha kind proprio: **se alguma regra do jogo
> consegue falar de um e nao do outro, sao tipos diferentes.**
>
> `apparition` (espirito do Animist, 14 registros) entrou aplicando essa regra
> na extracao. Pelo mesmo teste ficaram **de fora**: especializacao e avanco de
> companheiro animal (nenhuma regra mira "avancado" sem mirar "companheiro
> animal"), e companheiro de constructo do Inventor -- que nao e familia
> propria, so reflavoriza `animal-companion`.
>
> **Nivel do companheiro nao e nivel de personagem.** A regra oficial diz que o
> companheiro avanca com o nivel de quem o concedeu, ou seja `class_level` da
> classe doadora. Em multiclasse os dois divergem -- e mais um caso que a
> linguagem de predicado precisa saber expressar.

Fora: bestiario, perigo, NPC, veiculo, conteudo de aventura, regra de reino.

## Saida do build

```
base/
  index.json            campos filtraveis de todos os registros   (~0,53 MB gzip)
  text/<kind>.json      prosa, carregada sob demanda              (~3,6 MB gzip)
  base.sqlite           store canonico com prov e conflitos       (build-time)
  relatorio_portoes.md  os 9 portoes, resultado de cada um
  relatorio_fusao.md    unidos com chave / vetados por guarda / sem chave
```

## Portoes de qualidade

Cada portao declara **em que ponto do pipeline roda**. Portao que roda depois da
operacao que ele deveria vigiar nao vigia nada -- foi o defeito do portao 7 da
v1. Todos sao reportados em `base/relatorio_portoes.md` **inclusive quando
passam**: portao ausente e portao aprovado nao podem parecer a mesma coisa.

| # | portao | roda |
|---|---|---|
| 1 | todo campo preenchido tem `prov`, e nenhum `prov` vale `"desconhecida"` | pos-emissao |
| 2 | `level`/`rank` divergente entre fontes sem entrada em `conflitos` | pos-merge |
| 3 | `requires`, `grants` ou `progressao` citando `wb:` id inexistente | pos-emissao |
| 4 | queda de cobertura por kind contra o build anterior sem justificativa no LOG | pos-emissao |
| 5 | registro emitido sem `license`, ou com `xref` vazio | pos-merge |
| 6 | `traits` categoricamente disjunto sobrando depois das tres regras de uniao | pos-merge |
| 7 | duas entidades distintas colidindo no mesmo id | **pre-fusao**, sobre as colisoes de id |
| 8 | kind com >=20 registros de 2+ fontes e **zero** `conflitos` | pos-merge |
| 9 | contagem por kind contra o censo do AoN (`category` menos `remaster_id`), tolerancia declarada por kind | pos-emissao |

**"Pos-emissao" quer dizer: depois do ultimo processo que escreve
`index.json`** -- hoje `fundir_renomeados.py`, nao `emitir_textos.py`. Rodar
antes deixa passar os campos que a fusao acrescenta (`superseded_by`,
`aliases`, `historico`), que e o defeito do portao 7 da v1 pelo avesso. O
portao 9 alem disso e **aritmeticamente impossivel** antes da fusao: o censo
conta so o vigente, e antes da fusao os legados ainda estao na contagem sem
marca nenhuma.

> O piso do portao 8 e 20, nao 100: com 100, tres dos seis kinds que a
> auditoria provou silenciados continuariam passando -- `ancestry` (50
> registros com 2+ fontes e 3 divergencias reais), `class` (27 / 2) e
> `familiar-ability` (72).

O build **falha** em qualquer um deles. Portao 9 e o unico com tolerancia, e ela
e escrita por kind no proprio relatorio, com o motivo -- e onde entram os
desvios de categorizacao conhecidos (o AoN indexa heranca versatil como
`ancestry`, por exemplo).

> Os portoes 8 e 9 nasceram da auditoria: o 8 porque `conflitos` zerado em 6
> kinds passou despercebido por um build inteiro, o 9 porque a ausencia de
> `ritual`, `relic` e `language` so apareceu quando alguem contou contra um
> gabarito externo. **Metrica sem gabarito externo nao mede cobertura.**

> E a licao que atravessa todos: **o denominador tem de ser o universo, nao o
> subconjunto ja processado.** "Prosa em 100% (17.866/17.866)" era 95% real --
> os 907 registros sem referencia nenhuma nunca entravam na conta.
