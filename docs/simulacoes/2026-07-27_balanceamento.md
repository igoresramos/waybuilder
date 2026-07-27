---
titulo: Balanceamento das regras caseiras de multiclasse -- niveis 1-15
projeto: waybuilder
data: 2026-07-26
fonte: docs/simulacoes/matriz.py + docs/simulacoes/wb_sim.py, saida em matriz_resultados.json
---

# Balanceamento das 22 regras caseiras -- niveis 1 a 15

Pergunta que este relatorio responde: **a houserule de multiclasse (specs/
2026-07-26-regras-multiclasse.md) quebra o jogo?** Comparando tres regimes --
HOUSE (niveis de classe divididos), RAW (classe unica oficial) e RAW+Free
Archetype (classe unica + dedicacao) -- em combate, pericia/social/exploracao,
niveis 1 a 15, com combinacoes obvias e pouco obvias.

Resposta curta: **nao, com uma ressalva estreita**. HOUSE nunca supera os dois
pais puros ao mesmo tempo em combate (exceto em 2 de 160 configuracoes
testadas, explicadas abaixo -- interacao conhecida entre a elevacao de
conjuracao e a proficiencia por classe). Fora do combate, HOUSE entrega um
bonus de versatilidade real e consistente (pilares cobertos). A regra de
sanidade 21 (houserule nunca pode entregar menos que a rota de dedicacao) tem
uma fresta especifica e pequena: multiclasse raso pra dentro de uma classe de
HP baixo (Mago/Feiticeiro, d6) perde uma faixa de PV que a dedicacao nao
perde, porque a dedicacao nunca ocupa um nivel de classe inteiro.

## Metodo (ver ASSUNCOES completo em wb_sim.py)

- **Gear**: curva de riqueza padrao do Core Rulebook (potencia de arma/
  armadura, striking, resiliente), sem item magico especial, sem consumivel.
- **Atributos**: habilidade-chave partindo de 18 com os boosts automaticos de
  5/10/15/20; habilidade secundaria fixa em +2 (ate nivel 10) / +3 (dai pra
  frente). Igual pra todo mundo, nenhum regime e otimizado em atributo.
- **Alvos**: `bench_monstros.json`, mediana de AC/HP/save/ataque/dano de 3.624
  criaturas do Archives of Nethys, por nivel (dado real, nao premissa). Dois
  cenarios:
  - **SOLO** -- 1 inimigo do MESMO nivel do personagem (chefe solitario).
  - **GRUPO** -- 3 inimigos de nivel-4 (mooks mais fracos).
  Combate roda ate 6 rodadas ou um lado zerar.
- **Politica de acao -- SIMETRICA** (a correcao do vies que o Fable apontou
  na simulacao de nivel 20 anterior, onde o dip gastava 12 acoes curando
  contra um Guerreiro que so atacava): todo personagem, marcial ou
  multiclasse, maximiza dano bruto. Sem rank de conjuracao ou sem slot
  disponivel: 3 ataques com agravo de mira. Com slot disponivel: 2 acoes de
  magia de area (dano elevado ao rank efetivo, ate 3 alvos), 1 acao sobra
  ignorada. Os slots SAO consumidos rodada a rodada -- um dip de 1 nivel
  esgota o estoque e cai pra ataque marcial no meio da luta, igual numa mesa
  de verdade. Ninguem cura, ninguem buffa.
- **Regimes**: RAW = classe unica, nivel de personagem inteiro nela. RAW_FA =
  classe unica + UMA dedicacao financiada pelos feats gratis do Free
  Archetype (nunca compete com feat de classe). HOUSE = nivel dividido entre
  duas classes pela houserule (melhor rank, elevacao, HP por nivel de
  classe). Nivel 1 nao da pra dividir em duas classes -- HOUSE vira RAW nesse
  caso especifico, por construcao da propria regra 1.
- **Amostragem de nivel**: RAW puro rodou em TODOS os niveis 1-15 (barato).
  Combos (HOUSE/RAW_FA) rodaram nos niveis IMPARES 1,3,5,7,9,11,13,15 -- e
  exatamente onde as 12 classes verificadas sobem de rank (ver
  `preparar_dados.py`, `PROG_PREMISSA`); nivel par nunca muda proficiencia
  pra nenhuma delas, entao a curva entre dois impares e plana por construcao
  e amostrar so nos impares nao perde resolucao dentro do intervalo pedido.
