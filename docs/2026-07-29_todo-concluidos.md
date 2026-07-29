# TODO -- itens concluidos do Waybuilder

Arquivados em 2026-07-29 para o TODO.md conter so trabalho vivo.
Sao historico: nao voltam para a fila sem medicao nova.

## Item 1

INVALIDADO 2026-07-26 pela auditoria ampla. Dizia: 'base final 18.176 registros, prosa 100%, 597 pares fundidos, zero par nao unido'. Os tres numeros estavam errados -- prosa e 95% (metrica com denominador errado), e das 597 fusoes so 35% estavam certas. 'Zero par nao unido' media recall sem precisao: fundir tudo com tudo daria zero tambem. Ver itens 24 e 30

## Item 2

CONCLUIDO 2026-07-27. Grafo de progressao de dois niveis: classe -> feature -> sub-escolha. 62 class-features de segundo nivel ficam invisiveis hoje (teses e escolas do Mago, ordens Hellknight, ikons do Exemplar, gates do Kineticist, research fields do Alchemist)

## Item 3

CONCLUIDO 2026-07-29 (auditoria). teste_motor.py:241-249 prova: Cloistered 15 -> master, Warpriest 15 -> expert, mesma classe e nivel -- `class_level` sozinho nao alcancaria. E o nivel do companheiro sai do class_level de quem concedeu (Ranger 2 num personagem 12 -> companheiro nivel 4). || TEXTO ORIGINAL: Linguagem de predicado precisa falar de SUBCLASSE, nao so de classe. A proficiencia de conjuracao do Clerigo depende da Doutrina (Cloistered chega a legendary no 19, Warpriest para em master). Fura a premissa da regra 3 das houserules. Tambem: nivel do companheiro e o class_level de quem o concedeu, nao o nivel de personagem

## Item 4

RESOLVIDO 2026-07-27 com `pipeline/emitir_app.py` (passo 9 do build.sh). O artefato de BUILD e o payload do APP passaram a ser coisas diferentes: o indice de build carrega proveniencia por campo, xref para as tres fontes e registro de conflito -- 5,3 MB dos 13,9 de conteudo, que o construtor nunca le. O corte e por lista NEGRA (`prov`, `xref`, `conflitos`, `texto`, `mechanized`...), nao por lista branca, para que campo novo de extrator entre no payload por padrao em vez de sumir em silencio. Resultado medido: indice completo de 2,15 -> 1,04 MB gzip (52% menor) e, o numero que importa, o NUCLEO para montar ficha (class, class-feature, feat, ancestry, heritage, background, archetype, skill) em 0,49 MB gzip -- abaixo do alvo de 0,53 do projeto. Emite tambem `base/app/por-kind/*.json` para carga sob demanda: equipamento, magia e catalogo so entram quando a tela pedir. A prosa (17,9 MB) continua fora e e buscada por registro. 9 testes em pipeline/testes/test_emitir_app.py, entre eles o do orcamento. O diretorio `base/app/` e gitignored (derivado, 18 MB); so o `_manifesto.json` fica versionado, como registro historico do tamanho. Texto original: Separar indice e prosa no build final. Hoje o index tem 15,2 MB com texto embutido; o alvo medido e 0,53 MB de indice mais prosa sob demanda

## Item 5

CONCLUIDO 2026-07-26: os traits orfaos sao so 16, todos parametrizados -- resolvidos pelo mapa de familias em pipeline/normalizacao_traits.json

## Item 6

CONCLUIDO 2026-07-26: 35 PDFs oficiais extraidos dos zips (1,7 GB em pipeline/dados_brutos/pdfs/, fora do git; os 1.027 mapas .webp ignorados por decisao do Igor). Cobertura auditada, tabelas de conjuracao recuperadas, ambientacao avaliada. ARMADILHA: varios sao scan puro sem camada de texto (War of Immortals, Monster Core, Treasure Vault, Menace Under Otari, Lost Omens.pdf) -- rodar pdffonts antes, zero fontes = scan

## Item 7

CONCLUIDO 2026-07-29 (auditoria). docs/simulacoes/2026-07-27_balanceamento.md cobre niveis 1-15, combos obvias e nao obvias, combate + pericia/social/exploracao, HOUSE vs RAW vs RAW+FA. || TEXTO ORIGINAL: Rodar as simulacoes de balanceamento depois da base fechar DE VERDADE. Simulador e benchmark de 3.624 criaturas ja estao em docs/simulacoes/. O Igor pediu niveis 1-15, muitas combinacoes incluindo as pouco obvias (Monge/Clerigo), e nao so combate -- pericia, social, exploracao, como mestrar uma aventura padrao. Comparar HOUSE vs RAW vs RAW+Free Archetype

## Item 8

CONCLUIDO 2026-07-29 (auditoria). O relatorio de balanceamento ja usa politica de acao SIMETRICA -- que e exatamente a correcao do vies apontado pelo Fable (o dip gastava 12 acoes curando contra um Guerreiro que so atacava). Gear, atributos e alvos declarados no metodo. || TEXTO ORIGINAL: Re-rodar a simulacao de nivel 20 corrigindo o vies apontado pelo Fable: o dip gastava 12 acoes curando e era comparado com um Guerreiro que so ataca. Declarar gear, atributos e nivel dos alvos no documento

## Item 9

CONCLUIDO 2026-07-29 (auditoria). O app existe: Vite + React, PWA offline, sem backend; o picker e um modal reusado em todo slot; o documento de personagem e o proprio JSON. || TEXTO ORIGINAL: O front: PWA client-side, offline, sem backend. Um componente de picker reusado em todo slot. O JSON e a ficha

## Item 11

CONCLUIDO 2026-07-26. BUG barato, subconjunto do 28: aplicar normalizar_livro() antes de COMPARAR source em reconciliar.py. A funcao ja existe mas so roda depois; por isso boa parte dos 72 conflitos de source e falso

## Item 12

CONCLUIDO 2026-07-26 com resultado negativo: a arbitragem contra PDF nao valida a precedencia, porque a PREMISSA e falsa -- as fontes digitais incorporam errata posterior a publicacao, entao o impresso nao e arbitro. Deu 63% geral e 50% nos dois campos de maior volume. Validar de verdade exigiria historico de errata, que nenhuma fonte expoe. Nao trocar a precedencia: sem saber quem erra, inverter so troca qual metade fica errada

