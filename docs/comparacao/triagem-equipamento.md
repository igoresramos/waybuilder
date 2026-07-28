# Triagem de divergências -- Equipamento (Arma, Armadura, Escudo, Companheiro, Familiar)

Fontes: `docs/comparacao/aon/{arma,armadura,escudo,companheiro,familiar}.json`, geradas por
`pipeline/comparar_com_aon.py` a partir dos dumps `pipeline/dados_brutos/aon_equipment_*.json`
e `aon_companheiros.json` contra `pipeline/base/index.json`. Nenhum arquivo do pipeline foi
alterado -- esta é uma auditoria read-only.

Método: toda inspeção via `python3` ad-hoc sobre o `index.json` (9,4 MB), nunca leitura direta.
Desempate de divergência sempre contra `pipeline/dados_brutos/foundry/packs/pf2e/equipment/**`
(fonte de maior confiança para campos mecânicos) e contra o campo `remaster_id` do dump AoN
(liga entrada legado -> entrada remaster) para decidir rename vs. lacuna real.

**Achado central: nenhuma das 16 armas, 2 familiares, 6 níveis e 2 raridades "divergentes"
listados pelo comparador é uma lacuna de conteúdo real.** Todos são falsos positivos de
metodologia (filtro por `kind`, ou AoN listando reimpressões/nome legado). A lacuna real e
séria está em outro lugar: **110 das 1.041 armas (10,6%), 14 das 216 armaduras (6,5%) e 7 dos
125 escudos (5,6%) na nossa base têm campos mecânicos essenciais totalmente ausentes** --
incluindo `Fist`, `Shield Bash`, `Hide`, `Leather`, `Studded Leather` e `Unarmored`, que são
opções base que praticamente todo personagem usa.

---

## 1. Resumo por kind e categoria de divergência

| Kind | Faltando (bruto) | Faltando (real) | Nível divergente | Raridade divergente |
|---|---:|---:|---:|---:|
| Arma | 16 | **0** | 6 (0 real, 1 bug de merge) | 2 (0 real) |
| Armadura | 0 | 0 | 0 | 0 |
| Escudo | 0 | 0 | 0 | 0 |
| Companheiro | 0 | 0 | 0 | 0 |
| Familiar | 2 | **0** | 0 | 0 |

### Arma -- os 16 "faltam_em_nos"

| Categoria | Qtde | Veredito |
|---|---:|---|
| F-KIND (munição, existe como `kind=equipment`, não `weapon`) | 13 | Falso positivo: comparador só olha `kind=weapon`. `Arrows`, `Bolts`, `Sling Bullets`, `Blowgun Darts`, `Fishing Lure`, `Sun Shot`, `Wooden Taws`, `8-Round Magazine`, `Backpack Ballista Bolts`, `Backpack Catapult Stones`, `Repeating (Crossbow\|Hand Crossbow\|Heavy Crossbow) Magazine` -- todos presentes, íntegros, sob `wb:equipment/*`. |
| F-RENAME-REMASTER | 3 | `Khakkara` -> `Khakkhara` (Tian Xia Character Guide), `Kursarigama` -> `Kusarigama` (Tian Xia Character Guide), `Rungu` -> `Cruuk` (Player Core 2). Confirmado via `remaster_id` no dump AoN; as três formas remaster já estão na base (`wb:weapon/khakkhara`, `wb:weapon/kusarigama`, `wb:weapon/cruuk`). |
| A-FALTA-REAL | **0** | -- |

### Arma -- nível divergente (6 itens, todos `aon:0 / nosso:1`)

O dump `aon_equipment_weapon.json` lista **duas entradas** por nome para essas 6 armas: a
versão legado (nível 0, sourcebook antigo) e a versão remaster (nível 1). O comparador casou
contra a linha errada (nível 0).

| Arma | Nosso nível | Veredito |
|---|---:|---|
| Composite Longbow | 1 | Correto -- Foundry confirma nível 1 (Tian Xia Character Guide). Falso positivo. |
| Composite Shortbow | 1 | Correto -- Foundry confirma nível 1 (Player Core). Falso positivo. |
| Backpack Catapult | 1 | Correto -- Foundry confirma nível 1 (Guns & Gears Remastered). Falso positivo. |
| Repeating Crossbow | 1 | Correto -- Foundry confirma nível 1 (Guns & Gears Remastered). Falso positivo. |
| Flying Talon | 1 | Correto -- Foundry confirma nível 1 (Player Core 2). Falso positivo. |
| **Repeating Hand Crossbow** | 0 | **BUG REAL.** Nossa entrada canônica (`wb:weapon/repeating-hand-crossbow`, a única das 3 entradas duplicadas com dados mecânicos completos) usa fonte "Battlecry!" nível 0. O item Foundry correto (`repeating-hand-crossbow.json`, nível 1, Guns & Gears Remastered, dano 1d6 P) **não está referenciado por nenhuma entrada da base** -- ficou órfão na fusão. Dano bate (1d6 P em ambas), mas nível/fonte estão errados no item que o motor de fato usa. |