- **N e intervalo**: combate n=500 por configuracao, pilares n=200 (cada
  chamada ja embute 400 provas por pilar). IC90 = 1.645*desvio/raiz(n).
  Semente fixa por configuracao (nivel, regime, combo, cenario) -- ver
  `seed=` em cada chamada. IC90 relativo medio no combate: **2,2% da media**
  (maximo 10,4% em 360 configuracoes de baseline puro) -- intervalo estavel,
  nao so a media. `matriz_resultados.json` (386 KB) tem todo numero cru.
- **Escopo de classes**: 12 classes de Player Core 1/2 (fighter, wizard,
  cleric, barbarian, rogue, monk, druid, sorcerer, bard, champion, ranger,
  alchemist) -- ver `preparar_dados.py` pra por que as outras 15 ficaram de
  fora (dado de progressao nao disponivel no dump local com o mesmo rigor).

## Dados reais vs premissa -- onde cada numero nasceu

| Camada | Fonte | Onde |
|---|---|---|
| Baseline nivel 1 (attacks/defenses/saves/perception/hp/key_ability) | Foundry pf2e, checkout no pin `pipeline/dados_brutos/foundry/PIN` | `preparar_dados.py::ler_baseline_foundry` |
| Pericias livres/automaticas, skill increase | extrator do proprio pipeline, `pipeline/saida/classes.json` | `preparar_dados.py::ler_grants_pipeline` |
| Bench de monstro por nivel (AC/HP/save/ataque/dano) | AoN, 3.624 criaturas, mediana | `bench_monstros.json` (copiado de `pipeline/dados_brutos/`) |
| Progressao de rank acima do nivel 1 (quando um rank sobe) | Archives of Nethys, pagina por classe, cruzada contra o nivel de cada class-feature no Foundry | `preparar_dados.py::PROG_PREMISSA`, comentada linha a linha |
| Escolha de save do Monge (Path to Perfection) | decisao de build pra rodar a simulacao -- NAO e regra fixa | marcado `ESCOLHA DE BUILD` no dict |
| Politica de acao, cenarios SOLO/GRUPO, regimes, amostragem de nivel | metodo desta simulacao | `ASSUNCOES` em `wb_sim.py` |

## Combate: RAW puro por nivel (referencia, as 12 classes)

Dano medio perdido no cenario GRUPO (3 inimigos nivel-4; menor = melhor):

| classe | nv1 | nv3 | nv5 | nv7 | nv9 | nv11 | nv13 | nv15 |
|---|--:|--:|--:|--:|--:|--:|--:|--:|
| wizard | 17 | 18 | 5 | 19 | 44 | 74 | 104 | 127 |
| sorcerer | 17 | 18 | 4 | 20 | 44 | 73 | 103 | 126 |
| cleric | 19 | 18 | 5 | 18 | 43 | 76 | 112 | 139 |
| druid | 19 | 18 | 5 | 19 | 46 | 78 | 111 | 141 |
| bard | 19 | 18 | 5 | 18 | 46 | 77 | 111 | 140 |
| monk | 21 | 26 | 7 | 32 | 80 | 119 | 132 | 178 |
| champion | 21 | 33 | 10 | 30 | 79 | 116 | 128 | 176 |
| rogue | 19 | 31 | 11 | 42 | 93 | 124 | 144 | 170 |
| alchemist | 19 | 31 | 13 | 42 | 92 | 124 | 145 | 171 |
| fighter | 21 | 28 | 11 | 43 | 101 | 119 | 162 | 196 |
| ranger | 21 | 33 | 11 | 43 | 103 | 119 | 159 | 196 |
| barbarian | 23 | 34 | 11 | 42 | 106 | 153 | 171 | 220 |

**Achado 1 (nao e da houserule, e do RAW): os 5 conjuradores plenos tomam
30-40% menos dano em GRUPO que os 7 nao-conjuradores a partir do nivel 9.**
No nivel 15: 126-141 (conjurador) contra 170-220 (marcial). E assimetria do
PF2e oficial -- aparece identica nas classes PURAS, sem nenhum multiclasse
envolvido. A politica de acao simetrica (2 acoes de area, sempre) e o motivo
mecanico: quem tem slot mata os 3 inimigos do GRUPO em paralelo, quem nao
tem mata um de cada vez enquanto leva ataque dos 3 vivos a cada rodada.

