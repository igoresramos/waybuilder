---
spec: companheiro-concedido
req: WB-010
project: waybuilder
version: 1
status: implementada
created: 2026-07-29
altera: [WB-002, WB-003]
todo: 43
---

# Spec -- companheiro concedido por feat

## O problema, corrigido

A leitura anterior era "falta modelar companheiro no motor". **E falsa.** O
motor implementa companheiro inteiro, nos dois lados:

| ja existe | Python | TypeScript |
|---|---|---|
| cap de nivel (regra 17b) | `cap_ator` | `cap_ator` |
| maturidade young/mature/nimble/savage | `_maturidade_do_companheiro` | idem |
| Specialized Companion | `SPECIALIZADO` | idem |
| ficha completa (HP, AC, saves, ataques, support) | `_ficha_de_companheiro` | idem |

O buraco e outro, e menor: **o ator so entra por `doc["atores"]`, escrito a
mao.** Nenhum feat cria um. Quem pega `Animal Companion` no nivel 1 nao ganha
nada -- a ficha nao muda, o app nao pergunta a especie, e nao ha aviso.

O campo `concedido_por` ja existe no ator desde o desenho original. Esta spec e
ligar as pontas que ele previa.

## O que entra no escopo

**So companheiro animal.** Sao 12 concessores medidos na prosa oficial da base
(a busca completa esta em "Levantamento", abaixo). Familiar, eidolon,
companheiro construct e companheiro undead ficam de fora **e sao declarados
como divida** -- cada um tem stat block de forma diferente e um deles
(construct) nem tem stat block na base.

## Parte 1 -- dado: o termo `grant_actor`

Vocabulario novo em `grants`. Hoje sao 47 termos e nenhum concede ator:

```json
{"grant_actor": {"tipo": "companheiro", "escolhe": "animal-companion"}}
```

| campo | valor | por que |
|---|---|---|
| `tipo` | `companheiro` | mesmo vocabulario de `doc["atores"][].tipo` |
| `escolhe` | kind da base que povoa os candidatos | o motor nao precisa de lista escrita a mao |
| `opcoes` | lista de ids (opcional) | quando o feat restringe a especie |

`opcoes` existe porque dois dos doze restringem:

- **Rough Rider** -- "you gain a wolf as an animal companion": opcao unica.
- **Drake Rider Dedication** -- "riding drake, riding dragonet, or another
  animal companion": ordena os dois na frente, nao filtra. Principio zero.

`escolhe` e `opcoes` convivem: `opcoes` ordena, `escolhe` define o conjunto.

### De onde vem o dado

Passo novo do pipeline, `derivar_concessao_de_ator.py`, rodando em **7f** --
depois da prosa (5), depois da fusao (7), ao lado de
`derivar_mecanica_dedicacao.py` (7e), pela mesma razao registrada em
LESSONS.md: passo que enriquece nao pode rodar antes do passo que reescreve.

Regra de emissao, igual a do 7e: **so emite com sujeito ancorado em "you"**.

    you gain the service of a young animal companion     -> concede
    you gain a young animal companion                    -> concede
    you gain a wolf as an animal companion               -> concede, opcao fixa
    your animal companion gains ...                      -> NAO concede
    you can never take a feat that grants an animal companion -> NAO concede

A ancora nasce dos mesmos falsos positivos ja conhecidos: `Captain Dedication`
e `Necrologist Dedication` falam de companheiro para **proibi-lo**, e
`Reincarnated Companion`, `Heal Companion`, `Fell Rider` e `Swift Paragon`
falam do companheiro que voce **ja tem**. Uma busca por "animal companion" traz
23 registros; a ancora derruba para 12.

`Dragon Grip` fica de fora de proposito: ele da **acesso a especie** Riding
Drake, nao um companheiro. Acesso e outro modelo (nao existe ainda) e vira
divida declarada no relatorio.

### `prov`

O portao 1 exige `prov` para todo campo preenchido, e `grants` esta na lista.
Dois casos:

- `grants` vazio na entrada (10 dos 12): `prov["grants"] = "derivado:prosa-companheiro"`.
- `grants` ja preenchido (`Beastmaster Dedication` tem `grant_item`,
  `Rough Rider` tem `grant_feat`): o `prov` original **fica**, e a derivacao se
  registra em `prov["grants.grant_actor"]`. Sobrescrever apagaria o rastro de
  quem escreveu o resto do `grants`, e o portao 1 nao olha chave extra.

## Parte 2 -- motor: a concessao vira slot

### `_concessoes_de_ator()`

Varre o que o personagem TEM (feats escolhidos + features de classe e
subclasse, a mesma fonte de `_grants_em_cadeia`) e coleta cada `grant_actor`:

```python
{"origem": "wb:feat/animal-companion", "em": 1, "tipo": "companheiro",
 "escolhe": "animal-companion", "opcoes": [], "classe": "wb:class/ranger"}
```

`classe` sai do nivel: `classe_do_nivel[em]`. Isto **conserta** um chute que
existe hoje -- `_classe_do_ator` cai em "assume a classe de maior nivel e
avisa" quando o ator nao declara `classe`, e o cap da regra 17b sai errado num
multiclasse. Com a concessao, a classe vem da escolha que a gerou.

