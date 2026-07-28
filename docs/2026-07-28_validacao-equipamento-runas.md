---
tipo: validacao
projeto: waybuilder
data: 2026-07-28
escopo: equipamento (equipment, weapon, armor, shield, relic) e consumo pelo motor
---

# Validacao de equipamento e runas

Trabalho de medicao, nao de correcao. Nenhum `.py` foi alterado. Toda contagem abaixo
vem de script rodado contra `pipeline/base/index.json` (19.705 registros, pin
`2026-07-27`) e os dumps crus em `pipeline/dados_brutos/`. Onde o numero do pedido
original difere do medido, reporto os dois e explico a diferenca.

## Resumo executivo

**Runas: o motor aplica potencia (arma e armadura), NAO aplica propriedade
(striking/resilient/flaming/...).** Isso nao e um bug de calculo -- e uma
ausencia de campo inteira. O schema do documento de personagem so tem
`"potencia": N` no item de inventario; nao existe `"striking"` nem qualquer
outro campo de runa de propriedade em lugar nenhum (schema, motor, nem nas 17
fichas de exemplo). Uma arma "+1 Striking" na pratica vira, pro motor, uma
arma "+1" comum: acerto correto, **dano errado** (dado nao dobra).

Fora disso, a base de equipamento esta em bom estado: cobertura de campo
mecanico alta em weapon/armor/shield, e cruzamento com o AoN mostra **zero**
lacuna real em weapon/armor/shield e uma lacuna pequena (52 de 8.642, 0,6%) em
equipment generico. Relic e 100% prosa, sem nenhuma estrutura de "gift"
evolutivo -- nem prosa marca nivel, e nada aponta pra isso ser suportado hoje.

## 1. Runas -- o ponto central

### 1.1 Onde as runas existem na base

Ha DOIS lugares com dado de runa, e eles nao se falam:

**a) `kind=equipment`, campo `rune` (estruturado, mas raro).** So 112 dos 6.122
registros de equipment tem esse campo:

| `rune.tipo` | contagem | exemplo |
|---|---|---|
| `property` | 101 | `striking`, `flaming`, `frost`, `holy`, `disrupting`... |
| `potency` | 6 | `weapon-potency-1/2/3`, `armor-potency-1/2/3` |
| `reinforcing` | 5 | Reinforcing Rune (escudo), lesser..supreme |

Formato: `{"tipo": "potency"|"property"|"reinforcing", "aplica_em": "weapon"|"armor", "grau": int|null}`.

Para runas de **potencia** o `grau` e o numero certo (weapon-potency-1 ->
`grau:1`). Para runas de **propriedade** o `grau` NAO representa a forca do
efeito (extra dado de dano de Striking, valor de resistencia de
Energy-Resistant etc.) -- e so um resto de parsing de "(Greater)"/"(Major)" no
nome, e ele erra: `Striking (Greater)` e `Striking (Major)` saem os DOIS com
`grau:3`, quando deveriam ser 2 e 3 (Striking base=2 dados, Greater=3,
Major=4). Confirmado com `wb:equipment/striking-greater` e
`wb:equipment/striking-major`, ambos `"grau": 3`.

Em nenhum dos 112, `grants` tem qualquer coisa (`grants: []` sempre) -- o
efeito mecanico da runa de propriedade so existe em `text` (prosa), nunca em
campo consumivel.

**b) `kind=weapon`/`armor`/`shield`, campo `runes` (embutido no ITEM MAGICO ESPECIFICO).**
Armas/armaduras nomeadas (ex.: "Axe of the Dwarven Lords") trazem runas ja
aplicadas:

- weapon: 376 de 1.041 tem `runes: {potency, property: [...], striking}` != zero/vazio
- armor: 202 de 216 tem `runes: {potency, property: [...], resilient}` (a maioria com tudo zero -- e o formato PADRAO de todo item, so os 376/202 tem valor real)
- shield: 118 de 125 tem o mesmo padrao

Exemplo real: `wb:weapon/axe-of-the-dwarven-lords` ->
`{"potency": 4, "property": ["keen","returning","speed"], "striking": 3}`.

**O motor nao le NENHUM dos dois campos.** `grep -n "runes\|rune" motor/motor.py`
nao acha nenhuma referencia a `runes` (weapon/armor/shield) nem a `rune`
(equipment). A unica fonte de runa que o motor conhece e o campo livre
`potencia`, digitado pelo JOGADOR no item de inventario do PERSONAGEM -- nada
que vem do item em si.