## Item 14

CONCLUIDO 2026-07-27. As 11 classes conjuradoras tem tabela de slots completa, 20 niveis, em base/index.json. O Animist era o unico buraco e foi RECUPERADO de fonte que estava em disco desde sempre: o doc de classe do AoN carrega a tabela em HTML no campo `markdown`, e o extrator lia so `text`, que e a projecao achatada sem tabela. O cache do proprio extrator (dados_brutos/aon/class__animist.json) ja tinha o dado -- foi a conclusao errada de que 'nem Foundry nem AoN materializam a tabela' que mandou ler o PDF a olho e gerou o arquivo que se perdeu. Parser em pipeline/tabelas_conjuracao_aon.py, validado contra as outras 10 conjuradoras: reproduz as 10 celula a celula, incluindo truques, contra o pf2etools, que e fonte independente. Animist tem teto de rank 9 (terceira classe assim, junto de Magus e Summoner) mais um slot de apparition rank 10 pela feature Supreme Incarnation, de nivel 19; os dois pools ficam separados em slots_hibridos porque um nao conjura a magia do outro. build.sh rodado e conferido registro a registro contra o commit anterior: 19.738 -> 19.738, zero sumiram, zero nasceram, UM alterado (wb:class/animist, campos spellcasting e prov). Colateral zero.

## Item 15

CONCLUIDO 2026-07-26: os capitulos de ambientacao dos Lost Omens sao flavor puro -- IGNORAR, por decisao do Igor. Verificado por amostragem: o conteudo mecanico daqueles capitulos ja esta na base. Nao criar kinds region/organization como container de texto. A mecanica que sobrou virou o item 22

## Item 16

OBSOLETO 2026-07-29 (auditoria). Decisao de 2026-07-27: o app e para o Igor e a mesa dele, nao vai ser publicado. Marcar Product Identity para build publico deixou de fazer sentido. Reabrir se a decisao mudar. || TEXTO ORIGINAL: Licenciamento antes de publicar: texto de regra sob OGL/ORC e reutilizavel com atribuicao, mas conteudo de Golarion (nomes de deuses, nacoes, organizacoes) e Product Identity e NAO e. Marcar esses registros para poderem ser excluidos de um build publico

## Item 17

CONCLUIDO 2026-07-26. Kind ritual: extrator PRONTO (pipeline/extratores/rituais.py) com 151 registros em pipeline/saida/rituais.json -- a estimativa de 31 era so dos dois Player Core. FALTA: incluir 'rituais.json' no ENTRADA de reconciliar.py. Pendencias menores do extrator: pf2etools nao tem a categoria (cross-check de level caiu para foundry-vs-aon), e 4 requirements ficaram em prosa sem virar predicado

## Item 20

CONCLUIDO 2026-07-26. traits como UNIAO: spec JA corrigida e pipeline/normalizacao_traits.json JA pronto (17 renomeados, 9 removidos sem sucessor, 18 familias parametrizadas, cada entrada com prov citando pagina). FALTA aplicar no reconciliador -- hoje so rituais.py consome o mapa. Responde por 88% dos 2.299 conflitos: 72 facetas complementares, 31 ancestria renomeada, 18 granularidade (two-hand-d12 virava two-hand, perdendo o dado de dano)

## Item 21

CONCLUIDO 2026-07-26. COLISAO DE IDENTIDADE: wb:<kind>/<slug> assume nome unico por kind e nao e. 5 confirmadas contra AoN e Foundry: death-from-above (arquetipo nv8 vs mitico nv16, War of Immortals p.128), reckless-abandon (goblin vs barbaro nv16), dual-weapon-reload, even-the-odds, play-to-the-crowd. Desmembramento proposto caso a caso em docs/2026-07-26_colisoes-identidade.md. Detector melhor que traits disjuntos: registro-irmao com sufixo e xref incompleto -- 59 candidatos com conflito registrado, MAS com falso positivo conhecido nos -greater/-major/-true de item, que sao variantes legitimas. Pendente: ~16 candidatos por salto de level nao verificados, e wb:weapon/temperbrand indeterminado

## Item 23

OBSOLETO 2026-07-29 (auditoria). `Triggerbrand Salvo` ESTA na base -- era falso alarme. Os wayfinders do PFS Guide sao limite de fonte declarado: nenhuma das 3 fontes cobre o PFS Guide. || TEXTO ORIGINAL: Gaps de ingestao achados na verificacao dos Lost Omens: 4 wayfinders do PFS Guide e o feat 'Triggerbrand Salvo' nao estao na base

## Item 24

CONCLUIDO 2026-07-26. CRITICO, FACA PRIMEIRO -- a fusao Legacy<->Remaster destruiu dado. fundir_renomeados.py decide por similaridade de PROSA e deletou 597 registros; 393/597 (65,8%) fundiram registros com level/price_cp/damage diferentes, e amostra de 60 contra o remaster_id do AoN confirmou so 21 (35%) como fusao correta. wb:equipment/aeon-stone engoliu 24 pedras distintas; 'Poi'->'Shield Bash'; 'Tonfa'->'Shuan Ji' (mesmo livro); 6 armas viraram 'Gaff'. REVERTER e refazer usando remaster_id/legacy_id do AoN como chave. Prosa so como desempate. E ANTES de fundir, checar se algum campo estruturado discorda -- se discorda, nao funde

## Item 25

CONCLUIDO 2026-07-26. `mechanized` significa 4 coisas diferentes conforme o extrator: 12.742 registros (70,1%) tem true com grants vazio, e 370 tem false com grants cheio. O false se distribui por KIND inteiro -- e propriedade do extrator, nao do dado. Definir o significado unico na spec e fazer todos obedecerem

## Item 26

CONCLUIDO 2026-07-26. Divergencia silenciada: 6 kinds (class-feature, background, heritage, familiar-ability, ancestry, class) tem 1.618 registros com 2+ fontes e ZERO conflitos registrados. Comprovadas 145 divergencias reais de source.book contra o Foundry, nenhuma anotada. Esses extratores nao implementam deteccao de conflito -- logo 2.299 e PISO, nao total

