# Teste de carga e consistencia do motor -- 2026-07-28

Varredura sistematica de `motor/motor.py` (`Personagem`) contra as regras de
`specs/2026-07-26-regras-multiclasse.md`. Objetivo: achar onde o **motor**
quebra, trava ou produz numero incoerente -- nao onde falta dado. Nenhum
arquivo `.py` do projeto nem ficha de `motor/exemplos/` foi tocado.

Scripts e resultados brutos (JSON) ficam em
`/tmp/claude-1000/-mnt-c-Users-igor0/cf4835ec-3dd1-442c-ad27-6284421f280d/scratchpad/waybuilder_loadtest/`
(fora do repo, por regra do Tartarus -- sao artefato de teste descartavel,
nao produto de projeto):

- `lib.py` -- geracao de documento minimo (ancestralidade/heranca/background
  fixos, niveis de classe em blocos contiguos, subclasse do eixo primario,
  boosts livres calculados em 2 passadas)
- `task1_classe_unica.py`, `resultado_task1.json`
- `task2_multiclasse.py`, `resultado_task2.json`
- `task3_invariantes.py`, `resultado_task3.json`
- `task4_desempenho.py`, `resultado_task4.json`, `perfil_nivel20.txt`

## Resumo executivo

| | valor |
|---|---|
| fichas geradas (classe unica + multiclasse) | **285** (135 + 150) |
| fichas que quebraram (excecao) | **0** |
| violacoes de regra/invariante | **6**, todas da mesma causa raiz |
| invariantes gerais violados | **0** em 285 fichas (determinismo, shuffle, rank, atributo) |
| tempo medio de derivacao (nivel 20) | **5,76 ms** (pior caso 7,02 ms) |
| limiar de alerta (~100 ms) | nao atingido -- 14x de margem |

O motor **nao quebrou em nenhuma das 285 fichas** gerada por combinacao
sistematica (27 classes x 5 niveis + 50 combinacoes de multiclasse x 3
niveis). O unico grupo de violacoes encontrado (6 casos) tem uma causa unica
e rastreavel: a classe **Psychic** tem `key_ability: []` vazio na base --
nao e um bug de logica da regra 8, e uma lacuna de dado upstream que a regra
8 herda. Detalhe na secao 2.

O achado mais relevante para o app **client-side** nao e de correcao, e de
desempenho: `_veto_classe_de_dedicacao_ja_pega` -> `_classes_multiclasse`
percorre a base inteira (19.705 registros) em **toda** instanciacao de
`Personagem`, e hoje ja responde por ~90% do tempo de derivacao medido no
profile (ficha mais lenta). Nao cruza os 100ms hoje, mas e o unico ponto que
escala com o tamanho da base em vez de com o tamanho da ficha -- ver secao 4.

---

## 1. Varredura de classe unica (27 classes x niveis 1/5/10/15/20 = 135 fichas)

Metodo: `task1_classe_unica.py`. Cada ficha e Humano/Warrior + N niveis de
UMA classe + boosts livres exatos (calculados via `boosts_direito` numa
primeira derivacao) + a subclasse do eixo nomeado primario da classe (eixos
`outras-opcoes` foram deliberadamente deixados em aberto -- ver nota
metodologica no fim da secao). Checagens por ficha:

- deriva sem excecao -- **135/135 ok**
- HP > 0 e cresce estritamente a cada nivel testado (1<5<10<15<20) -- **ok em todas as 27 classes**
- `slots['class']`, `['ancestry']`, `['general']`, `['skill']` batem contra a
  tabela que o **proprio Foundry declara dentro de cada classe**
  (`classFeatLevels` etc., reaproveitando `simular_raw.tabelas_do_foundry()`)
  -- **0 divergencias em 135 fichas x 4 eixos**
