# Extracao de tabelas de conjuracao dos PDFs (2026-07-26)

Objetivo: preencher o buraco confirmado -- "tabela de slots de conjuracao nao esta
mecanizada em lugar nenhum" e "Animist nao tem tabela de slots em fonte nenhuma".

Dados extraidos: `pipeline/dados_brutos/tabelas_conjuracao_pdf.json`

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
- **Player Core / Player Core 2** nao foram abertos -- fora do escopo confirmado
  (classes ja padrao, nao e o buraco reportado).

Toda pagina citada abaixo e o **numero impresso no rodape** da pagina do livro (mesma
convencao do campo `source.page` que ja existe em `index.json`), nao o indice do
arquivo PDF.

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

### Magus -- CONFERIDO, tabela completa
- Livro: Secrets of Magic, pagina 36 (advancement table) e 39 (spells per day)
- Tradicao: arcane. Tipo: prepared (spellbook, como wizard), com uma regra propria:
  no maximo 2 slots do rank mais alto disponivel + 2 do rank imediatamente abaixo
- Proficiencia: trained(1) -> expert(9) -> master(17) -- **nao chega a legendary**
- Validacao cruzada: bate 100% com `index.json`
- Irregularidade: a partir do nivel 7, um rank fica marcado com asterisco na tabela --
  e um slot que so existe pela feature *studious spells* (pagina 41, nao lida em
  detalhe). Registrei a existencia, nao inventei o mecanismo interno

### Summoner -- CONFERIDO, tabela completa
- Livro: Secrets of Magic, pagina 52 (advancement table) e 55 (spells per day)
- Tradicao: **depende do eidolon escolhido** (arcane/divine/occult/primal) -- nao e
  fixo por classe
- Tipo: spontaneous com repertorio que **encolhe** -- toda vez que sobe de rank de
  slot, perde 2 spells do repertorio do rank mais baixo que caiu
- Proficiencia: trained(1) -> expert(9) -> master(17) -- tambem nao chega a legendary
- Validacao cruzada: bate 100% com `index.json`

## O que NAO foi feito (fora do escopo desta tarefa)

`index.json` confirma que **nenhuma classe conjuradora** (nem Cleric, nem Wizard, nem
nenhuma outra) tem tabela numerica de slots mecanizada hoje -- so a progressao de
proficiencia esta la. Ou seja, o buraco e maior do que so o Animist; mecanizar Cleric,
Wizard, Druid, Bard, Sorcerer, Oracle, Psychic e Witch fica pra uma proxima rodada, se
Igor quiser -- essas classes estao no Player Core / Player Core 2, que nem abri.

## Arquivos gerados

- `pipeline/dados_brutos/tabelas_conjuracao_pdf.json` -- dados estruturados das 5 classes
- Este relatorio