### Arma -- raridade divergente (2 itens)

Ambos os casos batem contra entradas **órfãs** de uma família de duplicatas descrita na
Seção 2 (não contra a entrada canônica mecanizada). `wb:weapon/bola` (canônica, Foundry) tem
raridade `common` e está correta; `wb:weapon/throwing-knife` (canônica, Foundry) tem raridade
`common` e está correta. As divergências reportadas apontam para `bola-nv0-weapon-331` e
`throwing-knife-uncommon`, que são stubs de reimpressão AoN sem nenhum dado mecânico -- não
deveriam nem estar concorrendo por "nossos" dados. Falso positivo de metodologia, mas expõe o
bug de duplicação real (Seção 2).

### Familiar -- os 2 "faltam_em_nos"

| Nome legado (AoN) | Nome remaster (já na base) | Fonte |
|---|---|---|
| Extra Reagents | Extra Alchemy | Player Core 2 |
| Faerie Dragon | Fey Dragonet | Player Core 2 |

Confirmado via `remaster_id`. **0 lacunas reais.**

---

## 2. Auditoria de integridade mecânica (seção principal)

### 2.1 Bug estrutural: duplicatas órfãs de arma (achado colateral, mas real)

8 nomes de arma têm **1 entrada canônica** (com todos os campos mecânicos, ligada ao Foundry
ou totalmente preenchida pelo AoN) **+ 1 a 3 entradas órfãs** (só nome/nível/raridade/traits,
zero campos mecânicos) geradas porque o AoN cataloga a mesma arma sob `id`s diferentes por
reimpressão/sourcebook, e a fusão não as deduplicou contra a canônica:

| Nome | Entrada canônica (íntegra) | Entradas órfãs (sem dano/grupo/categoria) |
|---|---|---|
| Bola | `wb:weapon/bola` | `bola-nv0`, `bola-nv0-weapon-123`, `bola-nv0-weapon-331` |
| Repeating Hand Crossbow | `wb:weapon/repeating-hand-crossbow` (mas órfã do Foundry certo -- ver 1.) | `repeating-hand-crossbow-nv0`, `repeating-hand-crossbow-nv1` |
| Aldori Dueling Sword | `wb:weapon/aldori-dueling-sword` | `aldori-dueling-sword-nv1` |
| Butterfly Sword | `wb:weapon/butterfly-sword` | `butterfly-sword-nv0` |
| Chakri | `wb:weapon/chakri` | `chakri-recovery` |
| Jiu Huan Dao | `wb:weapon/jiu-huan-dao` | `jiu-huan-dao-disarm` |
| Leiomano | `wb:weapon/leiomano` | `leiomano-deadly` |
| Throwing Knife | `wb:weapon/throwing-knife` | `throwing-knife-uncommon` |

Impacto: 11 entradas de arma inteiramente vazias de mecânica poluindo busca/autocomplete e
inflando a contagem total (1.041 vs. 1.029 "nossos" no comparador). Não quebram nada se o
motor sempre usar a canônica, mas são lixo de dados -- ver Ação Recomendada.

### 2.2 Cobertura de campos -- Arma (1.041 total)

| Campo | Presente | Ausente | % ausente |
|---|---:|---:|---:|
| `traits` (lista, pode ser vazia) | 1.041 | 0 | 0% |
| `damage` (dado + tipo) | 931 | **110** | **10,6%** |
| `group` | 972 | 69 | 6,6% |
| `weapon_category` | 974 | 67 | 6,4% |
| `bulk` | 974 | 67 | 6,4% |
| `usage` / `hands` | 939 | 102 | 9,8% |
| `price_cp` | 957 | 84 | 8,1% |
| `base_item` | 943 | 98 | 9,4% |
| `range` (só armas de grupo bow/crossbow/sling/dart/firearm, excluindo `thrown-N`) | 161/161 | 0 | 0% |

`range` está limpo: toda arma cujo dano vem de alcance embutido (`thrown-N`) corretamente não
tem campo `range` próprio (o número já está no trait); nenhuma arma de grupo puramente à
distância ficou sem `range`.

