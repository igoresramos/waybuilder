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
- desc: 'FATIA 3.2 (Resistance) CONCLUIDA 2026-07-30, spec specs/2026-07-30-resistencia-e-formula.md.
    A ficha nao tinha resistencia, fraqueza nem imunidade -- 233 + 11 + 14 grants
    que o motor ignorava, vindos de feat (125), equipment (59), armor (21), weapon
    (12), shield (9). Agora `visao.resistencias`, `.fraquezas` e `.imunidades`,
    com origem nomeada e a regra do livro de nao-empilhamento (duas fontes do
    mesmo tipo: vale a maior, nao a soma). SAIU JUNTO um defeito mais antigo:
    `_resolver_valor` resolvia so inteiro e `@actor.level`, e QUALQUER outra
    expressao virava ZERO EM SILENCIO -- 68 das 233 resistencias sao formula.
    Virou um mini-avaliador da gramatica medida (inteiro, `@actor.level`,
    `@armor.system.runes.potency`, `+`, `/`, `floor()`, `max()`), e o que estiver
    fora devolve None em vez de zero: zero e uma resposta, None diz "nao sei".
    DEFEITO MEU PEGO PELO DIFF DO FIXTURE: `tipo` e LISTA em 19 dos 258 (Blast
    Resistance protege fire E sonic) e eu convertia para texto cego, escrevendo
    "[''fire'', ''sonic'']" na ficha do campeao6. Uma resistencia a N tipos sao N
    linhas. FICA ANOTADO PARA A PROXIMA FATIA: 18 `flat_modifier` de `land-speed`
    ficam contados como nao modelados -- a velocidade existe na ficha do
    companheiro mas nao como numero do personagem.
    || TEXTO ORIGINAL: CORRIGIDO 2026-07-29 (auditoria): o numero do item estava errado. Nao sao ''175 das 176 sub-escolhas sem efeito'' -- sao 114 de 418 (27%) que JA tem `grants` e que o motor JA aplica, porque `_proficiencias` e `_grants_em_cadeia` leem `self.features`, que inclui a subclasse escolhida. O MECANISMO DE APLICACAO DEIXOU DE SER O PROBLEMA. O que trava sao as 304 opcoes com `grants: []`, e isso e EXTRACAO: converter_rule_elements.py so converteu os 99 declarativos (ActiveEffectLike com path de rank, sem predicate). Falta o grosso -- 1.784 FlatModifier, 1.495 ItemAlteration, 1.113 GrantItem, 1.077 RollOption, 563 ChoiceSet, 337 Resistance. || TEXTO ORIGINAL: SUBCLASSE NAO ALTERA NADA (parcialmente resolvido). Levantado pelo Igor a partir do caso Cloistered/Warpriest: das 176 opcoes de sub-escolha (bloodline 18, patron 24, mystery 12, instinct 16, racket 6, doctrine 3, muse 5, arcane-school 23, cause 13, implement 10...), **175 nao tinham efeito estruturado** -- escolher subclasse nao mudava numero nenhum na ficha. O dado existe: 584 das 841 class-features do Foundry tem Rule Elements. converter_rule_elements.py converteu os 99 declarativos (ActiveEffectLike com path de rank, sem predicate). FALTA o grosso, que depende de reimplementar o interpretador do Foundry: 1.784 FlatModifier, 1.495 ItemAlteration, 1.113 GrantItem, 1.077 RollOption, 563 ChoiceSet, 337 Resistance. E o item que a spec chama de ''maior custo do projeto'''
  id: 40
  date: '2026-07-29'
  priority: alta
- desc: 'CORRECAO DE ESCOPO (Igor, 2026-07-27): eu tinha lido o principio zero como ''mecanica de combate fica de fora'' e ESTAVA ERRADO. O app e para construir o personagem inteiro, como o Pathbuilder -- armas, armadura, pets, e TODOS os numeros na ficha. O que fica fora e retraining e arbitragem de mesa, nao os numeros. Isso reabre o item 42: o dano de rage do Giant Instinct, a penalidade de ataque multiplo do Flurry e a reacao de causa do Champion SAO numeros de ficha e precisam sair. FEITO nesta sessao: AC (com dex_cap, penalidade de armadura, escudo) e ataque/dano por arma equipada -- o dado ja estava na base (931 armas com damage, 202 armaduras com ac_bonus/dex_cap). FALTA: os Atores (companheiro, familiar, eidolon) com stats proprios, runas de potencia/impacto, e o interpretador parcial de rule elements para dano condicional'
  id: 43
  date: '2026-07-29'
  priority: alta
- desc: 'PARCIAL. (b) RESOLVIDO 2026-07-29: o cap de ator ancora na classe que concedeu, via `concedido_por`. (a) e (c) seguem como DECISAO DO IGOR. (a) a regra 17b (teto de invocacao) vale tambem para magia conjurada por slot de dedicacao de arquetipo? (c) a regra 23 (exclusao mutua) deve bloquear qualquer arquetipo que duplique concessao ja dada por nivel de classe -- ex: Beastmaster Dedication num Ranger que ja tem companheiro? DEFAULT ADOTADO no plano de 2026-07-29 enquanto o Igor nao decide: (a) sim, e reversivel num if. || TEXTO ORIGINAL: AMBIGUIDADE A RESOLVER COM O IGOR (2026-07-27, fim de sessao). Ele disse ''a regra que fizemos serve pra dedicacao tambem'' e a frase tem TRES leituras, com implementacoes diferentes. Nao arbitrei. (a) REGRA 17b EM SLOT DE ARQUETIPO -- o teto de invocacao passaria a valer tambem para magia conjurada de slot de dedicacao. Hoje nao vale: a regra 18 diz que Free Archetype roda RAW puro, entao o slot de arquetipo escapa. E a pergunta que ficou aberta duas vezes nesta sessao, inclusive na simulacao, que achou a incoerencia de a mesma magia sair em dois ranks na mesma ficha. Efeito: invocacao vinda de dedicacao pararia no rank do proprio slot em vez de subir por heightened. (b) CAP DE ATOR VINDO DE DEDICACAO -- RESOLVIDO 2026-07-29 pela spec companheiro-concedido: o `grant_actor` guarda o NIVEL em que o feat foi pego, e o nivel diz a classe, entao `_classe_do_ator` ancora na classe que concedeu em vez de chutar a de maior nivel. Num Ranger 3 / Fighter 5 o companheiro do Ranger dava 7 e agora da 5. Ator escrito a mao sem `concedido_por` mantem o comportamento antigo (chute + aviso). (c) REGRA 23 PARA ARQUETIPO NAO-MULTICLASSE -- a exclusao mutua deixaria de ser so entre classe e dedicacao da MESMA classe e passaria a valer para arquetipo comum que duplica concessao da classe, ex: Beastmaster Dedication num Ranger que ja tem companheiro por nivel. Hoje isso e permitido e o personagem fica com dois companheiros. Provavel que a resposta seja (a), porque foi a pergunta que eu deixei explicitamente aberta duas vezes -- mas ''provavel'' nao basta para regra de jogo, e (b) e um defeito de verdade independente da resposta'
  id: 47
  date: '2026-07-29'
  priority: alta
- desc: 'CONCLUIDO 2026-07-30 (commits 7e967b8e8 + este, spec specs/2026-07-30-cobertura-de-grants-completos.md).
    Os 8.360 registros mudos (42,4% da base) viraram ZERO. Eram oito kinds inteiros
    de tres extratores, e nenhum precisava de dado novo -- os tres ja computavam
    a resposta e a jogavam fora dentro do campo `mechanized` da v1. equipamento.py
    (equipment/weapon/armor/shield) tinha `perdeu` vindo de `converter_grants`;
    classes.py tinha `mechanized` para class e o retorno de `montar_grants_feature`
    para class-feature; taticas_kits.py nem era rodado pelo build.sh (a saida em
    disco era de 27/07 e envelheceu em silencio -- entrou no laco de extratores).
    O NUMERO QUE IMPORTA nao e o total: e `class-feature` com 608 `false`, 72%
    do kind, que agora diz com marca no registro o que o item 40 vinha dizendo
    em prosa -- o efeito de subclasse e de progressao esta majoritariamente por
    converter. Ate hoje era invisivel por construcao. Distribuicao final: 1.359
    true, 738 false, 6.345 null. O portao 10 caiu de 8.360 para 0 e a linha de
    base foi regravada; `test_portoes.py` deixou de ser catraca e virou assercao
    dura (todo registro responde, `null` conta como resposta). Os 724 registros
    com `grants_completos == false` que a auditoria citou nao viraram trabalho
    aqui: esta spec MARCA a perda, reparar e a Fase 3 (item 40) e o item 72.
    || TEXTO ORIGINAL: REESCRITO 2026-07-29 (auditoria) -- o item ficou MAIOR e mudou de eixo. Os 1.564 registros originais foram corrigidos, mas 724 novos apareceram sem ninguem ver (grants_completos == False hoje: spell 438, heritage 258, feat 27, familiar-ability 1) -- perfil de kind totalmente diferente do original. O ACHADO GRAVE e outro: 14.247 registros, 72% da base, NAO EMITEM o campo `grants_completos` -- equipment 6.122, feat 3.849, weapon 1.042, class-feature 841, trait 551, deity 488. Ou seja: a metrica de cobertura e cega em tres quartos da base, e NENHUM PORTAO COBRA ISSO. Por isso o conserto anterior sumiu do radar. PRIMEIRA TAREFA, antes de qualquer conserto de conteudo: portao novo que falhe quando um kind que deveria declarar grants_completos nao declara, e que reporte cobertura por kind. Metrica sem contrapartida de erro e propaganda. || TEXTO ORIGINAL: 1.564 REGISTROS PERDERAM MECANICA EM SILENCIO -- e o que estava por tras do debate sobre `mechanized`. Medido contra o clone do Foundry: 4.688 registros da base tem doc do Foundry COM rule elements, e em 1.564 deles (33,4%) a base emitiu `grants` vazio -- 3.667 rule elements no total (873 feat, 321 class-feature, 194 equipment, 134 weapon). Como `mechanized == bool(grants)`, esses 1.564 saem com `mechanized: false`, que e indistinguivel de ''esse registro nao tem mecanica nenhuma''. Nao e bug do conversor: `converter_rule_elements.py` converte de proposito so o declarativo (`GrantItem` sem predicado e `ActiveEffectLike` com path de rank), e documenta que o resto -- ItemAlteration 1.171, RollOption 539, ActiveEffectLike 316 -- exige reimplementar o interpretador do VTT. O que falta e MARCAR: `grants_completos` distingue ''nao tem'' de ''tinha e nao converti'', e vira portao. Isso, e so isso, justifica trocar `mechanized` pelos dois campos da v2 -- o rename sozinho nao valia nada, ja que `mechanized` e igual a `bool(grants)` em 100% dos 19.738'
  id: 59
  date: '2026-07-30'
  priority: concluido
- desc: 'PARTES (a) E (b) CONCLUIDAS 2026-07-30 (spec specs/2026-07-30-proficiencia-de-arma-nomeada.md).
    SOBRA SO A PARTE (c). (a) O remap de `weapon_proficiency` foi implementado nos
    dois motores: 91 ocorrencias em 54 registros que NUNCA eram lidas -- `grep
    weapon_proficiency motor/motor.py` dava um unico hit, dentro de um docstring.
    A gramatica de `definicao` nao sao 2 padroes e sim 28 formas estruturais, mas
    quatro seletores (`base`, `category`, `trait`, `group`) mais `or`/`and`/`not`
    cobrem 76 das 91 (83,5%); as 15 restantes sao 8 com placeholder dinamico do
    VTT, 3 `slug`, 3 `usage`/`melee`, 1 `type`. DECISAO REGISTRADA: o remap SOMA,
    nunca subtrai -- ler o RAW ao pe da letra faria um Guerreiro expert em marcial
    CAIR para trained ao pegar Archer Dedication. E o remap chega ao BONUS DE
    ATAQUE, nao so ao predicado: `_ataques` passou a resolver por `weapon:<slug>`
    em vez da categoria crua, que era onde o numero do jogador ficava errado.
    Provado em ficha (`_teste-validacao-remap-de-arma`): Mago 8 com Archer sai com
    arco longo trained/ataque 12 e espada longa untrained/ataque 0.
    (b) ACHADO NOVO, nao estava no item: `weapon:*` era LETRA MORTA. `wb:weapon/*`
    nao resolve, a chave literal caia em `_rank_sem` e voltava untrained SEMPRE --
    um Guerreiro expert em tres categorias respondia untrained. Cinco feats eram
    inalcancaveis por QUALQUER personagem (advanced-firearm-familiarity,
    cut-them-down-burn-them-out, diverse-weapon-expert, performance-weapon-expert,
    reaper-of-repose). Agora responde o melhor rank entre as quatro categorias,
    mesmo tratamento do `lore:*`. O item 95 saiu junto, como estava planejado.
    DIVIDA ANOTADA: 4 ocorrencias com `igual_a: null`, 2 delas em
    `armigers-protection`, cujo `definicao` cita `item:slug:hellknight-plate` --
    e remap de ARMADURA carregado na chave de arma. Anomalia de dado.
    || FALTA A PARTE (c), texto original abaixo: RE-MEDIDO 2026-07-29, e o item encolheu para UMA alegacao. (a) CAI: ''Archer Dedication nao move martial de untrained'' e comportamento CORRETO -- a prosa diz ''For the purposes of proficiency, treat any of these that are martial weapons as simple weapons, and any that are advanced weapons as martial weapons'', ou seja o feat REMAPEIA categoria, nao concede treino. O grant `weapon_proficiency` diz exatamente isso (`definicao: [item:category:martial, or[bow, crossbow]], igual_a: simple`). O motor ignorar isso custa PRECISAO DE ATAQUE com arma nomeada, nao rank de categoria: sao 89 ocorrencias, 87 delas com `igual_a: simple|martial|unarmed`. O lugar do conserto e `_rank_de_arma`, que ja faz a ponte arma->categoria. (b) JA RESOLVIDO 2026-07-29 pela spec de ChoiceSet: o Marshal dava Diplomacy E Intimidation porque as opcoes vinham soltas. (c) CONFIRMADO e e o que sobra: a class-feature COMPARTILHADA `wb:class-feature/weapon-expertise` concede so `simple: expert` e `unarmed: expert`, e 14 CLASSES apontam para ela -- Champion, Druid, Exemplar, Guardian, Investigator, Kineticist, Magus, Oracle, Psychic, Sorcerer, Swashbuckler, Thaumaturge, Witch, Wizard. Entre elas ha marciais (Campeao 5 e 7 sai com simple=expert e martial=trained) e nao-marciais (Druida, que esta certo). Uma feature so nao serve as duas progressoes. NAO da para derivar de ''expert no que a classe tinha no nivel 1'': o `attack_proficiency` do AoN so traz o nivel 1, e a variante `bard-weapon-expertise` da marcial expert sem o Bardo ser treinado em marcial. Exige a TABELA de progressao da classe (esta no `markdown` do AoN como HTML), mesmo caminho de `aplicar_conjuracao.py`.'
  id: 75
  date: '2026-07-29'
  priority: alta
- desc: 'CONCLUIDO 2026-07-30 (spec specs/2026-07-30-tradicao-por-subclasse.md).
    47 das 48 subclasses agora entregam a tradicao na ficha. Dois achados mudaram
    o desenho, e nenhum estava no item. (1) A FONTE TEM O DADO ESTRUTURADO: o
    dump do AoN traz `tradition: ["Occult"]` como campo -- bloodline 27/28,
    patron 27/27, eidolon 13/13, draconic-exemplar 44/44. Nao houve parse de
    prosa. (2) O REGISTRO QUE O JOGADOR PEGA NAO E O QUE TEM A TRADICAO: o eixo
    de subclasse oferece `wb:class-feature/bloodline-genie`, e essa class-feature
    sai com `xref.aon: None` -- o dump de class-features tem `tradition` em ZERO
    dos 1.254. Sao dois catalogos paralelos, entao foi preciso um passo novo
    (`derivar_tradicao_de_subclasse.py`, 7d2) que leva o campo para a opcao viva,
    casando por nome COM TRAVA PELA CLASSE DONA (sem ela `psychopomp`, que existe
    como bloodline E como eidolon, casaria cruzado). 47 pares, 0 ambiguos, 0 sem
    par. O eidolon nao vem do aon_kinds e sim do companheiros.py -- por isso os
    13 ficaram de fora na primeira rodada. NO MOTOR: `_conjuracao()` passou a
    chamar `_tradicao_por_escolha` quando a tradicao nao e uma das quatro
    palavras, e o resolvedor ganhou FILTRO POR CLASSE -- sem ele um Feiticeiro 5
    / Bruxa 3 saia com a mesma tradicao nas duas linhas, porque a varredura
    devolvia a primeira escolha de subclasse com tradicao. Nos dois motores.
    ARMADILHA REGISTRADA: casar por NOME dava `arcane` para o Draconic, que e a
    tradicao da versao LEGADA -- a base carrega a REMASTER, cuja tradicao e
    variavel (depende do draconic-exemplar). Casar por `xref.aon` resolve. O
    Draconic segue sem tradicao de proposito: o eixo `draconic-exemplar` existe
    na base (44 registros, ja com tradicao emitida) mas NAO esta ligado como
    escolha em classe nenhuma -- o motor avisa em vez de arbitrar. Ligar o eixo
    e uma linha, e vira item quando o 69/40 chegarem la.
    || TEXTO ORIGINAL: NUMERO CORRIGIDO 2026-07-29 (auditoria), e o item 41 foi fundido aqui. Nao sao ''48 subclasses com grants vazio'': hoje so bloodline do Feiticeiro esta 100% vazio (19/19); patron da Bruxa (0/16 vazios) e eidolon do Invocador (1/14) JA ganharam grants de pericia. Mas NENHUM desses grants carrega tradicao, entao o defeito central persiste com outro contorno: `_conjuracao()` nativo (motor.py:907) nunca resolve tradicao por subclasse -- testado com Bruxa de patron Baba Yaga escolhido, a tradicao continua sendo a string de prosa. O resolvedor `_tradicao_por_escolha` EXISTE, mas so esta ligado em `_conjuracao_de_arquetipo` (via dedicacao), nao na classe pura. DC e slots continuam corretos; o defeito e isolado ao campo de tradicao, que e o que filtra quais magias o personagem pode aprender. || TEXTO ORIGINAL: TRADICAO DE CONJURACAO NAO RESOLVE PARA FEITICEIRO, INVOCADOR E BRUXA -- medida a extensao completa em 2026-07-27. As 3 classes tem `spellcasting.tradition` como string de prosa nao resolvida, e as 48 subclasses que deveriam determinar a tradicao (18 bloodlines, 17 patrons, 13 eidolons) tem `grants: []` em 100% dos casos: nao ha de onde puxar a tradicao real em lugar nenhum da base. DC e slots continuam CORRETOS -- o defeito e isolado ao campo de tradicao, que e o que filtra quais magias o personagem pode aprender. Reproduzido em 3 fichas (feiticeiro5-fa-diabolico, bruxa5-tradicao-patron, invocador5-tradicao-eidolon). Relacionado ao item 41, que levantou o problema sem medir'
  id: 78
  date: '2026-07-30'
  priority: concluido
- desc: 'A regra de precedencia grants->foundry e letra morta: grants nunca gera conflito real no dataset, o merge adota silenciosamente o lado nao-vazio. Ou exercitar ou remover da spec'
  id: 13
  date: '2026-07-29'
  priority: media
- desc: 'A mecanica de filiacao EXISTE mas nao esta estruturada: 305 registros (155 equipment, 134 feat, 13 weapon, 3 armor) tem linha ''Access'' no texto citando organizacao/regiao/etnia como condicao de raridade uncommon, com requires:null. Mais 68 feats/archetypes com requires_texto tipo ''member of X''. Nenhuma chave do predicado sabe falar de filiacao. Solucao: ~20-25 stubs leves (id+nome, sem prosa) + termo novo no predicado. Principio zero: sugere, nunca bloqueia'
  id: 22
  date: '2026-07-29'
  priority: media
- desc: 'COBERTURA DE EFEITO POR SUBCLASSE -- levantamento completo, 8 eixos seguem zerados e a causa NAO e falha de extracao. Com efeito: muse 5/5, patron 16/24, oracle mystery 10/12, thaumaturge implement 8/10, gunslinger way 5/6, rogue racket 5/6, magus hybrid-study 2/8, swashbuckler style 2/6, wizard arcane-thesis 1/6, cleric doctrine 1/3. ZERADOS: barbarian instinct (16 opcoes, 27 feats dependem), champion cause (13, 9 feats), wizard arcane-school (23), witch lesson (20), psychic conscious-mind (6) e subconscious-mind (4), ranger hunters-edge (4, 14 feats), alchemist research-field (4). Medido: das 90 opcoes desses eixos, 62 NAO TEM rule element no Foundry (sao catalogo do AoN, o Foundry nao modela) e as 28 restantes usam ItemAlteration (60), DamageAlteration (12), DamageDice (7) -- mecanica de dano e de ataque. A prosa tambem nao ajuda: so 8 de 77 tem padrao regular. CONCLUSAO: o que falta e majoritariamente MECANICA DE COMBATE, que o principio zero poe fora de escopo (o app nao roda mecanica). O que importa para montar ficha -- proficiencia, pericia, feat e spell concedidos -- ja foi convertido. Decidir se vale um interpretador parcial so para dano de rage e afins'
  id: 42
  date: '2026-07-29'
  priority: media
- desc: 'PENSANDO EM CORTAR O ARQUETIPO DE MULTICLASSE (Igor, 2026-07-27) -- NAO FAZER AGORA, so anotado. A ideia: permitir apenas arquetipo de DEDICACAO comum e remover os de multiclasse, porque na houserule multiclasse ja se faz com nivel de classe -- as duas rotas competem, e a regra 23 acabou de declarar que se excluem. Cortar seria a conclusao natural da 23: em vez de marcar conflito caso a caso, some a rota duplicada. MEDIDO na base para dimensionar: 244 archetypes, dos quais 27 sao de multiclasse (arquetipo cujo nome e nome de classe) e 217 nao; 2.129 feats tem trait `archetype`, 226 tem `dedication` e exatamente 27 tem `multiclass` -- os 27 sao as dedicacoes das classes, e nenhum feat nao-dedicacao carrega o trait. Os 27 arquetipos de multiclasse tem 195 feats no total. Ou seja, cortar remove 27 dedicacoes + 195 feats de arquetipo, sobrando 199 dedicacoes e ~1.934 feats. O recorte e DERIVAVEL (trait `multiclass`), nao precisa de lista a mao. A VALIDAR antes de decidir: (a) algum feat de arquetipo NAO-multiclasse exige um feat de arquetipo de multiclasse como pre-requisito? Se sim, cortar quebra a cadeia; (b) o que se perde de conteudo unico -- ha feats de arquetipo de multiclasse que nao tem equivalente na progressao da classe (ex: as basic/expert/master spellcasting, que dao slots que nenhum nivel de classe da do mesmo jeito); (c) impacto na regra 21, que hoje usa a dedicacao de conjuracao como PISO -- se o arquetipo de multiclasse sumir, o piso precisa de outra referencia ou a regra 21 fica sem chao; (d) o Free Archetype (regra 2) continua ligado e passa a apontar so para os 217 restantes'
  id: 46
  date: '2026-07-29'
  priority: media
- desc: 'PARCIAL, re-medido 2026-07-29 (auditoria). (1) spell.level IMPLEMENTADO: 1.655 de 1.655, Fireball = 3 -- essa parte esta fechada. (2) PENDENTE: os 66 registros sem `traits` saem com a CHAVE OMITIDA, e a decisao de 27/07 dizia que deveriam sair como lista vazia. (5) e o item 59, nao duplicar aqui. || TEXTO ORIGINAL: DECIDIDO 2026-07-27 medindo as fontes, nao por opiniao. (1) SPELL PASSA A EMITIR `level`: as TRES fontes usam `level` e NENHUMA usa `rank` -- AoN 2.461/2.461, Foundry 1.802/1.802 (`system.level.value`), pf2etools 2.055/2.055; Fireball e `level: 3` nas tres. `rank` e a palavra da PROSA remaster, nenhuma fonte de dados adotou como campo. A base esta sozinha contra as tres. Emitir `level` e manter `rank` como espelho. (2) `traits` AUSENTE VIRA `[]`: sao 66 registros (39 class-feature, 27 class) e as fontes concordam que nao ha trait -- Foundry 0 de 66, AoN 2 de 66. E ausencia real, nao desconhecimento, entao `[]` e a representacao certa; os 2 do AoN sao falha de extracao a corrigir junto. (3) `source` POR SUBCAMPO: DESCARTADO. O Foundry nao publica pagina (0 de 28.788 docs; o bloco `publication` so tem license/remaster/title) e dos 1.518 registros sem `source.page` 1.441 nem tem xref.aon. A fusao por subcampo recuperaria QUATRO paginas -- nao paga mexer no reconciliador. (4) VOCABULARIO DE `prov`: manter o atual e documentar as formas, nao trocar; e convencao interna, nenhuma fonte opina, e sao 17.488 ocorrencias na convencao viva. (5) `mechanized`: ver item 59, que e o achado de verdade. Texto original: DECISAO DE SCHEMA PENDENTE (Igor decide): adotar ou nao a spec v2, que nasceu na linha paralela de 2026-07-27 e nao entrou aqui. Sao 5 pontos, todos com teste ja escrito e marcado expectedFailure em pipeline/testes/ -- cada um vira verde sozinho no dia em que for adotado, e o unittest acusa ''unexpected success'' pedindo a retirada do marcador. (1) `mechanized` (hoje em 19.738 registros, e igual a bool(grants) em 100% deles) daria lugar a `grants_completos` + `requires_parseado`, com null = nao se aplica -- mexe no motor; (2) spell teria `level` espelhando `rank` (hoje 1.638 de 1.649 spells tem level null; nao quebra o motor, que nao indexa magia por level); (3) `traits` ausente sairia como [] em vez de null (66 registros); (4) vocabulario fechado de `prov` (`<fonte>` ou `<fonte>~inferido:<regra>`) contra o atual, que usa `inferida:livro`, `derivado:gate-de-nivel`, `aon+foundry` -- 17.488 ocorrencias na convencao atual; (5) `source` fundido por SUBCAMPO em vez de disputado inteiro, para nao perder a pagina que so uma fonte tem (1.518 registros sem source.page). Nada disso e bug: e schema. Enquanto nao houver decisao, a v1 e a lei e a suite fica verde'
  id: 53
  date: '2026-07-29'
  priority: media
- desc: 'RE-MEDIDO 2026-07-29, e o item mudou de gravidade: e COSMETICO, nao numero errado. Contra o dump do AoN, 65 class-features nao existem na base por nome (nem como alias -- conferido, licao do item 18). Das 65, 35 sao LINHAS DE TABELA DE PROGRESSAO (''ability boost'', ''ancestry feat'', ''alchemist feats'') que o nosso modelo representa como SLOT e nao como feature -- ausencia correta. As outras 30 sao features de verdade: anathema, champions code, debilitating strikes, divine smite, exalt, familiar, great fortitude, hexes, incredible senses, lightning reflexes, premonition''s reflexes, quick rage, slippery mind, trackless step, vigilant senses, wild empathy, wild stride, e as spellcasting por tradicao. A PERGUNTA QUE DECIDE: o efeito delas ja chega na ficha? SIM. Medido: Campeao fort trained->expert(nv9)->master, Ladino reflex expert->master->legendary(nv17), percepcao idem -- a progressao da classe ja entrega o upgrade que `Lightning Reflexes` e `Vigilant Senses` representam. O que falta e a LINHA com o nome da feature na ficha, que para um construtor tem valor (o jogador quer ver ''Lightning Reflexes'' no nivel 9), mas nao e numero errado. Prioridade rebaixada.'
  id: 55
  date: '2026-07-29'
  priority: baixa
- desc: 'PARCIAL, re-medido 2026-07-29 (auditoria). O vies 1 (rank lido de system.skills em vez de trainedSkills.value) JA foi corrigido -- e o proprio conteudo do item. SOBRA o vies 2: falta o oraculo de EM QUE NIVEL cada aumento de pericia foi gasto, e sem ele a metrica de 62,9% nao mede a qualidade do motor. Falta o oraculo, nao o motor. || TEXTO ORIGINAL: CUIDADO COM A METRICA DE PERICIA: os 62,4% (1.287 de 2.064) NAO medem a qualidade do motor. Dois vieses, os dois descobertos ao construir a medicao. (1) `system.skills.<pericia>.rank` do ator do Foundry NAO e o rank final -- so registra escolha discricionaria; o treino automatico de classe vive em `trainedSkills.value` DENTRO do item de classe do mesmo ator. Provado com a Amiri: `athletics` sai ausente de `system.skills` e presente em `trainedSkills.value` do item Barbarian. O oraculo corrigido une as duas fontes (`max(rank explicito, 1 se automatico)`), as duas do proprio ator, nenhuma da nossa base. (2) Mesmo corrigido, falta o oraculo de EM QUE NIVEL cada aumento foi gasto, entao o motor comeca perdendo por construcao. Enquanto o item 67 nao entrar, este numero mede a lacuna, nao o motor. Os 2 casos em que o motor da rank MAIOR foram investigados um a um e o motor esta CERTO: Droven (Inventor) em crafting, pela class-feature `Expert Overdrive`, cujo texto RAW diz ''You become an expert in Crafting'' -- e o ator do Foundry que nao persiste bump automatico de class feature'
  id: 68
  date: '2026-07-29'
  priority: media
- desc: 'MEDIDO DE NOVO 2026-07-29, com a anatomia do balaio. 16 de 27 classes tem o eixo `outras-opcoes`, somando 265 opcoes. Piores: Inventor 52, Alchemist 33, Thaumaturge 30, Cleric 18, Exemplar 18. O balaio mistura TRES coisas de naturezas diferentes, e por isso nao sai com uma regra so: (a) PROGRESSAO concedida a todos -- o bloco de nivel 1 do Alchemist tem `advanced-alchemy`, `formula-book`, `infused-reagents`, `quick-alchemy` e `versatile-vials`, que todo Alquimista recebe, nao escolhe; idem `anathema-cleric`/`deity-cleric`/`initial-creed` no Clerigo. (b) VARIANTE DETERMINADA por uma sub-escolha ja feita -- `field-discovery-bomber/chirurgeon/mutagenist/toxicologist` e a mesma feature especializada pelo research field ja escolhido, e `first-doctrine-cloistered-cleric` vs `-warpriest` pela doutrina. (c) escolha paralela de verdade. TESTADA a regra ''sufixo bate com opcao de outro eixo da mesma classe'' para separar (b): pega 70 das 265, entao NAO domina -- 195 sobram. Nao implementei heuristica parcial: erraria nos 11 eixos que hoje funcionam. O caminho provavel e (a) primeiro, que e o maior e o mais objetivo: opcao que a classe concede a TODOS nao e opcao. || CORRIGIDO 2026-07-29 (auditoria): eram 25 de 27 classes com o eixo-balaio; hoje sao 16 de 27. aplicar_subclasses.py ja tem o fix por (eixo, nivel) mais a regra ''1 candidato = progressao'', e Fighter e Monk -- os piores exemplos citados -- estao corrigidos. O caso que sobra e o Alchemist, que mistura Advanced Alchemy (progressao) com Advanced Vials (sub-escolha de verdade). || TEXTO ORIGINAL: EIXO `outras-opcoes` E UM BALAIO -- 25 das 27 classes tem um. Achado 2026-07-27 ao investigar por que um Guerreiro 4 saia com `Warrior of Legend`: o Fighter nao tem subclasse no remaster, mas `aplicar_subclasses.py` cria um eixo generico e joga ali tudo que sobrou. O resultado mistura opcao de subclasse de verdade com feature de progressao normal: monk nivel 15 com `Greater Weapon Specialization` como se fosse escolha, champion no nivel ZERO, alchemist com `Advanced Alchemy` ao lado de `Advanced Vials (Bomber)`. Efeitos: (a) toda ficha dessas classes ganha um aviso falso `falta escolher outras-opcoes`; (b) feature de progressao so aparece se for `escolhida`; (c) desde o item 62 essas features tambem CONCEDEM (Warrior of Legend da Diehard), entao o erro de dado agora vira numero na ficha. Consertar no pipeline: separar eixo real de resto-da-progressao. Os 2 eixos legitimos por classe (racket, instinct, muse...) estao corretos e nao entram nisto'
  id: 69
  date: '2026-07-29'
  priority: media
- desc: 'PARTE (1) CONCLUIDA 2026-07-30 (spec specs/2026-07-30-bonus-de-pericia-e-salva.md).
    SOBRA A PARTE (2), a `proficiency` com expressao. ACHADO QUE MUDOU O ITEM: o
    total de pericia NAO EXISTIA no motor -- era calculado em
    `PainelDireito.tsx:94` (`nivel + RANK_BONUS[rank] + mod`), a mesma conta em
    tres lugares do componente. Numero que nasce em React nao tem oraculo, nao
    tem paridade e nao tem onde receber `flat_modifier`; era essa a causa real
    de os bonus nunca chegarem na ficha, e nao a falta de codigo de aplicacao.
    Entao a ordem foi: primeiro `visao.pericias` e `visao.salvas` no motor (com
    rank, atributo, bonus e detalhe, mesma forma do `ac`), depois os bonus.
    O diff dos 24 fixtures saiu com 4.850 insercoes e ZERO delecoes -- prova de
    que o numero nao mudou de valor, so de lugar. A regra de tipo do PF2e entrou
    junto: mesmo tipo nao empilha (vale o maior), tipos diferentes somam,
    untyped empilha com tudo. Sem ela tres itens de +1 de circunstancia dariam
    +3 onde o RAW da +1. Selector que o motor nao modela e CONTADO em
    `bonus_ignorados`, nao descartado calado. `nomeDeLore` tambem migrou da tela
    (`Lore: Azlant`, e nao `Azlant Lore`). Ficam de fora, declarados na spec: os
    1.247 condicionais (dependem de contexto de acao), os 51 dinamicos, os 41
    `value` que sao formula do VTT, e `initiative`, que o motor nao tem.
    || FALTA A PARTE (2), texto original: flat_modifier NAO-HP E PROFICIENCY COM EXPRESSAO -- escopo medido 2026-07-27, decisao pendente. (1) 1.709 ocorrencias de `flat_modifier` em 1.485 registros (equipment 806, feat 591, weapon 146, heritage 98) e o motor so aplica selector `hp`. Classificacao: 80% seriam numero de ficha, 16% mecanica de combate (fora do escopo), 4% duvidoso. MAS 1.247 das 1.709 (73%) sao `condicional: true` -- bonus estreito do tipo ''+2 em Atletismo so para Empurrar'' --, entao aplicar o grupo inteiro INFLARIA a ficha parada. So o incondicional e seguro destrava 15 feats e 1 dedicacao: custo quase zero (mesma logica ja usada para hp), retorno pequeno. (2) 57 ocorrencias de `proficiency` cujo valor nao e rank literal e sim expressao do Foundry, em 17 feats -- e sao DOIS padroes so: espelhar o rank de desarmado (7 registros) e o padrao de dedicacao de armadura (6, entre eles `sentinel-dedication`). Um primitivo declarativo de proficiencia ESPELHADA resolve 15 dos 17 sem avaliar expressao. Numeros conferidos de forma independente. Relatorio em docs/2026-07-27_escopo-flat-modifier.md'
  id: 72
  date: '2026-07-29'
  priority: media
- desc: 'PENDENCIAS MENORES DO REVIEW ADVERSARIAL DE 2026-07-27 (as graves ja foram consertadas no mesmo dia). (a) ESCOLHA DE NIVEL FUTURO tem tres tratamentos no mesmo motor: `_atributos` trata planejamento como caso normal e ignora, enquanto `_higiene_de_slot` e `_aumentos_de_pericia` tratam como erro; alem disso a contagem `len(usados) > len(niveis)` nao filtra por nivel, entao quem planeja o nivel 8 numa ficha de nivel 4 leva aviso. Decidir a semantica: ou o documento so descreve o presente, ou o motor recorta por nivel em TODA checagem. (b) `em: "criacao"` (string) desliga a checagem de nivel da higiene de slot -- e correto para ancestria/background, mas silencia feat posto em `criacao` por engano. (c) `_subclasse_de` e sensivel a ordem do array de escolhas e alimenta `_dc_de_conjuracao` -- pre-existente, so muda texto, mas e a ultima dependencia de ordem que sobrou depois do conserto de `ordem_de_classe`. Relatorio completo em docs/2026-07-27_review-adversarial-grants.md'
  id: 73
  date: '2026-07-29'
  priority: media
- desc: 'LACUNAS PONTUAIS DE SPELL/RITUAL/EQUIPAMENTO achadas na validacao por dominio de 2026-07-27. BOA NOTICIA primeiro: cobertura de spell e ritual contra o AoN e COMPLETA (0 ausentes nos dois, cruzando por nome normalizado no conjunto remaster), `level` em 100% dos 1.655 spells, e as 17 fichas batem com a formula RAW de AC/ataque/dano sem excecao. As lacunas: (a) 15 spells legacy com `acoes` ausente apesar de a prosa trazer ''Cast 10 minutes'' -- buraco de extracao; (b) 23 spells com `alcance` ausente, mesmo padrao; (c) campo `alvos`/targets nunca existiu em spell nem ritual (0% estrutural); (d) `heightened` estruturado cobre 31% dos spells e 42% nao tem nem dado nem a flag `heightened_so_prosa`, entao nao da para separar ''sem elevacao'' de ''lacuna''; (e) 17 spells zumbi (`desmembrado_de`) com rank/tradicoes ausentes, duplicatas orfas de fusao -- o canonico existe completo com outro id; (f) 52 itens de equipment (0,6%) ausentes do AoN, entre eles Cloak of Elvenkind, Bag of Holding e Hat of Disguise; (g) relic tem 122 canonicos (os 219 incluem 97 duplicatas -legacy) e os niveis de gift sao 100% prosa -- nem o dump do AoN usou o campo `type` (Minor/Major/Grand) que a fonte tem; o motor nem reconhece `kind=relic`; (h) armaduras e escudos duplicados sem dado mecanico (`wb:armor/leather`, `hide`, `studded-leather`, `unarmored` e 7 escudos de material precioso) coexistindo com a versao completa -- artefato de extracao, perigoso se o front casar por nome curto; (i) dano com arma finesse usa STR em vez de DEX para o Ladino com racket Thief; (j) bulk/carga nao existe no motor'
  id: 79
  date: '2026-07-29'
  priority: media
- desc: 'PARCIAL, re-medido 2026-07-29 (auditoria). (a) RESOLVIDO: 0 ids `-legacy` em class.subclasses hoje (eram 46, limpos no commit 1fbfd7864). (b)(c)(d)(e) IDENTICOS: 10 backgrounds com boosts e skill_training vazios; Focus Spells / Improved Evasion / Iron Will / Martial Weapon Mastery orfas de progressao; ikon(21) / mythic-calling(15) / element(6) / deviant-ability-classification(10) com 100% grants vazio; deity.favored_weapon com prefixo wb:equipment/ em exatamente 509 referencias. || TEXTO ORIGINAL: REQUIRES E SUBCLASSES CITANDO SLUG PRE-REMASTER -- levantado pela validacao de feats/ancestrias em 2026-07-27, PARCIALMENTE resolvido. A parte do motor esta fechada (item 80: `Base.resolver` segue o alias). O que FICA: (a) 46 ids `-legacy` esquecidos no catalogo de `class.subclasses` (barbarian, champion, oracle, witch) -- o jogador veria a opcao duplicada, legado e remaster lado a lado; (b) 10 backgrounds com `boosts` e `skill_training` vazios apesar de o dado bruto existir; (c) 4 class-features (`Focus Spells`, `Improved Evasion`, `Iron Will`, `Martial Weapon Mastery`) que nao aparecem em nenhuma `progressao`; (d) os kinds `ikon`, `mythic-calling`, `element` e `deviant-ability-classification` com `grants: []` em 100% dos registros, o que explica 37 das 50 class-features orfas; (e) `deity.favored_weapon` com prefixo errado (`wb:equipment/` em vez de `wb:weapon/`) em 509 casos. Cobertura de raro/incomum medida e essencialmente completa: ancestry 50/50 com distribuicao identica ao AoN, background 0 faltando, heritage 5 (todas common), archetype 1 (uncommon), feat 32 de 6.085 (so 2 uncommon, 0 rare/unique)'
  id: 83
  date: '2026-07-29'
  priority: media
- desc: 'COMPARACAO COM O PATHBUILDER, 1a rodada FECHADA (2026-07-29). De 65 pontos sobraram QUATRO, e NENHUM e buraco nosso -- tudo que o Pathbuilder oferece no slot de class feat de um Fighter 1, o Waybuilder tambem oferece. Os 61 que sairam eram quatro recortes distintos, cada um verificado contra a fonte: (1) o PATHBUILDER renomeia o que a Paizo nao renomeou, tirando nome proprio de Golarion (Product Identity) -- a ponte remaster_id do AoN nao registra os pares e os nomes curtos dele nao existem em nenhum dos 43.686 docs do dump. A nossa base esta certa; virou tabela de traducao em docs/comparacao/equivalencias-pathbuilder.json (22 pares); (2) a opcao ''Allow outdated CRB and APG?'' nasce Off e esconde todo o conteudo pre-remaster que a nossa base inclui -- a sonda agora liga; (3) renomeacao de VERDADE (`Drow Shootist` -> `Crossbow Infiltrator`, feita pela Paizo): o comparador passou a casar por `aliases`; (4) ruido de grafia. OS QUATRO QUE SOBRARAM, todos do nosso lado: `Stance Savant` (CRB nv14, nao existe no dump do AoN -- removido no remaster e carregado do Foundry legado, DECIDIR se fica), `Chelaxian Scion Dedication` (AP #223), `Knight Vigilant` (Character Guide), `Venture-Gossip Dedication` (Paizo Blog) -- os tres ultimos sao recorte de fonte do outro lado, nao defeito. Relatorio: docs/2026-07-29_comparacao-pathbuilder.md. PROXIMO: outras classes, outros slots (skill/general/ancestry) e niveis altos, onde o predicado tem mais o que errar'
  id: 84
  date: '2026-07-29'
  priority: media
- desc: 'Importador do Pathbuilder tem que AVISAR o que se perde. Confirmado com o Igor: o eidolon existe no app deles e nao sobrevive ao export. Perda silenciosa e o pior tipo'
  id: 10
  date: '2026-07-29'
  priority: baixa
- desc: 'Cobertura medida em 5 dos 26 livros: Player Core, Player Core 2, War of Immortals e Ancestry Guide (1.377 nomes, 99,8% fora rituals) mais Treasure Vault (898 nomes, 100%). Os outros 21 livros nao foram testados'
  id: 19
  date: '2026-07-29'
  priority: baixa
- desc: 'POR ULTIMO, decisao do Igor (2026-07-29): opcao de idioma ingles / pt-BR na interface. Depois de TODO o resto -- so faz sentido com o app fechado. Escopo a decidir quando chegar a vez: a UI (rotulos, botoes, mensagens do motor) e traduzivel; a PROSA das 19.706 entradas vem das fontes em ingles e nao tem versao pt-BR licenciada, entao o mais provavel e UI em pt-BR com conteudo de regra em ingles. Nome de trait e de entidade idem -- traduzir ''Reactive Strike'' quebraria a busca do jogador que le AoN'
  id: 31
  date: '2026-07-29'
  priority: baixa
- desc: 'PARCIAL, re-medido 2026-07-29 (auditoria). CAIU: licenca inferida sem marca zerou (2.494 hoje, todas marcadas); feat_category ausente 256 -> 172 (o valor bruto ''classfeature'' zerou). NAO MUDOU: prov.class inferido (414 de 841). PIOROU: source.page ausente 1.506 -> 1.598, cresceu com a base. E `traits` ausente segue em 66 registros (39 class-feature + 27 class), mas hoje sai como CHAVE OMITIDA, nao null nem [] -- ver item 53. || TEXTO ORIGINAL: Residuos menores da auditoria: wb:archetype/shared-archetype-feats e diretorio de organizacao do Foundry virado arquetipo em 14 feats; 1.440 licencas inferidas por heuristica sem marca no registro emitido; prov.class ''inferido de traits'' em 409 das 817 class-features; 152 pontos de prov marcados ''desconhecida''; 65 traits:null contra 3.036 []; 256 feats sem feat_category (3 com valor bruto ''classfeature''); 1.506 sem source.page'
  id: 34
  date: '2026-07-29'
  priority: baixa
- desc: 'NUMERO ATUALIZADO 2026-07-29 (auditoria): eram 160 registros (0,85%); hoje sao 176 (0,89%) -- cresceu proporcionalmente a base. Confirmado por contagem propria contra pipeline/canonico_livros.json. Mesmos exemplos: Bastion of Blasphemies, Crypt of Runes, Paizo Blog. || TEXTO ORIGINAL: 160 registros (0,85%) tem source.book fora do mapa canonico do AoN: APs recentes (Bastion of Blasphemies, Crypt of Runes), Paizo Blog, e siglas cruas do pf2etools (''PC1''). Nao tem grafia duplicada -- so nao ha entrada no AoN para canonizar contra. Resolver com mapa de siglas verificado, nunca por chute'
  id: 38
  date: '2026-07-29'
  priority: baixa
- desc: 'CORRIGIDO 2026-07-29 (auditoria): eram 684 campos com prov ''desconhecida'' + 128 vazios; hoje sao 13. A concentracao antiga (grants, requires, background) zerou. O campo mora so em pipeline/base/index.json e e descartado do app por emitir_app.py. Praticamente fechado -- confirmar os 13 e encerrar. || TEXTO ORIGINAL: 684 CAMPOS COM prov ''desconhecida'' e 128 com prov vazio. Concentracao: 313 em `grants`, 308 em `requires`, e por kind 526 em background. O portao 1 nao pega porque ele exige que `prov` EXISTA, e ''desconhecida'' existe -- e um nao-resposta que passa. Ou se descobre a fonte (background veio de onde?) ou o valor vira explicitamente `null` com o portao cobrando'
  id: 52
  date: '2026-07-29'
  priority: baixa
- desc: 'EXTRATOR REDUNDANTE: `pipeline/extratores/relicos_idiomas.py` roda (esta em rodar.py::EXTRATORES) e gera saida/relicos_idiomas.json com 239 registros, mas `relicos_idiomas.json` NUNCA esteve em `reconciliar.py::ENTRADA` -- a saida dele nao entra na base. Isso NAO e perda de dado: medido, relic e language chegam por `aon_kinds.json`, que cobre melhor (122 de 122 relic da base estao la, contra 51 do extrator dedicado; 121 de 123 language contra 95). Ou seja, o extrator dedicado e trabalho duplicado que ninguem consome, nao um buraco. Decidir: tirar do runner, ou promover a fonte e tirar os dois kinds do aon_kinds. Nao deletei -- mencionar antes de remover'
  id: 61
  date: '2026-07-29'
  priority: baixa
- desc: 'ARMAS SEM DANO -- PARCIALMENTE RESOLVIDO 2026-07-29. Eram 57 armas sem `damage`, mas 41 sao bombas alquimicas (o dano e do efeito, vazio esta certo), 6 sao municao/magazine/pellet e 5 sao arma magica ou material que HERDA o dano do item base. Restavam QUATRO de verdade. Blowgun e Dart Umbrella FORAM CORRIGIDAS: o AoN traz `damage: ''1 P''` (dano fixo 1, sem dado, que e RAW) e o parser de `recuperar_mecanica_equipamento.py` exigia `dN`. Agora ha um segundo padrao (`FIXO`) e a representacao OMITE a chave `dado` em vez de grava-la como None -- os dois motores fazem `dano.get(''dado'','''')`, e a chave presente com None imprimiria ''None'' na ficha. Travado por 3 assercoes no oraculo. FALTAM DUAS: Nine-Ring Sword e Wind and Fire Wheel (Tian Xia) nao tem fonte em disco nenhuma -- precisa de dump novo do AoN ou entrada curada'
  id: 85
  date: '2026-07-29'
  priority: baixa
