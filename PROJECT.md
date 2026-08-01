---
project: waybuilder
category: pessoal
status: active
priority: baixa
version: 1
started: 2026-07-26
hours: 38.5
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
- PWA: client-side, offline, sem backend (nucleo que monta ficha: 0,55 MB gzip --
  eram 0,53 ate o kind `action` entrar em 31/07, +21 KB por 263 concessoes que
  antes nao pousavam em lugar nenhum)
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
> **A bancada do Pathbuilder virou o motor da triagem** (2026-07-31). Ela
> compara o que o app OFERECE num slot com o que o Pathbuilder oferece, e as 27
> classes passaram a ser comparadas de verdade -- eram 13, e as outras 14 eram
> puladas em silencio, com arquivos velhos parados em disco fingindo cobertura.
>
> **O volume da bancada e ilusao de escala.** 558 pontos viram ~74 divergencias
> distintas: cada feat aparece em media 3,3 comparacoes, porque a lista de
> dedicacoes e a mesma para toda classe. Do que sobra, a maior parte e
> diferenca de MODELO declarada (o Pathbuilder conta escolha de pericia
> pendente de outro jeito) ou recorte de fonte -- nenhum dos dois e defeito.
>
> **Fila em 19 itens e nenhum `alta`.** Aberto de verdade: 69 e 107, que estao
> no mesmo bloqueio (a mae que concederia as features usa `GrantItem` com UUID
> dinamico, e o extrator pula os 163 casos assim, corretamente), e 84, que agora
> pede triagem dos 57 "so nosso". Bloqueados por coisa que nao existe: 68
> (oraculo de em que nivel cada aumento foi gasto), 10 (o importador em si) e 96
> (consumidor de `acesso`). 31 (i18n) fica por ultimo, decisao do Igor.

