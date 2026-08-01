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
- desc: 'DUAS FATIAS FEITAS 2026-07-31 (specs 2026-07-31-nomear-o-balaio-por-tag.md e
    2026-07-31-variante-por-subclasse.md). Balaio: 202 -> 111 -> e das 111, 68 deixaram de ser escolha
    livre. || FATIA 1 -- O BALAIO JA ERA EIXO, faltava o NOME: um Exemplar ja recebia os epitetos nos
    niveis 3/7/15 com `escolhe: 1`, o bloco funcionava, so se chamava `outras-opcoes` e na tela virava
    "Exemplar / outras-opcoes". O nome estava na `tags` dos registros. Cada balaio se PARTE por tag (grupo
    de 2+ vira eixo); 11 eixos cobrindo 91 opcoes -- Exemplar root/dominion/sovereignty-epithet (6/8/4),
    Sorcerer bloodline 18, Summoner eidolon 13, Animist apparition 13 + practice 4 (UM balaio com DOIS
    eixos), Barbarian instinct 9, Druid order 9, Investigator methodology 5, Champion blessing 2. PROVA:
    `candidatos("subclasse", n)` de TODAS as classes, antes x depois -- ZERO conjuntos mudaram. || FATIA
    2 -- VARIANTE POR SUBCLASSE: 68 opcoes cujo nome termina em parentese que casa EXATAMENTE uma opcao
    de subclasse da classe (`Field Discovery (Bomber)`, os 10 `Initiate Benefit (X)` do Taumaturgo, `Final
    Doctrine (Warpriest)`). Nao ha o que escolher -- o campo de pesquisa ja decidiu --, e antes as quatro
    apareciam iguais e um Bomber podia escolher a do Chirurgeon. GATE e nao remocao, porque NENHUMA e
    concedida pelo dono (`wb:class-feature/bomber` tem `grants: []`) e tira-las as tornaria inalcancaveis:
    ganharam `requires.subclass`, ficam na lista MARCADAS com o motivo (`exige a sub-escolha Chirurgeon;
    tem Bomber`). Thaumaturge 30, Alchemist 23, Cleric 12, zero puladas. || O QUE SOBRA: (a) ~30 PAIS
    GENERICOS das variantes (`Perpetual Infusions` sem parentese, ao lado dos quatro `(X)`) -- sem
    parentese nao ha regra que os explique sem inventar; (b) `Spell Repertoire (Sorcerer|Summoner)`, duas
    features automaticas arquivadas no balaio que nao chegam a ficha por nenhum outro caminho; (c) o modelo
    CERTO das 68 seria o dono CONCEDER a variante em vez de o jogador escolher-la marcada, e isso pede
    vocabulario novo de grant (`concede feature no nivel N`) que nao existe -- mudanca de motor, TS e tela.
    || O VOCABULARIO SAIU MENOR QUE O PREVISTO, e a fonte o dita (spec
    specs/2026-07-31-grant-condicional.md): nao e `concede feature no nivel N`, porque o NIVEL ja esta na
    progressao da classe (`First Doctrine` no 1, `Second` no 3) -- falta so a CONDICAO, `grants[].se`. Os
    64 pares `(opcao, item concedido)` estao declarados estaticamente no Foundry. Cobertura por familia:
    Taumaturgo bate (30 pares / 30 gateadas), Clerigo bate (12/12), Alquimista NAO (12/23), e o Gunslinger
    e familia nova que as 68 nao tinham. O gate desta fatia FICA para quem nao tiver par -- os dois
    modelos convivem.'
  id: 69
  date: '2026-07-31'
  priority: media
