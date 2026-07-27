# Waybuilder

Construtor de personagem de Pathfinder 2e com multiclasse ao estilo D&D 5e.
Piada com o Pathbuilder 2e, e eco do Wayfinder, a bussola da Pathfinder Society.

**Este arquivo e o ponto de retomada.** Comece por aqui em qualquer sessao nova.

---

## O que e, em uma frase

Um JSON e a ficha. Um front edita esse JSON. Nao ha servidor, nao ha mecanica de
jogo rodando -- e um construtor, nao um sistema.

## Os quatro principios que governam tudo

1. **Nao e um sistema de jogo.** `requires` sugere e ordena, **nunca bloqueia**.
   Quem quiser pegar algo fora do requisito, pega, e o app mostra que esta fora.
2. **O flavor nao se perde.** Texto narrativo, pre-requisito em prosa,
   condicao de ficcao -- tudo fica, tudo e legivel, nada disso filtra.
3. **Guardar decisao, nao resultado.** A ficha grava escolhas; o resto e
   derivado. Regra que muda re-deriva em vez de invalidar.
4. **Nada e descartado.** Conteudo cortado pela Paizo (alinhamento, Legacy sem
   sucessor) fica na base. Renomeado vira um registro so, com os dois nomes.

## O que ja esta decidido, e onde

| Assunto | Documento |
|---|---|
| As 22 regras de multiclasse | `specs/2026-07-26-regras-multiclasse.md` |
| Schema da base canonica | `specs/2026-07-26-schema-base.md` |
| Schema do documento de personagem | `specs/2026-07-26-schema-personagem.md` |
| Armadilhas tecnicas ja pagas | `LESSONS.md` |
| Historico de sessao | `LOG.md` |

**Nao redecida o que ja esta nesses arquivos sem ler o "por que" junto.** Quase
toda regra tem um bloco de citacao explicando o que foi medido para chegar nela.

## Estado do pipeline

```
pipeline/
  buscar_fontes.sh      reconstroi o clone do Foundry no pin (615 MB, fora do git)
  dump_aon.py           baixa o indice `aon` inteiro -- 43.686 docs, 93 categorias
  dados_brutos/         fontes fixadas (fora do git, reconstruiveis pelos dois acima)
  extratores/           um por familia de entidade
  reconciliar.py        funde colisoes de id, traits como uniao, canoniza livro
  auditar_conflitos.py  compara a base contra AoN e Foundry em disco
  desmembrar_colisoes.py  separa entidades distintas que caíram no mesmo slug
  emitir_textos.py      resolve a prosa
  fundir_renomeados.py  une Legacy<->Remaster pelo remaster_id do AoN
  portoes.py            os 7 portoes de qualidade
  build.sh              roda tudo na ordem certa
  saida/                saida crua de cada extrator
  base/                 a base canonica -- index.json + text/ + relatorios
```

**Rode `./build.sh`.** A ordem nao e obvia e ja foi errada: `emitir_textos` roda
**antes** de `fundir_renomeados` (a fusao usa prosa para desempatar sucessor
multiplo -- fora de ordem, o desempate acontece com prosa vazia, em silencio), e
o portao 7 roda **antes** da fusao.

Para re-extrair das fontes: `WB_REEXTRAIR=1 ./build.sh`.

## Estado da base (2026-07-26, apos a re-emissao)

**19.250 registros em 24 kinds.** Prosa em **99,2%** (169 sem prosa), 951 com
divergencia registrada, 350 com alias, 1.459 com `aliases_traits`, 281
desmembrados de colisao de identidade.

Os cinco defeitos da auditoria de 26/07 estao **resolvidos**:

1. **Fusao Legacy<->Remaster** refeita pelo `remaster_id`/`legacy_id` do AoN.
   Prosa nao cria mais par -- so desempata sucessor multiplo --, e campo
   estruturado divergente veta a fusao. `aeon-stone` voltou de 17 para 40
   registros; `Poi` e `Tonfa` voltaram a existir; **586 registros deletados pela
   fusao por prosa foram recuperados**.
2. **`traits` e uniao.** `bastard-sword` voltou a `two-hand-d12`;
   `absorb-strength` virou `kholo` com `aliases_traits: [gnoll]`. Conflitos
   cairam de 2.299 para 209 e `traits` saiu da lista de campos em disputa.
