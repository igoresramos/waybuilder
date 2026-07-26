---
project: waybuilder
items:
  - id: 1
    texto: "Rodar o pipeline completo quando os 3 extratores voltarem (equipamento, companheiros, referencia): reconciliar -> emitir_textos -> fundir_renomeados, validando os portoes. Base deve ir de ~9,9k para ~21k registros"
    prioridade: alta
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
promoted: []
---