### 1.2 O que o motor faz de fato

`motor/motor.py::_ataques` (linha 1363) e `_defesa` (linha 1316):

```python
potencia = int(entrada.get("potencia") or 0)          # _ataques, linha 1388
...
"ataque": self.nivel + RANK_BONUS[rank] + atributo + potencia ...
mod_dano = 0 if distancia else forca                    # linha 1390 -- SEM potencia, SEM striking
"dano": f"{dano.get('dados', 1)}{dano.get('dado', '')}{mod_dano:+d}" ...
```

```python
potencia = int(armaduras[0]["entrada"].get("potencia") or 0)  # _defesa, linha 1333
total = 10 + dex_usada + prof + item_bonus + potencia
```

- **Potencia em ataque**: aplicada. Correta tambem por nao entrar no dano
  (RAW remaster: a runa de potencia da bonus de item ao ataque, nunca ao
  dano -- isso NAO e bug, e a regra certa).
- **Potencia em AC**: aplicada, correta.
- **Striking (dado de dano)**: NAO aplicada. `dano.get('dados', 1)` vem
  sempre do registro BASE da arma (`1` pra maioria), nunca multiplicado.
- **Resilient/qualquer runa de propriedade de armadura** (bonus a saves): NAO
  aplicada -- `_defesa` nunca toca `runes.resilient` nem em `saves`.
- **Runas de propriedade de arma** (flaming, holy, disrupting...): NAO
  aplicadas -- nao ha nem onde declarar isso no documento do personagem.

### 1.3 Prova com ficha derivada

Criei `motor/exemplos/_teste-validacao-runas-arma-1-striking.json`: copia
exata de `guerreiro4-fa-archer.json` (Guerreiro humano nivel 4, Longsword
equipada), so mudando o item de inventario pra
`{"item": "wb:weapon/longsword", "potencia": 1, "striking": 1}` -- o campo
`striking` foi incluido de proposito pra provar que o motor o ignora (nao
existe no schema, e so texto morto no JSON).

```
$ python3 ficha.py exemplos/guerreiro4-fa-archer.json               (baseline, sem runa)
  Longsword   +10   dano 1d8+2   (expert, STR)

$ python3 ficha.py exemplos/_teste-validacao-runas-arma-1-striking.json  (potencia=1, striking=1)
  Longsword   +11   dano 1d8+2   (expert, STR)
```

Ataque sobe +10 -> +11 (potencia aplicada, correto). Dano continua **identico**
`1d8+2` -- deveria ser `2d8+2` (Striking dobra o dado: 1d8 -> 2d8). O campo
`"striking": 1` no JSON foi 100% ignorado.

Testei tambem AC com armadura +1 (mesma ficha, `chain-mail` com
`"potencia": 1`): `21 -> 22`, item `4 -> 5`. Potencia de armadura funciona
igual a de arma.

Ficha de teste **nao** e uma das 17 canonicas -- criada so pra esta validacao,
pode ser apagada.

### 1.4 Tamanho do buraco

- **112** registros de `equipment` sao runas nomeadas (101 propriedade + 6
  potencia + 5 reinforcing). De todas, so as **6 de potencia** tem um numero
  (`grau`) que já e diretamente usavel -- e mesmo essas nao estao ligadas ao
  fluxo real (o jogador nunca "equipa" a runa; digita o numero solto em
  `potencia`).
- **101** runas de propriedade (striking incluso) tem **zero** efeito
  derivavel do dado atual -- so prosa. Pra funcionar precisariam de: (a) um
  campo no schema do personagem pra declarar qual runa de propriedade esta
  etched (hoje nao existe NENHUM), e (b) um campo estruturado na runa com o
  efeito numerico (dado extra de dano p/ striking, valor de resistencia p/
  energy-resistant etc.) -- que tambem nao existe.
- **376 armas + 202 armaduras + 118 escudos** (696 registros) tem `runes`
  embutido com valores reais, mas nada disso e lido pelo motor mesmo quando o
  jogador equipa exatamente esse item especifico.
- Em resumo: a runa de POTENCIA (a mais simples, so um numero) funciona hoje
  via campo manual solto e nao documentado na spec. A runa de PROPRIEDADE
  (striking incluso -- provavelmente o efeito mais comum e mais impactante do
  jogo, presente em toda arma +1/+2/+3 padrao) e 100% ausente: sem campo no
  documento, sem numero na base, sem calculo no motor.

