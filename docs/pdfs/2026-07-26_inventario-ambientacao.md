# Inventario de ambientacao (worldbuilding) -- 15 PDFs Lost Omens

Data: 2026-07-26
Metodo: `pdfinfo` + `pdftotext -layout` (sumario + amostragem de 2-3 secoes por livro), cruzado contra `pipeline/base/index.json` (contagem por `source.book`). Nenhum arquivo em `pipeline/base/` foi modificado -- inventario e leitura pura.

Criterio de utilidade aplicado: **o texto serve para escolher ou interpretar um personagem?** Descricao de ancestria/cultura, de regiao/nacao de origem, de divindade praticada, de organizacao filiavel = util. Historia de guerra entre NPCs, mapa politico, estatistica de cidade, ficha de NPC, adventure hook = nao util.

## 1. Tabela por livro

| Livro | Paginas | Registros na base hoje | Util pelo criterio | % util (estimado) |
|---|---|---|---|---|
| Ancestry Guide | 146 | 362 | Cap.1 (lore extra de 14 ancestrias ja existentes, hoje NAO capturado) + Cap.2 (13 novas ancestrias, JA capturado via `text/ancestry.json`) | ~38-40% (mas boa parte ja esta na base) |
| Gods & Magic (2020, 1a ed. 2e) | 138 | 43 | Dogma/clero de 40 divindades, filosofias nao-teistas (Green Faith etc.) | ~38-40% |
| Grand Bazaar | 138 | 488 | So o capitulo Poppet (ancestria) -- ja capturado | ~4% |
| Impossible Lands | 346 | 243 | Cap. People (5 ancestrias regionais), aberturas de nacao, Religion | ~20-25% |
| Legends | 130 | 71 | Quase nada -- e biografia de NPC lendario | ~3-4% |
| Monsters of Myth | 130 | 43 | So o capitulo Ainamuuren (cultura + arquetipo) | ~2-3% |
| Mwangi Expanse | 314 | 97 | Cap. People (etnias/subculturas + ancestrias raras), Religion, aberturas de cidade | ~55-58% |
| Absalom, City of Lost Omens | 402 | 16 | Cultura e Costumes, Guilds and Unions, gangues, aberturas de distrito | ~10-12% |
| Shining Kingdoms | 194 | 161 | People, Beliefs, aberturas de nacao, Factions (parcial) | ~13-18% |
| Travel Guide | 130 | 99 | Vida cotidiana por topico (costumes, ritos, passatempos, organizacoes) | ~25-35% |
| World Guide (2e) | 138 | 127 | Fragmentos de cultura/panteao dispersos em meio a historia politica | ~10-15% |
| Pathfinder Society Guide | 130 | 159 | Vida na Society, Factions, Lodges | ~40% |
| Inner Sea Primer | 36 | 0 | **Pathfinder 1e**, mal classificado na pasta PF2e (ver nota abaixo) | n/a para a base 2e |
| Inner Sea World Guide (2011) | 322 | 0 | **Pathfinder 1e**, fora de escopo (ver aviso do briefing) | n/a para a base 2e |
| Lost Omens.pdf | 40 | desconhecido | **Sem camada de texto** -- ver nota abaixo | n/a |

### Notas tecnicas

- **`Lost Omens.pdf`** (titulo interno `PZO12002E.pdf`, "Print to PDF"): `pdffonts` retorna zero fontes embutidas e `pdftotext` do documento inteiro retorna 40 bytes. E um scan/print sem camada de texto -- ilegivel por extracao automatica. Nao foi possivel identificar a que livro corresponde. Se o conteudo for necessario, precisa de OCR ou de encontrar outra copia do arquivo.
- **`Inner Sea Primer.pdf`**: confirmado Pathfinder **1a edicao** pelo texto (menciona "Pathfinder Roleplaying Game", OGL v1.0a de 2010, vocabulario mecanico exclusivo de 1e como armor/weapon training). Esta arquivado na pasta `PF2e/Worldbuilding/`, o que esta errado -- deveria estar junto do outro material 1e (Inner Sea World Guide 2011). Contem descricoes de ~20 nacoes, divindades e etnias que coincidem em nome com o material 2e, entao pode servir de referencia de adaptacao futura, mas precisaria validacao contra retcons pos-remaster antes de qualquer uso.
- **`Inner Sea World Guide (2011)`**: confirmado Pathfinder 1e pela propria capa ("Pathfinder Roleplaying Game"). Fora de escopo da base 2e -- so serve como mapa de categorias/estrutura, nao como fonte direta.
- Ruido recorrente do `pdftotext -layout` em varios livros (Mwangi Expanse, Impossible Lands, Pathfinder Society Guide): barra de navegacao lateral (nomes de capitulo verticalizados na margem) aparece intercalada no meio do texto extraido. E reconhecivel e filtravel, nao e erro de extracao -- mas a ingestao real vai precisar de um passo de limpeza.

## 2. Categorias de texto util

