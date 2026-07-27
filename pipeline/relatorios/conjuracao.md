# Relatorio -- extrator de conjuracao (spell slots)

Pin do Foundry: `87f9e5028baaa10b70fdc766260b7886def17e04`

## Cobertura

- Classes cobertas: **11** (wizard, cleric, druid, sorcerer, bard, witch, oracle, psychic, animist, magus, summoner)
- Tabela de slots (1-20, todos os ranks) com o PDF oficial como fonte vencedora: **11** classes (wizard, cleric, druid, sorcerer, bard, witch, oracle, psychic, animist (sem cross-check pf2etools -- classe nao esta na fonte), magus, summoner)
- Conflito PDF x pf2etools registrado em `conflitos`: **1** classes (oracle)
- Sem cobertura de tabela completa: **0** (-)

## De onde veio cada pedaco do dado, por classe

| Classe | tradition/type | proficiencia | focus pool | slots/nivel | extra |
|---|---|---|---|---|---|
| Wizard | foundry (regex sobre descricao da class-feature de conjuracao) | foundry (system.spellcasting + items{} 'Expert/Master/Legendary Spellcaster') | foundry (regex sobre a class-feature dona do focus pool nativo) | waybuilder | - |
| Cleric | foundry (regex sobre descricao da class-feature de conjuracao) | foundry (regex sobre as 12 class-features de doutrina first..final-doctrine-{cloistered-cleric,warpriest}, ver conjuracao.md) | foundry (regex sobre Domain Initiate, feat granted pela Primeira Doutrina) | waybuilder | divine_font: foundry (divine-font.json) |
| Druid | foundry (regex sobre descricao da class-feature de conjuracao) | foundry (system.spellcasting + items{} 'Expert/Master/Legendary Spellcaster') | foundry (regex sobre a class-feature dona do focus pool nativo) | waybuilder | - |
| Sorcerer | foundry (regex sobre descricao da class-feature de conjuracao) | foundry (system.spellcasting + items{} 'Expert/Master/Legendary Spellcaster') | foundry (regex sobre a class-feature dona do focus pool nativo) | waybuilder | - |
| Bard | foundry (regex sobre descricao da class-feature de conjuracao) | foundry (system.spellcasting + items{} 'Expert/Master/Legendary Spellcaster') | foundry (regex sobre a class-feature dona do focus pool nativo) | waybuilder | - |
| Witch | foundry (regex sobre descricao da class-feature de conjuracao) | foundry (system.spellcasting + items{} 'Expert/Master/Legendary Spellcaster') | foundry (regex sobre a class-feature dona do focus pool nativo) | waybuilder | - |
| Oracle | foundry (regex sobre descricao da class-feature de conjuracao) | foundry (system.spellcasting + items{} 'Expert/Master/Legendary Spellcaster') | foundry (regex sobre a class-feature dona do focus pool nativo) | waybuilder | CONFLITO com pf2etools -- ver secao dedicada abaixo |
| Psychic | foundry (regex sobre descricao da class-feature de conjuracao) | foundry (system.spellcasting + items{} 'Expert/Master/Legendary Spellcaster') | foundry (regex sobre a class-feature dona do focus pool nativo) | waybuilder | - |
| Animist | aon (campo 'tradition': ['Divine']) | foundry (system.spellcasting + items{} 'Expert/Master/Legendary Spellcaster') | foundry (regex sobre animist-apparition-spellcasting.json, secao 'Vessel Spells') | waybuilder | notacao hibrida X+Y (dois pools) -- ver secao dedicada abaixo |
| Magus | foundry (regex sobre descricao da class-feature de conjuracao) | foundry (system.spellcasting + items{} 'Expert/Master/Legendary Spellcaster') | foundry (regex sobre a class-feature dona do focus pool nativo) | waybuilder | - |
| Summoner | foundry (regex sobre descricao da class-feature de conjuracao) | foundry (system.spellcasting + items{} 'Expert/Master/Legendary Spellcaster') | foundry (regex sobre a class-feature dona do focus pool nativo) | waybuilder | - |

## Descoberta principal: onde a tabela numerica REALMENTE vive

