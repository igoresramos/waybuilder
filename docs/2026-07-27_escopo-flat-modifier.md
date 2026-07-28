# Escopo de `flat_modifier` e `proficiency` nao-literal na base

Data: 2026-07-27
Metodo: medicao exaustiva via script Python sobre `pipeline/base/index.json` (19.705 registros). Nenhum arquivo `.py` do projeto foi alterado. Scripts em `/tmp/claude-1000/.../scratchpad/analyze_flat_modifier.py` e `classify.py` (descartaveis).

---

## 1. FLAT_MODIFIER

### 1.1 Volume total

- **1.709 ocorrencias** de `flat_modifier` em **1.485 registros distintos**.
- Distribuicao por `kind` de origem (ocorrencias / registros distintos):

| kind | ocorrencias | registros distintos |
|---|---|---|
| equipment | 806 | 681 |
| feat | 591 | 526 |
| weapon | 146 | 134 |
| heritage | 98 | 84 |
| armor | 46 | 41 |
| shield | 20 | 17 |
| familiar-ability | 2 | 2 |

`selector` e string em 1.427 ocorrencias e lista (multi-selector) em 282.

### 1.2 Ranking de selectors (top 20 por ocorrencia)

| ocorrencias | selector |
|---|---|
| 200 | saving-throw |
| 113 | perception |
| 95 | athletics |
| 90 | diplomacy |
| 80 | performance |
| 75 | skill-check |
| 64 | intimidation |
| 63 | deception |
| 52 | stealth |
| 39 | survival |
| 37 | ac |
| 37 | religion |
| 36 | land-speed |
| 33 | crafting |
| 30 | acrobatics |
| 29 | nature |
| 25 | strike-damage |
| 23 | thievery |
| 22 | hp |
| 21 | initiative |

Ha **328 familias distintas de selector** (combinacoes unicas de selector/lista-de-selectors), com cauda longa de selectors especificos de arma/item (ex.: `tiger-claw-damage`, `{item|_id}-damage`) que ocorrem 1-2 vezes cada.

### 1.3 Classificacao por familia (A / B / C)

Criterio: classifiquei cada um dos 131 componentes de selector distintos (nao cada tupla) em A/B/C, e uma tupla composta herda B se qualquer componente for B (regra de dominancia: um bonus que so vale numa rolagem de ataque continua sendo mecanica de combate mesmo que tambem toque uma pericia).

- **(A) Numero de ficha**: pericias (incluindo Lore com todos os sinonimos), `saving-throw`/`fortitude`/`reflex`/`will`, `ac`, `initiative`, `hp`, familia de velocidade (`speed`, `land-speed`, `fly-speed`, `swim-speed`, `climb-speed`, `all-speeds`), `spell-dc`, e `all` (bonus generico "as suas defesas").
- **(B) Mecanica de combate/situacional**: qualquer selector de dano ou rolagem de ataque (`strike-damage`, `*-attack-roll`, `spell-attack`, `spell-damage`, `weapon-damage`, todo o grupo `{item|...}-damage`/`-attack`, selectors nomeados de arma especifica), `skill-check`/`*-skill-check`/`check`/`perception-check`/`athletics-check` genericos (sempre situacionais nos exemplos lidos: Recall Knowledge, Escape, Aid), e `dying-recovery-check`.
- **(C) Duvidoso**: familia `*-dc` (`reflex-dc`, `fortitude-dc`, `will-dc`, `deception-dc`, `athletics-dc`, `perception-dc` -- DC que outros usam contra sua salvaguarda/pericia, nao a sua propria DC; mistura de uso permanente em itens e situacional em feats), `healing`/`healing-received`/`inline-healing` (nao e "numero parado", so importa quando algo cura o personagem), e os placeholders dinamicos `{item|flags.system.rulesSelections.*}` (o valor real depende de uma escolha dentro do item, ainda nao resolvida nos dados).

Resultado agregado:

| Grupo | Ocorrencias | Registros distintos que tocam o grupo |
|---|---|---|
| A | 1.370 (80,2%) | 1.210 |
| B | 272 (15,9%) | 255 |
| C | 67 (3,9%) | 64 |

(Soma dos "registros distintos" excede 1.485 porque alguns registros tem ocorrencias em mais de um grupo.)

Familias mais pesadas de cada grupo:

- **A**: `saving-throw` (200), `perception` (113), `athletics` (95), `diplomacy` (90), `performance` (80), `intimidation`+`deception`+`stealth`+`survival`+`religion`+`ac` (37-64 cada).
- **B**: `skill-check` (75), `strike-damage` (25), `{item|id}-ranged-damage` (21), `{item|id}-damage` (17), `strike-attack-roll` (8).
- **C**: `{item|flags.system.rulesSelections.skill}` (10), `perception-dc` (8), `reflex-dc` (6), `healing-received` (6), `fortitude-dc`+`reflex-dc` combinado (6).

### 1.4 Feats destravados se o motor aplicasse so o Grupo A

