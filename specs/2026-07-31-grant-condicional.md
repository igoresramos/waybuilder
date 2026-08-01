---
spec: grant-condicional
req: WB-063
project: waybuilder
version: 2
status: implementada
created: 2026-07-31
altera: [WB-002]
todo: [69, 107]
---

# Spec -- o grant que espera a escolha, e a condicao que nao alarga

> **v2, depois do review adversarial** (`docs/2026-07-31_review-adversarial-grant-condicional.md`).
> A v1 caiu em tres pontos, todos re-medidos e confirmados: o numero de pares
> estava inflado por um erro meu de leitura da fonte, a secao das 206 estava
> certa na conclusao e errada na justificativa, e a garantia de ordem nao
> existia. O nucleo -- `grants[].se` com avaliacao estrita -- sobreviveu.

## Como isto comecou, e a premissa que caiu

O item 107 dizia que os `GrantItem` com UUID dinamico pediam "interpretar a
escolha no build". Medidos nos packs de construcao, sao **221**, em duas formas:

| forma | n | o que diz |
|---|---:|---|
| `{item\|...rulesSelections.X}`, `ChoiceSet` da flag no MESMO item | 206 | "conceda o que foi escolhido neste eixo" |
| `{actor\|flags.system.<classe>.<flag>}` | 15 | "conceda o que foi escolhido em OUTRO item" |

### As 206 nao sao um bloco homogeneo -- correcao da v1

A v1 dizia "as 206 sao redundantes com o eixo, nao ha o que fazer". A conclusao
para esta spec continua valendo -- **nenhuma delas se resolve com `se`** --, mas
a justificativa era falsa por generalizar de um caso so (`Cause`). A particao
medida:

| grupo | o que acontece |
|---|---|
| identidade tipo `Cause` | o eixo existe e a escolha ja e a posse. Nada a fazer |
| redundantes com o slot do item 106 | o slot concedido ja pergunta ao jogador |
| **class-features sem mecanismo nenhum** | impulso do Kineticist, `grantedIkon` do Exemplar, sub-escolha de divindade -- **ficam sem resposta**, e esta spec nao as resolve |
| **9 backgrounds com escolha achatada** | **defeito ativo**, medido abaixo |

O terceiro grupo passa a ser divida declarada, nao "resolvido". O quarto virou
**item 112**, porque e bug na ficha de hoje e independe desta spec:

```
Beast Seeker         fonte 1-de-2  ->  base concede 2  (titan-wrestler + dirty-trick)
Child of the Polis   fonte 1-de-2  ->  base concede 2
Glory Hound          fonte 1-de-2  ->  base concede 2
Obari Wanderer       fonte 1-de-2  ->  base concede 2
Anti-Thrune Saboteur fonte 1-de-2  ->  base concede 1, escolhido arbitrariamente
Child of Notoriety   fonte 1-de-2  ->  base concede 0
Conservator          fonte 1-de-2  ->  base concede 0
Dedicated Delver     fonte 1-de-2  ->  base concede 0
Historical Reenactor fonte 1-de-2  ->  base concede 0
```

Um mesmo defeito, tres sintomas: feat a mais, feat arbitrario, feat perdido.

## Os pares: 44, e nao 79 -- correcao da v1

A v1 contou **79 pares** varrendo `ActiveEffectLike` com UUID no `value`, **sem
olhar o `mode`**. Esse era o erro, e ele importa:

| `mode` | n | o que significa |
|---|---:|---|
| `override` | 26 regras | escreve a flag: "a minha variante e esta" |
| `add` | 35 regras | **acumula numa lista**: "eu acrescento esta OPCAO" |

`add` nao e concessao, e **oferta**. O implemento do Taumaturgo:

```json
{"key": "ActiveEffectLike", "mode": "add",
 "path": "flags.system.thaumaturge.adeptChoices",
 "value": {"label": "{item|name}", "value": "...Adept Benefit (Amulet)"}}
```

Cada implemento ADICIONA uma opcao, e o Taumaturgo escolhe **um** implemento
para receber o Adept Benefit. Tratar isso como grant condicional daria os dois
Adept Benefits a um Taumaturgo com dois implementos -- numero errado na ficha,
introduzido por mim.

Contados so os `override`, sem os `Spell Effect:` do wild shape: **44 pares**.

