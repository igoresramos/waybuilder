---
project: waybuilder
items:
  # ==========================================================================
  # BLOCO 1 -- RE-EMISSAO DA BASE: **FECHADO em 2026-07-27**.
  # A base foi re-emitida sob a spec v2 e os 10 portoes de qualidade passam.
  # Evidencia por item em docs/2026-07-27_reemissao-base.md.
  # O que sobrou do bloco esta abaixo, com o motivo de ter sobrado.
  # ==========================================================================
  - id: 35
    texto: "Uniao de traits esta no lugar CERTO pelo caminho ERRADO: os extratores colapsam as tres fontes antes da reconciliacao, entao o reconciliador reconstroi a uniao a partir do proprio `conflitos` que o extrator gravou. Funciona (two-hand-d12 subiu de 2 para 10 registros, two-hand puro caiu de 19 para 2) mas depende de um efeito colateral. O certo e cada extrator chamar comum.uniao_traits() direto, e ai o campo `conflitos` de traits deixa de ser gerado na origem"
    prioridade: media
  - id: 36
    texto: "`prov: waybuilder` virou o novo `desconhecida` em parte dos campos: 70.010 de 339.238 valores (20,6%). Boa parte e legitima (id, kind, grants_completos -- calculados mesmo), mas `legado_de` (4.566), `remaster_de` (290), `requires_texto` (4.115) e `texto` (1.784) sao LEITURA de fonte rotulada como calculo do pipeline. Devem virar `aon~inferido:remaster_id` e a fonte real. Achado do review adversarial de 27/07"
    prioridade: media
  - id: 37
    texto: "Indice ainda carrega prosa crua: `texto` (1,88 MB, 10,2% dos bytes) e `heightened_so_prosa` dentro do index.json. gzip da 2,33 MB contra o orcamento de 0,53 MB da spec (4,4x). Tirando os dois campos: 1,76 MB. Isso e a metade do item 4 (separar indice e prosa) que da para fazer sem tocar no front"
    prioridade: media
  - id: 38
    texto: "`fundir_renomeados` sobrescreve `xref.legado_*` quando o alvo recebe 2+ legados: 107 alvos, 411 legados, so 1 id sobrevive por alvo -- 304 ids de fonte perdidos. O `historico[]` guarda nome e livro do legado, mas nao o id, entao o vinculo alvo->legado fica irrecuperavel a partir do alvo. Corrigir fazendo `legado_aon` virar lista ou guardando o xref dentro de cada entrada de historico"
    prioridade: media
  - id: 39
    texto: "Riscos de regressao sem portao, do review de 27/07: (a) `desmembrar` renomeia OS DOIS lados (know-it-all virou -archetype e -player-core; a spec manda um lado ficar com o slug base); (b) sufixo desambiguador por livro muda se a grafia canonica do livro mudar, ou seja o id nao e estavel entre builds; (c) extrator novo que escreva em saida/ sem entrar no ENTRADA de reconciliar.py nao entra na base e nenhum portao acusa"
    prioridade: media
  - id: 40
    texto: "Fusao legado/remaster: 67 alvos declarados pelo AoN nao existem na base (o AoN aponta para um doc que nenhum extrator emitiu). Levantar o que sao -- pode ser cobertura faltando, pode ser doc que o AoN indexa e nao e conteudo de jogador"
    prioridade: baixa
  - id: 41
    texto: "`e_artefato()` descarta registro sem livro/traits/level/grants -- hoje 1 caso, mas o criterio e largo e o descarte so aparece em print, nao no relatorio. Contradiz 'nada e descartado' sem deixar rastro"
    prioridade: baixa
  - id: 19
    texto: "Cobertura medida em 5 dos 26 livros: Player Core, Player Core 2, War of Immortals e Ancestry Guide (1.377 nomes, 99,8% fora rituals) mais Treasure Vault (898 nomes, 100%). Os outros 21 livros nao foram testados. Agora o portao 9 cobre por CATEGORIA do censo do AoN, que e gabarito melhor -- mas por livro segue sem teste"
    prioridade: baixa

  # ==========================================================================
  # BLOCO 2 -- MODELAGEM. A base esta fechada; e aqui que o projeto continua.
  # ==========================================================================
  - id: 2
    texto: "Grafo de progressao de dois niveis: classe -> feature -> sub-escolha. 62 class-features de segundo nivel ficam invisiveis hoje (teses e escolas do Mago, ordens Hellknight, ikons do Exemplar, gates do Kineticist, research fields do Alchemist). Parte do sintoma sumiu -- as referencias quebradas do portao 3 foram resolvidas -- mas a MODELAGEM continua sendo `classe -> feature` so"
    prioridade: alta
  - id: 3
    texto: "Linguagem de predicado precisa falar de SUBCLASSE, nao so de classe. A proficiencia de conjuracao do Clerigo depende da Doutrina (Cloistered chega a legendary no 19, Warpriest para em master). Fura a premissa da regra 3 das houserules. Tambem: nivel do companheiro e o class_level de quem o concedeu, nao o nivel de personagem. A simulacao de balanceamento de 27/07 so modelou Cloistered por causa disto"
    prioridade: alta
  - id: 22
    texto: "A mecanica de filiacao EXISTE mas nao esta estruturada: 305 registros (155 equipment, 134 feat, 13 weapon, 3 armor) tem linha 'Access' no texto citando organizacao/regiao/etnia como condicao de raridade uncommon, com requires:null. Mais 68 feats/archetypes com requires_texto tipo 'member of X'. Nenhuma chave do predicado sabe falar de filiacao. Solucao: ~20-25 stubs leves (id+nome, sem prosa) + termo novo no predicado. Principio zero: sugere, nunca bloqueia"
    prioridade: media
  - id: 42
    texto: "Predicado nao sabe falar de TRAIT DE HERANCA: dois feats (awakened-yaoguai-heritage, ascended-dragonet-heritage) exigem 'heranca versatil' e o parser virou isso em id inexistente. Estao declarados como ignorados em pipeline/aliases_referencias.json ate o termo existir"
    prioridade: baixa
  - id: 4
    texto: "Separar indice e prosa no build final. Hoje o index tem 20,9 MB com texto embutido; o alvo medido e 0,53 MB de indice mais prosa sob demanda. Ver item 37 para a metade barata"
    prioridade: media

  # ==========================================================================
  # BLOCO 3 -- CONSTRUTOR E VALIDACAO
  # ==========================================================================
  - id: 9
    texto: "O front: PWA client-side, offline, sem backend. Um componente de picker reusado em todo slot. O JSON e a ficha"
    prioridade: alta
  - id: 10
    texto: "Importador do Pathbuilder tem que AVISAR o que se perde. Confirmado com o Igor: o eidolon existe no app deles e nao sobrevive ao export. Perda silenciosa e o pior tipo"
    prioridade: baixa
  - id: 43
    texto: "Playtest dos dois pontos que a simulacao de 27/07 achou: (a) regra 17 (elevacao) desacopla rank de dano de rank de acerto e cria 2 pontos fora da curva em 160 configuracoes, todos em defensivo-forte + conjurador (Monge/Clerigo, GRUPO); (b) regra 21 tem fresta real -- dip de 1 nivel em classe de d6 PV perde PV que a dedicacao RAW_FA nao perde, em 14 de 63 comparacoes, concentradas nos niveis 3-5. Nenhum dos dois justifica mudar a regra sozinho; sao os candidatos numero 1 se o playtest achar problema"
    prioridade: media
  - id: 44
    texto: "O que a simulacao NAO respondeu e vale rodar depois: custo de jogar de healbot (a politica de acao simetrica removeu isso junto com o vies), atrito de recurso num dia inteiro de aventura, magia de controle/buff/invocacao, sinergia de festa de 4, e Warpriest (so Cloistered foi modelado -- depende do item 3)"
    prioridade: baixa
  - id: 16
    texto: "Licenciamento antes de publicar: texto de regra sob OGL/ORC e reutilizavel com atribuicao, mas conteudo de Golarion (nomes de deuses, nacoes, organizacoes) e Product Identity e NAO e. Marcar esses registros para poderem ser excluidos de um build publico. Hoje 2.013 registros tem `source.license_inferida: true` -- essa e a base do build publico e ela e derivada, nao lida"
    prioridade: baixa

  # ==========================================================================
  # CONCLUIDOS EM 2026-07-27 (re-emissao da base)
  # ==========================================================================
  - id: 24
    texto: "CONCLUIDO: a fusao Legacy<->Remaster foi refeita com o remaster_id/legacy_id do AoN. 734 pares declarados, 655 fundidos, 79 vetados por categoria diferente, NENHUM registro deletado (o absorvido fica com superseded_by). Amostra de 12 conferida contra a fonte: 12/12 corretas, contra 35% da v1. Poi, Tonfa, Kris, Kalis, Thorn Whip e Atlatl estao de volta com preco proprio; a familia Aeon Stone saiu de 1 para 38 registros"
    prioridade: concluido
  - id: 29
    texto: "CONCLUIDO: os 7 portoes viraram 10 e todos rodam com ordem declarada. O portao de duplicata roda ANTES da fusao; o 4 nao rebaixa mais a propria baseline; o 7 nao pode mais passar por acidente; o 8 ignora conflito de traits; o 9 varre as categorias do censo em vez de uma allow-list; o 10 (prosa) nasceu do review"
    prioridade: concluido
  - id: 21
    texto: "CONCLUIDO: 5 colisoes curadas em pipeline/colisoes_identidade.json (com o xref que identifica cada entidade) + detector generico por traits disjuntos + detector novo por salto de level >= 8, que achou o caso que os traits nao denunciam (Efficient Alchemy nv4 contra Efficient Alchemy (Paragon) nv20). O extrator tambem passou a recusar casamento por nome com salto de nivel (5 casos)"
    prioridade: concluido
  - id: 20
    texto: "CONCLUIDO (com ressalva no item 35): traits e uniao. two-hand-d12 subiu de 2 para 10 registros, two-hand puro caiu de 19 para 2, e o mapa de normalizacao ganhou grippli->tripkee (verificado pelos 4 heritages do Howl of the Wild)"
    prioridade: concluido
  - id: 28
    texto: "CONCLUIDO: source.book normalizado na ESCRITA (1.066 registros), grafia original preservada em source.book_raw, \\r\\n literal eliminado. Teste de invariante garante uma grafia por livro"
    prioridade: concluido
  - id: 11
    texto: "CONCLUIDO junto com o 28, e a comparacao passou a ser por chave normalizada dentro de comum.escolher()"
    prioridade: concluido
  - id: 17
    texto: "CONCLUIDO: ritual entrou no ENTRADA do reconciliador -- 151 registros contra 145 do censo (a base guarda tambem o legado marcado)"
    prioridade: concluido
  - id: 27
    texto: "CONCLUIDO: relic 122/122 e language 117/117 batem o censo exato; background subiu de 332 para 514 (a causa era .glob nao recursivo no pack do Foundry, que escondia os subdiretorios de adventure path e PFS)"
    prioridade: concluido
  - id: 26
    texto: "CONCLUIDO: os 6 kinds mudos agora registram divergencia (ancestry 25, background 225, class 2, heritage 170, familiar-ability 22) porque a escolha por precedencia virou funcao unica em pipeline/comum.py. `shield` continua com zero, mas por concordancia MEDIDA, nao por falta de instrumentacao"
    prioridade: concluido
  - id: 25
    texto: "CONCLUIDO: mechanized morreu. No lugar, grants_completos e requires_parseado com matriz por kind na spec (null = nao se aplica), aplicados nos 10 extratores"
    prioridade: concluido
  - id: 30
    texto: "CONCLUIDO: prosa em 99,1% da base (19.249/19.418) com o denominador certo -- a base inteira. Sem prosa: 168, todos em kind com isencao declarada e cobertos pelo portao 10. Zero chaves orfas"
    prioridade: concluido
  - id: 31
    texto: "CONCLUIDO: hide/leather/studded-leather casaram com a versao sufixada; heavy-power-suit NAO era duplicata (subCategory Heavy, bulk 3, exige modificacao de arquetipo) e teve a fonte completada; nine-ring-sword e wind-and-fire-wheel recusados e logados por falta de grounding, nao descartados em silencio"
    prioridade: concluido
  - id: 32
    texto: "CONCLUIDO: spell emite rank E level espelhados (1.667/1.667), com prov waybuilder~inferido:espelho-rank e invariante no portao 2. Das 50 tradicoes ausentes fora de focus, 48 fechadas por tradicao_de_classe e 5 por um bug real de precedencia (lista vazia do Foundry engolia o valor do AoN); sobrou 1 caso sem fonte nenhuma"
    prioridade: concluido
  - id: 33
    texto: "CONCLUIDO em parte: deity subiu para 490 (6 do Foundry que faltavam + 3 achados no caminho), familiar-ability de 133 para 171, heritage de 326 para 346 (herancas legadas so-AoN, que a enumeracao pelo Foundry perdia). O pf2etools_crosscheck de trait/deity/skill NAO foi consumido: o `source` de la e sigla de livro sem mapa para titulo, e sem titulo a licenca fica vazia e quebra o portao 5"
    prioridade: concluido
  - id: 34
    texto: "CONCLUIDO: shared-archetype-feats era pasta organizacional virando referencia (14 feats) -- filtrada; feat_category derivada para os 378 sem categoria e classfeature normalizado; traits null zerado; licenca inferida agora marcada no proprio registro (source.license_inferida); prov desconhecida eliminado do vocabulario"
    prioridade: concluido
  - id: 13
    texto: "CONCLUIDO com resultado negativo documentado: a precedencia de grants nunca e exercitada porque so o Foundry produz o campo. Nao e regra morta, e propriedade das fontes -- ficou escrito na spec para nao voltar como 'remover'"
    prioridade: concluido
  - id: 18
    texto: "CONCLUIDO: 'Life-Saving Yowl' NAO existe em fonte nenhuma nem no PDF -- o feat e Caterwaul (FEAT 13, Catfolk, Player Core 2) e ja estava na base. Cavern Kobold e Spellscale Kobold eram ausencia real (heritage legado do APG que o Foundry nao carrega) e entraram. Ver docs/2026-07-27_ausencias-pontuais.md"
    prioridade: concluido
  - id: 23
    texto: "CONCLUIDO com limite declarado: Triggerbrand Salvo esta na base; os 4 wayfinders do PFS Guide nao existem no AoN nem no Foundry -- e gap das fontes, nao do pipeline"
    prioridade: concluido
  - id: 14
    texto: "CONCLUIDO: as 11 classes conjuradoras tem tabela numerica de slots, com livro e pagina. As 8 que faltavam saiam do Player Core/PC2/Dark Archive por pdftotext (nenhum era scan). O extrator passou a consumir a tabela do PDF como fonte vencedora, e registrou o unico conflito real: o Oracle do pf2etools e a versao legada (2/3) contra a remaster do PDF (3/4), confirmada pelo texto do Foundry"
    prioridade: concluido
  - id: 7
    texto: "CONCLUIDO: matriz rodada nos niveis 1-15, 12 classes puras + 10 combinacoes (inclusive Monge/Clerigo, Barbaro/Mago, Ladino/Druida), HOUSE vs RAW vs RAW+Free Archetype, combate SOLO e GRUPO mais os 8 pilares de nao-combate. Relatorio em docs/simulacoes/2026-07-27_balanceamento.md; achados viraram os itens 43 e 44"
    prioridade: concluido
  - id: 8
    texto: "CONCLUIDO: o vies do nivel 20 foi corrigido na raiz -- politica de acao simetrica (ninguem cura, ninguem buffa, todo mundo maximiza dano) e consumo real de slot rodada a rodada. Gear, atributos e nivel/tipo dos alvos estao declarados no relatorio"
    prioridade: concluido
  - id: 1
    texto: "INVALIDADO 2026-07-26 pela auditoria ampla. Dizia: 'base final 18.176 registros, prosa 100%, 597 pares fundidos, zero par nao unido'. Os tres numeros estavam errados"
    prioridade: concluido
  - id: 5
    texto: "CONCLUIDO 2026-07-26: os traits orfaos sao so 16, todos parametrizados -- resolvidos pelo mapa de familias em pipeline/normalizacao_traits.json"
    prioridade: concluido
  - id: 6
    texto: "CONCLUIDO 2026-07-26: 35 PDFs oficiais extraidos dos zips. ARMADILHA: varios sao scan puro sem camada de texto -- rodar pdffonts antes, zero fontes = scan"
    prioridade: concluido
  - id: 12
    texto: "CONCLUIDO 2026-07-26 com resultado negativo: a arbitragem contra PDF nao valida a precedencia, porque as fontes digitais incorporam errata posterior a publicacao. Nao trocar a precedencia sem historico de errata"
    prioridade: concluido
  - id: 15
    texto: "CONCLUIDO 2026-07-26: os capitulos de ambientacao dos Lost Omens sao flavor puro -- IGNORAR. A mecanica que sobrou virou o item 22"
    prioridade: concluido
promoted: []
---
