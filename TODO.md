---
















# Criterio de prioridade (definido 2026-07-29):
#   alta  = bloqueia outro item OU entrega numero/opcao errada na ficha do jogador
#   media = buraco de conteudo
#   baixa = polimento
# `date` = data da ultima VERIFICACAO do item, nao da criacao. Todos os
# itens abertos foram medidos contra o codigo e a base em 2026-07-29
# (relatorio: docs/2026-07-29_auditoria-todo.md).
# Os 55 itens concluidos vivem em docs/2026-07-29_todo-concluidos.md.
project: waybuilder
items:
- desc: 'SOBRA DA FASE 3 FECHADA 2026-07-30 (spec specs/2026-07-30-bonus-de-item-equipado.md). O item
    pedia `ac` e `strike-damage`; na base canonica `ac` tinha 34 grants e ZERO incondicionais. Contando
    selector em LISTA apareceram 6, e ao aplicar veio o numero real: `_bonus_incondicionais` NAO LIA O
    INVENTARIO. Sao 293 grants incondicionais aplicaveis em equipment (261), armor (11), shield (11) e
    weapon (10) -- religion 26, intimidation 25, diplomacy 22, athletics 20, e o ac 6 -- todos em selectors
    que o motor ja somava. Item de +1 em Furtividade nao mudava Furtividade. A CA passou a DISPUTAR (`_melhor_por_tipo`)
    porque o item_bonus da armadura tambem e bonus de item. SEGUNDO DEFEITO: o contador anti-perda nunca
    contou -- `_velocidade` reatribuia `bonus_ignorados` e apagava o que os passos anteriores gravaram;
    agora memoizado. DANO E ATAQUE RECUSADOS COM NUMERO: 6 ocorrencias em 6 seletores + 34 dinamicos +
    3 formulas, mesmo criterio do ItemAlteration. ATORES RESOLVIDOS 2026-07-30 (commit 5afe8c06d, spec
    specs/2026-07-30-familiar-e-eidolon-concedidos.md): 16 registros concedem familiar e 2 concedem eidolon
    (eram 0 e 0); `candidatos()` deixou de devolver os 6.273 feats para o slot `familiar`. SOBRA SO O
    STAT BLOCK, e ele depende de FONTE que nao temos: `familiar-specific` nao tem um unico campo numerico,
    `eidolon` so tem velocidade, nao existe tabela de progressao, e a pagina de regras `Familiars` do
    AoN tem 796 caracteres so de conceito. Em PF2e o familiar deriva os numeros do personagem -- derivar
    sem a regra na mao seria inventar. PROXIMO PASSO: conseguir a fonte das estatisticas.'
  id: 43
  date: '2026-07-29'
  priority: alta
- desc: 'SOBRA DO ITEM 42, FECHADO 2026-07-30 (spec specs/2026-07-30-dano-de-furia.md). O que SOBROU do
    eixo `instinct` esta declarado com numero na spec e nao foi feito. (a) `ragingResistance` -- `3 +
    con.mod`, `8 + con.mod` com Unstoppable Juggernaut, mais o tipo de dano resistido por instinto: mesmo
    achado e mesmo tamanho do dano de furia, mas mexe em `_resistencias`, que tem gramatica propria. A
    MEDICAO JA ESTA PRONTA nos rule elements `Resistance` dos nove instintos. (b) os 30 `Strike` do Animal
    Instinct, um por animal -- conceder ataque desarmado e outra familia, sem consumidor na ficha hoje.
    (c) `item:trait:agile` cortando o dano de furia pela metade (2 regras, `mode: multiply 0.5`), `Effect:
    Share Rage` / `Guard''s Fury` / `Mighty Rage` (3 regras de efeito ativo) e o degrau `target:caster`
    do Superstition (4/8/16): todos por ARMA ou por ALVO no momento da rolagem, fora da ficha. (d) os
    22 `flat_modifier` condicionais em seletor de dano ja entram em `condicionais`, marcados e nao somados.'
  id: 101
  date: '2026-07-30'
  priority: baixa