O relatorio de `classes.py` (extrator irmao) registrou que a tabela de slots "fica em rule elements, nao decodificados nesta passada". Investigado a fundo: **isso nao procede**. Nenhuma class-feature de conjuracao (Wizard Spellcasting, Cleric Spellcasting, Sorcerer Spellcasting etc.) tem `system.rules` com dado numerico de slots -- a lista `rules[]` dessas features ou esta vazia, ou so tem `GrantItem`/`ChoiceSet` para mecanica auxiliar (ex.: escolha heal/harm do Divine Font). O Foundry carrega a tabela em tempo de execucao via codigo TypeScript (nao dado), nao emite ela em nenhum arquivo JSON dos compendios -- so serve de CROSS-CHECK textual pontual (ex.: Oracle abaixo), nunca de fonte estruturada. O pf2etools tem a tabela estruturada (`{"type": "table", "name": "<Classe> Spells per Day"}` dentro de `classFeature[]`/`subclassFeature[]`, ver `find_spells_per_day_table()`), mas **so como cross-check** desde 2026-07-27: pra 5 classes (sorcerer/oracle/psychic/magus/summoner) a branch `dev` so tem o arquivo LEGADO (pre-remaster), e no caso do Oracle isso da o numero ERRADO (ver secao dedicada). A fonte vencedora da tabela numerica agora e `pipeline/dados_brutos/tabelas_conjuracao_pdf.json` -- lida direto dos PDFs oficiais (Player Core, Player Core 2, Dark Archive, Secrets of Magic, War of Immortals), com livro e pagina citados por classe. Ver `escolher_slots()` em conjuracao.py.

## Numeros confirmados em 2+ fontes vs. 1 fonte so

- **Slots por nivel/rank (a tabela inteira)**: fonte vencedora e o PDF oficial (`tabelas_conjuracao_pdf.json`, `prov: "waybuilder"`), pra todas as 11 classes conjuradoras. Cross-check via pf2etools disponivel pra 10 delas (todas exceto animist, que nao esta no index.json da fonte) -- 9 batem exato, 1 diverge (**Oracle**, ver secao dedicada e `conflitos` no registro da classe). Validado tambem por consistencia interna: Wizard/Cleric/Druid/Bard/Witch tem a MESMA progressao (padrao de conjurador pleno: cantrips=5, 2 slots no rank 1, abre rank novo em nivel impar, rank 10 so no 19-20), o que bate com o conhecimento publicado do sistema.
- **Marcos de rank-up de proficiencia (trained/expert/master/legendary)**: confirmados so no Foundry (`system.spellcasting` + nomes das class-features `Expert/Master/Legendary Spellcaster`), 1 fonte. Nao cruzado com AoN/pf2etools nesta passada (ficaria fora do orcamento de tempo); risco baixo porque sao nomes de feature literais, nao inferencia.
- **Doutrina do Clerico (Cloistered vs Warpriest)**: achado que NAO estava previsto -- confirmado em 1 fonte (Foundry, texto das 12 features de doutrina) que Warpriest e estruturalmente mais lento e nunca chega a legendary (expert@11, master@19), enquanto Cloistered segue o padrao pleno (expert@7, master@15, legendary@19). Isso muda o campo `proficiency` do Clerico de um dict simples pra um dict por doutrina -- ver `classes['cleric']['proficiency']`.
- **Focus pool nativo**: confirmado em 1 fonte (Foundry, regex sobre a class-feature dona) por classe. Todas as 11 tem 1 Focus Point nativo, EXCETO Wizard (0 -- curriculo da escola concede spell slots, nao focus) e Psychic (2 -- unico caso, usado pra 'amps' em vez de focus spells convencionais; confirmado no texto de psi-cantrips-and-amps.json).
- **Divine Font**: confirmado em **2 fontes independentes que concordam**. Foundry (`divine-font.json`, regex programatico) diz 4/5/6 nos niveis 1/5/15; a nota de rodape da propria tabela do pf2etools (`class-cleric-pc1.json`, campo `footnotes`, texto solto nao parseado por regex) diz literalmente "The number is 4 at 1st level, 5 at 5th level, and 6 at 15th level" -- duas fontes, dois arquivos diferentes, mesmo numero. **Diverge do que a maioria lembra da regra pre-remaster (fixo em 4)**; a progressao 4/5/6 e a regra remaster (Player Core) vigente.
- **Oracle -- CONFLITO real, registrado**: pf2etools (`class-oracle.json`, arquivo legado, sem variante `-pc1`) mostra o padrao generico (2 slots no rank de entrada, 3 no seguinte). O PDF (Player Core 2, p.131) mostra 3/4 -- o Oracle remaster ganhou o mesmo slot bonus que o Sorcerer ja tinha. Cruzado com Foundry (`oracle-spellcasting.json`, texto literal "cast up to three 1st-rank spells"), que confirma o PDF. Registrado em `classes['oracle']['conflitos']` -- `escolhido: "waybuilder"`, com o valor do pf2etools preservado no proprio registro, nao descartado.
- **Animista**: PDF (War of Immortals, imagem-only, p.12-13) tem a tabela completa niveis 1-20, com notacao propria 'X+Y' (pool animist + pool apparition, independentes) -- preservada como esta, sem forcar inteiro. Sem cross-check estruturado (nao esta no index.json do pf2etools); nivel 1 bate com o que ja estava confirmado via texto (Foundry + AoN) em rodada anterior.