Defini "entrega NADA hoje" de forma literal e replicavel: **todos** os grants do registro sao `flat_modifier` (nenhum outro tipo de grant presente) e nenhum desses `flat_modifier` tem `selector == "hp"` (unico caso ja aplicado pelo motor). Essa e a generalizacao exata do padrao que motivou a tarefa (dedicacoes com "unico grant estruturado = flat_modifier").

- **1.194 registros** no total se encaixam nesse criterio (equipment 642, feat 385, weapon 116, armor 34, shield 17). Ou seja, o problema e maior em equipamento do que em feats -- fora do escopo pedido, mas relevante para dimensionar decisao futura.
- Entre os **385 feats**: **13 sao dedicacoes de arquetipo** (trait `dedication`). Nao confirmei os "15" da varredura manual inicial -- a contagem exaustiva da 13 com selector nao-hp puro (mais 1, `stonebound-dedication`, que usa `hp` e portanto ja funciona hoje).
- Se o motor passar a aplicar o Grupo A inteiro (condicional ou nao): **9 das 13 dedicacoes** ganhariam algo na ficha; **271 dos 372 feats nao-dedicacao** (72,8%) tambem.
  - As 4 dedicacoes que continuariam vazias: `pathfinder-agent-dedication` e `ritualist-dedication` (`skill-check`, B), `swordmaster-dedication` (`reflex-dc`, C), `warrior-of-legend-dedication` (dano de grupo de arma, B).
- **Mas ha uma ressalva importante** (ver 1.5): se o motor so aplicar com seguranca os casos **incondicionais** de Grupo A (bonus permanente, sem gatilho), o numero cai para **15 dos 385 feats** (3,9%) e **1 das 13 dedicacoes** (`bellflower-dedication`, +10 land-speed incondicional). O resto (985 ocorrencias de Grupo A, 72% do grupo) e marcado `condicional: true` e normalmente representa bonus estreito (ex.: "+2 contra veneno inalado", "+2 em Atletismo so para Empurrar/Derrubar"), que nao pode virar um numero simples somado ao total sem misrepresentar a regra.

### 1.5 O campo `condicional` e confiavel para separar A de B?

Nao. Medido:

- Dentro do **Grupo A**: 1.370 ocorrencias, das quais **985 (71,9%) tem `condicional: true`**. Ou seja, a maioria das ocorrencias que sao conceitualmente "pericia/salvaguarda/AC/velocidade" e, na pratica, um bonus estreito e situacional (ex.: `fey-transcendence` +2 status em saves so contra ilusao/emocao/encantamento; `gas-mask-of-clean-air` +1 item em saves so contra veneno inalado; `stampede-medallion-greater` +2 em Atletismo so para Empurrar/Derrubar). Aplicar isso como soma incondicional ao total da pericia estaria errado na maior parte dos casos.
- Dentro do **Grupo B**: 272 ocorrencias, das quais **48 (17,6%) tem `condicional` ausente/false** -- ou seja, ~1 em 6 selectors de combate aparecem como "sempre ativos" nos dados, o que tambem impede usar "condicional ausente => seguro aplicar" como regra geral.

**Criterio melhor**: a familia do selector (pericia/save/AC/velocidade vs. dano/ataque/DC-de-defesa) decide o que e "numero de ficha" em principio, mas dentro do Grupo A o campo `condicional` ainda e necessario para decidir COMO mostrar -- soma direta ao total (28% dos casos, incondicionais) vs. lista separada de "bonus situacionais" (72% dos casos, precisa de rotulo tipo "contra veneno inalado"). Nao existe hoje um campo estruturado com o predicado ("contra o que"/"quando") -- so o texto livre do registro. Portanto o campo `condicional` sozinho serve para **rotear** (numero direto vs. lista de situacionais), nao para decidir sozinho o que aparece.

---

## 2. PROFICIENCY com valor nao-literal

### 2.1 Volume

**57 ocorrencias em 17 registros distintos, todos `kind: feat`.** Nenhum equipment/weapon/armor/heritage tem esse problema -- e uma questao concentrada em feats de arquetipo/ancestralidade que dao proficiencia "espelhada" em outra proficiencia.

### 2.2 Formas encontradas

