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
- desc: 'SOBRA DA FASE 3 FECHADA 2026-07-30 (spec specs/2026-07-30-bonus-de-item-equipado.md). O
    item pedia `ac` e `strike-damage`; na base canonica `ac` tinha 34 grants e ZERO incondicionais.
    Contando selector em LISTA apareceram 6, e ao aplicar veio o numero real: `_bonus_incondicionais`
    NAO LIA O INVENTARIO. Sao 293 grants incondicionais aplicaveis em equipment (261), armor (11),
    shield (11) e weapon (10) -- religion 26, intimidation 25, diplomacy 22, athletics 20, e o ac
    6 -- todos em selectors que o motor ja somava. Item de +1 em Furtividade nao mudava Furtividade.
    A CA passou a DISPUTAR (`_melhor_por_tipo`) porque o item_bonus da armadura tambem e bonus de
    item. SEGUNDO DEFEITO: o contador anti-perda nunca contou -- `_velocidade` reatribuia `bonus_ignorados`
    e apagava o que os passos anteriores gravaram; agora memoizado. DANO E ATAQUE RECUSADOS COM NUMERO:
    6 ocorrencias em 6 seletores + 34 dinamicos + 3 formulas, mesmo criterio do ItemAlteration. ATORES
    RESOLVIDOS 2026-07-30 (commit 5afe8c06d, spec specs/2026-07-30-familiar-e-eidolon-concedidos.md):
    16 registros concedem familiar e 2 concedem eidolon (eram 0 e 0); `candidatos()` deixou de devolver
    os 6.273 feats para o slot `familiar`. SOBRA SO O STAT BLOCK, e ele depende de FONTE que nao
    temos: `familiar-specific` nao tem um unico campo numerico, `eidolon` so tem velocidade, nao
    existe tabela de progressao, e a pagina de regras `Familiars` do AoN tem 796 caracteres so de
    conceito. Em PF2e o familiar deriva os numeros do personagem -- derivar sem a regra na mao seria
    inventar. PROXIMO PASSO: conseguir a fonte das estatisticas.'
  id: 43
  date: '2026-07-29'
  priority: alta
- desc: 'A regra de precedencia grants->foundry e letra morta: grants nunca gera conflito real no
    dataset, o merge adota silenciosamente o lado nao-vazio. Ou exercitar ou remover da spec'
  id: 13
  date: '2026-07-29'
  priority: media
- desc: 'A mecanica de filiacao EXISTE mas nao esta estruturada: 305 registros (155 equipment, 134
    feat, 13 weapon, 3 armor) tem linha ''Access'' no texto citando organizacao/regiao/etnia como
    condicao de raridade uncommon, com requires:null. Mais 68 feats/archetypes com requires_texto
    tipo ''member of X''. Nenhuma chave do predicado sabe falar de filiacao. Solucao: ~20-25 stubs
    leves (id+nome, sem prosa) + termo novo no predicado. Principio zero: sugere, nunca bloqueia'
  id: 22
  date: '2026-07-29'
  priority: media
- desc: 'COBERTURA DE EFEITO POR SUBCLASSE -- levantamento completo, 8 eixos seguem zerados e a causa
    NAO e falha de extracao. Com efeito: muse 5/5, patron 16/24, oracle mystery 10/12, thaumaturge
    implement 8/10, gunslinger way 5/6, rogue racket 5/6, magus hybrid-study 2/8, swashbuckler style
    2/6, wizard arcane-thesis 1/6, cleric doctrine 1/3. ZERADOS: barbarian instinct (16 opcoes, 27
    feats dependem), champion cause (13, 9 feats), wizard arcane-school (23), witch lesson (20),
    psychic conscious-mind (6) e subconscious-mind (4), ranger hunters-edge (4, 14 feats), alchemist
    research-field (4). Medido: das 90 opcoes desses eixos, 62 NAO TEM rule element no Foundry (sao
    catalogo do AoN, o Foundry nao modela) e as 28 restantes usam ItemAlteration (60), DamageAlteration
    (12), DamageDice (7) -- mecanica de dano e de ataque. A prosa tambem nao ajuda: so 8 de 77 tem
    padrao regular. CONCLUSAO: o que falta e majoritariamente MECANICA DE COMBATE, que o principio
    zero poe fora de escopo (o app nao roda mecanica). O que importa para montar ficha -- proficiencia,
    pericia, feat e spell concedidos -- ja foi convertido. Decidir se vale um interpretador parcial
    so para dano de rage e afins'
  id: 42
  date: '2026-07-29'
  priority: media
