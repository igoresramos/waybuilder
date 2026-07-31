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
- desc: 'RE-MEDIDO PELA TERCEIRA VEZ EM 2026-07-31, e as duas medicoes anteriores estavam erradas por
    METODO. Contar "registro nunca citado por outro" da 15.771 de 19.606 -- numero sem sentido, porque
    99%% do equipamento nao e citado por ninguem: ele se escolhe do CATALOGO. Existem QUATRO caminhos
    de alcance, e nao um: (a) citacao por outro registro; (b) KIND -- slots que varrem um kind inteiro
    (equipamento, magia, feat, companheiro, familiar, eidolon, divindade...); (c) FILTRO -- os eixos por
    query criados em 31/07, que resolvem por `_casa_filtro`; (d) o GEMEO `equivale_a`, que o passo de
    colapso cria. Com os quatro, o numero real e **1.204**. O topo dele e catalogo puro e NAO e defeito:
    trait 551, relic 122, language 121. O que sobra de acionavel: `familiar-ability` 72 (declarado fora
    de escopo na spec do item 43 -- a escolha diaria de habilidade e recurso por dia, nao construcao),
    `class-kit` 32 (kits iniciais, sem consumidor) e 21 class-features avulsas. Os `draconic-exemplar`
    (44), `tactic` (37) e os gates do Kineticist SAIRAM da lista em 31/07. LICAO REGISTRADA: a pergunta
    nao e "quem cita este registro", e "por qual caminho o jogador chega nele" -- e sao quatro.'
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
  desc: 'FATIA 0 E A DERIVACAO DO EIXO FEITAS 2026-07-31 (specs 2026-07-31-escolha-aninhada-do-inventor.md
    e 2026-07-31-tag-e-eixo-por-query.md). O eixo por query deixou de ser LISTA A MAO e passou a ser DERIVADO:
    toda class-feature que a progressao concede e que tem `ChoiceSet` com `filter` e um eixo declarado
    pela fonte -- sao 41 na base. A lista a mao ja tinha cobrado o preco: cobria `Tactics` (nv 1) e deixava
    `Expert`, `Master` e `Legendary Tactician` de fora, e por isso 23 das 37 taticas seguiam inalcancaveis
    DEPOIS do passo que deveria alcanca-las. Com a derivacao sao 9 eixos (Commander 4 tiers: 14/21/26/31
    taticas; Kineticist 5: kinetic-gate + 4 thresholds, 6 cada). A GUARDA que impede duplicata e derivavel
    tambem: o eixo so nasce se o filtro alcanca registro hoje INALCANCAVEL -- e por isso o eidolon do
    Summoner foi corretamente PULADO (ja entra pelo slot de ator), assim como bloodline do Feiticeiro,
    druidic-order do Druida e animistic-practice do Animista. SOBRA: (a) `item:slug`, 74 usos, ainda ignorado
    no `_atomo_de_filtro`; (b) `Manifold Modifications` (feat nv 8, 17 opcoes) fora do eixo por ser feat
    e nao progressao; (c) as fatias 2 a 4, que somam 20 queries exatas e ZERO opcao nova; (d) 202 opcoes
    de balaio sem explicacao -- item 69.'
promoted: []
---