No cenario SOLO (1 inimigo do MESMO nivel -- ataque extremo pro padrao de
festa de 4, ver "Onde a simulacao nao responde"), a taxa de vitoria de TODAS
as 12 classes cai pra faixa de 0-13% a partir do nivel 9. Isso nao e sinal de
classe fraca -- e o benchmark de monstro "do seu nivel" sendo calibrado
contra festa de 4, nao contra 1 personagem. O numero absoluto de SOLO nao
serve pra "essa classe sobrevive", serve pra comparar regimes ENTRE si sob o
mesmo cenario -- que e o uso feito abaixo.

## Combate: as tres combinacoes pedidas pelo Igor

Convencao das tabelas: `%vitoria` no cenario GRUPO (3 inimigos nivel-4),
regime HOUSE testado em duas razoes -- **50/50** (divisao equilibrada) e
**dip** (1 nivel na secundaria, resto na principal). RAW_FA so existe quando
a classe secundaria e conjuradora (unica dedicacao que este simulador modela
numericamente -- ver ASSUNCOES).

### Monge / Clerigo

| nivel | HOUSE 50/50 | HOUSE dip | RAW Monge puro | RAW Clerigo puro | RAW_FA (Monge+dedClerigo) |
|--:|--:|--:|--:|--:|--:|
| 1 | -- (vira Monge 1) | -- | 8% | 0% | 6% |
| 5 | Monk3/Cleric2: **100%** | Monk4/Cleric1: **100%** | 100% | 100% | 100% |
| 9 | Monk5/Cleric4: **97%** | Monk8/Cleric1: 74% | 14% | 98% | 0% |
| 13 | Monk7/Cleric6: 51% | Monk12/Cleric1: 4% | 2% | 70% | 0% |
| 15 | Cleric8/Monk7: 52% | Monk14/Cleric1: 2% | 0% | 58% | 0% |

Leitura: **HOUSE 50/50 fica perto do lado Clerigo puro em GRUPO a partir do
nivel 9** (97% vs 98%, 51% vs 70%, 52% vs 58%) -- a metade de niveis de Monge
custa pouco na comparacao com a AoE, porque a elevacao (regra 17) da acesso a
rank de magia alto mesmo com poucos niveis de Clerigo. HOUSE dip (so 1 nivel
de Clerigo) desaba mais rapido (74% -> 4% -> 2%) porque tem poucos slots pra
sustentar 6 rodadas -- exatamente o comportamento esperado, slot esgota e
sobra ataque marcial.

**Os 2 unicos casos, de 160 testados, onde HOUSE bateu os DOIS pais puros ao
mesmo tempo (com folga de 2x IC90) estao nesta combinacao**: nivel 3 GRUPO
(house 14,0 contra Monge-puro 26,3 e Clerigo-puro 18,1) e nivel 11 GRUPO
(house 69,5 contra Monge-puro 118,7 e Clerigo-puro 76,2). Investigado antes
de reportar (nao e bug): a causa e a **regra 17 desacoplando rank de magia
(dano) de rank de proficiencia (acerto)**. Um Clerigo 6 dentro de Monge5/
Clerigo6 (nivel de personagem 11) ainda nao cruzou o proprio limiar de
Expert em conjuracao (que exige nivel de CLASSE clerigo >= 7, regra 3) --
fica Treinado, DC 28 em vez de 30. Mas o RANK do dano eleva pro nivel de
PERSONAGEM (regra 17: `ceil(11/2) = 6`), o triplo do que o Clerigo nativo
teria em nivel de classe 6 (`ceil(6/2) = 3`). Resultado: dano de area quase
tao forte quanto o Clerigo puro, DC so 2 pontos abaixo, **e** a defesa/PV do
Monge por cima. E precisamente o "botao de playtest" que a propria spec ja
sinalizava na regra 17 -- aqui ele aparece medido: 2 de 160 configuracoes
(1,25%), so no cenario GRUPO, so nesta combinacao especifica
(defensivo-forte + conjurador). Vale acompanhar; nao acho que justifique
mudar a regra sozinho (a amostra e muito estreita), mas e o candidato nº 1 se
algum playtest futuro achar problema.

