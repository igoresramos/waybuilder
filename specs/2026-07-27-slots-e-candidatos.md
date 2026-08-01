---
spec: slots-e-candidatos
req: WB-004
project: waybuilder
version: 2
status: implementada
created: 2026-07-27
aprovada_em: 2026-07-29
atualizada_em: 2026-08-01
todo: 65
---

# Spec -- slots abertos e candidatos por slot

**Status corrigido em 2026-07-29:** estava como `proposta` embora o que ela
descreve ja estivesse no ar desde o commit `f98b4b4e5`. `candidatos(slot, em)` e
`slots_abertos()` substituiram o `disponiveis()` por kind, e `_orcamento_de_boost`
fechou a higiene de atributo (item 74). Do item 65 sobra so `_termo_has` sem
recorte temporal.

**Versao 2, 2026-08-01:** a linha `class_feat` da tabela de elegibilidade dizia
so "trait de alguma classe do personagem". O motor deixou de se comportar assim
em `3a44f10` (2026-07-28), quando passou a aceitar tambem feat de arquetipo
nesse slot -- e a spec nao foi atualizada junto. Pior: ela foi marcada
`aprovada` em 2026-07-29, um dia DEPOIS de o motor ja a contradizer. Por 4 dias
a spec descreveu um motor que nao existia, e 28 testes escritos contra ela
ficaram vermelhos acusando o motor CERTO -- o defeito era de SDD, nao de codigo.
Ver "Por que o slot de classe aceita arquetipo" abaixo.

Itens do TODO: 65 (candidatos por slot -- parcial), 74 (higiene de atributo --
concluido)

## O problema

O motor sabe responder duas perguntas:

- **"o que eu tenho"** -- `visao()` devolve HP, proficiencias, features, slots.
- **"o que esta errado"** -- `fora_do_requisito` e `avisos`.

O app precisa de uma terceira, e ela nao existe:

> **"o que eu posso escolher AGORA, neste slot?"**

Hoje `disponiveis(kind="feat")` devolve os **6.273 feats** da base, ordenados
por atendimento de requisito. Uma tela de escolha nao pode receber isso: o slot
de Free Archetype do nivel 4 aceita um subconjunto pequeno e bem definido, e e
o motor que sabe qual e.

Falta tambem o outro lado da mesma moeda: **o que ainda esta por preencher**.
Uma ficha sem boost de atributo declarado deriva com todos os atributos em 10,
HP menor, e **nenhum aviso** -- o app nao teria como montar a lista de
pendencias.

## Principio zero, aplicado aqui

`requires` **sugere e ORDENA, nunca bloqueia**. Isto vale para a lista de
candidatos: ela e **ordenada**, com o que nao atende marcado e no fim -- nunca
filtrada. O jogador continua podendo escolher o que quiser.

A distincao que importa:

| conceito | significado | efeito na lista |
|---|---|---|
| **elegibilidade de slot** | o slot aceita este TIPO de coisa? | FILTRA |
| **requisito** (`requires`) | o personagem atende as condicoes? | ORDENA e marca |

Um feat sem trait `archetype` simplesmente **nao e candidato** ao slot de Free
Archetype -- isso nao e principio zero, e a definicao do slot. Ja um feat de
arquetipo cujo requisito o personagem nao atende **aparece na lista**, marcado.

## Parte 1 -- `slots_abertos()`

Devolve, para o personagem no estado atual, tudo que esta por preencher.

```python
[
  {
    "slot": "free_archetype",     # nome do slot no documento
    "em": 4,                      # nivel em que o slot existe
    "kind": "feat",               # que tipo de coisa preenche
    "escolhe": 1,                 # quantos itens
    "preenchido": False,
    "rotulo": "Free Archetype (nivel 4)",
  },
  {
    "slot": "boosts_livres", "em": 1, "kind": "ability", "escolhe": 4,
    "preenchido": False, "rotulo": "Boosts de atributo (nivel 1)",
    "origem": "wb:ancestry/human",
  },
  {
    "slot": "subclasse", "em": 1, "kind": "racket", "escolhe": 1,
    "preenchido": True, "rotulo": "Ladino / racket",
  },
]
```

Fontes de slot, todas ja derivadas hoje:

| slot | vem de | ja existe? |
|---|---|---|
| `class_feat`, `skill_feat`, `general_feat`, `ancestry_feat` | `self.slots` | sim |
| `free_archetype` | `self.slots` (regra 2) | sim |
| `skill_increase` | `self.aumentos_de_pericia` | sim |
| `subclasse` | `self.slots_de_subclasse` | sim |
| `boosts_livres` | **nao existe** -- item 74 | **nao** |
| `choice` pendente (grants com `choice`) | `grants[].choice` | **nao** |

### Item 74 -- orcamento de atributo

Precisa ser derivado como os outros orcamentos ja sao (pericia livre, slot de
feat). Fontes de boost, todas presentes em `grants`:

- **ancestria**: `ability_boost` com `livre` ou com `opcoes` de N>1
- **background**: idem (os 524 backgrounds tem o padrao "um dirigido + um livre")
- **classe**: habilidade-chave, que em Fighter/Ranger/Champion/Monk/Magus/
  Exemplar e escolha entre 2 (regra 8: so a PRIMEIRA classe)
- **nivel**: 4 boosts livres nos niveis 5, 10, 15, 20

O motor ja LE tudo isso -- `_atributos::aplicar_boosts` aplica quando `opcoes`
tem tamanho 1 e, quando e livre ou escolha-entre-N, escreve uma linha no log
`origem_boost` e segue. O que falta e transformar esse log em **orcamento**:
quantos boosts o personagem tem direito, quantos declarou, e o que sobra.

