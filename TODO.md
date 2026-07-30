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
- desc: 'PARCIALMENTE RESOLVIDO 2026-07-30. O eixo `instinct` do Barbaro saiu da lista de ZERADOS pelo
    lado que importa: escolher instinto agora LIBERA os feats de instinto (commit 7884391ca, spec instinto-com-dois-ids)
    -- antes nenhum dos 25 liberava, porque o requires citava `wb:class-feature/animal-instinct` e a tela
    oferecia `wb:instinct/animal`. ATENCAO A PREMISSA: a conclusao original deste item (''o que falta
    e mecanica de combate, que o principio zero poe fora de escopo'') repousa numa leitura que o IGOR
    DERRUBOU em 2026-07-27: ''eu tinha lido o principio zero como mecanica de combate fica de fora e ESTAVA
    ERRADO. O app e para construir o personagem inteiro... TODOS os numeros na ficha.'' O que sobra (dano
    de rage, DamageDice, DamageAlteration) e mecanica CONDICIONAL, que e outra familia -- essa sim ja
    recusada COM numero duas vezes (ItemAlteration e RollOption em 30/07, `strike-damage` em 30/07). Reavaliar
    sob o escopo corrigido antes de fechar.'
  id: 42
  date: '2026-07-29'
  priority: media
- desc: 'PENSANDO EM CORTAR O ARQUETIPO DE MULTICLASSE (Igor, 2026-07-27) -- NAO FAZER AGORA, so anotado.
    A ideia: permitir apenas arquetipo de DEDICACAO comum e remover os de multiclasse, porque na houserule
    multiclasse ja se faz com nivel de classe -- as duas rotas competem, e a regra 23 acabou de declarar
    que se excluem. Cortar seria a conclusao natural da 23: em vez de marcar conflito caso a caso, some
    a rota duplicada. MEDIDO na base para dimensionar: 244 archetypes, dos quais 27 sao de multiclasse
    (arquetipo cujo nome e nome de classe) e 217 nao; 2.129 feats tem trait `archetype`, 226 tem `dedication`
    e exatamente 27 tem `multiclass` -- os 27 sao as dedicacoes das classes, e nenhum feat nao-dedicacao
    carrega o trait. Os 27 arquetipos de multiclasse tem 195 feats no total. Ou seja, cortar remove 27
    dedicacoes + 195 feats de arquetipo, sobrando 199 dedicacoes e ~1.934 feats. O recorte e DERIVAVEL
    (trait `multiclass`), nao precisa de lista a mao. A VALIDAR antes de decidir: (a) algum feat de arquetipo
    NAO-multiclasse exige um feat de arquetipo de multiclasse como pre-requisito? Se sim, cortar quebra
    a cadeia; (b) o que se perde de conteudo unico -- ha feats de arquetipo de multiclasse que nao tem
    equivalente na progressao da classe (ex: as basic/expert/master spellcasting, que dao slots que nenhum
    nivel de classe da do mesmo jeito); (c) impacto na regra 21, que hoje usa a dedicacao de conjuracao
    como PISO -- se o arquetipo de multiclasse sumir, o piso precisa de outra referencia ou a regra 21
    fica sem chao; (d) o Free Archetype (regra 2) continua ligado e passa a apontar so para os 217 restantes'
  id: 46
  date: '2026-07-29'
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
- desc: 'RE-MEDIDO 2026-07-30, e a hipotese (a) do item NAO se confirma: ZERO das 265 opcoes de `outras-opcoes`
    esta tambem na `progressao` da classe -- nao ha sobreposicao a limpar. O balaio se REPETE POR NIVEL
    (o Alquimista tem 6 blocos `outras-opcoes`, um por degrau), e o bloco de nivel 1 dele mistura tres
    coisas: feature que a CADEIA de grants ja concede (`formula-book` e `versatile-vials` aparecem em
    `p.features` de um Alquimista 1 sem ele escolher nada), gemeo legado/remaster (`infused-reagents`
    virou `versatile-vials`) e variante por sub-escolha (`field-discovery-bomber` etc). A regra do sufixo
    pegou 9 pares no eixo `instinct` (item 42, resolvido) e nao ajuda aqui. SEGUE SENDO CURADORIA CASO
    A CASO, e o proprio item ja decidira nao implementar heuristica parcial para nao quebrar os 11 eixos
    que funcionam. Proximo passo objetivo: para cada opcao do balaio, checar se a cadeia de grants ja
    a concede -- se concede, nao e escolha.'
  id: 69
  date: '2026-07-29'
  priority: media
