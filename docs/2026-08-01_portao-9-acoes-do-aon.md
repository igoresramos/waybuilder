# Portao 9 -- as 44 `action` do AoN sem decisao

Data: 2026-08-01
Fecha: portao 9 (`kind ausente vs censo do AoN`), que estava com 1 falha.
Arquivo alterado: `pipeline/censo_ausencias.json` (bloco `ausencias.action`, insercao pura).

## Veredito

**Nenhuma das 44 e conteudo de jogador que falta extrair.** As 44 sao
sub-documento de outra entidade e o conteudo delas **ja esta na base**, no texto
da entidade dona. Nao ha item de extracao a abrir.

## O que sao, medido

A categoria `action` do AoN tem 225 docs vigentes em censo. Das 44 sem decisao:

| grupo | quantos | o que e |
|---|---:|---|
| `exclude_from_search: true` | 42 | bloco `Activate—X` de um item magico, que o AoN publica como doc `action` proprio |
| `exclude_from_search: false` | 2 | `Extend Pseudopod` e `Seedpod Spring`, acoes de companheiro-cadeira do Treasure Vault |

O nome vem quebrado nos 42: o campo `name` do dump carrega o parenteses de
traits, nao o rotulo. Por isso a amostra do portao imprimia
`(concentrate, manipulate)` e `(auditory, emotion, incapacitation, ...)` -- o
rotulo de verdade so aparece no `markdown`, em `**Activate—<rotulo>**`.
Exemplo: `action-3562`, nome `(concentrate, manipulate)`, rotulo real
`Ring in the Quiet`, do item _Silent Bell_.

### Prova de que o conteudo entrou

Casando `Activate—<rotulo>` (extraido do `markdown` do dump) contra o store de
texto da base (`pipeline/base/text/*.json`, 20.612 entradas):

- **68 de 68** docs `exclude_from_search: true` da categoria acharam o item pai
  na base, com o texto da ativacao presente. Zero orfaos.
- As 2 acoes de cadeira estao em `wb:text/animal-companion/oozeform-chair`
  (Extend Pseudopod) e `wb:text/animal-companion/rootball-chair`
  (Seedpod Spring).

Amostra verificavel -- `pipeline/base/text/equipment.json`,
`wb:text/equipment/silent-bell`:

```
... The clapper is curiously absent from this bell and, when idly rung, it
produces no audible sound. Activate—Ring in the Quiet Three Actions
(concentrate, manipulate) Frequency once per day; Effect ...
```

## Por que aceitar, e nao extrair

A populacao do kind `action` e o pack `actionspf2e` do Foundry, **nao** a
categoria `action` do AoN. Isso ja estava decidido em
`specs/2026-07-31-kind-action.md`, e o extrator repete no cabecalho
(`pipeline/extratores/acoes.py:24-27`):

> FONTE PRIMARIA E O FOUNDRY, e nao o AoN -- ao contrario de `tactic`. A
> categoria `action` do AoN tem 3.979 docs e mistura acao de ATIVAR ITEM MAGICO
> (Treasure Vault e irmaos, 918 citacoes): a populacao nao e a mesma. O AoN entra
> so para completar prosa e o par legado/remaster.

O portao 9 nao sabia dessa decisao -- e o unico portao que mede contra o AoN
inteiro. Registrar em `censo_ausencias.json` e exatamente o mecanismo previsto.

As 2 acoes de cadeira nao escapam pela outra ponta: elas **nao existem no pack
do Foundry**. `grep -rln "Seedpod Spring" pipeline/dados_brutos/` e
`grep -rln "Extend Pseudopod"` batem so em `aon_dump/action.json`,
`aon_dump/animal-companion.json`, `aon_companheiros.json` e
`aon_ponte_remaster.json` -- nenhum arquivo do Foundry.

Criar um registro `action` por ativacao de item duplicaria o texto do item e
daria ao motor um alvo homonimo a mais para resolver errado -- que e o defeito
que o proprio extrator de acoes existe para impedir (o caso `Into the Fray`,
descrito no cabecalho dele).

## O que fica pendente, e nao e deste portao

Dos **56 itens-pai distintos** das 70 ativacoes registradas, **39 estao com
`mechanized: false` e `grants_completos: null`** (17 com `true`/`true`). Ou
seja: o texto entrou, a mecanica nao. Isso e cobertura de mecanizacao, medida
pelo **portao 10** (`grants_completos`), que hoje passa por catraca. Nao muda o
veredito do portao 9 -- "esse conteudo entrou?" tem resposta sim.

## Defeito colateral encontrado no proprio portao 9

O portao cobre por id **ou por nome**. Como o `name` dos docs de ativacao vem
quebrado, **26 dos 68** passam hoje por colisao de nome com registro de outro
kind:

```
action-3570 '(concentrate)' -> ('trait', 'Concentrate', 'wb:trait/concentrate')
action-3568 '(manipulate)'  -> ('trait', 'Manipulate',  'wb:trait/manipulate')
```

Nenhum dos 68 e citado por id na base (`xref.aon`/`xref.legado_aon`): a
cobertura desses 26 e ilusoria. Por isso `ids_aceitos` tem **70 ids e nao 44** --
os 68 `exclude_from_search: true` mais as 2 acoes de cadeira. A decisao e a
mesma para todos; registrar so os 44 deixaria os outros 26 quebrando o build no
dia em que a colisao de nome mudar.

O casamento por nome sem exigir kind compativel e um furo geral do portao (nao
so em `action`). **Nao foi mexido aqui** -- apertar o criterio pode desmascarar
ausencia em outras categorias e deixar o build vermelho, e isso e mudanca de
semantica de portao, que pede spec propria. Fica registrado como achado.

## Evidencia

```
$ python3 pipeline/portoes.py --fase final
fase final: 20083 registros  (indices: aon=43686, foundry=28689)
  ...
  portao 9  OK    kind ausente vs censo do AoN: 0
```

Antes / depois em `pipeline/base/relatorio_portoes_final.md`:

```
-**FALHOU** -- 1 ocorrencia(s).
-- `action`: 44 de 225 vigentes do AoN nao estao na base ... (44 sem decisao registrada)
+**PASSOU** -- 0 ocorrencia(s).
+_Ausencias ja decididas (4 categorias) -- visiveis, nao bloqueiam:_
+- `action`: 44 de 225 vigentes do AoN nao estao na base ... -- as 44 sao sub-documento de OUTRA entidade ...
```

O portao 4 (`cobertura caindo vs build anterior: 4`) continua falhando -- e
anterior a esta mudanca e independente dela (o diff do relatorio nao toca a
secao dele).
