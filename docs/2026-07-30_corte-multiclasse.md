# Item 46 -- cortar o arquetipo de multiclasse? As quatro validacoes, medidas

Igor anotou a ideia em 2026-07-27 com quatro validacoes explicitas a fazer
**antes de decidir**. Elas estao feitas. Este documento e o parecer; a decisao
de produto e do Igor.

Medicao reproduzivel: `docs/medicoes/medir_corte_multiclasse.py`.

## O recorte, derivado por duas vias

Nunca por lista a mao -- lista a mao ja errou tres vezes neste projeto. Duas
vias independentes, e elas **batem exatamente**:

| via | resultado |
|---|---|
| arquetipo cujo NOME e nome de classe | 27 |
| arquetipo dono de um feat com trait `multiclass` | 27 |
| divergencia entre as duas | nenhuma |

O que sairia:

| | quantos |
|---|---:|
| arquetipos | **27** de 243 |
| feats atribuidos a eles | 195 |
| feats ORFAOS que pertencem ao corte | 7 |
| **total de feats** | **202** |
| feats que sobram | 6.063 |
| desses 202, com prosa propria | **202** (todos) |

> Os 7 orfaos sao um achado lateral: tem trait `archetype`, exigem uma dedicacao
> de multiclasse no `requires`, mas o campo `archetype` esta vazio. A anotacao
> original falava em 195; sao 202. A atribuicao de arquetipo tem buraco.

---

## (a) Algum feat que SOBRA depende de um feat que SAI?

**Sim.** E a validacao (a) sozinha nao acha tudo -- ela olha `requires`, e ha
dependencia por `grants` tambem.

### Quebra real: 1 pelo `requires`

```
wb:feat/master-spotter  (arquetipo Overwatch, que SOBRA)
    -> exige wb:feat/ranger-dedication, que SAI
```

Overwatch e arquetipo comum, nao de multiclasse. Cortar deixa um feat dele sem
porta.

### Quebra real: 1 pelos `grants` -- esta a validacao (a) nao previa

```
wb:feat/spellshot-dedication  (arquetipo Spellshot, que SOBRA)
    grant_spellcasting.cadeia   = wb:archetype/wizard        <- SAI
    grant_spellcasting.degraus  = basic/expert/master-wizard-spellcasting  <- SAEM
```

O Spellshot **nao tem escada propria**: ele empresta a do arquetipo de Mago.
Cortar o Mago deixa o Spellshot conjurando sem progressao nenhuma.

### Nao sao quebra, mas sao defeito de hoje: 3 homonimos

```
wb:feat/efficient-alchemy    -> wb:feat/advanced-alchemy
wb:feat/shield-of-reckoning  -> wb:feat/champions-reaction
wb:feat/swift-retribution    -> wb:feat/champions-reaction
```

Os tres sao feats de **classe** (traits `alchemist`, `champion`), e o
pre-requisito deles resolveu para o feat de **arquetipo** de mesmo nome, embora
`wb:class-feature/advanced-alchemy` e `wb:class-feature/champions-reaction`
existam na base. Mesmo caso em `grants`: `wb:class-feature/alchemy` concede
`wb:feat/quick-alchemy` (o do arquetipo) tendo
`wb:class-feature/quick-alchemy` ao lado.

**Isto e defeito hoje, independente do corte** -- e a familia da licao do item
18 (homonimo resolvido para o registro errado). Vai para o TODO com numero
proprio.

Os outros 7 (`auspicious-mount`, `heal-mount`, `imposing-destrier`,
`loyal-warhorse`, `shield-paragon`, `extended-kinesis`, `master-alchemy`) sao a
mesma familia, apontando para `devout-blessing` / `base-kinesis` /
`expert-alchemy`.

---

## (b) O que se perde de conteudo unico?

Os 202 feats concedem, somados:

| concessao | quantas |
|---|---:|
| `grant_item` | 86 |
| `choice` | 64 |
| `grant_feat` | 30 |
| `proficiency` | 19 |
| `flat_modifier` | 12 |
| **`grant_spellcasting`** | **10** |
| `skill_training` | 7 |
| resto (weapon_proficiency, grant_actor, crafting_ability, focus_pool, resistance, speed, familiar_abilities, fast_healing, versatile_vials, special_resource) | 11 |

O item que decide e a linha de conjuracao: **33 feats Basic/Expert/Master
Spellcasting**, cobrindo 11 rotas (Animist, Bard, Cleric, Druid, Magus, Oracle,
Psychic, Sorcerer, Summoner, Witch, Wizard). Sao a rota de conjuracao inteira
por arquetipo, com uma excecao adiante.

