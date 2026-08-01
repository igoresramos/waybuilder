---
spec: gate-elemental-do-kineticist
req: WB-061
project: waybuilder
version: 1
status: implementada
created: 2026-07-31
todo: 109
---

# Spec -- o impulso exige o elemento que o jogador abriu

## O maior defeito unico da bancada

Das 314 divergencias contra o Pathbuilder, **24 sao impulsos do Kineticist** --
`Aerial Boomerang`, `Burning Jet`, `Armor in Earth`, `Flashforge`,
`Winter's Clutch` e companhia, todos de *Rage of Elements*. Nos oferecemos, o
Pathbuilder recusa, e ele esta certo.

A causa e uma so: o `requires` de um impulso diz apenas
`class_level: {kineticist: >= 1}`. **Nada exige o elemento.** Um Kineticist de
Ar e Fogo ve os 116 impulsos, inclusive os de Madeira e Metal.

E um defeito, 24 aparicoes -- o que explica boa parte do volume da bancada.

## O que a fonte diz, verbatim

Do dump do AoN (`class.json`, texto da classe):

> **Composite**: A composite impulse combines multiple elements. You can gain an
> impulse with the composite trait only if your kinetic elements include **all**
> the elements listed in the impulse's traits.

Entao a regra nao e "algum elemento": e **todos os listados**.

## O que a base ja tem, medido

| | |
|---|---:|
| feats com trait `impulse` | 116 |
| com exatamente 1 trait de elemento | 95 |
| com 2 (e **todos** carregam o trait `composite`) | 16 |
| sem elemento nenhum | 5 |

Os 16 de dois elementos e os 16 com `composite` sao **o mesmo conjunto** -- nao
ha impulso de dois elementos sem o trait, nem `composite` de um so. A checagem
por trait e a checagem por contagem concordam, entao nao ha ambiguidade a
resolver.

Os 5 sem elemento -- `Command Elemental`, `Counter Element`, `Purify Element`,
`Fearsome Familiar`, `Imperious Aura` -- sao agnosticos por desenho: qualquer
Kineticist os pega. **Ficam intocados**, e e isso que prova que a regra nao e
"gateia tudo".

## O termo: `has`, e nao `subclass`

Medido, com um Kineticist que escolheu Air Gate e Fire Gate:

| termo | air | fire | earth |
|---|---|---|---|
| `{"has": "wb:class-feature/air-gate"}` | **True** | **True** | False |
| `{"subclass": {"kineticist": ...}}` | False | False | False |

`subclass` nao serve porque o eixo `kinetic-gate` e `escolhe: 2`, e o termo foi
desenhado para eixo de escolha unica. `has` responde certo nos tres casos.

## A regra

Para cada feat com trait `impulse` que carregue ao menos um dos seis elementos
(`air`, `earth`, `fire`, `metal`, `water`, `wood`), acrescentar ao `requires`:

```json
{"all": [{"has": "wb:class-feature/air-gate"},
         {"has": "wb:class-feature/fire-gate"}]}
```

um `has` por elemento listado, dentro de `all` -- que e o que "include all the
elements" quer dizer. O `requires` que ja existia entra num `all` junto; nunca
e substituido.

**`all`, e nao `and`.** O avaliador conhece `all`/`any`/`not`, e chave
desconhecida no topo do predicado passa em SILENCIO -- eu ja quebrei dois passos
hoje exatamente assim, e o gate inteiro virava no-op.

## Como se prova que funciona

1. Um Kineticist de **Ar e Fogo** atende `Aerial Boomerang` (air) e
   `Burning Jet` (fire).
2. O mesmo personagem NAO atende `Armor in Earth` nem `Flashforge` (metal), e o
   motivo nomeia o gate que falta.
3. `Ash Strider` (composite air+fire) e atendido por ele; `Desert Wind`
   (composite air+earth) **nao**, porque falta Terra -- e o que prova que
   composite exige TODOS e nao algum.
4. Os 5 agnosticos seguem atendidos por qualquer Kineticist.
5. Nenhuma outra classe muda.
6. Na bancada, os 24 impulsos somem das divergencias.
7. Paridade Python/TS, 10 portoes, oraculo, navegador.
