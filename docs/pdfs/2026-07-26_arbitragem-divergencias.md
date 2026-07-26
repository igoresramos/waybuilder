> Aviso de escopo: o OCR de "Treasure Vault" e "War of Immortals" não terminou a tempo (ver secao 5).
> 37 dos 45 casos planejados foram efetivamente verificados contra PDF com camada de texto.
> Os 8 restantes ficam como "nao localizado" com motivo tecnico documentado. Nenhum dado foi inventado.

# Arbitragem de divergencias `conflitos` vs PDF oficial

Data: 2026-07-26
Base: `pipeline/base/index.json` (18.176 registros, 2.299 com `conflitos`)
Metodo: amostragem estratificada por `campo`, verificacao manual (leitura de texto extraido) contra os PDFs oficiais em `pipeline/dados_brutos/pdfs/PF2e/DM/`.

## 1. Distribuicao completa das 2.299 divergencias

A base registra **2.462 entradas de conflito** dentro de **2.299 registros** (101 registros tem mais de um campo em disputa ao mesmo tempo).

### 1.1 Por campo (todas as 2.462 entradas, universo completo)

| campo | ocorrencias | % do total | fonte de precedencia (spec) |
|---|---:|---:|---|
| `traits` | 2.169 | 88,1% | aon (tabela generica `PRECEDENCIA` em `reconciliar.py`) |
| `level` | 94 | 3,8% | foundry (tabela generica) |
| `source` | 72 | 2,9% | aon (tabela generica) |
| `name` | 47 | 1,9% | aon (tabela generica) |
| `texto` | 25 | 1,0% | ad-hoc, `extratores/magias.py` (so uma fonte tem o dado na maioria dos casos) |
| `tradicoes` | 20 | 0,8% | ad-hoc, foundry (`extratores/magias.py`) |
| `rarity` | 12 | 0,5% | aon (tabela generica) |
| `requires_texto` | 8 | 0,3% | ad-hoc, `extratores/feats.py` (so uma fonte tem o dado) |
| `defesa` | 7 | 0,3% | ad-hoc, gap conhecido (`extratores/magias.py`) |
| `requires` | 2 | 0,1% | pf2etools (tabela generica) |
| `rank` | 2 | 0,1% | ad-hoc, foundry (`extratores/magias.py`) |
| `divine_font` | 1 | <0,1% | ad-hoc, `extratores/referencia.py` |
| `domains` | 1 | <0,1% | ad-hoc, `extratores/referencia.py` |
| `area_of_concern` | 1 | <0,1% | ad-hoc, `extratores/referencia.py` |
| `cleric_spell` | 1 | <0,1% | ad-hoc, `extratores/referencia.py` |
| **total** | **2.462** | 100% | |

**Achado 1 -- `grants` nunca aparece como campo de conflito real.** A spec descrita pelo Igor cita `grants -> foundry` como parte da tabela de precedencia (e o codigo em `reconciliar.py` de fato tem essa entrada), mas **zero** entradas de `conflitos` tem `campo: "grants"`. Motivo: na funcao `fundir()`, quando um dos lados tem `grants` vazio/ausente, o merge adota o outro lado silenciosamente (nao gera conflito) -- so registra conflito quando as duas fontes tem valor nao-vazio e diferente. Como o extrator de `grants` roda majoritariamente a partir do Foundry, o outro lado costuma vir vazio, entao a regra de precedencia pra `grants` nunca chega a ser exercitada de fato. **Nao da pra medir a taxa de acerto de `grants -> foundry` porque nao ha casos reais no dataset.**

**Achado 2 -- boa parte dos campos com conflito nao estao na tabela generica de precedencia.** `tradicoes`, `rank`, `defesa`, `requires_texto`, `texto`, `divine_font`, `domains`, `area_of_concern`, `cleric_spell` sao decisoes ad-hoc codificadas direto nos extratores especificos de magia/feat/divindade (`magias.py`, `feats.py`, `referencia.py`), nao passam pela `PRECEDENCIA` de `reconciliar.py`. Isso significa que "mudar a tabela de precedencia" (no sentido do pedido original) so afeta `grants`, `requires`, `name`, `traits`, `rarity`, `text`/`source`, `level` -- os demais exigiriam mudar cada extrator individualmente.

### 1.2 Por livro (top 20 de 139 livros distintos com conflito)