## Item 27

CONCLUIDO 2026-07-26. Dois kinds que a spec NUNCA listou, medidos contra o censo do AoN: `relic` (-116) e `language` (-85). Mesma classe de erro do ritual -- omissao ao escrever a lista de kinds, nao falha de extrator. Mais: background esta -167 (33% do kind!)

## Item 28

CONCLUIDO 2026-07-26. source.book sai com DUAS grafias para 26 obras, afetando 10.723 registros (59%), mais 160 com \r\n literal dentro do nome. Engloba o item 11 (normalizar_livro rodando so na comparacao): o problema nao e so comparar, e o valor emitido

## Item 29

CONCLUIDO 2026-07-26. Portoes de qualidade: dos 7 da spec, so o 5 esta implementado. O 1 falharia (2.694 sem prov.text), o 3 falharia (111 registros com requires citando 61 ids inexistentes). O portao 7 e TAUTOLOGICO -- pergunta por nome duplicado depois de a duplicata ter sido fundida, que e exatamente a fresta do death-from-above; tem que rodar ANTES da fusao. Implementar os 7 antes de re-emitir, senao a re-emissao repete os mesmos erros em silencio

## Item 30

CONCLUIDO 2026-07-26. 907 registros sem prosa (5,0%), nao os 100% reportados. A metrica de emitir_textos.py divide pelas referencias existentes, nao pela base -- registro sem referencia nenhuma nao entra no denominador. Corrigir a METRICA junto com o buraco, senao ela volta a mentir

## Item 31

CONCLUIDO 2026-07-26. 22 registros so-pf2etools sao duplicatas de registros ja existentes (wb:armor/hide vs wb:armor/hide-armor). Explicam os 6 sem license, os 23 sem rarity e 16 dos sem prosa -- o portao 5 estava detectando FALHA DE CASAMENTO, nao falta de licenca. O sintoma foi lido errado desde o inicio

## Item 32

RESOLVIDO 2026-07-27: spells com `level` foram de 22 para 1.655. Decidido medindo as tres fontes, que usam `level` e nenhuma usa `rank`. Texto original: spell usa `rank` e nunca `level`, fora do envelope da spec -- qualquer filtro por nivel descarta as 1.639 magias em silencio. Mais 513 sem tradicoes, das quais 50 nao sao focus. Decidir: spell vira excecao documentada, ou passa a emitir level tambem

## Item 33

FUNDIDO NO ITEM 55 em 2026-07-29 (auditoria): a metrica '3.033 mono-fonte' nao e reproduzivel como buraco de conteudo -- ela mistura proveniencia com ausencia. O portao 9 passa hoje com 0 ocorrencias inesperadas e cobertura 98,2-100% por raridade. O que falta de verdade e o que o 55 ja lista. || TEXTO ORIGINAL: 3.033 registros mono-fonte AoN com a materia-prima em disco e nao usada. O proprio pipeline ja gravou que faltam 42 nomes presentes no pf2etools, mais 6 deities, 38 familiar-abilities e 15 class-features do checkout do Foundry. Menor esforco por registro ganho de toda a lista

## Item 35

CONCLUIDO 2026-07-29 (auditoria). Os 3 registros (heavy-power-suit, nine-ring-sword, wind-and-fire-wheel) tem hoje `source` com livro e pagina reais e `license: OGL`, resolvidos de carona no re-dump do pf2etools que fechou o item 37. || TEXTO ORIGINAL: DECISAO DO IGOR: 3 registros (wb:armor/heavy-power-suit, wb:weapon/nine-ring-sword, wb:weapon/wind-and-fire-wheel) tem source vazio e nao existem em fonte nenhuma EM DISCO -- nem AoN, nem Foundry, nem o dump local do pf2etools. Vieram de consulta ao vivo ao pf2etools numa sessao antiga. Sao o que resta do portao 5. Opcoes: (a) re-baixar o pf2etools completo e reextrair, (b) marcar license como indeterminada com prov explicita, (c) remover. Nao inventei licenca

## Item 36

CONCLUIDO 2026-07-29 (auditoria). 0 linhas REVISAR no relatorio de colisoes (eram 13); 11 resolvidas por aplicar_curadoria.py. || TEXTO ORIGINAL: 13 colisoes de identidade que desmembrar_colisoes.py NAO resolveu: a base casou com um doc do AoN que nao representa nenhum dos grupos, entao escolher qual e o 'certo' exigiria arbitrar. Listadas em base/relatorio_colisoes.md como REVISAR. E o que resta do portao 7

## Item 37

CONCLUIDO 2026-07-29 (auditoria). 0 arquivos .missing em dados_brutos/pf2etools/ -- buscar_fontes.sh foi reescrito para clonar e fixar Pf2eToolsOrg/Pf2eTools de verdade. || TEXTO ORIGINAL: O dump local do pf2etools esta INCOMPLETO -- ha varios arquivos .missing em dados_brutos/pf2etools/ e a busca por 6 registros conhecidos devolveu zero. Diferente do Foundry e do AoN, essa fonte nao tem script de reconstrucao (buscar_fontes.sh so cobre o Foundry; dump_aon.py cobre o AoN). Enquanto isso, `requires` -- cuja precedencia e pf2etools -- roda com fonte parcial

## Item 39

FECHADO 2026-07-27 como NAO-DEFEITO, por decisao do Igor. Nao havia vazamento: liberar rank de slot vem do nivel de CLASSE (regra 16); heightened vem do nivel de PERSONAGEM dividido por 2 (regra 17), sempre, e independe do teto de slot da classe. Um Magus 20 oficial ja heightena truque e focus spell no rank 10 com slot maximo 9 -- e a regra do trait Cantrip, RAW puro. O campo `elevacao` do motor subtraia um eixo do outro, o que nao significa nada, e a assercao do simular_raw.py travava nessa subtracao. Com o Animist recuperado eram 3 classes e 18 falsas violacoes. Assercao reescrita para os eixos certos (nivel de classe == nivel de personagem; rank_efetivo == ceil(nivel/2)): simulacao de 2.000 personagens agora passa com ZERO violacoes.

