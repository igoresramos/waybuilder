---
spec: schema-base
project: waybuilder
version: 1
status: aprovada
created: 2026-07-26
---

# Schema da base canonica

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
  "level": 5,
  "traits": ["fighter"],
  "rarity": "common",
  "source": {
    "book": "Player Core", "page": 145,
    "license": "ORC", "remaster": true
  },
  "requires": { "...predicado..." },
  "grants":  [ "...efeitos..." ],
  "text": "wb:text/class-feature/fighter-weapon-mastery",
  "mechanized": true,
  "xref": {
    "foundry":   "Compendium.pf2e.classfeatures.Item.xxxx",
    "aon":       "class-feature-156",
    "pf2etools": "class-fighter-pc1#WeaponMastery"
  },
  "prov": {
    "name": "aon", "level": "foundry", "grants": "foundry",
    "requires": "pf2etools", "text": "aon"
  },
  "conflitos": [
    {"campo": "level", "foundry": 5, "aon": 5, "pf2etools": 5, "escolhido": "foundry"}
  ]
}
```

- **`prov`** e obrigatorio e por campo. Sem isso nao da para re-sincronizar so o
  que mudou nem auditar divergencia.
- **`conflitos`** so aparece quando as fontes discordam. Divergencia e registrada,
  nunca silenciada.
- **`mechanized`** separa as duas camadas: `true` = o app calcula pelos `grants`;
  `false` = so exibe o texto e o jogador controla na mao. Nunca trava o build.

  > **E derivado, nao declarado: `mechanized == bool(grants)`.** Medido em
  > 2026-07-26: o campo significava quatro coisas diferentes conforme o
  > extrator. 12.923 registros (70,1%) tinham `true` com `grants` vazio -- ou
  > seja, prometiam calculo sem nada para calcular -- e 374 tinham `false` com
  > `grants` cheio. Pior, o `false` se distribuia por **kind inteiro** (`deity`,
  > `trait`, `ritual`, `language`, `skill`): era propriedade de quem escreveu o
  > extrator, nao do dado.
  >
  > Como a unica coisa que o app consegue calcular sao os `grants`, o valor e
  > exatamente isso. Extrator nao declara mais este campo; o reconciliador
  > deriva.
- **`text`** e uma referencia, nao o texto. A prosa vive em arquivo separado
  (3,6 MB gzip) e carrega sob demanda.

## Precedencia entre fontes

Por campo, nao por registro:

| Campo | Vence | Motivo |
|---|---|---|
| `grants` (efeito mecanico) | **foundry** | unica com rank numerico e rule elements |
| `requires` (pre-requisito) | **pf2etools** | unica com `{@feat}`/`{@skill}` marcados |
| `text`, `name`, `rarity` | **aon** | e a Paizo; mais completa e atual |
| `level` | foundry, conferido contra pf2etools | ha duas fontes independentes -- divergencia e bug |
| `source`, `remaster` | **aon** | tem `remaster_id`/`legacy_id` para a ponte |
| `traits` | **nenhuma -- ver abaixo** | e conjunto, nao valor escalar |

Quando a fonte vencedora nao tem o campo, cai para a proxima na ordem acima e
`prov` registra de quem veio.

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
`trait`, `spellcasting_tradition`, `subclass`.

No PF2e oficial `class_level` e `character_level` sao sempre o mesmo numero.
A base guarda os dois separados assim mesmo -- e o que permite o builder existir
sem migracao depois.

### O gate de nivel e DERIVADO, nao lido

> Medido em 2026-07-27: `class_level` aparecia em **79 de 19.738 registros** --
> o termo que justifica o projeto inteiro estava praticamente vazio. E nao
> porque falta dado: porque **nenhuma fonte precisa da distincao**, ja que no
> PF2e os dois numeros sao sempre iguais.
>
> No PF2e o pre-requisito de um feat **nunca menciona nivel**: o nivel do feat
> *e* o gate. `Accompany`, com trait `bard` e `level: 8`, quer dizer "voce e um
> Bardo de nivel 8". Sob a houserule isso se parte em dois, e a regra de
> derivacao e mecanica:

| O feat tem | Gate derivado | Regra |
|---|---|---|
| trait de classe X | `class_level[X] >= N` | 12 |
| trait `archetype` | `character_level >= N` | 13 |
| trait de ancestria Y | `character_level >= N` **e** `has` a ancestria | 14 |
| nenhum dos anteriores | `character_level >= N` | 14 |

`archetype` vence trait de classe: arquetipo nao pertence a classe nenhuma.
O `requires` declarado pela fonte **nunca e sobrescrito** -- o gate entra como
mais uma clausula de um `all`, e clausula ja presente nao e duplicada.

### `subclass`: a camada do meio

```json
{"subclass": {"cleric": "wb:class-feature/warpriest"}}
```

> `has` nao serve para isto: e generico demais, e nao distingue "escolheu esta
> doutrina" de "pegou este feat". Um predicado que nao distingue nao consegue
> expressar "so para Warpriest".
>
> O caso que obriga o termo a existir e publicado: a proficiencia de conjuracao
> do Clerigo depende da **Doutrina**. Cloistered segue o conjurador pleno
> (expert 7, master 15, legendary 19); Warpriest e mais lento e nunca chega a
> legendary (expert 11, master 19). Duas progressoes, mesma classe, mesmo nivel
> -- `class_level` sozinho nao alcanca.
>
> O dado ja vinha certo desde a primeira extracao, em
> `spellcasting.proficiency`, com as duas progressoes separadas. Faltava o
> termo e faltava alguem consumir.

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

### `grants` vale para TODO kind, nao so para `class`

> Medido em 2026-07-27: esta era a unica linguagem de efeito da spec, e so
> `class` a usava. Ancestria guardava o efeito em campos soltos (`hp`, `size`,
> `speed`, `boosts`, `senses`, `flaw`, `languages`); background usava outro
> conjunto (`skill_training`, `attribute`, `skill`, `feat`). Tres formatos para
> o mesmo conceito.
>
> Consequencia visivel: `mechanized`, definido como `== bool(grants)`, marcava
> 50 ancestrias e 502 backgrounds como "o jogador resolve na mao", quando o
> efeito deles e calculavel e ja estava estruturado -- so que noutro lugar.
> Um motor precisava conhecer os tres formatos, e cada kind novo viraria caso
> especial.

Termos adicionais, emitidos pela projecao canonica de ancestria e background:

```json
[
  {"hp_ancestry": 10},
  {"size": "med"},
  {"speed": {"land": 20}},
  {"sense": "darkvision"},
  {"language": {"auto": ["common", "dwarven"], "free": 1}},
  {"skill_training": {"auto": ["arcana"], "lore": ["Azlant Lore"]}},
  {"grant_feat": ["wb:feat/assurance"]},
  {"requires_ancestry": "wb:ancestry/dwarf"}
]
```

Os campos originais **permanecem**: a projecao adiciona, nunca substitui. Nada
se perde e quem lia `r["hp"]` continua funcionando.

## Kinds em escopo

`class`, `class-feature`, `feat`, `ancestry`, `heritage`, `background`, `spell`,
`ritual`, `equipment`, `weapon`, `armor`, `shield`, `archetype`,
`familiar-ability`, `familiar-specific`, `animal-companion`, `eidolon`,
`apparition`, `trait`, `skill`, `deity`, `domain`

> `ritual` entrou depois. Foi **omissao ao escrever esta lista**, nao falha de
> extrator: zero registros em 18.176, e a palavra nao aparecia uma vez sequer
> nesta spec. Sao ~31 so nos dois Player Core. Ritual nao consome slot de
> escolha, mas o personagem sabe quais conhece, e o principio "nada e
> descartado" cobre o caso.

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
  index.json        campos filtraveis de todos os registros   (~0,53 MB gzip)
  text/<kind>.json  prosa, carregada sob demanda              (~3,6 MB gzip)
  base.sqlite       store canonico com prov e conflitos       (build-time)
```

## Portoes de qualidade

O build **falha** se:

1. Algum registro nao tem `prov` para todo campo preenchido.
2. `level` diverge entre foundry e pf2etools sem entrada em `conflitos`.
3. Um `requires` cita `wb:` id que nao existe na base.
4. Cobertura cai em relacao ao build anterior sem justificativa no LOG.
5. Algum registro emitido tem `license` ausente.
6. Sobra `traits` categoricamente disjunto entre fontes **depois** de aplicadas
   as tres regras de uniao -- e suspeita de colisao de identidade.
7. Um `name` normalizado aparece em dois registros do mesmo `kind` sem que a
   distincao esteja explicita no slug.
