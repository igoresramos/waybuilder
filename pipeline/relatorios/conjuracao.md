# Relatorio -- extrator de conjuracao (spell slots)

Pin do Foundry: `87f9e5028baaa10b70fdc766260b7886def17e04`

## Cobertura

- Classes cobertas: **11** (wizard, cleric, druid, sorcerer, bard, witch, oracle, psychic, animist, magus, summoner)
- Tabela de slots (1-20, todos os ranks) confirmada via pf2etools: **10** classes (wizard, cleric, druid, sorcerer, bard, witch, oracle, psychic, magus, summoner)
- Sem cobertura de tabela completa: **1** (animist (parcial -- so nivel 1-2, ver relatorio))

## De onde veio cada pedaco do dado, por classe

| Classe | tradition/type | proficiencia | focus pool | slots/nivel | extra |
|---|---|---|---|---|---|
| Wizard | foundry (regex sobre descricao da class-feature de conjuracao) | foundry (system.spellcasting + items{} 'Expert/Master/Legendary Spellcaster') | foundry (regex sobre a class-feature dona do focus pool nativo) | pf2etools (class-wizard-pc1.json, tabela 'Wizard Spells per Day') | - |
| Cleric | foundry (regex sobre descricao da class-feature de conjuracao) | foundry (regex sobre as 12 class-features de doutrina first..final-doctrine-{cloistered-cleric,warpriest}, ver conjuracao.md) | foundry (regex sobre Domain Initiate, feat granted pela Primeira Doutrina) | pf2etools (class-cleric-pc1.json, tabela 'Cleric Spells per Day') | divine_font: foundry (divine-font.json) |
| Druid | foundry (regex sobre descricao da class-feature de conjuracao) | foundry (system.spellcasting + items{} 'Expert/Master/Legendary Spellcaster') | foundry (regex sobre a class-feature dona do focus pool nativo) | pf2etools (class-druid-pc1.json, tabela 'Druid Spells per Day') | - |
| Sorcerer | foundry (regex sobre descricao da class-feature de conjuracao) | foundry (system.spellcasting + items{} 'Expert/Master/Legendary Spellcaster') | foundry (regex sobre a class-feature dona do focus pool nativo) | pf2etools (class-sorcerer.json, tabela 'Sorcerer Spells per Day') | - |
| Bard | foundry (regex sobre descricao da class-feature de conjuracao) | foundry (system.spellcasting + items{} 'Expert/Master/Legendary Spellcaster') | foundry (regex sobre a class-feature dona do focus pool nativo) | pf2etools (class-bard-pc1.json, tabela 'Bard Spells per Day') | - |
| Witch | foundry (regex sobre descricao da class-feature de conjuracao) | foundry (system.spellcasting + items{} 'Expert/Master/Legendary Spellcaster') | foundry (regex sobre a class-feature dona do focus pool nativo) | pf2etools (class-witch-pc1.json, tabela 'Witch Spells per Day') | - |
| Oracle | foundry (regex sobre descricao da class-feature de conjuracao) | foundry (system.spellcasting + items{} 'Expert/Master/Legendary Spellcaster') | foundry (regex sobre a class-feature dona do focus pool nativo) | pf2etools (class-oracle.json, tabela 'Oracle Spells per Day') | - |
| Psychic | foundry (regex sobre descricao da class-feature de conjuracao) | foundry (system.spellcasting + items{} 'Expert/Master/Legendary Spellcaster') | foundry (regex sobre a class-feature dona do focus pool nativo) | pf2etools (class-psychic.json, tabela 'Psychic Spells per Day') | - |
| Animist | aon (campo 'tradition': ['Divine']) | foundry (system.spellcasting + items{} 'Expert/Master/Legendary Spellcaster') | foundry (regex sobre animist-apparition-spellcasting.json, secao 'Vessel Spells') | NAO COBERTO -- ver slots_not_covered | cobertura parcial -- ver secao dedicada abaixo |
| Magus | foundry (regex sobre descricao da class-feature de conjuracao) | foundry (system.spellcasting + items{} 'Expert/Master/Legendary Spellcaster') | foundry (regex sobre a class-feature dona do focus pool nativo) | pf2etools (class-magus.json, tabela 'Magus Spells per Day') | - |
| Summoner | foundry (regex sobre descricao da class-feature de conjuracao) | foundry (system.spellcasting + items{} 'Expert/Master/Legendary Spellcaster') | foundry (regex sobre a class-feature dona do focus pool nativo) | pf2etools (class-summoner.json, tabela 'Summoner Spells per Day') | - |

