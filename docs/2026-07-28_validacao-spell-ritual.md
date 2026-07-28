# Validacao: spell, ritual e conjuracao no motor

Data: 2026-07-28. Escopo: `pipeline/base/index.json` (kinds `spell` e `ritual`),
cruzamento com `pipeline/dados_brutos/aon_spells.json` e `aon_rituals.json`, e
`motor/motor.py::_conjuracao` contra `specs/2026-07-26-regras-multiclasse.md`
(regras 16, 17, 17b, 18). Trabalho de VALIDACAO -- nenhum `.py` foi alterado.

Metodo: toda contagem abaixo saiu de script Python rodado contra os arquivos
reais, sem estimativa. Scripts ficaram em
`/tmp/claude-1000/.../scratchpad/analyze_spells.py` e `analyze_rituals.py`
(descartaveis, fora do repo).

**Correcao de contagem:** a tarefa citava 1.642 spells. O numero real medido em
`index.json` e **1.655** (`kind=spell`). Rituais batem: **151**.

---

## 1. Spell (1.655 registros)

### 1.1 Level -- 100% preenchido, e o cantrip NAO e level 0

```
sem 'level': 0 / 1655
distribuicao: {1: 464, 2: 213, 3: 234, 4: 258, 5: 179, 6: 101, 7: 78, 8: 55, 9: 46, 10: 27}
```

O conserto recente esta confirmado: cobertura de `level` e 100%. Distribuicao
cai suavemente do rank 1 ao 10, como esperado (mais spells de baixo nivel
publicadas ao longo dos anos).

**Cantrip e level 1, nao level 0.** Conferido: dos 112 spells com trait
`cantrip`, a distribuicao de `level` e `{1: 94, 2: 2, 3: 8, 5: 7, 7: 1}` --
NUNCA 0. Isso bate com o AoN e com o remaster do PF2e: cantrips sao "level 1"
na tabela de rank e escalam por `Heightened`, sem rank 0 proprio (o rank 0
e convencao de outras ferramentas, nao do sistema). Os cantrips de nivel > 1
sao os concedidos por classe/feat em nivel superior ao 1 (ex.: cantrips de
arquetipo ou feature tardia) -- coerente.

**`rank` quase espelha `level`, com 17 excecoes.** `rank` falta em 17 registros
onde `level` esta preenchido. Investigado: **os 17 sao a mesma familia** --
registros com campo `desmembrado_de` apontando pra um id canonico que TEM
`rank`/`tradicoes`/tudo preenchido (ex.: `wb:spell/object-reading-uncommon`
aponta pra `wb:spell/object-reading`, que existe e esta completo). Sao
remanescentes de uma dedupe/fusao incompleta -- duplicatas orfas de uma
variante "-uncommon"/"-evocation" que ficaram pra tras sem o `rank` que a
fusao normalmente copia. Nao contaminam a contagem funcional (a base tem o
registro certo com outro id), mas sao 17 ids "zumbis" com dado incompleto
que, se referenciados em algum `requires`/`grants` por engano, quebrariam
silenciosamente. Lista completa capturada no script; amostra:
`pillar-of-water-uncommon`, `powerful-inhalation-evocation`,
`stone-lance-evocation`, `tireless-worker-necromancy`,
`chilling-spray-evocation`, `imprint-message-uncommon`.

### 1.2 Traditions (`tradicoes`)

```
sem 'tradicoes' (vazio ou None): 526 / 1655
  com trait 'focus': 472
  SEM trait 'focus' (nao explicado por focus spell): 54
```

A hipotese da tarefa bate parcialmente: a maioria (472/526 = 89,7%) da
ausencia de tradicao e legitima -- magia de foco de classe realmente nao tem
tradicao livre (ela e amarrada a classe, nao a lista arcane/divine/occult/
primal). Mas sobram **54 spells sem tradicao livre E sem trait `focus`**.
Investigando essas 54: **todas tem o campo `tradicao_de_classe` preenchido**
(ex.: `bard`, `witch`, `psychic`, `summoner`) -- ou seja, o dado NAO esta
ausente, esta em outro campo. O motor/app so vai ler tradicao errado se olhar
so pra `tradicoes` e ignorar `tradicao_de_classe`. Nao e lacuna de dado, e
risco de leitura incompleta por quem consumir o campo errado -- vale
documentar isso pra quem for montar a tela de "spells disponiveis por
tradicao".