- desc: 'ACHADO LATERAL DA MEDICAO DO ITEM 46 (2026-07-30, docs/2026-07-30_corte-multiclasse.md). Tres
    defeitos independentes do corte, todos da familia da licao do item 18 (homonimo resolvido para o
    registro errado). (1) HOMONIMO CLASSE x ARQUETIPO: 10 registros com `requires`/`grants` apontando
    para o feat de ARQUETIPO tendo o `class-feature` de mesmo nome ao lado -- `efficient-alchemy` ->
    `wb:feat/advanced-alchemy` com `wb:class-feature/advanced-alchemy` na base; idem `shield-of-reckoning`
    e `swift-retribution` -> `champions-reaction`; idem `wb:class-feature/alchemy` CONCEDENDO
    `wb:feat/quick-alchemy` (o do arquetipo). (2) ATRIBUICAO DE ARQUETIPO COM BURACO: 7 feats com trait
    `archetype` e campo `archetype` vazio, identificaveis porque o `requires` cita uma dedicacao de
    multiclasse. (3) 18 arquetipos sem feat de dedicacao na base, ou seja sem porta de entrada. Medicao
    reproduzivel em docs/medicoes/medir_corte_multiclasse.py'
  id: 100
  date: '2026-07-30'
  priority: media
- desc: 'RE-MEDIDO 2026-07-29, e o item mudou de gravidade: e COSMETICO, nao numero errado. Contra o dump
    do AoN, 65 class-features nao existem na base por nome (nem como alias -- conferido, licao do item
    18). Das 65, 35 sao LINHAS DE TABELA DE PROGRESSAO (''ability boost'', ''ancestry feat'', ''alchemist
    feats'') que o nosso modelo representa como SLOT e nao como feature -- ausencia correta. As outras
    30 sao features de verdade: anathema, champions code, debilitating strikes, divine smite, exalt, familiar,
    great fortitude, hexes, incredible senses, lightning reflexes, premonition''s reflexes, quick rage,
    slippery mind, trackless step, vigilant senses, wild empathy, wild stride, e as spellcasting por tradicao.
    A PERGUNTA QUE DECIDE: o efeito delas ja chega na ficha? SIM. Medido: Campeao fort trained->expert(nv9)->master,
    Ladino reflex expert->master->legendary(nv17), percepcao idem -- a progressao da classe ja entrega
    o upgrade que `Lightning Reflexes` e `Vigilant Senses` representam. O que falta e a LINHA com o nome
    da feature na ficha, que para um construtor tem valor (o jogador quer ver ''Lightning Reflexes'' no
    nivel 9), mas nao e numero errado. Prioridade rebaixada.'
  id: 55
  date: '2026-07-29'
  priority: baixa
- desc: 'PARCIAL, re-medido 2026-07-29 (auditoria). O vies 1 (rank lido de system.skills em vez de trainedSkills.value)
    JA foi corrigido -- e o proprio conteudo do item. SOBRA o vies 2: falta o oraculo de EM QUE NIVEL
    cada aumento de pericia foi gasto, e sem ele a metrica de 62,9% nao mede a qualidade do motor. Falta
    o oraculo, nao o motor. || TEXTO ORIGINAL: CUIDADO COM A METRICA DE PERICIA: os 62,4% (1.287 de 2.064)
    NAO medem a qualidade do motor. Dois vieses, os dois descobertos ao construir a medicao. (1) `system.skills.<pericia>.rank`
    do ator do Foundry NAO e o rank final -- so registra escolha discricionaria; o treino automatico de
    classe vive em `trainedSkills.value` DENTRO do item de classe do mesmo ator. Provado com a Amiri:
    `athletics` sai ausente de `system.skills` e presente em `trainedSkills.value` do item Barbarian.
    O oraculo corrigido une as duas fontes (`max(rank explicito, 1 se automatico)`), as duas do proprio
    ator, nenhuma da nossa base. (2) Mesmo corrigido, falta o oraculo de EM QUE NIVEL cada aumento foi
    gasto, entao o motor comeca perdendo por construcao. Enquanto o item 67 nao entrar, este numero mede
    a lacuna, nao o motor. Os 2 casos em que o motor da rank MAIOR foram investigados um a um e o motor
    esta CERTO: Droven (Inventor) em crafting, pela class-feature `Expert Overdrive`, cujo texto RAW diz
    ''You become an expert in Crafting'' -- e o ator do Foundry que nao persiste bump automatico de class
    feature'
  id: 68
  date: '2026-07-29'
  priority: media