> **App de pe e verificado em quatro camadas** (2026-07-29): 9 portoes de
> pipeline, 132 assercoes do oraculo Python, 113 testes do porte TS e a checagem
> no navegador (`app/verificacao/`, dois scripts). A quarta entrou porque as
> tres primeiras passaram verdes sobre uma base que oferecia a mesma causa do
> Campeao duas vezes na tela.
>
> **Decisao de 2026-07-29: manter todo o conteudo legado.** Medido: as tres
> pilhas da triagem (971 removidos, 339 renomeados, 5.690 intocados) estao
> todas na base, e a fusao legacy/remaster guarda o nome antigo em `aliases`. A
> busca do app acha pelo nome antigo.
>
> **A conjuracao aparece na ficha** desde 2026-07-29 -- as duas rotas. A de
> arquetipo era inexistente (13 dedicacoes prometiam e nao entregavam) e a de
> CLASSE era calculada e nunca mostrada: o bloco so existia numa tela morta.
>
> **Companheiro concedido por feat funciona ponta a ponta** desde 2026-07-29:
> pegar `Animal Companion` abre o slot da especie, e a ficha do bicho sai
> derivada (spec `2026-07-29-companheiro-concedido.md`). Familiar, eidolon e
> companheiro construct/undead seguem como divida declarada em relatorio.
>
> Design fechado e **base canonica re-emitida**. As 22 regras de multiclasse, o
> schema da base e o schema do documento de personagem estao escritos, revisados
> adversarialmente e commitados.
>
> **19.705 registros em 54 kinds** (24 originais + 28 de sub-escolha promovidos a
> kind proprio + `tactic` e `class-kit`, que so o censo do AoN acusou), prosa em
> **99,0%** (191 sem prosa), 1.990 com divergencia registrada, 125 desmembrados
> de colisao de identidade.
>
> Re-emitida em 2026-07-27 com o dump completo do AoN (43.686 docs): **os nove
> portoes passam**, inclusive o 7 na fase pre-fusao. Spells com `level` foram de
> 22 para 1.655, `traits: null` zerou, e os desmembrados cairam de 310 para 125
> -- os 185 a menos eram duplicata criada a partir de doc legado.
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
> **E agora aplica o efeito das escolhas, nao so as registra (2026-07-27).** A
> cadeia de `grant_feat`/`grant_item` com alvo estatico e aplicada -- entao a
> dedicacao de arquetipo entrega o que promete (HP, proficiencia, feat e
> class-feature concedidos) --, o gasto de slot e confrontado com o slot, as
> duas regras RAW do trait `dedication` sao checadas e o aumento de pericia por
> nivel existe. Alvo dinamico continua sinalizado como pendente, que e a
> distincao que o app precisa.
>
> **E responde a pergunta que a TELA faz (2026-07-27).** `slots_abertos()` diz o
> que falta escolher (feat, subclasse, aumento de pericia, boost de atributo) e
> `candidatos(slot, em)` diz o que cabe em cada slot -- recortando pelo tipo que
> o slot aceita, com o requisito so ordenando e marcando. Era a lacuna que
> impedia comecar o front: `disponiveis("feat")` devolvia os 6.273 feats da base.
>
> **O payload do app e um artefato proprio.** O indice de build carrega
> proveniencia, xref e conflitos, que o construtor nunca le. `emitir_app.py`
> corta: 1,04 MB gzip no indice completo e **0,49 MB no nucleo que monta ficha**
> -- abaixo do alvo de 0,53 do projeto. As 20 fichas de exemplo derivam
> IDENTICAS nos dois indices.
>
> Derivacao de ficha de nivel 20: **0,30 ms**. Teste de carga de 285 fichas
> (27 classes x 5 niveis + 50 combinacoes de multiclasse): zero excecoes,
> determinismo e invariantes limpos.
>
> **97 assercoes** no oraculo Python, **107** no porte TS.
>
> **O APP EXISTE (2026-07-28).** Vite + React, PWA offline, sem backend. Monta
> um personagem do zero, nivel a nivel, com Free Archetype. O motor foi portado
> para TypeScript e as 20 fichas de exemplo derivam IDENTICAS nas duas
> implementacoes -- o Python fica como oraculo. Carga: 76 KB de app + 511 KB do
> nucleo; a prosa entra sob demanda.
>
> Layout em DUAS COLUNAS -- build a esquerda, ficha viva a direita --, refeito a
> partir do Pathbuilder que o Igor usa, depois de a primeira versao (tres abas
> separadas) nao servir. O picker e um modal com filtros e o texto completo do
> item.
>
> **Validado em quatro frentes paralelas (2026-07-27).** As 226 dedicacoes passam
> pelo motor sem uma excecao; 1.440 documentos malformados derivam sem explodir;
> embaralhar as escolhas nao muda a ficha. O review adversarial achou -- e o mesmo
> dia consertou -- uma regressao com personagem de nivel 0 (o estado inicial do
> construtor), o requisito circular criado ao aplicar grants, e a dependencia de
> ordem em `ordem_de_classe`.
>
> **O gargalo mudou de lugar: agora e DADO, nao motor.** Os quatro achados que
> mais custam sao de base -- 122 feats com gate de nivel travado numa classe so
> (`Reach Spell` inalcancavel para Mago), o eixo `outras-opcoes` como balaio em 25
> das 27 classes, 476 alvos de `grant_feat` sem resolver em background, e a
> ausencia de higiene de atributo (ficha sem boost declarado sai com tudo 10 e
> nenhum aviso). Itens 69 a 75.
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
> **Sessao de 2026-07-27 (05:41-07:03).** As 11 classes conjuradoras tem tabela
> de slots completa -- o Animist, ultimo buraco, foi recuperado do campo
> `markdown` do AoN, que o extrator nunca lia. Tres regras novas implementadas e
> testadas: **17b** (teto do que cria criatura: `summon` + `incarnate`, 37
> magias, mais companheiro e eidolon), **21** afiada de principio para invariante
> varrido nos 204 pares, e **23** (exclusao mutua entre nivel de classe e
> dedicacao da mesma classe). Ficha do companheiro em RAW puro, com maturidade
> derivada dos feats.
>
> Criado o **portao 8** contra perda silenciosa de artefato, depois de uma perda
> real: dump de fonte reproduzivel por pin fica em `dados_brutos/` e fora do git;
> tudo que exigiu leitura ou arbitragem humana vai em `dados_derivados/`, que e
> versionado.
>
> **PROXIMO PASSO, decidido com o Igor:** o app e para construir o personagem
> INTEIRO, como o Pathbuilder -- todos os numeros na ficha. Fica de fora so
> retraining e arbitragem de mesa. Nessa ordem:
> 1. **Slots abertos, genericos** -- 243 dos 6.044 feats (4%) abrem escolha, e a
>    cadeia de desbloqueio chega a profundidade 4. Slot tem de ser DERIVADO do
>    estado a cada escolha, nunca arvore estatica. Primeiro caso de teste pronto
>    e sem dado novo: o beneficio por especializacao do companheiro
>    (Ambusher/Bully/Daredevil/Racer/Tracker/Wrecker)
> 2. **Familiar e eidolon** -- so tem nivel e o cap da 17b. O eidolon usa
>    estatisticas do proprio Summoner, entao a ficha dele nao e independente
> 3. **Runas** -- potencia e impacto (`+1 striking longsword`)
> 4. **Interpretador parcial de Rule Elements** -- dano condicional das
>    subclasses (itens 42/43). Dano de rage e numero de ficha
>
> **Aberto para decisao do Igor:**
> - a regra 17b vale para slot de ARQUETIPO? A regra 18 diz que Free Archetype
>   roda RAW puro, mas isso deixa a rota gratuita passar a comprada em alguns
>   niveis. A spec nao decide
> - o piso da regra 21 achata uma faixa: no personagem 20, os niveis de classe 1
>   a 12 dao todos rank 8. Se o "deveria ser ainda mais forte" virar numero, e
>   ai que ele entra
> - itens 41 (tradicao por subclasse em Sorcerer/Summoner/Witch e prosa) e 42
>   (8 eixos de subclasse sem efeito)
>
> **Comece por `README.md`** -- ele e o ponto de retomada.


## Stack
- Python ou TypeScript para o pipeline
- SQLite como store canonico em tempo de build
- Saida: JSON comprimido (nucleo 0,55 MB gzip / prosa 3,6 MB gzip, medidos)
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