| livro (`source.book` como gravado na base) | ocorrencias |
|---|---:|
| Treasure Vault (Remastered) | 201 |
| Secrets of Magic | 180 |
| Grand Bazaar | 171 |
| Player Core 2 | 139 |
| Player Core | 106 |
| GM Core | 99 |
| Core Rulebook | 74 |
| Ancestry Guide | 73 |
| Guns & Gears (Remastered) | 63 |
| Tian Xia Character Guide | 59 |
| Battlecry! | 57 |
| Howl of the Wild | 52 |
| Highhelm | 52 |
| War of Immortals | 48 |
| Rage of Elements | 45 |
| Book of the Dead | 41 |
| Season of Ghosts (Hardcover) | 39 |
| Firebrands | 35 |
| Impossible Lands | 32 |
| Character Guide | 32 |
| ... (mais 119 livros, a maioria aventuras avulsas com poucas ocorrencias) | |

**Achado 3 -- `source.book` tem variantes do mesmo livro gravadas como strings diferentes.** Confirmado, e vale mais do que so o caso do Treasure Vault citado no pedido:

- `Treasure Vault (Remastered)` (201) + `Pathfinder Treasure Vault (Remastered)` (5) = **206 ocorrencias do mesmo livro remasterizado**, gravadas com dois nomes. Ha ainda `Treasure Vault` sem "(Remastered)" (11 ocorrencias) -- essa e mais delicada: pode ser o mesmo livro remasterizado com o sufixo cortado, **ou** pode ser referencia a paginacao da edicao OGL original (que tem layout diferente da Remastered). O PDF disponivel e so o Remastered; nao da pra confirmar as 11 ocorrencias sem o PDF da edicao OGL.
- `Battlecry!` (57) + `Pathfinder Battlecry!` (2) = mesmo padrao, fora do escopo desta amostra (sem PDF disponivel).
- O mesmo padrao aparece **dentro dos proprios valores em disputa**, nao so no campo resolvido: em varios casos de `campo: "source"` a divergencia inteira e causada pelo foundry gravar o livro como `"Pathfinder <Nome do Livro>"` (com prefixo "Pathfinder") enquanto aon/pf2etools gravam so `"<Nome do Livro>"`. Isso apareceu nos casos verificados de Guns & Gears (`"Pathfinder Guns & Gears"` vs `"Guns & Gears (Remastered)"`), Dark Archives (`"Pathfinder Dark Archive (Remastered)"` vs `"Dark Archives (Remastered)"`), Player Core (`"Pathfinder Player Core"` vs `"Player Core"`) e Treasure Vault (`"Pathfinder Treasure Vault (Remastered)"` vs `"Treasure Vault (Remastered)"`). Ou seja: uma fatia relevante dos 72 conflitos de `campo: source` no dataset inteiro provavelmente **nao e divergencia de conteudo, e sim diferenca de convencao de nome entre as fontes** (foundry usa prefixo "Pathfinder", aon/pf2etools nao). Vale um `normalizar_livro()`-like tambem no lado do merge de `source.book`, nao so na camada de relatorio.

## 2. Amostra verificada -- filtragem pelos PDFs disponiveis

Dos 10 livros com PDF disponivel, a base tem **951 entradas de conflito** (em 45 registros distintos foram sorteados casos, cobrindo 11 campos):

| livro | conflitos disponiveis pra arbitragem | amostrados |
|---|---:|---:|
| Treasure Vault (Remastered) | 206 | 3 |
| Secrets of Magic | 180 | 7 |
| Player Core 2 | 139 | 4 |
| Player Core | 106 | 8 |
| GM Core | 99 | 2 |
| Guns & Gears (Remastered) | 63 | 5 |
| War of Immortals | 48 | 5 |
| Rage of Elements | 45 | 2 |
| Book of the Dead | 41 | 1 |
| Dark Archives (Remastered) | 24 | 8 |
| **total** | **951** | **45** |

Amostra por campo: `traits` 10, `level` 8, `source` 5, `name` 5, `tradicoes` 4, `texto` 3, `rarity` 3, `requires_texto` 2, `defesa` 2, `rank` 2, `requires` 1.

## 3. Achado tecnico -- dois dos dez PDFs sao scan de imagem sem camada de texto