- desc: 'TERCEIRA hipotese do item tambem NAO se confirma (2026-07-30). O proprio item propunha: "para
    cada opcao do balaio, checar se a cadeia de grants ja a concede -- se concede, nao e escolha". Medido
    montando um personagem de cada uma das 16 classes com balaio, no nivel do bloco mais alto, e comparando
    com o que a cadeia entrega sem escolher nada: das 265 opcoes, apenas TRES ja sao concedidas (`formula-book`
    e `versatile-vials` do Alquimista, `champions-aura` do Campeao). Essas tres sao curadoria segura --
    sao oferecidas como escolha estando ja concedidas. As outras 262 seguem sem regra que as explique:
    a hipotese (a) do item deu zero (nenhuma esta na progressao), esta deu 3. O balaio nasce em aplicar_subclasses.py
    quando a classe TEM lista autoritativa do Foundry e o nome da feature nao esta nela. VER ITEM 99:
    os ChoiceSet dos class-features do Foundry nomeiam eixos, e e o unico caminho novo que apareceu --
    mas as listas LITERAIS cobrem zero das 265, entao o ganho, se houver, esta nas 104 de forma `query`.'
  id: 69
  date: '2026-07-30'
  priority: media
- desc: '5a RODADA FECHADA 2026-07-30 (commit 1bb66c6a9, spec requisito-de-subescolha). As cinco classes
    que faltavam entraram no DEFAULT do comparador, com atributos MEDIDOS pela sonda (Campeao STR+3 DEX+1
    CON+1 declara os cinco boosts porque a chave e escolha; Druida, Feiticeiro, Alquimista e Investigador
    tem chave unica e o motor a aplica sozinho). ACHOU DEFEITO NOSSO: cinco feats do Campeao que liberavamos
    e ele barrava, porque o requisito de CAUSA vivia em `requires_residuo` como prosa. Viraram requisito
    de verdade -- 26 clausulas em 7 eixos. Residuo 560 -> 534. TRIAGEM do resto, sem defeito nosso: os
    3 `so no Waybuilder` que aparecem em TODAS as classes (Chelaxian Scion, Knight Vigilant, Venture-Gossip)
    sao recorte de fonte; os `wb=False pb=True` por pericia sao a diferenca de modelo declarada. PROXIMAS
    RODADAS: (a) `Chemical Contagion` e `Enhanced Fire`, so no Pathbuilder no Alquimista 1, e `Artokus''s
    Fire`/`Powerful Alchemy`/`Certain Strategem`/`Red Herring`, so nossos -- por investigar; (b) general_feat
    fora do Guerreiro e do Bardo; (c) o quantificador "uma pericia que tenha a acao X" (Automatic/Dubious
    Knowledge); (d) as classes ainda sem rodada: Barbaro ja teve, faltam Commander, Exemplar, Guardian,
    Kineticist, Magus, Oracle, Psychic, Summoner, Swashbuckler, Thaumaturge, Witch, Inventor, Animist,
    Necromancer, Runesmith.'
  id: 84
  date: '2026-07-30'
  priority: media
- desc: 'Importador do Pathbuilder tem que AVISAR o que se perde. Confirmado com o Igor: o eidolon existe
    no app deles e nao sobrevive ao export. Perda silenciosa e o pior tipo'
  id: 10
  date: '2026-07-29'
  priority: baixa