- desc: 'PENSANDO EM CORTAR O ARQUETIPO DE MULTICLASSE (Igor, 2026-07-27) -- NAO FAZER AGORA, so
    anotado. A ideia: permitir apenas arquetipo de DEDICACAO comum e remover os de multiclasse, porque
    na houserule multiclasse ja se faz com nivel de classe -- as duas rotas competem, e a regra 23
    acabou de declarar que se excluem. Cortar seria a conclusao natural da 23: em vez de marcar conflito
    caso a caso, some a rota duplicada. MEDIDO na base para dimensionar: 244 archetypes, dos quais
    27 sao de multiclasse (arquetipo cujo nome e nome de classe) e 217 nao; 2.129 feats tem trait
    `archetype`, 226 tem `dedication` e exatamente 27 tem `multiclass` -- os 27 sao as dedicacoes
    das classes, e nenhum feat nao-dedicacao carrega o trait. Os 27 arquetipos de multiclasse tem
    195 feats no total. Ou seja, cortar remove 27 dedicacoes + 195 feats de arquetipo, sobrando 199
    dedicacoes e ~1.934 feats. O recorte e DERIVAVEL (trait `multiclass`), nao precisa de lista a
    mao. A VALIDAR antes de decidir: (a) algum feat de arquetipo NAO-multiclasse exige um feat de
    arquetipo de multiclasse como pre-requisito? Se sim, cortar quebra a cadeia; (b) o que se perde
    de conteudo unico -- ha feats de arquetipo de multiclasse que nao tem equivalente na progressao
    da classe (ex: as basic/expert/master spellcasting, que dao slots que nenhum nivel de classe
    da do mesmo jeito); (c) impacto na regra 21, que hoje usa a dedicacao de conjuracao como PISO
    -- se o arquetipo de multiclasse sumir, o piso precisa de outra referencia ou a regra 21 fica
    sem chao; (d) o Free Archetype (regra 2) continua ligado e passa a apontar so para os 217 restantes'
  id: 46
  date: '2026-07-29'
  priority: media
- desc: 'PARCIAL, re-medido 2026-07-29 (auditoria). (1) spell.level IMPLEMENTADO: 1.655 de 1.655,
    Fireball = 3 -- essa parte esta fechada. (2) PENDENTE: os 66 registros sem `traits` saem com
    a CHAVE OMITIDA, e a decisao de 27/07 dizia que deveriam sair como lista vazia. (5) e o item
    59, nao duplicar aqui. || TEXTO ORIGINAL: DECIDIDO 2026-07-27 medindo as fontes, nao por opiniao.
    (1) SPELL PASSA A EMITIR `level`: as TRES fontes usam `level` e NENHUMA usa `rank` -- AoN 2.461/2.461,
    Foundry 1.802/1.802 (`system.level.value`), pf2etools 2.055/2.055; Fireball e `level: 3` nas
    tres. `rank` e a palavra da PROSA remaster, nenhuma fonte de dados adotou como campo. A base
    esta sozinha contra as tres. Emitir `level` e manter `rank` como espelho. (2) `traits` AUSENTE
    VIRA `[]`: sao 66 registros (39 class-feature, 27 class) e as fontes concordam que nao ha trait
    -- Foundry 0 de 66, AoN 2 de 66. E ausencia real, nao desconhecimento, entao `[]` e a representacao
    certa; os 2 do AoN sao falha de extracao a corrigir junto. (3) `source` POR SUBCAMPO: DESCARTADO.
    O Foundry nao publica pagina (0 de 28.788 docs; o bloco `publication` so tem license/remaster/title)
    e dos 1.518 registros sem `source.page` 1.441 nem tem xref.aon. A fusao por subcampo recuperaria
    QUATRO paginas -- nao paga mexer no reconciliador. (4) VOCABULARIO DE `prov`: manter o atual
    e documentar as formas, nao trocar; e convencao interna, nenhuma fonte opina, e sao 17.488 ocorrencias
    na convencao viva. (5) `mechanized`: ver item 59, que e o achado de verdade. Texto original:
    DECISAO DE SCHEMA PENDENTE (Igor decide): adotar ou nao a spec v2, que nasceu na linha paralela
    de 2026-07-27 e nao entrou aqui. Sao 5 pontos, todos com teste ja escrito e marcado expectedFailure
    em pipeline/testes/ -- cada um vira verde sozinho no dia em que for adotado, e o unittest acusa
    ''unexpected success'' pedindo a retirada do marcador. (1) `mechanized` (hoje em 19.738 registros,
    e igual a bool(grants) em 100% deles) daria lugar a `grants_completos` + `requires_parseado`,
    com null = nao se aplica -- mexe no motor; (2) spell teria `level` espelhando `rank` (hoje 1.638
    de 1.649 spells tem level null; nao quebra o motor, que nao indexa magia por level); (3) `traits`
    ausente sairia como [] em vez de null (66 registros); (4) vocabulario fechado de `prov` (`<fonte>`
    ou `<fonte>~inferido:<regra>`) contra o atual, que usa `inferida:livro`, `derivado:gate-de-nivel`,
    `aon+foundry` -- 17.488 ocorrencias na convencao atual; (5) `source` fundido por SUBCAMPO em
    vez de disputado inteiro, para nao perder a pagina que so uma fonte tem (1.518 registros sem
    source.page). Nada disso e bug: e schema. Enquanto nao houver decisao, a v1 e a lei e a suite
    fica verde'
  id: 53
  date: '2026-07-29'
  priority: media
