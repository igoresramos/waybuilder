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
  dados_derivados/      artefato lido/arbitrado a mao -- VERSIONADO, ver o README de la
  artefatos_perdidos.json  registro de perda conhecida, consultado pelo portao 8
  extratores/           um por familia de entidade
  reconciliar.py        funde colisoes de id, traits como uniao, canoniza livro
  auditar_conflitos.py  compara a base contra AoN e Foundry em disco
  desmembrar_colisoes.py  separa entidades distintas que caíram no mesmo slug
  emitir_textos.py      resolve a prosa
  fundir_renomeados.py  une Legacy<->Remaster pelo remaster_id do AoN
  portoes.py            os 8 portoes de qualidade
  build.sh              roda tudo na ordem certa
  saida/                saida crua de cada extrator
  base/                 a base canonica -- index.json + text/ + relatorios
```

**Rode `./build.sh`.** A ordem nao e obvia e ja foi errada: `emitir_textos` roda
**antes** de `fundir_renomeados` (a fusao usa prosa para desempatar sucessor
multiplo -- fora de ordem, o desempate acontece com prosa vazia, em silencio), e
o portao 7 roda **antes** da fusao.

Para re-extrair das fontes: `WB_REEXTRAIR=1 ./build.sh`.

## Estado da base (2026-07-27)

**19.738 registros em 52 kinds** (24 originais + 28 eixos de sub-escolha
promovidos a kind proprio pelo item 2 do TODO). Prosa em **99,2%**. Portoes 1,
2, 4 e 5 passam; o 3 esta em 23 (era 80) e o 6 em 1.

Alem da re-emissao, esta camada foi construida depois: gate de nivel derivado
(`class_level` em 1.932 registros, era 79), `subclass` no predicado, efeito
unificado em `grants` e 422 registros com efeito vindo dos Rule Elements do
Foundry.

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
| 3 -- `requires` orfao | 23 (era 80) | vocabulario nao unificado, nao falta de conteudo. `resolver_referencias.py` casou 58 por nome |
| 6 -- traits disjunto | 1 | resto de conflito de traits |
| 7 -- homonimo | 13 | casaram com doc do AoN que nao representa nenhum grupo; desmembrar exigiria arbitrar |

O **portao 8** passa, com 4 perdas conhecidas registradas em
`pipeline/artefatos_perdidos.json`. Ele nasceu de uma perda real: a tabela de
conjuracao do Animist, lida a olho de um PDF imagem-only, foi gravada em
`dados_brutos/` -- que o `.gitignore` exclui alegando "reconstruivel pelos
pins" -- e sumiu sem nada reclamar. Ver a licao em `LESSONS.md` e o item 14.

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

## O motor ja monta ficha

```
motor/
  motor.py            documento de personagem -> visao calculada
  ficha.py            imprime a ficha            (python3 ficha.py)
  teste_motor.py      assercoes, uma por regra   (python3 teste_motor.py)
  validar_iconics.py  confere contra os personagens oficiais da Paizo
  simular_raw.py      2.000 personagens RAW, invariantes vs tabela do Foundry
  exemplos/guerreiro3-mago2.json
```

**Tres niveis de verificacao, e cada um pega coisa que os outros nao pegam:**

| | o que faz | estado |
|---|---|---|
| `teste_motor.py` | trava cada regra da spec | todas passam |
| `validar_iconics.py` | compara com os iconics da Paizo (Valeros, Ezren...) | **117/129 (91%)** |
| `simular_raw.py` | invariantes sobre 2.000 personagens de classe unica | 1 violacao conhecida (item 39) |

A logica do segundo: a houserule so diverge do RAW quando ha mais de uma classe,
entao **classe unica tem que bater exatamente com o oficial**. Se nao bate, o
motor esta errado -- sem discussao de balanceamento.

Fatia vertical 1 fechada: `Guerreiro 3 / Mago 2` sai completo -- HP decomposto
por nivel, proficiencias com origem, identidade de classe, slots de escolha,
conjuracao e DC. 11 das 22 regras implementadas (as que cabem em niveis 1-5).

A ficha traz HP decomposto por nivel, AC (com cap de DEX, escudo e penalidade de
armadura), ataque e dano por arma equipada, proficiencias com origem, identidade
de classe, slots, conjuracao e a lista do que o personagem pode pegar.

A houserule aparece viva na ficha:

```
Wizard 2  --  arcane, prepared
  Slots                  rank 1: 3          <- nivel de CLASSE (regra 16)
  Rank maximo do slot    1
  Rank efetivo           3   (ceil(5/2))    <- nivel de PERSONAGEM (regra 17)
  Elevacao ganha         +2 rank(s)
```

Mago 5 puro ganha elevacao **zero** -- a regra so age onde os dois numeros
divergem, que e exatamente o ponto.

## O que falta

O bloco de re-emissao fechou. O que resta esta em `TODO.md`; os quatro
primeiros:

1. **Atores** -- companheiro, familiar e eidolon com stats proprios. A spec
   diz que e o mesmo motor com menos slots; hoje o motor so verifica que
   existem.
2. **Runas** -- potencia e impacto (`+1 striking longsword`). O campo
   `potencia` ja e lido; falta modelar runa como item.
3. **Interpretador parcial de Rule Elements** -- para o dano condicional das
   subclasses (itens 42 e 43 do TODO). Deixou de ser "fora de escopo" depois
   da correcao de escopo do Igor em 2026-07-27: dano de rage e numero de
   ficha.
4. **O front** -- PWA client-side, offline, sem backend.

## Simulacoes

`docs/simulacoes/` guarda o simulador de balanceamento e o benchmark de 3.624
criaturas do AoN (mediana de AC/HP/save/ataque/dano por nivel). Foi o que
calibrou a regra de elevacao de magia. Rodar so depois da base fechar.

## Referencia externa

`docs/referencia/pathbuilder_export_exemplo.json` -- export real do Pathbuilder
2e, personagem deliberadamente complexo (Ranger + Summoner Dedication, dois
animal companions, um familiar, um eidolon). E o alvo de interoperabilidade e
tambem a prova de um buraco deles: o eidolon nao existe como estrutura.
