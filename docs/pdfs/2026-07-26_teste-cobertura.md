# Teste adversarial de cobertura -- PDFs oficiais vs. base Waybuilder

Data: 2026-07-26

## Afirmacao testada

"Os PDFs oficiais nao adicionam cobertura de regra -- a base ja cobre todos os 11 livros de regra que temos em PDF, e mais." Evidencia original: contagem de registros por `source.book`, sem checar completude interna de cada livro.

## Metodo

Amostragem dirigida via subagentes (Sonnet), um por livro, cada um usando listas/tabelas de indice do proprio PDF como gabarito (indice remissivo, tabelas de feats por nivel/nome, listas de magias por tradicao, tabelas de heranca), extraindo nomes e cruzando contra `name`/`aliases` dos registros do livro em `pipeline/base/index.json` e, quando ausente, contra um lookup global (nome -> lista de registros com esse nome ou alias, cobrindo os 18.176 registros da base inteira) para descartar falso positivo por reatribuicao de `source.book` ou remaster.

Livros cobertos:

| Livro | Paginas PDF | Camada de texto | Nomes cruzados | Resultado |
|---|---|---|---|---|
| Player Core | 466 | sim | 691 | medido |
| Player Core 2 | 322 | sim | 322 | medido |
| War of Immortals | 226 | **nao** (PDF escaneado, so imagem) | 186 | medido via render + leitura visual |
| Lost Omens: Ancestry Guide | 146 | sim | 178 | medido |
| Treasure Vault | 226 | **nao** (PDF escaneado, so imagem) | -- | **abandonado** |

**Total: 1.377 nomes cruzados em 4 livros.**

Treasure Vault foi abandonado a meio caminho: o PDF nao tem camada de texto extraivel (confirmado com `pdftotext`/`pdffonts` vazios, 229MB so de imagem), OCR pagina a pagina ficou caro demais e a maquina entrou em contencao de CPU (load average 26 em 6 nucleos) com outro OCR (War of Immortals) rodando em paralelo. Nao ha medicao de cobertura para Treasure Vault neste teste -- nem a favor, nem contra a afirmacao original.

Bestiario, NPC, perigo, veiculo e conteudo de aventura foram excluidos do escopo em todos os livros, por estarem fora do escopo do projeto Waybuilder de proposito.

## Achados (ausencias reais confirmadas)

### Gap sistemico: categoria "ritual" inteira ausente da base

A base **nao tem nenhum registro com `kind: "ritual"`** em nenhum dos 18.176 registros (confirmado por leitura direta do schema, nao so por livro). Rituals sao um tipo de conteudo mecanico proprio de PF2e remaster (distinto de spell), com sua propria tabela "Rituals by Rank" em cada livro de regra.

| Livro | Rituals confirmados no PDF e ausentes da base |
|---|---|
| Player Core | 18 de 19 (Animate Object, Atone, Awaken Animal, Blight, Binding Circle, Call Spirit, Collective Memories, Consecrate, Commune, Control Weather, Create Undead, Planar Displacement, Geas, Plant Growth, Planar Servitor, Primal Call, Resurrect, Rune Trap) -- o 19o, Wish, existe na base mas com `kind: "spell"` em vez de `kind: "ritual"` |
| Player Core 2 | 13 de 13 (Heartbond, Inveigle, Phantasmal Custodians, Reincarnate, Rest Eternal, Shadow Double, Astral Projection, Fortifying Brew, Ward Domain, Gathering Call, Teleportation Circle, Clone, Fantastic Facade) |

**31 nomes de rituals confirmados ausentes**, causa raiz unica: o pipeline de fusao (Foundry/pf2etools/AoN) aparentemente nunca ingeriu o tipo de documento "ritual" como categoria propria.

### Achados pontuais (fora do gap sistemico)

| Nome | Livro | Tipo | Pagina PDF | Motivo verificado da ausencia |
|---|---|---|---|---|
| Life-Saving Yowl | Player Core 2 | feat de ancestria (Catfolk, nivel 17, reaction) | p. 12 (impressa 11) | Nao existe na base sob nenhum `kind`, nem no lookup global. Nome provavelmente perdido em parsing de coluna de algum pipeline anterior -- confirmado ausente por checagem direta no `index.json`. |
| Cavern Kobold | Lost Omens: Ancestry Guide | heritage (Legacy) | p. 37 | A base tem "Cavernstalker Kobold" (Player Core 2, remaster) mas sem alias apontando para "Cavern Kobold". Nome legacy nao existe em lugar nenhum da base. Confirmado por checagem direta: `aliases` de "Cavernstalker Kobold" e `null`. |
| Spellscale Kobold | Lost Omens: Ancestry Guide | heritage (Legacy) | p. 37 | Mesmo padrao: "Spellhorn Kobold" (Player Core 2) existe sem alias para o nome legacy "Spellscale Kobold". Confirmado por checagem direta: `aliases` e `null`. |