## Descoberta principal: onde a tabela numerica REALMENTE vive

O relatorio de `classes.py` (extrator irmao) registrou que a tabela de slots "fica em rule elements, nao decodificados nesta passada". Investigado a fundo para esta extracao: **isso nao procede**. Nenhuma class-feature de conjuracao (Wizard Spellcasting, Cleric Spellcasting, Sorcerer Spellcasting etc.) tem `system.rules` com dado numerico de slots -- a lista `rules[]` dessas features ou esta vazia, ou so tem `GrantItem`/`ChoiceSet` para mecanica auxiliar (ex.: escolha heal/harm do Divine Font). O Foundry carrega a tabela em tempo de execucao via codigo TypeScript (nao dado), nao emite ela em nenhum arquivo JSON dos compendios. A tabela numerica estruturada **so existe no pf2etools**, como um bloco `{"type": "table", "name": "<Classe> Spells per Day"}` dentro de `classFeature[]`/`subclassFeature[]` -- ver `find_spells_per_day_table()` em conjuracao.py.

## Numeros confirmados em 2+ fontes vs. 1 fonte so

- **Slots por nivel/rank (a tabela inteira)**: confirmados em **1 fonte so** (pf2etools) para as 10 classes com tabela. Nao ha uma segunda fonte estruturada para cruzar -- nem Foundry nem AoN materializam a tabela numerica (ver secao acima). Validado indiretamente por consistencia interna: Wizard/Cleric/Druid/Bard/Witch/Oracle tem a MESMA progressao (padrao de conjurador pleno: cantrips=5, 2 slots no rank 1, abre rank novo em nivel impar, rank 10 so no 19-20), o que bate com o conhecimento publicado do sistema.
- **Marcos de rank-up de proficiencia (trained/expert/master/legendary)**: confirmados so no Foundry (`system.spellcasting` + nomes das class-features `Expert/Master/Legendary Spellcaster`), 1 fonte. Nao cruzado com AoN/pf2etools nesta passada (ficaria fora do orcamento de tempo); risco baixo porque sao nomes de feature literais, nao inferencia.
- **Doutrina do Clerico (Cloistered vs Warpriest)**: achado que NAO estava previsto -- confirmado em 1 fonte (Foundry, texto das 12 features de doutrina) que Warpriest e estruturalmente mais lento e nunca chega a legendary (expert@11, master@19), enquanto Cloistered segue o padrao pleno (expert@7, master@15, legendary@19). Isso muda o campo `proficiency` do Clerico de um dict simples pra um dict por doutrina -- ver `classes['cleric']['proficiency']`.
- **Focus pool nativo**: confirmado em 1 fonte (Foundry, regex sobre a class-feature dona) por classe. Todas as 11 tem 1 Focus Point nativo, EXCETO Wizard (0 -- curriculo da escola concede spell slots, nao focus) e Psychic (2 -- unico caso, usado pra 'amps' em vez de focus spells convencionais; confirmado no texto de psi-cantrips-and-amps.json).
- **Divine Font**: confirmado em **2 fontes independentes que concordam**. Foundry (`divine-font.json`, regex programatico) diz 4/5/6 nos niveis 1/5/15; a nota de rodape da propria tabela do pf2etools (`class-cleric-pc1.json`, campo `footnotes`, texto solto nao parseado por regex) diz literalmente "The number is 4 at 1st level, 5 at 5th level, and 6 at 15th level" -- duas fontes, dois arquivos diferentes, mesmo numero. **Diverge do que a maioria lembra da regra pre-remaster (fixo em 4)**; a progressao 4/5/6 e a regra remaster (Player Core) vigente.
- **Animista**: ver secao dedicada abaixo -- unica classe sem tabela completa confirmada.

