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
    vocabulario novo de grant (`concede feature no nivel N`) que nao existe -- mudanca de motor, TS e tela.'
  id: 69
  date: '2026-07-31'
  priority: media
- desc: 'COMPARADOR CONSERTADO 2026-07-31 (spec specs/2026-07-31-colisao-no-comparador.md) -- era a
    pendencia declarada desta task. `norm()` apaga o sufixo de desambiguacao de proposito, mas o codigo
    guardava UM registro por chave e pulava TODOS os que produziam aquela chave: 75 chaves da base
    normalizam igual, envolvendo 205 feats. Agora o veredito e do GRUPO -- se qualquer irmao concorda com
    o Pathbuilder, nao ha divergencia (o desmembrado legitimo continua sem virar sobra falsa); so ha
    divergencia quando NENHUM concorda, e ai sai nomeando todos. E a colisao vai DECLARADA no relatorio
    (`colisoes_de_normalizacao`). Medido antigo x novo sobre a MESMA base, para separar do drift: as
    contagens ficaram identicas em todos os slots, 48 colisoes passaram a ser declaradas em 14 relatorios,
    12 linhas duplicadas sumiram (`Crossbow Infiltrator Dedication` x11, que casava por nome E por alias)
    e 2 FALSOS POSITIVOS caiiram. Os dois falsos positivos sao o oposto do que este item previa: em
    `green empathy` temos dois registros -- `Plant Empathy`, que carrega `Green Empathy` em `aliases` e
    esta disponivel, e o `Green Empathy` de verdade, que nao esta -- e o codigo antigo comparava o irmao
    errado e acusava `wb=true pb=false`. A colisao nao so ESCONDIA ponto do placar: ela INVENTAVA. ||
    RODADA 6 FEITA 2026-07-31 (docs/medicoes/2026-07-31_pathbuilder-rodada-6.md). As 27 classes estao
    cobertas, com ZERO defeitos nossos em 152 pontos triados. ACHADO ESTRUTURAL: oito classes travam o
    Class Feat do nivel 1 atras de escolha de subclasse obrigatoria (Animist, Witch, Magus, Psychic,
    Oracle, Summoner, Druida, Feiticeiro) -- e informacao, nao falha. SOBRA: 3 pares novos de renomeacao
    Golarion->generico para `equivalencias-pathbuilder.json`; os 33 pontos do Kineticist que so confirmam
    o gap dos itens 97/99; e os JSONs de comparacao gravados estavam DEFASADOS em relacao a base (em_comum
    222->224, 223->225, 98->99 so por a base ter crescido) -- proxima rodada comeca regravando as sondas.'
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
promoted: []
---
