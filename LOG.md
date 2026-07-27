---
project: waybuilder
---

# LOG -- Waybuilder

## 2026-07-27

### Sessao | 05:41-07:03 | perda de artefato, Animist recuperado, regras 17b/21/23 | igor + claude-code

**Perda de artefato, e o portao que faltava.** `dados_brutos/tabelas_conjuracao_pdf.json`
-- as tabelas de conjuracao lidas a olho de paginas renderizadas do War of
Immortals -- nunca entrou no git e sumiu. O `.gitignore` excluia `dados_brutos/`
alegando "reconstruivel pelos pins": verdade para o clone do Foundry e o dump do
AoN, falso para trabalho derivado a mao. O `TODO.md` seguia marcando o item 14
como CONCLUIDO e o relatorio seguia citando o caminho; nada reclamava.

Varredura de todo caminho citado em arquivo versionado: 42 caminhos, **3 nao
existiam**. Um era perda real, dois eram scripts de dump substituidos por
`dump_aon.py` (sem perda de dado, mas `companheiros.py` mandava rodar um script
inexistente -- bug real). Criados `pipeline/dados_derivados/` (versionado),
`artefatos_perdidos.json` (perda registrada com motivo, dano medido e decisao) e
o **portao 8**: caminho citado que some quebra o build; perda ja conhecida
aparece no relatorio sem bloquear.

**O Animist voltou, e de fonte melhor que o PDF.** A conclusao de 26/07 dizia
que "nem Foundry nem AoN materializam a tabela". Meia verdade: o item de classe
do Foundry so tem o flag `spellcasting: 1`, mas o doc de classe do AoN carrega a
tabela inteira em HTML no campo `markdown` -- e o extrator lia so `text`, a
projecao achatada. **O dado estava no cache que o proprio extrator ja baixava.**
Foi essa conclusao errada que mandou alguem ler o PDF a olho.

Parser em `pipeline/tabelas_conjuracao_aon.py`, validado contra as outras 10
conjuradoras: reproduz as 10 **celula a celula**, incluindo truques, contra o
pf2etools -- fonte independente. As 11 conjuradoras agora tem tabela completa.
Animist tem teto de rank 9 (terceira classe assim, com Magus e Summoner) mais um
slot de apparition rank 10 pela Supreme Incarnation.

**A conferencia registro a registro pagou.** `build.sh` rodado e comparado com o
commit anterior via `comparar_bases.py` novo: 19.738 -> 19.738, zero sumiram,
zero nasceram. O primeiro build alterou **dois** registros, e o segundo era
regressao minha: o focus pool do Cloistered Cleric zerou. Causa raiz maior que o
sintoma -- `load_foundry_feat` le de `dados_brutos/foundry/feats/`, que tem **0
arquivos contra 6.045 no clone**, porque `classes.py` so popula `classes/` e
`class-features/`. Falta silenciosa: devolve `None` e o campo vira `null`.
Corrigido com fallback para o clone. Build final: **1 registro alterado**, o
pretendido.

**Regra 17b -- teto do que cria criatura.** Escopo corrigido pelo Igor: Spirit
Link e Protector Tree saem (nao criam nada), `incarnate` entra -- 23 magias, zero
interseccao com `summon`, sao as invocacoes de rank 4 a 10. 37 no total, so por
trait, zero curadoria.

**Regra 21 virou invariante testado.** A simulacao (Opus, relatorio em
`docs/simulacoes/`) achou **50 de 204 pares** violando: no nivel 20 o dip ficava
em 0% da dedicacao gratuita. Decisao do Igor: *"o dip tem que obrigatoriamente
ser pelo menos tao forte quanto uma dedicacao no mesmo nivel de personagem"*.
Piso implementado, e a regra virou varredura EXAUSTIVA dos 204 pares em
`teste_motor.py`.

**Regra 23 -- exclusao mutua** entre nivel de classe X e dedicacao de X, nos dois
sentidos. Corrige divergencia que ja existia: um Mago 20 puro recebia
`atende: true` para Wizard Dedication, porque a proibicao mora numa regra geral
de arquetipo e nao no `requires` do feat.

**Ficha do companheiro, RAW puro**, com as regras citadas verbatim em
`docs/2026-07-27_atores.md`. Maturidade derivada dos feats, nao lida do
documento. A escolha nimble/savage virou **slot no vocabulario generico**
(`eixo/nivel/slot/escolhe/opcoes`), nao campo ad-hoc -- correcao de rumo do Igor
no meio da tarefa do agente.

**Medido a pedido do Igor:** 243 dos 6.044 feats (4%) abrem escolha, e a cadeia
de desbloqueio na base chega a **profundidade 4**. O encadeamento NAO esta no
formato do Foundry (opcoes de `ChoiceSet` sao valores ou consultas, nunca
ponteiro para item com escolha dentro) -- e grafo de dependencia, nao arvore
aninhada. Conclusao: slot tem de ser derivado do estado a cada escolha, nunca
arvore estatica.

**Duas afirmacoes minhas corrigidas no caminho**, registradas para nao voltarem:
o item 39 nao era defeito (heightened vem do nivel de personagem e independe do
teto de slot -- a assercao do validador e que estava errada, com 18 falsas
violacoes); e o argumento de que bloquear a dedicacao propria custaria 8 slots
estava inflado (o personagem pega qualquer uma das outras 26).

### Sessao | fonte limpa + fatia vertical 1 | igor + claude-code

**Item 37 -- pf2etools completo.** A terceira fonte vivia como 242 arquivos
baixados um a um por HTTP, adivinhando nomes; os 50 `.json.missing` eram chutes
de nome, nao conteudo faltando. Clone no pin (7d1ec43f), 382 arquivos em escopo.
Os 140 novos caem nos buracos: `baseitems.json`, `deities.json`, `traits.json`,
`archetypes.json`, `companionsfamiliars.json`, `optionalfeatures.json`.

