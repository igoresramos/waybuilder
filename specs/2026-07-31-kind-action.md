---
spec: kind-action
project: waybuilder
version: 1
status: aprovada
created: 2026-07-31
todo: [111]
---

# Spec -- o pack que ninguem lia, e o predicado que da para traduzir

## O buraco, medido

O pack `actionspf2e` do Foundry (em disco: `packs/pf2e/actions/`) **nao e lido
por extrator nenhum**, e nao ha kind `action` na base. Isso nao e catalogo
faltando: e concessao quebrada em duas classes.

| | |
|---|---:|
| documentos no pack | 557 |
| referenciados por `GrantItem` de pack de construcao | **317** (56,9%) |
| referencias estaticas, de 322 donos | 353 |
| dessas, com `predicate` no proprio `GrantItem` | 44 |
| leitores dinamicos de escopo `actor` | 2 |

Terreno completo em `docs/medicoes/2026-07-31_terreno-pack-actions.md`.

O pack nao tem campo de nivel, e isso e correto: **o nivel de uma deed vem de
quem a concede**, nao dela. Nenhuma classe lista item de `actionspf2e` na sua
progressao -- zero ocorrencias.

## Decisao 1 -- `action` vira kind proprio

Mesmo precedente de `tactic` e `class-kit`, que so o censo do AoN acusou. A
forma e propria (`actionType` com `action`/`reaction`/`passive`/`free`,
`category`, e **sem nivel**), e `class-feature` nao a cobre.

O motor ja tem o gancho: `candidatos()` atende 4 blocos `ChoiceSet` com
`itemType: action` que o item 106 deixou declarados sem pool. `self._kinds` e
derivado do proprio index -- kind novo entra sem mudanca de codigo.

## Decisao 2 -- entra o pack INTEIRO, nao so as 317

O relatorio de terreno recomenda cortar nas 317 referenciadas. **Discordo, e o
motivo e de manutencao, nao de completude.**

1. O corte por referencia cria **dependencia de ordem**: o extrator passaria a
   depender de uma varredura de quem cita quem, feita antes dele. O projeto ja
   foi mordido por dependencia de ordem duas vezes (`ordem_de_classe`; o
   desempate de `fundir_renomeados` com prosa vazia).
2. O portao 9 ficaria com uma **sub-regra por pasta** em vez de uma linha
   removida -- e sub-regra de portao e onde a cobertura mente.
3. O custo esta medido e e irrelevante: 557 registros a ~45 B/registro gzip
   (analogo de `tactic`, mesmo pack) sao **~25-39 KB** contra um nucleo de
   0,529 MB. Menos de 5%.
4. O item 97 ja fixou a doutrina: **catalogo nao citado nao e defeito**. Trait
   551, relic 122 e language 121 vivem na base sem consumidor, e a terceira
   medicao daquele item mostrou que contar "nunca citado" como buraco e o
   proprio erro de metodo.

> O principio 1 ("nao e um sistema de jogo") **nao** e violado por isso.
> `Stride` na base e catalogo; o app viraria sistema de jogo se passasse a
> RODAR a acao, nao por conhece-la. O principio 4 ("nada e descartado") empurra
> na mesma direcao.

`FORA_DE_ESCOPO` do portao 9 perde a linha `action`, inteira.

## Decisao 3 -- `montar_ficha` ganha `action`

Em `emitir_app.py`, a tupla do nucleo. Sem isso a deed carrega sob demanda,
tarde demais para a primeira tela do Gunslinger e do Campeao. O corte de la e
por lista negra de CAMPO, nao de kind, entao nada mais muda.

## Decisao 4 -- `PACK_PARA_KIND` ganha `actionspf2e: action`, e isto conserta um falso positivo

Hoje `Way of the Drifter` concede `Into the Fray` e o resolvedor por nome
entrega **`wb:feat/into-the-fray`, que e outro registro** -- feat de nivel 8,
trait `archetype`, do arquetipo Viking. A deed do Gunslinger nao existe, e o
casamento acerta o alvo errado em silencio.

> Este e o mesmo defeito que a spec `2026-07-31-gemeo-do-grant-item.md`
> corrigiu para `classfeatures`: resolver **so por nome** e o erro; o pack do
> UUID e quem decide o kind. Sem esta linha, criar o kind `action` PIORA o
> caso, porque passaria a existir um segundo candidato e a preferencia por
> `feat` continuaria vencendo -- calada, e agora sem nem o alarme de "nao
> resolveu".
>
> Corolario que vale para o portao: minha propria medicao de 31/07 contou
> `Into the Fray` como alcancavel. Sao **10** alvos ausentes no Gunslinger, nao
> 9.

## Decisao 5 -- traduzir o subconjunto avaliavel de `predicate`

Dos 44 `GrantItem` que apontam para acoes com `predicate`, **26 usam apenas
prefixos que o nosso vocabulario ja sabe avaliar**:

