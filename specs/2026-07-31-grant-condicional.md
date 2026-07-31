---
spec: grant-condicional
project: waybuilder
version: 1
status: proposta
created: 2026-07-31
todo: [69, 107]
---

# Spec -- o grant que espera a escolha, e a condicao que nao alarga

## Como isto comecou, e a premissa que caiu

O item 107 declarou um bloqueio:

> SOBRAM 33: nao tem gemeo concedido, e a mae que os concederia (`Cause`, do
> Campeao) usa `GrantItem` com UUID DINAMICO
> (`{item|flags.system.rulesSelections.cause}`) -- aponta para o que o jogador
> escolheu, e o extrator pula os 163 casos assim, corretamente. Resolver pede
> interpretar a escolha no build, outra familia.

Medido contra a fonte, **"os casos assim" nao sao uma familia so**, e a maior
delas nao precisa de nada. Varridos os packs de construcao do Foundry
(`class-features`, `feats`, `classes`, `heritages`, `ancestries`,
`backgrounds`, `deities`), sao **221** ocorrencias hoje, em duas formas:

| forma | n | o que diz |
|---|---:|---|
| `{item\|...rulesSelections.X}` com o `ChoiceSet` da flag `X` **no mesmo item** | 206 | "conceda o que foi escolhido NESTE eixo" |
| `{actor\|flags.system.<classe>.<flag>}` | 15 | "conceda o que foi escolhido em OUTRO item" |

Das 206: 165 com `ChoiceSet` de `filter`, 36 de lista literal, 4 sem `choices`
e **1** orfa de verdade (`Runtsage`).

### As 206 ja estao resolvidas, e por isso pular foi certo

O proprio caso citado pelo item 107 e desta forma. `Cause`, do Campeao:

```json
{"key": "ChoiceSet", "flag": "cause",
 "choices": {"filter": ["item:tag:champion-cause", {"or": [...sanctification...]}]}}
{"key": "GrantItem", "uuid": "{item|flags.system.rulesSelections.cause}"}
```

O `GrantItem` concede **a propria opcao escolhida no ChoiceSet irmao**. Isso e
identidade: no nosso modelo, escolher a opcao de um eixo JA e te-la. E o eixo
existe -- `wb:class/champion` tem `subclasses[eixo=cause]` com as sete causas
(`justice`, `liberation`, `redemption`, `obedience`, `iniquity`,
`desecration`, `grandeur`).

> **Nao ha o que implementar aqui, e implementar seria pior.** Converter o
> grant dinamico em concessao faria a ficha conceder de novo o que a escolha ja
> deu. O extrator continua pulando as 206, agora com o motivo certo escrito:
> nao e "referencia que nao sei resolver", e "redundante com o eixo".

## O defeito, medido: as 15 de escopo `actor`

Aqui a escolha vive em OUTRO item. A opcao escolhida escreve uma flag no ator,
e a feature generica -- que ja esta na progressao da classe, no nivel certo --
le a flag para saber QUAL variante conceder. `Cloistered Cleric`:

```json
{"key": "ActiveEffectLike", "mode": "override", "path": "flags.system.cleric",
 "value": {"firstDoctrine":  "Compendium.pf2e.classfeatures.Item.First Doctrine (Cloistered Cleric)",
           "secondDoctrine": "...Second Doctrine (Cloistered Cleric)",
           "...": "6 doutrinas"}}
```

e `First Doctrine`, concedida pela progressao do Clerigo no nivel 1:

```json
{"key": "GrantItem", "uuid": "{actor|flags.system.cleric.firstDoctrine}"}
```

> **Isto nao e "interpretar a escolha do jogador no build". E uma tabela.** A
> opcao declara o mapa INTEIRO, estaticamente, na propria fonte. Nada aqui
> depende de runtime: depende de ler os dois lados e cruzar.

Cruzados os dois lados, saem **79 pares** `(opcao, item concedido)`. Descontados
os 15 `Spell Effect:` do wild shape do Druida -- que sao efeito de VTT, nao
construcao --, sobram **64 acionaveis**, de **31 opcoes**:

| familia | pares | opcoes |
|---|---:|---:|
| Taumaturgo (`initiateBenefit`, `adeptBenefit`, `paragonBenefit`) | 30 | 20 |
| Clerigo (as 6 doutrinas x 2 subclasses) | 12 | 2 |
| Alquimista (`fieldDiscovery`, `greaterFieldDiscovery`, `advancedVials`) | 12 | 4 |
| Gunslinger (`initialDeed`, `slingersReload`) | 10 | 5 |

