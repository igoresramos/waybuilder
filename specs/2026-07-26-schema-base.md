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
- **`text`** e uma referencia, nao o texto. A prosa vive em arquivo separado
  (3,6 MB gzip) e carrega sob demanda.

## Precedencia entre fontes

Por campo, nao por registro:

| Campo | Vence | Motivo |
|---|---|---|
| `grants` (efeito mecanico) | **foundry** | unica com rank numerico e rule elements |
| `requires` (pre-requisito) | **pf2etools** | unica com `{@feat}`/`{@skill}` marcados |
| `text`, `name`, `traits`, `rarity` | **aon** | e a Paizo; mais completa e atual |
| `level` | foundry, conferido contra pf2etools | ha duas fontes independentes -- divergencia e bug |
| `source`, `remaster` | **aon** | tem `remaster_id`/`legacy_id` para a ponte |

Quando a fonte vencedora nao tem o campo, cai para a proxima na ordem acima e
`prov` registra de quem veio.

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
`equipment`, `weapon`, `armor`, `shield`, `archetype`, `familiar-ability`,
`familiar-specific`, `animal-companion`, `eidolon`, `trait`, `skill`, `deity`,
`domain`

> `eidolon` e `familiar-specific` entraram depois: sao categorias proprias no
> AoN (13 e 47 registros) que a primeira leitura do escopo nao pegou. O trait
> `Minion` marca 123 documentos e serve de rede de seguranca para achar o que
> escapar das categorias -- companheiro de constructo, montaria, morto-vivo.
>
> Regra que decide se algo ganha kind proprio: **se alguma regra do jogo
> consegue falar de um e nao do outro, sao tipos diferentes.**

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
