# Spec -- slots abertos e candidatos por slot

Status: proposta
Data: 2026-07-27
Itens do TODO: 65 (candidatos por slot), 74 (higiene de atributo)

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
| `class_feat` | `kind == feat` e trait de alguma classe do personagem |
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
