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

**Numeros atuais:** **18.176 registros em 21 kinds**, prosa em 100% (17.866/17.866),
2.299 com divergencia registrada, 359 com alias. Index 15,2 MB + prosa 16,7 MB.
Residuo: 6 registros sem `license`.

**A base precisa ser re-emitida antes de se construir por cima dela.** A revisao
de 26/07 achou tres defeitos no dado ja emitido -- `traits` usando precedencia
em vez de uniao, colisao de identidade por slug, e o kind `ritual` ausente. Os
tres estao corrigidos na spec e nos insumos (`pipeline/normalizacao_traits.json`,
`pipeline/saida/rituais.json`), mas **o pipeline ainda nao rodou de novo**.
Detalhe em `TODO.md` itens 17, 20 e 21, e nas secoes novas do `LESSONS.md`.

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

Ja resolvido nesta sessao: reextracao das class-features sob o schema corrigido,
e a tabela de slots de conjuracao (10 de 11 classes; Animist nao existe em fonte
nenhuma).

## Simulacoes

`docs/simulacoes/` guarda o simulador de balanceamento e o benchmark de 3.624
criaturas do AoN (mediana de AC/HP/save/ataque/dano por nivel). Foi o que
calibrou a regra de elevacao de magia. Rodar so depois da base fechar.

## Referencia externa

`docs/referencia/pathbuilder_export_exemplo.json` -- export real do Pathbuilder
2e, personagem deliberadamente complexo (Ranger + Summoner Dedication, dois
animal companions, um familiar, um eidolon). E o alvo de interoperabilidade e
tambem a prova de um buraco deles: o eidolon nao existe como estrutura.
