# Extrator de Equipamento, Armas, Armaduras e Escudos

`pipeline/extratores/equipamento.py` -> `pipeline/saida/equipamento.json`
(7.496 registros, 7,15 MB) + `pipeline/saida/_equipamento_estatisticas.json`

Fontes: Foundry `packs/pf2e/equipment/` (commit `87f9e5028b...`, 5.698 arquivos),
AoN elasticsearch (categorias `weapon`/`armor`/`shield`/`equipment`, cache em
`dados_brutos/aon_equipment_<cat>.json`), pf2etools `data/items/baseitems.json`
(410 itens base, cache em `dados_brutos/pf2etools/baseitems.json`).

## Contagem por kind

| kind | registros | com estrutura mecanica | so prosa |
|---|---:|---:|---:|
| equipment | 6.137 | 5.959 | 178 |
| weapon | 1.034 | 1.030 | 4 |
| armor | 207 | 202 | 5 |
| shield | 118 | 118 | 0 |
| **total** | **7.496** | **7.309** | **187** |

`mechanized`: 7.440 `true` / 56 `false` (rule element do Foundry fora do
vocabulario minimo de `grants` implementado -- ver secao final).

**Os numeros nao batem com "VOLUME ESPERADO" do brief (equipment 8.642 |
weapon 614 | armor 75 | shield 32) de proposito.** Aqueles são contagens da
*categoria* do AoN (como a Paizo organiza a pagina). O `kind` do registro
segue o `type` do Foundry (como o item se comporta mecanicamente), que e o
campo vencedor por contrato. Um item magico especifico que ataca e causa dano
(ex.: um bordao de combate, uma bomba alquimica) e `type: weapon` no Foundry
mesmo que o AoN o cataloge em "Equipment" -- entao ele sai como `wb:weapon/...`,
nao `wb:equipment/...`. Ver "kind reconciliado" abaixo.

## Como as runas foram modeladas

Nao existe "+1 Striking Longsword" como registro proprio -- nem no Foundry,
nem aqui. Runas fundamentais e de propriedade sao itens comuns dentro do
pacote `equipment` do Foundry, marcados por `system.usage.value` no formato
`etched-onto-(a-)?(weapon|armor|shield)`. O extrator:

1. Emite o item base (`wb:weapon/longsword`, `wb:armor/leather-armor`, ...)
   com um campo `runes` = snapshot do `system.runes` do Foundry (slots que
   aquele tipo de item aceita -- `potency`/`striking`/`property[]` para arma,
   `potency`/`resilient`/`property[]` para armadura, `reinforcing` para
   escudo). Em item mundano isso vem zerado; em item magico especifico com
   runa ja embutida (ex.: `handwraps-of-mighty-blows`) vem preenchido.
2. Emite a runa como `kind: equipment` normal, com um campo extra
   `rune: {tipo, aplica_em, grau}` quando detectada. `tipo` in
   `potency|striking|resilient|reinforcing|property`; `aplica_em` in
   `weapon|armor|shield`; `grau` e o nivel do bonus quando dedutivel do nome
   (`weapon-potency-2` -> grau 2; `resilient-greater` -> grau 3). 155 runas
   detectadas: 6 potency, 5 reinforcing, 101 na categoria generica `property`
   (`tipo` cai em `property` quando o nome nao segue o padrao canonico
   `<grau->striking/resilient` -- por exemplo `resilient-greater.json` bate
   certo, mas `mythic-striking.json` nao tem grau reconhecivel e fica em
   `property` mesmo sendo uma runa `striking`; a classificacao fina de
   `tipo` e best-effort, `aplica_em` e confiavel).

A composicao do item final (base + runas) fica para o app, em tempo de
construcao -- e o unico jeito de nao multiplicar 1.034 armas x 4 graus de
potency x 4 de striking x N de propriedade em dezenas de milhares de SKUs
ineditos. Coerente com o Principio zero: o Waybuilder monta, nao pre-calcula
todo combo possivel.

## Variante de nivel: um registro ou varios?

**Um registro por item distinto.** PF2e nao tem "a mesma arma em varios
niveis" -- cada arquivo do Foundry e cada `id` do AoN e um nome proprio.
Onde parece variante de nivel (pocoes, bombas alquimicas, cristais de
potencia) a Paizo da nomes diferentes por grau (`Acid Flask (Lesser)`,
`(Moderate)`, `(Greater)`, `(Major)`), entao cada grau vira um `wb:equipment/`
proprio (`acid-flask-lesser`, `acid-flask-greater`, ...) com seu proprio
nivel e preco. Nao houve necessidade de colapsar nada -- diferente do caso de
`class-feature` da spec-base, aqui nivel e escalar intrinseco do item, nao
da progressao de outra entidade.

## Divergencias entre fontes

