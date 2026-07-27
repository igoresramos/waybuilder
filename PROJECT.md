---
project: waybuilder
category: pessoal
status: active
priority: baixa
version: 1
started: 2026-07-26
hours: 10
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
> Depende de uma base de dados canonica -- o merge de tres fontes que
> isoladamente sao incompletas. Essa base **existe e esta fechada** desde
> 2026-07-27. Base e construtor sao um projeto so, construidos em fatias
> verticais.

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
> **A base canonica esta fechada.** Re-emitida em 2026-07-27 sob a spec v2, com
> os 10 portoes de qualidade passando. As 22 regras de multiclasse, o schema da
> base e o schema do documento de personagem seguem escritos e revisados
> adversarialmente.
>
> O pipeline roda ponta a ponta (`python3 pipeline/rodar.py`: 10 extratores ->
> reconciliar -> prosa -> fusao -> portoes) e produz **19.418 registros em 24
> kinds**, prosa em **99,1%**, 2.867 com divergencia registrada, 646 com
> `superseded_by` e **nenhum registro deletado**. Index 20,9 MB + prosa 17,9 MB.
>
> O dano que a auditoria de 26/07 achou foi corrigido e medido -- a fusao
> legado/remaster passou a usar a chave que o AoN publica (12/12 corretas na
> amostra, contra 35% antes), `traits` virou uniao de verdade
> (`two-hand-d12` de 2 para 10 registros), e entraram os kinds que faltavam:
> `ritual` 151, `relic` 122, `language` 117, `background` de 332 para 514.
> Verificacao completa em `docs/2026-07-27_reemissao-base.md`.
>
> As regras caseiras tambem foram medidas: a matriz de balanceamento
> (`docs/simulacoes/2026-07-27_balanceamento.md`, niveis 1-15, HOUSE vs RAW vs
> RAW+Free Archetype) diz que **a houserule nao quebra o jogo** -- 2 pontos
> fora da curva em 160 configuracoes, e um bonus de versatilidade fora do
> combate sem nenhuma perda medida.
>
> **O proximo passo e modelagem, nao dado**: o grafo de progressao de dois
> niveis e o predicado sabendo falar de subclasse. Depois, o front.
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
