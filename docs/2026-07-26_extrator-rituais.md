# Extrator de rituais (kind=ritual)

Data: 2026-07-26
Entrega: `pipeline/extratores/rituais.py` -> `pipeline/saida/rituais.json`

## Resumo

**151 rituais extraidos**, zero antes desta extracao (a base tinha 18.176 registros
em 21 kinds e nenhum ritual -- omissao ao escrever a lista de kinds da spec, nao
falha de extrator).

| Fonte | Docs brutos | Conceitos unicos usados |
|---|---:|---:|
| Foundry (`packs/pf2e/spells/rituals/`, commit `87f9e50...`) | 150 | 150 |
| AoN (`category=ritual`, dump Elasticsearch) | 201 | 145 (pos-dedupe legado/remaster) |
| pf2etools | 0 | indisponivel (ver secao 2) |

Uniao dos dois conjuntos por nome normalizado = **151** rituais (150 do Foundry
+ 1 exclusivo da AoN que o Foundry nao tem: *Rite of the Blood Crown*, de
*Crown of the Kobold King*).

- 144 rituais casados nas duas fontes (Foundry + AoN)
- 6 so no Foundry (Adventure Path/PFS scenario que a AoN nao indexa em
  `category=ritual`): *Anima Invocation (Modified)*, *Aspirational State*,
  *Create Mycoguardian*, *Destroy Mindscape*, *Rite of Cleansing Flame*,
  *Unfettered Mark*
- 1 so na AoN: *Rite of the Blood Crown*

## 1. Por que a estrutura de loop e diferente de `magias.py`

`magias.py` usa a AoN como fonte que dirige a iteracao (loop externo), porque
la a AoN e superset do Foundry (todo spell do Foundry tem par na AoN). Em
rituais e o **inverso parcial**: o Foundry tem 150 conceitos unicos contra 145
da AoN pos-dedupe -- 6 rituais de modulos/PFS que a AoN so indexa como pagina
de aventura, nao em `category=ritual`.

Se este extrator seguisse o padrao de `magias.py` (loop pela AoN, Foundry so
como lookup), os 6 rituais Foundry-only sumiriam da base -- contra o principio
"nada e descartado" da spec. Por isso `extrair()` itera a **uniao dos nomes
normalizados** das duas fontes, casando cada uma quando existe.

## 2. pf2etools indisponivel

`pipeline/dados_brutos/pf2etools/` tem `spells-*.json` (203 arquivos) mas
nenhum contem rituais -- nem como entrada dentro dos arquivos de spell, nem
como arquivo `rituals-*.json` separado. Nao foi baixado nesta rodada (o
snapshot de pf2etools no repo e datado e nao inclui a categoria).