- desc: 'DESTRAVADO 2026-07-31: as 27 classes passam a ser COMPARADAS DE VERDADE. O comparador so
    conhecia 13 (`DEFAULT` 13, `BOOSTS_DO_PATHBUILDER` 11) e PULAVA EM SILENCIO as outras 14 -- que tinham
    sonda E tinham arquivo de comparacao em disco, de 07:12 do mesmo dia, nunca mais regerado. A checagem
    "toda sonda tem comparacao" passava e mentia, e a rodada 6 dizia "27 classes cobertas, zero defeitos":
    valia para 13. || O ELO PERDIDO estava em disco: a rodada 6 JA tinha medido os boosts das 14 (30
    arquivos `estado-pathbuilder-*.json`), e ninguem estendeu as tabelas. Estendi DERIVANDO dos arquivos
    medidos, nunca chutando: modificador na tela = numero de boosts, e a habilidade-chave so entra na
    lista quando e ESCOLHA (Exemplar e Magus `dex|str`, Psychic `int|cha` declaram os cinco; as outras
    tem chave unica e o motor aplica sozinho). Medi mais 7 em paralelo para fechar (Exemplar, Thaumaturge,
    Kineticist, Inventor, Guardian, Barbarian, Ranger). DEFAULT 13->27, BOOSTS 11->25. || RESULTADO: zero
    pulados, e os pontos a triar subiram de 344 para **497**. Os 153 novos: 79 divergencias, 56 so-nosso,
    9 so-deles. TRIADOS POR FAMILIA, e NENHUMA e nova: 57 sao "nos aceitamos, eles nao" (dedicacoes --
    balde de recorte de fonte, o mesmo das 13); 20 sao pre-requisito de PERICIA (survival/stealth/arcana/
    occultism trained) -- a diferenca de modelo JA DECLARADA no proprio comparador, porque o Pathbuilder
    conta escolha de pericia pendente como alcancavel e nos avaliamos o estado atual e MARCAMOS; 1 e o
    gate do Kineticist (`Extended Kinesis` exige `Base Kinesis`), familia dos itens 97/99; 1 e
    proficiencia de arma nomeada (Aldori). Concentracao: Kineticist 25, Witch 11, Summoner 10, Magus 9. ||
    TRIAGEM FEITA 2026-07-31 (relatorio docs/medicoes/2026-07-31_triagem-57-so-nosso.md), e A HIPOTESE
    SE CONFIRMOU: o balde escondia defeito novo. Sao 56 pontos na recontagem exata, nao 57 (discrepancia
    anotada e nao resolvida). Placar: DEFEITO NOSSO 21 pontos / 8 raizes, RECORTE DE FONTE 31, LIMITE DO
    COMPARADOR 4, diferenca de modelo ja declarada 0. || OS 8 SAO UMA FAMILIA SO -- par AoN/Foundry da
    mesma entidade que nenhum mecanismo funde, um lado `prov.name=aon` e outro `prov.name=foundry`:
    `knight-vigilant` x `knight-vigilant-dedication`, `armor-` x `armored-regiment-training`, `flash-forge`
    x `flashforge`, `voice-of-the-elements-kineticist` x `voice-of-elements`, `automatic-` x
    `autonomic-psychic-action`, `vermillion-` x `vermilion-threads` (nossa grafia com 2 L e a do Foundry,
    o AoN e o proprio PB usam 1 L), `whisper-` x `whispers-of-warning`, e `deepest-wellspring` x `amp-focus`
    (este ultimo NAO e grafia: o AoN linka `remaster_id` feat-3693 -> feat-8336 nos dois sentidos e a guarda
    de nivel divergente 18x12 vetou a fusao, deixando o feat legado vivo). O PIOR e `voice-of-elements`:
    o lado com nome do AoN tem `grants: []` e o do Foundry tem 7 -- conteudo PARTIDO, nao so nome duplicado.
    || DERRUBA CLASSIFICACAO ANTIGA de tres rodadas: `Armor Regiment Training` (rodada 6 disse "falha de
    importacao do lado dele") esta no dump do PB como `{"nome": "Armored Regiment Training", "atende": true}`;
    idem `Knight Vigilant Dedication` e `Vermilion Threads`. Conferido a mao nos dumps, nao so pelo agente.
    || O CONSERTO NAO E CURADORIA: vira o item 110, porque curar 8 pares a mao repete o preco do item 85.'
  id: 84
  date: '2026-07-31'
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
- desc: 'FECHADO 2026-07-31 (spec specs/2026-07-31-par-curado-tian-xia.md). A premissa estava ERRADA:
    nao faltava dump do AoN. As duas armas estavam no dump que ja existia, sob os nomes chineses, e a
    base ja tinha os registros COMPLETOS -- `Nine-Ring Sword` e `Jiu Huan Dao` (1d8 S, martial, sword),
    `Wind and Fire Wheel` e `Feng Huo Lun` (1d4 S, advanced, knife). O nome em ingles aparece so na PROSA
    do AoN ("Also known as wind and fire wheels"), e por isso busca por nome nunca achava. Os dois
    registros vazios vinham do pf2etools, unica fonte que manteve o nome ingles. NENHUM mecanismo
    existente os juntava: `derivar_alias_legado` le `legacy_id` e o vinculo esta la (weapon-623 ->
    weapon-288), mas o AoN renomeou os DOIS lados e a guarda de nome-igual pula, corretamente; o colapso
    de irmaos casa por nome e os nomes nao se parecem. Par curado, dois. E `equivale_a` sozinho NAO
    bastou: `resolver()` segue `aliases`, nao ele, entao a arma equipada pelo id antigo continuava saindo
    com dano `1`. Fecha preenchendo o que FALTA a partir do gemeo, so campo ausente -- `disarm` do
    registro antigo continua la. Agora as quatro rendem: 1d8 e 1d4. SOBRA DECLARADA:
    `wb:weapon/jiu-huan-dao-disarm`, terceira variante (weapon-99, sem remaster_id nem legacy_id) -- sao
    tres registros do AoN para a mesma arma; triagem de homonimo, outra familia.'
  id: 85
  date: '2026-07-31'
  priority: baixa
- desc: 'PASSO DOIS DO ITEM 22: estruturar `acesso` em filiacoes. Hoje e texto verbatim em 728 registros,
    e as formas se repetem (102 armas de fogo, 102 gadgets, 80 Pathfinder Society, 73 Knights of Lastwall,
    72 Absalom/New Thassilon, 55 Firebrands, 28 Tian Xia, 27 Hermea) -- da para cobrir a maioria com ~15
    stubs. SO FAZ SENTIDO depois que houver consumidor: hoje nada no motor pergunta ''de que organizacao
    voce e''. Junto vem a decisao de UI: a ficha deveria mostrar o `acesso` do item incomum.'
  id: 96
  date: '2026-07-30'
  priority: baixa
- desc: 'RE-MEDIDO PELA TERCEIRA VEZ EM 2026-07-31, e as duas medicoes anteriores estavam erradas por
    METODO. Contar "registro nunca citado por outro" da 15.771 de 19.606 -- numero sem sentido, porque
    99%% do equipamento nao e citado por ninguem: ele se escolhe do CATALOGO. Existem QUATRO caminhos
    de alcance, e nao um: (a) citacao por outro registro; (b) KIND -- slots que varrem um kind inteiro;
    (c) FILTRO -- os eixos por query criados em 31/07, resolvidos por `_casa_filtro`; (d) o GEMEO
    `equivale_a`, que o passo de colapso cria. Com os quatro, o numero real e **1.204**. O topo dele e
    catalogo puro e NAO e defeito: trait 551, relic 122, language 121. O que sobra de acionavel:
    `familiar-ability` 72 (declarado fora de escopo na spec do item 43), `class-kit` 32 (kits iniciais,
    sem consumidor) e 21 class-features avulsas. Os `draconic-exemplar` (44), `tactic` (37) e os gates
    do Kineticist SAIRAM da lista em 31/07. LICAO: a pergunta nao e "quem cita este registro", e "por
    qual caminho o jogador chega nele" -- e sao quatro. || TEXTO ANTERIOR PRESERVADO ABAIXO.
    CAUSA RESOLVIDA 2026-07-30 (commit 9c86ee6c3, spec escolha-multipla-e-ikons). O eixo `ikon` do
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
  date: '2026-07-29'
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
  priority: baixa
  desc: 'FATIA 0, A DERIVACAO DO EIXO E O ATOMO `item:slug` FEITOS 2026-07-31 (specs
    2026-07-31-escolha-aninhada-do-inventor.md, 2026-07-31-tag-e-eixo-por-query.md e
    2026-07-31-atomo-slug.md). O eixo por query deixou de ser LISTA A MAO e passou a ser DERIVADO:
    toda class-feature que a progressao concede e que tem `ChoiceSet` com `filter` e um eixo declarado
    pela fonte -- sao 41 na base. A lista a mao ja tinha cobrado o preco: cobria `Tactics` (nv 1) e deixava
    `Expert`, `Master` e `Legendary Tactician` de fora, e por isso 23 das 37 taticas seguiam inalcancaveis
    DEPOIS do passo que deveria alcanca-las. Com a derivacao sao 9 eixos (Commander 4 tiers: 14/21/26/31
    taticas; Kineticist 5: kinetic-gate + 4 thresholds, 6 cada). A GUARDA que impede duplicata e derivavel
    tambem: o eixo so nasce se o filtro alcanca registro hoje INALCANCAVEL -- e por isso o eidolon do
    Summoner foi corretamente PULADO (ja entra pelo slot de ator), assim como bloodline do Feiticeiro,
    druidic-order do Druida e animistic-practice do Animista. || `item:slug` FECHADO, E A PREMISSA DO
    ITEM ESTAVA ERRADA: nao eram 74 usos (regex antigo cortava em espaco), sao 79, e implementa-lo no
    `_atomo_de_filtro` nao mudaria NADA -- o atomo nao e avaliado la. 60 vivem em `grants/choice` de
    `tipo: spell`, e `slots_concedidos` so coleta `tipo == "feat"`; mesmo coletando, a ficha nao modela
    QUAIS magias o personagem sabe (`_conjuracao` entrega capacidade -- slots, tradicao, DC -- e nao ha
    campo de magia conhecida em nenhum dos dois motores), entao o slot nao teria onde pousar. Outros 3
    apontam para ARMADURA (`Armiger''s Protection`) e nao existe caminho de remap de armadura. SOBRARAM
    DOIS, e eram numero errado na ficha: `Sister of the Golden Erinys Dedication` trata `asp-coil` e
    `scourge` (as duas marciais) como SIMPLES, e `_arma_casa` nao conhecia o seletor `slug` -- um Clerigo
    com a dedicacao lia untrained nas duas. Corrigido nos dois motores (`slug` tem a mesma semantica de
    `base`), com ficha de validacao propria e verificacao de navegador (+0 -> +4, espada longa de controle
    intacta). A ambiguidade que o item temia NAO existe: o atomo TESTA o candidato, nao aponta para
    registro. Os 69 atomos estaticos resolvem 100%% contra a base (55 por id, 14 por alias; os 5 restantes
    sao nomes pre-remaster ja aliasados). SOBRA: (a) o slot de escolha de MAGIA -- 10 blocos, 11 registros
    (`Dragon Spit`, `Hag Magic`, `Arcane Tattoos`...) que nunca sao perguntados ao jogador; depende de a
    ficha modelar magia conhecida, que e decisao de produto do Igor e nao existe hoje; (b) remap de
    ARMADURA, inexistente (3 atomos); (c) `Manifold Modifications` (feat nv 8, 17 opcoes) fora do eixo por
    ser feat e nao progressao; (d) as fatias 2 a 4, que somam 20 queries exatas e ZERO opcao nova; (e) 202
    opcoes de balaio sem explicacao -- item 69; (f) defeito de fonte `item:slug:dispel magic` (com espaco),
    em `wb:feat/methodical-magic`, no ramo de magia que nao e avaliado.'