`tradicao_de_classe` no total: preenchido em 86/1655 (a maioria dos 54 acima
mais alguns outros). Contagem por tradicao livre:
`{'arcane': 777, 'primal': 590, 'occult': 635, 'divine': 445}`.

### 1.3 Campos essenciais pra ficha

Nomenclatura real da base (portugues, nao os nomes em ingles citados na
tarefa): `acoes` (tempo de conjuracao), `alcance` (range), `duracao`,
`defesa` (save), `traits`, `rarity`. **Nao existe campo `targets`/`alvos`
estruturado -- 0/1655.** O alvo so existe dentro da prosa (`texto`).

```
faltando 'acoes'    : 32 / 1655
faltando 'alcance'  : 539 / 1655
faltando 'targets'  : 1655 / 1655  (campo nao existe, 100% ausente)
faltando 'duracao'  : 556 / 1655
faltando 'defesa'   : 925 / 1655
faltando 'traits'   : 45 / 1655   (presente mas vazio [])
faltando 'rarity'   : 0 / 1655
```

Investigado cada um pra separar "ausencia legitima" de "buraco de extracao":

- **`acoes` (32 faltando):** 17 sao os zumbis `desmembrado_de` do item 1.1.
  Os outros **15 sao buraco real de extracao**, todos spells LEGACY
  (`source.remaster: false`, mecanica de alinhamento removida no remaster):
  `litany-against-sloth`, `litany-against-wrath`, `litany-of-depravity`,
  `litany-of-righteousness`, `litany-of-self-interest`,
  `touch-of-corruption`, `undetectable-alignment`, `vindicators-judgement`,
  `detect-alignment`, `discomfiting-whisper`, `dragon-claws`, `dread-aura`,
  `efficient-apport`, `glyph-of-warding`, `misdirection`. Confirmado
  manualmente: a prosa (`texto`) desses 15 **contem** "Single Action" /
  "Two Actions" / "Cast 10 minutes" logo no cabecalho -- o parser tinha o
  dado e nao extraiu pra `acoes`. Reproducao:
  `wb:spell/glyph-of-warding` -> `texto` comeca com
  `"Glyph of Warding Source Core Rulebook pg. 341 ... Cast 10 minutes
  (material, somatic, verbal) Range touch..."`, mas `acoes` e `null`.

- **`alcance` (539 faltando):** a maioria e legitima -- spells de auto-alvo
  (self/touch implicito) nao imprimem linha "Range" no stat block oficial.
  Mas **23 desses 539 tem a palavra "Range " dentro da propria `texto`**,
  ou seja tinham o dado e ele nao foi capturado -- outro buraco de extracao,
  menor que o de `acoes` mas do mesmo tipo.

- **`targets` (100% ausente):** nao e bug de extracao, e ausencia de
  *schema*. O dado de alvo existe na prosa (`Target 1 creature`, etc., visivel
  no `texto` de varios exemplos acima) mas nunca foi promovido a campo
  estruturado. Se a ficha precisa mostrar "alvo: 1 creature" sem parsear
  texto livre, falta essa coluna inteira no pipeline.

- **`duracao` (556) e `defesa` (925):** nao investiguei um a um (volume
  grande, a maior parte deve ser legitima -- spell instantanea nao tem
  duracao, spell sem save nao tem defesa), mas dado o padrao encontrado em
  `acoes`/`alcance` (parser perde dado presente na prosa numa fatia pequena
  e legacy), e razoavel supor uma fatia semelhante de buraco real aqui
  tambem. Nao medi essa fatia -- fica como proximo passo se for decidido
  investir tempo.

- **`traits` vazio (45):** confirmado como lista vazia real (`[]`), nao
  ausencia do campo (o campo esta presente em 1655/1655). Todos os 45 tem
  `rank`/`tradicoes` normais -- e plausivel que sejam spells realmente sem
  trait de escola/execucao no remaster (o remaster extinguiu traits de
  escola de magia), mas nao confirmei um a um contra o AoN.

### 1.4 Heightened / elevacao

```
sem campo 'heightened'                : 17  (os mesmos zumbis desmembrado_de)
'heightened' == [] (vazio)            : 1125
'heightened' com dado ESTRUTURADO     : 513
'heightened_so_prosa' == true         : 448
sem estruturado E sem so_prosa (nem indicado) : 694
```