- desc: 'PARCIALMENTE RESOLVIDO 2026-07-29 (spec specs/2026-07-29-termos-de-predicado.md). Tres termos novos, e SO onde a base ja respondia: `sense` (le `grants.sense`, 81 registros que ninguem lia -- e de quebra a ficha ganhou `visao().sentidos`), `focus_pool` (o motor ja calculava o pool da regra 22) e `has_actor` (le a concessao de companheiro derivada no mesmo dia). Medido: predicado parseado 3.889 (91,3%) -> 3.919 (92,0%); frase rejeitada inteira 372 -> 342. DECISAO REGISTRADA, e ela e resposta e nao divida: alinhamento NAO vira termo -- `evil alignment` (7), `tenets of good` (4), `tenets of evil` (4), `any good alignment` (3) somam 18 clausulas de um conceito que o Remaster ABOLIU; na base `alignment` so existe em `deity`. Modelar exigiria inventar estado de personagem para responder pergunta de edicao anterior. Ficam visiveis em `requires_residuo`, como requisito de mesa. O QUE SOBRA, com dado faltando de verdade: `a familiar` (5) -- nao ha paralelo do `grant_actor` para familiar, o feat concede por `grant_item` de compendio Foundry; `healing font`/`harmful font` (7) -- `divine_font` existe em 479 divindades mas diz o que a DIVINDADE permite, nao o que o Clerigo escolheu (sub-escolha nao modelada); e 7 clausulas com tag `{@feat X|Fonte}` grudada que o parser nao separou (1% do residuo)'
  id: 87
  date: '2026-07-29'
  priority: baixa