- desc: 'FEITO 2026-07-31 (spec specs/2026-07-31-slot-concedido-generico.md), a pedido do Igor: nao
    tratar magia como caso especial e sim PADRONIZAR -- toda habilidade que concede escolha abre um slot
    com filtro, do mesmo jeito. Confirmado contra o Pathbuilder, que faz igual: o painel de nivel dele e
    uma lista de pendencias (`Set Abilities`, `Skill Training`, `Heritage`, `Class Feat`) e nao um mecanismo
    por familia. O motor lia so `tipo == "feat"` (43 blocos) e ignorava os outros 26: spell 11, heritage
    7, action 4, weapon 2, ancestry 1, deity 1 -- quem pegava `Dragon Spit` nao escolhia truque nenhum.
    Sao 69 blocos, todos com filtro e nenhum com lista solta. REGRA: o `tipo` estreita quando existe kind
    com aquele nome, o filtro estreita depois, e um cobre o buraco do outro -- sem kind, `Adopted Ancestry`
    (cujo filtro e so referencia dinamica de ator) oferecia os 19.606 registros da base; sem filtro, as
    taticas do Commander sumiam, porque `action` nao e kind. ACHADOS DE TABELA: (a) o default "atomo ignorado
    conta como SATISFEITO" e seguro sob and/or, onde ALARGA, e se INVERTE sob `not`/`nor`, onde reprova
    tudo -- `Adopted Ancestry` nascia com slot VAZIO; agora clausula so de desconhecido nao decide o NAO;
    (b) `feat_concedido` NUNCA foi renderizado pela UI, nem para feat: o motor abria o slot desde a spec
    de 30/07 e a tela nunca desenhou, entao quem pegava `Ancient Elf` nao era perguntado nada -- consertado
    junto, com helpers de doc por `flag` (a identidade do slot nao e o nivel: dois concessores caem no
    mesmo). `item:slug` deixou de ser codigo morto e virou requisito. SOBRA: (a) 25 blocos sem `tipo` na
    fonte nenhuma (`Assurance`, dedicacoes de multiclasse) -- sem `itemType` o pool nao e derivavel por
    regra, cada um precisa de resposta propria; (b) [RETIRADO 2026-07-31] a lacuna de leitura de `itemType` NAO EXISTE:
    a medicao pareava por REGISTRO em vez de por BLOCO, e registro com duas escolhas (uma com itemType,
    lida certo, e outra sem) entrava na conta. Pareando por bloco com o `filtro` verbatim como chave, o
    numero e ZERO -- o extrator esta certo; (c) a conjuracao do personagem segue como CAPACIDADE, sem lista de magias, e a assimetria
    e consciente.'
  id: 106
  date: '2026-07-31'
  priority: baixa