**3 achados pontuais confirmados**, mais **31 rituals (1 causa raiz sistemica)** = **34 nomes individuais confirmadamente ausentes da base**, em 1.377 nomes checados.

## Falsos positivos descartados

Os subagentes levantaram dezenas de "ausencias" aparentes que, apos checagem de aliases/lookup global, se mostraram presentes. Os padroes mais relevantes:

- **Feats/features compartilhados entre classes**: a base modela um feat concedido a multiplas classes como UM registro so, com todas as classes em `traits`/`class` (design correto). Caso mais relevante: o agente do War of Immortals reportou "Reactive Strike (variante Exemplar)" como ausente da base. **Verificado e descartado por mim diretamente no `index.json`**: existe `wb:feat/reactive-strike` (Player Core 2, nivel 6) com `traits` incluindo `barbarian, champion, commander, exemplar, guardian, magus, swashbuckler` -- exatamente o padrao de feature compartilhada. Nao e achado, e comportamento correto do design da base.
- **Reatribuicao de `source.book` entre reimpressoes**: nomes existem na base mas com o livro "errado" do ponto de vista de origem historica (ex: 7 feats de Barbarian do Player Core 2 aparecem na base sob `source.book: "Player Core"` porque sao feats compartilhados Barbarian+Fighter; spells do PC2 como "Chilling Spray", "Imprint Message", "Object Reading" aparecem sob livros de reimpressao como "Gods & Magic" ou modulos de aventura). Conteudo presente, so a etiqueta de fonte historica diverge -- nao e gap de cobertura.
- **Remaster com alias correto**: 58 de 61 "ausencias" iniciais no Ancestry Guide foram localizadas no lookup global sob `source.book: "Player Core 2"`, linkadas corretamente via `aliases` ao nome legacy (heritages de Hobgoblin, Tengu, feats de Aasimar, etc.). O mecanismo de fusao Legacy/Remaster funciona na esmagadora maioria dos casos -- os 2 kobolds acima sao excecao, nao regra.
- **Ruido de extracao propria dos agentes**: nomes cortados por colisao com palavras de cabecalho de coluna ("DIVINE", "PRIMAL"), apostrofo tipografico (’) vs. reto (') divergente entre a lista extraida e a base, e um caso de arquetipo modelado via feat de dedicacao (`kind: "feat"`) em vez de registro de arquetipo proprio (`kind: "archetype"`) -- todos confirmados presentes apos correcao manual, nao contam como achado.

## Veredito

A afirmacao original -- "os PDFs nao adicionam cobertura de regra" -- **nao se sustenta integralmente**, mas o desvio medido e pequeno e concentrado em duas causas especificas, nao numa lacuna ampla e dispersa:

1. **Achado real e sistemico**: a base nao tem categoria "ritual" (`kind: "ritual"`) — 31 rituals confirmados ausentes so nos 2 livros medidos (Player Core + Player Core 2). Isso e uma lacuna de cobertura genuina e vale correcao no pipeline (provavelmente um tipo de documento do Foundry VTT que nunca foi ingerido).
2. **Achados pontuais**: 3 casos isolados (1 feat de ancestria perdido em parsing, 2 aliases de heranca de kobold faltando) em 1.377 nomes checados -- ruido de pipeline normal, nao padrao sistemico.

Taxa de cobertura medida por livro (excluindo o gap sistemico de rituals, que e uma categoria inteira faltando e nao um problema de completude por livro):

- Player Core: 673/691 = 97,4% bruto: mas as 18 ausencias sao 100% rituals; feats e spells = 100% cobertos.
- Player Core 2: 321/322 = 99,7% bruto (excluindo 13 rituals do denominador de "pontual").
- War of Immortals: 186/186 = 100% (o unico achado inicial foi falso positivo).
- Lost Omens Ancestry Guide: 176/178 = 98,9%.

**Amostra: 4 livros de 26 disponiveis (11 DM + 15 Worldbuilding), 1.377 nomes.** Treasure Vault nao foi medido (PDF sem camada de texto, OCR inviavel no tempo/recursos disponiveis) -- nao ha dado sobre ele. Os outros 21 livros (incluindo GM Core, Book of the Dead, Secrets of Magic, Guns & Gears, Rage of Elements, Dark Archive, e 14 outros Lost Omens) nao foram tocados neste teste; nao da pra generalizar o veredito pra eles.

**Conclusao pratica**: dentro do que foi medido, Igor esta certo de que os PDFs quase nao adicionam cobertura -- exceto pela categoria "ritual", que e uma lacuna real e vale a pena investigar/corrigir no pipeline de fusao. Descontando rituals (32 dos 1.377 nomes cruzados eram rituals), sobram 1.345 nomes nao-ritual checados com 3 ausencias reais = 99,8% de cobertura pontual.
