---
spec: nomear-o-balaio-por-tag
project: waybuilder
version: 1
status: aprovada
created: 2026-07-31
todo: 69
---

# Spec -- o balaio ja era eixo; faltava o NOME

## Tres medicoes minhas erradas antes de chegar aqui

Vale registrar, porque o erro foi sempre o mesmo e ja tem lição no projeto:

1. Classifiquei as 202 opcoes por sufixo de nome e conclui que os 18 do Exemplar
   eram "eixos que ninguem modelou". **Falso.**
2. Medi alcance somando as `opcoes` dos blocos nao-balaio. **Falso**: os eixos
   criados em 31/07 guardam `filtro` e deixam `opcoes` vazia de proposito, entao
   tudo saiu como "eixo novo".
3. Medi alcance pelo motor e tudo saiu como "DUPLICATA". **Tambem enganoso**: os
   registros sao alcancaveis atraves do PROPRIO balaio, que e um bloco de
   subclasse como qualquer outro.

A pergunta certa, que e a licao do item 97, era: *por qual caminho o jogador
chega nele* -- e a resposta e "pelo balaio, que ja funciona".

## O que o balaio realmente e

Um Exemplar de nivel 15 recebe hoje:

```
candidatos("subclasse", 3)  -> The Brave, The Cunning, The Deft, ...      (6)
candidatos("subclasse", 7)  -> Born of the Bones of the Earth, ...        (8)
candidatos("subclasse", 15) -> Healer of the World, The Last Ruler, ...   (4)
```

Os epitetos estao la, no nivel certo, com `escolhe: 1`. O bloco **funciona como
eixo**. O unico defeito e o nome: `outras-opcoes`, que na tela vira
"Exemplar / outras-opcoes". O jogador escolhe sem saber o que esta escolhendo.

E o nome existe na fonte, na `tags` dos proprios registros.

## O que a tag agrupa, medido

| classe | nivel | tag | do bloco |
|---|---:|---|---|
| Exemplar | 3 | `exemplar-root-epithet` | 6/6 |
| Exemplar | 7 | `exemplar-dominion-epithet` | 8/8 |
| Exemplar | 15 | `exemplar-sovereignty-epithet` | 4/4 |
| Barbarian | 1 | `barbarian-instinct` | 9/9 |
| Druid | 1 | `druid-order` | 9/9 |
| Investigator | 1 | `investigator-methodology` | 5/5 |
| Champion | 1 | `blessing-of-the-devoted` | 2/2 |
| Sorcerer | 1 | `sorcerer-bloodline` | 18/19 |
| Summoner | 1 | `summoner-eidolon` | 13/14 |
| Animist | 1 | `animist-apparition` | 13/17 |
| Animist | 1 | `animistic-practice` | 4/17 |

**91 das 202** opcoes do balaio. E o Animista mostra que renomear o bloco nao
basta: um unico balaio dele carrega **dois** eixos distintos.

## A regra

Para cada bloco `outras-opcoes`, agrupar as opcoes por `tag`. Todo grupo com
**2 ou mais** vira um bloco proprio, com `eixo` = a tag. O que nao tem tag, ou
cujo grupo tem so um, **fica no balaio** -- o balaio nao morre, encolhe.

Nao se inventa nome: a tag e o nome, verbatim da fonte. E nada muda de
conteudo -- as mesmas opcoes, no mesmo nivel, com o mesmo `escolhe`. O que muda
e o bloco ter identidade.

## O efeito colateral, que e um ACHADO e nao um defeito

Feiticeiro (18 de 19) e Invocador (13 de 14) tem sobra de UMA opcao, e o bloco
residual vira um "falta escolher `outras-opcoes` (1 opcoes)". Feio, e correto.

A sobra dos dois e a mesma coisa: **`Spell Repertoire (Sorcerer)`** e
**`Spell Repertoire (Summoner)`** -- que nao sao linhagem nem eidolon, sao
feature automatica da classe, arquivada no balaio por engano. Medido: nenhuma
das duas chega a ficha por qualquer outro caminho (`has` responde `False`, nao
estao na progressao, nao ha concessao).

Antes desta spec elas estavam MISTURADAS entre as 19 linhagens, e um Feiticeiro
podia escolher "Spell Repertoire" no lugar de uma linhagem. A divisao nao criou
o problema; ela o isolou, e o aviso passa a dizer em voz alta que o app nao sabe
o que aquele registro e. Marcar, nunca esconder -- e apaga-las as tornaria
inalcancaveis, que e a familia do item 97.

Sao mais dois nomes para o resto do item 69.

## O que esta spec NAO resolve, e declara com numero

As **111 opcoes restantes** do balaio, que a medicao por sufixo ja explicou em
estrutura mas nao em modelo:

- ~68 sao **variante por subclasse** (`Field Discovery (Bomber)`,
  `Initiate Benefit (Amulet)`): o parentese casa exatamente uma opcao de
  subclasse ja escolhida, entao nao ha o que escolher -- pedem gate
  `requires: {subclass: ...}`, nao eixo.
- ~30 sao o **pai generico** dessas variantes (`Perpetual Infusions` ao lado dos
  quatro `Perpetual Infusions (X)`).
- o resto e cauda.

Isso e outra spec, e continua no item 69.

## Como se prova que funciona

1. O Exemplar ganha `exemplar-root-epithet` (nv 3), `exemplar-dominion-epithet`
   (7) e `exemplar-sovereignty-epithet` (15), com 6, 8 e 4 opcoes -- e nenhum
   balaio sobra nesses niveis.
2. O balaio do Animista, que era um bloco de 17, vira DOIS eixos (13 e 4).
3. O balaio total cai de 202 para 111.
4. Nenhuma opcao muda de nivel, some ou aparece: os `candidatos("subclasse", n)`
   de cada classe sao os MESMOS conjuntos de antes, so redistribuidos entre
   blocos com nome.
5. Nenhuma classe sem tag no balaio muda.
6. Paridade Python/TS, diff de fixture LIDO, 10 portoes, navegador.