### 1.5 Achado colateral: `potencia` nao esta no schema aprovado

`specs/2026-07-26-schema-personagem.md` nao menciona o campo `potencia` uma
unica vez (`grep` zero hits). O motor le e as 17 fichas de exemplo usam, mas
a spec aprovada (que segundo `CLAUDE.md` e fonte de verdade antes de
implementar) nao documenta esse campo. Se a spec for atualizada pra cobrir
runas de propriedade, vale fechar essa lacuna junto.

## 2. Arma e armadura -- integridade do dado

### 2.1 Weapon (1.041 registros -- pedido citava 1.038; diferenca de 3, dado
re-emitido depois do pedido, nao investiguei a fundo por ser marginal)

| campo | tem | falta |
|---|---|---|
| `damage` | 931 | 110 |
| `group` | 972 | 69 |
| `weapon_category` | 974 | 67 |
| `traits` | 1.028 | 13 |
| `bulk` | 974 | 67 |
| `price_cp` | 957 | 84 |
| `range` | 347 | 694 |

`range` "faltando" em 694 **nao e defeito** -- sao armas corpo a corpo, que
RAW nao tem alcance. Conferido pelos traits dos "sem range": `finesse`,
`two-hand-d8`, `reach`, `trip` etc, tudo melee. Dentro desses 694, achei **17**
que deveriam ter alcance e nao tem (thrown/ranged de verdade): `Rope Dart`,
`Throwing Knife` (x2 variantes), `War Javelin`, `Chakri`, `Bola` (x3
variantes), `Repeating Hand Crossbow` (x2), `Bow Staff (Ranged)`, `Cane Pistol
(Melee)`, `Dagger Pistol (Melee)`, `Three Peaked Tree (Melee)`. A maioria
desses TAMBEM esta nos 110 sem `damage` -- sao itens de "combination weapon"
(arma dupla melee+ranged) mal capturados no split.

`damage` faltando em 110: maioria e bombas alquimicas por grau (`Acid Flask
(Lesser/Moderate/Greater/Major)`, `Blood Bomb`, `Atrophy Bomb` etc.) e as
metades "ranged" de armas de combinacao. Isso e uma lacuna real de extracao,
nao um "nao se aplica" como o `range`.

### 2.2 Armor (216 -- bate com o pedido)

| campo | tem | falta |
|---|---|---|
| `ac_bonus` | 202 | 14 |
| `dex_cap` | 202 | 14 |
| `check_penalty` | 202 | 14 |
| `speed_penalty` | 202 | 14 |
| `armor_category` | 202 | 14 |
| `strength` | 182 | 34 |

Os mesmos 14 registros faltam os 5 campos juntos -- nao e ruido espalhado, e
um bloco de itens sem NENHUM dado mecanico. Entre eles: `wb:armor/leather`,
`wb:armor/hide`, `wb:armor/studded-leather`, `wb:armor/unarmored` --
armaduras **basicas do Player Core**, que existem numa segunda vez com nome
completo e dado completo (`wb:armor/leather-armor` tem `ac_bonus` etc.
normal). Isso cheira a registro duplicado/orfao de extracao (uma tabela de
"precious material armor" ou pagina de indice que virou item por engano) --
vale investigar antes de qualquer front consumir por nome curto.

### 2.3 Shield (125 -- bate com o pedido)

| campo | tem | falta |
|---|---|---|
| `ac_bonus` | 118 | 7 |
| `hardness` | 118 | 7 |
| `hp` | 118 | 7 |
| `bt` | 118 | 7 |

Mesmo padrao do armor: os 7 sem dado sao o mesmo bloco nos 4 campos
(`Dragonhide Shield`, `Highhelm War Shield`, `Mithral Shield`, `Noqual
Shield`, `Orichalcum Shield`, `Siccatite Shield`, `Sturdy Shield`) -- todos
escudos de material precioso, mesmo padrao suspeito do armor.

### 2.4 Cruzamento com o AoN

Comparei por `xref.aon`/`legado_de` e, como reforco, por nome normalizado
(cobre casos onde o id do AoN mudou entre dumps).