## Item 41

FUNDIDO NO ITEM 78 em 2026-07-29 (auditoria): mesmo defeito. O 41 levantou o problema, o 78 mediu a extensao. || TEXTO ORIGINAL: TRADICAO DE MAGIA POR SUBCLASSE nao e modelavel hoje. Sorcerer, Summoner e Witch tem `spellcasting.tradition` gravado como PROSA -- literalmente a string 'variavel (definida pela escolha de bloodline/eidolon/patron)'. A tradicao real vem da subclasse (Genie=arcane, Nymph=primal...) e esta so no texto ('Spell List Arcane'). Consequencia: o predicado `spellcasting_tradition` da spec nao funciona para 3 das 10 classes conjuradoras, e a ficha mostra a string descritiva no lugar da tradicao. Extrair do texto e viavel (padrao 'Spell List <tradicao>'), mas e derivacao de prosa -- decidir se entra

## Item 44

CONCLUIDO 2026-07-29 (auditoria). Nao ha decisao nem integracao pendente: a tabela de conjuracao saiu do campo `markdown` do AoN, e as 11 conjuradoras (Animist incluso) estao completas sem depender dos PDFs. || TEXTO ORIGINAL: REABERTO 2026-07-27 COM BOA NOTICIA: os 35 PDFs NAO se perderam -- estao em pipeline/dados_brutos/pdfs/ NESTE PC (1,7 GB), junto com pipeline/dados_derivados/tabelas_conjuracao_pdf.json com as 11 conjuradoras, livro e pagina. O texto abaixo foi escrito no outro clone, que nao os tinha. Nao ha decisao a tomar sobre rebaixar livro nenhum. O que sobra e a integracao (item 45 / task 16). Texto original: os 35 PDFs oficiais (1,7 GB) sumiram de pipeline/dados_brutos/pdfs/ e os zips de origem tambem nao estao mais no Downloads. Nunca entraram no git (nem deveriam, por peso e licenciamento). Consequencia: nao da para refazer a leitura da tabela do Animist (item 14) nem qualquer nova arbitragem contra impresso. A base emitida NAO depende deles -- as tres fontes digitais continuam inteiras e reconstruiveis. Opcoes: (a) rebaixar os livros e refazer so as paginas 12-13 do War of Immortals, (b) deixar o Animist sem tabela e o motor avisando, (c) achar a tabela numa fonte digital de terceiro. Nao arbitrei

## Item 45

CONCLUIDO 2026-07-27. Perda silenciosa de artefato: criado pipeline/dados_derivados/ (versionado, para tudo que exigiu leitura/julgamento humano) separado de dados_brutos/ (dump reproduzivel por pin, fora do git); registro pipeline/artefatos_perdidos.json com motivo, dano medido e decisao; portao 8 em portoes.py falhando quando documento versionado cita caminho que nao existe e nao esta registrado. Varredura completa feita: dos 42 caminhos citados em arquivos versionados, 3 nao existiam -- tabelas_conjuracao_pdf.json (perda real), _dump_aon_rituais.py e _wb_dump_companheiros.py (substituidos por dump_aon.py, sem perda de dado)

## Item 48

CONCLUIDO 2026-07-27. PORTAO QUE PASSAVA POR AUSENCIA DE DADO -- o pior defeito achado no porte da linha paralela. `indice_aon()` e `indice_foundry()` voltavam VAZIOS nesta maquina (procuravam dados_brutos/foundry_repo/ e dados_brutos/aon_dump/, que aqui se chamam foundry/ e nunca foram gerados), e os portoes 2 e 7 respondiam `return 0` -- ou seja, PASSARAM. Um portao que se desliga sozinho e devolve zero e a mesma falha que ele existe para pegar. Corrigido em tres frentes: (a) comum.packs_foundry() com os dois nomes de pasta, usado por portoes/emitir_textos/aplicar_subclasses/converter_rule_elements (os extratores ja tinham o fallback); (b) indice_aon() cai nos apelidos versionados (dados_brutos/aon_*.json, 33.348 docs) quando aon_dump/ nao existe, completando campo em vez de sobrescrever; (c) portao desligado devolve None e o relatorio diz NAO MEDIDO, que nao conta como aprovacao e bloqueia --gravar-cobertura. Com os indices carregando de verdade o portao 2 passa limpo (0 divergencias de level nao registradas) e o portao 7 acusou 2 colisoes novas -- item 49

## Item 49

RESOLVIDO 2026-07-27, e nao era colisao: as duas eram FALSO POSITIVO do portao 7, e a investigacao rendeu duas regras. (a) `hellknight-dedication` -- feat-1078 (nv6) declara remaster_id apontando para feat-8818, que e `Hellknight Preferment` e JA esta na base com o nome novo. Doc que declara remaster_id e a versao legado de outra coisa, nao entidade a distinguir. (b) `cane-pistol-melee` -- weapon-592--melee e o legado de weapon-215--melee (o remaster tirou o trait `agile`), mesma arma em duas edicoes. Regra 1: descontar do indice por nome todo doc com remaster_id. Regra 2: dois docs que apontam para o MESMO alvo sao a mesma entidade mesmo que o alvo nao esteja no grupo -- foi o caso das 3 magias do Oracle (`Temporal Distortion`, `Time Skip`, `Manifold Lives`), com um doc em Divine Mysteries e outro em Dark Archives (Remastered), ambos com legacy_id spell-1195/1196/1197. Com as duas regras o portao 7 foi de 2 achados falsos para ZERO, e o ruido de 'mesmo level e mesmos traits' caiu de 198 para 20. Os dois `Death from Above` nao declaram remaster_id, entao a colisao real continua sendo pega

## Item 50