- desc: 'POR ULTIMO, decisao do Igor (2026-07-29): opcao de idioma ingles / pt-BR na interface. Depois
    de TODO o resto -- so faz sentido com o app fechado. Escopo a decidir quando chegar a vez: a UI (rotulos,
    botoes, mensagens do motor) e traduzivel; a PROSA das 19.706 entradas vem das fontes em ingles e nao
    tem versao pt-BR licenciada, entao o mais provavel e UI em pt-BR com conteudo de regra em ingles.
    Nome de trait e de entidade idem -- traduzir ''Reactive Strike'' quebraria a busca do jogador que
    le AoN'
  id: 31
  date: '2026-07-29'
  priority: baixa
- desc: 'ARMAS SEM DANO -- PARCIALMENTE RESOLVIDO 2026-07-29. Eram 57 armas sem `damage`, mas 41 sao bombas
    alquimicas (o dano e do efeito, vazio esta certo), 6 sao municao/magazine/pellet e 5 sao arma magica
    ou material que HERDA o dano do item base. Restavam QUATRO de verdade. Blowgun e Dart Umbrella FORAM
    CORRIGIDAS: o AoN traz `damage: ''1 P''` (dano fixo 1, sem dado, que e RAW) e o parser de `recuperar_mecanica_equipamento.py`
    exigia `dN`. Agora ha um segundo padrao (`FIXO`) e a representacao OMITE a chave `dado` em vez de
    grava-la como None -- os dois motores fazem `dano.get(''dado'','''')`, e a chave presente com None
    imprimiria ''None'' na ficha. Travado por 3 assercoes no oraculo. FALTAM DUAS: Nine-Ring Sword e Wind
    and Fire Wheel (Tian Xia) nao tem fonte em disco nenhuma -- precisa de dump novo do AoN ou entrada
    curada'
  id: 85
  date: '2026-07-29'
  priority: baixa
- desc: 'PARTE FECHADA 2026-07-30 (spec pre-requisito-de-familiar): `a familiar` virou termo de verdade.
    Quando o item foi escrito nao havia paralelo do `grant_actor` para familiar; no dia seguinte a spec
    familiares-e-eidolons-concedidos derivou 16 registros que concedem familiar e 2 que concedem eidolon,
    e `has_actor` ja lia isso -- faltava so `ATOR_RE` aceitar o bicho. 6 clausulas saíram do residuo.
    RECUSADO COM NUMERO na mesma spec: quebra de clausula por virgula (70 clausulas tem virgula e quase
    toda e LISTA dentro de um conceito unico; ", and" sao 8 e so 1 quebraria limpo; e `{@feat X|Fonte},
    <prosa>` nao aparece em nenhum dos 28 registros que tem residuo e nenhum requires). SOBRA (medido
    2026-07-30, e agora TUDO destravado pela divindade): 6 clausulas de arma favorita / pericia divina
    / santificacao. `favored_weapon` ja esta em 479 divindades como id real, `weapon_category` em 1.032
    de 1.039 armas, e a tabela de proficiencia do Clerigo tem a chave literal "Deity''s favored weapon".
    FALTA UM CAMPO, e e a DECIMA lacuna de leitura: `divine_skill` esta na prosa do AoN de praticamente
    toda divindade (Athletics 79, Nature 67, Society 60, Diplomacy 57...) e a base tem ZERO. Precisa de:
    (a) ler `divine_skill` da prosa, mesmo formato do modal de santificacao; (b) tres termos -- `deity_favored_weapon_category`
    (deadly-simplicity exige favorita simple/unarmed), proficiencia na pericia divina (mortal-herald x2,
    "master in Religion or your deity''s divine skill") e santificacao declarada (sanctify-water); (c)
    padroes de parser. Alinhamento segue recusado. Divindade OPCIONAL para quem nao e Clerigo nem Campeao
    (`you follow a deity`, 4 clausulas) e decisao de produto, nao de motor.'
  id: 87
  date: '2026-07-30'
  priority: baixa