- desc: 'CAUSA RAIZ ACHADA E METADE FECHADA 2026-07-31 (spec specs/2026-07-31-gemeo-do-grant-item.md).
    A hipotese do item -- "por as 37 na PROGRESSAO da classe" -- estava ERRADA: o Foundry nao as lista
    nas `items` da classe (Ranger tem `Hunt Prey@1` e `Hunter''s Edge@1`, sem `Warden Spells`; Alquimista
    tem `Alchemy@1`, sem `Advanced Alchemy`). Elas sao SUB-FEATURES concedidas pela mae, e a mae as
    declara: `Alchemy -> GrantItem classfeatures.Item.Advanced Alchemy`. || O DEFEITO:
    `converter_rule_elements.py` resolvia o UUID SO POR NOME, e o indice `por_nome` PREFERE `feat` no
    desempate -- entao com o Foundry dizendo `classfeatures.Item.X` a base gravava `wb:feat/X` e o
    class-feature ficava inalcancavel. E o achado do item 100, agora com a causa. Medido: 548 GrantItem
    com pack conhecido, 23 nomes existem em dois kinds, **6 estavam no kind ERRADO**. O outro caminho
    (`unificar_efeitos.resolver_grant_item`) JA usava o pack; faltava alinhar este. || E A QUEBRA QUE O
    ITEM 100 PREVIU ACONTECEU: corrigido o alvo, `efficient-alchemy` (que cita o FEAT) deixou de ser
    atendido por um Alquimista 8. Conserto e o prescrito la -- `equivale_a` entre os 4 pares --, e o `has`
    passa a aceitar o gemeo nos dois sentidos. O indice de gemeos e CACHEADO na Base: a primeira versao
    varria os 19.606 registros a cada `has` e o oraculo passou de segundos para +6 minutos. || SOBRAM 33:
    nao tem gemeo concedido, e a mae que os concederia (`Cause`, do Campeao) usa `GrantItem` com UUID
    DINAMICO (`{item|flags.system.rulesSelections.cause}`) -- aponta para o que o jogador escolheu, e o
    extrator pula os 163 casos assim, corretamente. Resolver pede interpretar a escolha no build, outra
    familia. || RE-MEDIDO 2026-07-31 E ESTE PARAGRAFO ESTA ERRADO EM DUAS COISAS (spec
    specs/2026-07-31-grant-condicional.md). (1) "os casos assim" nao sao uma familia: sao 221 hoje, em
    DUAS formas. 206 usam `{item|...}` com o `ChoiceSet` da flag NO MESMO ITEM -- "conceda o que foi
    escolhido neste eixo", que e identidade e o nosso eixo ja modela; o proprio `Cause` e desses, e
    `wb:class/champion` TEM `subclasses[eixo=cause]` com as sete causas. Pular foi certo, e implementar
    seria conceder de novo o que a escolha ja deu. Sobra 1 orfa real (`Runtsage`). As outras 15 usam
    `{actor|flags.system.<classe>.<flag>}` -- a escolha vive em OUTRO item -- e essas NAO pedem
    interpretador: a opcao declara o mapa inteiro estaticamente (`Cloistered Cleric` escreve as 6
    doutrinas), sao 79 pares, 64 acionaveis. (2) A FAMILIA DO CAMPEAO ESTA ERRADA: o que prende ali nao e
    UUID dinamico, e `GrantItem` com `predicate` (balde de 293) somado a `Retributive Strike` /
    `Liberating Step` nao existirem na base -- pack `actionspf2e` nao extraido, item 111.'
  id: 107
  date: '2026-07-31'
  priority: media
- desc: 'FECHADO 2026-07-31 (spec specs/2026-07-31-pericia-de-recall-knowledge.md). Achado por 12 sondas
    de `skill_feat` em PARALELO, a primeira vez que a bancada cobriu skill feat fora de Fighter/Rogue.
    Tres feats se ofereciam a quem nao podia pega-los porque a clausula real vivia em `requires_residuo`
    e o `requires` guardava so o gate de nivel: `automatic-knowledge` (expert), `dubious-knowledge`
    (trained) e `masterful-obfuscation` (master), todos "in a skill with the Recall Knowledge action".
    A forma e quantificada -- nao nomeia pericia, pergunta se EXISTE alguma com o rank --, entao virou
    `skill:recall-knowledge`, mesmo desenho de `lore:*` (item 95) e `weapon:*`. A lista das oito e RAW e
    vive no motor como constante; Perception e Athletics ficam FORA, e e isso que faz o termo discriminar.
    Qualquer Lore conta. || ERRO MEU QUE O TESTE PEGOU, e que eu tinha cometido em DOIS passos: envelopei
    o termo novo em `{"and": [...]}` e o avaliador so conhece `all`/`any`/`not` -- chave desconhecida no
    topo do predicado passa em SILENCIO, entao o gate inteiro virava no-op e os tres seguiam disponiveis.
    Consertado nos dois passos (`derivar_pericia_de_recall` e `derivar_variante_por_subclasse`) e nos 3
    registros que ja tinham o envelope inerte. || PROVA NA BANCADA: `Automatic Knowledge` e `Masterful
    Obfuscation` SUMIRAM das divergencias (598 -> 582 pontos). O que resta e a diferenca de modelo ja
    declarada -- o Pathbuilder conta escolha de pericia pendente como alcancavel.'
  id: 108
  date: '2026-07-31'
  priority: baixa