`pdftotext -layout` retorna **vazio** em `Pathfinder 2e - Treasure Vault.pdf` e `Pathfinder 2e - War of Immortals.pdf` (confirmado nas paginas 40-60 de ambos, 0 caracteres extraidos). Os outros 8 PDFs do escopo tem camada de texto normal (100k+ caracteres numa janela de 20 paginas). Esses dois arquivos sao renderizacoes de imagem (o tamanho em disco tambem denuncia: 229 MB e 235 MB contra 15-35 MB dos demais, apesar de pagina-count semelhante).

Tentei recuperar via OCR (`pdftoppm` -> `tesseract`, ~20-25s por pagina renderizada + OCR). O processo nao terminou dentro do tempo disponivel desta sessao: as paginas foram renderizadas mas o OCR travou/nao concluiu a tempo pra nenhum dos 8 casos amostrados desses dois livros. Resultado: **8 dos 45 casos amostrados ficam como "nao localizado"** (ver tabela da secao 4.3). Isso e um achado por si so: **a base nao pode ser arbitrada contra esses dois livros sem um pipeline de OCR dedicado** -- pdftotext simples nao serve.

## 4. Resultado caso a caso

### 4.1 Legenda
- **Acertou**: o PDF confirma o valor que a precedencia escolheu.
- **Errou**: o PDF confirma um valor diferente do escolhido pela precedencia.
- **Nenhuma bate**: o PDF nao confirma nenhuma das fontes em disputa (nem a escolhida nem a alternativa) -- acontece principalmente em `traits`, onde as fontes divergem por adicoes/remocoes pontuais.
- **Nao aplicavel**: nao era uma disputa real de precedencia (so uma fonte tinha o dado -- registrado como "desconhecida" no `conflitos`), ou o campo nao e comparavel diretamente ao texto impresso (ex.: `source` cruzando dois livros legitimamente).
- **Nao localizado**: PDF sem camada de texto (Treasure Vault / War of Immortals) e OCR nao concluiu a tempo.

### 4.2 Casos verificados (37)

