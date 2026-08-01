---
spec: choiceset
req: WB-009
project: waybuilder
version: 1
status: implementada
created: 2026-07-29
todo: 93
---

# Spec -- ChoiceSet: o personagem recebia TODAS as opcoes

## O problema

`Marshal Dedication` da, em RAW, treino **em UMA** entre Diplomacy e
Intimidation -- e sobe para expert se ja for treinado. A base grava:

```json
"grants": [{"choice": {"flag": "marshal-skill", "opcoes": 4}},
           {"proficiency": {"diplomacy": "trained"}},
           {"proficiency": {"diplomacy": "expert"}},
           {"proficiency": {"intimidation": "trained"}},
           {"proficiency": {"intimidation": "expert"}}]
```

O personagem recebe **as quatro**. Diplomacy E Intimidation, trained E expert.

Medido: **248 registros** (243 feat, 5 familiar-ability) tem o marcador `choice`
com consequencias soltas ao lado.

## Onde o dado se perde

Nao e falta de fonte -- o Foundry expressa o vinculo de forma explicita. No
`marshal-dedication.json`:

```json
{"key": "ChoiceSet", "rollOption": "marshal-skill",
 "choices": [{"value": "diplomacy-trained",  "label": "PF2E.Skill.Diplomacy"},
             {"value": "diplomacy-expert",   "label": "PF2E.Skill.Diplomacy"},
             {"value": "intimidation-trained", ...}, ...]}

{"key": "ActiveEffectLike", "path": "system.skills.diplomacy.rank", "value": 1,
 "predicate": ["marshal-skill:diplomacy-trained"]}
```

**`<rollOption>:<value>` e o elo.** Cada consequencia diz de qual opcao ela
depende.

O extrator joga os dois fora (`pipeline/extratores/feats.py:882-893`):

```python
elif k == "ChoiceSet":
    resumo = {"flag": r.get("flag")}
    if isinstance(esc, list):
        resumo["opcoes"] = len(esc)     # <- guarda a CONTAGEM e descarta as opcoes
```

E as consequencias, que tinham `predicate`, viram grants incondicionais.

## Quanto e recuperavel

Varredura nos packs do Foundry:

| | docs |
|---|---:|
| com `ChoiceSet` | 1.069 |
| com `rollOption` | 418 |
| **com consequencia predicada no rollOption** | **328** |

Os 328 sao o alvo: neles o elo opcao -> efeito esta escrito na fonte e so
precisa ser preservado. Os outros dependem de filtro dinamico
(`{item|flags...}`), que e outra historia.

**Nao da para adivinhar pelo que ja esta na base:** dos 83 registros com `choice`
e grants irmaos, em apenas 23 o numero de irmaos bate com o numero de opcoes.
Aninhar por posicao seria chute. O elo tem de vir da fonte.

## A decisao

### 1. O extrator preserva a estrutura

```json
{"choice": {"flag": "marshal-skill",
            "opcoes": [
              {"valor": "diplomacy-trained", "rotulo": "Diplomacy",
               "grants": [{"proficiency": {"diplomacy": "trained"}}]},
              {"valor": "intimidation-trained", "rotulo": "Intimidation",
               "grants": [{"proficiency": {"intimidation": "trained"}}]}
            ]}}
```

`opcoes` deixa de ser um numero e passa a ser a lista. Consequencia com
`predicate` no rollOption sai da raiz de `grants` e entra na opcao dela.

**Compatibilidade:** onde nao ha `rollOption` ou nao ha consequencia predicada, o
formato antigo (`opcoes` numero) continua, e nada muda. O motor aceita os dois.

### 2. O motor abre slot e aplica so o escolhido

- `grants` com `choice.opcoes` como LISTA abre slot `escolha_de_grant`, com o id
  do registro e a flag como chave.
- O jogador declara
  `{"em": N, "slot": "escolha_de_grant", "pega": "marshal-skill:diplomacy-trained"}`.
- **So os grants da opcao escolhida sao aplicados.** Sem escolha, NENHUM e
  aplicado -- e a higiene avisa, no mesmo desenho de `boosts_livres` e
  `pericias_livres`.

Aplicar todos "ate o jogador decidir" seria o defeito de hoje com outro nome.
Nao aplicar nada e o principio zero: o motor nao inventa a escolha.

## O que esta spec NAO resolve, e declara

- **Os 741 ChoiceSet sem consequencia predicada** (1.069 - 328) continuam com o
  marcador resumido. Nao ha elo na fonte para preservar; exigem o interpretador
  de filtro dinamico, que e o item 40.
- **O `predicate` das opcoes** (`skill:diplomacy:rank:0`) nao e avaliado: ele diz
  QUANDO a opcao esta disponivel (so oferece "trained" a quem e untrained). Sem
  isso o jogador ve as quatro e pode escolher uma que nao faz sentido. Fica
  declarado -- e melhor que receber as quatro de graca, e pior que o certo.

## Como se prova que funciona

1. `marshal-dedication` passa a ter `choice.opcoes` como lista de 4, cada uma com
   seus grants, e **nenhuma** proficiencia solta na raiz.
2. Um Guerreiro com Marshal Dedication e **sem** escolha declarada nao recebe
   Diplomacy nem Intimidation, e a ficha avisa que falta escolher.
3. Declarando `marshal-skill:diplomacy-trained`, ele recebe Diplomacy trained --
   e **nao** recebe Intimidation.
4. `slots_abertos()` lista a escolha pendente com as opcoes e os rotulos.
5. Registro cujo ChoiceSet nao tem consequencia predicada nao muda de forma.
6. As 22 fichas derivam identicas nas duas linguagens.
7. Os 10 portoes seguem verdes.
