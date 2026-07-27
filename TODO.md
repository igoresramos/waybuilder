---
project: waybuilder
items:
  # ==========================================================================
  # BLOCO 1 -- RE-EMISSAO DA BASE. Nada de construtor antes disto.
  # Ordem sugerida: 24 -> 29 -> 21 -> 20 -> 28/11 -> 17 -> 27 -> 26 -> 25 -> 30
  # ==========================================================================
  - id: 24
    texto: "CONCLUIDO 2026-07-26. CRITICO, FACA PRIMEIRO -- a fusao Legacy<->Remaster destruiu dado. fundir_renomeados.py decide por similaridade de PROSA e deletou 597 registros; 393/597 (65,8%) fundiram registros com level/price_cp/damage diferentes, e amostra de 60 contra o remaster_id do AoN confirmou so 21 (35%) como fusao correta. wb:equipment/aeon-stone engoliu 24 pedras distintas; 'Poi'->'Shield Bash'; 'Tonfa'->'Shuan Ji' (mesmo livro); 6 armas viraram 'Gaff'. REVERTER e refazer usando remaster_id/legacy_id do AoN como chave. Prosa so como desempate. E ANTES de fundir, checar se algum campo estruturado discorda -- se discorda, nao funde"
    prioridade: concluido
  - id: 29
    texto: "CONCLUIDO 2026-07-26. Portoes de qualidade: dos 7 da spec, so o 5 esta implementado. O 1 falharia (2.694 sem prov.text), o 3 falharia (111 registros com requires citando 61 ids inexistentes). O portao 7 e TAUTOLOGICO -- pergunta por nome duplicado depois de a duplicata ter sido fundida, que e exatamente a fresta do death-from-above; tem que rodar ANTES da fusao. Implementar os 7 antes de re-emitir, senao a re-emissao repete os mesmos erros em silencio"
    prioridade: concluido
  - id: 21
    texto: "CONCLUIDO 2026-07-26. COLISAO DE IDENTIDADE: wb:<kind>/<slug> assume nome unico por kind e nao e. 5 confirmadas contra AoN e Foundry: death-from-above (arquetipo nv8 vs mitico nv16, War of Immortals p.128), reckless-abandon (goblin vs barbaro nv16), dual-weapon-reload, even-the-odds, play-to-the-crowd. Desmembramento proposto caso a caso em docs/2026-07-26_colisoes-identidade.md. Detector melhor que traits disjuntos: registro-irmao com sufixo e xref incompleto -- 59 candidatos com conflito registrado, MAS com falso positivo conhecido nos -greater/-major/-true de item, que sao variantes legitimas. Pendente: ~16 candidatos por salto de level nao verificados, e wb:weapon/temperbrand indeterminado"
    prioridade: concluido
  - id: 20
    texto: "CONCLUIDO 2026-07-26. traits como UNIAO: spec JA corrigida e pipeline/normalizacao_traits.json JA pronto (17 renomeados, 9 removidos sem sucessor, 18 familias parametrizadas, cada entrada com prov citando pagina). FALTA aplicar no reconciliador -- hoje so rituais.py consome o mapa. Responde por 88% dos 2.299 conflitos: 72 facetas complementares, 31 ancestria renomeada, 18 granularidade (two-hand-d12 virava two-hand, perdendo o dado de dano)"
    prioridade: concluido
  - id: 28
    texto: "CONCLUIDO 2026-07-26. source.book sai com DUAS grafias para 26 obras, afetando 10.723 registros (59%), mais 160 com \\r\\n literal dentro do nome. Engloba o item 11 (normalizar_livro rodando so na comparacao): o problema nao e so comparar, e o valor emitido"
    prioridade: concluido
  - id: 11
    texto: "CONCLUIDO 2026-07-26. BUG barato, subconjunto do 28: aplicar normalizar_livro() antes de COMPARAR source em reconciliar.py. A funcao ja existe mas so roda depois; por isso boa parte dos 72 conflitos de source e falso"
    prioridade: concluido
  - id: 17
    texto: "CONCLUIDO 2026-07-26. Kind ritual: extrator PRONTO (pipeline/extratores/rituais.py) com 151 registros em pipeline/saida/rituais.json -- a estimativa de 31 era so dos dois Player Core. FALTA: incluir 'rituais.json' no ENTRADA de reconciliar.py. Pendencias menores do extrator: pf2etools nao tem a categoria (cross-check de level caiu para foundry-vs-aon), e 4 requirements ficaram em prosa sem virar predicado"
    prioridade: concluido
  - id: 27
    texto: "CONCLUIDO 2026-07-26. Dois kinds que a spec NUNCA listou, medidos contra o censo do AoN: `relic` (-116) e `language` (-85). Mesma classe de erro do ritual -- omissao ao escrever a lista de kinds, nao falha de extrator. Mais: background esta -167 (33% do kind!)"
    prioridade: concluido
  - id: 26
    texto: "CONCLUIDO 2026-07-26. Divergencia silenciada: 6 kinds (class-feature, background, heritage, familiar-ability, ancestry, class) tem 1.618 registros com 2+ fontes e ZERO conflitos registrados. Comprovadas 145 divergencias reais de source.book contra o Foundry, nenhuma anotada. Esses extratores nao implementam deteccao de conflito -- logo 2.299 e PISO, nao total"
    prioridade: concluido
  - id: 25
    texto: "CONCLUIDO 2026-07-26. `mechanized` significa 4 coisas diferentes conforme o extrator: 12.742 registros (70,1%) tem true com grants vazio, e 370 tem false com grants cheio. O false se distribui por KIND inteiro -- e propriedade do extrator, nao do dado. Definir o significado unico na spec e fazer todos obedecerem"
    prioridade: concluido
  - id: 30
    texto: "CONCLUIDO 2026-07-26. 907 registros sem prosa (5,0%), nao os 100% reportados. A metrica de emitir_textos.py divide pelas referencias existentes, nao pela base -- registro sem referencia nenhuma nao entra no denominador. Corrigir a METRICA junto com o buraco, senao ela volta a mentir"
    prioridade: concluido
  - id: 14
    texto: "CONCLUIDO 2026-07-27. Tabela numerica de slots de conjuracao: NENHUMA das 11 classes tem. Recuperadas do PDF e guardadas em pipeline/dados_brutos/tabelas_conjuracao_pdf.json: Animist (War of Immortals p.12-13, hibrido prepared divine + spontaneous pela apparition), Magus e Summoner (Secrets of Magic). Exemplar e Kineticist confirmados NAO-conjuradores. Faltam as 8 do Player Core / Player Core 2"
    prioridade: concluido
  - id: 31
    texto: "CONCLUIDO 2026-07-26. 22 registros so-pf2etools sao duplicatas de registros ja existentes (wb:armor/hide vs wb:armor/hide-armor). Explicam os 6 sem license, os 23 sem rarity e 16 dos sem prosa -- o portao 5 estava detectando FALHA DE CASAMENTO, nao falta de licenca. O sintoma foi lido errado desde o inicio"
    prioridade: concluido
  - id: 32
    texto: "spell usa `rank` e nunca `level`, fora do envelope da spec -- qualquer filtro por nivel descarta as 1.639 magias em silencio. Mais 513 sem tradicoes, das quais 50 nao sao focus. Decidir: spell vira excecao documentada, ou passa a emitir level tambem"
    prioridade: media
  - id: 33
    texto: "3.033 registros mono-fonte AoN com a materia-prima em disco e nao usada. O proprio pipeline ja gravou que faltam 42 nomes presentes no pf2etools, mais 6 deities, 38 familiar-abilities e 15 class-features do checkout do Foundry. Menor esforco por registro ganho de toda a lista"
    prioridade: media
  - id: 18
    texto: "Tres ausencias pontuais confirmadas contra o PDF: 'Life-Saving Yowl' (feat de Catfolk nivel 17, Player Core 2) nao existe na base; 'Cavern Kobold' e 'Spellscale Kobold' (Ancestry Guide) sao herancas legacy sem alias. Reconferir depois do item 24 -- podem ser vitimas da fusao por prosa"
    prioridade: media
  - id: 23
    texto: "Gaps de ingestao achados na verificacao dos Lost Omens: 4 wayfinders do PFS Guide e o feat 'Triggerbrand Salvo' nao estao na base"
    prioridade: baixa
  - id: 34
    texto: "Residuos menores da auditoria: wb:archetype/shared-archetype-feats e diretorio de organizacao do Foundry virado arquetipo em 14 feats; 1.440 licencas inferidas por heuristica sem marca no registro emitido; prov.class 'inferido de traits' em 409 das 817 class-features; 152 pontos de prov marcados 'desconhecida'; 65 traits:null contra 3.036 []; 256 feats sem feat_category (3 com valor bruto 'classfeature'); 1.506 sem source.page"
    prioridade: baixa
  - id: 13
    texto: "A regra de precedencia grants->foundry e letra morta: grants nunca gera conflito real no dataset, o merge adota silenciosamente o lado nao-vazio. Ou exercitar ou remover da spec"
    prioridade: baixa

  - id: 35
    texto: "DECISAO DO IGOR: 3 registros (wb:armor/heavy-power-suit, wb:weapon/nine-ring-sword, wb:weapon/wind-and-fire-wheel) tem source vazio e nao existem em fonte nenhuma EM DISCO -- nem AoN, nem Foundry, nem o dump local do pf2etools. Vieram de consulta ao vivo ao pf2etools numa sessao antiga. Sao o que resta do portao 5. Opcoes: (a) re-baixar o pf2etools completo e reextrair, (b) marcar license como indeterminada com prov explicita, (c) remover. Nao inventei licenca"
    prioridade: media
  - id: 36
    texto: "13 colisoes de identidade que desmembrar_colisoes.py NAO resolveu: a base casou com um doc do AoN que nao representa nenhum dos grupos, entao escolher qual e o 'certo' exigiria arbitrar. Listadas em base/relatorio_colisoes.md como REVISAR. E o que resta do portao 7"
    prioridade: media
  - id: 37
    texto: "O dump local do pf2etools esta INCOMPLETO -- ha varios arquivos .missing em dados_brutos/pf2etools/ e a busca por 6 registros conhecidos devolveu zero. Diferente do Foundry e do AoN, essa fonte nao tem script de reconstrucao (buscar_fontes.sh so cobre o Foundry; dump_aon.py cobre o AoN). Enquanto isso, `requires` -- cuja precedencia e pf2etools -- roda com fonte parcial"
    prioridade: alta
  - id: 38
    texto: "160 registros (0,85%) tem source.book fora do mapa canonico do AoN: APs recentes (Bastion of Blasphemies, Crypt of Runes), Paizo Blog, e siglas cruas do pf2etools ('PC1'). Nao tem grafia duplicada -- so nao ha entrada no AoN para canonizar contra. Resolver com mapa de siglas verificado, nunca por chute"
    prioridade: baixa

  - id: 39
    texto: "REGRA 17 FURA EM CONJURADOR PARCIAL -- decisao do Igor. A simulacao de 2.000 personagens de classe unica achou: Magus e Summoner param no rank 9 de slot (nao 10), entao `rank_efetivo = ceil(nivel/2)` da a eles +1 rank de elevacao mesmo PUROS, no nivel 19 e 20. A houserule vaza para o jogo padrao em 2 das 11 classes conjuradoras. A spec afirma 'Mago 20 puro nao muda porque o +2 nao tem para onde ir a partir do rank 10' -- verdade para conjurador pleno, falso para parcial. Opcoes: (a) capar a elevacao pelo max_rank nativo da classe, (b) aceitar como buff intencional a conjurador parcial, (c) tratar so quando ha multiclasse. Nao arbitrei"
    prioridade: alta

  - id: 40
    texto: "SUBCLASSE NAO ALTERA NADA (parcialmente resolvido). Levantado pelo Igor a partir do caso Cloistered/Warpriest: das 176 opcoes de sub-escolha (bloodline 18, patron 24, mystery 12, instinct 16, racket 6, doctrine 3, muse 5, arcane-school 23, cause 13, implement 10...), **175 nao tinham efeito estruturado** -- escolher subclasse nao mudava numero nenhum na ficha. O dado existe: 584 das 841 class-features do Foundry tem Rule Elements. converter_rule_elements.py converteu os 99 declarativos (ActiveEffectLike com path de rank, sem predicate). FALTA o grosso, que depende de reimplementar o interpretador do Foundry: 1.784 FlatModifier, 1.495 ItemAlteration, 1.113 GrantItem, 1.077 RollOption, 563 ChoiceSet, 337 Resistance. E o item que a spec chama de 'maior custo do projeto'"
    prioridade: alta
  - id: 41
    texto: "TRADICAO DE MAGIA POR SUBCLASSE nao e modelavel hoje. Sorcerer, Summoner e Witch tem `spellcasting.tradition` gravado como PROSA -- literalmente a string 'variavel (definida pela escolha de bloodline/eidolon/patron)'. A tradicao real vem da subclasse (Genie=arcane, Nymph=primal...) e esta so no texto ('Spell List Arcane'). Consequencia: o predicado `spellcasting_tradition` da spec nao funciona para 3 das 10 classes conjuradoras, e a ficha mostra a string descritiva no lugar da tradicao. Extrair do texto e viavel (padrao 'Spell List <tradicao>'), mas e derivacao de prosa -- decidir se entra"
    prioridade: alta

  # ==========================================================================
  # BLOCO 2 -- MODELAGEM. Depende da base re-emitida.
  # ==========================================================================
  - id: 2
    texto: "CONCLUIDO 2026-07-27. Grafo de progressao de dois niveis: classe -> feature -> sub-escolha. 62 class-features de segundo nivel ficam invisiveis hoje (teses e escolas do Mago, ordens Hellknight, ikons do Exemplar, gates do Kineticist, research fields do Alchemist)"
    prioridade: concluido
  - id: 3
    texto: "Linguagem de predicado precisa falar de SUBCLASSE, nao so de classe. A proficiencia de conjuracao do Clerigo depende da Doutrina (Cloistered chega a legendary no 19, Warpriest para em master). Fura a premissa da regra 3 das houserules. Tambem: nivel do companheiro e o class_level de quem o concedeu, nao o nivel de personagem"
    prioridade: alta
  - id: 22
    texto: "A mecanica de filiacao EXISTE mas nao esta estruturada: 305 registros (155 equipment, 134 feat, 13 weapon, 3 armor) tem linha 'Access' no texto citando organizacao/regiao/etnia como condicao de raridade uncommon, com requires:null. Mais 68 feats/archetypes com requires_texto tipo 'member of X'. Nenhuma chave do predicado sabe falar de filiacao. Solucao: ~20-25 stubs leves (id+nome, sem prosa) + termo novo no predicado. Principio zero: sugere, nunca bloqueia"
    prioridade: media
  - id: 4
    texto: "Separar indice e prosa no build final. Hoje o index tem 15,2 MB com texto embutido; o alvo medido e 0,53 MB de indice mais prosa sob demanda"
    prioridade: media

  # ==========================================================================
  # BLOCO 3 -- CONSTRUTOR E VALIDACAO
  # ==========================================================================
  - id: 7
    texto: "Rodar as simulacoes de balanceamento depois da base fechar DE VERDADE. Simulador e benchmark de 3.624 criaturas ja estao em docs/simulacoes/. O Igor pediu niveis 1-15, muitas combinacoes incluindo as pouco obvias (Monge/Clerigo), e nao so combate -- pericia, social, exploracao, como mestrar uma aventura padrao. Comparar HOUSE vs RAW vs RAW+Free Archetype"
    prioridade: media
  - id: 9
    texto: "O front: PWA client-side, offline, sem backend. Um componente de picker reusado em todo slot. O JSON e a ficha"
    prioridade: baixa
  - id: 10
    texto: "Importador do Pathbuilder tem que AVISAR o que se perde. Confirmado com o Igor: o eidolon existe no app deles e nao sobrevive ao export. Perda silenciosa e o pior tipo"
    prioridade: baixa
  - id: 8
    texto: "Re-rodar a simulacao de nivel 20 corrigindo o vies apontado pelo Fable: o dip gastava 12 acoes curando e era comparado com um Guerreiro que so ataca. Declarar gear, atributos e nivel dos alvos no documento"
    prioridade: baixa
  - id: 16
    texto: "Licenciamento antes de publicar: texto de regra sob OGL/ORC e reutilizavel com atribuicao, mas conteudo de Golarion (nomes de deuses, nacoes, organizacoes) e Product Identity e NAO e. Marcar esses registros para poderem ser excluidos de um build publico"
    prioridade: baixa
  - id: 19
    texto: "Cobertura medida em 5 dos 26 livros: Player Core, Player Core 2, War of Immortals e Ancestry Guide (1.377 nomes, 99,8% fora rituals) mais Treasure Vault (898 nomes, 100%). Os outros 21 livros nao foram testados"
    prioridade: baixa

  # ==========================================================================
  # CONCLUIDOS
  # ==========================================================================
  - id: 1
    texto: "INVALIDADO 2026-07-26 pela auditoria ampla. Dizia: 'base final 18.176 registros, prosa 100%, 597 pares fundidos, zero par nao unido'. Os tres numeros estavam errados -- prosa e 95% (metrica com denominador errado), e das 597 fusoes so 35% estavam certas. 'Zero par nao unido' media recall sem precisao: fundir tudo com tudo daria zero tambem. Ver itens 24 e 30"
    prioridade: concluido
  - id: 5
    texto: "CONCLUIDO 2026-07-26: os traits orfaos sao so 16, todos parametrizados -- resolvidos pelo mapa de familias em pipeline/normalizacao_traits.json"
    prioridade: concluido
  - id: 6
    texto: "CONCLUIDO 2026-07-26: 35 PDFs oficiais extraidos dos zips (1,7 GB em pipeline/dados_brutos/pdfs/, fora do git; os 1.027 mapas .webp ignorados por decisao do Igor). Cobertura auditada, tabelas de conjuracao recuperadas, ambientacao avaliada. ARMADILHA: varios sao scan puro sem camada de texto (War of Immortals, Monster Core, Treasure Vault, Menace Under Otari, Lost Omens.pdf) -- rodar pdffonts antes, zero fontes = scan"
    prioridade: concluido
  - id: 12
    texto: "CONCLUIDO 2026-07-26 com resultado negativo: a arbitragem contra PDF nao valida a precedencia, porque a PREMISSA e falsa -- as fontes digitais incorporam errata posterior a publicacao, entao o impresso nao e arbitro. Deu 63% geral e 50% nos dois campos de maior volume. Validar de verdade exigiria historico de errata, que nenhuma fonte expoe. Nao trocar a precedencia: sem saber quem erra, inverter so troca qual metade fica errada"
    prioridade: concluido
  - id: 15
    texto: "CONCLUIDO 2026-07-26: os capitulos de ambientacao dos Lost Omens sao flavor puro -- IGNORAR, por decisao do Igor. Verificado por amostragem: o conteudo mecanico daqueles capitulos ja esta na base. Nao criar kinds region/organization como container de texto. A mecanica que sobrou virou o item 22"
    prioridade: concluido
promoted: []
---