- `aumentos_de_pericia` recalculado de forma independente (lendo
  `skill_increase.levels` de cada classe direto da base, sem chamar nenhum
  metodo do motor) e comparado por igualdade exata com
  `p.aumentos_de_pericia` -- **0 divergencias**
- `slots_abertos()` -- chamado nas 135 fichas, nunca lancou excecao, sempre
  devolveu `list`, e todo item trouxe os 4 campos minimos (`slot`, `em`,
  `kind`, `escolhe`) -- **0 problemas estruturais**
- proficiencia sempre dentro de `untrained..legendary` -- **0 divergencias**
- `fora_do_requisito` -- **0** em todas as 135 (esperado: nenhuma ficha desta
  bateria escolhe feat, entao nada ha pra reprovar)
- `avisos` -- **263 no total**, 100% explicaveis:
  - **135** (uma por ficha) -- `wb:background/warrior: grant_feat com alvo
    nao resolvido pelo pipeline (Intimidating Glare / Compendium....) --
    nao aplicado`. Sistemico porque o background e fixo em todas as fichas
    desta bateria; e um gap do PIPELINE (referencia do Foundry que a
    extracao nao resolveu), nao do motor -- o motor esta corretamente
    avisando em vez de aplicar um `grant_feat` incompleto.
  - **~123** -- `<Classe>: falta escolher 'outras-opcoes' (N opcoes)`,
    concentradas em Alchemist, Cleric, Champion, Inventor, Exemplar,
    Thaumaturge e outras 9 classes. Consequencia direta de eu ter deixado
    esses eixos sem escolha de proposito (ver nota metodologica) -- nao e
    achado sobre o motor, e o motor sinalizando corretamente uma escolha que
    a ficha de teste nao fez.
  - **5** -- `Cleric: progressao de conjuracao depende da subclasse
    (cloistered_cleric, warpriest) e nenhuma foi escolhida -- usando
    cloistered_cleric`. Efeito colateral do ponto acima: o eixo `doctrine`
    do Clerigo tem 3 opcoes (`battle-creed`, `cloistered-cleric`,
    `warpriest`) e o gerador sempre pega a primeira da lista
    (`battle-creed`), que nao e nenhuma das duas que alimentam a tabela de
    conjuracao -- o motor cai no default e AVISA, comportamento correto.

**Nota metodologica sobre `outras-opcoes`:** o pipeline bota varias
sub-escolhas de classe (feats de linhagem, opcoes de doutrina secundaria,
etc.) num eixo generico `outras-opcoes` em vez de um nome derivado. Optei
por nao escolher esses eixos no gerador (para nao arriscar `pega` invalido
por chute), e o motor respondeu exatamente como a spec manda: avisou, nao
travou, nao escondeu a lacuna. Esses avisos sao esperados desta bateria e
nao contam como defeito do motor.

### Tabela de nivel 20 -- todas as 27 classes