Consequencia direta na precedencia: a spec pede `level -> foundry, conferido
contra pf2etools`. Sem pf2etools, o cross-check caiu para **foundry vs aon**
(as duas fontes independentes disponiveis) -- mesmo espirito da regra ("duas
fontes independentes, divergencia e bug"), documentado em `conflitos` quando
acontece. Zero divergencias de `level` entre foundry e aon nos 144 casados.

Se pf2etools for baixado depois pra rituais, o extrator precisa de um terceiro
cross-check; nao foi adicionado aqui por nao haver dado pra testar contra.

## 3. Campos proprios de ritual

Empacotados num bloco `"ritual"` (nao poluindo o envelope, por pedido) com
nomes em ingles -- **decisao deliberada**: sao os termos literais do stat
block de PF2e (`Cast`, `Cost`, `Secondary Casters`, `Primary Check`,
`Secondary Checks`), diferente dos campos compartilhados com magia
(`acoes`/`alcance`/`area`/`duracao`/`defesa`) que ficam em portugues por
convencao ja estabelecida em `magias.py`.

```json
"ritual": {
  "cast": "1 day",
  "cost": "rare oils, see Creature Creation Rituals",
  "secondary_casters": 1,
  "secondary_casters_note": null,
  "primary_check": "Arcana (expert)",
  "secondary_checks": "Crafting",
  "requirements": null,
  "results": {
    "critical_success": "...",
    "success": "...",
    "failure": "...",
    "critical_failure": "..."
  }
}
```

- **`cast`** -- tempo de conjuracao. Duplicado em `acoes` (top-level, mesmo
  campo que `magias.py` usa pra spell) porque e o mesmo dado fisico
  (`system.time.value` do Foundry) e faz sentido em ambos os lugares:
  `acoes` mantem paridade com o campo de spell pra quem consome so o
  envelope generico; `ritual.cast` da nome de dominio ao mesmo valor dentro
  do bloco proprio.
- **`cost`** -- material consumido, string livre (varia demais pra
  estruturar: "rare oils", "20 gp x nivel do alvo", "blood sacrifice (see
  below)"). Foundry (`system.cost.value`) vence quando existe; AoN
  (`cost`/`cost_markdown`) como fallback.
- **`secondary_casters`** -- inteiro, quantos ajudantes o ritual pede. **Achado
  de qualidade**: o Foundry usa `0` tambem como placeholder pra "quantidade
  variavel ou qualificada" -- nao so pra "nenhum ajudante". Evidencia: nos 168
  pares Foundry+AoN comparaveis, 13 divergiam, e **as 13 tinham `foundry=0`**
  contra um numero real na AoN (`up to 5`, `4 or more`, `1 to 9`, etc.); nenhum
  caso teve `foundry=0` confirmado por um `aon=0` correspondente. Ao mesmo
  tempo, `0` genuino existe de verdade: os quatro rituais de "Pact"
  (`Daemonic/Demonic/Diabolic/Div Pact`) sao solo -- voce barganha sozinho com
  o ser convocado, sem ajudantes humanos, e la o Foundry tambem diz `0` mas
  sem nenhuma AoN pra contestar.
  Regra aplicada: **foundry vence exceto quando vale `0` E a AoN tem um numero
  diferente** -- nesse caso cai pro numero da AoN, registrado em `conflitos`
  (`campo: "ritual.secondary_casters"`). Quando `foundry=0` e a AoN nao tem
  nada pra contestar, o `0` fica (evidencia insuficiente pra descartar, e ha
  caso confirmado de zero legitimo). 11 registros tiveram esse conflito
  resolvido a favor da AoN; ver a lista completa no proprio `rituais.json`
  (campo `conflitos`).
- **`secondary_casters_note`** -- texto residual da AoN quando o numero vem
  com qualificador (`"1, must be the ritual's target"`, `"up to 5"`, `"3 or
  more"`). Sem equivalente no Foundry (que so guarda o inteiro).
- **`primary_check`** / **`secondary_checks`** -- string livre com a(s)
  pericia(s) e rank minimo (ex: `"Arcana (master) or Occultism (master)"`).
  Nao foi estruturado em lista de opcoes porque o formato varia demais
  ("Nature if target is druid, Religion otherwise", "whichever isn't used pro
  primary") -- estruturar aqui seria inventar semantica que nem a fonte
  formaliza.
- **`requirements`** -- prosa rara (so 4 dos 151 rituais: *Community Repair*,
  *Divine Keystone*, *Planar Displacement*, *Ravenous Reanimation*), do campo
  `system.requirements` do Foundry (ex: "You must be an evil dragon"). **Nao
  foi mapeado pro `requires` do envelope** -- `requires` e a linguagem de
  predicado formal da spec (`all`/`any`/`has`/`trait`/...), e esses 4 textos
  sao prosa livre que nao formaliza de forma confiavel sem inventar semantica
  (ex: "cornerstone from the structure... used as a locus" nao vira predicado
  nenhum). Ficou como campo proprio de texto.
- **`results`** -- texto de cada grau de sucesso (Critical
  Success/Success/Failure/Critical Failure), parseado do HTML de descricao do
  Foundry (`<strong>Rotulo</strong>` como marcador) via `parse_degree_of_success`.
  Quando o Foundry tem descricao vazia (stub) mas a AoN tem a prosa completa em
  texto plano, cai pro fallback `parse_degree_of_success_plain` (mesma logica,
  ancorada no separador `---` que a AoN usa entre stat block e prosa, pra nao
  casar "Success"/"Failure" soltos em outro lugar do texto). Cobertura: **150 de
  151** com os 4 graus parseados. O unico sem (*Primal Call*) e estrutural, nao
  falha de parser: o ritual so diz "functions as [Planar Servitor] except...",
  sem secao de graus propria.

## 4. `mechanized` sempre `false`

Nao ligado a presenca de dado do Foundry (144/151 tem match mecanico rico:
tempo, custo, pericias). Ritual nao tem `grants` -- nao ha nada que o builder
calcule automaticamente pra ficha de personagem, o resultado sempre depende de
rolagem e arbitragem de mesa. Isso bate com o principio da spec ("mechanized:
false nao e lacuna, e caso normal") e evita a falsa impressao de que o
builder algum dia vai resolver um ritual sozinho.

## 5. `traits`: uniao, nao precedencia (regra nova aplicada do zero)

Este e o primeiro extrator escrito depois da regra "traits e uniao" entrar na
spec, e nasce obedecendo -- com um ajuste no meio do trabalho: a spec e o
arquivo `pipeline/normalizacao_traits.json` foram atualizados por outra sessao
enquanto este extrator estava sendo escrito (a versao 1 do mapa legado tinha
`oread/sylph/undine -> naari`, corrigida depois pra so `ifrit -> naari`). O
extrator foi ajustado pra consumir o arquivo compartilhado em vez de manter
mapa proprio hardcoded -- ver `_load_legacy_to_remaster_traits()`.

1. **Mapa legado -> remaster**, carregado de `pipeline/normalizacao_traits.json`
   (`renomeados`, 17 entradas com prov citando fonte/pagina cada uma) -- **nao
   hardcoded no extrator**. Disparou em **7 dos 151 rituais**: `positive ->
   vitality` (*Halt Death*, *Mother's Blessing*, *Plant Growth*), `evil ->
   unholy` (*Form of the Sandpoint Devil*, *Ravenous Reanimation*), `negative
   -> void` (*Blight*, *Void Harvest*). O termo legado fica em `aliases_traits`
   de cada um desses 7 registros.
2. **Absorcao por granularidade** (trait parametrizado absorve o base, ex.
   `two-hand-d12` absorve `two-hand`) -- implementado como regex generica
   (`_absorb_granularity`, cobre todo sufixo `-d\d+`/`-\d+`/`-aim-d\d+`, igual
   o texto da spec). Conferido contra a lista explicita de familias
   parametrizadas em `normalizacao_traits.json` (`two-hand`, `fatal`,
   `fatal-aim`, `deadly`, `volley`, `thrown`, etc.) -- todas cobertas pelo
   padrao generico, sem precisar de lista hardcoded. Sem disparo nos dados de
   ritual (trait parametrizado e coisa de arma/item, ritual nao carrega).
3. Uniao alfabetica do que sobra.

**Filtro adicional que magias.py nao tem**: a AoN mistura raridade (`Rare`,
`Uncommon`) dentro do proprio campo `trait`, junto dos traits de verdade.
`magias.py` herda esse ruido sem filtrar (nao e problema meu corrigir la).
Aqui, `merge_traits` remove `{common, uncommon, rare, unique}` antes da uniao
-- senao **toda** entrada com rarity != common ganharia "uncommon"/"rare" como
trait fantasma (teria acontecido em ~140+ dos 151 registros).

Resultado: **48 dos 144 rituais casados** (Foundry + AoN) tinham trait-sets
diferentes entre as duas fontes -- na maioria, a AoN ainda carrega o trait de
escola de magia legado (`necromancy`, `transmutation`, `evocation`,
`abjuration`, `conjuration`) que o remaster removeu do Foundry. Esses 5 termos
estao listados em `normalizacao_traits.json` -> `removidos_sem_sucessor`
(9 traits de escola/alinhamento sem substituto no remaster) -- **mantidos na
uniao** (nao filtrados): a AoN legado ainda descreve uma faceta real do
conceito, e a propria existencia dessa lista no arquivo compartilhado existe
pra essas divergencias especificas NAO dispararem o portao de qualidade 6
("suspeita de colisao de identidade") por engano -- ja estao documentadas e
explicadas, nao sao sinal de fusao de entidades diferentes. Com precedencia
(qualquer uma das duas fontes vencendo sozinha) esses traits teriam sumido ou
duplicado incorretamente; com uniao, sobrevivem os dois. `prov.traits`
registra quais fontes contribuiram por registro (`["foundry"]`, `["aon"]` ou
`["foundry", "aon"]`).

43 rituais (28%) ficam sem nenhum trait (alem da raridade, que e campo
separado) -- normal: muitos rituais remaster nao tem trait de escola nem
outro trait descritivo, so `Uncommon`/`Rare`/`Common`.

## 6. Cobertura de licenca, remaster e livros

- **150/151** com `source.license` preenchido (so o Foundry fornece licenca,
  igual `magias.py`). O unico sem: **Rite of the Blood Crown** (so-AoN, de
  *Crown of the Kobold King*, sem par no Foundry pra dar a licenca).
- `source.remaster=true`: 103 (68%) / `false`: 48 (32%).
- 51 livros distintos, do Player Core (19 rituais) a modulos/PFS avulsos
  (maioria com 1 ritual so). Nao ha concentracao anomala.

## 7. Achado de dado bruto corrigido na extracao

Dois rituais (*Ash-Strewn Ending*, *Footholds and Foothills*) tinham
`source.book` vindo da AoN com `\r\n` colado no fim do titulo
(`"Pathfinder #218: Titanbane\r\n"`). Corrigido com `.strip()` no ponto de
atribuicao -- artefato de scrape da propria AoN, nao do extrator.

## 8. `level` (rank do ritual)

Chamado de `level` (nao `rank` como `magias.py` faz pra spell) **de proposito**:
o envelope da spec usa literalmente `level`, e `reconciliar.py` (tabela
`PRECEDENCIA` e o filtro `e_artefato`) ja espera esse nome. `magias.py` usa
`rank` -- decisao antiga daquele extrator, nao mexida aqui, mas este extrator
novo segue o nome do contrato pra nao quebrar os portoes de qualidade quando
`rituais.json` entrar em `ENTRADA` de `reconciliar.py` (nao adicionado -- fora
do escopo pedido).

Distribuicao por nivel: 1(9) 2(20) 3(23) 4(18) 5(26) 6(19) 7(10) 8(11) 9(9) 10(6).

## 9. O que ficou pendente / sem resolver

- **pf2etools**: sem dado pra rituais no snapshot local (secao 2). Cross-check
  de `level` roda so foundry-vs-aon.
- **`requires` formal**: os 4 `requirements` em prosa (secao 3) nao viraram
  predicado -- ficaram como texto livre no bloco `ritual`.
- **`rituais.json` nao esta em `ENTRADA` de `pipeline/reconciliar.py`** --
  por instrucao explicita de nao rodar nem mexer no reconciliador. Precisa
  ser adicionado numa sessao futura pra entrar em `base/index.json`.
- **Heightened estruturado**: so 5 dos 151 rituais tem `system.heightening`
  no Foundry; outros 43 mencionam "Heightened" so em prosa
  (`heightened_so_prosa=true`), igual ao padrao ja visto em `magias.py`.

## 10. Dados brutos adicionados (nao existiam antes desta extracao)

- `pipeline/dados_brutos/foundry/spells/rituals/*.json` (150 arquivos,
  copiados do clone pinado no commit `87f9e5028baaa10b70fdc766260b7886def17e04`
  -- `magias.py` deixa essa pasta de fora explicitamente, entao nunca tinha
  sido copiada pra `dados_brutos/`)
- `pipeline/dados_brutos/aon_rituals.json` (201 docs brutos, `category=ritual`)
- `pipeline/dados_brutos/_dump_aon_rituais.py` (script de dump, mesmo padrao
  de `_dump_aon_ancestrias.py`, com `User-Agent` explicito -- o endpoint
  pendura sem ele)