**a) Descricao de ancestria/cultura ("como e ser um X")**
Ja parcialmente capturado no pipeline atual (`text/ancestry.json`, prosa "You Might.../Others Probably..." por ancestria). O que falta e a camada de **variacao regional** dentro de uma ancestria (subgrupo etnico/cultural, nao uma ancestria nova): ex. "Alijae elves" no Mwangi Expanse -- nao existe como registro em `heritage` nem `ancestry` na base hoje.
> "Alijae elves usually have some manner of divine patron... They consider faith a much more personal matter."

**b) Descricao de regiao/nacao de origem**
Categoria mais volumosa. Prosa sobre temperamento, valores e cotidiano de um povo ligado a um territorio -- nao a ficha politica/administrativa da nacao.
> "Andoran e um pais onde cada vida e considerada valiosa... a filosofia de que todo individuo tem valor igual." (Shining Kingdoms)

**c) Divindade em pratica (dogma vivido, nao so Edicts/Anathema)**
Parcialmente ja capturado em `text/deity.json` (a entrada oficial da divindade ja tem prosa longa). O que falta e o **recorte regional**: como uma divindade e vivida em um lugar especifico.
> "Em Druma, os Kalistocratas... fundem sua riqueza e a injetam no corpo, mumificando-se." (Shining Kingdoms)

**d) Organizacao filiavel**
Nao existe hoje nenhum `kind` equivalente na base. Cobre desde grandes organizacoes (Pathfinder Society e suas 5 faccoes, 11 lodges) ate guildas/gangues locais (Absalom).
> "Being accepted into the Pathfinder Society is only the beginning; even a capable adventurer must undergo additional training..." (Pathfinder Society Guide)

**e) Costume/rito transversal (nao amarrado a uma ancestria, deidade ou nacao especifica)**
Menor prioridade -- e o tipo de texto mais dificil de encaixar em um registro existente porque atravessa varias categorias ao mesmo tempo (ex.: como diferentes ancestrias contam o tempo, ritos de passagem por regiao).
> "Elves: Thanks to their long lifespan, elves speak less of years than phases..." (Travel Guide)

## 3. Proposta de modelagem

**Recomendacao: dois movimentos separados, nao um so.**

**(1) Dois `kind` novos -- `region` e `organization`.**
Seguem exatamente o padrao ja usado por `ancestry`, `deity`, `background`: um registro minimo em `index.json` (id, kind, name, source) + prosa correspondente em `text/region.json` / `text/organization.json`. Sem campos mecanicos (`grants`) na maioria dos casos -- sao entradas de identidade/contexto, nao de build. Isso cobre as categorias (b) e (d) acima, que hoje nao tem lugar nenhum na base. E a opcao certa porque mantem a arquitetura uniforme (todo `kind` = metadado + texto), em vez de inventar um formato paralelo so pra isso.

**(2) Enriquecer (append, nao substituir) os `text/ancestry.json` e `text/deity.json` existentes com o recorte regional.**
Cobre as categorias (a) e (c). Uma entrada de ancestria ja existente (ex. `dwarf`, hoje so com o texto do Player Core) ganha um paragrafo adicional de contexto do Ancestry Guide Cap.1, tageado com a fonte. O mesmo pra divindades com pratica regional descrita em mais de um livro. Isso evita duplicar a identidade da ancestria/divindade em dois lugares -- o flavor fica onde o usuario ja vai olhar quando escolhe aquele registro.

**O que eu NAO recomendo agora:** criar um `kind` para categoria (e) (costume transversal). E pouco volume, dificil de amarrar a um id especifico, e o retorno por esforco de modelagem e baixo comparado a (1) e (2). Se aparecer necessidade real depois, tratar como excecao pontual (ex.: anexar a nota de "elfos contam tempo em fases" na propria entrada de ancestria elf, em vez de criar infraestrutura nova).

## 4. Estimativa de volume

Somando as estimativas de paginas uteis por livro (livros 2e utilizaveis, excluindo os dois volumes 1e e o PDF corrompido):

- Ancestry Guide: ~55-60 pag.
- Gods & Magic: ~50-55 pag.
- Grand Bazaar: ~6 pag.
- Impossible Lands: ~70-85 pag.
- Legends: ~3-5 pag.
- Monsters of Myth: ~3-4 pag.
- Mwangi Expanse: ~170-180 pag.
- Absalom, City of Lost Omens: ~40-50 pag.
- Shining Kingdoms: ~25-35 pag.
- Travel Guide: ~30-40 pag.
- World Guide: ~12-18 pag.
- Pathfinder Society Guide: ~52 pag.

**Total: aproximadamente 500-550 paginas de texto util**, das quais uma fatia relevante (talvez 30-40%, sobretudo em Ancestry Guide, Grand Bazaar e parte do Mwangi Expanse) ja tem overlap com o que o pipeline ja capturou como texto de ancestria/divindade -- o volume genuinamente **novo** para a base (regioes + organizacoes + enriquecimento regional) fica na faixa de **~350-400 paginas equivalentes**.

Concentracao: **Mwangi Expanse** (maior densidade absoluta, ~55-58% do livro), **Impossible Lands** e **Pathfinder Society Guide** (melhor proporcao util/pagina) sao os tres livros com melhor retorno para processar primeiro.
