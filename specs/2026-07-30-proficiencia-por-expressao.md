---
spec: proficiencia-por-expressao
project: waybuilder
version: 1
status: aprovada
created: 2026-07-30
todo: 72
---

# Spec -- a proficiencia que o motor escreve como `untrained` porque nao sabe ler

## O problema

Um Azarketi Guerreiro 13 que pega `Azarketi Weapon Expertise` sai com:

```
weapon-base-trident: untrained
weapon-base-spear:   untrained
weapon-base-crossbow: untrained
```

O feat existe justamente para elevar essas armas ao rank de arma do
personagem -- que num Guerreiro 13 e **master**. O motor escreve o oposto.

E pior que ausencia: `untrained` e uma AFIRMACAO. Um campo vazio faz a tela
perguntar; um `untrained` errado faz o jogador atacar com o numero errado.

## A causa

`grants[].proficiency` tem 1.071 valores na base. **1.024 sao rank literal**
(`trained`, `expert`...) e **47 sao expressao do VTT**:

| forma | ocorrencias |
|---|---:|
| `@actor.system.proficiencies.attacks.unarmed.rank` | 40 |
| `@actor.system.proficiencies.defenses.light.rank` | 2 |
| `@actor.system.proficiencies.defenses.medium.rank` | 1 |
| `max(unarmored, light, medium)` | 1 |
| `ternary(gte(@actor.level,19),3,ternary(gte(@actor.level,13),2,1))` | 1 |
| `min(N, @actor.flags.system.*)` | 2 |

`aplicar()` recebe a expressao no lugar do rank e a passa para `melhor_rank`,
que nao a reconhece e devolve `untrained`. Nao ha aviso: o valor errado entra
calado.

Sao **13 registros**, quase todos os `<Ancestria> Weapon Expertise` de nivel 13
(Ghoran 7, Vanara 7, Vishkanya 7, Conrasu 6, Azarketi 5, Genie 4), mais
`executioner-weapon-training`, `mountain-skin`, `harbingers-protection` e
`invulnerable-rager`.

## As decisoes

1. **Resolver o que da para resolver.** `@actor.system.proficiencies.<grupo>.
   <chave>.rank` vira o rank que o personagem TEM naquela chave. O mapa e
   direto: `attacks.unarmed` -> `unarmed`, `defenses.light` -> `light`,
   `defenses.medium` -> `medium`, `defenses.unarmored` -> `unarmored`. Isso
   cobre 43 das 47 (91%), incluindo as 40 da forma dominante.
2. **`max(...)` e `ternary(gte(@actor.level,N),R,...)` entram**, porque a
   gramatica ja foi medida e e pequena. Rank numerico (1, 2, 3) mapeia para
   trained/expert/master, que e a escala do proprio Foundry.
3. **O que nao resolve NAO vira `untrained`: nao vira nada.** As 2 formas com
   `@actor.flags.system.*` dependem de contador de estado de jogo que a ficha
   parada nao tem. A chave simplesmente nao e aplicada, e a ocorrencia e
   CONTADA em `proficiencia_ignorada` -- ausencia e honesta, `untrained` e
   mentira. Mesma regra do `_resolver_valor` das resistencias, que devolve
   `None` em vez de zero.

## A ordem, que e o que torna isto correto

A expressao le `self.proficiencias`, que esta sendo construida na mesma passada.
Funciona porque `aplicar` roda em tres blocos e nesta ordem: **classes**,
**features**, **feats**. Os 13 registros com expressao sao todos `feat`, e as
chaves que eles leem (`unarmed`, `light`, `medium`) vem de classe ou feature.
Quando o feat e avaliado, o valor lido ja esta no lugar.

Isso fica escrito no codigo: se algum dia um registro de CLASSE trouxer
expressao, ela le uma chave ainda vazia, e o resolvedor devolve `None` em vez de
um numero errado -- degrada para ausencia, nao para valor falso.

## O que esta spec NAO resolve, e declara

- **As 2 ocorrencias com `@actor.flags.system.*`** (`reclaimantPlea.count`,
  `vigilantBenedition.count`): contador que sobe durante a sessao de jogo. Nao
  e ficha parada.
- **`weapon-base-*` como chave de proficiencia.** Ela ja existe na base e o
  `_rank_de_arma` ja a consulta; esta spec so faz o valor certo chegar la.

## Como se prova que funciona

1. Azarketi Guerreiro 13 com `Azarketi Weapon Expertise` responde **master**
   nas cinco armas, e nao `untrained`.
2. O mesmo personagem no nivel 1 (unarmed trained) responde **trained**.
3. `mountain-skin` resolve pela chave de DEFESA, nao de ataque.
4. As 2 formas com `flags` nao criam chave nenhuma, e aparecem em
   `proficiencia_ignorada`.
5. Nenhuma proficiencia de rank literal muda -- o diff dos fixtures prova.
6. Quatro camadas verdes e os 10 portoes.