## O que teve que ser codificado a mao (e por que)

**Nada foi codificado a mao (`prov: "codificada:manual"`) nesta extracao.** Todo numero emitido em `slots_per_level`, `proficiency`, `focus_pool` e `divine_font` vem de parsing programatico (regex/table walk/leitura de JSON) rodado em tempo de execucao contra arquivo de fonte real cacheado em `pipeline/dados_brutos/` -- inclusive `tabelas_conjuracao_pdf.json`, que e ele mesmo o produto de uma extracao anterior (leitura de PDF, nao numero chutado por este extrator).

## Classes sem cobertura (parcial ou total)

- Nenhuma das 11 classes conjuradoras ficou sem tabela de slots: o PDF cobre as 11 (10 com padrao numerico simples + Animist com notacao hibrida). Cross-check estruturado via pf2etools cobre 10 das 11 (falta so animist, que nao esta no index.json da fonte).

## Fontes legado vs. remaster (pf2etools)

O pf2etools (branch `dev`) nao tem variante `-pc2` (Player Core 2, remaster) para sorcerer/oracle/psychic/magus/summoner -- confirmado com fetch direto do `index.json` da fonte, so existem `class-<slug>.json` (arquivo unico, printing mais antigo: CRB/APG/DA/SoM) pra essas 5 classes. wizard, cleric, druid, bard e witch tem a variante `-pc1` (remaster, `remaster: true` confirmado no JSON). Isso nao afeta os NUMEROS da tabela de slots (a progressao numerica de slots por nivel nao mudou entre legado e remaster nessas classes -- so terminologia de bloodline/mystery/conscious mind mudou), mas fica registrado porque e uma divergencia real entre o pin da spec (que assume remaster como fonte preferida) e o que a fonte de fato tem disponivel.

## Portoes de qualidade (spec)

- Todo campo preenchido em `conjuracao.json` (deste extrator) tem `prov` correspondente -- portao 1 da spec.
- `conflitos` registrados: **1** classe(s) (oracle) -- divergencia PDF x pf2etools nunca e silenciada, mesma operacao que a escolha (`escolher_slots()`, mesmo formato de `comum.escolher()`).
- `grants_completos` / `requires_parseado`: nao aplicaveis a este arquivo (nao segue o envelope `kind: class-feature` da spec-base; e um arquivo auxiliar de dados tabulares referenciado por `wb:class-feature/<slug>-spellcasting`, ja emitido por `classes.py`). Ver nota de integracao abaixo.

## Nota de integracao com classes.json

Este arquivo (`saida/conjuracao.json`) e um dado **suplementar**, carregado ao lado de `saida/classes.json` (nao dentro dele -- outro agente esta mexendo nesse arquivo em paralelo, sem tocar nele). Cada entrada usa `id: "wb:class-feature/<slug>-spellcasting"`, que deve bater com o registro de class-feature de conjuracao ja emitido por `classes.py` (ex.: `wb:class-feature/wizard-spellcasting`). A reconciliacao/merge dos dois arquivos fica para uma etapa posterior do build, fora do escopo desta extracao.