| kind | AoN (bruto) | base (kind puro) | sem match so por ID | sem match por ID *e* nome | veredito |
|---|---|---|---|---|---|
| weapon | 614 | 1.041 | 86 | 0 (apos unir com `equipment`) | **zero lacuna real** |
| armor | 75 | 216 | 7 | 0 | **zero lacuna real** |
| shield | 32 | 125 | 0 | 0 | **zero lacuna real** |
| equipment | 8.642 | 6.122 | 2.230 | **52** (apos unir com weapon/armor/shield/relic e normalizar aspas) | **52 itens realmente ausentes (0,6%)** |
| relic | 219 (tiers) | 122 (canonico) | -- | ver secao 4 | ver secao 4 |

A maior parte do "sem match por ID" em todo kind e reclassificacao: itens que
o AoN cataloga como "equipment" generico (armas magicas nomeadas, staves,
armaduras/escudos especificos) entraram na base sob `kind=weapon`/`armor`/
`shield` em vez de `kind=equipment` -- e por isso o cruzamento tem que ser
feito contra a UNIAO dos kinds, nao kind a kind isolado. Feito isso,
weapon/armor/shield fecham 100%.

Os **52 itens realmente ausentes** de `equipment` (contra a uniao de todos os
kinds, nomes normalizados) incluem itens conhecidos: `Cloak of Elvenkind`,
`Bag of Holding (Type I)`, `Hat of Disguise`, `Goggles of Night`, os
equivalentes "Standard-Grade" de Darkwood/Mithral (arma, armadura, escudo,
objeto -- 8 itens), `Tanglefoot Bag (Lesser)`, `Thunderstone (Lesser)`,
`Smokestick (Lesser)`, itens de nivel 0 como `Artisan's Tools`/`Thieves'
Tools`/`Healer's Tools`, e o bloco `Spellcasting (1st..9th level)` (servico de
GM, discutivel se deveria contar como "equipamento"). Lista completa
disponivel no script de validacao (nao commitado -- rodar de novo se precisar
da lista crua).

## 3. O motor na pratica -- as 17 fichas de exemplo

Rodei `python3 motor/ficha.py motor/exemplos/<arquivo>.json` pras 17 e
conferi a mao AC, ataque e dano contra as formulas:

- `AC = 10 + min(mod_DEX, dex_cap) + (nivel + RANK_BONUS[rank]) + item_bonus + potencia`
- `Ataque = nivel + RANK_BONUS[rank] + atributo + potencia`
- `Dano = dados_da_arma + mod_STR` (ou DEX se a distancia)

**Todas as 17 batem com a formula, sem excecao.** Exemplos conferidos a mao:

- `barbaro6-fa-duas-dedicacoes-limpo`: AC 19 = 10 + DEX +1 + prof 8 (trained
  em unarmored, nivel 6 + RANK_BONUS trained 2) + item 0. Ataque Greataxe
  +14 = nivel 6 + RANK_BONUS expert 4 + STR +4 + potencia 0. Bate.
- `campeao6-alquimista4-fa-nivel10`: AC 27 = 10+1(DEX cap nao estourado)+12(trained
  nivel10=10+2)+4(item)+0. Bate, e escudo +2 aparece separado (nao somado na
  AC base -- correto, escudo so entra quando "levantado", o motor
  corretamente deixa de fora do total e mostra a parte).
- `guerreiro6-fa-duas-dedicacoes`: `DEX perdida: 2` -- Chain Mail tem
  `dex_cap` baixo e o personagem tem DEX 16 (+3); o motor capa em +1 e reporta
  a perda corretamente.