Existe campo estruturado (`heightened`, lista de `{tipo, passo, efeito}` --
ex.: `{"tipo": "incremental", "passo": 3, "efeito": "(ver texto)"}`), mas so
**513/1655 (31%)** tem dado estruturado de fato. Ha uma flag
`heightened_so_prosa` que marca 448 casos como "so da pra saber pela prosa" --
presumivelmente honesta (o pipeline sabe que nao conseguiu estruturar e
avisa). Mas sobram **694 spells (42%) sem heightened estruturado E sem a flag
de so-prosa marcada** -- nao da pra saber, so olhando o dado, se esses 694
simplesmente nao tem elevacao (spells de rank fixo, legitimo) ou se e lacuna
silenciosa de extracao. Nao investiguei essa fatia spell a spell; e o maior
buraco de cobertura encontrado nesta auditoria em termos de volume.

### 1.5 Cruzamento com `pipeline/dados_brutos/aon_spells.json`

Achado importante de metodo antes do numero: o dump bruto tem **2.461**
registros, mas mistura versoes LEGACY e REMASTER do mesmo spell (campos
`legacy_id`/`remaster_id` fazem o vinculo -- 794 remaster com par legacy, 800
legacy com par remaster, 867 sem par). Comparar contra os 2.461 direto
infla falsos positivos de "spell ausente". Filtrando pra so o conjunto
remaster (excluindo quem tem `remaster_id`, ou seja quem foi substituido):
**1.661 candidatos**.

Cruzamento por `id` do xref (`spell['xref']['aon']`) achou 8 "ausentes":
investigando cada um, **todos os 8 existem na base por nome** (ex.:
`spell-2436 Pact Broker` no dump aponta pra um id AoN antigo; a base tem
`wb:spell/pact-broker` com `xref.aon: spell-2597`, um id MAIS NOVO que nao
esta no dump -- o AoN reindexou o spell entre a data do dump e a data da
extracao da base, provavelmente por causa de uma reimpressao/merge de fonte
(Divine Mysteries + Dark Archives Remastered)). Isso e churn de ID do lado
do AoN, nao lacuna da base.

**Cruzamento definitivo por NOME normalizado** (que sobrevive ao churn de
id): dos 1.661 candidatos remaster do AoN, **0 (zero) estao ausentes da
base por nome**. Cobertura de spell remaster e 100%, medida no nivel mais
robusto disponivel.

Sobram 2 nomes que existem na base mas nao no conjunto "remaster" do AoN:
`Restoration` e `Glyph of Warding`. Investigado: ambos estao corretamente
marcados `source.remaster: false` na base -- sao legado, mantidos de
proposito. `Restoration` foi removida no remaster (`remaster_id: ['0']`,
sentinela de "sem substituto"); `Glyph of Warding` virou **ritual** no
remaster (`remaster_id: ['ritual-124']`) -- nao e erro, e a base carregando
conteudo legacy alem do remaster.

**Resumo spell x AoN: base = 1655, AoN remaster = 1661 nomes unicos, 0
ausentes. Cobertura completa.**

---

## 2. Ritual (151 registros)

```
sem 'level'                 : 0 / 151
distribuicao por level      : {1: 9, 2: 20, 3: 23, 4: 18, 5: 26, 6: 19, 7: 10, 8: 11, 9: 9, 10: 6}
sem 'traits' (vazio)        : 62 / 151
sem 'acoes' (tempo)         : 0 / 151
sem 'alcance'               : 71 / 151
sem 'rarity'                : 0 / 151
sem campo estruturado 'ritual' : 0 / 151
```

Dentro do campo estruturado `ritual` (`{cast, cost, primary_check,
secondary_checks, secondary_casters, requirements, results}`):

```
ritual.cast              faltando: 0 / 151
ritual.primary_check     faltando: 0 / 151   <- 100%, a pericia primaria SEMPRE esta
ritual.secondary_checks  faltando: 18 / 151
ritual.secondary_casters faltando: 20 / 151
ritual.cost              faltando: 35 / 151
ritual.requirements      faltando: 147 / 151
ritual.results           faltando: 1 / 151
```

`level`, `acoes` (tempo de conjuracao) e `primary_check` (pericia primaria)
estao **100% cobertos** -- os tres campos mais criticos pra rodar um ritual
numa mesa estao completos. `requirements` faltando em 147/151 nao e defeito:
a maioria dos rituais do PF2e simplesmente nao publica uma linha
"Requirements" no stat block (e campo raro no sistema, nao obrigatorio).