| Classe | HP | Slots de class feat | Aumentos de pericia | `slots_abertos()` | avisos | fora do requisito |
|---|---:|---|---|---:|---:|---:|
| Alchemist | 248 | 1,2,4,6,...,20 (11) | 3,5,7,...,19 (9) | 56 | 7 | 0 |
| Animist | 248 | 2,4,...,20 (10) | 3,5,...,19 (9) | 50 | 2 | 0 |
| Barbarian | 328 | 1,2,4,...,20 (11) | 3,5,...,19 (9) | 51 | 2 | 0 |
| Bard | 248 | 2,4,...,20 (10) | 3,5,...,19 (9) | 49 | 1 | 0 |
| Champion | 288 | 1,2,4,...,20 (11) | 3,5,...,19 (9) | 52 | 3 | 0 |
| Cleric | 248 | 2,4,...,20 (10) | 3,5,...,19 (9) | 55 | 8 | 0 |
| Commander | 248 | 1,2,4,...,20 (11) | 3,5,...,19 (9) | 50 | 1 | 0 |
| Druid | 248 | 2,4,...,20 (10) | 3,5,...,19 (9) | 50 | 2 | 0 |
| Exemplar | 288 | 1,2,4,...,20 (11) | 3,5,...,19 (9) | 53 | 4 | 0 |
| Fighter | 288 | 1,2,4,...,20 (11) | 3,5,...,19 (9) | 50 | 1 | 0 |
| Guardian | 328 | 1,2,4,...,20 (11) | 3,5,...,19 (9) | 50 | 1 | 0 |
| Gunslinger | 248 | 1,2,4,...,20 (11) | 3,5,...,19 (9) | 50 | 1 | 0 |
| Inventor | 248 | 1,2,4,...,20 (11) | 3,5,...,19 (9) | 53 | 4 | 0 |
| Investigator | 248 | 1,2,4,...,20 (11) | **2,3,4,...,20 (19)** | 70 | 2 | 0 |
| Kineticist | 268 | 1,2,4,...,20 (11) | 3,5,...,19 (9) | 50 | 1 | 0 |
| Magus | 248 | 2,4,...,20 (10) | 3,5,...,19 (9) | 49 | 1 | 0 |
| Monk | 288 | 1,2,4,...,20 (11) | 3,5,...,19 (9) | 50 | 1 | 0 |
| Oracle | 248 | 2,4,...,20 (10) | 3,5,...,19 (9) | 50 | 2 | 0 |
| Psychic | 208 | 2,4,...,20 (10) | 3,5,...,19 (9) | 49 | 1 | 0 |
| Ranger | 288 | 1,2,4,...,20 (11) | 3,5,...,19 (9) | 52 | 3 | 0 |
| Rogue | 248 | 1,2,4,...,20 (11) | **2,3,4,...,20 (19)** | 70 | 1 | 0 |
| Sorcerer | 208 | 2,4,...,20 (10) | 3,5,...,19 (9) | 50 | 2 | 0 |
| Summoner | 288 | 2,4,...,20 (10) | 3,5,...,19 (9) | 50 | 2 | 0 |
| Swashbuckler | 288 | 1,2,4,...,20 (11) | 3,5,...,19 (9) | 53 | 1 | 0 |
| Thaumaturge | 248 | 1,2,4,...,20 (11) | 3,5,...,19 (9) | 53 | 4 | 0 |
| Witch | 208 | 2,4,...,20 (10) | 3,5,...,19 (9) | 50 | 2 | 0 |
| Wizard | 208 | 2,4,...,20 (10) | 3,5,...,19 (9) | 50 | 2 | 0 |

As 16 classes que a spec lista como concedentes de class feat no nivel 1
(regra 8) -- Alchemist, Barbarian, Champion, Commander, Exemplar, Fighter,
Guardian, Gunslinger, Inventor, Investigator, Kineticist, Monk, Ranger,
Rogue, Swashbuckler, Thaumaturge -- batem **exatamente** com as 16 que
aparecem com 11 entradas em vez de 10 na coluna de slots (o `1` extra).
Rogue e Investigator sao os unicos com aumento de pericia todo nivel (regra
15), confirmando a cadencia derivada de dado que a spec exige.

**Confirma tambem a ressalva que a propria spec ja registrava:** Summoner
sai com 10 (sem o `1`) porque o feat de nivel 1 dele se chama "evolution
feat" no dado, nao `feat_slot.kind == "class"` no padrao `"<classe> feat"` --
exatamente o caso que a spec cita como motivo de "sao ao menos 17" em vez
de 16. Isto **nao e um achado novo**: e a spec confirmando, na pratica,
uma lacuna que ela mesma ja documentou de proposito. Fica registrado aqui
porque a varredura sistematica e o jeito de ver o efeito concreto (Summoner
nunca ganha o slot de classe no nivel 1 nesta implementacao) em vez de so
na intencao escrita.

---

## 2. Varredura de multiclasse (50 combinacoes x niveis 5/10/20 = 150 fichas)