- desc: 'RE-MEDIDO 2026-07-29, e o item mudou de gravidade: e COSMETICO, nao numero errado. Contra
    o dump do AoN, 65 class-features nao existem na base por nome (nem como alias -- conferido, licao
    do item 18). Das 65, 35 sao LINHAS DE TABELA DE PROGRESSAO (''ability boost'', ''ancestry feat'',
    ''alchemist feats'') que o nosso modelo representa como SLOT e nao como feature -- ausencia correta.
    As outras 30 sao features de verdade: anathema, champions code, debilitating strikes, divine
    smite, exalt, familiar, great fortitude, hexes, incredible senses, lightning reflexes, premonition''s
    reflexes, quick rage, slippery mind, trackless step, vigilant senses, wild empathy, wild stride,
    e as spellcasting por tradicao. A PERGUNTA QUE DECIDE: o efeito delas ja chega na ficha? SIM.
    Medido: Campeao fort trained->expert(nv9)->master, Ladino reflex expert->master->legendary(nv17),
    percepcao idem -- a progressao da classe ja entrega o upgrade que `Lightning Reflexes` e `Vigilant
    Senses` representam. O que falta e a LINHA com o nome da feature na ficha, que para um construtor
    tem valor (o jogador quer ver ''Lightning Reflexes'' no nivel 9), mas nao e numero errado. Prioridade
    rebaixada.'
  id: 55
  date: '2026-07-29'
  priority: baixa
- desc: 'PARCIAL, re-medido 2026-07-29 (auditoria). O vies 1 (rank lido de system.skills em vez de
    trainedSkills.value) JA foi corrigido -- e o proprio conteudo do item. SOBRA o vies 2: falta
    o oraculo de EM QUE NIVEL cada aumento de pericia foi gasto, e sem ele a metrica de 62,9% nao
    mede a qualidade do motor. Falta o oraculo, nao o motor. || TEXTO ORIGINAL: CUIDADO COM A METRICA
    DE PERICIA: os 62,4% (1.287 de 2.064) NAO medem a qualidade do motor. Dois vieses, os dois descobertos
    ao construir a medicao. (1) `system.skills.<pericia>.rank` do ator do Foundry NAO e o rank final
    -- so registra escolha discricionaria; o treino automatico de classe vive em `trainedSkills.value`
    DENTRO do item de classe do mesmo ator. Provado com a Amiri: `athletics` sai ausente de `system.skills`
    e presente em `trainedSkills.value` do item Barbarian. O oraculo corrigido une as duas fontes
    (`max(rank explicito, 1 se automatico)`), as duas do proprio ator, nenhuma da nossa base. (2)
    Mesmo corrigido, falta o oraculo de EM QUE NIVEL cada aumento foi gasto, entao o motor comeca
    perdendo por construcao. Enquanto o item 67 nao entrar, este numero mede a lacuna, nao o motor.
    Os 2 casos em que o motor da rank MAIOR foram investigados um a um e o motor esta CERTO: Droven
    (Inventor) em crafting, pela class-feature `Expert Overdrive`, cujo texto RAW diz ''You become
    an expert in Crafting'' -- e o ator do Foundry que nao persiste bump automatico de class feature'
  id: 68
  date: '2026-07-29'
  priority: media
- desc: 'MEDIDO DE NOVO 2026-07-29, com a anatomia do balaio. 16 de 27 classes tem o eixo `outras-opcoes`,
    somando 265 opcoes. Piores: Inventor 52, Alchemist 33, Thaumaturge 30, Cleric 18, Exemplar 18.
    O balaio mistura TRES coisas de naturezas diferentes, e por isso nao sai com uma regra so: (a)
    PROGRESSAO concedida a todos -- o bloco de nivel 1 do Alchemist tem `advanced-alchemy`, `formula-book`,
    `infused-reagents`, `quick-alchemy` e `versatile-vials`, que todo Alquimista recebe, nao escolhe;
    idem `anathema-cleric`/`deity-cleric`/`initial-creed` no Clerigo. (b) VARIANTE DETERMINADA por
    uma sub-escolha ja feita -- `field-discovery-bomber/chirurgeon/mutagenist/toxicologist` e a mesma
    feature especializada pelo research field ja escolhido, e `first-doctrine-cloistered-cleric`
    vs `-warpriest` pela doutrina. (c) escolha paralela de verdade. TESTADA a regra ''sufixo bate
    com opcao de outro eixo da mesma classe'' para separar (b): pega 70 das 265, entao NAO domina
    -- 195 sobram. Nao implementei heuristica parcial: erraria nos 11 eixos que hoje funcionam. O
    caminho provavel e (a) primeiro, que e o maior e o mais objetivo: opcao que a classe concede
    a TODOS nao e opcao. || CORRIGIDO 2026-07-29 (auditoria): eram 25 de 27 classes com o eixo-balaio;
    hoje sao 16 de 27. aplicar_subclasses.py ja tem o fix por (eixo, nivel) mais a regra ''1 candidato
    = progressao'', e Fighter e Monk -- os piores exemplos citados -- estao corrigidos. O caso que
    sobra e o Alchemist, que mistura Advanced Alchemy (progressao) com Advanced Vials (sub-escolha
    de verdade). || TEXTO ORIGINAL: EIXO `outras-opcoes` E UM BALAIO -- 25 das 27 classes tem um.
    Achado 2026-07-27 ao investigar por que um Guerreiro 4 saia com `Warrior of Legend`: o Fighter
    nao tem subclasse no remaster, mas `aplicar_subclasses.py` cria um eixo generico e joga ali tudo
    que sobrou. O resultado mistura opcao de subclasse de verdade com feature de progressao normal:
    monk nivel 15 com `Greater Weapon Specialization` como se fosse escolha, champion no nivel ZERO,
    alchemist com `Advanced Alchemy` ao lado de `Advanced Vials (Bomber)`. Efeitos: (a) toda ficha
    dessas classes ganha um aviso falso `falta escolher outras-opcoes`; (b) feature de progressao
    so aparece se for `escolhida`; (c) desde o item 62 essas features tambem CONCEDEM (Warrior of
    Legend da Diehard), entao o erro de dado agora vira numero na ficha. Consertar no pipeline: separar
    eixo real de resto-da-progressao. Os 2 eixos legitimos por classe (racket, instinct, muse...)
    estao corretos e nao entram nisto'
  id: 69
  date: '2026-07-29'
  priority: media
