# Extracao de tabelas de conjuracao dos PDFs (2026-07-26, atualizado 2026-07-27)

Objetivo: preencher o buraco confirmado -- "tabela de slots de conjuracao nao esta
mecanizada em lugar nenhum" e "Animist nao tem tabela de slots em fonte nenhuma".

Dados extraidos: `pipeline/dados_brutos/tabelas_conjuracao_pdf.json`

**2026-07-27**: recuperadas as 8 classes que faltavam (item 14 do TODO.md) -- Bard,
Cleric, Druid, Oracle, Psychic, Sorcerer, Witch, Wizard. Cobertura de tabela de slots
agora e 11/11 classes conjuradoras (Animist continua parcial, ver secao dedicada).

## Metodo

- **War of Immortals.pdf** (235 MB) e um PDF **imagem-only** -- `pdftotext` e `pdffonts`
  confirmam que nao ha camada de texto nenhuma (nem na capa, nem no meio, nem no fim).
  Instalei `tesseract-ocr` via apt, mas acabei nao precisando: rendericei as paginas
  relevantes com `pdftoppm -r 100 -png` e li as tabelas direto da imagem (mais confiavel
  que OCR pra tabela numerica densa).
- **Secrets of Magic** (pdfcoffee) tem camada de texto real -- usei `pdftotext -layout`
  no arquivo inteiro e depois `grep`/`sed` pra achar as tabelas certas.
- **Rage of Elements** (pdfcoffee) tambem tem texto real -- confirmei rapido que
  Kineticist nao e conjurador (nao tem "Spellcasting" nas Initial Proficiencies) e
  parei ali, sem gastar tempo com paginas que nao existem.
- **Player Core.pdf** (21 MB) e **Player Core 2.pdf** (31 MB): `pdffonts` confirma
  camada de texto real (fontes embutidas TrueType/Type1C) -- nao sao scan, apesar do
  aviso da LESSONS.md de que "PDF de regra acima de ~100 MB quase sempre e imagem" (esses
  dois sao pequenos o bastante pra escapar da regra). Usei `pdftotext -layout` no arquivo
  inteiro, sem precisar renderizar imagem nem OCR.
- **Dark Archive** (pdfcoffee, 15 MB): tambem tem texto real. Unica fonte oficial pro
  **Psychic** -- essa classe nunca foi reeditada em Player Core ou Player Core 2 (nem o
  pf2etools nem o Foundry tem variante remaster dela).
- Verifiquei o Table of Contents de cada PDF antes de procurar as tabelas -- **Witch
  esta no Player Core (PC1)**, nao no Player Core 2 como eu teria assumido de memoria
  (confirmado lendo o TOC diretamente, nao chutado). Player Core 2 tem Oracle e
  Sorcerer entre as classes conjuradoras que faltavam.

Toda pagina citada abaixo e o **numero impresso no rodape** da pagina do livro (mesma
convencao do campo `source.page` que ja existe em `index.json`), nao o indice do
arquivo PDF. Descobri o numero real cruzando `pdftotext -f <N> -l <N>` pagina a pagina
com o rodape impresso -- o footer de uma pagina aparece no texto extraido *dessa mesma*
pagina, o que exige cuidado (o footer da pagina anterior pode aparecer colado antes do
titulo da tabela, gerando off-by-one se nao checar com `-f/-l`).

## Resultado por classe

### Animist -- CONFERIDO, tabela completa
- Livro: War of Immortals, pagina 12 (advancement table) e 13 (spells per day)
- Tradicao: divine. Tipo: **hibrido** -- dois pools de slot independentes que nao se
  misturam: *animist spellcasting* (prepared, lista divine comum) + *apparition
  spellcasting* (spontaneous, repertorio das apparitions atuned no dia)
- Proficiencia: trained(1) -> expert(7) -> master(15) -> legendary(19), progressao
  unica, **nao varia por apparition escolhida**
- Validacao cruzada: a progressao de proficiencia batida contra `index.json` (campo
  `progressao`) bate 100% com o que a tabela do PDF mostra
- Irregularidade: nivel 19-20 ganham um slot de apparition rank 10 ("0+1*") que vem da
  feature *supreme incarnation* e funciona diferente dos slots normais (nao explorei o
  detalhe, so registrei que existe)