Prova de reproducibilidade: 7 dos 8 extratores deram contagem **identica**. O
oitavo (rituais) achou defeito real -- nao existe pasta `rituals/` no Foundry,
ritual e magia com `system.ritual`; o extrator lia um recorte feito a mao numa
sessao antiga e, quando sumiu, 6 rituais exclusivos do Foundry sumiam calados.

Portao 5 zerado: os 3 orfaos nao eram falta de licenca -- o bloco de `source` do
extrator de equipamento so tinha ramo para AoN e Foundry, entao item exclusivo do
pf2etools saia com `source` vazio por construcao. Mais as 141 siglas de livro
extraidas de `js/parser.js` da propria fonte. Itens magicos ligados: +2.632.

**Fatia vertical 1 -- o motor monta ficha.** `motor/` implementa 11 das 22
regras, com 24 assercoes travando cada uma. Guerreiro 3 / Mago 2 sai completo.
A houserule aparece viva: Mago 2 num personagem 5 tem os slots de um Mago 2 e
conjura no rank 3 (+2 de elevacao); Mago 5 puro ganha elevacao zero.

O que a fatia descobriu, que era o motivo de faze-la:
- **a progressao misturava concessao com escolha** -- `wb:class/wizard` declarava
  49 features, sendo 15 concedidas; o resto sao as 23 escolas e 5 teses, opcao
  mutuamente exclusiva. Um motor ingenuo daria todas ao Mago 1. Fonte
  autoritativa: `system.items` da classe no Foundry
- **item 2 fechado**: as 28 categorias de sub-escolha do AoN viraram kind proprio
- **item 14 fechado**: a tabela de slots existia desde a primeira sessao e nunca
  entrou na base, por ser mapa e nao lista
- **portao 3: 80 -> 23** -- nao faltava conteudo, faltava vocabulario unificado

Base: 19.429 -> 19.738. Portoes 1, 2, 4 e 5 passam.

**Avaliacao pedida pelo Igor, registrada porque muda a prioridade:** o risco do
projeto saiu de "os dados estao errados" para "o modelo de efeito e fragmentado e
a regra nunca foi testada na mesa". O efeito mecanico mora em tres formatos
(classe usa `grants`, ancestria usa campos soltos, background usa outro
conjunto) e a spec define `grants` como a linguagem unica. E `class_level`, a
razao de o projeto existir, aparece em 79 de 19.738 registros.

## 2026-07-26

### Sessao | re-emissao do bloco 1 | igor + claude-code
Executado o bloco 1 inteiro do TODO (re-emissao da base). 11 itens fechados.

**Bloqueio achado antes de qualquer item, e nao registrado em lugar nenhum:**
7 dos 10 extratores e o `emitir_textos` apontavam para um clone do Foundry em
`/tmp/claude-.../scratchpad/pf2e-research`, de uma sessao ja encerrada. O clone
nao existia mais e **o pipeline nao rodava** -- re-executar o extrator de
equipamento dava 5.698 registros contra os 7.496 da base, mono-fonte, exit code
0. Pior: `carregar_aon()` cai para lista vazia em silencio quando o dump falta,
e os dumps do AoN para equipamento nunca tinham sido salvos. **A base de 18.176
registros nao era reproduzivel a partir do repo.**
- clone refeito no pin dentro de `dados_brutos/`, `buscar_fontes.sh` reconstroi
- `dump_aon.py` novo: indice `aon` inteiro em disco, 43.686 docs em 93
  categorias (bate com o censo remoto)
- os 7 caminhos hardcoded de `/tmp` foram substituidos

**Itens fechados:** 29 (os 7 portoes), 20 (traits como uniao), 24 (fusao por
`remaster_id`), 30 (metrica de prosa), 17 (rituais), 28 e 11 (grafia de livro),
27 (relic/language/background), 21 (colisoes desmembradas), 26 (divergencia
detectada), 25 (`mechanized` derivado), 31 (confirmado: era falha de casamento).

**Numeros:** base 18.176 -> **19.250 registros em 24 kinds**. Prosa de 95%
reportado (82,6% real) para **99,2%**. 586 registros que a fusao por prosa tinha
deletado foram recuperados. 318 irmaos criados no desmembramento. Portoes 1, 2 e
4 passam; 3, 5 e 7 seguem abertos com causa documentada.

**Duas correcoes a spec, verificadas contra as fontes:**
- `Death from Above`: a spec dizia "o Foundry separa os dois; o AoN indexa so o
  mitico". E o contrario nos dois lados. O defeito nunca foi fusao de
  duplicatas -- e **casamento ambiguo**, escolher 1 entre N em silencio
- `mechanized` passou a ser derivado (`== bool(grants)`); significava quatro
  coisas conforme o extrator

**Aberto para decisao do Igor:** 3 registros (`heavy-power-suit`,
`nine-ring-sword`, `wind-and-fire-wheel`) nao existem em fonte nenhuma em disco
-- vieram de consulta ao vivo ao pf2etools. Nao inventei licenca (item 35). E o
dump local do pf2etools esta incompleto, sem script de reconstrucao (item 37) --
`requires`, cuja precedencia e pf2etools, roda hoje com fonte parcial.


### Sessao | 18:40-21:30 | igor + claude-code
Exploracao dos PDFs oficiais e revisao ampla da base. **O pipeline nao foi
re-rodado**, entao o `index.json` esta byte a byte como estava no inicio -- mas
a sessao descobriu que ele ja continha dano. Esta sessao produziu diagnostico,
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