- desc: 'PARTE (1) CONCLUIDA 2026-07-30 (spec specs/2026-07-30-bonus-de-pericia-e-salva.md). SOBRA
    A PARTE (2), a `proficiency` com expressao. ACHADO QUE MUDOU O ITEM: o total de pericia NAO EXISTIA
    no motor -- era calculado em `PainelDireito.tsx:94` (`nivel + RANK_BONUS[rank] + mod`), a mesma
    conta em tres lugares do componente. Numero que nasce em React nao tem oraculo, nao tem paridade
    e nao tem onde receber `flat_modifier`; era essa a causa real de os bonus nunca chegarem na ficha,
    e nao a falta de codigo de aplicacao. Entao a ordem foi: primeiro `visao.pericias` e `visao.salvas`
    no motor (com rank, atributo, bonus e detalhe, mesma forma do `ac`), depois os bonus. O diff
    dos 24 fixtures saiu com 4.850 insercoes e ZERO delecoes -- prova de que o numero nao mudou de
    valor, so de lugar. A regra de tipo do PF2e entrou junto: mesmo tipo nao empilha (vale o maior),
    tipos diferentes somam, untyped empilha com tudo. Sem ela tres itens de +1 de circunstancia dariam
    +3 onde o RAW da +1. Selector que o motor nao modela e CONTADO em `bonus_ignorados`, nao descartado
    calado. `nomeDeLore` tambem migrou da tela (`Lore: Azlant`, e nao `Azlant Lore`). Ficam de fora,
    declarados na spec: os 1.247 condicionais (dependem de contexto de acao), os 51 dinamicos, os
    41 `value` que sao formula do VTT, e `initiative`, que o motor nao tem. || FALTA A PARTE (2),
    texto original: flat_modifier NAO-HP E PROFICIENCY COM EXPRESSAO -- escopo medido 2026-07-27,
    decisao pendente. (1) 1.709 ocorrencias de `flat_modifier` em 1.485 registros (equipment 806,
    feat 591, weapon 146, heritage 98) e o motor so aplica selector `hp`. Classificacao: 80% seriam
    numero de ficha, 16% mecanica de combate (fora do escopo), 4% duvidoso. MAS 1.247 das 1.709 (73%)
    sao `condicional: true` -- bonus estreito do tipo ''+2 em Atletismo so para Empurrar'' --, entao
    aplicar o grupo inteiro INFLARIA a ficha parada. So o incondicional e seguro destrava 15 feats
    e 1 dedicacao: custo quase zero (mesma logica ja usada para hp), retorno pequeno. (2) 57 ocorrencias
    de `proficiency` cujo valor nao e rank literal e sim expressao do Foundry, em 17 feats -- e sao
    DOIS padroes so: espelhar o rank de desarmado (7 registros) e o padrao de dedicacao de armadura
    (6, entre eles `sentinel-dedication`). Um primitivo declarativo de proficiencia ESPELHADA resolve
    15 dos 17 sem avaliar expressao. Numeros conferidos de forma independente. Relatorio em docs/2026-07-27_escopo-flat-modifier.md'
  id: 72
  date: '2026-07-29'
  priority: media
- desc: 'PENDENCIAS MENORES DO REVIEW ADVERSARIAL DE 2026-07-27 (as graves ja foram consertadas no
    mesmo dia). (a) ESCOLHA DE NIVEL FUTURO tem tres tratamentos no mesmo motor: `_atributos` trata
    planejamento como caso normal e ignora, enquanto `_higiene_de_slot` e `_aumentos_de_pericia`
    tratam como erro; alem disso a contagem `len(usados) > len(niveis)` nao filtra por nivel, entao
    quem planeja o nivel 8 numa ficha de nivel 4 leva aviso. Decidir a semantica: ou o documento
    so descreve o presente, ou o motor recorta por nivel em TODA checagem. (b) `em: "criacao"` (string)
    desliga a checagem de nivel da higiene de slot -- e correto para ancestria/background, mas silencia
    feat posto em `criacao` por engano. (c) `_subclasse_de` e sensivel a ordem do array de escolhas
    e alimenta `_dc_de_conjuracao` -- pre-existente, so muda texto, mas e a ultima dependencia de
    ordem que sobrou depois do conserto de `ordem_de_classe`. Relatorio completo em docs/2026-07-27_review-adversarial-grants.md'
  id: 73
  date: '2026-07-29'
  priority: media