- desc: 'FECHADO 2026-07-31 (spec specs/2026-07-31-gate-elemental-do-kineticist.md). Era o MAIOR defeito
    unico da bancada: 24 das 314 divergencias contra o Pathbuilder eram impulsos do Kineticist que nos
    oferecíamos e ele recusava, com ele certo. O `requires` de um impulso dizia so `class_level:
    {kineticist: >= 1}` e NADA exigia o elemento -- um Kineticist de Ar e Fogo via os 116 impulsos,
    inclusive os de Madeira e Metal. Agora cada impulso exige `has` do gate de cada elemento no seu trait:
    111 gateados, 16 deles `composite`. A REGRA E DA FONTE, verbatim do dump do AoN: "You can gain an
    impulse with the composite trait only if your kinetic elements include ALL the elements listed" --
    entao `all`, nunca `any`, e `Desert Wind` (ar+terra) e recusado a quem so tem ar. Os 5 agnosticos
    (`Command Elemental`, `Counter Element`, `Purify Element`, `Fearsome Familiar`, `Imperious Aura`)
    ficam INTOCADOS, e e isso que prova que a regra nao gateia tudo. || O termo e `has` e nao `subclass`:
    medido, `subclass` responde False ate para o gate escolhido, porque o eixo `kinetic-gate` e
    `escolhe: 2` e o termo foi desenhado para eixo de escolha unica. || PROVA NA BANCADA: os 24 impulsos
    SUMIRAM das divergencias; 582 -> 558 pontos, e as divergencias distintas caem de ~100 para 74.'
  id: 109
  date: '2026-07-31'
  priority: baixa
- desc: 'ABERTO 2026-07-31 pelo item 84. CLASSE DE DEFEITO, nao lista de consertos: par AoN/Foundry da
    MESMA entidade que vive como DOIS registros na base, um com `prov.name=aon` e outro `prov.name=foundry`,
    porque nenhum mecanismo os junta -- `derivar_alias_legado` le `legacy_id` e nao ha; o colapso de irmaos
    casa por NOME e os nomes divergem por uma letra, um plural ou um artigo. Ja custou tres vezes: item 85
    (Tian Xia, dois pares curados a mao), item 107 (mesmo sintoma por OUTRO mecanismo -- o pack do UUID
    escolhendo o kind errado) e agora 8 pares do item 84. NAO CURAR A MAO: medir a classe inteira primeiro
    -- varrer a base por pares com `prov.name` divergente, mesmo livro, nivel igual ou proximo e nome
    similar, e ver se sao 8 ou 80. So depois decidir entre passo de fusao novo e curadoria. DOIS ALVOS
    SEPARADOS: (a) a grafia divergente, que e o grosso; (b) a GUARDA de campo estruturado divergente em
    `fundir_renomeados.py`, que vetou uma fusao CORRETA quando o AoN dizia `remaster_id` explicito nos dois
    sentidos (`deepest-wellspring` nv18 -> `amp-focus` nv12) -- vinculo explicito da fonte deveria vencer
    a guarda de nivel. IMPACTO NA FICHA, medido: `voice-of-elements` (foundry) tem 7 grants e
    `voice-of-the-elements-kineticist` (aon) tem 0, entao QUAL dos dois o jogador escolhe muda o que ele
    recebe. || MEDIDO 2026-07-31 (docs/medicoes/2026-07-31_classe-pares-nao-fundidos.md, mais medicao
    propria de conferencia). RESPOSTA DA PERGUNTA QUE DECIDE: **passo novo, nao curadoria** -- a ordem de
    grandeza e de centenas, nao de 8. Mas a classe tem DUAS GRAVIDADES e elas nao devem ser consertadas
    juntas: (a) CONTEUDO PARTIDO, 8 pares, onde os dois lados divergem em `grants` e escolher um ou outro
    muda o que o jogador recebe -- e o unico grupo que poe numero errado na ficha; (b) RUIDO DE CATALOGO,
    a familia `Wand of X`: **107** grupos (varinha + rank) que tem lado `aon` E lado `foundry`, conferido
    com criterio proprio. Cada grupo tem TRES registros, nao dois -- `(2nd-Level Spell)` legado e
    `(2nd-Rank Spell)` remaster, os dois do AoN, mais `(2nd-Rank)` do Foundry --, entao a familia sozinha
    infla o catalogo em ~200 registros. Nivel bate em 100% dos 107 e `grants` e 0 nos tres lados: nao ha
    numero errado, ha busca poluida. || A GUARDA DE `level` EM `fundir_renomeados.py`: o relatorio do
    agente disse 22 vetos indevidos; medindo direto no dump do AoN o quadro e outro e MAIOR. Dos 11.367
    pares `legacy->remaster`, **8.465 sao 1:1** e **2.902 sao N:1**. Entre os 1:1, **183 tem `level`
    divergente** -- `Animal Elocutionist` nv5->nv1, `Divine Health` nv4->nv2, `Sanctify Water` nv7->nv2.
    A DISTINCAO QUE NINGUEM FEZ, e que e o conserto: o sinal de identidade nao e "o `level` bateu", e a
    CARDINALIDADE. Em par 1:1 declarado pelo AoN, `level` divergente e rebalanceamento de edicao e
    esperado -- a guarda esta lendo o campo errado. Em N:1 a guarda esta CERTA e fica: os graus de item
    (`winter-wolf-elixir` + `-moderate` + `-greater` -> `witchwarg-elixir`) apontam todos para o mesmo
    alvo, e fundir apagaria dado. Dos 392 vetos totais, a amostra visivel no relatorio (60) tem 30 por
    `level` e 30 por `kind`, e os de `kind` (class-feature x class) sao ruido do proprio AoN, veto certo.'
  id: 110
  date: '2026-07-31'
  priority: alta
