---
project: waybuilder
category: pessoal
status: planning
priority: baixa
version: 1
started: 2026-07-26
hours: 6.5
repo:
tags: [rpg, pathfinder-2e, dados, pipeline, pwa, houserules]
hidden: false
---

# Waybuilder

## Objetivo
> Construtor de personagem de Pathfinder 2e com regra caseira de multiclasse ao
> estilo D&D 5e -- niveis de classe que se dividem, em vez dos arquetipos de
> dedicacao do PF2e oficial. O nome e piada com o Pathbuilder 2e, o app que ele
> substitui, e ecoa o Wayfinder, a bussola da Pathfinder Society.
>
> Depende de uma base de dados canonica que hoje nao existe: o merge de tres
> fontes que isoladamente sao incompletas. Base e construtor sao um projeto so,
> construidos em fatias verticais.

## Quem usa
> Igor e a mesa dele.

## Escopo
### Dentro

**Componente 1 -- base canonica (RAW puro, sem houserule)**
- ~29.236 registros: classes, class features, feats, ancestralidades, herancas,
  backgrounds, magias, equipamento, armas, armaduras, escudos, arquetipos,
  familiares, companheiros, traits, pericias, divindades, dominios
- Pipeline re-executavel: `fetch -> normalizar -> reconciliar -> emitir`
- ID canonico + tabela de reconciliacao entre as tres fontes
- Proveniencia por campo (qual fonte deu qual valor)
- Conversao dos ~40 tipos de Rule Element do Foundry para formato declarativo
  portatil -- o item de maior custo do projeto
- Estruturacao dos pre-requisitos de feat (hoje prosa em todas as fontes)
- Base Remaster com merge curado do Legacy (11.353 pares de dedupe,
  2.294 orfaos a triar)
- SQLite como store canonico em build, emitindo JSON para o cliente

**Componente 2 -- construtor**
- Linguagem de predicado que fala `class_level[X]` **e** `character_level`.
  Nenhuma fonte usa os dois; e onde a houserule inteira mora
- Modelo de tres conceitos: `Entry` (tudo e linha da mesma tabela), `Slot`
  (buraco a preencher, gerado pela progressao), `Actor` (o personagem -- e
  tambem cada pet, familiar, companheiro, com a mesma engine)
- Estatisticas derivadas por `fold` sobre os efeitos concedidos
- Duas camadas na mesma tabela: mecanizada (o app calcula) e prosa (o jogador
  controla na mao), separadas por flag
- Um componente de picker reusado em todo slot
- PWA: client-side, offline, sem backend (indice cabe em 0,53 MB gzip)
- Free Archetype sempre ligado, rodando RAW

**Fatias verticais** -- cada uma vai da fonte ate a tela
1. Guerreiro + Mago, niveis 1-5, uma ancestralidade (~300 registros)
2. Todas as classes, niveis 1-20
3. Arquetipos e Free Archetype
4. Itens, companheiros, ficha completa

### Fora
- Bestiario, perigos, NPCs, conteudo de aventura, veiculos, regras de reino
- Retraining -- resolvido na mesa, nao no app
- Arte e tokens (licenciamento restrito, ver LESSONS)
- Modo de jogo / encontro / tracking de combate

## Estado atual
> Design fechado e **base canonica montada**. As 22 regras de multiclasse, o
> schema da base e o schema do documento de personagem estao escritos, revisados
> adversarialmente e commitados.
>
> O pipeline roda ponta a ponta (7 extratores -> reconciliar -> prosa -> fusao)
> e produz **18.176 registros em 21 kinds**, prosa em 100% (17.866/17.866),
> 2.299 com divergencia entre fontes registrada, 597 pares Legacy<->Remaster
> fundidos, zero par nao unido. Index 15,2 MB + prosa 16,7 MB.
> Resíduo unico: 6 registros sem `license` (portao de qualidade 5 falhando).
>
> **A base NAO esta fechada. A auditoria de 2026-07-26 achou perda de dado
> real** -- a fusao Legacy<->Remaster deletou 597 registros decidindo por
> similaridade de prosa, e so 35% das fusoes estavam certas
> (`wb:equipment/aeon-stone` engoliu 24 pedras distintas). Reverter e refazer
> com o `remaster_id` do AoN e o item mais urgente da lista.
>
> **Os outros defeitos que precisam de re-emissao:**
> 1. `traits` usava precedencia e devia ser uniao -- 88% dos conflitos, com
>    perda de dado real (`two-hand-d12` virava `two-hand`) e injecao de nome
>    legado de ancestria numa base remaster-first. Spec ja corrigida, mapa de
>    normalizacao pronto em `pipeline/normalizacao_traits.json`
> 2. `wb:<kind>/<slug>` assume nome unico por kind -- 5 colisoes confirmadas,
>    59 candidatos levantados
> 3. Faltava o kind `ritual` inteiro -- extrator escrito, 151 registros em
>    `pipeline/saida/rituais.json`, ainda **fora** de `ENTRADA` do reconciliador
>
> Falta o construtor. Depois da re-emissao, os proximos sao de modelagem: o
> grafo de progressao de dois niveis e o predicado sabendo falar de subclasse.
>
> **Comece por `README.md`** -- ele e o ponto de retomada.


## Stack
- Python ou TypeScript para o pipeline
- SQLite como store canonico em tempo de build
- Saida: JSON comprimido (indice 0,53 MB gzip / prosa 3,6 MB gzip, medidos)
- Front: PWA, sem backend

## Fontes
| Fonte | Serve para | Licenca |
|---|---|---|
| `github.com/foundryvtt/pf2e` | motor mecanico, ranks como numero, progressao | Apache-2.0 (codigo) + OGL/ORC (conteudo) |
| `github.com/Pf2eToolsOrg/Pf2eTools` | pre-requisitos com referencias marcadas | MIT (codigo) + OGL/ORC (conteudo) |
| `elasticsearch.aonprd.com` (indice `aon`) | texto, busca, cobertura, ponte legado/remaster | conteudo Paizo, OGL/ORC |

## Interoperabilidade
O JSON de export do Pathbuilder 2e virou padrao de fato (20+ parsers open
source). Emitir esse formato no que couber, com bloco de extensao para o que
nao cabe -- `class` e `level` la sao valor unico e nao expressam multiclasse.
