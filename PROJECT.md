---
project: waybuilder
category: pessoal
status: planning
priority: baixa
version: 1
started: 2026-07-26
hours: 7
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
> Design fechado e **base canonica re-emitida**. As 22 regras de multiclasse, o
> schema da base e o schema do documento de personagem estao escritos, revisados
> adversarialmente e commitados.
>
> **19.738 registros em 52 kinds** (24 originais + 28 de sub-escolha promovidos a
> kind proprio), prosa em **99,2%** (166 sem prosa), 1.550 com
> divergencia registrada, 281 desmembrados de colisao de identidade.
>
> A re-emissao de 2026-07-26 fechou os cinco defeitos da auditoria: a fusao
> Legacy<->Remaster passou a usar o `remaster_id` do AoN em vez de similaridade
> de prosa (**586 registros deletados foram recuperados**; `aeon-stone` voltou de
> 17 para 40); `traits` virou uniao; as colisoes de identidade foram
> desmembradas; entraram `ritual`, `relic`, `language` e 168 backgrounds que
> faltavam; e os 7 portoes de qualidade existem de fato.
>
> **Antes disso, um bloqueio nao registrado precisou ser resolvido:** 7 dos 10
> extratores apontavam para um clone do Foundry num diretorio de scratchpad de
> sessao (`/tmp/...`) que ja nao existia. O pipeline nao rodava, e re-executar
> produzia uma base menor e mono-fonte **sem erro nenhum**. Fonte refeita dentro
> de `dados_brutos/`, com `buscar_fontes.sh` e `dump_aon.py` reconstruindo as
> duas maiores.
>
> **O motor ja monta ficha COMPLETA (2026-07-27).** HP, AC (com cap de DEX,
> escudo, penalidade), ataque e dano por arma, proficiencias, identidade de
> classe, conjuracao e a lista do que pode pegar. Validado contra os iconics da
> Paizo: **117 de 129 batem (91%)**.
>
> **(historico)** Fatia vertical 1 fechada: `motor/`
> implementa 11 das 22 regras e imprime `Guerreiro 3 / Mago 2` completo, com 24
> assercoes de teste travando cada regra. A houserule aparece viva -- Mago 2 num
> personagem 5 tem os slots de um Mago 2 e conjura no rank 3; Mago 5 puro ganha
> elevacao zero, que e o comportamento correto.
>
> Fechados junto: o grafo de progressao de dois niveis (item 2 -- as 28
> categorias de sub-escolha do AoN viraram kind proprio, e a progressao agora
> separa concessao de escolha usando `system.items` do Foundry como fonte
> autoritativa) e a tabela de slots de conjuracao (item 14).
>
> **Os tres itens de modelagem fecharam** (gate de nivel, subclasse no predicado,
> efeito unificado). `class_level` foi de 79 para 1.932 registros.
>
> **PROXIMO PASSO, decidido com o Igor:** o app e para construir o personagem
> INTEIRO, como o Pathbuilder -- todos os numeros na ficha. Fica de fora so
> retraining e arbitragem de mesa. Nessa ordem:
> 1. **Atores** -- companheiro, familiar e eidolon com stats proprios. A spec ja
>    diz que e o mesmo motor com menos slots; hoje o motor so verifica que
>    existem
> 2. **Runas** -- potencia e impacto (`+1 striking longsword`). O campo
>    `potencia` ja e lido, falta modelar runa como item
> 3. **Interpretador parcial de Rule Elements** -- para o dano condicional das
>    subclasses (item 42/43). Deixou de ser "fora de escopo": dano de rage e
>    numero de ficha
>
> **Aberto para decisao:** itens 39 (regra 17 fura em Magus/Summoner), 41
> (tradicao por subclasse em Sorcerer/Summoner/Witch e prosa), 42 (8 eixos de
> subclasse sem efeito).
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
