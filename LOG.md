---
project: waybuilder
---

# LOG -- Waybuilder

## 2026-07-26

### Sessao | 18:40-21:15 | igor + claude-code
Exploracao dos PDFs oficiais e revisao ampla da base. **Nada foi reprocessado --
a base de 18.176 registros segue intacta**; esta sessao produziu diagnostico,
correcao de spec e um extrator novo.

- **35 PDFs oficiais** extraidos dos zips do Downloads (1,7 GB, fora do git).
  Os 1.027 mapas `.webp` foram ignorados por decisao do Igor
- **8 agentes despachados**, a maioria em paralelo: tabelas de conjuracao,
  arbitragem de divergencias, ambientacao, cobertura, mecanica dos Lost Omens,
  normalizacao de traits, colisoes de identidade, extrator de rituais
- **Achado 1 -- `traits` nao e campo de precedencia, e de uniao.** Responde por
  88% dos 2.299 conflitos e quase nenhum era divergencia: 72 facetas
  complementares, 31 ancestria renomeada no remaster (com a precedencia
  escolhendo o nome LEGADO numa base remaster-first), 18 granularidade
  (`two-hand-d12` virando `two-hand`, perdendo o dado de dano). Spec corrigida
- **Achado 2 -- `wb:<kind>/<slug>` assume nome unico por kind, e nao e.**
  5 colisoes confirmadas contra AoN e Foundry (`death-from-above` sao dois
  feats distintos fundidos numa quimera). Detector melhor achado pelo agente:
  registro-irmao com sufixo e `xref` incompleto -- 59 candidatos, com falso
  positivo conhecido nos `-greater`/`-major` de item
- **Achado 3 -- faltava o kind `ritual` inteiro.** Zero em 18.176, e a palavra
  nao aparecia na spec: omissao de escopo, nao falha de extrator. Extrator
  escrito, **151 rituais** (a estimativa de 31 era so dos dois Player Core)
- **Achado 4 -- a tabela de slots de conjuracao nao existe para classe nenhuma.**
  Nao era buraco do Animist. Animist, Magus e Summoner recuperados do PDF;
  Exemplar e Kineticist confirmados nao-conjuradores
- **Arbitragem contra PDF: premissa invalida.** Montei um teste tratando o
  impresso como arbitro; deu 63% e o defeito foi meu -- as fontes digitais
  incorporam errata posterior a publicacao, entao o teste mediu concordancia
  com o impresso, nao acerto
- **Lost Omens: ambientacao ignorada** por decisao do Igor (e flavor puro, e o
  conteudo mecanico daqueles capitulos ja esta na base). Mas sobrou mecanica
  real nao estruturada: 305 registros com linha `Access` citando organizacao ou
  regiao e `requires` vazio
- **Cobertura auditada**: Treasure Vault 898 nomes / 100%; Player Core, Player
  Core 2, War of Immortals e Ancestry Guide 1.377 nomes / 99,8% fora rituals
- **`pipeline/normalizacao_traits.json`**: 17 renomeados, 9 removidos sem
  sucessor, 18 familias parametrizadas, cada entrada com `prov` citando pagina.
  Corrigiu dois erros meus que ja estavam na spec -- `oread`/`sylph`/`undine`
  nao viraram `naari` (so `ifrit`), e `illusion` sobreviveu ao remaster
- Nota de wiki criada: `merge-n-fontes-precedencia-vs-uniao.md`
- **A auditoria ampla voltou no fim e mudou o estado do projeto.** 13 achados;
  o critico e que a **fusao Legacy<->Remaster destruiu dado**: decide por
  similaridade de prosa, deletou 597 registros e so 35% das fusoes estavam
  certas. `wb:equipment/aeon-stone` engoliu 24 pedras distintas. Tambem
  derrubou dois numeros que eu vinha reportando: prosa e **95%, nao 100%**
  (907 sem prosa -- a metrica dividia pelo subconjunto errado), e das 2.299
  divergencias, 6 kinds simplesmente **nao detectam conflito**, entao o numero
  e piso e nao total. Dos 7 portoes de qualidade, so 1 esta implementado, e o
  portao 7 e tautologico -- pergunta por duplicata depois de a fusao ja ter
  acontecido
- **A base NAO esta fechada.** Precisa de re-emissao antes de qualquer trabalho
  de construtor. Detalhe nos itens 24-34 do TODO

### Evento | igor + claude-code
- Projeto criado via /tartarus:novo

