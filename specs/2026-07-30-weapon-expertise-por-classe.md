---
spec: weapon-expertise-por-classe
req: WB-055
project: waybuilder
version: 1
status: implementada
created: 2026-07-30
todo: 75
---

# Spec -- o Campeao 5 fica trained em marcial onde o livro diz expert

## O problema

`wb:class-feature/weapon-expertise` e **um registro so, compartilhado por 14
classes**, e concede:

```json
{"proficiency": {"simple": "expert", "unarmed": "expert"}}
```

Entre as 14 ha classes marciais e nao-marciais, e uma feature so nao serve as
duas progressoes. Medido num personagem de nivel 7:

| classe | simple | martial | o livro diz |
|---|---|---|---|
| Champion | expert | **trained** | martial expert |
| Exemplar | expert | **trained** | martial expert |
| Guardian | expert | **trained** | martial expert |
| Investigator | expert | **trained** | martial expert |
| Magus | expert | **trained** | martial expert |
| Thaumaturge | expert | **trained** | martial expert |

Sao **dois pontos a menos em todo ataque** com arma marcial, a partir do nivel em
que a feature entra (5 no Campeao). Nao e cosmetico: e o numero que o jogador
usa na mesa.

## O que a medicao mudou no item

O item 75c dizia "14 classes apontam para ela, entre elas marciais e
nao-marciais" e supunha que a correcao exigia a TABELA de progressao do AoN em
HTML, "mesmo caminho de `aplicar_conjuracao.py`". Duas coisas nao batem:

1. **A resposta esta na PROSA, nao na tabela.** O AoN tem 53 documentos de
   Weapon Expertise com texto, cada um com o campo `class` e a frase exata:
   "Your proficiency ranks for simple weapons, martial weapons, and unarmed
   attacks increase to expert". Nao ha HTML a raspar.
2. **Metade do trabalho ja existe.** A base ja tem variante por classe para
   Bard, Inventor, Ranger, Swashbuckler, Psychic, Druid, Wizard e Alchemist --
   e as tres primeiras ja concedem `martial: expert` corretamente. O buraco sao
   as **6 classes que so apontam para a compartilhada** e cuja prosa pede
   marcial.

As outras 8 das 14 (Druid, Kineticist, Oracle, Psychic, Sorcerer, Swashbuckler,
Witch, Wizard) estao CERTAS como estao: a prosa delas diz "simple weapons and
unarmed attacks", e o Swashbuckler ja tem variante propria com marcial.

## A decisao

Um passo novo, `derivar_weapon_expertise.py`, que:

1. Le os documentos de Weapon Expertise do AoN que tem `class` e prosa.
2. Extrai as categorias da frase `proficiency rank(s) for ... increase(s) to
   expert`. O vocabulario e fechado: `simple`, `martial`, `unarmed`.
3. Para cada classe cuja progressao aponta para a COMPARTILHADA, compara o que a
   prosa pede com o que a classe ja recebe somando TODAS as suas features de
   weapon expertise. Se nada falta, nao mexe.
4. Se falta, cria um irmao `wb:class-feature/weapon-expertise-<classe>` com o
   que a prosa pede e reaponta a progressao daquela classe -- e so dela.

**Irmao por classe, e nao editar a compartilhada**: dar marcial ao registro
compartilhado daria marcial ao Druida tambem. E o mesmo desmembramento que
`desmembrar_colisoes.py` faz quando um id serve a duas entidades.

`prov` marca `derivado:prosa-weapon-expertise`, e o passo e idempotente.

## O que esta spec NAO resolve, e declara

- **A duplicata Druida/Swashbuckler/Psychic/Wizard**, que apontam para a
  compartilhada E para a variante propria. A uniao da o valor certo, entao nao
  ha numero errado -- so redundancia. Mexer nisso e limpeza, nao correcao.
- **`Alchemical Weapon Expertise`** ja modela a bomba (`weapon-base-alchemical-
  bomb`) e fica como esta.
- **`bard-weapon-expertise` dar marcial expert sem o Bardo ser treinado em
  marcial.** E o que o livro diz, e o item ja tinha notado; nao e defeito nosso.
- **Weapon Legendary/Mastery** e os degraus seguintes: outra medicao, se
  tiverem o mesmo compartilhamento.

## Como se prova que funciona

1. Champion 5 responde `martial: expert`; hoje responde `trained`.
2. Idem Exemplar, Guardian, Investigator, Magus e Thaumaturge no nivel em que
   cada um recebe a feature.
3. **Druid 11 e Sorcerer 11 continuam sem marcial** -- o irmao so nasce para
   quem a prosa manda, e o diff dos fixtures prova que o resto nao mexeu.
4. O ataque com arma marcial do Campeao 5 sobe 2 pontos.
5. O passo roda duas vezes sem duplicar registro nem progressao.
6. Quatro camadas verdes e os 10 portoes.
