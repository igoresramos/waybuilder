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
  dados_brutos/     dumps fixados das 3 fontes (fora do git, reconstruivel)
  extratores/       um por familia de entidade
  reconciliar.py    funde colisoes de id, registra divergencia
  emitir_textos.py  resolve a prosa
  fundir_renomeados.py  une Legacy<->Remaster por similaridade de texto
  saida/            saida crua de cada extrator
  base/             a base canonica -- index.json + text/ + relatorios
```

Ordem de execucao: extratores -> `reconciliar` -> `emitir_textos` -> `fundir_renomeados`.

## A base foi re-emitida em 27/07 e os portoes passam

O dano que a auditoria de 26/07 achou (`docs/2026-07-26_auditoria-ampla.md`)
foi corrigido e **medido**. Relatorio de verificacao:
`docs/2026-07-27_reemissao-base.md`.

**Numeros atuais:** 19.418 registros em 24 kinds, **prosa em 99,1%**, 2.867 com
divergencia registrada, 646 com `superseded_by` (nenhum registro deletado).
Index 20,9 MB + prosa 17,9 MB.

| defeito da v1 | estado |
|---|---|
| fusao por prosa deletou 597 registros, 35% corretas | chave da fonte (`remaster_id`), **12/12** corretas na amostra, **nada deletado** |
| `traits` por precedencia destruia o dado parametrizado | uniao: `two-hand-d12` de 2 para 10 registros |
| `wb:<kind>/<slug>` fundia homonimos numa quimera | curadoria por `xref` + dois detectores (traits disjuntos e salto de nivel) |
| faltavam `ritual`, `relic`, `language`; `background` -167 | 151 / 122 / 117 / 514 |
| 1 dos 7 portoes implementado | **10 portoes, todos passando** |

O que sobrou esta no `TODO.md` (itens 35-41), cada um com o numero que o
sustenta. Nenhum e bloqueante para o construtor.

**Ordem de execucao:** `python3 pipeline/rodar.py` -- extratores, reconciliar,
prosa, fusao e portoes, na unica ordem em que funciona. `--sem-extratores`
pula a parte cara.

## As tres fontes, e o que cada uma serve

| Fonte | Serve para | Pin |
|---|---|---|
| `foundryvtt/pf2e` | mecanica executavel, progressao, ranks numericos | commit `87f9e5028baaa10b70fdc766260b7886def17e04` |
| `Pf2eToolsOrg/Pf2eTools` | pre-requisito com referencias marcadas | branch `dev`, snapshot datado |
| Archives of Nethys | texto, cobertura, ponte legado/remaster | dump do Elasticsearch `aon` |

Cuidado: **`Pf2ools` sem o "e" e um repo morto.** A fonte viva e `Pf2eToolsOrg`.

## O que falta

A **base fechou**. O que resta esta detalhado em `TODO.md`; os tres primeiros:

1. **Grafo de progressao de dois niveis** -- 62 class-features de segundo nivel
   (teses do Mago, ordens Hellknight, ikons do Exemplar, gates do Kineticist)
   ficam invisiveis modelando so `classe -> feature`
2. **Predicado precisa falar de SUBCLASSE** -- a proficiencia de conjuracao do
   Clerigo depende da Doutrina, e o nivel do companheiro e o `class_level` de
   quem o concedeu. Nenhum dos dois cabe em `class_level` puro
3. **O front**

## Simulacoes

`docs/simulacoes/` guarda o simulador, o benchmark de 3.624 criaturas do AoN e
a matriz completa. Rodada de 27/07 (`2026-07-27_balanceamento.md`), niveis
1-15, HOUSE vs RAW vs RAW+Free Archetype, combate e nao-combate:

- **A houserule nao quebra o jogo.** HOUSE nunca supera os dois pais puros ao
  mesmo tempo em combate, exceto em 2 de 160 configuracoes -- as duas em
  Monge/Clerigo, com causa identificada na regra 17.
- **Fora do combate ela entrega o que prometia**: +0,62 pilar de 8 sobre o
  melhor pai puro, e **nenhum caso medido de perda**.
- **A regra 21 tem uma fresta estreita**: dip de 1 nivel em classe de d6 PV
  perde vida que a dedicacao do Free Archetype nao perde (14 de 63
  comparacoes, concentradas nos niveis 3-5).

Os dois pontos viraram itens 43 e 44 do TODO -- candidatos a playtest, nao
mudanca de regra.

## Referencia externa

`docs/referencia/pathbuilder_export_exemplo.json` -- export real do Pathbuilder
2e, personagem deliberadamente complexo (Ranger + Summoner Dedication, dois
animal companions, um familiar, um eidolon). E o alvo de interoperabilidade e
tambem a prova de um buraco deles: o eidolon nao existe como estrutura.