**Traits parametrizados presentes na base** (contagem de ocorrências, não é uma auditoria de
correção, só confirma que o vocabulário existe): `deadly-*` 112, `two-hand-*` 183,
`versatile-*` 147, `thrown-*` 100, `agile` 165, `finesse` 176.

#### As 110 armas sem `damage` -- decomposição

| Causa | Qtde | Gravidade |
|---|---:|---|
| Bombas alquímicas (Acid Flask, Blood Bomb, Glue Bomb, Redpitch Bomb, Tallow Bomb, Silver Orb, Spider Satchel, Steelscour, Water Bomb, Pernicious Spore Bomb, Bioluminescence Bomb, Atrophy Bomb -- todas as variantes lesser/moderate/major/greater) | 41 | **Alta** -- toda a linha de ataque do Alquimista via bomba fica sem dano. |
| Modos melee/ranged de armas de combinação (Axe Musket, Cane Pistol, Gun Sword, Hammer Gun, Mace Multipistol, Rapier Pistol, Triggerbrand, Lancer, Bow Staff, Piercing Wind, Three Peaked Tree, Mikazuki, Black Powder Knuckle Dusters, Dagger Pistol, Explosive Dogslicer, Gnome Amalgam Musket, Wrecker, Crescent Cross -- ambos os modos) | 36 | **Alta** -- armas avançadas reais, os dois modos de ataque ficam sem dano/grupo/categoria. |
| Armas base ou específicas sem dado inerente (`Fist`, `Shield Bash`, `Blowgun`, `Dwarven Waraxe`, `Dagger of Venom`, `Flame Tongue`, `Holy Avenger`, `Nine-Ring Sword`, `Orichalcum Weapon`, `Wind and Fire Wheel`, `Mithral Tree`, `Tekko-kagi`, `Dart Umbrella`, `Drake Rifle`, `Reinforced Frame`) | 15 | **Crítica para 2 delas.** `Fist` (ataque desarmado universal, deveria ser 1d4 B) e `Shield Bash` (deveria ser 1d4 B) não têm dano -- toda ficha sem arma equipada ou usando escudo quebra a aba de Ataques. As demais são armas específicas mágicas que deveriam herdar o dano da arma-base e não herdam. |
| Duplicatas órfãs (Seção 2.1) | 11 | Baixa -- não deveriam existir como entradas separadas. |
| Munição/consumível sem dano próprio (correto por design: `Bolts (Phalanx Piercer)`, `Firearm Ammunition` x2, `Magazine` x2, `Spray Pellet`, `Alchemical Bomb` genérico) | 7 | Nenhuma -- comportamento esperado. |

**Total:** 41+36+15+11+7 = 110.

### 2.3 Cobertura de campos -- Armadura (216 total)

| Campo | Presente | Ausente | % ausente |
|---|---:|---:|---:|
| `traits` | 216 | 0 | 0% |
| `ac_bonus` / `dex_cap` / `check_penalty` / `speed_penalty` / `armor_category` / `group` / `bulk` | 202 | **14** | **6,5%** |
| `strength` | 182 | 34 | 15,7% (20 são armaduras `unarmored`, legitimamente sem requisito de Força; 14 coincidem com o bloco quebrado abaixo; 1 anomalia real isolada) |
| `price_cp` | 187 | 29 | 13,4% |
| `base_item` | 181 | 35 | 16,2% |

#### As 14 armaduras sem `ac_bonus` (bloco mecânico inteiro ausente)

Todas vêm só do `pf2etools` (sem match no Foundry nem no AoN estruturado) -- têm apenas
nome/nível/fonte, zero número de jogo:

`Hide`, `Leather`, `Studded Leather`, `Unarmored` -- **armaduras/categorias base que qualquer
personagem pode escolher**; mais 10 armaduras mágicas específicas: `Breastplate of Command`,
`Celestial Armor`, `Demon Armor`, `Elven Chain`, `Grisantian Pelt Armor`, `Heavy Power Suit`,
`Lion's Pelt`, `Remorhaz Armor`, `Rhino Hide`, `Sovereign Steel Armor`.

**Gravidade: crítica.** `Hide`, `Leather` e `Unarmored` são as opções mais comuns do jogo --
qualquer build "sem armadura" ou com couro básico calcula CA errado (ou nulo) hoje.

Achado secundário isolado: `Reinforced Chassis` é armadura `medium` e deveria ter `strength`,
mas está no grupo dos 34 sem o campo -- vale conferir junto do lote acima, é o único caso de
armadura não-`unarmored` sem requisito de Força.

