---
spec: bonus-de-item-equipado
project: waybuilder
version: 1
status: aprovada
created: 2026-07-30
todo: 43
---

# Spec -- o item equipado nao muda numero nenhum na ficha

## Como o item apareceu

Investigando a sobra da Fase 3 (`ac` e `strike-damage`, item 43), a primeira
medicao disse que `ac` tinha **34 grants e zero incondicionais** -- nada a
fazer. A segunda, contando os selectors escritos em LISTA, achou 6. E ao ir
aplicar os 6 descobriu-se que eles nunca chegam ao motor: os seis vivem em
registros de `equipment`, e **`_bonus_incondicionais` nao le o inventario**.

Ai o numero real apareceu, e ele nao e sobre `ac`.

## O tamanho, medido

`flat_modifier` sem `condicional`, selector estatico, valor inteiro -- os tres
filtros que o proprio motor ja aplica -- em registros de kind `equipment`,
`armor`, `weapon` e `shield`:

| kind | grants |
|---|---:|
| equipment | 261 |
| armor | 11 |
| shield | 11 |
| weapon | 10 |
| **total** | **293** |

Por selector, os maiores: `religion` 26, `intimidation` 25, `diplomacy` 22,
`athletics` 20, `acrobatics` 18, `arcana` 17, `stealth` 17, `perception` 13,
`performance` 12, `deception` 12, `saving-throw` 9, `medicine` 9, `society` 9,
`land-speed` 8, `nature` 8, ... e **`ac` 6**.

Todos esses selectors o motor **ja sabe onde somar**: pericia, salva, percepcao
e velocidade sao passos implementados. Nao falta regra nova. Falta a fonte.

Um personagem vestindo um item de +1 em Furtividade tem, hoje, a mesma
Furtividade de quem nao veste nada.

## A causa

`_resistencias` monta a lista de fontes assim (motor.py:3220-3232):

```
classes -> ancestria/heranca/background -> features -> feats -> INVENTARIO EQUIPADO
```

`_bonus_incondicionais` monta a **mesma lista, sem a ultima linha**. Os dois
blocos sao identicos, verbatim, exceto pelo inventario -- e foi por isso que a
resistencia vinda de equipamento (59 registros) chegou na ficha em 30/07 e o
bonus vindo de equipamento nunca chegou.

`equipado` continua sendo a condicao: espada na mochila nao ajuda ninguem. E a
mesma guarda que `_resistencias` usa.

## O `ac`, e a parte que nao e obvia

Dos 293, os 6 de `ac` sao `wb:equipment/bands-of-force` (e greater/major) e
`wb:equipment/assassins-bracers-type-i` (e II/III), todos do tipo `item`.

O `item_bonus` da armadura **tambem e bonus de item**. Somar o grant por cima
dele daria a quem veste Couro (+1 item) com Bands of Force (+1 item) uma CA de
+2 onde o RAW da +1: bonus do mesmo tipo nao empilham, vale o maior.

Entao `_defesa` deixa de somar `item_bonus + potencia` direto e passa a
**disputar**:

```
total = 10 + dex_usada + prof + _melhor_por_tipo(contendores)
```

com a armadura entrando como `("item", item_bonus + potencia, nome)`.

`_melhor_por_tipo` ja existe e ja e a regra do livro (spec
`2026-07-30-bonus-de-pericia-e-salva.md`). Nao ha regra nova a escrever -- ha
uma regra existente a aplicar onde ela ja devia estar.

A runa de potencia soma ao bonus da armadura ANTES da disputa, e nao disputa com
ela: pelo RAW a runa **aumenta** o bonus de item da armadura.

Sem nenhum grant, `_melhor_por_tipo([("item", ib + pot, nome)])` devolve
`ib + pot`. **O caminho de hoje e caso particular do novo.**

## O segundo defeito, achado ao implementar: o contador nunca conta

`_bonus_incondicionais()` termina em `self.bonus_ignorados = dict(fora)` --
atribuicao, nao acumulo. E ele tem tres chamadores, nesta ordem em `_derivar`:
`_defesa` (207), `_pericias_e_salvas` (209) e `_velocidade` (211).

`_pericias_e_salvas` GRAVA as chaves `selector nao modelado: X` depois de
chamar. `_resistencias` (210) tambem grava. E `_velocidade` (211) chama de novo,
reatribui, e **apaga as duas**.

Provado, nao deduzido:

```
p.bonus_ignorados = {"selector nao modelado: initiative": 3}
p._velocidade()
-> {}
```

Hoje nenhum personagem tem uma unica chave `selector nao modelado`. O mecanismo
que existe para tornar a perda silenciosa impossivel estava, ele proprio,
silenciado -- e foi assim que o `ac` pode sumir sem aparecer nem como ignorado,
protegido por um `OUTRO_PASSO = {"hp", "ac"}` cujo comentario afirma que
`_defesa` cuida do `ac`. `_hp` de fato le `flat_modifier`; `_defesa` nao lia.

Conserto: `_bonus_incondicionais` passa a ser calculado uma vez e memoizado. O
resultado nao muda entre os passos 207 e 211 (nenhum deles altera features,
feats, ancestria ou inventario), entao a memoizacao e correta.

## O que esta spec NAO resolve, e declara

- **Dano e ataque**, a outra metade da sobra da Fase 3, medidos junto e
  RECUSADOS com numero: depois dos filtros do motor sobram **6 ocorrencias em 6
  seletores diferentes** (`unarmed-damage`, `horns-damage`, `jaws-damage`,
  `melee-strike-damage`, `damage`, `attack`) -- um mecanismo de mapeamento
  selector->ataque por registro, alem de 34 selectors dinamicos (`{item|id}-*`)
  e 3 formulas. Mesmo criterio de custo por ocorrencia que recusou ItemAlteration
  (93 em quatro propriedades) e RollOption. Ficam CONTADOS em `bonus_ignorados`
  -- que so agora conta de verdade.
- **Os grants condicionais**, de `ac` (28) e de qualquer outro selector: sem
  contexto de acao a ficha parada nao pode aplica-los. Familia ja declarada em
  pericia, salva e resistencia.
- **A duplicacao do bloco de `fontes`** entre `_resistencias` e
  `_bonus_incondicionais`. Sao as mesmas dez linhas nos dois. Fica ANOTADO e nao
  mexido: os dois funcionam, e extrair helper e refatorar codigo que nao esta
  quebrado.
- **Escudo.** `self.ac["escudo"]` segue informando a parte, porque erguer o
  escudo e uma acao.

## Como se prova que funciona

1. Personagem com item de +1 em Furtividade equipado tem Furtividade +1 maior
   que o mesmo personagem sem ele; desequipar volta ao valor anterior.
2. Fixture novo `_teste-validacao-bonus-de-item.json` cobre: pericia vinda de
   item, CA com Couro + Bands of Force dando **+1** (nao +2), e Bands of Force
   Major (+3) com Couro (+1) dando **+3**.
3. Personagem sem item de bonus: CA e pericias identicas as de hoje -- o diff
   dos 26 fixtures prova que so muda quem tem item equipado.
4. `bonus_ignorados` passa a conter chaves `selector nao modelado` de verdade
   num personagem que tenha selector fora do modelo.
5. `ac` pode sair de `OUTRO_PASSO` sem sumir do contador, porque agora tem passo
   proprio real.
6. Paridade Python/TS em todos os casos e os 10 portoes verdes.