| Forma | Ocorrencias / registros | Significado em regra PF2e | Convertivel para declarativo? |
|---|---|---|---|
| `@actor.system.proficiencies.attacks.unarmed.rank` | 40 / 7 (`azarketi-weapon-expertise`, `conrasu-weapon-expertise`, `executioner-weapon-training`, `genie-weapon-expertise`, `ghoran-weapon-expertise`, `vanara-weapon-expertise`, `vishkanya-weapon-expertise`) | "Sempre que voce ganhar proficiencia especialista+ numa arma X (de classe), ganhe a mesma proficiencia num conjunto fixo de armas de ancestralidade." O valor e um espelho continuo do rank de Ataque Desarmado. | **Sim, facil.** E um unico padrao reutilizavel: `linked_proficiency: mirror_from=unarmed`, sem teto nem calculo extra. Cobre 70% das ocorrencias com uma unica regra generica. |
| `max(defesa-media.rank, ternary(nivel>=13, min(defesa-desarmada.rank,expert), trained))` (variacoes light/medium/heavy) | 10 / 4 (`champion-dedication`, `guardian-dedication`, `sentinel-dedication`, `armigers-protection`) | Dedicacao de armadura classica: treinado em light+medium (ou heavy se ja tinha as duas); ao ganhar especialista+ numa armadura irma, ganha o mesmo na desta feat; aos 13+, ser especialista em Defesa Desarmada tambem conta. | **Sim, moderado.** Mesma formula reaparece identica nas 3 dedicacoes -- vale a pena um unico primitivo `linked_proficiency` com clausula de nivel opcional, em vez de reimplementar por feat. |
| `max(defesa-A.rank, defesa-B.rank, ...)` sem clausula de nivel | 4 / 3 (`harbingers-protection`, `mountain-skin` x2, `warpriests-armor`) | Mesma ideia, mas mais simples: "ao ganhar especialista+ em qualquer/outra armadura, ganhe tambem nesta". | **Sim, facil.** Subconjunto mais simples do mesmo primitivo acima (sem a clausula de nivel 13). |
| `ternary(nivel>=19,3,ternary(nivel>=13,2,1))` | 1 / 1 (`invulnerable-rager`) | Rank de heavy armor sobe so por nivel de personagem (1=trained em 1, 2=expert aos 13, 3=master aos 19), sem referenciar outra proficiencia. | **Sim, trivial.** E so uma tabela nivel->rank. |
| `min(cap, @actor.flags.system.<feat>.count)` | 2 / 2 (`reclaimant-plea`, `vigilant-benediction`) | Feat repetivel (ate 3x): cada selecao extra sobe o rank de spellcasting divino em 1 degrau, ate um teto (expert na 2a, master na 3a). O rank depende de "quantas vezes voce pegou este feat", nao de outra proficiencia. | **Sim, mas padrao diferente.** Precisa de "contador de selecoes do mesmo feat_id", nao de espelhamento entre proficiencias -- primitivo separado, isolado (so 2 registros). |

Todos os 17 registros/formas sao listados acima (numero pequeno, cobertura de 100%).

### 2.3 Caso citado (`sentinel-dedication`)

Confirmado: esta no grupo "max/ternary com clausula de nivel 13" junto com `champion-dedication` e `guardian-dedication` -- as 3 sao a mesma dedicacao de armadura de arquetipo (Player Core 2), reaproveitando a formula identica. Resolver esse padrao uma vez resolve as 3 (mais `armigers-protection`, que so tem `light` na base).

---

## Resumo e recomendacao

- `flat_modifier`: 1.709 ocorrencias / 1.485 registros. 80% (1.370 ocorrencias) sao conceitualmente "numero de ficha" (pericia/save/AC/velocidade/iniciativa), mas **72% delas sao condicionais** (bonus estreito, tipo "so contra veneno inalado") -- nao da pra somar direto ao total sem uma UI de "bonus situacional" separada.
- Implementar so os casos **incondicionais** de Grupo A e a fatia mais barata e mais segura, mas destrava pouco: 15 de 385 feats "vazios" (3,9%), so 1 de 13 dedicacoes.
- Implementar o Grupo A **inteiro** (incluindo condicionais, exibidos como lista de bonus situacionais em vez de soma direta) destrava 271/372 feats nao-dedicacao e 9/13 dedicacoes -- ganho real, mas exige UI nova (lista "bonus condicionais" por pericia/save), nao so uma soma no motor.
- Grupo B (dano/ataque, 16% das ocorrencias) esta corretamente fora do escopo do Waybuilder (mecanica de combate) -- nao vale implementar.
- `proficiency` nao-literal: so 17 feats, 57 ocorrencias, 100% resolviveis com 2 primitivos declarativos (`linked_proficiency` espelhando outra proficiencia -- cobre 15 dos 17 registros -- e "contador de selecoes do feat" para os 2 restantes). Baixo volume, alto reaproveitamento (o padrao de espelhamento de arma cobre sozinho 7 registros e 40 ocorrencias).

**Recomendacao**: vale a pena (a) o `flat_modifier` incondicional de Grupo A (ganho pequeno mas de custo quase zero -- e so aplicar a mesma logica que ja existe para `hp`) e (b) o `linked_proficiency` para espelhamento de proficiencia (resolve 15/17 do problema 2 com um unico primitivo simples, sem depender de avaliar expressoes Foundry). NAO vale, no minimo por agora: Grupo B/C de `flat_modifier` (fora de escopo ou baixo volume) nem a UI de "bonus situacionais condicionais" (72% do Grupo A) -- isso e feature nova de exibicao, nao so parsing, e merece spec propria antes de entrar.
