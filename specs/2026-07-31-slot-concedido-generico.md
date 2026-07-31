---
spec: slot-concedido-generico
project: waybuilder
version: 1
status: aprovada
created: 2026-07-31
todo: 106
---

# Spec -- o slot concedido para de ser so de feat

## A regra, numa frase

**Todo `grants.choice` que declara `tipo` e `filtro` abre um slot.** O `filtro`
define o pool, a `flag` da identidade ao slot, o nivel do concessor da o `em`, e
o `tipo` e rotulo.

Hoje a linha que impede isso e uma so:

```python
if not isinstance(ch, dict) or ch.get("tipo") != "feat":
    continue
```

## Por que generico, e nao um ramo para magia

Foi decisao do Igor, e o Pathbuilder concorda. O painel de nivel dele nao separa
mecanismo de feat de mecanismo de magia -- e **uma lista de pendencias por
nivel**, cada uma com contagem, rotulo e valor:

```
Level 1
  4  Set Abilities
  3  Skill Training
  1  Class Skill
     Heritage        Not Selected
     Ancestry Feat   Not Selected
     Class Feat      Not Selected
```

Heranca e treino de pericia entram na mesma lista que Class Feat. E a estrutura
que o Waybuilder ja tem: `abertos` empurra `{slot, em, kind, escolhe, flag,
rotulo}` e a tela renderiza generico. Faltava so parar de filtrar por `feat`.

## O universo, medido

| `tipo` | blocos | com filtro | com `opcoes` |
|---|---:|---:|---:|
| feat | 43 | 43 | 0 |
| spell | 11 | 11 | 0 |
| heritage | 7 | 7 | 0 |
| action | 4 | 4 | 0 |
| weapon | 2 | 2 | 0 |
| ancestry | 1 | 1 | 0 |
| deity | 1 | 1 | 0 |

**69 blocos, todos com filtro e nenhum com lista solta.** A regra cobre os 69
sem excecao.

O que os 11 de magia entregam, resolvido contra a base:

| concessor | opcoes |
|---|---:|
| `wb:heritage/makari-lizardfolk` | 2 |
| `wb:feat/dragon-spit` | 4 |
| `celestial-magic`, `fiendish-magic`, `hag-magic`, `methodical-magic` | 6 |
| `wb:feat/arcane-tattoos` | 7 |
| `wb:heritage/born-of-elements` | 8 |
| `wb:feat/parallel-breakthrough` | 30 |
| `wb:feat/diverse-mystery` | 37 |
| `wb:feat/merge-with-the-source` | 6, aninhado |

`Dragon Spit` da 4 e nao 5 porque o filtro cita `produce-flame` E `ignition`,
que sao a mesma magia (nome pre-remaster e remaster) -- o alias colapsa sozinho,
sem regra nova.

## A decisao de desenho: quem define o pool e o FILTRO

Nao o `tipo`. Os 4 blocos de `action` sao taticas do Commander e **nao existe
`kind: action` na base** -- mas o filtro (`item:trait:tactic` + as tags de
`commander-*-tactic`) ja as alcanca, pelo mesmo `_casa_filtro` que os eixos do
Commander usam desde 31/07. Amarrar o pool ao `kind` obrigaria a inventar um
kind fantasma so para satisfazer o rotulo.

Entao: pool = todo registro da base que casa o filtro. O `tipo` vira `kind` no
slot aberto, para a tela saber o que esta pedindo.

## `item:slug` deixa de ser codigo morto

Ele foi declarado sem consumidor em `specs/2026-07-31-atomo-slug.md`, e com esta
spec passa a ser **requisito**: 60 dos 69 atomos vivem justamente nos filtros de
`tipo: spell`, e atomo ignorado conta como SATISFEITO. Sem implementa-lo, o slot
de `Dragon Spit` ofereceria as 1.638 magias da base em vez de 4.

E o mesmo par de causa e efeito do `item:tag` em 31/07: o vocabulario entra
junto com quem o consome, nunca antes.

## O nome do slot NAO muda

O slot continua se chamando `feat_concedido` no documento do personagem, mesmo
carregando magia. Renomear obrigaria a migrar documentos salvos, fixtures e
fichas de exemplo, e o unico ganho seria estetico -- o `kind` do slot ja diz o
que ele pede, e o `rotulo` e o que o jogador le. Fica registrado como divida de
nome, nao de comportamento.

## O que esta spec NAO resolve, e declara com numero

- **25 blocos sem `tipo` na fonte nenhuma** (`Assurance`, as dedicacoes de
  multiclasse, `basic-lesson`...). Sem `itemType` no Foundry, o pool nao e
  derivavel por regra; cada um precisa de resposta propria. Nao entram.
- **3 registros TEM `itemType` no Foundry e o nosso extrator descartou**
  (`multifarious-muse` e `skill-mastery` com `feat`, `verdant-weapon` com
  `weapon`). E lacuna de leitura, conserto de pipeline, e sai em item proprio --
  esta spec so mexe em motor.
- **155 blocos com `opcoes` inline** e outra familia, ja resolvida pela spec de
  escolha aninhada do Inventor.
- **A conjuracao do personagem** (os 5 truques do Mago, os slots por rank)
  segue como CAPACIDADE, sem lista de magias. A assimetria e consciente: o app
  modela o que a fonte declara como escolha discreta, e a Paizo declara estes 11
  e nao os outros.

## Como se prova que funciona

1. Um Yaoguai de heranca `Born of Elements` ganha um slot de magia com **8**
   opcoes -- hoje nao ganha slot nenhum.
2. Um personagem com `Dragon Spit` ganha um slot com **4**, e nao com 1.638 --
   e o que prova que `item:slug` esta sendo avaliado.
3. Um Commander com `Tactical Excellence` ganha slot de tatica.
4. O slot de feat concedido continua identico ao que era: mesmo `em`, mesma
   `flag`, mesmo pool. Nenhuma ficha de exemplo muda de veredito.
5. A escolha feita fica gravada e o slot some da lista de pendencias.
6. Paridade Python/TS, diff de fixture LIDO.
7. `npm run build`, oraculo, 10 portoes e navegador verdes.