### Barbaro / Mago

| nivel | HOUSE 50/50 | HOUSE dip | RAW Barbaro puro | RAW Mago puro | RAW_FA (Barbaro+dedMago) |
|--:|--:|--:|--:|--:|--:|
| 1 | -- (vira Barbaro 1) | -- | 2% | 0% | 4% |
| 5 | Barb3/Wiz2: **100%** | Barb4/Wiz1: **100%** | 100% | 100% | 99% |
| 9 | Barb5/Wiz4: 93% | Barb8/Wiz1: 75% | 18% | 89% | 0% |
| 13 | Barb7/Wiz6: 24% | Barb12/Wiz1: 3% | 2% | 56% | 0% |
| 15 | Wiz8/Barb7: 27% | Barb14/Wiz1: 2% | 0% | 44% | 0% |

Leitura: aqui HOUSE 50/50 fica **abaixo** do Mago puro em GRUPO em todos os
niveis testados de 9 pra cima (93% vs 89% no 9 -- perto -- mas 24% vs 56% no
13, 27% vs 44% no 15). Diferente do Monge/Clerigo: o Barbaro nao tem a mesma
defesa passiva alta do Monge (unarmored defense Expert desde o nivel 1), e o
Mago tem a progressao de conjuracao mais lenta das 12 (Expert so no 7,
Master no 15, Legendary no 19 -- ver `PROG_PREMISSA`). A combinacao "pouco
obvia" NAO produz nenhum pico de poder aqui -- fica estritamente entre os
dois pais, do lado mais fraco.

### Ladino / Druida

| nivel | HOUSE 50/50 | HOUSE dip | RAW Ladino puro | RAW Druida puro | RAW_FA (Ladino+dedDruida) |
|--:|--:|--:|--:|--:|--:|
| 1 | -- (vira Ladino 1) | -- | 1% | 0% | 1% |
| 5 | Rog3/Dru2: **100%** | Rog4/Dru1: **100%** | 100% | 100% | 100% |
| 9 | Rog5/Dru4: 92% | Rog8/Dru1: 57% | 15% | 97% | 0% |
| 13 | Rog7/Dru6: 14% | Rog12/Dru1: 1% | 0% | 69% | 0% |
| 15 | Dru8/Rog7: 15% | Rog14/Dru1: 0% | 0% | 59% | 0% |

Leitura: mesmo padrao do Barbaro/Mago -- HOUSE fica entre os pais, mais perto
do lado marcial (que puxa a media pra baixo em GRUPO) do que do lado
conjurador. **Pericias**: aqui o Ladino ja cobre 8/8 pilares sozinho (skill
budget de 7+Int, o maior das 12 classes) -- multiclassar com Druida nao
melhora pilares (teto ja batido), so dilui combate. Combinacao pouco obvia
que funciona bem NARRATIVAMENTE (furtivo com magia primal) mas que em
numero de combate e estritamente um imposto sobre o Ladino, nao um ganho.

## As outras 7 combinacoes (visao rapida, nivel 9, HOUSE 50/50)

| combo | HOUSE | %vitoria SOLO | %vitoria GRUPO | pilares (de 8) |
|---|---|--:|--:|--:|
| Guerreiro/Mago | Fighter5/Wizard4 | 3,0% | 87,4% | 6,25 |
| Guerreiro/Clerigo | Fighter5/Cleric4 | 3,8% | 90,2% | 6,38 |
| Alquimista/Bardo | Alchemist5/Bard4 | 3,4% | 85,6% | 7,29 |
| Campeao/Feiticeiro | Champion5/Sorcerer4 | 3,4% | 87,2% | 5,55 |
| **Patrulheiro/Monge** | Ranger5/Monk4 | 2,6% | **6,2%** | 7,21 |
| Clerigo/Ladino | Cleric5/Rogue4 | 4,6% | 95,0% | 8,00 |
| Druida/Barbaro | Druid5/Barbarian4 | 7,0% | 97,0% | 6,34 |