3. **Colisao de identidade:** 318 irmaos criados. `death-from-above` agora e
   nv16 mythic + `death-from-above-archetype` nv8, batendo com o AoN. 13 casos
   ambiguos ficaram marcados `REVISAR`, sem arbitrar.
4. **Kinds que faltavam:** `ritual` (151), `relic` (122), `language` (123), e
   `background` foi de 332 para 502 -- faltavam 168, quase todos de Player's
   Guide de Adventure Path.
5. **Os 7 portoes implementados.** O 1 foi de 2.694 falhas a zero. O 7 foi
   **reescrito**: a versao da spec nunca dispararia, porque a ambiguidade nao
   produz dois registros -- o extrator casa por nome, escolhe um candidato entre
   os N da fonte e os outros somem sem rastro.

### O que ainda falha, e por que

| Portao | Falhas | Causa |
|---|---|---|
| 3 -- `requires` orfao | 80 | citam class-features de **segundo nivel** (`enigma-muse`, `ruffian-racket`, `universalist-wizard`) que a base nunca extraiu. Fecha junto com o item 2 |
| 5 -- sem `license` | 3 | `heavy-power-suit`, `nine-ring-sword`, `wind-and-fire-wheel`: vieram de consulta ao vivo ao pf2etools numa sessao antiga e **nao existem em fonte nenhuma em disco**. Precisam de decisao |
| 7 -- homonimo | 13 | casaram com doc do AoN que nao representa nenhum grupo; desmembrar exigiria arbitrar |

> **Correcao a spec, verificada contra as fontes:** ela dizia que em
> `Death from Above` "o Foundry separa os dois; o AoN indexa so o mitico". E o
> contrario nos dois lados -- o Foundry tem **um** (nv8, archetype) e o AoN tem
> **dois**. O defeito nunca foi fusao de duplicatas; foi **casamento ambiguo**,
> escolhendo 1 entre N candidatos em silencio.

## As tres fontes, e o que cada uma serve

| Fonte | Serve para | Pin |
|---|---|---|
| `foundryvtt/pf2e` | mecanica executavel, progressao, ranks numericos | commit `87f9e5028baaa10b70fdc766260b7886def17e04` |
| `Pf2eToolsOrg/Pf2eTools` | pre-requisito com referencias marcadas | branch `dev`, snapshot datado |
| Archives of Nethys | texto, cobertura, ponte legado/remaster | dump do Elasticsearch `aon` |

Cuidado: **`Pf2ools` sem o "e" e um repo morto.** A fonte viva e `Pf2eToolsOrg`.

## O que falta

O bloco de re-emissao fechou. O que resta esta em `TODO.md`; os tres primeiros:

1. **Grafo de progressao de dois niveis** -- 62 class-features de segundo nivel
   (teses do Mago, ordens Hellknight, ikons do Exemplar, gates do Kineticist)
   ficam invisiveis modelando so `classe -> feature`.
   > O portao 3 aponta exatamente para ca: 80 `requires` ja citam essas
   > entidades. E o AoN **ja as categoriza**, uma categoria por eixo --
   > `arcane-thesis` (10), `muse` (9), `racket` (10), `instinct` (16),
   > `doctrine` (5), `research-field` (8), `hellknight-order` (14), `ikon` (21),
   > `bloodline` (28), `mystery` (22), `way` (11), `patron` (27)... Todas ja
   > estao em `dados_brutos/aon_dump/`. `extratores/aon_kinds.py` extrai
   > categoria do AoN de forma generica -- e o caminho mais curto.
2. **Predicado precisa falar de SUBCLASSE** -- a proficiencia de conjuracao do
   Clerigo depende da Doutrina, e o nivel do companheiro e o `class_level` de
   quem o concedeu. Nenhum dos dois cabe em `class_level` puro
3. **O front**

## Simulacoes

`docs/simulacoes/` guarda o simulador de balanceamento e o benchmark de 3.624
criaturas do AoN (mediana de AC/HP/save/ataque/dano por nivel). Foi o que
calibrou a regra de elevacao de magia. Rodar so depois da base fechar.

## Referencia externa

`docs/referencia/pathbuilder_export_exemplo.json` -- export real do Pathbuilder
2e, personagem deliberadamente complexo (Ranger + Summoner Dedication, dois
animal companions, um familiar, um eidolon). E o alvo de interoperabilidade e
tambem a prova de um buraco deles: o eidolon nao existe como estrutura.
