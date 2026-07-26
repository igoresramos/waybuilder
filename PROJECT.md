---
project: nethys
category: pessoal
status: planning
priority: baixa
version: 1
started: 2026-07-26
hours: 0
repo:
tags: [rpg, pathfinder-2e, dados, pipeline]
hidden: false
---

# Nethys

## Objetivo
> Base de dados canonica de Pathfinder 2e, montada pelo merge de tres fontes
> que isoladamente sao incompletas: Foundry VTT pf2e (efeitos mecanicos
> executaveis), pf2etools (pre-requisitos com referencias marcadas) e
> Archives of Nethys (texto, cobertura e ponte legado/remaster).
> E o pre-requisito do `nethys-builder`, o construtor de personagem com regras
> caseiras de multiclasse estilo D&D 5e.

## Quem usa
> Igor. Consumida pelo `nethys-builder` e por qualquer ferramenta futura de PF2e.

## Escopo
### Dentro
- 29.236 registros: classes, class features, feats, ancestralidades, herancas,
  backgrounds, magias, equipamento, armas, armaduras, escudos, arquetipos,
  familiares, companheiros, traits, pericias, divindades, dominios
- Pipeline re-executavel: `fetch -> normalizar -> reconciliar -> emitir`
- ID canonico proprio + tabela de reconciliacao entre as tres fontes
- Proveniencia por campo (qual fonte deu qual valor)
- Conversao dos ~40 tipos de Rule Element do Foundry para formato declarativo
  portatil -- o item de maior custo do projeto
- Estruturacao dos pre-requisitos de feat (hoje prosa em todas as fontes)
- Linguagem de predicado que sabe falar `class_level[X]` e `character_level`,
  mesmo que nenhuma fonte use os dois
- Base Remaster com merge curado do Legacy (11.353 pares de dedupe,
  2.294 orfaos a triar)
- SQLite como store canonico em build, emitindo JSON para o cliente

### Fora
- Bestiario, perigos, NPCs, conteudo de aventura, veiculos, regras de reino
- Qualquer regra caseira -- a base e RAW puro; houserules vivem no builder
- Interface de usuario
- Arte e tokens (licenciamento restrito, ver LESSONS)

## Estado atual
> Design de dados fechado apos pesquisa em Foundry, pf2etools, Pathbuilder 2e e
> Archives of Nethys. Spec ainda nao escrita.

## Stack
- Python ou TypeScript para o pipeline
- SQLite como store canonico em tempo de build
- Saida: JSON comprimido (indice 0,53 MB gzip / prosa 3,6 MB gzip, medidos)

## Fontes
| Fonte | Serve para | Licenca |
|---|---|---|
| `github.com/foundryvtt/pf2e` | motor mecanico, ranks como numero, progressao | Apache-2.0 (codigo) + OGL/ORC (conteudo) |
| `github.com/Pf2eToolsOrg/Pf2eTools` | pre-requisitos com referencias marcadas | MIT (codigo) + OGL/ORC (conteudo) |
| `elasticsearch.aonprd.com` (indice `aon`) | texto, busca, cobertura, ponte legado/remaster | conteudo Paizo, OGL/ORC |
