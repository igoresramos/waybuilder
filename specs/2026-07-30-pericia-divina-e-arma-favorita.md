---
spec: pericia-divina-e-arma-favorita
req: WB-042
project: waybuilder
version: 1
status: implementada
created: 2026-07-30
altera: [WB-002]
todo: 87
---

# Spec -- a decima lacuna de leitura: `divine_skill`

## O achado

`Divine Skill` esta na prosa do AoN de praticamente toda divindade, e a base
tem **zero**. Medido:

| | quantas |
|---|---:|
| divindades na base | 488 |
| com `divine_skill` hoje | **0** |
| lidas da prosa | **475** |
| sem a frase `Divine Skill` | 13 |
| com mais de uma pericia | **0** |

As 13 sao filosofias e afins -- Atheism, Whispering Way, Prophecies of
Kalistrade, Laws of Mortality, Sangpotshi, Shoanti Animism, God Calling,
Norns... Elas nao tem pericia divina, e ausencia aqui e **resposta**, nao falha.

Distribuicao: Athletics 50, Nature 46, Society 40, Survival 39, Intimidation
38, Crafting 37, Diplomacy 36, Occultism 34, Deception 33, Stealth 28.

Mesmo formato do modal de santificacao, que ja se provou: a prosa do AoN traz
o campo e o extrator o descarta.

## O tamanho real e MAIOR que o item previa

O item 87 falava em 6 clausulas. Medido no residuo, sao **18 clausulas de
divindade**, e **11** fecham -- porque tres termos ja existem desde a spec
`divindade-na-ficha` e ninguem os aplicou ao residuo.

**Fecham com termo que JA EXISTE (4):**

| clausula | vira |
|---|---|
| `worshipper of a specific deity` (feat e archetype) | `has_deity` |
| `worship a deity with a divine font that grants heal` | `deity_font_permitido: heal` |
| `deity who grants the cold, fire, nature, or travel domain` | `any` de `domain` |

**Fecham com termo NOVO (7):**

| clausula | termo |
|---|---|
| `deity with a simple or unarmed attack favored weapon` | `deity_favored_weapon_category` |
| `trained with your deity's favored weapon` | `proficiency_favored_weapon` |
| `expert in your deity's favoured weapon` | idem (grafia britanica) |
| `master in Religion or your deity's divine skill` (x2) | `proficiency_divine_skill` |
| `must worship a deity that lists "holy" or "unholy" in their sanctification` | `any` de `deity_sanctification` |
| `You are not sanctified with the holy or unholy trait` | `not` + `has` das opcoes |

**NAO fecham (7), com o motivo:**

- **5 de alinhamento** (`you worship a good-aligned deity` e irmas) e
  `vigilant-benediction` (`alignment permitted by the chosen deity`).
  Alinhamento segue **recusado**: o Remaster aboliu o conceito, e a recusa ja
  tem numero em spec anterior.
- **`versatile-font`** (`deity that allows clerics to have both fonts`) precisa
  que o feat CONCEDA a segunda fonte, e concessao de escolha e outra familia --
  ja declarado assim na spec `fonte-divina-escolhida`.

## Os tres termos novos

| termo | pergunta | ancora |
|---|---|---|
| `deity_favored_weapon_category` | a arma favorita da divindade e desta categoria? | `favored_weapon` (479 divindades) -> `weapon_category` (1.032 de 1.039 armas) |
| `proficiency_favored_weapon` | o personagem tem rank X na arma favorita da divindade? | `_rank_de_arma`, que ja resolve `weapon:<slug>` |
| `proficiency_divine_skill` | o personagem tem rank X na pericia divina? | `divine_skill` + `self.pericias` |

Os tres respondem **False com motivo escrito** quando nao ha divindade
escolhida -- nunca estouram. Principio zero: marca, nao esconde.

## A conversao mora num passo TARDIO, e por que

Como em `derivar_requisito_de_subescolha.py`: o parser de `feats.py` roda na
EXTRACAO, e `divine_skill`, `favored_weapon` e os dominios so existem na base
depois. Na hora em que a clausula e lida nao ha com o que casar.

**Padrao, nao lista por registro.** Cada forma vira uma expressao regular sobre
o texto da clausula, e o passo relata quantas casaram. Uma clausula que nao
casar continua em `requires_residuo`, intacta.

## O que esta spec NAO resolve, e declara

- **Alinhamento** -- recusado de novo, agora com 6 clausulas contadas.
- **`versatile-font`** -- precisa de concessao de escolha.
- **Divindade OPCIONAL para quem nao e Clerigo nem Campeao** (`you follow a
  deity`, 4 clausulas): e **decisao de produto do Igor**, nao de motor. Fica
  fora ate ele decidir.
- **As 13 sem pericia divina** ficam sem o campo. Ausencia e resposta.

## Como se prova que funciona

1. 475 divindades ganham `divine_skill`; hoje sao 0. As 13 filosofias ficam sem.
2. Nenhuma divindade recebe mais de uma pericia.
3. `wb:feat/deadly-simplicity` deixa de ter as duas clausulas no residuo.
4. Um Clerigo de divindade com arma favorita SIMPLE atende
   `deity_favored_weapon_category`; um de arma martial nao, com o motivo
   nomeando a arma.
5. `proficiency_divine_skill` responde pela pericia certa: um Clerigo de
   Sarenrae (divine skill Medicine) master em Medicine atende; treinado nao.
6. Sem divindade escolhida, os tres termos respondem False **com motivo**, e
   nada estoura.
7. As 11 clausulas saem do residuo, e o total cai na mesma medida.
8. Nenhum registro perde `requires` que ja tinha.
9. Paridade Python/TS, diff de fixture LIDO.
10. Quatro camadas verdes.
