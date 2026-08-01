---
spec: pericia-de-recall-knowledge
req: WB-067
project: waybuilder
version: 1
status: implementada
created: 2026-07-31
altera: [WB-002]
todo: 108
---

# Spec -- "expert in a skill with the Recall Knowledge action"

## O defeito, achado pelo Pathbuilder

Doze sondas de `skill_feat` rodadas em paralelo -- a primeira vez que a bancada
cobre skill feat fora de Fighter/Rogue -- mostraram tres feats que **nos
oferecemos e o Pathbuilder recusa**:

| feat | RAW exige | nosso `requires` |
|---|---|---|
| `wb:feat/automatic-knowledge` | **expert** numa pericia com Recall Knowledge | `character_level >= 2` |
| `wb:feat/dubious-knowledge` | **trained** numa pericia com Recall Knowledge | `character_level >= 1` |
| `wb:feat/masterful-obfuscation` | **master** numa pericia com Recall Knowledge | so o gate de nivel |

A causa e a mesma nos tres: a clausula real ficou em `requires_residuo`, prosa
que nunca virou termo, e o `requires` guarda apenas o gate de nivel. Entregar
opcao que o personagem nao pode pegar e o criterio `alta` do projeto.

## A forma e quantificada, e o motor ja sabe o padrao

"<rank> in a skill with the Recall Knowledge action" nao nomeia pericia: ela
pergunta **se existe alguma** com aquele rank. E exatamente o que `lore:*` ja
faz desde o item 95 -- "alguma Lore", devolvendo o MELHOR rank da ficha, porque
o requisito pode pedir mais que trained. E o que `weapon:*` faz para arma.

Entao o termo novo e o mesmo desenho, com outra lista: `skill:recall-knowledge`.

## Quais pericias entram, e por que a lista pode ser fixa

RAW, Recall Knowledge e acao de **Arcana, Crafting, Lore (qualquer), Medicine,
Nature, Occultism, Religion e Society**. Nao e heuristica nem amostra: e a
lista do livro, e ela nao muda com a fonte -- por isso pode viver no motor como
constante, do mesmo jeito que `CATEGORIAS_DE_ARMA` vive.

Perceber e Atletismo NAO entram, e e isso que faz o termo discriminar: um
Barbaro treinado so em Athletics e Intimidation continua reprovado, que e a
resposta certa.

## O desenho

1. **Motor**: `skill:recall-knowledge` resolve para o melhor rank entre as oito,
   contando qualquer `lore:*` da ficha. Entra no mesmo `_termo_proficiency` que
   ja despacha `weapon:` e `lore:`.
2. **Pipeline**: um passo le `requires_residuo`, casa a forma
   `^(trained|expert|master|legendary) in a skill with the recall knowledge`,
   emite `proficiency: {"skill:recall-knowledge": {">=": <rank>}}` num `and`
   com o que ja existia, e **remove a clausula do residuo** -- residuo resolvido
   que fica no residuo mente sobre o tamanho do que falta.

Sao **exatamente 3** registros, todos medidos. Nada de varredura por
semelhanca: a regex e ancorada no comeco da clausula.

## Como se prova que funciona

1. Um Mago 2 (trained em Arcana pela classe) ATENDE `Dubious Knowledge`.
2. Um Barbaro 2 treinado so em Athletics/Intimidation NAO atende -- e o motivo
   nomeia o rank que falta.
3. `Automatic Knowledge` exige **expert**: o mesmo Mago 2 nao atende, e um
   personagem com expert numa das oito atende.
4. Lore conta: quem so tem `Alcohol Lore` trained atende `Dubious Knowledge`.
5. Os tres registros saem do `requires_residuo`.
6. Paridade Python/TS, 10 portoes, oraculo, navegador.
