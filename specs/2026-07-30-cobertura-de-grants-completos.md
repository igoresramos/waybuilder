---
spec: cobertura-de-grants-completos
req: WB-030
project: waybuilder
version: 1
status: implementada
created: 2026-07-30
altera: [WB-002]
todo: 59
---

# Spec -- os tres extratores que nunca responderam `grants_completos`

## O problema

`grants_completos` existe para separar duas coisas que `grants: []` confunde:
"este registro nao tem mecanica nenhuma" e "tinha mecanica e o pipeline nao
converteu". O portao 10 (spec `2026-07-29-portao-de-cobertura-de-grants.md`) ja
vigia a cobertura como catraca, mas ele foi calibrado sobre a realidade de
ontem: **8.360 dos 19.706 registros (42,4%) nao emitem o campo**.

Nao esta espalhado. Sao **oito kinds inteiros**, de **tres extratores**:

| extrator | kinds | registros sem o campo |
|---|---|---:|
| `equipamento.py` | equipment, weapon, armor, shield | 7.423 |
| `classes.py` | class, class-feature | 868 |
| `taticas_kits.py` | tactic, class-kit | 69 |

Todo o resto da base ja responde.

## O que cada extrator ja tem na mao

Nenhum dos tres precisa de dado novo. Os tres **ja computam a informacao** e a
gravam no campo da v1, `mechanized`:

- `equipamento.py:713` chama `converter_grants(f["rules"], ...)` e recebe
  `perdeu` -- o segundo valor de retorno e exatamente "havia rule element que
  eu nao sei converter". So nunca chegou a `comum.mecanizacao()`.
- `classes.py:604` calcula `mechanized = len(rules_extra) == 0` para `class`, e
  `montar_grants_feature()` devolve `(grants, mechanized, motivos)` para
  `class-feature`, onde `mechanized = not subf_extra and not rules`.
- `taticas_kits.py` monta o envelope com `aon_kinds.converter()`, que **desde
  2026-07-29 ja emite `grants_completos: None`** -- a saida em disco e de
  27/07, anterior a mudanca. Rodar de novo ja traz o campo; o que falta e o
  valor CERTO, porque `None` esta errado nestes dois kinds (ver abaixo).

O trabalho e ligar o que existe a `comum.mecanizacao()`, que e a unica funcao
autorizada a decidir o tri-estado.

## A decisao por kind

`comum.mecanizacao(kind, tinha_mecanica, perdeu_mecanica, ...)`. O que muda de
kind para kind e so o que alimenta os dois primeiros argumentos.

| kind | `tinha_mecanica` | `perdeu_mecanica` |
|---|---|---|
| equipment / weapon / armor / shield | `bool(doc_foundry["rules"])` | `perdeu` de `converter_grants` |
| class | **sempre True** | `bool(system["rules"])` |
| class-feature | `bool(proficiencies or subfeatures_extra or rules)` | `bool(subfeatures_extra or rules)` |
| tactic / class-kit | **sempre True** | **sempre True** |

Tres justificativas, porque nenhuma e obvia:

**`class` tem mecanica sempre.** O registro nasce de `montar_grants_classe()`,
que le `hp`, `perception`, `savingThrows` e `attacks` -- campos estruturados que
toda classe tem. `grants` nunca sai vazio. `None` ali seria mentira: nao ha
ausencia de declaracao, ha declaracao completa em 22 das 27.

**`class-feature` sem nada declarado responde `None`, nao `True`.** Sao 164
features cujo doc do Foundry nao tem `subfeatures` nem `rules`. Marcar `True`
repetiria o erro das 61 dedicacoes: o consumidor concluiria que `grants: []`
representa a feature, quando o que houve foi a fonte nao declarar.