### Bard -- CONFERIDO, tabela completa
- Livro: Player Core, pagina 96 (advancement table) e 97 (spells per day)
- Tradicao: occult. Tipo: spontaneous (spell repertoire), mas a **contagem** de slots
  segue o padrao identico ao dos conjuradores prepared -- 2 slots no rank de entrada,
  3 no seguinte. Bard NAO tem o slot bonus que Oracle/Sorcerer tem
- Proficiencia: trained(1) -> expert(7) -> master(15) -> legendary(19), padrao pleno.
  Confirmado no texto da advancement table (linhas "expert spellcaster"/"master
  spellcaster"/"legendary spellcaster" nos niveis certos) e em Foundry
  (`occult-spellcasting.json`)
- Cross-check: pf2etools (`class-bard-pc1.json`, tabela "Bard Spells per Day") --
  match exato nos 20 niveis, todos os ranks, incluindo cantrips (fixo em 5) e o slot
  especial de rank 10 (niveis 19-20, feature *magnum opus*)

### Cleric -- CONFERIDO, tabela completa
- Livro: Player Core, pagina 110 (advancement table) e 111 (spells per day)
- Tradicao: divine. Tipo: prepared. Padrao pleno identico ao Bard (2 slots no rank de
  entrada, 3 no seguinte)
- A tabela impressa marca com `*` o rank mais alto disponivel em cada nivel -- e so
  informativo de onde o Divine Font se aplica ("The number is 4 at 1st level, 5 at
  5th level, and 6 at 15th level"), nao um numero diferente do que ja esta na celula.
  Os slots extras do Divine Font em si ja estao capturados a parte
  (`extract_divine_font()` em `conjuracao.py`, ja validado em rodada anterior) --
  nao duplicados aqui
- A advancement table (pagina 110) **nao lista** milestones de spellcaster (expert/
  master/legendary) porque a proficiencia do Clerico depende da Doutrina (Cloistered
  vs Warpriest), tratada nas 12 features de doutrina, nao na advancement table
  generica -- confirma o que ja estava documentado no TODO item 73 e em
  `conjuracao.py` (`extract_cleric_doctrine_proficiency`). Fora do escopo desta tarefa
  (item 14 e so sobre slots)
- Cross-check: pf2etools (`class-cleric-pc1.json`, tabela "Cleric Spells per Day") --
  match exato nos 20 niveis, incluindo o rodape do Divine Font (4/5/6) e o slot
  especial de rank 10 (feature *miraculous spell*)

### Druid -- CONFERIDO, tabela completa
- Livro: Player Core, pagina 124 (advancement table) e 125 (spells per day)
- Tradicao: primal. Tipo: prepared. Padrao pleno identico ao Bard/Cleric
- Proficiencia: trained(1) -> expert(7) -> master(15) -> legendary(19), confirmado na
  advancement table e em Foundry (`druid-spellcasting.json`)
- Cross-check: pf2etools (`class-druid-pc1.json`) -- match exato nos 20 niveis. Slot
  especial de rank 10 vem da feature *primal hierophant*

### Exemplar -- CONFERIDO, nao e conjuradora
- Livro: War of Immortals, pagina 29-30
- Initial Proficiencies e Advancement table nao citam spellcasting, spell attack ou
  spell DC em nenhum nivel. Mecanica e "divine spark" canalizado em ikons (immanence
  passivo + transcendence ativo), sem spell slots
- Sem tabela de slots porque nao existe -- nao ha o que preencher aqui

### Kineticist -- CONFERIDO, nao e conjuradora
- Livro: Rage of Elements, pagina 13
- Usa "kinetic gate" + impulses (acao com trait `impulse`), nao lanca spells, nao tem
  spell slots
- Mesma conclusao: nao ha tabela de slots porque a classe nao usa esse sistema

### Oracle -- CONFERIDO, tabela completa (com divergencia legado x remaster resolvida)
- Livro: Player Core 2, pagina 130 (advancement table) e 131 (spells per day)
- Tradicao: divine (fixa, nao depende de mystery). Tipo: spontaneous (spell repertoire)
- **Irregularidade real**: Oracle ganha 1 slot A MAIS que o padrao pleno em cada rank
  -- 3 slots no rank de entrada (nao 2) e 4 no rank seguinte (nao 3), igual ao
  Sorcerer
- **Divergencia encontrada e resolvida**: a primeira tentativa de cross-check via
  pf2etools (`class-oracle.json`) apontou o padrao generico (2/3) -- esse arquivo e a
  versao **LEGADO/pre-remaster** (sem variante `-pc1` disponivel na fonte) e reflete a
  regra ANTIGA, sem o slot bonus. So foi pego comparando literalmente PDF vs pf2etools
  linha a linha; nao e erro de leitura, e mudanca real de regra entre a edicao antiga
  (Advanced Player's Guide) e o remaster (Player Core 2). Resolvido cruzando com
  Foundry (`oracle-spellcasting.json`, texto literal: "Each day, you can cast up to
  three 1st-rank spells"), que reflete a regra remaster vigente e bate 100% com o PDF
- Proficiencia: trained(1) -> expert(7) -> master(15) -> legendary(19), confirmado na
  advancement table e em Foundry
- Cross-check final: Foundry (fonte b), nao pf2etools -- unica das 8 classes onde as
  duas fontes auxiliares divergem entre si

### Psychic -- CONFERIDO, tabela completa (fonte legado, classe nunca remasterizada)
- Livro: Dark Archive, pagina 11 (advancement table e spells per day, ambas na mesma
  pagina fisica)
- Tradicao: occult. Tipo: spontaneous (spell repertoire)
- Classe **nunca foi reimpressa** em Player Core ou Player Core 2 -- unica fonte
  oficial continua sendo o Dark Archive (2022, pre-remaster, tabela usa "level" em vez
  de "rank")
- Padrao proprio, mais fraco que as outras 10 classes: 1 slot no rank de entrada (nao
  2), sobe pra 2 no nivel seguinte (nao 3), **nunca chega a 3 slots** em rank nenhum.
  Cantrips base e 3, nao 5 -- rodape da tabela diz "Your conscious mind gives you
  three additional cantrips with amps", ou seja sao 3 cantrips normais + 3 psi
  cantrips especiais via feature de conscious mind, nao 6 cantrips normais.
  Compensado por outras features da classe (amps, thought echoes), fora do escopo de
  slots
- Confirmado em Foundry (`psychic-spellcasting.json`, texto literal: "Each day, you
  can cast one 1st-rank spell")
- Cross-check: pf2etools (`class-psychic.json`) bate 100%, mas e um cross-check **mais
  fraco** que os outros -- e a MESMA fonte fisica (Dark Archive) materializada por
  outro pipeline, nao uma fonte independente do livro. Foundry (confirmado acima) e o
  cross-check independente real aqui

### Magus -- CONFERIDO, tabela completa
- Livro: Secrets of Magic, pagina 36 (advancement table) e 39 (spells per day)
- Tradicao: arcane. Tipo: prepared (spellbook, como wizard), com uma regra propria:
  no maximo 2 slots do rank mais alto disponivel + 2 do rank imediatamente abaixo
- Proficiencia: trained(1) -> expert(9) -> master(17) -- **nao chega a legendary**
- Validacao cruzada: bate 100% com `index.json`
- Irregularidade: a partir do nivel 7, um rank fica marcado com asterisco na tabela --
  e um slot que so existe pela feature *studious spells* (pagina 41, nao lida em
  detalhe). Registrei a existencia, nao inventei o mecanismo interno

### Sorcerer -- CONFERIDO, tabela completa
- Livro: Player Core 2, pagina 146 (advancement table) e 147 (spells per day)
- Tradicao: variavel (definida pela escolha de bloodline; a class-feature nao fixa
  uma tradicao -- mesma mecanica do Witch/patron e Summoner/eidolon)
- Mesmo padrao bonus do Oracle: 3 slots no rank de entrada, 4 no seguinte. Ao
  contrario do Oracle, o Sorcerer **ja tinha** esse bonus antes do remaster -- o
  pf2etools legado (`class-sorcerer.json`) ja mostra 3/4, confirmado tambem em
  Foundry (`sorcerer-spellcasting.json`: "Each day, you can cast up to three 1st-rank
  spells")
- Proficiencia: trained(1) -> expert(7) -> master(15) -> legendary(19)
- Cross-check: pf2etools (`class-sorcerer.json`) + Foundry, ambos batem 100% com o
  PDF -- ao contrario do Oracle, aqui NAO houve divergencia entre legado e remaster

### Witch -- CONFERIDO, tabela completa
- Livro: Player Core, pagina 180 (advancement table) e 181 (spells per day)
- Tradicao: variavel (definida pela escolha de patron; mesma mecanica do
  Sorcerer/bloodline). Tipo: prepared
- Padrao pleno normal (2/3), nao ganha o bonus que Oracle/Sorcerer tem
- Proficiencia: trained(1) -> expert(7) -> master(15) -> legendary(19), confirmado em
  Foundry (`witch-spellcasting.json`: "you can prepare up to two 1st-rank spells")
- Cross-check: pf2etools (`class-witch-pc1.json`) -- match exato. Slot especial de
  rank 10 vem da feature *patron's gift*

### Wizard -- CONFERIDO, tabela completa
- Livro: Player Core, pagina 194 (advancement table) e 195 (spells per day)
- Tradicao: arcane. Tipo: prepared (spellbook). Padrao pleno normal (2/3)
- Proficiencia: trained(1) -> expert(7) -> master(15) -> legendary(19), confirmado em
  Foundry (`wizard-spellcasting.json`: "you can prepare up to two 1st-rank spells")
- Cross-check: pf2etools (`class-wizard-pc1.json`) -- match exato. Slot especial de
  rank 10 vem da feature *archwizard's spellcraft*

### Summoner -- CONFERIDO, tabela completa
- Livro: Secrets of Magic, pagina 52 (advancement table) e 55 (spells per day)
- Tradicao: **depende do eidolon escolhido** (arcane/divine/occult/primal) -- nao e
  fixo por classe
- Tipo: spontaneous com repertorio que **encolhe** -- toda vez que sobe de rank de
  slot, perde 2 spells do repertorio do rank mais baixo que caiu
- Proficiencia: trained(1) -> expert(9) -> master(17) -- tambem nao chega a legendary
- Validacao cruzada: bate 100% com `index.json`

## Status final (2026-07-27): item 14 do TODO.md fechado

As 8 classes que faltavam (Bard, Cleric, Druid, Oracle, Psychic, Sorcerer, Witch,
Wizard) foram recuperadas do PDF oficial (Player Core, Player Core 2, Dark Archive) e
cross-checadas. Cobertura de tabela de slots agora e **11/11 classes conjuradoras**:
- 10 com tabela numerica completa (niveis 1-20, todos os ranks): Bard, Cleric, Druid,
  Kineticist e Exemplar N/A (nao conjuradoras), Magus, Oracle, Psychic, Sorcerer,
  Summoner, Witch, Wizard
- 1 parcial: Animist (so niveis 1-2 confirmados, ver secao dedicada -- tabela completa
  nao existe estruturada em nenhuma das fontes fixadas do projeto)

Nada ficou pra tras nas 8 classes desta rodada -- todas com numero confirmado em pelo
menos 2 fontes independentes (PDF + pf2etools ou PDF + Foundry). A unica divergencia
encontrada (Oracle: pf2etools legado x PDF remaster) foi investigada e resolvida, nao
descartada -- ver secao "Oracle" acima.

**Nao integrado ainda**: `tabelas_conjuracao_pdf.json` continua sendo um arquivo
auxiliar, separado de `index.json` e de `saida/conjuracao.json` (que ja extrai as
mesmas 10 tabelas completas direto do pf2etools em tempo de execucao, via
`conjuracao.py`, rodado em 2026-07-26). A reconciliacao final entre as 3 fontes --
qual vira o dado canonico do `index.json`, com que precedencia -- fica pra uma
proxima etapa do build, fora do escopo desta tarefa.

## Arquivos gerados

- `pipeline/dados_brutos/tabelas_conjuracao_pdf.json` -- dados estruturados das 13
  classes (11 conjuradoras + Exemplar e Kineticist confirmadas nao-conjuradoras)
- Este relatorio