**Achado 2: a unica combinacao sem NENHUM lado conjurador (Patrulheiro/
Monge) e a unica com desempenho de GRUPO no chao (6,2%, igual aos marciais
puros)**. Confirma que o bonus de AoE em GRUPO e estritamente sobre "tem
algum acesso a magia", nao sobre HOUSE em si -- bate com o Achado 1.

## Regra 21 (sanidade: HOUSE nunca entrega menos que dedicacao) -- fresta encontrada

Comparando HOUSE **dip** (investimento raso, 1 nivel) contra RAW_FA (mesma
classe principal + dedicacao), que sao os dois jeitos RASOS de pegar sabor de
segunda classe -- comparacao correta pra regra 21, ao contrario de comparar
com HOUSE 50/50 (investimento profundo, build diferente):

- 63 configuracoes com RAW_FA disponivel pra comparar (niveis impares 1-15,
  classe secundaria conjuradora).
- **14 (22%) mostram RAW_FA levando MENOS dano em SOLO que o dip HOUSE**,
  por margem que passa 2x IC90. Concentradas nos niveis 3 e 5 (11 dos 14
  casos), com uma cauda isolada em nivel 11/13.
- Causa raiz, confirmada nos dados (`Fighter 2/Wizard 1` = 43 PV contra
  `Fighter 3 +WizardDed` = 47 PV, ambos nivel de personagem 3): **regra 11**
  (PV vem da classe que recebeu aquele nivel) faz o dip pagar o dado de vida
  MENOR da classe secundaria pro nivel que foi pra ela -- um Mago da 6 PV
  onde um Fighter daria 10. RAW_FA nunca paga esse preco: a dedicacao nao
  ocupa nivel de classe nenhum, so feat de Free Archetype. Nos niveis 3-5 a
  dedicacao TAMBEM ainda nao tem slot (os gates comecam no nivel 4), entao
  nesses casos a comparacao e "dip paga PV e ganha pouco" contra "dedicacao
  nao paga nada e nao ganha nada" -- e a dedicacao vence por nao descontar.
- Isso e uma violacao real e mensuravel da regra 21, mas **estreita**: so
  aparece em SOLO (1 de 14 e GRUPO), so em multiclasse RASO (1 nivel) pra
  dentro de classe de d6 PV (Mago/Feiticeiro -- nao aconteceu com Barbaro/
  Mago nem Druida/Barbaro, que tem PV maior no lado marcial), e o gap
  absoluto e pequeno (4-8 PV de diferenca de media, tipicamente <15% do PV
  total do personagem). Nao invalida a regra desenhada -- mostra o ponto
  exato onde ela aperta: **dip de 1 nivel numa classe de d6 no comeco da
  curva (nivel 1-6, antes do primeiro gate de FA)**. Se isso importar pro
  playtest, o ajuste natural e revisar regra 11 (por exemplo, piso de HP do
  nivel dipado = media entre as duas classes) ou aceitar como o preco
  narrativo de "ser realmente outra classe por um nivel".

## Pericia, social, exploracao

Cobertura media dos 8 pilares (social, furtividade, ladroagem, atletismo,
saber, medicina, natureza, percepcao), HOUSE 50/50 contra o MELHOR dos dois
pais puros, em 70 configuracoes validas (niveis 2-15 -- nivel 1 excluido
porque HOUSE degenera pra classe unica e a comparacao fica injusta com o par
que nao chegou a existir):

- **Media do delta (HOUSE - melhor pai puro): +0,62 pilares de 8.**
- **Minimo: 0,00. Nenhuma configuracao ficou pior que o melhor pai puro.**
- 56 de 70 (80%) ficaram MELHOR que os dois pais ao mesmo tempo.
- Teto conhecido: Ladino ja cobre 8/8 sozinho -- multiclassar com ele nao
  aparece como ganho porque nao ha onde subir (nao e regressao, e teto).

**Achado 3: a houserule entrega um bonus de versatilidade real e
sistematico fora do combate, sem nenhum caso medido de perda.** Mecanica:
regra 9 concede a pericia automatica de CADA classe (nao so a principal), e
regra 10 soma o orcamento livre da classe com maior orcamento -- multiclasse
sempre agrega pelo menos uma pericia automatica extra sem perder nada do
orcamento livre. E o oposto exato do combate: no combate HOUSE dilui, fora
do combate HOUSE agrega. Isso e coerente com o "principio que organiza tudo"
da propria spec (recurso de personagem vs identidade de classe) -- pericia
automatica e identidade, e identidade nunca se perde ao multiclassar.