O Taumaturgo encadeia dois niveis: `Amulet` escreve Initiate **e** Adept, e
`Adept Benefit (Amulet)` escreve Paragon. A cadeia de grants ja e recursiva,
com guarda de profundidade e de visitados; isto so a exercita.

## O que muda para o item 69, e por que ele estava certo

O item 69, fatia 2, gateou 68 variantes por subclasse com `requires.subclass`:
elas aparecem na lista, MARCADAS com o motivo (`exige a sub-escolha
Chirurgeon; tem Bomber`). E o proprio item declarou o limite:

> o modelo CERTO das 68 seria o dono CONCEDER a variante em vez de o jogador
> escolhe-la marcada, e isso pede vocabulario novo de grant (`concede feature
> no nivel N`) que nao existe

**Os 64 pares sao esse vocabulario, ditado pela fonte.** E o vocabulario e
menor do que o item previa: nao e "concede feature no nivel N", porque o nivel
JA esta na progressao da classe (`First Doctrine` no 1, `Second` no 3). Falta
so a condicao.

Sobreposicao com as 68, medida so por familia e nao registro a registro:
Taumaturgo bate (30 pares / 30 gateadas), Clerigo bate (12 / 12), Alquimista
**nao** (12 pares / 23 gateadas). O Gunslinger nao aparece nas 68. Ou seja:
esta spec cobre parte das 68 e acrescenta uma familia que elas nao tinham. O
gate do item 69 **fica onde esta** para o que nao tiver par -- os dois modelos
convivem, e a spec nao remove gate nenhum.

## O vocabulario: `grants[].se`

Um campo, opcional, em qualquer entrada de `grants`:

```json
{
  "id": "wb:class-feature/first-doctrine",
  "grants": [
    {"grant_feat": ["wb:class-feature/first-doctrine-cloistered-cleric"],
     "se": {"has": "wb:class-feature/cloistered-cleric"}},
    {"grant_feat": ["wb:class-feature/first-doctrine-warpriest"],
     "se": {"has": "wb:class-feature/warpriest"}}
  ]
}
```

`se` guarda um predicado da MESMA gramatica de `requires` -- `all`/`any`/`not`
e os termos existentes. Nao ha termo novo: `has` ja resolve alias e gemeo
(spec `2026-07-31-gemeo-do-grant-item.md`) e ja tem recorte temporal (spec
`2026-07-29-recorte-temporal-do-has.md`).

Ausencia de `se` significa incondicional -- e o que os grants de hoje sao.

## A regra que faz esta spec ser segura, e que inverte o default

O avaliador tem, deliberadamente, um default permissivo:

```python
if metodo is None:
    continue          # termo desconhecido nao reprova: nao arbitra
```

Isso e **certo em `requires`**, que so sugere e marca: atomo ignorado ALARGA a
lista, e o principio zero manda nao esvaziar em silencio. Em **`se`** o mesmo
default se inverte de sentido: um termo que o motor nao entende faria a ficha
CONCEDER -- e conceder todas as variantes de uma vez poe numero errado na
ficha, sem aviso. E a mesma armadilha que o item 108 pagou, com o envelope
`{"and": [...]}` que virou no-op silencioso em dois passos.

**Regra: `se` que nao puder ser DECIDIDO nao concede, e marca pendente.** Nao e
o mesmo que "nao concede": pendente e o estado que o motor ja distingue para
alvo dinamico, e o app precisa dele para nao confundir com ausencia. Em
concreto:

1. o avaliador de `se` roda em modo estrito -- termo desconhecido devolve
   INDECIDIVEL, nao "satisfeito";
2. INDECIDIVEL nao concede e entra na lista de pendencias com o motivo;
3. so `False` explicito descarta em silencio (a variante da outra subclasse
   nao e pendencia: e escolha do jogador que foi para outro lado).

## Ordem de avaliacao

`se` le estado que outra escolha produz, entao a ordem importa -- e o projeto ja
foi mordido por dependencia de ordem duas vezes (`ordem_de_classe`, e o
desempate de `fundir_renomeados` com prosa vazia).

A condicao e avaliada **dentro** de `_grants_em_cadeia`, que ja roda depois de
`self.features` estar montado (progressao + subclasse escolhida). Nenhuma
reordenacao nova: as opcoes de subclasse entram como feature antes de a cadeia
comecar. O que a spec exige e que isso vire **teste**, nao suposicao -- ver
prova 5.