Metodo: `task2_multiclasse.py`. 50 pares de classe (3 obrigatorios --
Monge/Clerigo, Barbaro/Mago, Alquimista/Bardo -- + 47 amostrados com semente
fixa `20260728` do universo de 351 pares possiveis, cobrindo pares
improvaveis como Psychic/Thaumaturge, Guardian/Witch, Commander/Summoner
etc.). Split de nivel: primeira classe recebe `ceil(nivel/2)` niveis
contiguos (1..n1), segunda recebe o resto (n1+1..nivel) -- ela e sempre a
"primeira classe" da regra 8 porque recebeu o nivel 1.

- deriva sem excecao -- **150/150 ok**
- **regra 1** (nivel de personagem = soma dos niveis de classe) -- **0
  violacoes** em 150 fichas
- **regra 8** (boost de chave so da primeira classe) -- **6 violacoes**,
  todas no mesmo padrao: ver abaixo
- **regra 10** (orcamento de pericia livre nao multiplica) -- recalculado
  de forma independente com a mesma formula delta-max da spec (lendo
  `skill_training.free` de cada classe direto da base) e comparado por
  igualdade exata -- **0 violacoes** em 150 fichas; nenhum caso onde o total
  bateu com `livre1 + livre2` sem que um dos dois fosse zero
- **regra 12** (class feat em nivel PAR de personagem) -- `slots['class']`
  recalculado independentemente (pares de 2 a `nivel`, mais o 1 se a
  primeira classe concede feat no proprio nivel 1) e comparado por
  igualdade de conjunto -- **0 violacoes**
- **regra 21** (rota de nivel >= dedicacao, eixo invocacao) -- para toda
  classe conjuradora presente em cada combinacao, `p.cap_invocacao(nivel_de_
  classe) >= p.rank_de_dedicacao()` -- **0 violacoes** em todos os pares com
  conjurador
- **regra 11** (HP por nivel-dono) -- HP recalculado de forma independente
  somando, para CADA nivel de personagem, o `hp_per_level` da classe que
  literalmente recebeu aquele nivel (`p.classe_do_nivel`) + modificador de
  CON, e comparado por igualdade EXATA (sem feats de HP nesta bateria, a
  igualdade tem que ser exata, nao so "nao menor que") -- **0 violacoes**
  em 150 fichas

### O unico achado: Psychic tem `key_ability` vazio na base

As 6 violacoes de regra 8 sao 100% fichas com **Psychic como primeira
classe** (Psychic/Thaumaturge nos 3 niveis, Psychic/Sorcerer nos 3 niveis).
Causa raiz, confirmada por leitura direta da base:

```
wb:class/psychic -> key_ability: []
wb:class-feature/the-distant-grasp (Conscious Mind, primeira opcao do eixo)
  -> key_ability: None, boosts: None
```

`_atributos()` (motor.py:552-564) so aplica boost de chave quando
`chaves = classe.get("key_ability")` tem 1 ou mais elementos:

```python
if len(chaves) == 1:
    self.boosts[chaves[0]] += 1
    ...
elif chaves:
    ...  # boost pendente, jogador escolhe
```

Com `chaves == []`, nenhum dos dois ramos executa e nenhuma linha
`"(1a classe)"` aparece em `origem_boost` -- e por isso o teste acusou
"falta boost da primeira classe". **Isto e correto dado o dado que a classe
carrega**; a regra 8 em si (so a primeira classe da o boost) nao foi violada
-- o motor simplesmente nao tem de onde tirar QUAL atributo, porque no PF2e
oficial a chave do Psychic e Intelligence OU Charisma, decidida pela
subclasse "Conscious Mind" escolhida no nivel 1, e essa informacao nao esta
na base nem na classe nem na feature de subclasse (`key_ability: None` nos
dois `wb:class-feature/the-*` verificados).