O `ability_flaw` da ancestria continua automatico (nao e escolha).

## Parte 2 -- `candidatos(slot, em)`

```python
p.candidatos("free_archetype", em=4)
->
[
  {"id": "wb:feat/quick-shot", "nome": "Quick Shot", "level": 4,
   "atende": True,  "motivos": [], "ja_pego": False},
  {"id": "wb:feat/archer-expertise", "nome": "Archer Expertise", "level": 6,
   "atende": False, "motivos": ["exige nivel de personagem >= 6; tem 4"],
   "ja_pego": False},
]
```

### Regras de elegibilidade por slot

| slot | aceita |
|---|---|
| `class_feat` | `kind == feat` e (trait de alguma classe do personagem **ou** trait `archetype`) |
| `skill_feat` | `kind == feat` e trait `skill` |
| `general_feat` | `kind == feat` e trait `general` |
| `ancestry_feat` | `kind == feat` e trait da ancestralidade do personagem |
| `free_archetype` | `kind == feat` e trait `archetype` |
| `skill_increase` | `kind == skill` (mais os `lore:` que o personagem tem) |
| `subclasse` | os `opcoes` daquele bloco de `slots_de_subclasse` |
| `boosts_livres` | os 6 atributos |
| `nivel_de_classe` | `kind == class` |

Nenhuma dessas listas e escrita a mao: todas saem de trait ou de campo que a
base ja tem. Onde a regra de casa muda o RAW (regra 23, dedicacao da propria
classe), o veto ja existe em `_veto_dedicacao_da_propria_classe` e entra como
**motivo**, nunca como filtro.

### Por que o slot de classe aceita arquetipo

A regra RAW do PF2e e que a porta de entrada de um arquetipo e **gastar um feat
de classe** na Dedication. O Free Archetype e regra VARIANTE: quem nao joga com
ela so tem o slot de classe para entrar num arquetipo.

O numero que fecha o argumento, medido em `pipeline/base/index.json` de
2026-08-01: das **225 dedicacoes** da base (feats com trait `dedication`),
**zero** carregam trait de classe. Exigir trait de classe no slot, como a versao
1 desta spec dizia, tornava as 225 inalcancaveis por ele -- a unica porta para
qualquer arquetipo virava o slot de Free Archetype, e um personagem sem a regra
variante nao conseguiria nunca entrar em arquetipo nenhum. Isso e um filtro que
BLOQUEIA escolha legal, o oposto do principio zero.

O recorte continua sendo recorte, nao "aceita qualquer coisa". Num Guerreiro 4:

| conjunto | tamanho |
|---|---|
| `disponiveis("feat")` | 6.239 |
| `candidatos("class_feat", em=4)` | 2.239 |
| ...por trait `fighter` | 124 |
| ...por trait `archetype` | 2.115 (destes, 225 sao dedicacao) |

Ou seja: 4.000 feats de OUTRAS classes continuam fora da lista. O que entra a
mais e exatamente o corpo de arquetipo, que e o que o RAW manda entrar.

Consequencia aceita: um feat de arquetipo NAO-dedicacao (os 2.115 menos 225)
tambem aparece, mesmo que o personagem ainda nao tenha a Dedication dele. Isso e
`requires` fazendo o seu papel -- o feat aparece com `atende: False` e o motivo
"exige X Dedication", nunca sumido. Principio zero: sugere, nao bloqueia.

A regra 23 nao muda: `_veto_dedicacao_da_propria_classe` marca a dedicacao da
propria classe como fora-do-requisito, e ela continua na lista.

Implementacao: `_aceita_no_slot`, `motor/motor.py:3634-3646`.

`ja_pego` marca o que o personagem ja tem -- o app nao deve oferecer duas vezes
o que nao se pode pegar duas vezes, mas quem decide exibir e a tela.

### Ordenacao

1. `atende` primeiro (True antes de False)
2. depois `level` crescente
3. depois nome

E a ordem que `disponiveis()` ja usa; muda so o conjunto de entrada.

## Compatibilidade

`disponiveis(kind=...)` **continua existindo** e com o mesmo comportamento --
ela e usada por `ficha.py` e por teste. `candidatos()` e adicao, nao troca.

## Como se prova que funciona

1. `candidatos("free_archetype", em=2)` num Guerreiro 4 **nao** contem
   `wb:feat/reactive-shield` (sem trait `archetype`) e **contem**
   `wb:feat/archer-dedication`.
2. A lista e menor que `disponiveis("feat")` em pelo menos uma ordem de
   grandeza.
3. Feat de nivel alto aparece na lista com `atende: False` -- nunca sumido.
4. `slots_abertos()` numa ficha completa devolve lista vazia de pendencias; ao
   remover as escolhas de `boosts_livres`, devolve o boost pendente com a
   contagem certa.
5. Para as 27 classes, o total de boosts com direito bate com o RAW: 4 de
   ancestria (2 livres + 1 dirigido + flaw), 2 de background, 1 de classe, 4
   por nivel a cada 5 niveis.
6. `candidatos("class_feat", em=4)`, para cada uma das 27 classes, so contem
   feat com trait daquela classe OU com trait `archetype` -- nenhum item cai
   fora dos dois. Feat de classe alheia sem `archetype` (`call-wizardly-tools`,
   traits `concentrate/teleportation/wizard`) fica de fora num Guerreiro.
7. As 225 dedicacoes estao TODAS na lista de `class_feat` de cada uma das 27
   classes. E o teste que impede a regressao de 2026-07-27 voltar: se alguem
   reintroduzir o filtro por trait de classe, este cai com 225 faltando.
   Testes: `motor/testes/test_payload_do_app.py`,
   `motor/testes/test_slots_e_candidatos.py`.