`traits` vazio em 62/151 (41%) e `alcance` ausente em 71/151 (47%) sao
volumes grandes o suficiente pra merecer nota, mas nao investiguei
individualmente se sao legitimos (rituais de area sem alvo pontual, sem
trait de escola no remaster) ou lacuna -- diferente do caso de spell, aqui
nao achei um sinal claro (tipo "Range" aparecendo na prosa) que provasse
buraco de extracao real; fica como suspeita nao confirmada.

### 2.1 Cruzamento com `pipeline/dados_brutos/aon_rituals.json`

Dump bruto: 201 registros, mesma mistura legacy/remaster (`legacy_id`: 57,
`remaster_id`: 56). Filtrando pro conjunto remaster (sem `remaster_id`):
**145 candidatos**.

Por nome normalizado: **0 rituais do conjunto remaster do AoN estao
ausentes da base**. Cobertura completa, mesmo padrao do spell.

A base tem 151 registros contra 145 candidatos remaster do AoN -- a
diferenca (6) sao rituais **que nao existem no dump do AoN de jeito nenhum**
(nem versao legacy nem remaster, testado por nome exato): todos de
Adventure Path / PFS Scenario muito especificos --
`Anima Invocation (Modified)`, `Aspirational State`, `Create Mycoguardian`,
`Destroy Mindscape`, `Rite of Cleansing Flame`, `Unfettered Mark`. Nao e
defeito da base -- e conteudo de nicho que o scraper do AoN usado pra gerar
este dump nao indexou (paginas de AP muitas vezes demoram a entrar no
Nethys, ou o scraper focou nas paginas principais de Rituals). A base tem
MAIS cobertura que este dump especifico do AoN, no sentido de que carrega
conteudo que o dump nao tem.

**Resumo ritual x AoN: base = 151, AoN remaster = 145 nomes unicos, 0
ausentes; a base tem 6 a mais (conteudo de AP nao indexado no dump).**

---

## 3. Conjuracao no motor (`_conjuracao`, regras 16/17/17b/18)

### 3.1 O que esta CERTO -- medido e validado

`motor/teste_motor.py` roda hoje e **passa 100%** (rodado nesta auditoria,
sem alteracao no codigo), incluindo a varredura EXAUSTIVA dos 204 pares
(nivel de classe 1-20 x nivel de personagem 1-20) da regra 21, os testes de
`cap_invocacao`/`cap_ator` (regra 17b), e o teste da progressao de DC
dependente de subclasse do Clerigo (Cloistered vs Warpriest).

Alem da suite existente, refiz manualmente (script novo, nao alterei nada
do motor) os seguintes casos usando as fichas de exemplo:

**Slots por rank batem com a tabela oficial de nivel de CLASSE.** Conferido
direto no dado (`wb:class/*.spellcasting.slots_per_level`) contra o que a
memoria de PF2e Remaster diz:
- Wizard (prepared): nivel 1 = 2 slots rank1; nivel 2 = 3; nivel 3 = 3+2;
  nivel 4 = 3+3; nivel 5 = 3+3+2. Bate.
- Sorcerer (spontaneous): nivel 5 = cantrips 5, rank1:4, rank2:4, rank3:3,
  max_rank 3. Bate.
- Witch (prepared): nivel 5 = cantrips 5, rank1:3, rank2:3, rank3:2. Bate.
- Summoner (spontaneous): nivel 1 = 1 slot rank1; nivel 5 = SO rank2:2 +
  rank3:2 (sem rank1 -- peculiaridade real do Summoner remasterizado, a
  tabela oficial dele "rola" os ranks baixos pra fora conforme sobe, ao
  contrario de Wizard/Sorcerer que acumulam). Bate com a regra publicada.