- desc: '(a)(b)(c) RESOLVIDOS 2026-07-30, spec specs/2026-07-30-alvo-e-salvaguarda-de-magia.md. O
    item dizia (c) "campo alvos/targets nunca existiu em spell nem ritual (0% estrutural)" e tratava
    como lacuna de FONTE. Nao era: o dump do AoN tem `target` em 1.234 e `saving_throw` em 894, em
    texto simples. Era lacuna de LEITURA -- `magias.py` lia alcance/area/duracao SO do Foundry (`fsys`),
    entao magia sem par la saia vazia mesmo com o AoN preenchido, e alvo/salva nem campo tinham.
    Agora: `alvos` 0 -> 804, `salvaguarda` 0 -> 618, `alcance` 1.116 -> 1.139, `duracao` 1.099 ->
    1.121, `area` 385 -> 412 (de 1.655). Texto cru, sem parse: o Foundry entrega area como `{tipo,valor}`
    e o AoN como "20-foot burst", e converter poria dois formatos no mesmo campo. ARMADILHA: o Foundry
    grava `""` (string vazia) em 515 magias, entao um fallback com `is None` nao dispara -- tem de
    tratar vazio como ausente. Este item so pode ser medido depois de descobrir que `saida/magias.json`
    estava PARADO em 27/07 (o build chamava `magias.py`, que nao escreve nada). || RESTO DO ITEM:
    LACUNAS PONTUAIS DE SPELL/RITUAL/EQUIPAMENTO achadas na validacao por dominio de 2026-07-27.
    BOA NOTICIA primeiro: cobertura de spell e ritual contra o AoN e COMPLETA (0 ausentes nos dois,
    cruzando por nome normalizado no conjunto remaster), `level` em 100% dos 1.655 spells, e as 17
    fichas batem com a formula RAW de AC/ataque/dano sem excecao. As lacunas: (a) 15 spells legacy
    com `acoes` ausente apesar de a prosa trazer ''Cast 10 minutes'' -- buraco de extracao; (b) 23
    spells com `alcance` ausente, mesmo padrao; (c) campo `alvos`/targets nunca existiu em spell
    nem ritual (0% estrutural); (d) `heightened` estruturado cobre 31% dos spells e 42% nao tem nem
    dado nem a flag `heightened_so_prosa`, entao nao da para separar ''sem elevacao'' de ''lacuna'';
    (e) 17 spells zumbi (`desmembrado_de`) com rank/tradicoes ausentes, duplicatas orfas de fusao
    -- o canonico existe completo com outro id; (f) 52 itens de equipment (0,6%) ausentes do AoN,
    entre eles Cloak of Elvenkind, Bag of Holding e Hat of Disguise; (g) relic tem 122 canonicos
    (os 219 incluem 97 duplicatas -legacy) e os niveis de gift sao 100% prosa -- nem o dump do AoN
    usou o campo `type` (Minor/Major/Grand) que a fonte tem; o motor nem reconhece `kind=relic`;
    (h) armaduras e escudos duplicados sem dado mecanico (`wb:armor/leather`, `hide`, `studded-leather`,
    `unarmored` e 7 escudos de material precioso) coexistindo com a versao completa -- artefato de
    extracao, perigoso se o front casar por nome curto; (i) dano com arma finesse usa STR em vez
    de DEX para o Ladino com racket Thief; (j) bulk/carga nao existe no motor'
  id: 79
  date: '2026-07-29'
  priority: media