**Classificacao:** achado de PIPELINE/DADO, nao de logica do motor -- listado
aqui porque so apareceu rodando o motor de ponta a ponta com Psychic como
primeira classe, e o efeito pratico e real: qualquer personagem com Psychic
entrando primeiro nunca recebe boost de habilidade-chave. Psychic e a UNICA
das 27 classes com `key_ability` vazio (as outras 26 tem 1 ou 2 entradas).
Nao mexi na base nem no motor -- reporte, nao correcao.

### Verificacao extra: simetria da regra 8 nos 3 pares obrigatorios

Rodado a parte (nao no lote de 150, adicional): cada par nas duas ordens,
nivel de personagem 10.

| Par | Ordem | Quem recebe o boost de chave | Quem fica sem |
|---|---|---|---|
| Monk/Cleric | normal | Monk | Cleric |
| Cleric/Monk | invertida | Cleric | Monk |
| Barbarian/Wizard | normal | Barbarian | Wizard |
| Wizard/Barbarian | invertida | Wizard | Barbarian |
| Alchemist/Bard | normal | Alchemist | Bard |
| Bard/Alchemist | invertida | Bard | Alchemist |

Simetria perfeita nos 6 casos -- a regra 8 segue corretamente **quem recebeu
o nivel 1**, nao a ordem no array `escolhas` nem a ordem alfabetica.

---

## 3. Invariantes gerais (sobre as 285 fichas das secoes 1 e 2)

Metodo: `task3_invariantes.py`.

| Invariante | Fichas checadas | Violacoes |
|---|---:|---:|
| Determinismo (mesma ficha derivada 2x, `visao()` identica) | 285 | **0** |
| Embaralhar `escolhas` nao muda nenhum numero (`nivel`, `hp`, `atributos`, `modificadores`, `proficiencias`, `pericias_livres`, `boosts`, `slots`, `ac`) | 285 | **0** |
| Proficiencia sempre em `untrained..legendary` | 285 (todas as chaves de `proficiencias`) | **0** |
| Nenhum atributo negativo | 285 | **0** |
| Nenhum atributo > 24 no nivel 20 (77 fichas de nivel 20) | 77 | **0** |

O achado de `_niveis_de_classe` documentado no proprio `motor.py` (regra 8
dependia de ORDEM do array antes de ordenar por `em`) segue corrigido: o
teste de shuffle rodou em cima de TODAS as 150 fichas multiclasse, incluindo
os pares onde a regra 8 e observavel, e nao achou nenhuma regressao.

---

## 4. Desempenho

Metodo: `task4_desempenho.py`. Duas baterias:

- **77 fichas de nivel de personagem 20** (27 classe-unica + 50 multiclasse
  10/10), cada uma derivada 5x, usando o **minimo** das 5 amostras por ficha
  (a minima e o custo real de CPU; amostras maiores sao ruido de scheduler
  do SO, nao do motor)
- **corpus geral**, as 285 fichas das secoes 1-2, 1 amostra cada

| | media | mediana | p95 | pior caso | ficha do pior caso |
|---|---:|---:|---:|---:|---|
| Nivel 20 (77 fichas) | 5,76 ms | 5,63 ms | 6,86 ms | **7,02 ms** | Sorcerer10/Summoner10 |
| Corpus geral (285 fichas) | 5,90 ms | 5,90 ms | -- | 7,36 ms | Sorcerer3/Summoner2 |

**Limiar de alerta era ~100 ms -- nenhuma ficha chegou nem a 10% disso.**
Ainda assim, perfilei a ficha mais lenta (`Sorcerer10/Summoner10`, 20
repeticoes via `cProfile`) porque o comportamento encontrado importa para a
arquitetura, mesmo sem violar o limiar:

