---
spec: bonus-de-pericia-e-salva
req: WB-028
project: waybuilder
version: 1
status: implementada
created: 2026-07-30
altera: [WB-002]
todo: 72
---

# Spec -- o total de pericia sai da tela e vai para o motor, e passa a receber bonus

## Os dois problemas, e o segundo depende do primeiro

### 1. O total de pericia e calculado NA TELA

`PainelDireito.tsx:94` faz `v.nivel + RANK_BONUS[rank] + mod`. A mesma conta
aparece tres vezes no arquivo (pericia, Lore, salva/percepcao). O motor entrega
so `proficiencias` -- ranks --, e o numero que o jogador LE nasce no componente
React.

Isso quebra o desenho do projeto em tres pontos de uma vez:

- **nao tem oraculo**: o Python nao calcula, entao nao ha gabarito;
- **nao tem paridade**: o Python nao tem esse numero para divergir;
- **nao tem onde receber bonus**: `flat_modifier` nao alcanca a tela.

AC e ataque ja moram no motor (`_defesa`, `_ataques`), com detalhe e tudo.
Pericia e salva ficaram para tras.

### 2. `flat_modifier` so aplica `hp` -- 1.709 ocorrencias, 462 incondicionais

O motor le exatamente um selector. Medido na base:

| grupo | incondicionais |
|---|---:|
| pericia (as 16) | **230** |
| lista de selectors | 51 |
| dinamico (`{item\|id}-...`) | 51 |
| perception | 25 |
| land-speed | 24 |
| hp (**o unico aplicado hoje**) | 19 |
| saving-throw | 16 |
| cauda (initiative, swim-speed, will...) | ~26 |

Das 1.709, **1.247 sao `condicional: true`** -- "+2 em Atletismo so para
Empurrar". Aplicar o grupo inteiro INFLARIA a ficha parada, e por isso esta spec
so trata incondicional.

`value` e inteiro em 420 dos 462, texto em 41 (formula do VTT) e nulo em 1.

## As decisoes

1. **O motor passa a emitir `pericias` e `salvas` com total**, na mesma forma
   que `ac` ja usa: rank, atributo, bonus e `detalhe` legivel. A tela deixa de
   calcular e passa a ler -- e o calculo ganha oraculo, fixture e paridade.
   Nesta primeira passada o numero e IDENTICO ao que a tela ja mostrava: a
   mudanca e de lugar, nao de valor. Isso e proposital, e o diff dos fixtures
   deve provar exatamente isso.

2. **Bonus incondicional entra, com as regras de tipo do PF2e.** Bonus do mesmo
   TIPO nao empilham -- vale o maior; tipos diferentes somam. `type` ausente
   conta como `untyped`, que empilha com tudo (RAW). Sem isso, um personagem com
   tres itens de +1 de circunstancia sairia com +3 onde o RAW da +1.

3. **Selector que o motor nao modela e IGNORADO, e contado.** `initiative`,
   `perception-dc`, `healing-received`, `skill-check` generico e os 51 dinamicos
   ficam de fora desta passada. Nao viram aviso na ficha (seria ruido em
   `candidatos()`), e sim numero no relatorio do build.

4. **Lista de selectors** (`["ac", "saving-throw"]`, 51 casos) aplica em cada
   selector da lista. E a mesma declaracao escrita de forma compacta.

5. **`value` nao-inteiro e ignorado** -- 41 formulas do VTT e 1 nulo. Avaliar
   formula do Foundry e o interpretador inteiro (item 40), nao esta passada.

## O que esta spec NAO resolve, e declara

- **Os 1.247 condicionais.** Precisam de contexto de acao ("so para Empurrar"),
  que a ficha nao tem. Ficam visiveis no registro, como hoje.
- **Os 51 dinamicos.** Dependem de escolha nao modelada, mesmo territorio do
  ChoiceSet e do `grant_item` dinamico.
- **`proficiency` com expressao** (57 ocorrencias, item 72 parte 2). E outro
  primitivo -- proficiencia ESPELHADA -- e merece spec propria.
- **Iniciativa.** O motor nao tem o conceito; entra quando tiver.

## Como se prova que funciona

1. `visao.pericias` traz as 16 pericias mais as Lore do personagem, cada uma com
   `rank`, `atributo`, `total` e `detalhe`.
2. `visao.salvas` traz fortitude/reflex/will e percepcao pela mesma conta.
3. Para uma ficha SEM nenhum `flat_modifier`, o total do motor e igual, numero a
   numero, ao que `PainelDireito` calculava -- e o diff dos fixtures mostra so
   campos NOVOS, nunca valor diferente.
4. Destreinado nao soma o nivel: so o atributo (RAW).
5. Um personagem com `Ant Kholo` (+1 de circunstancia em Deception) sai com
   Deception um ponto acima, e o `detalhe` nomeia a fonte.
6. Duas fontes de +1 de CIRCUNSTANCIA na mesma pericia dao +1, nao +2.
7. Um +1 de circunstancia e um +1 de item na mesma pericia dao +2.
8. Bonus condicional NAO entra no total.
9. A tela le `visao.pericias` e para de calcular -- `RANK_BONUS` some de
   `PainelDireito.tsx`.
10. Quatro camadas verdes, e o relatorio do build diz quantos `flat_modifier`
    ficaram de fora e por que.