| prefixos do predicado | n | traducao |
|---|---:|---|
| `class:` | 13 | `class_level: {<slug>: {">=": 1}}` |
| `class:` + `feat:` | 7 | `any` dos dois |
| `feat:` | 6 | `has: wb:feat/<slug>` |
| `feature:` | 12 | **sem traducao** -- fica pulado |
| `evolution:` / `enhancement:` | 6 | **sem traducao** -- fica pulado |

Esses 26 pousam em `grants[].se`, o campo da spec
`2026-07-31-grant-condicional.md`. Exemplos medidos:

```
Way of the Vanguard -> Clear a Path            ["class:gunslinger"]
Redemption -> Glimpse of Redemption            [{"or": ["class:champion", "feat:champions-reaction"]}]
Impulses -> Base Kinesis                       ["class:kineticist"]
```

> **Isto emenda a spec do grant condicional**, que declarava `GrantItem` com
> `predicate` inteiramente fora e dizia "o `se` e NOSSO vocabulario, nao o
> predicado deles". Certo para 18 dos 44; errado para 26, cujo predicado e um
> `has`/`class_level` escrito com outra sintaxe. Traduzir o que se traduz nao e
> implementar o interpretador do VTT -- e o mesmo movimento que
> `converter_rule_elements.py` ja faz ao converter so o declarativo.
>
> Consequencia direta: **o Campeao passa a ser resolvido**. `Justice ->
> Retributive Strike` e `Liberation -> Liberating Step` estao nesses 26. O item
> 107 achava que o Campeao pedia interpretar escolha do jogador; ele pedia duas
> coisas que existem, um kind e uma traducao de predicado.

Os 18 restantes ficam pulados **com o motivo escrito no relatorio**, nunca em
silencio -- `feature:`, `evolution:` e `enhancement:` falam de estado que a
nossa ficha nao modela.

## O passo do pipeline

`extratores/acoes.py`, no mesmo molde de `taticas_kits.py`:

1. le os 557 docs de `packs/pf2e/actions/`, emitindo `id` `wb:action/<slug>`,
   `name`, `traits`, `actionType`, `category`, `source` (100% dos docs tem
   `publication`) e prosa;
2. **sem `level`** -- o campo nao existe na fonte e inventa-lo seria arbitrar;
3. funde com o AoN por nome apenas para a PROSA e para o par
   Legacy/Remaster (`remaster_id`/`legacy_id`), com a ressalva medida no
   terreno: a categoria `action` do AoN tem 3.979 docs e mistura acao de ATIVAR
   ITEM MAGICO (Treasure Vault e irmaos, 918 citacoes) -- a populacao nao e a
   mesma, entao o Foundry e a fonte primaria e o AoN so completa;
4. Pf2eTools (442 docs, limpo) entra como terceira fonte pelo caminho normal de
   reconciliacao.

## Como se prova que funciona

1. `wb:action/ten-paces` existe, com `actionType: action` e sem `level`.
2. Um Gunslinger 1 `Way of the Pistolero` tem `Ten Paces` na ficha; um
   `Way of the Sniper` nao tem, e tem `One Shot, One Kill`.
3. `Way of the Drifter` concede `wb:action/into-the-fray` -- e **nao**
   `wb:feat/into-the-fray`. Teste explicito, porque este passava antes por
   homonimo.
4. Um Campeao 1 de causa `Justice` tem `Retributive Strike`; o de `Liberation`
   tem `Liberating Step`; nenhum tem os dois.
5. Um personagem que nao e Campeao nem tem `Champion's Reaction` nao recebe
   nenhuma das duas, mesmo com a causa na ficha (o `or` do predicado traduzido).
6. Os 18 predicados sem traducao aparecem no relatorio com o prefixo que os
   barrou, contados.
7. Portao 9 passa com `action` fora de `FORA_DE_ESCOPO`.
8. Payload: o nucleo cresce menos de 5% e o `_manifesto.json` registra o kind.
9. Paridade Python/TS nas 20 fichas de exemplo, e os 10 portoes.

## O que esta spec NAO resolve, e declara

1. **As 240 acoes de mesa entram como catalogo puro**, sem slot e sem
   consumidor. E deliberado (decisao 2), nao lacuna.
2. **Os 18 `predicate` de `feature:`/`evolution:`/`enhancement:`** continuam
   pulados. `evolution:` e do Summoner e depende do slot de feat de evolucao do
   eidolon, que a base nao modela (achado ja registrado na rodada 6).
3. **A via secundaria do Gunslinger** -- `Slinger's Readiness` e `Practiced
   Reloads`, os 2 feats que perguntam "qual e a MINHA deed inicial" -- depende
   da spec do grant condicional, nao desta. Esta spec entrega a via primaria,
   que e a `Way` concedendo a propria deed.
4. **Sem nivel na acao**, a ficha mostra a deed no nivel de quem a concede.
   Nenhuma tela depende disso hoje; se um dia depender, o dado nao esta na
   fonte.