- desc: '4a RODADA FECHADA 2026-07-30 (Barbaro 6, secao 8 do relatorio docs/2026-07-30_comparacao-pathbuilder-rodada-3.md).
    NENHUM defeito nosso na aba -- 98x99 em class feats, tudo nas familias ja declaradas. O valor veio
    da investigacao do unico item so-dele (`Reckless Abandon`): revelou que o nome antigo nao virava alias
    FORA de magia, e sairam 335 renomeacoes (commit 1ce0d2601, spec alias-legado-fora-de-magia). PROXIMAS
    RODADAS: general_feat fora do Guerreiro e do Bardo; o quantificador ''uma pericia que tenha a acao
    X'' (Automatic/Dubious Knowledge); e classes ainda nao comparadas -- Champion, Druid, Sorcerer, Alchemist,
    Investigator (o DEFAULT do comparador tem 8).'
  id: 84
  date: '2026-07-29'
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
    <prosa>` nao aparece em nenhum dos 28 registros que tem residuo e nenhum requires). SOBRA: as 19 clausulas
    de divine font, que dependem do item novo 98 (a ficha nao tem divindade). Alinhamento segue recusado
    -- conceito que o Remaster aboliu.'
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
- desc: 'RE-MEDIDO 2026-07-30 por agente, e o achado e MAIOR que o item. Confirmadas as 48 class-features
    inalcancaveis. Mas os 26 pares com irmao de mesmo slug nao sao o problema: TODOS os 21 registros do
    kind `ikon` e TODOS os 15 do kind `mythic-calling` sao inalcancaveis, com ou sem par. Ou seja, o compendio
    `pf2e.classfeatures` do Foundry mistura Ikons e Mythic Callings com class-features de verdade, e o
    extrator rotulou tudo como class-feature. Padrao unico nos 33 pares: mesmo nome (a menos de capitalizacao),
    mesmo livro, `class: []` em 100%, xref do Foundry SO do lado class-feature. FUNDIR NAO RESOLVE ALCANCABILIDADE
    -- so tira a duplicidade. O que resolve e a CAUSA: o Exemplar concede `divine-spark-and-ikons` no
    nivel 1 e a prosa oficial diz "Select three ikons", mas a classe nao tem eixo de ikon nenhum. O AoN
    tem exatamente 21 docs de ikon, entao nao ha lacuna de conteudo -- ha lacuna de ESCOLHA. BLOQUEIO
    MEDIDO: o eixo precisa de `escolhe: 3` e hoje os 52 blocos da base usam `escolhe: 1`; o motor le UMA
    escolha por bloco (`next((o for o in opcoes if o in escolhidas), None)`) e ignora o campo. Fazer `escolhe:
    N` funcionar mexe em _subclasses, slots_abertos, _termo_subclass e no porte TS -- justamente o trecho
    que ja produziu regressao pega pela paridade. Os 22 sem irmao sao outra coisa: 6 gates do Kineticist
    + elemental-school + advanced-vials-toxicologist sao gap de progressao real; 7 deviant-classification
    tem primo por NOME em `deviant-ability-classification` (kind que tem duplicidade propria nao resolvida);
    3 echoes-of-* e 4 genericos (focus-spells, iron-will, improved-evasion, martial-weapon-mastery) sao
    stubs orfaos.'
  id: 97
  date: '2026-07-30'
  priority: baixa
- id: 98
  date: '2026-07-30'
  priority: baixa
  desc: 'PARTE PRINCIPAL FECHADA 2026-07-30 (commit 69d2df0f5, spec divindade-na-ficha). Entrou: eixo
    `deity` derivado de quem cita `class-feature/deity-*` (Clerigo e Campeao, 488 opcoes), quatro termos
    nos dois motores (deity, has_deity, deity_font, domain), os padroes de parser e a linha da divindade
    na ficha com dominio e arma resolvidos por nome. Residuo de divindade: 54 -> 25 clausulas. SOBRA,
    em ordem de valor: (a) a SUB-ESCOLHA da fonte para as 137 divindades que permitem heal e harm -- hoje
    o motor nao reprova nenhuma das duas (principio zero), e resolver exige um eixo cujas opcoes dependam
    da escolha anterior, que nenhum eixo da base tem; (b) arma favorita / pericia divina / santificacao
    como termo (6 clausulas, o dado ja esta em favored_weapon e sanctification); (c) divindade OPCIONAL
    para quem nao e Clerigo nem Campeao -- `you follow a deity` (4 clausulas) hoje so responde false para
    as outras classes, e um Monge que segue divindade e legitimo em PF2e; (d) alinhamento segue RECUSADO
    -- conceito que o Remaster aboliu.'
promoted: []
---