**Um achado real, fora do escopo de potencia/striking**: em
`ladino2-druida2-bardo2-fa.json` o personagem tem a subclasse `wb:class-feature/thief`
(Rogue Thief racket -- RAW: usa DEX no dano de arma finesse em vez de STR).
O motor entrega `Rapier +11 dano 1d6-1 (trained, DEX)` -- ataque usa DEX
(correto, finesse), mas o **dano usa STR (-1)**, quando deveria usar DEX
(+3): `1d6+3`, nao `1d6-1`. Diferenca de 4 no dano medio por acerto. Isso
**esta documentado no proprio codigo** (`motor.py` linha 1366-1368: "Thief
usa DEX, e isso vem de rule element com predicado -- por isso nao esta aqui")
-- ou seja, gap conhecido pelos autores, nao descoberta minha, mas confirmo
aqui com numero e reproducao formal.

**Bulk/carga: nao existe no motor.** `grep -n "bulk" motor/motor.py` nao acha
nada -- nem leitura do campo `bulk` da arma/armadura, nem soma no documento,
nem linha na `visao()`/`ficha.py`. Confirma a suspeita do pedido.

**Achado adicional**: 181 weapons + 55 armors + 22 shields (258 no total) tem
`grants` estruturado e nao-vazio (`mechanized: true` -- resistencias, bonus
extra etc. de itens magicos especificos, ex.: Arachnid Harness da resistencia
a veneno 2). O motor nunca le `grants` de item de inventario -- so le
`ac_bonus`/`dex_cap`/`check_penalty`/`strength` (armor) e
`damage`/`traits`/`weapon_category`/`range` (weapon). Entao mesmo os itens
magicos com efeito ja estruturado na base ficam mudos na ficha.

## 4. Relic (122 canonico / 219 nos textos)

**Diferenca 219 vs 122 explicada**: `pipeline/base/text/relic.json` tem 219
chaves, mas 97 delas sao sufixadas `-legacy` (versao pre-remaster, linkada
via `historico` do registro atual -- ex.: `wb:text/relic/clean-luck-legacy`
e a versao antiga de `wb:relic/clean-luck`). So 1 texto (`holy-light`) ficou
orfao sem registro correspondente. Os **122 registros `kind=relic`** sao o
numero canonico correto pra medir cobertura -- 219 e a contagem de
texto bruto, contando duplicata legado.

**Gift levels: 100% prosa, sem estrutura nenhuma.** Verificado:

- Nenhum dos 122 registros tem campo de tier/grau/nivel de gift.
- `grants: []` em TODOS os 122, sem excecao.
- `level: null` em todos que checei -- nao ha nivel de personagem associado.
- O dump bruto do AoN (`aon_relics.json`, 219 entradas) tem um campo `type`
  com os valores `Relic Minor Gift` (108), `Relic Major Gift` (74), `Relic
  Grand Gift` (37) -- ENTAO o AoN sabe o tier de cada entrada, mas esse dado
  **nao foi extraido pra base**. O `type` nem aparece nos 122 registros
  canonicos.
- A evolucao (efeito cresce com nivel de personagem) esta as vezes descrita
  em PROSA dentro do proprio texto -- ex.: "Deadly Spark": "damage increases
  by 1d12 at 6th level and by another 1d12 every 4 levels thereafter" -- mas
  isso e string solta, sem campo `{nivel: 6, incremento: "1d12"}` nem nada
  parseavel.
- `motor/motor.py` **nao tem nenhuma referencia a "relic"** (`grep -n relic
  motor/motor.py` = zero linhas). Relic nem entra em `_equipados()` --
  inventario com item `kind=relic` e simplesmente invisivel pro motor hoje,
  independente de gift level.

Resposta direta: **o dado NAO suporta gift levels.** Nem estrutura (nenhum
campo), nem prosa parseavel (texto livre sem marcacao), nem motor (relic nem
e reconhecido como kind equipavel).

## 5. O que esta certo

- Potencia (arma e armadura) e aplicada corretamente em ataque e AC, inclusive
  corretamente EXCLUIDA do dano (RAW remaster: potencia nao afeta dano).
- AC, ataque e dano batem com a formula RAW em todas as 17 fichas de exemplo,
  sem excecao -- incluindo casos com escudo separado do total e DEX capado
  por armadura pesada.
- weapon/armor/shield: cobertura de campo mecanico alta (>90% na maioria dos
  campos que se aplicam) e **zero lacuna real contra o AoN** depois de
  cruzar pela uniao de kinds.
- A extracao de runa (`rune` em equipment, `runes` em weapon/armor/shield) e
  um trabalho real que ja existe na base -- so nao esta ligado ao motor nem
  ao schema do personagem. Nao e "dado ausente", e "dado presente e
  desconectado".
- Relic: numero canonico (122) e consistente e explicavel; a diferenca do
  numero citado no pedido (219) tem causa raiz identificada (duplicata
  legado), nao e erro de contagem.

## Arquivos tocados

- Criado (teste, fora das 17 canonicas):
  `motor/exemplos/_teste-validacao-runas-arma-1-striking.json`
- Nenhum `.py` alterado.
- Script de analise (scratchpad, nao commitado):
  `/tmp/claude-1000/-mnt-c-Users-igor0/cf4835ec-3dd1-442c-ad27-6284421f280d/scratchpad/cobertura.py`