**`tactic` e `class-kit` respondem `False`, e isso e o proprio extrator quem
diz.** A docstring de `taticas_kits.py` ja registra: tatica tem mecanica real
("ativar um efeito num aliado que ouve o Step") e kit tem mecanica real (lista
de itens iniciais), e a **linguagem de `grants` da spec nao tem vocabulario para
nenhuma das duas**. Isso e perda declarada, que e a definicao de `False`. O
`None` que `aon_kinds.converter()` daria por heranca esta errado aqui -- ele
descreve fonte que nao declarou, e estas duas declaram.

## O numero que vai aparecer

Projetado registro a registro contra o dump do Foundry (via `xref.foundry`, que
ja guarda o casamento feito pelo extrator):

| kind | true | false | null | total |
|---|---:|---:|---:|---:|
| equipment | 877 | 41 | 5.204 | 6.122 |
| weapon | 303 | 11 | 728 | 1.042 |
| armor | 63 | 4 | 149 | 216 |
| shield | 25 | 0 | 100 | 125 |
| class-feature | 69 | **608** | 164 | 841 |
| class | 22 | 5 | 0 | 27 |
| tactic | 0 | 37 | 0 | 37 |
| class-kit | 0 | 32 | 0 | 32 |
| **total** | **1.359** | **738** | **6.345** | **8.442** |

O numero que importa nao e o total: e **`class-feature` com 608 `False`, 72% do
kind**. Ele diz, com marca no registro, o que o item 40 vem dizendo em prosa --
o efeito de subclasse e de progressao de classe esta majoritariamente por
converter. Ate hoje isso era invisivel por construcao, porque o kind nao
respondia. Este e o valor real da spec: nao e emitir campo, e **parar de esconder
608 perdas**.

`equipment` com 5.204 `null` nao e lacuna: e a maioria do catalogo (corda, tocha,
racao) que nao tem rule element nenhum no Foundry, e `null` e a resposta certa.

## Efeito no portao 10

A catraca conta registros SEM resposta e reprova quando o numero SOBE. Isto o
derruba de **8.360 para 0**, entao ela passa folgada. Depois de reemitir, a
linha de base e regravada (`--gravar-cobertura`) com o novo piso -- sem isso a
catraca continua tolerando uma regressao de 8.360 registros.

Com a base em zero, a catraca deixa de ser o instrumento principal e o teste do
oraculo assume: `test_portoes.py` passa a exigir **todo registro com o campo**,
sem tolerancia. Catraca serve para descer de um numero alto; chegando a zero,
assercao dura e mais barata e mais honesta.

## O que esta spec NAO resolve, e declara

- **Converter os 738 `False`.** Esta spec MARCA a perda, nao a repara. Reparar
  e a Fase 3 do plano (item 40) para `class-feature`, e o item 72 para o
  `flat_modifier` de equipamento.
- **Dar vocabulario de `grants` para tatica e kit.** Enquanto a linguagem nao
  tiver como expressar "ativa efeito em aliado" e "concede lista de itens
  iniciais", os 69 continuam `False` com razao.
- **`mechanized`.** Continua sendo emitido pelos tres extratores, como no resto
  da base. A troca de schema v1 -> v2 e o item 53, e nao entra aqui: mexer nela
  junto misturaria duas mudancas independentes no mesmo diff.

## Como se prova que funciona

1. Registros sem `grants_completos` caem de 8.360 para **0**, e nenhum kind
   fica de fora do relatorio do portao 10.
2. `class-feature` reporta 608 `False` -- e um numero que SOBE de zero, e isso
   e a spec funcionando, nao regressao.
3. `wb:class/fighter` responde `True` (nenhum rule element extra); uma classe
   com `rules` no doc responde `False`.
4. Um item sem doc do Foundry (`wb:equipment/*` so do AoN) responde `null`, e
   nao `false` -- ausencia de fonte nao e perda.
5. `wb:tactic/*` e `wb:class-kit/*` respondem `False` em 37/37 e 32/32.
6. `test_portoes.py` passa a exigir cobertura total e fica verde.
7. Os 10 portoes verdes, oraculo Python verde, 113 testes do TS verdes,
   verificacao de navegador verde.