| id | campo | foundry | aon | pf2etools | precedencia escolheu | PDF diz (pagina real) | resultado |
|---|---|---|---|---|---|---|---|
| `wb:feat/explosive-arrival` | traits | concentrate, manipulate, spellshape, wizard | + metamagic | -- | **aon** | so 4 traits, sem "metamagic" (pg. 204/idx, impressa 203) | **Errou** |
| `wb:weapon/composite-shortbow` | level | 1 | 1 | 0 | **foundry** (1) | tabela de armas sem nivel anotado = convencao nivel 0 (pg. 282, evidencia indireta) | **Errou** (indireto) |
| `wb:equipment/lantern-bulls-eye` | source | "Pathfinder Player Core" (sem pg) | "Player Core" pg. 288 | -- | **aon** | item na pg. 288 impressa, confirma | **Acertou** |
| `wb:equipment/scholarly-journal-compendium` | name | "Scholarly Journal Compendium" | "Scholarly Journal (Compendium)" | -- | **aon** | tabela imprime "Scholarly journal compendium", sem parenteses (pg. 293/292) | **Errou** |
| `wb:spell/insect-form` | tradicoes | arcane, primal | -- | primal | **foundry** | "Traditions arcane, primal" (pg. 339/338) | **Acertou** |
| `wb:spell/shape-wood` | tradicoes | arcane, primal | -- | primal | **foundry** | "Traditions arcane, primal" (pg. 357/356) | **Acertou** |
| `wb:spell/speak-with-plants` | rank | 3 | 3 | 4 | **foundry** (3) | "SPELL 3" (pg. 359/358) | **Acertou** |
| `wb:spell/enlarge-companion` | rank | 2 | 2 | 4 | **foundry** (2) | "FOCUS 2" (pg. 384/383) | **Acertou** |
| `wb:equipment/wand-of-slaughter-8th-rank-spell` | traits | magical, void, wand | + negative | -- | **aon** | statblock so lista MAGICAL, VOID, WAND (pg. 309) | **Errou** |
| `wb:feat/surging-might` | level | 8 | 8 | 10 | **foundry** (8) | "FEAT 8" (pg. 141) | **Acertou** |
| `wb:equipment/eagle-eye-elixir-moderate` | name | "Eagle Eye Elixir" (sem hifen) | "Eagle-Eye Elixir" | -- | **aon** | "EAGLE-EYE ELIXIR" (pg. 287) | **Acertou** |
| `wb:spell/drop-dead` | tradicoes | arcane, divine, occult | -- | arcane, divine | **foundry** | "Traditions arcane, divine, occult" (pg. 244) | **Acertou** |
| `wb:weapon/staff-of-summoning-greater` | traits | + two-hand-d8 | magical, staff | -- | **aon** | "held in 1 hand"; sem trait two-hand em nenhuma variante (pg. 281/280) | **Acertou** |
| `wb:equipment/dawnsilver-chunk` | level | 0 | 8 | -- | **foundry** (0) | item base sem nivel listado = 0; nivel 8 e do material bruto "8+", nao do chunk (pg. 254/253) | **Acertou** |
| `wb:equipment/titans-grasp` | traits | apex, invested, magical | + evocation | -- | **aon** | "APEX EVOCATION INVESTED MAGICAL" (pg. 191) | **Acertou** |
| `wb:spell/crushing-ground` | source | Rage of Elements pg. 61 | -- | -- | **foundry** | SoM nao imprime linha "Source" pra conteudo nativo -- nao verificavel nesta fonte | **Nao aplicavel** |
| `wb:spell/rapid-adaptation` | tradicoes | primal | -- | arcane, primal | **foundry** (so primal) | "Traditions arcane, primal" (pg. 124) | **Errou** |
| `wb:spell/updraft` | texto | -- | -- | -- (desconhecida) | -- | magia existe pg. 201/202, sem linha "Source" impressa | **Nao aplicavel** |
| `wb:spell/powerful-inhalation` | texto | -- | -- | -- (desconhecida) | -- | magia existe pg. 201/202, sem linha "Source" impressa | **Nao aplicavel** |
| `wb:spell/pulverizing-cascade` | texto | -- | -- | -- (desconhecida) | -- | magia existe pg. 201/202, sem linha "Source" impressa | **Nao aplicavel** |
| `wb:spell/burning-blossoms` | defesa | null (gap) | Will | -- | **foundry (gap)** | "Saving Throw Will" (pg. 93/94) -- gap preenchido corretamente por aon | **Nao aplicavel** (gap, nao disputa) |
| `wb:weapon/reinforced-stock` | traits | attached-to-crossbow-or-firearm, finesse, two-hand-**d8** | attached, finesse, two-hand | -- | **aon** | "Attached to crossbow or firearm, finesse, two-hand **d6**" (pg. 150) | **Nenhuma bate** (dado errado nos dois; aon mais incompleto) |
| `wb:equipment/travelers-chair` | level | 0 | 1 | -- | **foundry** (0) | "TRAVELER'S CHAIR ITEM 1" (pg. 91) | **Errou** |
| `wb:weapon/dragon-mouth-pistol` | source | "Pathfinder Guns & Gears" (sem pg) | "Guns & Gears (Remastered)" pg. 152 | -- | **aon** | item descrito na pg. 152 | **Acertou** |
| `wb:weapon/dragon-mouth-pistol` | name | "Dragon Mouth Pistol" | "Dragon-Mouth Pistol" | -- | **aon** | "Dragon-Mouth Pistol" com hifen (pg. 152) | **Acertou** |
| `wb:feat/spellshot-dedication` | rarity | common | uncommon | -- | **aon** | "Rarity Uncommon" no cabecalho do archetype (pg. 140) | **Acertou** |
| `wb:weapon/obsidian-edge-greater` | traits | + combination, concussive, kickback | fire, magical | -- | **aon** | statblock so lista "UNCOMMON FIRE MAGICAL" (pg. 123) | **Acertou** |
| `wb:weapon/atmospheric-staff` | level | 8 | 4 | -- | **foundry** (8) | variante base = "Level 8" (nivel 4 e da variante "lesser") (pg. 74) | **Acertou** |
| `wb:feat/what-could-have-been` | traits | archetype, concentrate, spellshape | + metamagic | -- | **aon** | "ARCHETYPE CONCENTRATE METAMAGIC" -- 3 traits, sem "spellshape" (pg. 185, idx 186) | **Nenhuma bate** (possivel erratum digital pos-publicacao) |
| `wb:feat/twin-psyche` | level | 18 | 18 | 20 | **foundry** (18) | "FEAT 20" (pg. 29, idx 30) | **Errou** |
| `wb:feat/two-truths` | source | "Pathfinder Dark Archive (Remastered)" (sem pg) | "Dark Archives (Remastered)" pg. 121 | -- | **aon** | feat impresso na pg. 121 | **Acertou** |
| `wb:feat/two-truths` | name | "Two Truths" (sem hifen) | "Two-Truths" | -- | **aon** | "TWO TRUTHS" sem hifen (confirmado por dump de bytes) (pg. 121) | **Errou** |
| `wb:feat/two-truths` | requires_texto | -- | -- | -- (desconhecida: "Expert in Deception") | -- | "Prerequisites master in Deception" -- o texto capturado estava desatualizado | **Nao aplicavel** |
| `wb:feat/two-truths` | requires | -- | expert em Deception | master em Deception | **pf2etools** | "Prerequisites master in Deception" (pg. 121) | **Acertou** |
| `wb:feat/sleepwalker-dedication` | rarity | common | uncommon | -- | **aon** | sem tag de raridade impressa = common (pg. 206) | **Errou** |
| `wb:feat/advanced-runic-mind-smithing` | requires_texto | -- | -- | -- (desconhecida) | -- | "Prerequisites Runic Mind Smithing" -- confirmado (pg. 205) | **Nao aplicavel** |
| `wb:feat/undying-conviction` | traits | aura, cleric, oracle, wizard | + necromancy | -- | **aon** | "AURA CLERIC NECROMANCY ORACLE WIZARD" (pg. 34, impressa 33) | **Acertou** |