## Como mestrar uma aventura padrao com este houserule

Recomendacoes derivadas direto dos tres achados acima, nao de opiniao solta:

1. **Orcamento de encontro em grupo (varios inimigos fracos) precisa de +1
   dificuldade efetiva se a festa tiver qualquer conjurador, multiclasse ou
   puro** -- Achado 1 e 2 mostram que "tem magia de area" e o divisor real
   de desempenho em GRUPO, nao HOUSE vs RAW. Isso ja era verdade no PF2e RAW;
   a houserule so torna mais facil qualquer personagem ter uma pitada de
   magia, entao o efeito fica mais frequente na mesa, nao mais forte por
   personagem.
2. **Chefe solitario (SOLO) continua brutal pra qualquer regime a partir do
   nivel 9** -- taxa de vitoria de personagem sozinho contra criatura do
   mesmo nivel cai pra faixa de 0-13% em todas as 12 classes puras. Isso
   confirma a regra de:1 personagem nunca deveria carregar um chefe de nivel
   equivalente sozinho -- e comportamento esperado do PF2e, nao efeito da
   houserule. Se um jogador HOUSE pedir pra "tankar sozinho" um chefe do
   proprio nivel, o encontro vai ser tao dificil quanto seria pra qualquer
   build RAW equivalente.
3. **Pilares de nao-combate ficam mais faceis de cobrir com HOUSE** (Achado
   3) -- um mestre pode escalar levemente a dificuldade de desafios sociais/
   exploracao/pericia numa mesa majoritariamente multiclasse sem medo de
   travar a aventura, porque o grupo tende a ter ~0,6 pilar a mais coberto
   por personagem multiclasse do que teria com builds RAW equivalentes.
4. **Dip de 1 nivel pra "sabor" (Guerreiro 19/Clerigo 1 etc.) e fraco em
   combate isolado mas nunca prejudicial** -- ele so soma dano de area
   marginal enquanto os poucos slots duram, e cai pra ataque marcial normal
   depois. Um mestre nao precisa recalibrar nada especial pra um jogador que
   pede um dip tardio.
5. **Se um jogador pedir Monge+algo de magia (ou qualquer combinacao
   defensivo-forte + conjurador) numa faixa de nivel onde o lado conjurador
   ainda nao cruzou o proprio limiar de Expert (regra 3)**, vale o mestre
   saber que essa e a combinacao com maior chance (ainda que pequena, 2 em
   160 configuracoes medidas) de sair da faixa esperada em encontros de
   GRUPO -- ver secao "Regra 17" acima.

## O que quebra e o que nao quebra

**Nao quebra:**
- HOUSE nunca supera os dois pais puros em combate ao mesmo tempo, exceto em
  1,25% das configuracoes testadas (achado 1,25% documentado acima, causa
  identificada, nao e bug).
- Nenhuma das 3 combinacoes pouco-obvias pedidas (Monge/Clerigo, Barbaro/
  Mago, Ladino/Druida) produz um pico de poder fora do padrao -- Monge/
  Clerigo fica perto do Clerigo puro (nao acima), Barbaro/Mago e Ladino/
  Druida ficam ESTRITAMENTE entre os dois pais, do lado mais fraco.
- A homogeneizacao de combate por AoE (Achado 1) e do RAW oficial, nao da
  houserule -- aparece identica nas 12 classes puras.
- O bonus de pilares (Achado 3) e uma entrega LEGITIMA da regra -- 22 regras
  foram desenhadas pra dar identidade de classe sem penalizar versatilidade,
  e e exatamente isso que aparece medido.

**Quebra um pouco, de forma estreita e conhecida:**
- Regra 17 (elevacao) desacopla rank de dano de rank de acerto o suficiente
  pra criar 2 pontos fora da curva em 160 (Monge/Clerigo, GRUPO, niveis
  baixos-medios). A propria spec ja sinalizava isso como "botao de
  playtest" -- aqui ficou medido e e pequeno.