---

## (c) O que acontece com o piso da regra 21? -- **a validacao que decide**

O piso e `RANK_DEDICACAO`, tabela fixa no `motor.py`, citada verbatim de
"Spellcasting Archetypes". Numericamente ela sobrevive ao corte: e constante,
nao le a base.

**Mas ela deixa de descrever coisa alguma.** A regra 21 esta escrita assim:

> A comparacao e contra a rota **gratuita**: sob Free Archetype (regra 2,
> sempre ligada) a dedicacao nao custa feat de classe.

Cortadas as 11 escadas de multiclasse, sobram **7** dedicacoes com conjuracao,
e delas so **2** tem escada Basic/Expert/Master propria:

| dedicacao que sobra | tradicao | escada propria? |
|---|---|---|
| Captivator | occult | **sim** |
| Rivethun Involutionist | divine | **sim** |
| Spellshot | arcane | nao -- **emprestada do Mago, que sai** |
| Harrower, Psychic Duelist, Pure Legion Enforcer, Student of Perfection | -- | nao concedem escada |

Ou seja, depois do corte:

- **occult** e **divine** mantem uma rota gratuita, cada uma atras de um
  arquetipo de raridade e sabor muito especificos;
- **arcane** e **primal** ficam **sem rota gratuita nenhuma**.

O piso da regra 21 passaria a comparar o nivel de classe contra uma rota que o
personagem nao pode pegar em duas das quatro tradicoes. E o piso nao e enfeite:
foi ele que consertou a regra 17b, com **50 dos 204 pares** violando o
invariante e o dip chegando a **0%** da dedicacao no nivel 20. Tirar a rota e
manter o piso e deixar um numero sem fundamento; tirar os dois devolve a 17b ao
estado que a simulacao ja provou quebrado.

---

## (d) Alcance do Free Archetype (regra 2)

| | quantos |
|---|---:|
| arquetipos hoje | 243 |
| depois do corte | **216** |
| desses, com feat de dedicacao na base | 198 |
| sem porta de entrada | 18 |

Os 18 sem porta ja estao assim hoje -- lacuna anterior, nao consequencia do
corte. Vai para o TODO junto com os homonimos.

---

## Parecer: **nao cortar**

Quatro razoes, em ordem de peso.

**1. A regra 21 perde o chao (validacao c).** E a unica validacao das quatro
com resposta terminal. Arcane e primal ficariam sem rota gratuita, e o piso
viraria numero sem referente. Refundar o piso em outra coisa seria invencao --
e este projeto nao inventa tabela.

**2. A premissa do corte nao se sustenta.** A anotacao diz: *"na houserule
multiclasse ja se faz com nivel de classe -- as duas rotas competem, e a regra
23 acabou de declarar que se excluem"*. A regra 23 exclui **por classe**: nivel
de Mago e dedicacao de Mago nao convivem. Ela nao torna as rotas redundantes em
geral -- um Guerreiro pegando Wizard Dedication e exatamente a "rota paralela
mais barata" que a **regra 20 mantem de proposito**. Cortar nao e a conclusao
natural da 23; e revogar a 20.

**3. O custo/beneficio esta invertido.** O corte remove 202 registros com prosa
propria, quebra o Overwatch e orfana a escada do Spellshot -- para evitar que o
motor marque, num personagem de classe unica, **uma** dedicacao e os ~7 feats
atras dela. Sao 202 removidos para calar 8 marcados.

**4. Contraria o principio zero.** O principio do projeto e *marcar, nunca
esconder nem apagar*. A regra 23 ja faz isso, com o motivo escrito. O corte e
apagar por construcao -- a operacao que o projeto inteiro recusa.

### Se ainda assim for para cortar

O caminho e derivavel e reversivel, e o custo esta dimensionado:

1. recorte por trait `multiclass` (nunca lista a mao), incluindo os 7 orfaos;
2. re-ancorar `wb:feat/master-spotter` ou tira-lo junto;
3. dar escada propria ao Spellshot ou tira-lo junto;
4. decidir o que vira o piso da regra 21 para arcane e primal -- **este passo
   nao tem resposta derivavel e e o que trava**.

## O que este documento gerou de trabalho novo

- **homonimo classe x arquetipo**: 10 registros com `requires`/`grants`
  apontando para o feat de arquetipo tendo o `class-feature` de mesmo nome ao
  lado. Familia da licao do item 18.
- **atribuicao de arquetipo com buraco**: 7 feats com trait `archetype` e campo
  `archetype` vazio.
- **18 arquetipos sem feat de dedicacao** na base.
