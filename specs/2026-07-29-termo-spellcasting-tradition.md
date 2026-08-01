---
spec: termo-spellcasting-tradition
req: WB-019
project: waybuilder
version: 1
status: implementada
created: 2026-07-29
altera: [WB-002]
todo: 89
---

# Spec -- o termo `spellcasting_tradition`

## O problema

O censo de termos do predicado, feito em 2026-07-29:

| termo | clausulas | tem handler? |
|---|---:|---|
| `has` | 4.726 | sim |
| `character_level` | 4.340 | sim |
| `class_level` | 2.219 | sim |
| `proficiency` | 1.063 | sim |
| `subclass` | 199 | sim |
| `ability` | 136 | sim |
| **`spellcasting_tradition`** | **99** | **NAO** |
| `trait` | 53 | sim |
| `focus_pool` | 17 | sim |
| `sense` | 13 | sim |
| `has_actor` | 6 | sim |
| `nao_modelavel` | 3 | por desenho |

**99 clausulas, em 27 arquetipos, sem handler em NENHUM dos dois motores.** Pelo
principio zero, termo desconhecido nao reprova -- entao elas liberam sempre.

Efeito medido na comparacao com o Pathbuilder: seis dedicacoes de conjuracao
(`Cathartic Mage`, `Necrologist`, `Shadowcaster`, `Soulforger`, `Time Mage`,
`War Mage`) aparecem disponiveis para um **Guerreiro 6** e um **Ladino 2**, que
nao conjuram nada. O Pathbuilder barra, e ali ele esta certo.

`cathartic-mage-dedication` e o retrato do defeito:

```json
{"all": [{"any": [{"ability": {"cha": {">=": 14}}},
                  {"spellcasting_tradition": "arcane"},
                  {"spellcasting_tradition": "divine"},
                  {"spellcasting_tradition": "occult"},
                  {"spellcasting_tradition": "primal"}]},
         {"character_level": {">=": 2}}]}
```

O `any` passa a vacuo: quatro dos cinco ramos sao ignorados, e basta o nivel.

`requires_residuo` e `null` nesses casos -- **nao e residuo, e lacuna de
implementacao.** A diferenca importa: residuo e coisa que decidimos nao avaliar;
isto e coisa que o schema sabe dizer e o motor nao sabe ouvir.

**Os dois motores erram IGUAL,** e por isso nenhum teste de paridade pega. E a
mesma classe de silencio das 14 fichas de hoje cedo -- so que ali a divergencia
salvou, e aqui nao ha divergencia nenhuma para salvar.

## O dado existe

Das 12 classes com `spellcasting`, **8 tem tradicao resolvida** na base:

| tradicao | classes |
|---|---|
| `divine` | Animist, Cleric, Oracle |
| `occult` | Bard, Psychic |
| `arcane` | Magus, Wizard |
| `primal` | Druid |

Tres guardam **prosa** no lugar da tradicao -- Sorcerer (bloodline), Summoner
(eidolon), Witch (patron): a string literal
`"variavel (definida pela escolha de bloodline; nao ha tradicao fixa na
class-feature)"`. E o item 78.

O motor tambem ja monta conjuracao **de arquetipo** (`_conjuracao_de_arquetipo`,
2026-07-29), com tradicao resolvida -- um Guerreiro com Cleric Dedication e
Basic Cleric Spellcasting conjura `divine` de verdade, e deve atender.

## A decisao

```json
{"spellcasting_tradition": "arcane"}
```

Le-se: **"o personagem consegue conjurar magia dessa tradicao?"**

O termo percorre `self.conjuracao` -- que ja inclui classe E arquetipo -- e
responde:

1. **alguma entrada com a tradicao pedida** -> atende.
2. **nenhuma entrada de conjuracao** -> NAO atende. E o caso do Guerreiro e do
   Ladino, e e o ganho inteiro desta spec.
3. **conjura, mas a tradicao esta em prosa** (Feiticeiro, Invocador, Bruxa) ->
   **atende**, pelo principio zero: o motor nao sabe qual e a tradicao e nao vai
   reprovar sobre o que nao sabe.

### Por que o caso 3 nao empurra aviso

A tentacao e avisar "tradicao indefinida" ali. **Nao.** `candidatos()` avalia o
predicado de milhares de feats por slot -- um aviso por avaliacao viraria
enxurrada e afogaria os avisos que importam.

E o aviso seria redundante: a ficha **ja mostra** a string de prosa no lugar da
tradicao. A marca existe, e visivel, e esta no lugar certo -- a ficha, nao o log.
Quando o item 78 resolver a tradicao por subclasse, o caso 3 morre sozinho.

## O que esta spec NAO resolve, e declara

**Nao resolve o item 78.** Um Feiticeiro continua atendendo `arcane`, `divine`,
`occult` e `primal` ao mesmo tempo, porque nao sabemos qual e a dele. Isso e
melhor do que hoje (onde ate o Guerreiro atende) e pior do que o certo. O item
78 fecha.

## Como se prova que funciona

1. Um Clerigo 2 atende `{"spellcasting_tradition": "divine"}`.
2. O mesmo Clerigo **nao** atende `{"spellcasting_tradition": "arcane"}`.
3. Um Guerreiro 6 **nao** atende nenhuma das quatro tradicoes.
4. Um Guerreiro com Cleric Dedication + Basic Cleric Spellcasting **atende**
   `divine` -- conjuracao de arquetipo conta.
5. Um Feiticeiro 5 atende as quatro (caso 3, declarado).
6. `Cathartic Mage Dedication` sai da lista de candidatos de um Guerreiro 6.
7. As 22 fichas derivam identicas nas duas linguagens.
8. Na comparacao com o Pathbuilder, as seis dedicacoes saem da divergencia.

## A armadilha do porte

Termo novo mexe em **TRES** lugares: o metodo no Python (que despacha por
convencao, `getattr(self, f"_termo_{termo}")`), o metodo no TS, e **a linha do
`switch`** no TS. A terceira e a que se esquece, e esquecer nao levanta erro --
pelo principio zero, termo ignorado nao reprova. Custou 14 fichas em 2026-07-29.