## O que teve que ser codificado a mao (e por que)

**Nada foi codificado a mao (`prov: "codificada:manual"`) nesta extracao.** Todo numero emitido em `slots_per_level`, `proficiency`, `focus_pool` e `divine_font` vem de parsing programatico (regex/table walk) rodado em tempo de execucao contra arquivo de fonte real cacheado em `pipeline/dados_brutos/`. Onde a fonte simplesmente nao tinha o dado (Animista, tabela completa), a saida fica `None`/parcial em vez de um numero inventado.

## Classes sem cobertura (parcial ou total)

- **animist**: proficiencia, tradicao, tipo e focus pool cobertos (fonte: Foundry). Tabela de slots por nivel **NAO coberta** -- so os dois pontos de nivel 1 e 2 citados em texto (2 fontes concordantes no nivel 1: Foundry + AoN). Motivo: animista nao esta no index.json do pf2etools (`data/class/index.json`, checado com fetch direto -- 404 pra `class-animist(-pc1/-pc2).json`), e nem Foundry nem AoN materializam a tabela numerica em nenhum campo (so referenciam 'Animist Spells per Day' como nome de tabela, sem os valores).
- Nenhuma outra classe das 11 pedidas ficou descoberta -- wizard, cleric, druid, sorcerer, bard, witch, oracle, psychic, magus e summoner tem a tabela 1-20 completa.

## Fontes legado vs. remaster (pf2etools)

O pf2etools (branch `dev`) nao tem variante `-pc2` (Player Core 2, remaster) para sorcerer/oracle/psychic/magus/summoner -- confirmado com fetch direto do `index.json` da fonte, so existem `class-<slug>.json` (arquivo unico, printing mais antigo: CRB/APG/DA/SoM) pra essas 5 classes. wizard, cleric, druid, bard e witch tem a variante `-pc1` (remaster, `remaster: true` confirmado no JSON). Isso nao afeta os NUMEROS da tabela de slots (a progressao numerica de slots por nivel nao mudou entre legado e remaster nessas classes -- so terminologia de bloodline/mystery/conscious mind mudou), mas fica registrado porque e uma divergencia real entre o pin da spec (que assume remaster como fonte preferida) e o que a fonte de fato tem disponivel.

## Portoes de qualidade (spec)

- Todo campo preenchido em `conjuracao.json` (deste extrator) tem `prov` correspondente -- portao 1 da spec.
- Nao ha `conflitos` registrados: como so uma fonte materializa a tabela numerica, nao houve dois valores pra comparar campo a campo.
- `grants_completos` / `requires_parseado`: nao aplicaveis a este arquivo (nao segue o envelope `kind: class-feature` da spec-base; e um arquivo auxiliar de dados tabulares referenciado por `wb:class-feature/<slug>-spellcasting`, ja emitido por `classes.py`). Ver nota de integracao abaixo.

## Nota de integracao com classes.json

Este arquivo (`saida/conjuracao.json`) e um dado **suplementar**, carregado ao lado de `saida/classes.json` (nao dentro dele -- outro agente esta mexendo nesse arquivo em paralelo, sem tocar nele). Cada entrada usa `id: "wb:class-feature/<slug>-spellcasting"`, que deve bater com o registro de class-feature de conjuracao ja emitido por `classes.py` (ex.: `wb:class-feature/wizard-spellcasting`). A reconciliacao/merge dos dois arquivos fica para uma etapa posterior do build, fora do escopo desta extracao.