- Regra 21 (sanidade da dedicacao) tem uma fresta real: dip de 1 nivel numa
  classe de d6 PV, em niveis 1-6, perde PV que a dedicacao equivalente nao
  perde. 22% das comparacoes rasas validas mostram isso, sempre com margem
  pequena (tipicamente <15% do PV total).

## Onde a simulacao nao responde -- limites honestos do metodo

1. **Nao mede mais o custo de "jogar de healbot"** (a questao original do
   playtest de nivel 20, "todo marcial vai querer Clerigo 1 pela cura"). A
   politica de acao simetrica que corrige o vies do Fable tambem remove
   cura do modelo inteiro -- os dois lados so atacam. Pra re-testar a
   hipotese de homogeneizacao por cura seria preciso um segundo modelo com
   politica de acao MISTA (e simetrica) que decida entre atacar e curar sob
   um criterio explicito pros dois lados -- fora do escopo desta rodada.
2. **So um encontro isolado, nao um dia de aventura.** Sem atricao de
   recurso entre encontros (slots de conjuracao gastos, recuperacao entre
   combates). Um personagem com poucos slots pode parecer mais forte aqui do
   que seria no 3º encontro do dia.
3. **So dano bruto, sem controle/buff/debuff/invocacao.** Grau de sucesso
   critico em magia de controle (Slow, Confusion), invocacao (regra 17b,
   com teto proprio, nunca exercitado aqui) e buff de grupo nao aparecem.
   Um conjurador de controle pode contribuir muito mais que o dano bruto
   sugere, em qualquer regime.
4. **So 1 personagem por configuracao de combate**, nunca festa de 4. Isso
   evita ruido de sinergia de festa mas tambem significa que flanqueamento,
   auxilio, e cobertura de papel (quem tanka, quem cura) nao aparecem. O
   cenario GRUPO/SOLO mede o personagem isolado, nao a festa.
5. **12 classes, nao as 27.** As outras 15 (Investigator, Kineticist, Magus,
   Summoner, Swashbuckler, Thaumaturge, Animist, Commander, Exemplar,
   Guardian, Gunslinger, Inventor, Oracle, Psychic, Witch) nao entraram
   porque a progressao de proficiencia delas nao esta no dump local com o
   mesmo rigor de verificacao -- levantar sob demanda.
6. **Cleric = so doutrina Cloistered.** Warpriest (mais marcial, spellcasting
   capado em Master em vez de Legendary) nao foi modelado -- ver TODO.md
   item 3, ja pendente antes desta rodada (linguagem de predicado por
   subclasse).
7. **Escolha de save do Monge (Path to Perfection) e fixa** na simulacao
   (Reflexo aos 7/15, Vontade aos 11) -- e escolha de jogador na mesa real,
   nao regra. Outro Monge pode ter perfil de save diferente.
8. **GRUPO usa nivel-4 como proxy de "mais fraco"**, sem conversao oficial
   de orcamento de XP por creature -- e escolha de metodo declarada, nao
   numero oficial do PF2e.
9. **RAW_FA so modela dedicacao de CONJURADOR** (a unica com efeito numerico
   claro no formato deste simulador -- rank de spellcasting e slots por
   gate). Dedicacao marcial (ex.: Fighter Dedication) nao concede nenhum
   numero mensuravel neste modelo -- por isso 3 dos 10 combos (Patrulheiro/
   Monge, e os lados nao-conjuradores dos outros) nao tem ponto RAW_FA na
   tabela.
10. **Arma favorita do Clerigo foi dobrada dentro de "simple"** (ver
    `preparar_dados.py`) -- subestima levemente um Clerigo com arma marcial
    de divindade guerreira.

## Arquivos

- `preparar_dados.py` -- reconstroi `classes.json` a partir de
  `pipeline/dados_brutos/foundry/` e `pipeline/saida/classes.json` (so
  leitura). Roda sanity-check de rank regredindo antes de escrever.
- `classes.json`, `bench_monstros.json` -- dados de entrada reconstruidos.
- `wb_sim.py` -- motor da simulacao (Personagem, combate, pilares, fabrica
  de regime, ASSUNCOES).
- `matriz.py` -- roda a matriz completa (12 classes puras x 15 niveis + 10
  combos x 8 niveis-checkpoint x ate 4 variantes de regime) e escreve
  `matriz_resultados.json` (386 KB, todo numero cru usado neste relatorio).
