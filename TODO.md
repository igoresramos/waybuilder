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
- desc: 'DESTRAVADO 2026-07-31 -- a fonte EXISTE em disco e foi verificada (docs/medicoes/2026-07-31_fonte-de-familiar-e-eidolon.md).
    O item estava parado por "conseguir a fonte das estatisticas"; ela nunca faltou. E a DECIMA PRIMEIRA
    lacuna de leitura, e a maior ate agora: nao e um campo, e um ARQUIVO INTEIRO. `pipeline/dados_brutos/aon_dump/rules.json`
    tem 3.645 registros e NENHUM extrator o le (conferido por grep em pipeline/ e pipeline/extratores/).
    FAMILIAR -- formula fechada, sem ambiguidade: `rules-162` diz "5 Hit Points for each of your levels";
    `rules-161` (legado, Core Rulebook) diz que AC e saves sao iguais aos do mestre ANTES de circunstancia
    e status, e que Perception/Acrobatics/Stealth = nivel + modificador de conjuracao; `rules-2122` (REMASTER,
    Player Core pg. 212) ajusta para `3 + nivel`, com opcao de usar `mod de conjuracao + nivel` se for
    maior -- e a versao remaster que vale, pela regra de sempre usar a mais recente; `rules-165` da Speed
    25 ft (ou swim 25, escolha ao ganhar); nao faz Strikes e usa o nivel do mestre como modificador. EIDOLON
    -- nao tem HP proprio, compartilha o pool do invocador; os arrays de atributo, cap de Dex e bonus
    de item por tipo estao ESTRUTURADOS em `pipeline/dados_brutos/pf2etools_repo/data/companionsfamiliars.json`
    (chave `eidolon`, 12 registros com campos `stats`/`skills`/`size`), faltando so o tipo "Swarm", que
    esta em prosa. POR QUE O COMPANHEIRO ANIMAL JA FUNCIONA e estes dois nao: puro schema do AoN -- `animal-companion`
    tem colunas numericas nativas, `eidolon` e `familiar-specific` nao tem, e o extrator `companheiros.py`
    so le coluna, nunca prosa nem `rules.json`. NAO precisa de dump novo nem de PDF.'
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
- desc: 'ACHADO AO DESTRAVAR O ITEM 43 (2026-07-31): `pipeline/dados_brutos/aon_dump/rules.json` tem
    **3.645 registros** e **3,8 milhoes de caracteres** de prosa de REGRA, e NENHUM extrator o le -- conferido
    por grep em `pipeline/*.py` e `pipeline/extratores/*.py`, zero ocorrencias. Nao e um campo esquecido,
    e um ARQUIVO INTEIRO. Por livro: GM Core 799, Core Rulebook 785, Gamemastery Guide 590, Player Core
    497, Kingmaker 139, Secrets of Magic 104, Treasure Vault 72+69. O item 43 mostrou que ali mora a formula
    do familiar, que estava sendo tratada como fonte inexistente. A PERGUNTA A MEDIR antes de qualquer
    spec: quantos OUTROS itens da fila (e quantas clausulas de `requires_residuo`) sao respondidos por
    este arquivo? Varredura por termo dos itens abertos contra os 3.645 registros. Provavel que seja a
    maior veia nao lida que sobrou -- as dez lacunas anteriores eram todas de CAMPO.'
  id: 103
  date: '2026-07-31'
  priority: media