### Sessao | igor + claude-code
- Brainstorming completo das regras caseiras de multiclasse -- 21 regras fechadas
- Pesquisa em 4 agentes paralelos: Foundry pf2e (Sonnet), pf2etools (Sonnet),
  Pathbuilder 2e (Sonnet), review adversarial do design (Fable)
- Endpoint Elasticsearch do Archives of Nethys validado e usado como fonte de
  verificacao ao longo da sessao (43.686 docs, indice `aon`)
- Dataset medido: 29.236 registros relevantes -- indice 0,53 MB gzip,
  prosa 3,6 MB gzip. Confirma arquitetura client-side sem backend
- Simulacoes de Monte Carlo (200k iteracoes) para calibrar a regra de elevacao
  de magia. Derrubaram duas propostas minhas e fecharam em "sem teto"
- Decidido: base e construtor sao um projeto so, construidos em fatias
  verticais. Fatia 1 = Guerreiro + Mago, niveis 1-5

### Evento | igor
- Projeto renomeado de `nethys` para `waybuilder` -- piada com o Pathbuilder 2e,
  e eco do Wayfinder, a bussola da Pathfinder Society

### Sessao | igor + claude-code
- Spec `2026-07-26-schema-base.md` aprovada -- contrato unico de envelope,
  `prov`, `conflitos`, linguagem de predicado e efeito
- Primeiro extrator do pipeline escrito e rodado: `pipeline/extratores/ancestrias.py`
  (stdlib-only, `extrair() -> list[dict]`), cobrindo ancestry + heritage + background
- 708 registros emitidos em `pipeline/saida/ancestrias.json` (50 ancestrias,
  326 heranças, 332 backgrounds), enumerados a partir do Foundry pf2e
  (commit `87f9e5028baaa10b70fdc766260b7886def17e04`), enriquecidos via dump
  local do AoN (94/436/612 docs) e cross-check com pf2etools
- Portoes de qualidade do schema verificados manualmente: 0 ids fora do
  padrao, 0 duplicados, 0 campo preenchido sem `prov`, 0 sem `license`,
  0 referencia orfa heritage<->ancestry
- Mapa Legacy->Remaster calculado do conjunto AoN inteiro: 4 ancestrias e 12
  heranças renomeadas via `remaster_id`/`legacy_id` (Gnoll->Kholo, Grippli->
  Tripkee, Half-Elf->Aiuvarin, Half-Orc->Dromaar); 9 ancestrias e 7 heranças
  legado sem substituto (Ifrit/Oread/Suli/Sylph/Undine/Beastkin/Aphorite da
  Ancestry Guide, Ardande/Talos ja remaster mas sem legado, Aasimar/Tiefling
  sem ponte formal no AoN -- fundiram em Nephilim (Player Core) sem
  `remaster_id`, confirmado por leitura direta do texto); 97 backgrounds
  legado sem substituto (maioria player's guide de AP encerrada)
- Achado: 19/50 ancestrias e 121/326 heranças no Foundry ainda sao Legacy/OGL
  (nunca remasterizadas oficialmente -- Android, Anadi, Kitsune, Sprite,
  Strix, Skeleton, etc.)
- Relatorio completo em `pipeline/relatorios/ancestrias.md`

### Sessao | ~14:30-18:30 (estimado) | igor + claude-code
- Projeto criado, renomeado `nethys` -> `waybuilder`, e escopo colapsado em um
  projeto so (base + construtor), construido em fatias verticais
- **3 specs escritas e aprovadas**: as 22 regras caseiras de multiclasse, o
  schema da base canonica, e o schema do documento de personagem
- **Review adversarial em Fable duas vezes.** O primeiro demoliu uma regra que o
  Igor nunca propos -- erro meu de transcricao. O segundo, sobre a spec real,
  achou 7 defeitos legitimos, todos endereçados
- **Base canonica montada**: 6 extratores em paralelo (classes, feats, magias,
  ancestrias, conjuracao, e mais 3 rodando), reconciliacao, emissao de prosa e
  fusao de renomeados. ~9,9k registros com prosa em 100% e portoes passando
- Simulacoes de Monte Carlo (200k iteracoes) calibraram a regra de elevacao de
  magia; benchmark de 3.624 criaturas do AoN extraido e guardado
- **Principio zero definido pelo Igor**: isto e um construtor de personagem, nao
  um sistema de jogo. `requires` sugere, nunca bloqueia
- README.md criado como ponto de retomada para sessoes futuras
- Encerrada com 3 extratores ainda rodando (equipamento, companheiros,
  referencia) -- base deve chegar a ~21k registros