- desc: 'MODIFICADOR DE INT NAO ENTRA NO ORCAMENTO DE PERICIA LIVRE. Declarado fora de escopo pela spec specs/2026-07-29-pericias-livres.md, que implementou o slot `pericias_livres`. Em RAW o personagem treina `livres + mod(INT)` pericias; o motor soma so as livres da classe (2 a 7, medido nas 27). A causa e ordem de derivacao: `_proficiencias()` roda ANTES de `_atributos()` (motor.py:191-192), entao o INT ainda nao existe quando `_orcamento_de_pericia` faz a conta. Consequencia: personagem de INT alto tem direito a mais pericias do que o motor oferece, e a higiene cobra menos do que deveria -- um Mago de INT 18 deveria ter 2+4=6 e o motor oferece 2. Conserto exige reordenar a derivacao (ou calcular o INT antes das pericias), que e mudanca de risco e merece medicao propria: conferir que nada em `_proficiencias` alimenta `_atributos`.'
  id: 92
  date: '2026-07-29'
  priority: media
- desc: 'FEAT QUE ABRE SLOT DE FEAT -- levantado pelo Igor em 2026-07-29, MAPEADO e nao resolvido. `Natural Ambition` (ancestria humana) da um class feat de nivel 1 EXTRA; `General Training` da um general feat; `Ancestral Paragon`, um ancestry feat. Hoje o motor nao abre slot nenhum por causa deles -- `_slots_de_feat` deriva os slots so da progressao de classe e da regra 2 (Free Archetype), entao o feat e pego e nao entrega nada, e o jogador nao tem onde escolher o feat prometido. MAPEADO por varredura da prosa: 11 registros, sendo 3 de ancestry, 1 de class, 2 de general, 5 de skill. Lista: advanced-general-training (general); ancestral-paragon (ancestry, 1st-level); general-training (general, 1st-level); hag-claws (ancestry); inscribed-with-elders-deeds (ancestry, 5th-level); magical-knowledge (skill); mortal-possibility (skill); natural-ambition (class, 1st-level); rogue-dedication (skill); skill-mastery (skill); skill-mastery-rogue (skill). CUIDADO NA VARREDURA, ja custou uma medicao errada: ''gain a class FEATURE that grants...'' casa com ''class feat'' por prefixo -- o padrao precisa de `feat\b(?!ure)`, senao os 20 `*-weapon-expertise` entram como falso positivo. O conserto natural e o mesmo desenho de `pericias_livres` e `escolha_de_grant`, feitos hoje: o feat declara o slot que abre, `slots_abertos` oferece, e a higiene cobra enquanto nao for escolhido. O slot precisa carregar o TIPO (class/skill/general/ancestry) e o NIVEL maximo do feat (`Natural Ambition` da um de nivel 1, nao um de qualquer nivel).'
  id: 94
  date: '2026-07-29'
  priority: alta