- desc: 'RE-MEDIDO E VERIFICADO 2026-07-31 (docs/medicoes/2026-07-31_homonimos-e-duplicatas.md, com
    nota de correcao no topo). Tres defeitos independentes, achados na medicao do item 46. (1) HOMONIMO
    CLASSE x ARQUETIPO: **12** ocorrencias (3 em `requires`, 9 em `grants`) em 11 registros de origem,
    onde o alvo e mesmo feat de ARQUETIPO tendo `class-feature` de mesmo nome ao lado -- `quick-alchemy`
    6, `advanced-alchemy` 2, `champions-reaction` 2, `keen-recollection` 1, `surprise-attack` 1. CUIDADO
    COM A CONTAGEM: uma medicao automatizada deu 40 porque contou todo `wb:feat/X` com `wb:class-feature/X`
    homonimo, sem checar se o feat era de arquetipo; `shield-block` (general, 12x) e `reactive-strike`
    (classe, 5x) NAO sao defeito -- feat e feature de mesmo nome ai e RAW correto, e o motor ja resolve
    por alias (testado: Guerreiro 2 com a class-feature responde True a `has` do feat). (2) ATRIBUICAO
    DE ARQUETIPO VAZIA: **73** feats com trait `archetype` e campo `archetype` vazio -- muito maior que
    os 7 medidos antes, que so olhavam o recorte de multiclasse. Destes, 49 sao re-ancoraveis automaticamente
    porque o `requires` cita uma dedicacao de arquetipo conhecido; 24 pedem curadoria. (3) **18** arquetipos
    sem nenhum feat de dedicacao apontando para eles, e nenhum tem dedicacao de nome similar so nao atribuida.'
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
- desc: 'ACHADO PELA VERIFICACAO `verificar-eixos.mjs` AO FECHAR O 87 (2026-07-30) -- e PRE-EXISTENTE,
    confirmado rodando a verificacao no estado anterior. O eixo `deity` do Campeao oferece `Ma''at` DUAS
    vezes: `wb:deity/maat` (Divine Mysteries, remaster) e `wb:deity/maat-ln` (Gods & Magic, legado). MEDIDO:
    e o UNICO caso -- 1 nome de divindade duplicado em 488, e 1 unica divindade com sufixo de alinhamento
    legado no id (`-ln`). Familia de `fundir_renomeados.py` / `derivar_alias_legado.py`, que nao alcancou
    este par. ATENCAO AO FUNDIR, verificado 2026-07-31: `wb:deity/maat-ln` E REFERENCIADO, por `wb:class/champion`
    e `wb:class/cleric` -- ele esta no eixo `deity` das duas. Uma medicao automatizada afirmou "0 referencias,
    seguro fundir" e estava ERRADA; fundir sem tratar as duas listas quebra o eixo. O remaster e o canonico,
    o legado vira alias.'
  id: 102
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
  desc: 'RE-DIMENSIONADO 2026-07-31 (docs/medicoes/2026-07-31_dimensionar-avaliador-de-query.md). TRES
    PREMISSAS DESTE ITEM ESTAVAM ERRADAS, e as tres foram verificadas contra o codigo e a base. (1) "exige
    um avaliador de query, que e trabalho e risco novos" -- ELE JA EXISTE: `_casa_filtro` em `motor/motor.py:3184`
    e `app/src/motor/personagem.ts:3437`, com `or`/`and`/`not`/`nor`/`xor`/`lte`, ja chamado em producao
    para recortar slot. Nenhum dos operadores usados pelas queries falta. (2) "povoariam `Exemplar.Ikon`
    (22)" -- o eixo `ikon` do Exemplar JA EXISTE na base com 21 opcoes e `escolhe: 3` (feito na spec escolha-multipla-e-ikons);
    o 22 era contagem de REGRAS, nao de opcoes. Idem o "33" do Kineticist, que rende 6 gates. (3) "as
    74 de lista literal cobrem zero do balaio" -- falso: 59 opcoes literais estao no balaio `outras-opcoes`
    (Inventor 47, Wizard 12). O QUE SOBRA DE VERDADE: as 194 ChoiceSet sao QUATRO formas, nao duas --
    88 `filter`, 74 literal, 16 `ownedItems`, 16 string. E o que a query destrava sao DOIS eixos em classes
    que hoje tem ZERO bloco de subclasse (confirmado): Kineticist (6 gates + impulsos) e Commander (11
    escolhas de tatica, 14 a 31 opcoes). DIVIDA VIVA que ninguem tinha contado: `_atomo_de_filtro` so
    entende `trait`/`level`/`category`/`rarity`, e os filtros da base usam `item:slug` 74 vezes e `item:tag`
    54 -- ignorados e contados como SATISFEITOS. Isso e correto para ESTREITAR slot de feat (principio
    zero: nao esvaziar em silencio) e DESTRUTIVO para DEFINIR eixo, porque o eixo sai com tudo dentro
    (mediana medida: 16.383 itens sobrando; 67 listas erradas por excesso contra 3 vazias). ORDEM OBRIGATORIA:
    ensinar `item:tag` ao motor ANTES de usar filtro para definir eixo. RECORTE 80/20 PROPOSTO: Fatia
    0 (ler as literais por nome, sem avaliador nenhum) + Fatia 1 (`item:tag` + extrair os ChoiceSet dos
    class-features, que hoje sao 0 dos 847) fecham 68 das 88 queries e nomeiam 136 do balaio, com UM atomo
    novo. As fatias seguintes somam 20 queries e ZERO opcao nova -- valem por correcao de nivel, nao por
    volume. NAO VERIFIQUEI todas as 11 afirmacoes do relatorio; conferi 4 -- o avaliador existente, o
    eixo do Exemplar, os zero blocos de Kineticist/Commander e a divida de `item:slug`/`item:tag` -- e
    as 4 se sustentaram.'
promoted: []
---