- desc: '(e) RESOLVIDO 2026-07-30, e ele era maior do que o item dizia. `deity.favored_weapon` tinha
    prefixo `wb:equipment/` em 509 referencias -- e as 509 eram ORFAS, nenhuma resolvia, e nenhum
    portao cobrava porque o portao 3 so varria `requires` e `subclasses`. Com `wb:weapon/`, 480 resolvem;
    28 sao ataque NATURAL (claw, jaws, tail) que nao e arma na base e agora sai como NOME simples,
    sem `wb:`, para nao afirmar id que nao existe. O conserto teve de ser nos DOIS caminhos do extrator:
    o do AoN e o que vence na precedencia, e mexer so no do Foundry nao mudou nada. PORTAO 3 VIROU
    VARREDURA COMPLETA -- lista de campos escrita a mao ja tinha falhado duas vezes (subclasses,
    favored_weapon), entao campo novo com referencia nasce vigiado. A varredura achou 43, e a triagem
    levou a duas correcoes maiores (ver spec de alias de magia). Sobra 1 tolerada e nomeada: `wb:deity/malthus`
    cita `Light Crossbow`, e o AoN nao tem arma com esse nome -- inconsistencia entre duas tabelas
    da propria fonte, e inventar o mapeamento seria pior. || RESTO DO ITEM: PARCIAL, re-medido 2026-07-29
    (auditoria). (a) RESOLVIDO: 0 ids `-legacy` em class.subclasses hoje (eram 46, limpos no commit
    1fbfd7864). (b)(c)(d)(e) IDENTICOS: 10 backgrounds com boosts e skill_training vazios; Focus
    Spells / Improved Evasion / Iron Will / Martial Weapon Mastery orfas de progressao; ikon(21)
    / mythic-calling(15) / element(6) / deviant-ability-classification(10) com 100% grants vazio;
    deity.favored_weapon com prefixo wb:equipment/ em exatamente 509 referencias. || TEXTO ORIGINAL:
    REQUIRES E SUBCLASSES CITANDO SLUG PRE-REMASTER -- levantado pela validacao de feats/ancestrias
    em 2026-07-27, PARCIALMENTE resolvido. A parte do motor esta fechada (item 80: `Base.resolver`
    segue o alias). O que FICA: (a) 46 ids `-legacy` esquecidos no catalogo de `class.subclasses`
    (barbarian, champion, oracle, witch) -- o jogador veria a opcao duplicada, legado e remaster
    lado a lado; (b) 10 backgrounds com `boosts` e `skill_training` vazios apesar de o dado bruto
    existir; (c) 4 class-features (`Focus Spells`, `Improved Evasion`, `Iron Will`, `Martial Weapon
    Mastery`) que nao aparecem em nenhuma `progressao`; (d) os kinds `ikon`, `mythic-calling`, `element`
    e `deviant-ability-classification` com `grants: []` em 100% dos registros, o que explica 37 das
    50 class-features orfas; (e) `deity.favored_weapon` com prefixo errado (`wb:equipment/` em vez
    de `wb:weapon/`) em 509 casos. Cobertura de raro/incomum medida e essencialmente completa: ancestry
    50/50 com distribuicao identica ao AoN, background 0 faltando, heritage 5 (todas common), archetype
    1 (uncommon), feat 32 de 6.085 (so 2 uncommon, 0 rare/unique)'
  id: 83
  date: '2026-07-29'
  priority: media