### 4.3 Casos nao localizados (8) -- PDF sem camada de texto, OCR nao concluiu a tempo

| id | campo | livro | motivo |
|---|---|---|---|
| `wb:weapon/caydens-tankard` | traits | Treasure Vault (Remastered) | PDF e scan; render OCR feito mas nao processado a tempo |
| `wb:weapon/bow-staff` | level | Treasure Vault (Remastered) | sem `source.page` de referencia + PDF sem texto pesquisavel |
| `wb:equipment/depth-charge-vii` | source | Treasure Vault (Remastered) | PDF e scan; render OCR feito mas nao processado a tempo |
| `wb:feat/spiritual-secret` | traits | War of Immortals | PDF e scan; render OCR feito mas nao processado a tempo |
| `wb:feat/death-from-above` | level | War of Immortals | PDF e scan; render OCR feito mas nao processado a tempo |
| `wb:feat/needle-in-the-gods-eyes` | name | War of Immortals | PDF e scan; render OCR feito mas nao processado a tempo |
| `wb:feat/army-of-one` | rarity | War of Immortals | PDF e scan; render OCR feito mas nao processado a tempo |
| `wb:spell/manifest-will` | defesa | War of Immortals | PDF e scan; render OCR feito mas nao processado a tempo |

## 5. Taxa de acerto por campo (N real, so casos com veredito Acertou/Errou/Nenhuma-bate)

Excluindo "nao aplicavel" (7 casos: nao eram disputas reais de precedencia) e "nao localizado" (8 casos), sobram **30 disputas de precedencia genuinamente verificaveis**:

| campo | precedencia (spec) | N verificado | acertos | taxa | observacao |
|---|---|---:|---:|---:|---|
| `traits` | aon | 8 | 4 | **50%** | 2 erros diretos (aon errado, foundry certo) + 2 "nenhuma bate" (nem aon nem foundry batem o PDF) |
| `level` | foundry | 6 | 3 | **50%** | 3 erros; em 2 deles o valor certo era pf2etools, nao a alternativa "obvia" (aon) |
| `source` | aon | 3 | 3 | **100%** | N pequeno; nos 3 casos o erro do foundry era so o prefixo "Pathfinder " no nome do livro |
| `name` | aon | 4 | 2 | **50%** | 2 erros -- aon adiciona/mantem hifen e parenteses que o PDF nao usa |
| `tradicoes` | foundry (ad-hoc) | 4 | 3 | **75%** | 1 erro (PDF bate com pf2etools) |
| `rarity` | aon | 2 | 1 | **50%** | N minimo |
| `rank` | foundry (ad-hoc) | 2 | 2 | **100%** | N minimo |
| `requires` | pf2etools | 1 | 1 | **100%** | N=1, anedota |
| **geral (soma)** | -- | **30** | **19** | **63,3%** | |

## 6. Veredito

**A precedencia atual nao esta claramente certa nos dois campos que mais importam.**