- desc: 'ABERTO 2026-07-31 pela spec do grant condicional. O pack `actionspf2e` do Foundry NAO E LIDO por
    extrator nenhum e nao ha kind `action` na base -- e ele e pre-requisito de duas classes. MEDIDO: (a)
    as 9 deeds do Gunslinger (`Ten Paces`, `One Shot, One Kill`, `Clear a Path`, `Living Fortification`,
    `Covered Reload`, `Raconteur''s Reload`, `Reloading Strike`, `Touch and Go`, `Spring the Trap`) sao
    alvo dos pares de grant condicional e nao existem: das 10 concessoes do Gunslinger so 1 tem onde
    pousar; (b) `Retributive Strike` e `Liberating Step`, que as causas do Campeao concedem, tambem nao
    existem -- e e ISSO que prende o Campeao, nao o UUID dinamico que o item 107 acusou. Bloqueia a parte
    Gunslinger/Campeao da spec `2026-07-31-grant-condicional.md`. Decidir junto: `action` vira kind
    proprio (o censo do AoN ja acusou `tactic` e `class-kit` assim) ou as acoes entram como
    `class-feature`. O item 106 ja tinha esbarrado nisto de lado ("`action` nao e kind") sem abrir item.
    || TERRENO MEDIDO 2026-07-31 (docs/medicoes/2026-07-31_terreno-pack-actions.md). O pack e
    `packs/pf2e/actions/` em disco: **557 docs**, 100% com `publication`, sem campo de nivel. **317
    (56,9%) sao de CONSTRUCAO** -- alvo de 353 referencias estaticas de `GrantItem` vindas de
    class-features/feats/heritages/ancestries/backgrounds; as outras 240 sao vocabulario RAW de mesa
    (Stride, exploracao, downtime) e ficam fora. Os 11 alvos existem nas tres fontes; Foundry como
    primaria, igual a `tactic`. DECISAO: **kind proprio `action`** -- mesmo padrao de `tactic`/`class-kit`,
    formato que `class-feature` nao cobre, e o motor JA tem gancho (`candidatos()` atende 4 blocos
    `itemType=action` do item 106). Custo no payload 14-40 KB gzip contra nucleo de 0,529 MB: irrelevante.
    Efeito colateral conhecido: `action` esta em `FORA_DE_ESCOPO` no portao 9 e sai de la junto.
    || DOIS ACHADOS QUE CORRIGEM A MEDICAO ANTERIOR: (a) as 10 deeds do Gunslinger tem `GrantItem`
    ESTATICO na propria `Way of X`, e nao dependem do mecanismo condicional -- so os 2 feats leitores
    (`Slinger''s Readiness`, `Practiced Reloads`) dependem. Mas o grant estatico carrega
    `predicate: [class:gunslinger]` e cai no balde dos 293 pulados, entao os dois caminhos estao
    bloqueados, por motivos diferentes; (b) `Into the Fray` NAO existia na base -- `wb:feat/into-the-fray`
    e outro registro, nv8 trait `archetype` do Player Core 2, e casou por COLISAO DE NOME. Minha medicao
    de 31/07 contou como alcancavel: sao 10 alvos ausentes no Gunslinger, nao 9. Familia do portao 7.
    || IMPLEMENTADO 2026-07-31 (extratores/acoes.py). **520 registros**, nao 557: as 37 taticas do
    Commander saem porque JA sao extraidas como `kind: tactic` -- traze-las aqui criava 37 pares "mesma
    entidade, dois kinds", a classe do item 110 fabricada por nos, e o oraculo pegou. Efeito medido:
    `GrantItem sem alvo na base` caiu de **290 para 27** e os grants convertidos subiram de 556 para 819
    (+263 concessoes que nao pousavam em lugar nenhum). Os 10 portoes passam, oraculo verde, iconics
    identicos (118/136 no HP), pericia identica (62,9%). TRES ACHADOS DE PERCURSO: (a) traduzir
    `tipo: action` para o kind `action` sozinho ESVAZIAVA os 4 blocos de tatica do Commander (21 -> 0),
    porque no Foundry tatica E `type: action` e aqui e `kind: tactic` -- o `tipo` passa a alcancar os
    dois kinds, nos dois motores; (b) meu indice do AoN usava `setdefault` e escolhia 1 entre N em
    silencio, o defeito que o portao 7 existe para pegar (`Retributive Strike` tem dois docs no AoN);
    agora so casa quando e INEQUIVOCO, e 173 ficam com xref vazio de proposito; (c) o falso positivo do
    `Into the Fray` desapareceu.
    || CORRECAO DE REGISTRO 2026-07-31, apos auditoria adversarial
    (docs/2026-07-31_auditoria-estado.md): eu registrei este item como ENTREGA CHEIA e ele NAO ESTA.
    A **Decisao 5 da spec -- traduzir os 26 `predicate` de `class:`/`feat:` -- nao foi implementada**, e
    com ela caem as provas 2, 3, 4 e 5 da propria spec. Verificado: `wb:class-feature/justice` e
    `wb:class-feature/liberation` seguem com `grants: []`, `way-of-the-drifter` so tem a proficiencia, e
    ha ZERO registros com `grants[].se` na base. Ou seja: o Campeao e o Gunslinger, que sao a
    motivacao-titulo da spec, continuam sem receber nada. O que ENTROU foi o kind `action` e as
    integracoes (extrator, `PACK_PARA_KIND` nos dois caminhos, portao 9, `montar_ficha`) -- e isso
    sozinho ja rendeu 290 -> 27 e 556 -> 819. O que FALTA depende de `grants[].se`, que vive na spec do
    grant condicional: as duas specs se cruzam e nenhuma das duas fecha sozinha.
    || DEFEITO NOVO INTRODUZIDO POR MIM, e ja consertado: o conserto do caminho em
    `recuperar_mecanica_equipamento` ACORDOU um bug antigo da fonte -- o dump do AoN traz
    `damage_type: ["Piercing"]` hardcoded nas 11 armas de combinacao `(Melee)` mesmo quando a string diz
    outra coisa (`Gun Sword (Melee)`: `damage: "1d8 S"` e `damage_type: ["Piercing"]` no MESMO doc). O
    passo lia o campo estruturado e gravou `piercing` em arma cortante: trocou um `None` honesto por um
    valor errado PLAUSIVEL, que e pior porque ninguem desconfia. Corrigido lendo a LETRA da string
    (`S`/`B`/`P`), com `damage_type` so como desempate. As 11 voltaram ao certo (Axe Musket, Black Powder
    Knuckle Dusters, Bow Staff, Cane Pistol, Crescent Cross, Gnome Amalgam Musket, Gun Sword, Hammer Gun,
    Mace Multipistol, Mikazuki, Piercing Wind).'
  id: 111
  date: '2026-07-31'
  priority: alta