- desc: '3a RODADA FECHADA 2026-07-30 (relatorio docs/2026-07-30_comparacao-pathbuilder-rodada-3.md).
    Terreno novo: `ancestry_feat` (nunca comparado), Fighter 12 e Ranger 4. UM defeito nosso, e ele
    foi consertado na mesma rodada: `_expr` divide em " or " ANTES de chamar `_atomo`, entao "spellcasting
    class feature with the divine or primal tradition" virava "...with the divine" + "primal tradition"
    e caia inteira em `requires_residuo` -- mesma classe do item 91. A causa NAO era falta de termo
    (`spellcasting_tradition` existe desde 29/07). Consertado reconhecendo a frase antes do corte.
    Junto sairam duas familias irmas que so passaram a ter resposta por causa do item 78 DE HOJE:
    "divine spells" / "bloodline that grants arcane spells" (7 clausulas) e a contracao "you''re
    able to cast spells" (4). Residuo 602 -> 598, e a divergencia do ancestry_feat foi a ZERO. O
    RESTO NAO E DEFEITO: 7 pares novos de renomeacao do Pathbuilder (Shory/Saoc/Irriseni/Quah/Tupilaq
    -> generico, tabela agora com 33 pares, verificados contra os 43.686 docs do AoN); 22 dos 25
    "so no Pathbuilder" do ancestry_feat ele mesmo pinta de vermelho (ele lista as 60 de todas as
    ancestrias, nos oferecemos as 42 da ancestria do personagem); 21 das 26 divergencias do Ranger
    4 sao a familia JA DECLARADA de pericia pendente; e as 5 no sentido contrario sao principio zero
    (pre-requisito narrativo tipo "member of the Ulfen Guard" nao bloqueia aqui e bloqueia la). FICA
    PARA A SEGUNDA LEVA (Wizard 16, Cleric 20, Rogue 8/skill_feat) deu o DEFEITO MAIS GRAVE DO DIA:
    `has` de class-feature era SEMPRE falso em `candidatos()`. A guarda de auto-satisfacao (`f.get("raiz")
    != excluir`) descartava toda feature da PROGRESSAO da classe, porque `raiz` e None e `_avaliando`
    tambem e None fora de `_checar_requisitos` -- e em `candidatos()` ele NUNCA e setado. 139 clausulas
    em 135 registros: um Magus nunca podia pegar feat de Spellstrike (21), um Monge feat de Ki (12).
    Consertado nos dois motores + ficha de validacao com Magus 6. Mais: guarda de `archetype` na
    aba de skill feat do comparador (118 falsos positivos -> 7), `master at` alem de `master in`
    no RANK_RE, e 2 pares novos de renomeacao (tabela em 35). `Lightning Snares` e `Wild Empathy`
    fecharam como recorte de EDICAO (o remaster reclassificou o primeiro; a fonte da razao a nos
    no segundo). FICA PARA A PROXIMA: general feat fora do Guerreiro, e o quantificador "uma pericia
    que tenha a acao X". || TEXTO ORIGINAL: COMPARACAO COM O PATHBUILDER, 1a rodada FECHADA (2026-07-29).
    De 65 pontos sobraram QUATRO, e NENHUM e buraco nosso -- tudo que o Pathbuilder oferece no slot
    de class feat de um Fighter 1, o Waybuilder tambem oferece. Os 61 que sairam eram quatro recortes
    distintos, cada um verificado contra a fonte: (1) o PATHBUILDER renomeia o que a Paizo nao renomeou,
    tirando nome proprio de Golarion (Product Identity) -- a ponte remaster_id do AoN nao registra
    os pares e os nomes curtos dele nao existem em nenhum dos 43.686 docs do dump. A nossa base esta
    certa; virou tabela de traducao em docs/comparacao/equivalencias-pathbuilder.json (22 pares);
    (2) a opcao ''Allow outdated CRB and APG?'' nasce Off e esconde todo o conteudo pre-remaster
    que a nossa base inclui -- a sonda agora liga; (3) renomeacao de VERDADE (`Drow Shootist` ->
    `Crossbow Infiltrator`, feita pela Paizo): o comparador passou a casar por `aliases`; (4) ruido
    de grafia. OS QUATRO QUE SOBRARAM, todos do nosso lado: `Stance Savant` (CRB nv14, nao existe
    no dump do AoN -- removido no remaster e carregado do Foundry legado, DECIDIR se fica), `Chelaxian
    Scion Dedication` (AP #223), `Knight Vigilant` (Character Guide), `Venture-Gossip Dedication`
    (Paizo Blog) -- os tres ultimos sao recorte de fonte do outro lado, nao defeito. Relatorio: docs/2026-07-29_comparacao-pathbuilder.md.
    PROXIMO: outras classes, outros slots (skill/general/ancestry) e niveis altos, onde o predicado
    tem mais o que errar'
  id: 84
  date: '2026-07-29'
  priority: media
- desc: 'Importador do Pathbuilder tem que AVISAR o que se perde. Confirmado com o Igor: o eidolon
    existe no app deles e nao sobrevive ao export. Perda silenciosa e o pior tipo'
  id: 10
  date: '2026-07-29'
  priority: baixa
- desc: 'Cobertura medida em 5 dos 26 livros: Player Core, Player Core 2, War of Immortals e Ancestry
    Guide (1.377 nomes, 99,8% fora rituals) mais Treasure Vault (898 nomes, 100%). Os outros 21 livros
    nao foram testados'
  id: 19
  date: '2026-07-29'
  priority: baixa
- desc: 'POR ULTIMO, decisao do Igor (2026-07-29): opcao de idioma ingles / pt-BR na interface. Depois
    de TODO o resto -- so faz sentido com o app fechado. Escopo a decidir quando chegar a vez: a
    UI (rotulos, botoes, mensagens do motor) e traduzivel; a PROSA das 19.706 entradas vem das fontes
    em ingles e nao tem versao pt-BR licenciada, entao o mais provavel e UI em pt-BR com conteudo
    de regra em ingles. Nome de trait e de entidade idem -- traduzir ''Reactive Strike'' quebraria
    a busca do jogador que le AoN'
  id: 31
  date: '2026-07-29'
  priority: baixa
- desc: 'PARCIAL, re-medido 2026-07-29 (auditoria). CAIU: licenca inferida sem marca zerou (2.494
    hoje, todas marcadas); feat_category ausente 256 -> 172 (o valor bruto ''classfeature'' zerou).
    NAO MUDOU: prov.class inferido (414 de 841). PIOROU: source.page ausente 1.506 -> 1.598, cresceu
    com a base. E `traits` ausente segue em 66 registros (39 class-feature + 27 class), mas hoje
    sai como CHAVE OMITIDA, nao null nem [] -- ver item 53. || TEXTO ORIGINAL: Residuos menores da
    auditoria: wb:archetype/shared-archetype-feats e diretorio de organizacao do Foundry virado arquetipo
    em 14 feats; 1.440 licencas inferidas por heuristica sem marca no registro emitido; prov.class
    ''inferido de traits'' em 409 das 817 class-features; 152 pontos de prov marcados ''desconhecida'';
    65 traits:null contra 3.036 []; 256 feats sem feat_category (3 com valor bruto ''classfeature'');
    1.506 sem source.page'
  id: 34
  date: '2026-07-29'
  priority: baixa
- desc: 'NUMERO ATUALIZADO 2026-07-29 (auditoria): eram 160 registros (0,85%); hoje sao 176 (0,89%)
    -- cresceu proporcionalmente a base. Confirmado por contagem propria contra pipeline/canonico_livros.json.
    Mesmos exemplos: Bastion of Blasphemies, Crypt of Runes, Paizo Blog. || TEXTO ORIGINAL: 160 registros
    (0,85%) tem source.book fora do mapa canonico do AoN: APs recentes (Bastion of Blasphemies, Crypt
    of Runes), Paizo Blog, e siglas cruas do pf2etools (''PC1''). Nao tem grafia duplicada -- so
    nao ha entrada no AoN para canonizar contra. Resolver com mapa de siglas verificado, nunca por
    chute'
  id: 38
  date: '2026-07-29'
  priority: baixa