CONCLUIDO 2026-07-27 com pipeline/normalizar_traits.py, rodando como passo 7b do build (depois do ultimo escritor de index.json) e ja aplicado na base: 113 conflitos de traits resolvidos, 891 registros normalizados, 0 nome legado de ancestria restante, portao 6 passou de FALHA para OK. ARMADILHA achada ao aplicar: `unir_do_conflito` tratava a chave `antes` -- o valor que `desmembrar_colisoes` DESCARTA de proposito ao realinhar -- como se fosse fonte, e ressuscitava o trait removido: `death-from-above` voltava a ter `archetype` junto de `mythic`, recriando a quimera que o desmembramento desfez. Corrigido com `traits_uniao.e_fonte()`, que so aceita nome de fonte real. Texto original: ORDEM DE PIPELINE, dois defeitos com a mesma raiz. (a) 113 registros ainda tem conflito de `traits` (95 equipment, 8 weapon, 7 feat): a reparacao traits_uniao.unir_do_conflito() roda dentro de reconciliar.main, mas quem CRIA conflito de traits depois dela -- auditar_conflitos.py e desmembrar_colisoes.py, passos 3 e 4 do build.sh -- nao passa pela reparacao. (b) 13 registros carregam nome legado de ancestria nos traits (grippli 5, aasimar 3, gnoll 3, ifrit 2) embora normalizacao_traits.json tenha os 6 mapeamentos: registro de fonte unica nunca passa por unir(), que so e chamado quando ha conflito entre fontes. Os dois somem rodando a normalizacao/reparacao como passo final do build, depois do ultimo escritor da base

## Item 51

CONCLUIDO 2026-07-27: gerar_canonico_livros.py aprende as obras fora do dump do AoN a partir de saida/, preferindo a grafia SEM o prefixo editorial `Pathfinder` (a convencao do AoN) em vez da mais frequente, que entregaria a do Foundry. 46 obras entraram assim e as duas ambiguas caem na mesma grafia. So vale na base depois do item 57. Texto original: DUAS OBRAS DE 236 COM GRAFIA DUPLA: 'Lost Omens: Pathfinder Society Guide' x 'Pathfinder Lost Omens Pathfinder Society Guide', e o mesmo par para 'The Grand Bazaar'. Nao e o normalizador (os dois caem na mesma chave nas duas implementacoes) -- e canonico_livros.json, que so tem entrada para obra presente no dump do AoN: essas duas nao tem, entao canonizar_livro() devolve a grafia de entrada e as duas sobrevivem. Fix: fallback para a grafia mais frequente na propria base quando a chave nao existe no dump

## Item 54

CONCLUIDO 2026-07-29 (auditoria). tactic = 37 e class-kit = 32 na base, exatamente o esperado; o extrator taticas_kits.py existe e esta em reconciliar.py::ENTRADA. || TEXTO ORIGINAL: DOIS KINDS INTEIROS FALTANDO, achados pelo portao 9 (censo do AoN por categoria, criado 2026-07-27). `tactic` -- as 37 tacticas do Commander, Battlecry! -- e `class-kit` -- os 32 kits de equipamento inicial. Nenhum dos outros portoes podia ver: nao houve queda de cobertura (nunca existiram), nao houve referencia orfa, nao houve conflito. Os dois dumps JA ESTAO em disco (dados_brutos/aon_tactics.json e aon_class_kits.json), entao falta extrator e entrada em reconciliar.py, nao coleta. O `tactic` importa para o construtor: e escolha de personagem do Commander

## Item 56

CONCLUIDO 2026-07-29 (auditoria). 0 registros pre-remaster sem contrapartida (eram 69), reproduzindo a metodologia contra a ponte do AoN. Acrobat e Master Spotter, os exemplos citados, resolvem hoje para o sucessor. || TEXTO ORIGINAL: 69 REGISTROS SERVINDO CONTEUDO PRE-REMASTER SEM CONTRAPARTIDA. Medido em 2026-07-27 contra a ponte do AoN: 646 registros tem xref.aon apontando para um doc que o AoN marca com remaster_id de MESMA categoria (ou seja, doc legado com sucessor real). Em 577 deles o sucessor tambem esta na base como registro proprio -- isso e esperado e correto, e a fusao vetada por campo estruturado divergente (regra do item 24: se discorda, nao funde). Os outros **69 nao tem sucessor nenhum na base**, entao o unico dado disponivel e o pre-remaster: 63 sao arquetipos (Acrobat archetype-45 -> archetype-236, Archer, Assassin, Bard, Bastion, Archaeologist...), mais master-spotter e outros. Como o extrator casa por nome e o nome nao mudou, ninguem percebeu. Separado disto e sem acao: 38 class-features cujo remaster_id aponta para a CLASSE (padrao do AoN, o veto por `kind` ja barra) e 71 com remaster_id='0' = removido no remaster e mantido de proposito

## Item 57

RESOLVIDO 2026-07-27: dump completo do AoN gerado (93 categorias, 43.686 docs) e a base re-emitida com sucesso -- 19.705 registros, 54 kinds, nove portoes verdes. Os extratores que degradavam tinham dois bugs reais, corrigidos: ancestrias.py (caminho foundry_repo + glob nao-recursivo escondendo 182 de 515 backgrounds) e classes.py (apostrofo como separador no slug). Texto original: BLOQUEIO PARA RE-EMITIR A BASE, descoberto 2026-07-27 ao tentar. Duas coisas independentes. (a) PROCEDENCIA MISTA: dos 15 arquivos de pipeline/saida/, NOVE vieram da linha paralela (ancestrias, aon_kinds, classes, companheiros, feats, magias, referencia, relicos_idiomas, rituais) e SEIS da linha do GitHub (equipamento, conjuracao, tabelas_conjuracao_aon e as estatisticas). O merge de 27/07 resolveu os 36 conflitos pela versao do GitHub, mas arquivo que so um lado mexeu entrou sem conflito. Consequencia: a base commitada NAO e reproduzivel a partir do que esta em disco -- um rebuild deu +449 registros, 341 sumidos e 790 novos, misturando as duas linhas. (b) RE-EXTRAIR NAO RESOLVE NESTA MAQUINA: rodando os 9 extratores com o codigo desta linha, `ancestrias.json` caiu de 910 para 0 registros e `aon_kinds.json` de 1.403 para 0, `equipamento.json` perdeu 86 e `classes.json` trocou 47 ids -- e TODOS sairam com exit 0. Falta `dados_brutos/aon_dump/` (o dump completo; aqui so existem os apelidos por categoria). O .gitignore justifica excluir dados_brutos alegando 'reconstruivel pelos pins', e isso e falso enquanto dump_aon.py nao rodar. ORDEM PARA DESTRAVAR: rodar dump_aon.py, re-extrair os 9, conferir cada saida contra o commitado, so entao re-emitir