- desc: 'PASSO DOIS DO ITEM 22: estruturar `acesso` em filiacoes. Hoje e texto verbatim em 728 registros,
    e as formas se repetem (102 armas de fogo, 102 gadgets, 80 Pathfinder Society, 73 Knights of Lastwall,
    72 Absalom/New Thassilon, 55 Firebrands, 28 Tian Xia, 27 Hermea) -- da para cobrir a maioria com ~15
    stubs. SO FAZ SENTIDO depois que houver consumidor: hoje nada no motor pergunta ''de que organizacao
    voce e''. Junto vem a decisao de UI: a ficha deveria mostrar o `acesso` do item incomum.'
  id: 96
  date: '2026-07-30'
  priority: baixa
- desc: 'CAUSA RESOLVIDA 2026-07-30 (commit 9c86ee6c3, spec escolha-multipla-e-ikons). O eixo `ikon` do
    Exemplar existe, com `escolhe: 3` -- o primeiro bloco da base que nao escolhe 1 --, e os 21 ikons
    ganharam `equivale_a` com o gemeo class-feature. Os dois motores passaram a ler `escolhe`; antes o
    motor fazia `next(...)` e perderia duas escolhas em silencio. SOBRA, cada um com causa PROPRIA e medida:
    (a) `wb:feat/additional-ikon` concede um QUARTO ikon -- a maquinaria de "feat abre slot" ja existe
    (feat_concedido, grant_actor), falta o feat declarar, e nenhum campo da fonte diz; (b) os 15 `mythic-calling`
    seguem inalcancaveis porque a ficha nao modela regras miticas -- ausencia declarada; (c) os 22 sem
    gemeo: 6 gates do Kineticist + `elemental-school` + `advanced-vials-toxicologist` sao gap de progressao
    de VERDADE (o slot da classe aponta para outra feature), 7 `deviant-classification` tem primo por
    NOME e nao por slug em `deviant-ability-classification` (kind que tem duplicidade propria nao resolvida),
    e 4 stubs genericos (focus-spells, iron-will, improved-evasion, martial-weapon-mastery).'
  id: 97
  date: '2026-07-30'
  priority: baixa
- id: 98
  date: '2026-07-30'
  priority: baixa
  desc: 'FECHADO 2026-07-30. A parte principal saiu no commit 69d2df0f5 (eixo de divindade, quatro termos,
    parser, linha na ficha) e a sub-escolha da FONTE -- o unico limite que a spec declarava -- saiu no
    bed0f5754. Um Clerigo de Aakriti que escolhe `harm` deixa de atender Healing Hands; antes os dois
    atendiam. Dois termos para nao ser circular: `deity_font_permitido` (a divindade permite?) no requires
    das opcoes e `deity_font` (a fonte do personagem?) nas clausulas de feat. O QUE SOBRA vive em outros
    itens: arma favorita / pericia divina / santificacao como TERMO (6 clausulas) e divindade opcional
    para quem nao e Clerigo nem Campeao ficam no 87; alinhamento segue recusado; `Versatile Font` precisa
    de CONCESSAO de escolha, que e outra familia.'
- id: 99
  date: '2026-07-30'
  priority: media
  desc: 'PRIMEIRO ALVO FECHADO 2026-07-30 (commit 726c8cb9e, spec santificacao-escolhida): a santificacao
    virou eixo, e com ela a base ganhou o desenho de SUB-ESCOLHA FILTRADA que faltava -- opcao com `requires`
    proprio, avaliada por `candidatos()`, MARCADA e nunca escondida. O mesmo desenho fechou a fonte divina
    em seguida. A medicao evitou uma armadilha: inferir o modal da lista achatada (`["holy"]` = obriga)
    erraria em 408 divindades, porque a prosa do AoN diz `can choose holy` em 265 delas -- so 108 obrigam.
    SOBRAM 191 das 194 regras ChoiceSet. As 74 de lista LITERAL cobrem zero do balaio e zero dos inalcancaveis
    (apontam para draconic-exemplar 95, animal-companion 12, skill 11 -- ja modelados). A carga esta nas
    104 de forma `query`, que buscam no compendio por predicado e povoariam `Kineticist.KineticGate` (33)
    e `Exemplar.Ikon` (22): exige um avaliador de query, que e trabalho e risco novos e ainda nao foi
    dimensionado.'
promoted: []
---