1. **Fronteira de `kind` diverge entre AoN e Foundry** (a divergencia mais
   relevante desta extracao). AoN organiza por pagina de catalogo; Foundry
   por mecanica de item. Reconciliados via `kind_por_chave_foundry` (Foundry
   decide quando tem opiniao):
   - `equipment -> weapon`: 898 (bombas alquimicas, bordoes/varinhas usados
     como arma, itens magicos especificos de ataque)
   - `equipment -> shield`: 143
   - `equipment -> armor`: 207
   - `weapon -> equipment`: 23 (caminho inverso, mais raro)
   Sem essa reconciliacao cada um desses nomes viraria DOIS registros
   orfaos (um so-Foundry sem enriquecimento do AoN, um so-AoN sem os campos
   mecanicos do Foundry) em vez de um so, completo. Foi o primeiro bug
   encontrado ao rodar o extrator (contagem de `weapon` inflada em ~13
   registros fantasmas antes do fix).
2. **`traits`**: 1.677 conflitos. O Foundry usa slugs proprios para tracos
   parametrizados de dano (`versatile-p`, `versatile-s`, `two-hand-d12`)
   onde o AoN usa o nome legivel (`versatile`, `two-hand`). AoN venceu em
   todos (contrato), mas o dado do Foundry desses casos especificos
   carrega informacao (qual dado/tipo o trait modifica) que o slug do AoN
   perde -- fica so em `xref.foundry` para quem precisar remontar.
3. **`level`**: 55 conflitos, nivel legado vs remaster normalmente 1 unidade
   de diferenca em itens que mudaram de preco/nivel na reedicao. Foundry
   venceu (contrato).
4. **pf2etools**: cache local restrito a `baseitems.json` (410 itens base
   de arma/armadura/escudo) -- nao ha cache dos ~150 arquivos
   `items-<livro>.json` de itens magicos por sourcebook, entao a "terceira
   opiniao" so cobre item base, nao equipamento magico. Onde cobre
   (233 armas, 32 armaduras, 16 escudos em FTA — as tres fontes concordando),
   serviu de conferencia extra; fora disso nao bloqueou nada porque o
   contrato nao exige pf2etools para nenhum campo desta extracao (so
   `requires`, que equipamento normalmente nao tem).

## O que nao conseguiu mapear

- **1.636 registros sem `license`** (1.577 `equipment`, 54 `weapon`, 5
  `armor`) -- o livro-fonte do AoN nao apareceu em nenhum item do Foundry
  com `publication.license` preenchida, entao a tabela de licenca aprendida
  por cruzamento (mesmo truque de `feats.py`) nao teve voto pra esse livro.
  Sao majoritariamente splatbooks de aventura/aventura-especifica com poucos
  itens cada. Sem isso, esses registros nao passam no portao de qualidade
  #5 da spec (licenca ausente) -- **ficaram fora do build ate essa lacuna
  ser fechada**, ou precisam de uma lista curada livro->licenca como
  fallback.
- **6 registros sem `source` nenhum** (`heavy-power-suit`, `hide`,
  `leather`, `studded-leather`, `nine-ring-sword`, `wind-and-fire-wheel`) --
  existem so no Foundry ou so no pf2etools, sem primary_source no AoN e sem
  `publication` no Foundry preenchida.
- **187 registros so-prosa** (sem nenhum campo mecanico estruturado: bulk,
  preco, dano, ac...) -- em geral itens de historia/decoracao sem stats
  (`abysium` cru como material, plantas, curiosidades) onde nem Foundry nem
  AoN carregam numero nenhum.
- **56 registros `mechanized: false`** -- tem `system.rules` no Foundry com
  rule element fora do vocabulario minimo que implementei aqui (so
  `FlatModifier`/`Resistance`/`Immunity`/`Weakness`/`DamageDice`; o
  conjunto completo de `feats.py` — `ActiveEffectLike`, `GrantItem`,
  `ChoiceSet` etc — nao foi portado porque equipamento raramente concede
  proficiencia/escolha como feat concede; a decisao foi deliberada para nao
  reimplementar o conversor inteiro sem evidencia de que valeria a pena).
- **`grants`/`requires` ficam vazios/`null` por padrao** -- equipamento no
  PF2e nao tem pre-requisito no sentido do schema (nada de
  `class_level`/`ability`/`has`), entao `requires` nunca e preenchido nesta
  extracao; e `grants` so aparece quando ha `rules[]` convertivel (a maioria
  dos itens mundanos nao tem nenhuma).

## Auto-review

- Portao de qualidade #1 da spec (todo campo preenchido tem `prov`)
  verificado programaticamente: 0 violacoes em 7.496 registros.
- `conflitos` so aparece quando ha divergencia real (traits/level), nunca
  populado por omissao.
- Bug de fronteira de `kind` (item 1 acima) encontrado e corrigido antes da
  entrega -- primeira rodada tinha duplicatas fantasma; segunda rodada
  reconciliou 1.271 registros pro kind certo.
