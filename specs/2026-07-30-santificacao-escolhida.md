---
spec: santificacao-escolhida
req: WB-050
project: waybuilder
version: 1
status: implementada
created: 2026-07-30
todo: [98, 99]
---

# Spec -- a santificacao, e a primeira sub-escolha FILTRADA da base

## De onde veio

Do item 99: os class-features do Foundry declaram os eixos em regras
`ChoiceSet`, e `Deity (Champion)`, `Deity (Cleric)` e `Vindicator` trazem o
mesmo, com prompt `PF2E.SpecificRule.Prompt.Sanctification` e tres opcoes --
`holy`, `unholy` e `none` --, **cada uma condicionada a divindade escolhida**.

E era exatamente o que a spec `divindade-na-ficha` declarou faltar: *"precisa
de um eixo cujas opcoes dependam da escolha anterior, e nenhum eixo da base
filtra hoje"*.

## A descoberta que mudou o desenho

A base guarda `sanctification` como lista achatada -- `["holy"]`,
`["holy","unholy"]` ou ausente. Ia inferir dela: "uma opcao so = obrigatoria".

**Estaria errado, e em 408 divindades.** A prosa do AoN traz o modal, e o
extrator o descarta:

| frase do AoN | divindades |
|---|---:|
| `can choose holy` | 265 |
| `can choose unholy` | 143 |
| `none` | 112 |
| `must choose unholy` | 87 |
| `can choose holy or unholy` | 73 |
| `must choose holy` | 23 |
| (nao casou) | 14 |

Cayden Cailean tem `["holy"]` na base e a prosa diz **"can choose holy"** -- ele
NAO obriga. Só 110 divindades obrigam. Nona vez do mesmo padrao no projeto: a
fonte publica e o extrator nao le.

## As decisoes

1. **`sanctification_escolha`**, campo novo, lido da prosa do AoN: `"can"`,
   `"must"` ou `null`. O `sanctification` existente (a lista) nao muda -- ele
   espelha o campo do AoN e ja esta certo.
2. **Tres registros proprios** (`wb:sanctification/holy`, `/unholy`, `/none`),
   cada um com o seu `requires`. Nao e maquinaria nova: `candidatos()` ja
   avalia o `requires` de cada opcao e devolve `atende: false` para quem nao
   cabe. **Filtrar aqui e MARCAR, nunca esconder** -- principio zero, igual ao
   resto do app.
3. **Um termo, `deity_sanctification`**, que responde pela divindade escolhida:
   - `holy` cabe se a divindade permite ou obriga holy;
   - `unholy` idem;
   - `none` cabe se a divindade **nao obriga** nenhuma das duas -- que e
     literalmente o predicado do Foundry (`nor must:holy, must:unholy`).
4. **O eixo vai nas mesmas classes do eixo de divindade** (Clerigo e Campeao),
   derivado de quem tem `class-feature/deity-*`. O `Vindicator` tambem traz o
   ChoiceSet, mas ele e uma CAUSA do Campeao: o eixo ja existe na classe, e
   repetir por subclasse seria oferecer a mesma escolha duas vezes.
5. **Sem divindade escolhida, nenhuma opcao atende** -- e a tela mostra as tres
   marcadas, com o motivo. Nao inventa santificacao para quem nao tem deus.

## O que esta spec NAO resolve, e declara

- **As 14 divindades cuja frase nao casou** ficam com
  `sanctification_escolha: null` e sao tratadas como `can` -- nao reprovar e o
  certo quando nao se sabe. Uma delas e `Atheism`, que nao e divindade.
- **A sub-escolha da FONTE divina** (as 137 divindades que permitem heal e
  harm) usa exatamente este mesmo desenho e entra logo em seguida, em mudanca
  propria: o termo `deity_font` ja existe e so precisa passar a olhar a
  escolha.
- **O efeito mecanico** de ser holy/unholy (dano de santidade, fraquezas) nao
  entra: e mecanica condicional, a familia ja recusada com numero tres vezes.
- **As outras 191 regras `ChoiceSet`** do item 99 seguem por ler; as de forma
  `query` precisam de avaliador proprio.

## Como se prova que funciona

1. `wb:deity/cayden-cailean` responde `sanctification_escolha: "can"` e
   `wb:deity/iomedae`, `"must"`.
2. Um Clerigo de Cayden Cailean: `holy` atende, `none` atende, `unholy` nao.
3. Um Clerigo de Iomedae (`must choose holy`): `holy` atende e **`none` NAO** --
   e a diferenca que a inferencia ingenua teria perdido.
4. Um Clerigo de Abadar (`can choose holy or unholy`): as tres atendem.
5. Um Clerigo de Magdh (`none`): so `none` atende.
6. Sem divindade escolhida, nenhuma das tres atende, e o motivo diz por que.
7. As tres opcoes **aparecem sempre** na lista, marcadas -- nunca somem.
8. Quatro camadas verdes.