- desc: 'ABERTO 2026-07-31 pelo review adversarial da spec do grant condicional. BUG ATIVO NA FICHA, e
    nao divida de modelagem: 9 backgrounds tem `ChoiceSet` de escolha 1-de-2 na fonte (skill + feat
    correspondente, `{"label": "Athletics", "value": {"feat": "Titan Wrestler", "skill": "athletics"}}`)
    e a base NAO modela a escolha. Tres sintomas do mesmo defeito, medidos um a um: FEAT A MAIS -- 4
    concedem OS DOIS (`beast-seeker` da `titan-wrestler` E `dirty-trick`, idem `child-of-the-polis`,
    `glory-hound`, `obari-wanderer`); FEAT ARBITRARIO -- 1 concede so o primeiro sem o jogador escolher
    (`anti-thrune-saboteur` -> `lengthy-diversion`); FEAT PERDIDO -- 4 concedem ZERO (`child-of-notoriety`,
    `conservator`, `dedicated-delver`, `historical-reenactor`). O padrao na fonte e `GrantItem` com UUID
    dinamico de SUB-CAMPO (`{item|flags.system.rulesSelections.choice.feat}`), que o extrator pula junto
    com os outros dinamicos -- e como o `value` da opcao e um objeto, o alvo nao e a opcao escolhida e sim
    um CAMPO dela. Familia do slot concedido generico (item 106), nao do grant condicional. O review
    estimou 19; medicao propria contra fonte e base deu 9, dos quais 8 com sintoma visivel.'
  id: 112
  date: '2026-07-31'
  priority: alta
- desc: 'ABERTO 2026-07-31, achado ao regenerar a base para o item 111. `recuperar_mecanica_equipamento.py`
    estava QUEBRADO NAS DUAS FONTES, e em silencio -- imprimia `fontes: foundry=0 itens, aon=0 itens` e
    seguia. (a) `do_foundry` usava caminho FIXO `dados_brutos/foundry/packs/...` quando nesta maquina o
    clone e `foundry_repo/`: e exatamente a armadilha que `comum.packs_foundry()` existe para resolver, e
    este passo ficou de fora da correcao que ja tinha alcancado portoes, emitir_textos, aplicar_subclasses
    e converter_rule_elements. (b) `do_aon` procurava `aon_equipment_weapon.json` e irmaos, nomes que nao
    existem desde que a fonte foi refeita dentro de `dados_brutos/` -- o dump grava `aon_dump/weapon.json`.
    CUSTO MEDIDO: **53 armas perdiam `damage` a cada rebuild**, `Blowgun`, `Fist` e `Shield Bash` entre
    elas, e a base versionada sobrevivia so porque carregava o dado de um build ANTIGO, feito quando o
    clone tinha o outro nome. Ninguem teria notado ate a proxima regeneracao. CONSERTADO no mesmo dia
    (foundry 0 -> 1.328 itens, aon 0 -> 399) e o oraculo voltou a passar. O QUE FICA ABERTO: nenhum portao
    cobre PERDA DE CAMPO. O portao 4 conta registros por kind e nao viu 53 armas ficarem sem dano; o 8
    cobre artefato de disco, nao campo. Um portao de campo critico por kind (`damage` em weapon,
    `ac_bonus` em armor/shield, ja declarados em `CRITICO` no proprio passo) e o que teria pego isto na
    hora -- e o mesmo desenho do portao 11 que a spec do grant condicional pede.
    || FECHADO 2026-07-31 (spec specs/2026-07-31-portao-de-campo-critico.md). **Portao 11** conta CAMPO
    por kind e falha quando o numero CAI vs o build anterior -- mesma semantica do 4, um nivel abaixo.
    Linha de base gravada: `weapon.damage` 986, `armor.ac_bonus` 206, `shield.ac_bonus` 118, no MESMO
    `_cobertura.json` do portao 4 (linha de base em dois arquivos e um arquivo para esquecer de gravar).
    O dict de campos criticos e IMPORTADO de `recuperar_mecanica_equipamento.CRITICO`, nunca copiado --
    duas listas do mesmo conceito divergem, foi assim que o `DEFAULT` do comparador ficou em 13 classes
    com o jogo em 27. PROVA: base intacta passa; tirando `damage` de 53 armas o portao 11 FALHA
    (`weapon.damage: 986 -> 933`) e o portao 4 na MESMA base sabotada PASSA -- que e a medida exata da
    cegueira que existia. E "caiu?" e nao "existe?" de proposito: 102 registros seguem sem campo critico
    por razao legitima (bomba com dano por formula, item de aventura), e portao que nasce vermelho e
    desligado na primeira semana. ACHADO DE PERCURSO: a primeira versao criou impasse de bootstrap --
    o portao devolvia `nao medido` sem linha de base, e a guarda de `--gravar-cobertura` se recusa a
    gravar com portao nao medido, entao a linha nunca nasceria. `None` ficou so para o arquivo INTEIRO
    ausente; chave nova em arquivo existente e primeira medicao e passa. SOBRA DECLARADA: so tres campos
    em tres kinds (`spell.rank`, `feat.level`, `class.progressao` ficam de fora ate alguem medir quantos
    ja nascem vazios); o portao ve campo AUSENTE, nao campo ERRADO; e o alarme na ORIGEM continua
    faltando -- o passo que le fonte e acha zero itens ainda imprime e segue.'
  id: 113
  date: '2026-07-31'
  priority: alta