```
893.500 chamadas de funcao em 0.354s (20 instanciacoes de Personagem)

ncalls  cumtime  filename:lineno(function)
    20    0.354   motor.py:127 Personagem.__init__
    20    0.335   motor.py:1777 _checar_requisitos
    20    0.334   motor.py:1893 _veto_classe_de_dedicacao_ja_pega
    20    0.333   motor.py:1722 _classes_multiclasse   <- 94% do tempo total
818100    0.151   {method 'get' of 'dict' objects}
  6500    0.018   motor.py:72 norm_slug (via re.sub)
    20    0.005   motor.py:299 _proficiencias
    20    0.003   motor.py:630 _hp
```

`_classes_multiclasse()` (motor.py:1722) constroi o mapa "nome normalizado
-> id de classe" dos 27 arquetipos de multiclasse varrendo **os 19.705
registros da base inteira DUAS VEZES** (uma para montar o dict de classes,
outra para casar arquetipos) toda vez que um `Personagem` e instanciado. Ha
cache (`self._mc_cache`), mas e cache de **instancia** -- morre com a ficha
e e reconstruido do zero na proxima. Isso concentra ~90% do tempo de
derivacao numa unica operacao que **nao depende de nada da ficha**, so da
`Base` (que ja e carregada uma vez e reusada). Hoje isso custa poucos
milissegundos porque a base tem 19.705 registros; e o unico ponto medido
neste teste cujo custo escala com o TAMANHO DA BASE em vez do tamanho da
ficha -- vale relatar mesmo sem estourar o limiar, porque e exatamente o
tipo de coisa que so aparece numa varredura de carga, nao num teste unitario
de uma ficha so.

Nao mexi no codigo (fora do escopo desta tarefa). Se algum dia a base
crescer ou o app começar a instanciar `Personagem` em lote (ex.: liste
de NPCs), mover `_mc_cache` para o objeto `Base` (calculado uma vez,
compartilhado por todo `Personagem` que usa aquela `Base`) elimina o
gargalo por completo -- e a mesma tecnica que `Base.dedicacao_do_arquetipo`
ja usa (cache em `self._dedicacao_de`, na `Base`, nao na `Personagem`).

---

## Metodologia -- o que NAO foi testado

- Fichas com feats escolhidos (class_feat, skill_feat etc.) ficaram fora do
  gerador de carga -- escolher um feat legal por slot exigiria simular o
  picker do app inteiro. Isso significa que `fora_do_requisito`,
  `_veto_dedicacao_da_propria_classe` fora do caminho de `disponiveis()`, e
  a cadeia de `grants` de feats especificos nao foram exercitados por
  volume aqui (ja tem cobertura dedicada em `motor/teste_motor.py` e
  `motor/testes/`).
- Eixos `outras-opcoes` de subclasse foram deixados sem escolha de
  proposito (ver nota na secao 1) -- geram aviso esperado, nao bug.
- `disponiveis()` / `candidatos()` (a "pergunta central do construtor") nao
  entraram no lote de carga -- cada chamada percorre potencialmente os 6.273
  feats da base e mereceria bateria propria de desempenho, fora do escopo
  pedido aqui (deriva de ficha).

## Conclusao

O motor aguentou 285 fichas de combinacao sistematica (27 classes solo em 5
niveis + 50 pares de multiclasse em 3 niveis, incluindo os pares
improvaveis pedidos) sem uma unica excecao, sem violar nenhuma das 5 regras
de multiclasse checadas independentemente (1, 8, 10, 11, 12, 21), e sem
quebrar nenhum dos 4 invariantes gerais (determinismo, ordem, rank, range de
atributo) em nenhuma das 285 fichas. O unico grupo de numeros incoerentes
(6 casos de regra 8 nao aplicada) tem uma causa de dado especifica e
verificada (Psychic sem `key_ability` na base), nao uma falha de logica.
Desempenho esta 14x abaixo do limiar de alerta, com uma unica operacao
(`_classes_multiclasse`, sem cache em `Base`) respondendo por ~90% do custo
medido -- reportado como risco de escala, nao como defeito atual.