- desc: 'CONCLUIDO 2026-07-30, junto com a parte (a) do item 75 como estava previsto
    -- assim o teste de paridade prova o conserto em vez de passar por vacuo. A
    guarda virou `this.proficiencias.has(chave)`. Confirmado na varredura: dos 13
    `Object.hasOwn` do arquivo, era o UNICO sobre um `Map`; os outros 12 operam
    sobre objeto JSON plano e estao certos.
    || TEXTO ORIGINAL: PARIDADE DORMENTE: `app/src/motor/personagem.ts` usa `Object.hasOwn(this.proficiencias, chave)` dentro de `_rank_de_arma`, e `this.proficiencias` e um `Map` -- `Object.hasOwn` sobre Map e SEMPRE false, entao a guarda ''rank de arma NOMEADA ganha da categoria'' nunca dispara no TS. No Python a guarda (`if chave in self.proficiencias`) funciona. Os dois motores divergem, e o teste de paridade NAO pega porque hoje ninguem preenche chave `weapon:` na ficha -- e defeito dormente. ELE ACORDA quando o item 75 for feito: a ponte de `weapon_proficiency` (89 ocorrencias, o remap de categoria do Archer Dedication) e exatamente o que passa a escrever chave `weapon:`. CONSERTAR JUNTO COM O 75, nao antes -- assim o teste de paridade prova o conserto em vez de passar por vacuo. Reportado ao Igor em 2026-07-29 e registrado aqui depois, porque a primeira vez ficou so na conversa.'
  id: 95
  date: '2026-07-30'
  priority: concluido
promoted: []
---