- desc: 'ABERTO 2026-07-31, achado ao rodar a terceira camada depois do item 111.
    `docs/2026-07-27_simulacao-raw.md` versionado declarava **violacoes: 0**, e a base ja produzia
    **343**. Nao foi regressao: medido isolando as duas variaveis -- motor do HEAD sobre a base nova da
    343, e motor novo sobre a base do HEAD da 343 tambem. O relatorio em disco e que era velho, gerado
    antes de os eixos de dragao nascerem (`dragon-instinct-type`, `draconic-bloodline-type`,
    `wyrmblessed-bloodline-type`, spec de 31/07). A DIVIDA REAL: `Barbarian` e `Sorcerer` tem eixo
    obrigatorio no nivel 1 que nao gera aviso quando fica sem escolha -- o simulador esta certo em
    cobrar, e o `simular_raw.py` nao roda no `build.sh`, entao ninguem viu. MESMA CLASSE DO ITEM 84:
    arquivo velho parado em disco fingindo cobertura. Duas coisas a decidir: (a) o aviso de eixo
    obrigatorio sem escolha, que e o defeito de verdade; (b) por o simulador no `build.sh` ou num portao,
    senao o proximo relatorio envelhece igual.'
  id: 114
  date: '2026-07-31'
  priority: media
- desc: 'FECHADO 2026-07-31 (spec specs/2026-07-31-slots-de-criacao-na-tela.md). DOIS DEFEITOS RELATADOS
    PELO IGOR TESTANDO O APP, os dois da mesma familia do item 106 -- o motor abre o slot e a tela nao
    desenha. (a) "n tem como colocar +2 em nada": o `BoostPicker` mostrava UMA fileira de seis botoes com
    toggle, entao clicar STR duas vezes desmarcava. O motor ja entregava as fontes SEPARADAS em
    `visao.boosts.fontes` (Human 1, Human 1, Fighter chave 1 com `opcoes: [dex,str]`, criacao 4 livres) e
    a tela descartava o campo inteiro. A regra de PF2e que a fileira unica achatava: boost do MESMO bloco
    vai para atributo diferente, blocos DIFERENTES podem cair no mesmo -- e e assim que se chega a +2.
    Agora e uma linha por fonte. (b) "n tem como upar pericias": `grep -rn pericias_livres app/src/` fora
    do motor dava ZERO, e `candidatos()` NAO conhecia o slot em nenhum dos dois motores -- caia no `else`
    final e devolvia FEATS. O slot existia em `slots_abertos()` desde 29/07 e nunca foi perguntado.
    || ACHADO DE PERCURSO: compactar as escolhas de boost (gravar so as preenchidas) fazia o mapeamento
    fonte->escolha DESLIZAR no primeiro buraco. Posicao vazia agora e `pega: []`, e foi medido que o
    motor a ignora na soma e nao a conta em `declarados`. || VERIFICADO NO NAVEGADOR
    (`app/verificacao/verificar-slots-de-criacao.mjs`, 10 checagens): STR em duas fontes da +2, a linha
    da chave oferece 2 atributos e nao 6, o bloco de 4 livres bloqueia o repetido, os 3 slots de pericia
    aparecem e oferecem PERICIA. As fixtures passavam verdes o tempo todo -- os dois defeitos eram so da
    tela, e so a quarta camada os pegaria.'
  id: 115
  date: '2026-07-31'
  priority: alta
- desc: 'DECISAO DE PRODUTO DO IGOR, 2026-07-31: o app tem de deixar ESCOLHER MAGIA, como o Pathbuilder --
    "n pode me dizer so q tenho os slots, clerigo precisa da font e tudo mais". Ele avisou que nao precisa
    resolver agora. ISTO DESTRAVA ITENS QUE ESTAVAM PARADOS ESPERANDO ESTA DECISAO, e o texto deles diz
    isso com todas as letras: item 105 -- "a ficha nao modela QUAIS magias o personagem sabe (`_conjuracao`
    entrega capacidade -- slots, tradicao, DC -- e nao ha campo de magia conhecida em nenhum dos dois
    motores), entao o slot nao teria onde pousar... e decisao de produto do Igor e nao existe hoje", com
    10 blocos e 11 registros (`Dragon Spit`, `Hag Magic`, `Arcane Tattoos`) que nunca sao perguntados;
    item 106 -- "a conjuracao do personagem segue como CAPACIDADE, sem lista de magias, e a assimetria e
    consciente". VERIFICAR JUNTO: a fonte divina do Clerigo (`divine-font`) FOI implementada no item 98
    (eixo de divindade, `deity_font`, commits 69d2df0f5 e bed0f5754) -- se ela nao aparece na tela, e a
    mesma familia do item 115 (motor abre, tela nao desenha) e nao falta de dado. Escopo a decidir:
    magia conhecida (repertorio) x preparada por dia sao modelos diferentes, e `Versatile Font` precisa
    de CONCESSAO de escolha, ja declarada como outra familia no item 98.'
  id: 116
  date: '2026-07-31'
  priority: alta
promoted: []
---