- desc: 'CORRIGIDO 2026-07-29 (auditoria): eram 684 campos com prov ''desconhecida'' + 128 vazios;
    hoje sao 13. A concentracao antiga (grants, requires, background) zerou. O campo mora so em pipeline/base/index.json
    e e descartado do app por emitir_app.py. Praticamente fechado -- confirmar os 13 e encerrar.
    || TEXTO ORIGINAL: 684 CAMPOS COM prov ''desconhecida'' e 128 com prov vazio. Concentracao: 313
    em `grants`, 308 em `requires`, e por kind 526 em background. O portao 1 nao pega porque ele
    exige que `prov` EXISTA, e ''desconhecida'' existe -- e um nao-resposta que passa. Ou se descobre
    a fonte (background veio de onde?) ou o valor vira explicitamente `null` com o portao cobrando'
  id: 52
  date: '2026-07-29'
  priority: baixa
- desc: 'EXTRATOR REDUNDANTE: `pipeline/extratores/relicos_idiomas.py` roda (esta em rodar.py::EXTRATORES)
    e gera saida/relicos_idiomas.json com 239 registros, mas `relicos_idiomas.json` NUNCA esteve
    em `reconciliar.py::ENTRADA` -- a saida dele nao entra na base. Isso NAO e perda de dado: medido,
    relic e language chegam por `aon_kinds.json`, que cobre melhor (122 de 122 relic da base estao
    la, contra 51 do extrator dedicado; 121 de 123 language contra 95). Ou seja, o extrator dedicado
    e trabalho duplicado que ninguem consome, nao um buraco. Decidir: tirar do runner, ou promover
    a fonte e tirar os dois kinds do aon_kinds. Nao deletei -- mencionar antes de remover'
  id: 61
  date: '2026-07-29'
  priority: baixa
- desc: 'ARMAS SEM DANO -- PARCIALMENTE RESOLVIDO 2026-07-29. Eram 57 armas sem `damage`, mas 41
    sao bombas alquimicas (o dano e do efeito, vazio esta certo), 6 sao municao/magazine/pellet e
    5 sao arma magica ou material que HERDA o dano do item base. Restavam QUATRO de verdade. Blowgun
    e Dart Umbrella FORAM CORRIGIDAS: o AoN traz `damage: ''1 P''` (dano fixo 1, sem dado, que e
    RAW) e o parser de `recuperar_mecanica_equipamento.py` exigia `dN`. Agora ha um segundo padrao
    (`FIXO`) e a representacao OMITE a chave `dado` em vez de grava-la como None -- os dois motores
    fazem `dano.get(''dado'','''')`, e a chave presente com None imprimiria ''None'' na ficha. Travado
    por 3 assercoes no oraculo. FALTAM DUAS: Nine-Ring Sword e Wind and Fire Wheel (Tian Xia) nao
    tem fonte em disco nenhuma -- precisa de dump novo do AoN ou entrada curada'
  id: 85
  date: '2026-07-29'
  priority: baixa
- desc: 'PARCIALMENTE RESOLVIDO 2026-07-29 (spec specs/2026-07-29-termos-de-predicado.md). Tres termos
    novos, e SO onde a base ja respondia: `sense` (le `grants.sense`, 81 registros que ninguem lia
    -- e de quebra a ficha ganhou `visao().sentidos`), `focus_pool` (o motor ja calculava o pool
    da regra 22) e `has_actor` (le a concessao de companheiro derivada no mesmo dia). Medido: predicado
    parseado 3.889 (91,3%) -> 3.919 (92,0%); frase rejeitada inteira 372 -> 342. DECISAO REGISTRADA,
    e ela e resposta e nao divida: alinhamento NAO vira termo -- `evil alignment` (7), `tenets of
    good` (4), `tenets of evil` (4), `any good alignment` (3) somam 18 clausulas de um conceito que
    o Remaster ABOLIU; na base `alignment` so existe em `deity`. Modelar exigiria inventar estado
    de personagem para responder pergunta de edicao anterior. Ficam visiveis em `requires_residuo`,
    como requisito de mesa. O QUE SOBRA, com dado faltando de verdade: `a familiar` (5) -- nao ha
    paralelo do `grant_actor` para familiar, o feat concede por `grant_item` de compendio Foundry;
    `healing font`/`harmful font` (7) -- `divine_font` existe em 479 divindades mas diz o que a DIVINDADE
    permite, nao o que o Clerigo escolheu (sub-escolha nao modelada); e 7 clausulas com tag `{@feat
    X|Fonte}` grudada que o parser nao separou (1% do residuo)'
  id: 87
  date: '2026-07-29'
  priority: baixa
promoted: []
---
