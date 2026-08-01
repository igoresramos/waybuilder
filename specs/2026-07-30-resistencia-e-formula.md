---
spec: resistencia-e-formula
req: WB-049
project: waybuilder
version: 1
status: implementada
created: 2026-07-30
todo: 40
---

# Spec -- resistencia, fraqueza e imunidade, e o mini-avaliador de formula

Fatia 3.2 do plano (`docs/planos/2026-07-29-backlog-completo.md`).

## O problema

A ficha nao tem resistencia. Nem imunidade, nem fraqueza. A base tem:

| grant | ocorrencias |
|---|---:|
| `resistance` | 233 |
| `immunity` | 14 |
| `weakness` | 11 |

Vindas de feat (125), equipment (59), armor (21), weapon (12), shield (9) e
familiar-ability (7). O motor nao le nenhuma das tres, e a `visao` nao tem campo
para elas. Um Barbaro de instinto, um Kineticista de terra e um anao com
armadura de resistencia saem todos sem numero nenhum.

## A segunda metade do problema: `valor` e formula

`_resolver_valor` hoje resolve TRES coisas: inteiro, `@actor.level` e
`@actor.details.level.value`. Qualquer outra expressao vira **zero** -- em
silencio.

Isso ja era divida do `flat_modifier` de HP, e aqui morde de verdade. Medido nos
`resistance`/`weakness`:

| valor | ocorrencias |
|---|---:|
| inteiro literal | 122 |
| `floor(@actor.level/2)` (nas 3 grafias) | 26 |
| `max(1,floor(@actor.level/2))` / `max(floor(...),1)` | 20 |
| `@actor.level` | 19 |
| `N + @armor.system.runes.potency` | 22 |
| `N + floor(@actor.level/2)` | 2 |

A gramatica inteira e: **inteiro, `@actor.level`,
`@armor.system.runes.potency`, `+`, `/`, `floor()` e `max()`**. Nao ha
multiplicacao, nao ha subtracao, nao ha aninhamento alem de `max(1, floor(...))`.

`@armor.system.runes.potency` o motor JA tem: `_defesa` calcula a potencia da
armadura equipada (linha 1736), do registro ou da entrada do inventario.

## As decisoes

1. **`_resolver_valor` vira um mini-avaliador da gramatica medida**, e nao um
   interpretador geral. Substitui as duas variaveis por numero e reduz
   `floor(a/b)` e `max(a,b)` ate sobrar aritmetica de `+` e `/` inteira.
   Expressao que nao couber na gramatica devolve `None` -- e nao zero. Zero e
   uma resposta; `None` diz "nao sei", e quem chama decide. O chamador do HP
   continua tratando ausencia como "nao soma".

2. **`visao.resistencias`, `visao.fraquezas` e `visao.imunidades`**, cada uma
   como lista de `{tipo, valor, origem}`. Imunidade nao tem valor.

3. **Mesma regra de nao-empilhamento das resistencias do PF2e**: duas fontes de
   resistencia ao MESMO tipo nao somam -- vale a maior. E a regra do livro, e e
   a mesma forma do `_melhor_por_tipo` que os bonus ja usam.

4. **Tipo dinamico (`{item|flags...}`) e ignorado e CONTADO** -- 44 dos 233.
   Depende de escolha nao modelada, mesmo territorio do ChoiceSet. Entra em
   `bonus_ignorados`, junto com o resto que nao se aplica em silencio.

5. **`custom` (14) fica de fora** -- e o balde do Foundry para resistencia que
   so a prosa descreve. Contado, nao inventado.

## O que esta spec NAO resolve, e declara

- **Resistencia condicional.** A base nao marca `condicional` em `resistance`
  como marca em `flat_modifier`; se aparecer caso que dependa de contexto, vira
  item proprio.
- **`@armor.system.runes.potency` sem armadura equipada** resolve para 0, que e
  o valor correto: sem armadura nao ha runa.
- **Os 44 tipos dinamicos e os 14 `custom`** -- 58 de 233 (25%). O relatorio
  conta; a ficha nao inventa.

## Como se prova que funciona

1. `_resolver_valor("floor(@actor.level/2)")` num personagem 8 devolve 4;
   `max(1,floor(@actor.level/2))` num personagem 1 devolve 1 (e nao 0).
2. `_resolver_valor("2 + @armor.system.runes.potency")` com armadura +1 devolve
   3, e sem armadura devolve 2.
3. `_resolver_valor("@actor.abilities.str.mod")` devolve `None` -- fora da
   gramatica, e o motor nao chuta zero.
4. Um personagem com feat que concede resistencia a fogo 5 sai com
   `resistencias` contendo `{tipo: "fire", valor: 5}` e a origem nomeada.
5. Duas fontes de resistencia a fogo, 5 e 10, dao 10 -- nao 15.
6. Imunidade e fraqueza aparecem nas suas listas.
7. Tipo dinamico nao entra na ficha e aparece contado.
8. As sete valem identicas no porte TypeScript.
9. Quatro camadas verdes; fixtures regenerados e o diff LIDO.