## Item 58

RESOLVIDO 2026-07-27 na re-emissao: desmembrados caiu de 310 para 125. Texto original: 217 REGISTROS DUPLICADOS na base, medidos direto no artefato commitado (sem rebuild). Dos 310 desmembrados, 217 foram criados a partir de um doc LEGADO do AoN (doc que declara remaster_id), quase todos equipment (210). Exemplo: `wb:feat/play-to-the-crowd-concentrate` nasceu de feat-1978, que e o legado de feat-6335 -- que ja e `wb:feat/play-to-the-crowd`. O mesmo feat entrou duas vezes. Causa: `desmembrar_colisoes.py` montava o indice por nome com TODOS os docs do AoN, sem descontar legado, entao todo nome que o remaster renomeou virava 'colisao'. CORRIGIDO no codigo em 2026-07-27 (mesmo filtro do portao 7): num build limpo os irmaos caem de 310 para 2. Os 217 so somem quando a base for re-emitida -- depende do item 57

## Item 62

RESOLVIDO 2026-07-27. `_grants_em_cadeia` passou a APLICAR o que a cadeia concede com alvo estatico (o dinamico `{item|...}` continua so sinalizado, porque depende de escolha ainda nao feita): class-feature vira linha de feature, feat vira feat efetivo, e `_proficiencias`/`_hp`/`_termo_has` leem os feats efetivos em vez de so os escolhidos. Os tres casos medidos foram conferidos na ficha depois do conserto: battle-harbinger 52 -> 56 HP (e pegar Toughness a mao junto NAO soma duas vezes); shieldmarshal com `society: expert`; Fighter 4 + barbarian-dedication com Rage nas features. Mais: `wizard-dedication` da `arcana: trained`, `skill_training.auto` de feat treina pericia e `skill_training.free` soma ao orcamento. A visao ganhou `concedidos` (id, nome, origem) e a ficha imprime 'Concedido (nao escolhido)'. Os 4 expectedFailure de motor/testes/test_free_archetype.py viraram teste normal. Texto original: QUANTIFICADO 2026-07-27 com tres casos verificados na ficha: (a) HP -- `battle-harbinger-dedication` concede Toughness por `grant_item`, e Toughness tem `flat_modifier: {selector: hp, value: @actor.level}`, que o motor SABE somar. Resultado: 52 HP com a dedicacao contra 56 pegando Toughness a mao, num nivel 4. Faltam exatamente `nivel` pontos; (b) PERICIA -- `shieldmarshal-dedication` concede `{proficiency: {society: expert}}`, chave PLANA que o motor ja le de classe, e a linha de Society nem aparece na ficha; (c) FEATURE -- Fighter 4 + `barbarian-dedication` sai com features `[Reactive Strike, Shield Block, Bravery, Warrior of Legend]`, sem Rage. Causa unica: `_proficiencias` percorre classes e `self.features`, nunca os feats escolhidos; de feat o motor so aproveita `flat_modifier` de HP. Distribuicao entre as 226 dedicacoes: grant_item 114, grant_feat 67 (todos com alvo estatico), proficiency 49, flat_modifier 34, skill_training 20. Texto original: FREE ARCHETYPE -- O MOTOR NAO ENTREGA O QUE A DEDICACAO PROMETE. Achado central da rodada de agentes de 2026-07-27, e o mais importante para o objetivo do Igor. O motor le `grants` so para as chaves planas de CLASSE e de FEATURE; `grant_feat`/`grant_item` ficam INERTES e grants de FEAT ESCOLHIDO nunca sao aplicados. Medido: 388 registros concedem algo resolvivel (249 feat, 71 class-feature, 42 heritage, 24 background), entre eles 68 DEDICACOES de arquetipo. barbarian-dedication deveria dar `wb:class-feature/rage`; cleric-dedication, `deity-cleric`; ranger-dedication, `hunt-prey`; witch-dedication, `familiar-witch`; alchemist-dedication, `alchemical-crafting` + `quick-alchemy`; swashbuckler-dedication, `panache` + `stylish-combatant`. Pior: ate grant PLANO de feat e ignorado -- `wizard-dedication` tem `{"proficiency": {"arcana": "trained"}}` e a ficha sai com arcana sem rank. Sob Free Archetype, que e a regra 2 e esta SEMPRE ligada, isso significa que a dedicacao entra no slot e nao entrega nada. Consertar em `motor.py::_proficiencias` (aplicar grants de feat) e no ponto que aplica `grant_feat`. O guarda de profundidade ja existe, entao nao ha risco de loop

## Item 63

RESOLVIDO 2026-07-27 em `_higiene_de_slot`, chamado no fim de `_slots_de_feat`. Confronta gasto com slot nos cinco trilhos (class/skill/general/ancestry/free_archetype): mais escolhas que slots, escolha em nivel sem slot, e feat sem trait `archetype` no slot gratuito. Sinaliza em `avisos`, nunca recusa (principio zero). Os 3 expectedFailure viraram teste normal. Texto original: FREE ARCHETYPE -- HIGIENE DE SLOT INEXISTENTE. `motor.py::_slots_de_feat` coleta as escolhas em `self.gastos` mas NUNCA as confronta com `self.slots`. Consequencias medidas com fichas de teste em motor/exemplos/: (a) feat SEM trait `archetype` entra no slot de free_archetype sem aviso -- `Reactive Shield`, traits `['fighter','guardian']`, ocupa o slot e a ficha sai limpa; (b) pick de free_archetype em nivel IMPAR passa; (c) 3 picks num personagem com 2 slots passa. Um unico ponto de conserto resolve os tres. Fonte de dado existe: 2.128 feats tem trait `archetype`

## Item 64