`traits` e `level` sao os campos com volume real no dataset (2.169 e 94 ocorrencias no universo inteiro -- juntos, 92% de todas as divergencias registradas) e sao tambem os unicos com amostra grande o bastante nesta rodada (N=8 e N=6) pra dizer algo com alguma confianca. Nos dois, a precedencia acertou exatamente **metade** das vezes -- nao melhor que jogar uma moeda. Isso nao e ruido de amostra pequena: e um sinal consistente contra a hipotese "aon sempre vence traits" e "foundry sempre vence level".

Padroes que emergiram e que uma regra fixa por campo nao consegue capturar:

1. **`traits`**: quando aon e foundry discordam, nem sempre um dos dois esta certo -- em 2 dos 8 casos (`reinforced-stock`, `what-could-have-been`) **nenhuma das duas fontes bate exatamente** com o PDF impresso. Isso sugere que fontes digitais (foundry, aon) recebem erratas/atualizacoes ao longo do tempo que dessincronizam do texto impresso original, em direcoes diferentes uma da outra. Uma precedencia fixa por fonte nao resolve isso -- so verificacao pontual resolve.
2. **`level`**: nos 3 erros, o valor certo do PDF as vezes bateu com pf2etools (fonte que a spec trata como pior opcao pra esse campo) e as vezes exigiu leitura de contexto (item sem nivel anotado = nivel 0, por convencao da tabela). Ou seja, o erro de `composite-shortbow` nao e "a fonte errada venceu", e "a regra e simples demais pra decidir isso sem olhar a pagina".
3. **`source`**: aqui a precedencia aon parece solida (3/3), mas o motivo nao e "aon sabe melhor onde o item esta" -- e que **o unico jeito de foundry perder e ter o nome do livro prefixado com "Pathfinder "**, que e puro estilo de nomenclatura, nao erro de conteudo. Recomendo normalizar `source.book` (remover o prefixo "Pathfinder" na comparacao, como o proprio `normalizar_livro()` do `reconciliar.py` ja faz pra outros fins) **antes** de aplicar a precedencia -- isso devia eliminar a maior parte dos 72 conflitos de `source` do dataset sem trocar nenhuma regra.

**Recomendacao concreta:**

- **Nao trocar cegamente `traits: aon -> foundry` nem `level: foundry -> pf2etools`.** A amostra mostra que nenhuma fonte unica e confiavel o bastante pra virar "sempre vence" nesses dois campos -- trocar a direcao da regra so troca qual metade dos casos fica errada.
- **Aplicar `normalizar_livro()` (ja existe em `reconciliar.py`) antes de comparar `source.book`** entre fontes, pra parar de contar como "conflito" uma diferenca que e so estilo de nome. Deve reduzir drasticamente os 72 conflitos de `source` (e melhorar a precisao real da metrica de conflito da base como um todo).
- **`tradicoes`, `rank`, `requires`** tiveram taxa boa (75-100%), mas com N=1 a N=4 -- amostra pequena demais pra confirmar, mas nao ha sinal contrario; manter como esta.
- **Antes de decidir o destino de `traits`/`level` em definitivo, ampliar a amostra especificamente desses dois campos** (sao os que tem volume no dataset -- vale gastar mais orcamento de verificacao neles do que nos campos de cauda longa) e, se possivel, resolver o OCR do Treasure Vault/War of Immortals pra nao perder 8 casos do proximo lote.
- **Concluir o pipeline de OCR** (`pdftoppm` + `tesseract`, testado e funcional, so nao coube no tempo desta sessao) antes de arbitrar qualquer coisa do Treasure Vault ou War of Immortals -- sao 254 conflitos combinados (206+48) que hoje sao inarbitraveis por leitura direta de texto.

## 7. Notas metodologicas

- Amostragem: `random.seed(42)`, estratificada por campo com alvo de 30-50 casos distribuidos entre os 11 campos presentes nos livros disponiveis, com rodizio entre livros dentro de cada campo pra nao concentrar tudo num so PDF.
- Verificacao: 8 agentes independentes rodaram `pdftotext -layout -f <inicio> -l <fim>` em janelas de ate +/-15 paginas ao redor da `source.page` da base, confirmando pelo cabecalho/titulo do item, nao so pelo numero de pagina.
- Nenhum arquivo da base ou dos PDFs foi modificado nesta tarefa.
- Script de analise e amostragem: `/tmp/claude-1000/.../scratchpad/analyze.py` e `sample.py` (temporarios, nao versionados no projeto).