`base_item`/`price_cp` ausentes nos outros ~20-30 casos além dos 14 acima são majoritariamente
armaduras naturais/barding de ancestralidade (`Titan Nagaji Scales`, `Bakuwa Lizardfolk Bony
Plates`, bardings) que plausivelmente não têm preço de compra por serem inatas -- menor
prioridade, não verificado item a item.

### 2.4 Cobertura de campos -- Escudo (125 total)

| Campo | Presente | Ausente | % ausente |
|---|---:|---:|---:|
| `traits` | 125 | 0 | 0% |
| `ac_bonus` / `hardness` / `hp` / `bt` / `speed_penalty` / `bulk` | 118 | **7** | **5,6%** |
| `price_cp` | 116 | 9 | 7,2% |
| `base_item` | 106 | 19 | 15,2% |

#### Os 7 escudos sem `ac_bonus` (bloco mecânico inteiro ausente)

Mesmo padrão -- só `pf2etools`, sem Foundry/AoN estruturado: `Dragonhide Shield`, `Highhelm
War Shield`, `Mithral Shield`, `Noqual Shield`, `Orichalcum Shield`, `Siccatite Shield`,
`Sturdy Shield`.

**Gravidade: média.** Todos são variantes de material específico (não o escudo base de
madeira/aço/torre), então o impacto é menor que o caso de armadura, mas ainda quebra a aba de
Defesa para quem escolher essas opções.

---

## 3. Ação recomendada para o pipeline (priorizada por impacto no motor)

1. **P0 -- Mecanizar `Hide`, `Leather`, `Studded Leather`, `Unarmored`, `Fist`, `Shield
   Bash`.** São as opções mais usadas do jogo (armadura básica e ataques desarmado/escudo) e
   hoje não têm nenhum número de jogo. Valores são triviais de obter (regra core, sem
   variação): puxar do Foundry `unarmored.json`/`hide.json`/`leather.json`/etc. no pack de
   equipamento, que hoje aparentemente não estão linkados (xref vazio nessas 4 armaduras) --
   vale checar se os arquivos Foundry existem e por que o merge não pegou.
2. **P0 -- Investigar por que 4 armaduras base + `Repeating Hand Crossbow` ficaram sem xref de
   Foundry** apesar do arquivo Foundry existir (`Hide`, `Leather` quase certamente têm
   equivalente no pack `equipment/`). Isso é um bug de matching na fusão, não falta de fonte --
   provavelmente o mesmo bug para as 10 armaduras mágicas específicas e os 7 escudos de material.
3. **P1 -- Mecanizar as 41 bombas alquímicas e os 36 modos melee/ranged de arma de
   combinação.** Ambos os grupos são opções de ataque reais e concentradas (poucas classes de
   item, muitos itens) -- boa relação esforço/cobertura. Os dados de dano das bombas e dos
   modos de combinação existem no Foundry (`type: weapon`, sistema `damage`); provavelmente um
   filtro de import excluiu itens com `_id` compartilhado entre modos ou com `consumable: true`.
4. **P1 -- Deduplicar as 11 entradas órfãs de arma** (`bola-nv0*`, `repeating-hand-crossbow-nv*`,
   `*-nv0`, `*-recovery`, `*-disarm`, `*-deadly`, `throwing-knife-uncommon`). Ou mesclar seus
   `aon` ids como `xref` alternativo na entrada canônica, ou removê-las do `kind=weapon` -- hoje
   poluem contagem e busca sem adicionar informação.
5. **P2 -- Mecanizar as ~10 armas mágicas específicas sem dano herdado** (`Holy Avenger`,
   `Flame Tongue`, `Dagger of Venom`, `Nine-Ring Sword`, `Orichalcum Weapon`, `Wind and Fire
   Wheel`, `Mithral Tree`, `Dwarven Waraxe`) e os 7 escudos de material específico. Menor
   frequência de uso que P0/P1, mas mesmo padrão de causa raiz (falta herdar campo da
   arma/escudo-base quando o item específico só adiciona runas/efeito).
6. **P2 -- Corrigir o xref de `Repeating Hand Crossbow`** para apontar para o item Foundry
   correto (nível 1, Guns & Gears Remastered) em vez do nível 0 (Battlecry!). Dano já bate;
   é só nível/fonte errados.
7. **P3 -- Nenhuma ação necessária** para os 16 "faltam_em_nos" de arma, os 2 de familiar, os
   5/6 níveis divergentes e as 2 raridades divergentes -- todos falsos positivos de
   metodologia do comparador (filtro por `kind`, ou reimpressão/rename no dump AoN não
   resolvido antes de comparar). Se o comparador for reusado, vale ele próprio resolver
   `remaster_id` e cruzar `equipment`+`weapon` antes de reportar `faltam_em_nos`.
