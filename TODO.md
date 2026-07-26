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
    texto: "Repescar traits orfaos: quando o extrator de referencia voltar, cruzar os traits citados pelos ~10k registros contra os extraidos. Orfao e erro de normalizacao em algum extrator"
    prioridade: media
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
    texto: "Ambientacao dos Lost Omens (DECISAO DO IGOR PENDENTE): proposta e dois kinds novos, region e organization, mais append de recorte regional na prosa de ancestry/deity ja existente. A base ja tem a descricao basica de ancestria e divindade; falta a camada regional (subculturas como 'Alijae elves', pratica local de divindade, organizacoes filiaveis). ~350-400 paginas novas. Melhor retorno: Mwangi Expanse, Impossible Lands, Society Guide"
    prioridade: media
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
promoted: []
---
