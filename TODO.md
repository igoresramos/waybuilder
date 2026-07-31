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
- desc: 'SOBRA DO ITEM 43, FECHADO 2026-07-31 (spec specs/2026-07-31-estatisticas-de-familiar-e-eidolon.md).
    Familiar e eidolon ganharam ficha; o que ficou de fora esta declarado com numero na spec. (a) As
    10 habilidades de familiar (`rules-2125`: amphibious, burrower, climber, darkvision, echolocation,
    fast movement, flier, manual dexterity, scent, tough) -- so `Tough` mexe em numero (`+2 HP por nivel`),
    as outras nove sao sentido e movimento, e a ESCOLHA diaria delas e recurso por dia, nao construcao.
    (b) Os ataques desarmados do eidolon (`rules-1584`: 4 dados possiveis no primario, secundario fixo
    1d6 agile finesse) -- depende de conceder Strike, mesma familia dos 30 `Strike` do Animal Instinct
    ja recusada no item 101. (c) O boost de atributo do eidolon (`rules-1583`, "gets boosts at the same
    time you do") -- pede o orcamento de boost do personagem aplicado a outra ficha. (d) O tipo `Swarm`
    e o unico eidolon sem array na fonte estruturada; hoje aparece MARCADO com o motivo. (e) A aba da
    ficha ainda se chama "Companheiro" mesmo quando o ator e familiar ou eidolon -- cosmetico.'
  id: 104
  date: '2026-07-31'
  priority: baixa
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
- desc: 'MEDIDO E REDIMENSIONADO 2026-07-31, e a propria premissa deste item nao se sustentou. Ele
    dizia "provavel que seja a maior veia nao lida que sobrou". NAO E. `pipeline/dados_brutos/aon_dump/rules.json`
    tem mesmo 3.645 registros e 3,8 milhoes de caracteres que nenhum extrator abre, mas o que sobra dali
    e quase todo prosa de MESA, nao numero de ficha. Medido por duas vias: (1) das 389 clausulas distintas
    em `requires_residuo`, apenas **13** tem o texto literal aparecendo no arquivo, e sao frases genericas
    (`living creature`, `good alignment`, `you have a focus pool`) que casam por acaso, nao por conterem
    a regra; (2) so **39 das 3.645** paginas carregam formula de personagem (`equal to your level`, `per
    level`, `equal to yours` e irmas), e dessas **4 ja foram consumidas** pela spec de familiar e eidolon.
    Das ~35 que sobram, a maioria e de MESTRE (Treasure by Encounter, Unexpected Difficulty, Complex Crafting)
    ou de regra variante que nao usamos (Building a Dual-Class Character, Advanced Undead, Cryptids). As
    poucas de personagem foram conferidas a mao -- `rules-35` (Proficiency), `rules-1147` (Devotee Benefits)
    e `rules-1331` (Character Advancement) descrevem coisas que o motor JA implementa. CONCLUSAO: o familiar
    foi a EXCECAO, nao o padrao -- o statblock dele morava numa pagina de regra em vez de na entidade.
    Prioridade rebaixada de media para baixa. Se alguem voltar aqui, o alvo sao as ~35 paginas com formula,
    nao os 3.645 registros.'
  id: 103
  date: '2026-07-31'
  priority: baixa
- desc: 'PARTE FECHADA 2026-07-31 (passo `derivar_arquetipo_do_feat.py`). FEITO: **37** dos 73 feats
    com trait `archetype` e campo vazio foram re-ancorados lendo a dedicacao no proprio `requires`. Nao
    foram 49 como a medicao automatizada previa: 12 citam DUAS dedicacoes (`Skill Mastery` aceita Rogue
    OU Investigator) e ancorar num dos dois seria escolher -- poe o feat na lista errada, que e pior que
    deixa-lo sem lista. Sobram 36 sem ancora, que ficam como estao. O QUE SOBRA E MUDOU DE NATUREZA: os
    12 homonimos classe x arquetipo foram investigados e NAO sao defeito de numero. Testado: um Alquimista
    5 responde `True` a `has wb:feat/advanced-alchemy`, porque `wb:class-feature/alchemy` CONCEDE o feat
    de arquetipo -- a cadeia funciona e `efficient-alchemy` atende corretamente. O que esta errado e QUAL
    REGISTRO vai para a ficha: o do arquetipo (nivel 4, fonte de arquetipo) em vez do `class-feature`
    de mesmo nome, que existe na base e fica INALCANCAVEL (`wb:class-feature/advanced-alchemy` e
    `wb:class-feature/quick-alchemy` respondem `False` ao `has`). E cosmetico, familia do item 55, e o
    lado inalcancavel e familia do item 97. O conserto certo e `equivale_a` entre o par, como foi feito
    nos gemeos de instinto -- assim os dois ids resolvem; trocar o alvo do `grants` sozinho QUEBRARIA a
    cadeia que hoje funciona.'
  id: 100
  date: '2026-07-30'
  priority: baixa
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
- desc: 'RODADA 6 FEITA 2026-07-31 (docs/medicoes/2026-07-31_pathbuilder-rodada-6.md, com nota de correcao
    no topo). As 14 classes que faltavam foram rodadas -- Guardian, Exemplar, Commander, Gunslinger, Inventor,
    Kineticist, Swashbuckler e Thaumaturge no nivel 1; Animist, Witch, Magus, Psychic, Oracle e Summoner
    no nivel 2. Boosts MEDIDOS com `sonda-estado-pathbuilder.mjs`, nunca chutados. Com isso as 27 classes
    estao cobertas. RESULTADO: **zero defeitos nossos** em 152 pontos triados. O unico candidato (`wb:feat/incredible-familiar`
    com trait `animist`) foi verificado contra a fonte e NAO e defeito -- o AoN publica esse trait no
    Player Core e `prov.traits` mostra AoN e Foundry concordando; o Pathbuilder e que carrega a lista
    pre-remaster do Dark Archive/APG. Balde certo: recorte de fonte. ACHADO ESTRUTURAL que vale guardar:
    seis classes travam o Class Feat do nivel 1 atras de escolha de subclasse obrigatoria (Animist, Witch,
    Magus, Psychic, Oracle, Summoner), somadas a Druida e Feiticeiro ja conhecidas -- sao 8 no total,
    e isso e informacao, nao falha. LIMITE DO COMPARADOR, agora conhecido: `incredible-familiar` e `incredible-familiar-animist`
    colidem na normalizacao e o script conta como "casado", entao par assim nunca aparece no placar --
    consertar antes da proxima rodada, senao a cobertura mente. SOBRA: 3 pares novos de renomeacao Golarion->generico
    para `equivalencias-pathbuilder.json`, e os 33 pontos do Kineticist que so confirmam o gap ja rastreado
    nos itens 97/99 (os 6 gates elementais zerados).'
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
- id: 105
  date: '2026-07-31'
  priority: media
  desc: 'FATIA 0 FEITA 2026-07-31 (spec specs/2026-07-31-escolha-aninhada-do-inventor.md), e ela rendeu
    mais do que o dimensionamento previa. O previsto era "ler as literais por nome e nomear 59 do balaio".
    O que se achou foi ESTRUTURA: o Inventor era a UNICA classe sem eixo nenhum -- tres blocos `outras-opcoes`
    (22, 15, 15) -- e o nivel 1 misturava 4 INOVACOES com 18 MODIFICACOES da inovacao, enquanto os niveis
    7 e 15 eram tiers de modificacao. O Foundry declara tudo em `ChoiceSet` de lista literal (1.012 deles,
    529 referencias, 395 distintas, 362 resolvem na base, ZERO ambiguas). FEITO: 6 eixos criados (Inventor
    `innovation` 4, `initial-modification` 13, `breakthrough-modification` 32, `revolutionary-modification`
    45; Mago `thassilonian-sin` 7 e `rooted-branch` 5), 63 opcoes saindo do balaio (265 -> 202), e 25
    opcoes com gate por sub-escolha. Ganho de desenho: BLOCO CONDICIONAL -- quando todas as opcoes de
    um eixo pedem a mesma sub-escolha, a condicao e do EIXO, e um Mago de outra escola simplesmente NAO
    TEM o eixo de pecado thassiloniano (antes o motor avisava "falta escolher" para todo Mago). SOBRA:
    (a) `item:slug`, 74 usos, ainda ignorado no `_atomo_de_filtro` -- todos apontam para registro especifico
    e o slug do Foundry nem sempre e o nosso id; (b) `Manifold Modifications` (feat nv 8, 17 opcoes) ficou
    fora do eixo por ser feat e nao progressao -- entra pela familia de slot concedido por feat; (c) as
    fatias 2 a 4 do dimensionamento, que somam 20 queries exatas e ZERO opcao nova; (d) 202 opcoes de
    balaio seguem sem explicacao (Alchemist 33, Thaumaturge 30, Cleric 18, Animist 13, Oracle 12) -- e
    o item 69.'
promoted: []
---
