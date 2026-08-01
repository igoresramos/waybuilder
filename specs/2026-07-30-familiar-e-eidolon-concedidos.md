---
spec: familiar-e-eidolon-concedidos
req: WB-036
project: waybuilder
version: 1
status: implementada
created: 2026-07-30
altera: [WB-002, WB-001]
todo: 43
---

# Spec -- a Bruxa nao tem familiar e o Invocador nao tem eidolon

## O problema

`derivar_concessao_de_ator.py` deriva `grant_actor` da prosa oficial, e resolveu
o companheiro animal: 12 registros passaram a dizer "eu concedo um companheiro".
Mas o regex dele so casa **"animal companion"**.

Medido na base: **0 registros concedem familiar e 0 concedem eidolon.**

Consequencia: um Bruxo nivel 1 -- cuja PRIMEIRA feature de classe se chama
`Familiar (Witch)` -- nao tem familiar nenhum na ficha. Um Invocador nivel 1,
cuja classe inteira gira em torno do eidolon, nao tem eidolon. O ator so entra
por `doc["atores"]` escrito a mao, que e exatamente o buraco que o passo de
companheiro fechou para o outro tipo.

## Quem concede, medido

A ancora e a mesma do companheiro -- **sujeito em "you" e artigo INDEFINIDO** --,
e e ela que separa quem GANHA um familiar de quem fala do familiar que ja tem.
Sem o artigo, o padrao traz 68 registros e a maioria e ruido: as 18 `lesson` e
as 16 `patron` dizem "You gain the X hex, **and your familiar learns** Y", que
pressupoe o familiar em vez de conceder.

| rota | quantos | exemplos |
|---|---:|---|
| feat com "you gain a familiar" | **15** | `familiar`, `animal-accomplice`, `alchemical-familiar`, `leshy-familiar`, `crocodiles-twin`, `familiar-master-dedication` |
| feat com "you gain an eidolon" | **1** | `summoner-dedication` |
| progressao de classe | **2** | Bruxa nivel 1 -> `class-feature/familiar-witch`; Invocador nivel 1 -> `class-feature/eidolon` |

Os dois falsos positivos do eidolon (`wb:class/summoner` e
`wb:class-feature/evolution-feat`) dizem "You gain an **evolution feat** for your
eidolon" -- concedem FEAT, nao ator, e caem fora pela mesma ancora.

## A rota da classe nao e prosa

Bruxa e Invocador nao dizem "you gain a familiar" em lugar nenhum: eles
**concedem uma class-feature** que se chama Familiar e Eidolon, e a progressao ja
esta estruturada. Entao essa rota nao passa por regex: sai de
`class.progressao`, casando o `concede` contra os dois ids conhecidos. Dado
estruturado tem precedencia sobre prosa em todo o resto do pipeline, e aqui
tambem.

## O que esta spec NAO resolve, e declara com o motivo

**O bloco de estatisticas do familiar e do eidolon nao existe nas nossas
fontes.** Procurado:

- `wb:familiar-specific` (39 registros) tem `required_abilities` e
  `concede_habilidades` e **zero campo numerico** -- nem HP, nem CA, nem
  percepcao, nem ataque.
- `wb:eidolon` (13) tem `stats` com tradicao, plano natal, sentidos, pericias e
  ataques sugeridos; o unico numero real e `velocidade`.
- A pagina de regras `Familiars` do AoN (Core Rulebook pg. 217) tem 796
  caracteres e descreve o CONCEITO: "A familiar has the same level you do",
  "minion trait", "only one familiar at a time". A secao com os numeros nao
  esta no dump.
- Nao existe tabela de progressao: "quantas habilidades de familiar por nivel"
  vive so como prosa dentro de `class-feature/familiar-witch`.

Isso e coerente com o jogo -- em PF2e o familiar deriva os numeros do
personagem, e o eidolon tambem --, mas **derivar sem a regra na mao seria
inventar**, e este projeto nao inventa numero. A ficha do ator continua entrando
sem stat block, que e o que o tipo `Ator` ja declara em `tipos.ts`. O stat block
e item proprio, e comeca por conseguir a fonte.

Tambem ficam de fora:

- **A tese `Improved Familiar Attunement` do Mago**, que altera o familiar em
  vez de conceder um: a prosa comeca em "Your connection with your familiar",
  pressupondo. Se o Mago ganha familiar por outra rota, e medicao propria.
- **O teto de um familiar por vez** ("You can have only one familiar at a
  time"). E regra de validacao, nao de concessao, e vale junto com a regra 23.

## Como se prova que funciona

1. Os registros que concedem familiar sobem de **0 para 16** e os que concedem
   eidolon, de **0 para 2**.
2. Um Bruxo nivel 1 tem um ator do tipo `familiar` na ficha; hoje tem zero.
3. Um Invocador nivel 1 tem um ator do tipo `eidolon`.
4. `Lesson of Calamity` e `Faith's Flamekeeper` NAO concedem nada -- o artigo
   indefinido e quem os derruba, e o relatorio mostra a contagem.
5. `evolution-feat` nao concede eidolon.
6. O passo e idempotente: rodar duas vezes nao duplica.
7. Quatro camadas verdes e os 10 portoes.