### `slots_abertos()`

Uma concessao sem ator casado abre slot:

```python
{"slot": "companheiro", "em": 1, "kind": "animal-companion", "escolhe": 1,
 "origem": "wb:feat/animal-companion", "rotulo": "companheiro (nivel 1)"}
```

### `candidatos("companheiro", em=N)`

Registros de `kind == "animal-companion"` (113 na base), com as `opcoes` do
concessor ordenadas na frente. `atende`/`motivos` seguem a regra geral: o
`requires` da especie ordena, nunca filtra.

### Casamento concessao <-> ator

O ator continua vivendo em `doc["atores"]` -- ele **e** uma decisao (nome,
especie, grau escolhido), e o documento guarda decisao. O motor nao inventa
ator; ele so diz que falta um.

Chave do casamento: `concedido_por` + `em`. O `em` desempata quando o mesmo
feat concede duas vezes (`Mammoth Lord` da um segundo companheiro) e e opcional
-- ator antigo sem `em` casa com a primeira concessao daquela origem.

Tres situacoes, tres respostas:

| situacao | resposta |
|---|---|
| concessao sem ator | slot aberto |
| ator com `concedido_por` que ninguem concede | aviso (feat removido depois) |
| ator sem `concedido_por` | continua valendo, como hoje |

A ultima linha e compatibilidade: as fichas de teste ja tem ator escrito a mao,
e elas nao podem quebrar.

## Parte 3 -- app

- O bloco do nivel ganha o `Slot` de companheiro quando ha concessao naquele
  nivel, com os candidatos vindos de `p.candidatos("companheiro", n)`.
- Escolher a especie **cria** a entrada em `doc.atores` com `tipo`,
  `concedido_por`, `em` e `escolhas: [{slot: "animal", pega}]`.
- Limpar o slot remove o ator daquela origem. Remover o feat concedente deixa o
  ator orfao com aviso -- nao apaga sozinho: apagar decisao do jogador em
  cascata e o comportamento que a spec do documento rejeita.
- A ficha ganha o painel do companheiro: nome, especie, maturidade, AC, HP,
  saves, percepcao, ataques e support benefit. Os numeros ja vem prontos em
  `visao().atores`.

## Levantamento -- os 12 concessores

| id | frase | opcoes |
|---|---|---|
| `wb:feat/animal-companion` | you gain the service of a young animal companion | livre |
| `wb:feat/animal-companion-ranger` | idem | livre |
| `wb:feat/animal-trainer-dedication` | you gain the services of a young animal companion | livre |
| `wb:feat/beastmaster-dedication` | you gain the service of a young animal companion | livre |
| `wb:feat/cavalier-dedication` | you gain a young animal companion | livre |
| `wb:feat/commanders-companion` | you gain the service of a young animal companion | livre |
| `wb:feat/demon-hunting-companion` | you gain a young animal companion | livre |
| `wb:feat/drake-rider-dedication` | young riding drake, riding dragonet, or another | ordena 2 |
| `wb:feat/faithful-steed` | you gain the service of a young animal companion | livre |
| `wb:feat/mammoth-lord-dedication` | you gain a megafauna you tamed as a young animal companion | livre |
| `wb:feat/rough-rider` | you gain a wolf as an animal companion | fixa |
| `wb:feat/spirit-companion` | you gain the service of a young animal companion | livre |

## Divida declarada

Fica registrada no relatorio do passo, nao inventada aqui:

| o que | quem | por que fora |
|---|---|---|
| companheiro construct | Clockwork Reanimator Dedication, Prototype Companion, Rise My Creature! | a base nao tem stat block de construct companion |
| companheiro undead | Undead Master Dedication | idem |
| familiar | 29 feats + Witch + 18 lessons + 16 patrons | modelo proprio (habilidades, nao especie); `familiar_abilities` ja existe em `grants` e nao foi ligado |
| eidolon | Summoner e 63 feats | ficha compartilhada com o invocador, modelo proprio |
| acesso a especie | Dragon Grip | `access` nao existe no vocabulario |

## Como se prova que funciona

1. Ranger 1 com `Animal Companion` no `class_feat` do nivel 1 e **sem** ator no
   documento: `slots_abertos()` traz `{"slot": "companheiro", "em": 1}`.
2. `candidatos("companheiro", 1)` traz as 113 especies; com `Rough Rider`, o
   Wolf vem primeiro.
3. Escolhida a especie, o slot fecha e `visao().atores[0]` traz a ficha com HP,
   AC e ataques -- os mesmos numeros que `_ficha_de_companheiro` ja produzia
   com o ator escrito a mao.
4. Num `Ranger 3 / Fighter 5` cujo companheiro veio do Ranger, o cap sai **5**
   (`min(3 + 2, 8)`, regra 17b), e nao **7** -- que e o que sai hoje, ancorado
   no Fighter por ser a classe de maior nivel, e ainda com aviso de chute.
5. Ficha antiga, com ator escrito a mao e sem `concedido_por`, deriva igual --
   os 20 fixtures continuam passando campo a campo.
6. Python e TypeScript devolvem o mesmo `visao()` para as fichas dos fixtures.