RESOLVIDO 2026-07-27, as duas. (1) `_exige_a_dedicacao_do_arquetipo`: feat com trait `archetype` e sem `dedication` exige a Dedication daquele arquetipo, achada por `Base.dedicacao_do_arquetipo` -- o vinculo e 1:1 na base (225 arquetipos, nenhum com duas dedicacoes), entao nao precisou de lista escrita a mao; se o `requires` ja reprovou pela mesma dedicacao, o motivo nao e repetido. (2) `_nova_dedicacao_exige_dois_feats`: percorre os picks em ordem de nivel e cobra 2 feats nao-dedicacao de cada arquetipo ja dedicado antes de aceitar a proxima. O texto RAW foi conferido na PROPRIA base antes de codar (76 dedicacoes repetem a clausula 'two other feats from the <X> archetype'), nao de memoria. Os 2 expectedFailure viraram teste normal. Texto original: FREE ARCHETYPE -- DUAS REGRAS DO PF2e QUE NAO EXISTEM NEM NO DADO NEM NO CODIGO. (1) 'nao se pode pegar uma NOVA dedicacao antes de ter 2 outros feats do arquetipo anterior' -- e a regra que impede colecionar dedicacao; sem ela um nivel 20 pega 10 dedicacoes e o Free Archetype vira buffet. Testado: Archer Dedication no nv2 e Marshal Dedication no nv4 com zero feats de Archer no meio nao gera sinal nenhum. (2) 'feat de arquetipo exige a dedicacao daquele arquetipo' como regra ESTRUTURAL e nao caso a caso -- hoje o motor so sabe pelo `requires` da base, e em 181 feats de arquetipo nao-dedicacao o `requires` nao cita dedicacao alguma (so nivel), entao o motor fica calado. As duas sao derivaveis do dado que ja existe (trait `dedication` + o arquetipo dono do feat). Lembrar do PRINCIPIO ZERO: sinalizar, nunca bloquear

## Item 66

CONCLUIDO 2026-07-29. `_conjuracao_de_arquetipo` entrou as 16:06 (commit 4d74a824b): Cleric Dedication + Basic Cleric Spellcasting devolve tradicao divine e rank trained, nao mais lista vazia. || TEXTO ORIGINAL: MOTOR -- conjuracao por dedicacao nao entra na ficha. `motor.py::_conjuracao` itera so `ordem_de_classe`, entao Cleric Dedication + Basic Cleric Spellcasting no trilho gratuito produz `conjuracao: []`. A regra 18 fala em slots de arquetipo que a visao calculada nao tem. Menor, mas quebra o caso 'conjurador por arquetipo', que e comum em mesa

## Item 67

RESOLVIDO 2026-07-27 em `_aumentos_de_pericia`, chamado no fim de `_proficiencias`. A cadencia vem do DADO: as 27 classes da base declaram `skill_increase.levels` -- 25 no padrao [3,5,..,19] e 2 (Ladino e Investigador) em todo nivel de 2 a 20 --, e vale a regra 15 (a cadencia de uma classe conta do nivel de personagem em que ela entrou). O aumento sobe um degrau, serve para entrar numa pericia (untrained -> trained, que e RAW), e respeita o teto por nivel (master >= 7, legendary >= 15). Higiene junto: aumento a mais ou em nivel sem aumento e sinalizado, nunca recusado. Ficha de referencia nova em motor/exemplos/ladino4-aumentos-de-pericia.json e 14 testes em motor/testes/test_aumento_de_pericia.py. NAO fecha a metrica do item 68: os 62,4% foram a 62,9% porque as fichas derivadas dos iconics nao declaram em que nivel cada aumento foi gasto -- falta o oraculo, nao o motor. Texto original: MOTOR NAO IMPLEMENTA `skill_increase`. O schema do documento de personagem declara o slot (specs/2026-07-26-schema-personagem.md:173) e `grep -n skill_increase motor/motor.py` devolve ZERO. Ou seja: o aumento de pericia por nivel -- que no PF2e acontece nos niveis 3, 5, 7, 9... e e uma das poucas escolhas que TODO personagem faz -- nao existe no motor. Achado pela validacao de pericia contra os iconics: 775 dos 777 pontos divergentes sao o motor dando rank MENOR que o oficial, e a causa e essa mais a falta de oraculo de 'em que nivel cada aumento foi gasto'

## Item 71

CONCLUIDO 2026-07-29 (auditoria). derivar_gate_nivel.py:92-104 emite `any` sobre TODOS os traits de classe; medido na base de hoje: 123 feats com class_level dentro de `any` (o item falava de 122). Reach Spell, Blind-Fight e Animal Companion conferidos um a um. || TEXTO ORIGINAL: GATE DE NIVEL TRAVA O FEAT NA PRIMEIRA CLASSE EM ORDEM ALFABETICA -- 122 feats. Achado 2026-07-27 pela varredura de ruido de avisos, confirmado direto na base. `pipeline/derivar_gate_nivel.py:92-94` faz `sorted(traits & set(classes))[0]` quando o feat tem MAIS DE UM trait de classe, e emite `class_level` so daquela. Efeito: `Reach Spell` (traits bard/cleric/druid/oracle/sorcerer/witch/wizard) saiu com `class_level: {bard: >=1}`, entao pelo motor um Mago NAO pode pegar Reach Spell; `Blind-Fight` (fighter/investigator/ranger/rogue) ficou preso em fighter; `Animal Companion` (druid/ranger) em druid. Medido: 132 feats tem 2+ traits de classe e 122 sairam com gate de uma classe so. Gerou 45 falsos positivos em 31 das 129 fichas de iconic. Isto dói DOBRADO na houserule, que e multiclasse por nivel: e justo o feat que um Guerreiro 2/Ladino 2 deveria alcancar pelos dois lados. Conserto: quando houver N traits de classe, emitir `any` sobre as N. Exige re-rodar o passo do gate e re-emitir index.json

## Item 74

