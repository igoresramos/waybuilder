---
project: waybuilder
items:
  - id: 1
    texto: "CONCLUIDO 2026-07-26: pipeline rodado com as 7 familias. Base final 18.176 registros em 21 kinds, prosa 100%, 597 pares Legacy<->Remaster fundidos, zero par nao unido. Residuo: 6 registros sem license"
    prioridade: concluido
  - id: 2
    texto: "Grafo de progressao de dois niveis: classe -> feature -> sub-escolha. 62 class-features de segundo nivel ficam invisiveis hoje (teses e escolas do Mago, ordens Hellknight, ikons do Exemplar, gates do Kineticist, research fields do Alchemist)"
    prioridade: alta
  - id: 3
    texto: "Linguagem de predicado precisa falar de SUBCLASSE, nao so de classe. Achado na extracao de conjuracao: a proficiencia do Clerigo depende da Doutrina (Cloistered chega a legendary no 19, Warpriest para em master no 19). Fura a premissa da regra 3"
    prioridade: alta
  - id: 4
    texto: "Separar indice e prosa no build final. Hoje o index tem 8,8 MB com texto embutido; o alvo medido e 0,53 MB de indice mais prosa sob demanda"
    prioridade: media
  - id: 5
    texto: "CONCLUIDO 2026-07-26 pela auditoria ampla: os traits orfaos sao so 16, todos parametrizados -- resolvidos pelo mapa de familias em pipeline/normalizacao_traits.json"
    prioridade: concluido
  - id: 6
    texto: "Explorar os PDFs oficiais quando o Igor passar o caminho. Dois objetivos separados -- cobertura (o que existe la e nao entrou pelas 3 fontes) e ambientacao (texto de mundo que nenhuma fonte tem). Usar agentes, sao zips de ~2GB. Ferramenta ja conferida: pdftotext, pdfinfo, pypdf, unzip, 902 GB livres"
    prioridade: media
  - id: 7
    texto: "Rodar as simulacoes de balanceamento depois da base fechar. Simulador e benchmark de 3.624 criaturas ja estao em docs/simulacoes/. O Igor pediu niveis 1-15, muitas combinacoes incluindo as pouco obvias (Monge/Clerigo), e nao so combate -- pericia, social, exploracao, como mestrar uma aventura padrao"
    prioridade: media
  - id: 8
    texto: "Re-rodar a simulacao de nivel 20 corrigindo o vies apontado pelo Fable: o dip gastava 12 acoes curando e era comparado com um Guerreiro que so ataca. Declarar gear, atributos e nivel dos alvos no documento"
    prioridade: baixa
  - id: 9
    texto: "O front: PWA client-side, offline, sem backend. Um componente de picker reusado em todo slot. O JSON e a ficha"
    prioridade: baixa
  - id: 10
    texto: "Importador do Pathbuilder tem que AVISAR o que se perde. Confirmado com o Igor: o eidolon existe no app deles e nao sobrevive ao export. Perda silenciosa e o pior tipo"
    prioridade: baixa
  - id: 11
    texto: "BUG barato: aplicar normalizar_livro() antes de COMPARAR source em reconciliar.py. A funcao ja existe mas so roda depois; por isso boa parte dos 72 conflitos de source e falso -- e o foundry gravando 'Pathfinder <Livro>' contra '<Livro>' das outras duas fontes"
    prioridade: alta
  - id: 12
    texto: "A tabela de precedencia da spec NAO esta validada. Arbitragem contra PDF deu 63% geral e 50% nos dois campos de maior volume (traits = 88% dos conflitos, level = 3,8%). Nao trocar nada: em varios casos nenhuma fonte bate com o impresso. Validar de verdade exige historico de erratas, que nao temos -- o PDF impresso nao e arbitro, as fontes digitais incorporam errata posterior"
    prioridade: media
  - id: 13
    texto: "A regra de precedencia grants->foundry e letra morta: grants nunca gera conflito real no dataset, o merge adota silenciosamente o lado nao-vazio. Ou exercitar ou remover da spec"
    prioridade: baixa
  - id: 14
    texto: "Tabela numerica de slots de conjuracao: NENHUMA das 11 classes tem. Recuperadas do PDF: Animist (War of Immortals p.12-13, hibrido prepared divine + spontaneous pela apparition), Magus e Summoner (Secrets of Magic). Exemplar e Kineticist confirmados nao-conjuradores. Faltam as 8 do Player Core / Player Core 2"
    prioridade: alta
  - id: 15
    texto: "RESOLVIDO 2026-07-26: os capitulos de ambientacao dos Lost Omens sao flavor puro -- IGNORAR, por decisao do Igor ('se e apenas flavor e nada de mecanica, pode ignorar'). Verificado por amostragem: o conteudo mecanico daqueles capitulos ja esta na base. Nao criar kinds region/organization como container de texto"
    prioridade: concluido
  - id: 22
    texto: "A mecanica de filiacao EXISTE mas nao esta estruturada: 305 registros (155 equipment, 134 feat, 13 weapon, 3 armor) tem linha 'Access' no texto citando organizacao/regiao/etnia como condicao de raridade uncommon, com requires:null. Mais 68 feats/archetypes com requires_texto tipo 'member of X'. Nenhuma chave do predicado sabe falar de filiacao. Solucao: ~20-25 stubs leves (id+nome, sem prosa) para as organizacoes citadas como pre-requisito + termo novo no predicado. Lembrar do principio zero: sugere, nunca bloqueia"
    prioridade: media
  - id: 23
    texto: "Gaps de ingestao achados na verificacao dos Lost Omens: 4 wayfinders do PFS Guide e o feat 'Triggerbrand Salvo' nao estao na base"
    prioridade: baixa
  - id: 16
    texto: "Licenciamento antes de publicar: texto de regra sob OGL/ORC e reutilizavel com atribuicao, mas conteudo de Golarion dos Lost Omens (nomes de deuses, nacoes, organizacoes) e Product Identity e NAO e. Se a ambientacao entrar na base, marcar esses registros para poderem ser excluidos de um build publico"
    prioridade: baixa
  - id: 17
    texto: "FALTA UM KIND INTEIRO: ritual. Zero registros em 18.176, zero com o trait, e a palavra nao aparece uma vez sequer na spec do schema -- foi omissao de escopo, nao bug de extrator. 31 rituals confirmados ausentes (18 Player Core + 13 Player Core 2). E conteudo de jogador, nao bestiario. Precisa entrar na lista de kinds da spec e ganhar extrator"
    prioridade: alta
  - id: 18
    texto: "Tres ausencias pontuais confirmadas contra o PDF: 'Life-Saving Yowl' (feat de Catfolk nivel 17, Player Core 2) simplesmente nao existe na base; 'Cavern Kobold' e 'Spellscale Kobold' (Ancestry Guide) sao herancas legacy que ficaram sem alias na fusao Legacy<->Remaster"
    prioridade: media
  - id: 19
    texto: "Cobertura medida so em 4 dos 26 livros (1.377 nomes cruzados, 99,8% fora rituals). Treasure Vault segue SEM medicao -- e scan puro e o OCR foi abandonado por custo. Os outros 22 livros nao foram testados"
    prioridade: baixa
  - id: 20
    texto: "CORRIGIR A SPEC: traits sai da tabela de precedencia e vira UNIAO. Responde por 88% dos 2.299 conflitos e quase nenhum e divergencia real -- sao facetas complementares (72 casos: foundry lista trait de arma, aon lista trait de item magico), ancestria renomeada no remaster (31: foundry nephilim/naari vs aon tiefling/aasimar/ifrit -- a precedencia escolhe o nome LEGADO numa base remaster-first) e trait parametrizado (18: two-hand-d12 vira two-hand e perde o dado mecanico). Precisa de normalizacao de parametro e mapa legado->remaster"
    prioridade: alta
  - id: 21
    texto: "COLISAO DE IDENTIDADE: wb:<kind>/<slug> assume nome unico por kind e nao e. 16 suspeitas. Confirmado em wb:feat/death-from-above -- sao DOIS feats no War of Immortals (arquetipo nv8 e mitico nv16 p.128); o Foundry separa, o AoN indexa so o mitico, e a base fundiu numa quimera com nivel de um e nome/traits/texto do outro. wb:feat/reckless-abandon e igual (goblin vs barbaro nv16). Portao de qualidade proposto: traits categoricamente disjuntos depois de descontar as causas de merge = colisao, falha o build"
    prioridade: alta
  - id: 24
    texto: "CRITICO -- a fusao Legacy<->Remaster destruiu dado. fundir_renomeados.py decide por similaridade de PROSA e deletou 597 registros; 393/597 (65,8%) fundiram registros com level/price_cp/damage diferentes, e amostra de 60 contra o remaster_id do AoN confirmou so 21 (35%) como fusao correta. wb:equipment/aeon-stone engoliu 24 pedras distintas; 'Poi'->'Shield Bash'; 'Tonfa'->'Shuan Ji' (mesmo livro); 6 armas viraram 'Gaff'. REVERTER e refazer usando o remaster_id/legacy_id do AoN como chave, nao prosa. Prosa so como desempate, nunca como criterio"
    prioridade: alta
  - id: 25
    texto: "`mechanized` significa 4 coisas diferentes conforme o extrator que o escreveu: 12.742 registros (70,1%) tem true com grants vazio, e 370 tem false com grants cheio. O false se distribui por KIND inteiro, nao por registro -- ou seja, e propriedade do extrator, nao do dado. Definir o significado unico na spec e fazer todos obedecerem"
    prioridade: alta
  - id: 26
    texto: "Divergencia silenciada: 6 kinds (class-feature, background, heritage, familiar-ability, ancestry, class) tem 1.618 registros com 2+ fontes e ZERO conflitos registrados. Comprovadas 145 divergencias reais de source.book contra o Foundry, nenhuma anotada. Esses extratores nao implementam a deteccao de conflito -- o numero de 2.299 divergencias e piso, nao total"
    prioridade: alta
  - id: 27
    texto: "Buracos de cobertura medidos contra o censo do AoN: background -167 (33% do kind!), e dois kinds que a spec NUNCA listou -- `relic` (-116) e `language` (-85). Mesma classe de erro do ritual: omissao ao escrever a lista de kinds, nao falha de extrator"
    prioridade: alta
  - id: 28
    texto: "source.book sai com DUAS grafias para 26 obras, afetando 10.723 registros (59%), mais 160 com \\r\\n literal dentro do nome. Relacionado ao item 11 (normalizar_livro rodando tarde), mas maior: nao e so comparacao, e o valor emitido"
    prioridade: alta
  - id: 29
    texto: "Dos 7 portoes de qualidade da spec, so o 5 esta implementado. O portao 1 falharia (2.694 sem prov.text), o 3 falharia (111 registros com requires citando 61 ids inexistentes). E o portao 7 e TAUTOLOGICO: pergunta por nome duplicado depois de a duplicata ter sido fundida -- que e exatamente a fresta por onde o death-from-above passou. Reescrever o 7 para rodar ANTES da fusao"
    prioridade: alta
  - id: 30
    texto: "907 registros sem prosa (5,0%), nao os 100% reportados. A metrica de emitir_textos.py divide pelas referencias existentes, nao pela base -- registro sem referencia nenhuma nao entra no denominador e some da conta. Corrigir a metrica junto com o buraco"
    prioridade: media
  - id: 31
    texto: "22 registros so-pf2etools sao duplicatas de registros ja existentes (wb:armor/hide vs wb:armor/hide-armor). Explicam os 6 sem license, os 23 sem rarity e 16 dos sem prosa -- ou seja, o portao 5 estava detectando FALHA DE CASAMENTO, nao falta de licenca. O sintoma foi lido errado desde o inicio"
    prioridade: media
  - id: 32
    texto: "spell usa `rank` e nunca `level`, fora do envelope da spec -- qualquer filtro por nivel descarta as 1.639 magias silenciosamente. Mais 513 sem tradicoes, das quais 50 nao sao focus. Decidir: spell vira excecao documentada na spec, ou passa a emitir level tambem"
    prioridade: media
  - id: 33
    texto: "3.033 registros mono-fonte AoN com a materia-prima em disco e nao usada. O proprio pipeline ja gravou que faltam 42 nomes presentes no pf2etools, mais 6 deities, 38 familiar-abilities e 15 class-features do checkout do Foundry. Menor esforco por registro ganho de toda a lista"
    prioridade: media
  - id: 34
    texto: "Residuos menores da auditoria: wb:archetype/shared-archetype-feats e diretorio de organizacao do Foundry virado arquetipo em 14 feats; 1.440 licencas inferidas por heuristica sem marca no registro emitido; prov.class 'inferido de traits' em 409 das 817 class-features; 152 pontos de prov marcados 'desconhecida'; 65 traits:null contra 3.036 []; 256 feats sem feat_category (3 com valor bruto 'classfeature'); 1.506 sem source.page"
    prioridade: baixa
promoted: []
---