| familia | pares | com `predicate` proprio |
|---|---:|---:|
| Clerigo (6 doutrinas x 2 subclasses) | 12 | 0 |
| Alquimista (`fieldDiscovery`, `greaterFieldDiscovery`, `advancedVials`) | 12 | 0 |
| Gunslinger (`initialDeed`, `slingersReload`) | 10 | 0 |
| Taumaturgo (`initiateBenefit` apenas) | 10 | 10 |

### O que desta spec e realmente necessario

Gunslinger e Taumaturgo tem **via primaria estatica**: a `Way of X` e o
implemento concedem a propria variante por `GrantItem` direto -- com
`predicate` (`class:gunslinger`, `feat:thaumaturge-dedication`), que a spec
`2026-07-31-kind-action.md` passa a traduzir. Para eles o `se` cobre so os
feats leitores (`Slinger's Readiness`, `Practiced Reloads`).

**O nucleo desta spec sao Clerigo 12 + Alquimista 12**, que nao tem via
primaria: a doutrina generica esta na progressao e o mapa vive na subclasse.

O Adept/Paragon do Taumaturgo (`mode: add`) **sai desta spec** e vira spec
propria: e slot de escolha sobre lista acumulada, familia do item 106.

## O vocabulario: `grants[].se`

```json
{"grant_feat": ["wb:class-feature/first-doctrine-cloistered-cleric"],
 "se": {"has": "wb:class-feature/cloistered-cleric"}}
```

`se` guarda predicado da mesma gramatica de `requires`. Ausencia de `se`
significa incondicional, que e o que os grants de hoje sao.

## A regra que faz isto ser seguro: avaliacao estrita

O avaliador tem default permissivo -- termo desconhecido nao reprova. Isso e
certo em `requires`, que so marca; em `se` o mesmo default **concede**, e
conceder as seis doutrinas de uma vez poe numero errado na ficha, calado.

`se` roda em modo estrito, com tres regras:

1. **termo desconhecido** devolve INDECIDIVEL, nao "satisfeito";
2. **chave desconhecida no topo** (`{"and": [...]}` em vez de `all`) tambem
   devolve INDECIDIVEL -- e o defeito exato do item 108, onde o predicado
   inteiro virou no-op em silencio, e o unico jeito de ele nao voltar e
   ser INDECIDIVEL em vez de vazio;
3. **`not(INDECIDIVEL)` = INDECIDIVEL**, nunca `True`. Negacao nao promove
   ignorancia a permissao -- e o mesmo achado do item 106, onde o default
   permissivo se inverte sob `not`/`nor`.

INDECIDIVEL **nao concede e vira pendencia com motivo**. So `False` explicito
descarta em silencio, porque a variante da outra subclasse nao e pendencia: e
escolha que foi para outro lado.

### Portao de build, e nao susto em runtime

O vocabulario aceito em `se` e uma lista fechada, verificada por **portao 11**:
todo `se` da base tem de ser decidivel contra o vocabulario do motor. Assim um
termo novo quebra o BUILD, com nome e registro, em vez de virar pendencia
silenciosa na ficha do jogador. A avaliacao estrita e a rede; o portao e a
barreira.

## Ordem de avaliacao: fila com ponto fixo -- correcao da v1

A v1 afirmava que avaliar `se` dentro de `_grants_em_cadeia` bastava, porque
`self.features` ja estaria montado. **Falso para grant encadeado**: a cadeia
percorre em passada unica sobre um snapshot, entao um `se` que depende do que
outro `se` concede devolve `False` conforme a ordem -- e pela regra 3 acima,
`False` some sem pendencia. O projeto ja foi mordido por ordem duas vezes.

Desenho:

1. os grants com `se` nao sao resolvidos na passada; entram numa **fila**;
2. depois da cadeia, a fila e reavaliada **ate ponto fixo**: cada volta que
   concede alguma coisa habilita a proxima, e o laco para quando uma volta
   inteira nao concede nada;
3. **teto de voltas** igual a `MAX_PROFUNDIDADE_GRANTS`, e estouro e erro de
   build, nao silencio;
4. `INDECIDIVEL` sobrevivente ao ponto fixo vira pendencia -- so ai, nunca
   antes, porque uma volta adiante poderia te-lo decidido.