## O passo do pipeline

`derivar_grant_condicional.py`, depois de `converter_rule_elements.py` e antes
de `unificar_efeitos.py`:

1. varre os packs de construcao por `ActiveEffectLike` cujo `path` comece em
   `flags.system.` e cujo `value` (string ou objeto) contenha UUID de
   compendio -- sao os 79 pares;
2. varre por `GrantItem` de escopo `actor` -- sao os 15 leitores -- e casa
   flag com flag;
3. para cada par casado, escreve em `grants` do LEITOR uma entrada com `se:
   {has: <id da opcao>}` e alvo resolvido pelo pack (`PACK_PARA_KIND`, a mesma
   regra do gemeo -- resolver so por nome e o defeito que a spec do gemeo
   corrigiu);
4. descarta `Spell Effect:` por prefixo, declarando a contagem no relatorio;
5. alvo que nao resolve na base entra em `relatorio_grant_condicional.md` como
   ausencia, com nome e pack -- nunca sumindo em silencio.

## Como se prova que funciona

1. Um Clerigo 3 `Cloistered Cleric` tem `First Doctrine (Cloistered Cleric)` e
   `Second Doctrine (Cloistered Cleric)` na ficha, e **nao** tem as do
   Warpriest.
2. Trocada a subclasse para `Warpriest`, a ficha inverte as seis.
3. Um Taumaturgo 9 com implemento `Amulet` recebe Initiate, Adept e Paragon
   Benefit (Amulet) nos niveis certos -- a cadeia de dois lances.
4. Um Alquimista `Bomber` nao recebe `Field Discovery (Chirurgeon)`.
5. **Determinismo:** embaralhar a ordem das escolhas no documento nao muda a
   ficha -- o teste de invariante ja existe e passa a cobrir estes casos.
6. **Estrito:** um `se` com termo inventado NAO concede, e aparece como
   pendencia com motivo. Teste proprio, porque este e o unico ponto onde o
   default do avaliador precisa ser o contrario do que ele e.
7. Paridade Python/TS: as 20 fichas de exemplo derivam identicas nos dois
   motores.
8. Os 10 portoes passam.
9. Verificacao no navegador (`app/verificacao/`): a ficha do Clerigo mostra a
   doutrina certa. A terceira camada ja passou verde sobre base errada uma vez
   -- por isso esta camada existe.

## O que esta spec NAO resolve, e declara com numero

1. **As 206 de escopo `item` continuam puladas**, agora por redundancia com o
   eixo, nao por ignorancia. Sobra `Runtsage`, 1 caso, sem `ChoiceSet` irmao --
   nao investigado.
2. **9 alvos nao existem na base**, e por isso 9 dos 64 pares vao morrer no
   passo 5 acima: as deeds do Gunslinger (`Ten Paces`, `One Shot, One Kill`,
   `Clear a Path`, `Living Fortification`, `Covered Reload`, `Raconteur's
   Reload`, `Reloading Strike`, `Touch and Go`, `Spring the Trap`). Vivem no
   pack `actionspf2e`, que **nenhum extrator le** -- nao ha kind `action`. O
   Gunslinger entra nesta spec com 1 dos 10 pares funcionando; os outros 9 so
   depois que o pack for extraido.
3. **O Campeao nao e resolvido por esta spec**, e o item 107 aponta a familia
   errada para ele. A rota `Cause -> causa escolhida` ja esta modelada (secao
   1). O que prende ali e OUTRA coisa: `Justice` concede `Retributive Strike`
   por `GrantItem` com **`predicate`** -- balde de 293 pulados, nao de UUID
   dinamico -- e `Retributive Strike` / `Liberating Step` tambem nao existem na
   base, pelo mesmo pack `actionspf2e` do ponto 2.
4. **O gate do item 69 nao e removido.** As gateadas sem par continuam
   aparecendo marcadas. Converter as demais pede medir registro a registro a
   sobreposicao, que esta spec nao fez.
5. **`GrantItem` com `predicate` (293) segue fora.** O predicado do Foundry
   fala de estado de combate e flag de ator; avaliar isso e o interpretador,
   que continua recusado. O `se` desta spec e NOSSO vocabulario, alimentado por
   uma tabela estatica -- nao e o predicado deles.