**Cantrips por dia:** todas as classes conjuradoras testadas (Sorcerer,
Witch, Summoner, Wizard) mostraram 5 cantrips/dia, constante -- correto
(cantrips nao contam contra slot, sao "quantos truques diferentes voce
sabe/prepara por dia", 5 e o numero padrao pra conjurador de rank pleno).

**Regra 17 (rank_efetivo = ceil(nivel_de_personagem/2)) esta implementada e
verificada em dois regimes:**
- Classe unica (Feiticeiro 5 puro, Bruxa 5 pura, Invocador 5 puro): a regra
  fica **invisivel** como o design pretende -- `rank_efetivo == max_rank_cru`,
  elevacao = +0, em todos os 3 casos medidos.
- Multiclasse (Guerreiro 3 / Mago 2, personagem nivel 5): Mago tem nivel de
  CLASSE 2 (max_rank_cru=1, slots de Mago-2 reais: 3 de rank 1), mas
  `rank_efetivo = ceil(5/2) = 3`. Elevacao = +2. Confirma exatamente o
  exemplo do enunciado da tarefa ("Mago 2 num personagem de nivel 5 deve
  conjurar em rank 3").

**DC de conjuracao (10 + mod + prof + nivel) conferido a mao, script
separado, nao o motor:**
- Feiticeiro 5 puro: nivel 5 + rank trained (+2) + mod CHA (+4) = 11 ->
  **DC 21**. Bate com o output do motor.
- Guerreiro 3 / Mago 2 (nivel 5, rank de classe do Mago = 2 = trained):
  nivel 5 + rank trained (+2) + mod INT (+2, atributo 14) = 9 -> **DC 19**.
  Recalculado por fora com `p.atributos`/`p.modificadores` direto do objeto
  `Personagem`: bate exatamente (10 + 5 + 2 + 2 = 19).

A regra 3 (bonus = nivel de PERSONAGEM + rank, rank pelo nivel de CLASSE) e
a regra 5 (rank/proficiencia dependente de subclasse pro Clerigo) estao
corretas e ja cobertas por teste automatizado.

### 3.2 Defeito confirmado: tradicao do conjurador nao resolve pra 3 classes

**O problema conhecido do enunciado esta confirmado e mensurado.** Sorcerer,
Summoner e Witch tem `spellcasting.tradition` como STRING DE PROSA nao
resolvida, nao um valor de tradicao real:

```
wb:class/sorcerer.spellcasting.tradition = "variavel (definida pela escolha
  de bloodline; nao ha tradicao fixa na class-feature)"
wb:class/summoner.spellcasting.tradition = "variavel (definida pela escolha
  de eidolon; nao ha tradicao fixa na class-feature)"
wb:class/witch.spellcasting.tradition = "variavel (definida pela escolha de
  patron; nao ha tradicao fixa na class-feature)"
```

`motor.py::_conjuracao` (linha 841) faz `sc.get("tradition")` direto e poe
esse texto cru no campo `tradicao` da ficha derivada -- reproduzido nas 3
fichas de exemplo (`motor/exemplos/feiticeiro5-fa-diabolico.json`,
`motor/exemplos/bruxa5-tradicao-patron.json` [NOVA],
`motor/exemplos/invocador5-tradicao-eidolon.json` [NOVA]):

```
Sorcerer 5  --  variavel (definida pela escolha de bloodline; nao ha
                tradicao fixa na class-feature), spontaneous
Witch 5     --  variavel (definida pela escolha de patron; nao ha tradicao
                fixa na class-feature), prepared
Summoner 5  --  variavel (definida pela escolha de eidolon; nao ha
                tradicao fixa na class-feature), spontaneous
```

**Extensao medida: e um problema estrutural, nao so do motor.** Fui atras de
onde o motor DEVERIA puxar a tradicao real e nao ha de onde puxar -- **nenhum
registro das 3 fontes de subclasse tem `grants` estruturado**:

```
kind=bloodline : 18 registros, TODOS com grants: []
kind=patron    : 17 registros, TODOS com grants: []
kind=eidolon   : 13 registros, TODOS com grants: []
```

Total: **48 opcoes de subclasse, 3 classes, 0 com tradicao estruturada em
qualquer lugar da base.** A informacao existe (a prosa de cada bloodline diz
qual tradicao ela da -- ex.: Diabolic Bloodline e Divine), mas so como texto
livre em `pipeline/base/text/bloodline.json` etc., nao como campo. O motor
nao tem bug de logica aqui -- tem bug de **fallback ausente**: quando o dado
estruturado nao resolve, ele deveria cair pra alguma fonte (mapear
bloodline->tradicao a mao, ou pelo menos nao vazar a string de prosa pro
campo `tradicao` da ficha) e nao faz nenhum dos dois.

**Efeito pratico:** qualquer app que leia `conjuracao[].tradicao` pra filtrar
"quais spells esse personagem pode aprender/preparar" quebra para os 3
classes inteiros (Sorcerer, Summoner, Witch) -- nao filtra spell nenhum, ou
filtra por uma string que nao bate com nenhuma das 4 tradicoes reais em
`spell.tradicoes`. Isso NAO aparece na suite `teste_motor.py` porque nenhum
teste atual olha o campo `tradicao` de Sorcerer/Summoner/Witch -- os testes
existentes cobrem slots/DC/cap_invocacao, que sao corretos independente da
tradicao (a DC usa `key_ability`, nao tradicao). E um buraco de cobertura de
teste, nao so de dado.

**DC e slots continuam corretos apesar do bug** (confirmado nas 3 fichas:
DC calculada bate com nivel+rank+mod em todos os casos) -- o defeito e
isolado ao campo de exibicao/filtro de tradicao, nao contamina o resto da
derivacao.

### 3.3 Regra 17b (teto de invocacao) e regra 18 (arquetipo roda RAW)

Nao testei fichas novas pra isso -- a suite `motor/teste_motor.py` ja cobre
com precisao maior do que eu conseguiria a mao (varredura exaustiva de 204
pares, mais casos pontuais de Summoner 2/Guerreiro 10, Summoner 20 puro,
Mago 2/personagem 5, Ranger 2/personagem 12, Ranger 12 puro) e todos passam
nesta auditoria. Nao ha necessidade de fichas extras: a cobertura de teste
ja excede o que uma amostragem manual acrescentaria.

---

## Resumo executivo

**Cobertura (numeros medidos, nao estimados):**

| Item | Medido |
|---|---|
| Spells na base | 1.655 (tarefa citava 1.642 -- corrigido) |
| Spells com `level` | 1.655/1.655 (100%) |
| Cantrip = level 0 ou 1? | **1**, nunca 0 |
| Spells sem tradicao livre | 526/1.655; 472 sao focus (legitimo), 54 tem `tradicao_de_classe` preenchido (dado existe, so em outro campo) |
| Spells ausentes do AoN (por nome, conjunto remaster) | **0** de 1.661 |
| Rituais na base | 151 (bate com a tarefa) |
| Rituais com `level`/`acoes`/`primary_check` | 151/151 (100%) |
| Rituais ausentes do AoN (por nome, conjunto remaster) | **0** de 145 |

**Defeitos achados, com reproducao:**

1. **Tradicao de conjuracao nao resolve pra Sorcerer/Summoner/Witch** (3
   classes, 48 subclasses sem `grants` estruturado em bloodline/patron/
   eidolon). Motor vaza string de prosa pro campo `tradicao`. Reproduzir:
   `python3 motor/ficha.py motor/exemplos/feiticeiro5-fa-diabolico.json`
   (ou as 2 fichas novas) e olhar a secao CONJURACAO.
2. **17 spells "zumbi"** (`desmembrado_de`) com `rank`/`tradicoes`/etc.
   ausentes -- duplicatas de uma fusao incompleta; o registro canonico
   existe e esta completo com outro id.
3. **15 spells legacy com `acoes` ausente apesar do dado estar na prosa**
   (todos com trait de alinhamento, pre-remaster) -- buraco de extracao
   confirmado comparando `texto` com `acoes`.
4. **23 spells com `alcance` ausente apesar de "Range" aparecer na prosa** --
   mesmo padrao, escala menor.
5. **Campo `targets`/`alvos` nao existe** em spell nem ritual -- 0% de
   cobertura estrutural (nao e regressao, nunca existiu).
6. **`heightened` estruturado cobre so 31%** dos spells (513/1.655); 42%
   (694) nao tem nem o dado estruturado nem a flag `heightened_so_prosa` --
   nao da pra saber, sem investigar um a um, se sao spells sem elevacao
   (legitimo) ou lacuna.

**O que esta certo (validado, nao só assumido):**

- `level` 100% em spell; `level`/`acoes`/`primary_check` 100% em ritual.
- Cobertura de conteudo contra o AoN e **completa nos dois kinds** (0
  ausentes por nome, no conjunto remaster) -- a base nao esta perdendo
  spell nem ritual nenhum que deveria ter.
- As regras 3, 5, 16, 17, 17b, 18, 21, 23 de conjuracao no motor estao
  implementadas corretamente e passam tanto na suite automatizada quanto em
  recalculo manual feito nesta auditoria (DC, slots, rank efetivo,
  elevacao) para Wizard, Sorcerer, Witch e Summoner.
- O bug de tradicao e isolado: nao contamina DC nem slots, so o campo de
  exibicao/filtro de tradicao.

## Arquivos novos desta auditoria

- `motor/exemplos/bruxa5-tradicao-patron.json` -- ficha de validacao, Witch
  5 pura, pra medir o bug de tradicao tambem em Witch.
- `motor/exemplos/invocador5-tradicao-eidolon.json` -- ficha de validacao,
  Summoner 5 puro, mesma finalidade pra Summoner.

Nenhum arquivo `.py` foi alterado.
