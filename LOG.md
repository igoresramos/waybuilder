---
project: waybuilder
---

# LOG -- Waybuilder

## 2026-07-26

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