**Recorte temporal e raiz.** Na cadeia, `_avaliando_em` e `_avaliando` sao
`None`, entao `has` nao recorta por nivel nem exclui a propria raiz. Para `se`
isso e explicitado, e nao herdado por acidente:

- **recorte temporal ligado**: a condicao e avaliada no nivel em que a
  concessao acontece. A doutrina do nivel 3 nao pode ser habilitada por escolha
  feita no 5;
- **exclusao por raiz ligada**: o que o proprio grant concede nao pode
  satisfazer a condicao dele. E a circularidade que o review adversarial de
  27/07 ja achou uma vez, e que a wiki registra.

## O passo do pipeline

`derivar_grant_condicional.py`, depois de `converter_rule_elements.py`:

1. varre `ActiveEffectLike` com `path` em `flags.system.`, **`mode: override`**
   e UUID no `value` -- os 44 pares. `mode: add` e ignorado com contagem no
   relatorio, apontando a spec de slot que o cobre;
2. varre `GrantItem` de escopo `actor` e casa flag com flag;
3. **a chave do par inclui a classe** (`cleric.firstDoctrine`), nunca so o
   sufixo -- `firstDoctrine` de duas classes colidiria;
4. escreve `se: {has: <id da opcao>}` no LEITOR, com alvo resolvido pelo pack
   (`PACK_PARA_KIND`), nunca so por nome;
5. par cujo alvo nao resolve entra no relatorio com nome e pack.

## Como se prova que funciona

1. Clerigo 3 `Cloistered Cleric` tem as duas primeiras doutrinas dele e nenhuma
   do Warpriest; trocada a subclasse, as seis invertem.
2. Alquimista `Bomber` nao recebe `Field Discovery (Chirurgeon)`.
3. **Taumaturgo com DOIS implementos recebe UM Adept Benefit** -- o teste que
   pega a regressao que a v1 teria introduzido. Aqui ele so prova que o
   `mode: add` ficou de fora.
4. **Ponto fixo:** um caso montado de `se` encadeado (A habilita B habilita C)
   converge, e converge igual comecando de qualquer ordem.
5. **Determinismo por ORIGEM:** embaralhar a ordem das ORIGENS da cadeia -- nao
   so das escolhas no documento -- nao muda a ficha. A prova da v1 nao
   exercitava isto.
6. **Estrito:** `se` com termo inventado, com chave desconhecida no topo, e com
   `not` de indecidivel, os tres NAO concedem e viram pendencia com motivo.
7. **Portao 11** falha quando um `se` da base usa termo fora do vocabulario.
8. **Recorte temporal:** escolha de nivel 5 nao habilita concessao de nivel 3.
9. Paridade Python/TS nas 20 fichas; os 11 portoes; verificacao no navegador.

## O que esta spec NAO resolve, e declara

1. **As 206 de escopo `item`** nao se resolvem por `se`. As de identidade e as
   de slot ja estao cobertas; as **class-features sem mecanismo nenhum**
   (impulso do Kineticist, `grantedIkon`, sub-escolha de divindade) ficam como
   divida declarada, com o numero a medir no item 106.
2. **Os 9 backgrounds** viram o item 112. Bug ativo, independente desta spec.
3. **O Adept/Paragon do Taumaturgo** (`mode: add`, 35 regras) sai para spec
   propria de slot sobre lista acumulada.
4. **O Gunslinger rende 0 de 10 hoje**, nao 1 de 10 como a v1 dizia: `Into the
   Fray` casava por homonimo com um feat do arquetipo Viking. Depende da spec
   `2026-07-31-kind-action.md`.
5. **O Campeao nao vem por aqui.** A rota `Cause -> causa` ja e modelada; o que
   prende sao `GrantItem` com `predicate` e as acoes ausentes -- as duas coisas
   estao na spec do kind `action`, onde **26 dos 44 predicados** que apontam
   para acoes se traduzem para `class_level`/`has`. A v1 dizia que `predicate`
   estava inteiramente fora; certo para 18, errado para 26.
6. **Ficha ja salva** nao muda de resultado por esta spec -- ela grava decisao,
   nao resultado. Mas **motor velho com base nova ignoraria `se` e concederia
   tudo**: o `_manifesto.json` passa a declarar a versao de vocabulario, e o app
   recusa base que exija termo que ele nao conhece. Ja houve caso de service
   worker servindo bundle velho.