CONCLUIDO 2026-07-29 (auditoria). `_orcamento_de_boost` (motor.py:655-692) confronta direito com declarado. Ficha sem boosts_livres agora avisa: 'boosts de atributo: 0 declarado(s) de 9 a que o personagem tem direito -- faltam 9', com as fontes discriminadas. A alegacao central do item ('NENHUM aviso') nao se sustenta mais. || TEXTO ORIGINAL: ATRIBUTO NAO TEM HIGIENE -- ficha sem boost declarado sai com tudo 10 e NENHUM aviso. Achado 2026-07-27 pela rodada de fichas montadas, e confirmado direto: removendo as escolhas `boosts_livres` do documento, os atributos caem para 10/10/10/10/10/10, o HP cai de 52 para 48 e `avisos` fica vazio. O motor APLICA o que o jogador declara em `boosts_livres` (a formulacao 'boosts nunca sao aplicados' e imprecisa), mas nunca confronta DIREITO com DECLARADO: `_atributos::aplicar_boosts` so soma quando `opcoes` tem tamanho 1, e tudo que e livre ou escolha-entre-N vira linha no log `origem_boost`, que nem aparece na ficha renderizada. Afeta praticamente toda ficha: os 524 backgrounds tem esse padrao, Human tem 2 livres, e o key ability de Fighter/Ranger/Champion/Monk/Magus/Exemplar e escolha entre 2. E a MESMA classe de defeito do item 63 (higiene de slot), so que em atributo: falta o `_higiene_de_boost` -- quantos boosts o personagem tem direito por nivel/ancestria/background/classe, quantos declarou, e o que falta escolher

## Item 76

RESOLVIDO 2026-07-27 em `emitir_textos.py`: depois de gravar os sidecars, a copia inline sai do indice -- e SO quando o ponteiro resolve de fato no arquivo recem-escrito. A ordem foi invertida de proposito (sidecar primeiro, remocao depois): na ordem original, uma falha entre as duas escritas apagaria a unica prosa do registro. Texto original: PROSA VAZANDO INLINE NO INDICE -- 1.858 registros. Achado 2026-07-27 ao medir a composicao do index.json por campo. A arquitetura e: prosa vive em `base/text/<kind>.json` e o indice aponta por `text: wb:text/<kind>/<slug>`. Mas 1.858 registros trazem TAMBEM um campo `texto` com a prosa embutida, somando 1,77 MB (12,7% do indice). Nao e so peso: e duas copias da mesma prosa que podem divergir. `emitir_app.py` ja descarta o campo no payload do cliente, entao nao chega no app -- mas a causa segue no pipeline e precisa ser achada (algum extrator ou o emissor de textos emite os dois). Descobrir qual passo grava `texto` e faze-lo gravar so o ponteiro

## Item 80

RESOLVIDO 2026-07-27. O MOTOR NAO RESOLVIA ALIAS, E O PORTAO 3 RESOLVIA -- portao verde escondendo defeito, que e pior que portao ausente. A base guarda o nome PRE-REMASTER como alias (`wb:feat/stunning-fist` e o mesmo feat que `stunning-blows`, `wild-shape` virou `untamed-form`, `divine-ally` virou `devout-blessing`): sao 348 ids alternativos. O portao 3 sempre resolveu alias antes de reclamar e por isso reportava ZERO orfaos; o motor comparava id cru em `_termo_has`, entao 24 referencias de `requires` de feats de classes centrais NUNCA eram satisfeitas, por mais que o personagem tivesse o feat. Consertado com `Base.resolver()`, que so age sobre id que nao existe (id valido nunca e desviado por alias homonimo). 5 testes em test_cadeia_de_grants.py. Achado pela validacao por dominio, que reportou 44 ocorrencias -- sao 24 ids distintos, todos resolviveis por alias

## Item 81

RESOLVIDO 2026-07-27. DERIVACAO 19x MAIS RAPIDA: 5,76 ms -> 0,30 ms por ficha de nivel 20. O profile de um teste de carga de 285 fichas mostrou ~90% do tempo em `_classes_multiclasse`, que varria os 19.705 registros da base A CADA `Personagem` novo -- o cache era de INSTANCIA, quando o resultado depende so do catalogo. Movido para `Base.multiclasse()`. Era o unico ponto medido cujo custo escalava com o tamanho da BASE em vez do tamanho da FICHA, que e exatamente o que nao pode acontecer num app client-side que re-deriva a ficha a cada clique. A suite do motor tambem caiu de 9,5 s para 3,5 s

## Item 82

RESOLVIDO 2026-07-27. PSYCHIC ERA A UNICA CLASSE SEM `key_ability`, e a causa nao era o extrator: o Foundry declara `system.keyAbility.value: []` para ela, porque modela a chave pela subclasse (subconscious mind). A prosa oficial diz `Key Attribute: Intelligence or Charisma`. Corrigido por CURADORIA versionada (`dados_derivados/correcoes_curadas.json` + `aplicar_curadoria.py`, passo 4i do build), com a guarda que importa: cada entrada declara o `valor_atual` que espera achar, e se a fonte consertar o dado o passo FALHA ALTO em vez de sobrescrever em silencio um valor que passou a estar certo. Achado por teste de carga: das 285 fichas geradas, as 6 unicas que violaram a regra 8 eram Psychic como primeira classe

## Item 86

RESOLVIDO 2026-07-29 (spec specs/2026-07-29-requisito-parcial.md). A premissa mudou na medicao: 158 dos 178 alvos JA tinham o pre-requisito estruturado no Foundry, em itens atomicos -- nao era falta de fonte, era o parser tudo-ou-nada (`_combinar` devolvia None se qualquer clausula falhasse, e o gate de nivel preenchia o vazio, disfarcando a perda de 'dado pobre'). Agora o parser emite o que deu (`parse_parcial`) e o resto vai por escrito em `requires_residuo`, que o motor NUNCA avalia e a tela mostra como 'requisito de mesa' -- principio zero aplicado ao pre-requisito. Medido: predicado parseado 3.609 (84,7%) -> 3.889 (91,3%); frase rejeitada inteira 652 -> 372; residuo por escrito 0 -> 593; divergencia com o Pathbuilder (Fighter 6, dedicacao) 52 -> 23. O portao 1 passou a cobrar `prov` do campo novo. FICA PENDENTE, e agora com nome: os padroes mecanicos que o schema de predicado nao modela -- `tenets of good` (20), `low-light vision` (11), `focus pool` (10), `an animal companion` (6), `a familiar` (5). Cada um pede um termo novo; hoje estao visiveis em `requires_residuo` em vez de invisiveis

