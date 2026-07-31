---
spec: variante-por-subclasse
project: waybuilder
version: 1
status: aprovada
created: 2026-07-31
todo: 69
---

# Spec -- a variante que o parentese ja nomeia

## O que sobrou no balaio depois da spec anterior

Nomear o balaio por tag tirou 91 das 202. Das 111 que ficaram, **68 sao
variante por subclasse**: o nome termina num parentese que casa **exatamente** o
nome de uma opcao de subclasse da propria classe.

| classe | familia | variantes |
|---|---|---:|
| Alchemist | `Field Discovery (Bomber\|Chirurgeon\|Mutagenist\|Toxicologist)` | 4 |
| Alchemist | `Perpetual Infusions`, `Perpetual Potency`, `Greater Field Discovery`, `Perpetual Perfection`, `Advanced Vials` | 4 cada |
| Thaumaturge | `Initiate Benefit (Amulet\|Bell\|Chalice\|Lantern\|Mirror\|Regalia\|Shield\|Tome\|Wand\|Weapon)` | 10 |
| Cleric | `Final Doctrine (Warpriest)` e irmas | -- |

**Nao ha o que escolher.** Um Alquimista que ja escolheu Bomber recebe
`Field Discovery (Bomber)`; as outras tres nao sao opcao dele. Hoje o app
oferece as quatro lado a lado, sem distincao, e um Bomber pode escolher a do
Chirurgeon.

## A medicao que decide o desenho

**Nenhuma das 68 e concedida pelo dono**: `wb:class-feature/bomber` tem
`grants: []`. Entao tira-las do balaio as tornaria INALCANCAVEIS, que e a
familia do item 97 e o oposto do principio zero.

O caminho e o que ja esta provado em 281 registros -- o termo `subclass`,
nascido na spec do Inventor:

```json
"requires": {"subclass": {"alchemist": "wb:class-feature/bomber"}}
```

A opcao continua na lista e passa a vir **MARCADA** para quem escolheu outro
campo de pesquisa, com o motivo escrito. Filtrar e marcar, nunca esconder.

## A regra

Para cada opcao de balaio cujo nome termine em `(S)`, onde `S` e **exatamente**
o nome de uma opcao de subclasse da mesma classe: acrescentar
`requires: {subclass: {<slug da classe>: <id daquela opcao>}}`.

Tres guardas, todas por medicao e nao por gosto:

1. **Casamento exato de nome**, sem normalizacao esperta. `(Level 13)` nao e
   subclasse e nao casa; `(Sorcerer)` nao e opcao de subclasse do Feiticeiro e
   nao casa.
2. **Dono unico.** Se o parentese casar opcao de mais de um eixo da classe, nao
   gateia -- e a licao do `initial-modification` do Inventor, que tem quatro
   donos e cujo gate no bloco fazia o eixo sumir para quem escolheu outro.
3. **Nao mexe em quem ja tem `requires`.** Se a opcao ja carrega requisito, o
   novo termo entra num `and` com o que existia; nunca substitui.

## O que esta spec NAO resolve, e declara

- Os **~30 pais genericos** (`Perpetual Infusions` sem parentese, ao lado dos
  quatro `(X)`) continuam no balaio. Eles nao tem parentese e nao ha regra que
  os explique sem inventar; e a cauda do item 69.
- As opcoes seguem sendo **escolha marcada** e nao concessao automatica. O
  modelo certo seria o dono CONCEDER a variante, e isso pede vocabulario novo de
  grant (`concede feature no nivel N`) que hoje nao existe -- mudanca de motor,
  TS e tela. Fica registrado como o passo seguinte, com o numero: 68.

## Como se prova que funciona

1. As 68 ganham `requires.subclass`, com `prov` dizendo de onde veio.
2. Um Alquimista **Bomber** atende `Field Discovery (Bomber)` e NAO atende as
   outras tres -- e o motivo nomeia o campo de pesquisa que falta.
3. As tres continuam na lista, marcadas. Nenhuma some.
4. Um Alquimista que ainda nao escolheu campo nao atende nenhuma das quatro, e
   tambem nao e reprovado por engano em outra coisa.
5. Nenhuma opcao sem parentese casando subclasse e tocada.
6. Paridade Python/TS, diff de fixture LIDO, 10 portoes, navegador.
