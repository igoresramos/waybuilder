---
spec: slots-de-criacao-na-tela
req: WB-070
project: waybuilder
version: 1
status: implementada
created: 2026-07-31
todo: [115]
---

# Spec -- o motor abre o slot, a tela nao desenha

## Os dois defeitos, relatados pelo Igor testando o app

> "nos boosts tu so pode clicar em cada status uma vez, ou seja, n tem como
> colocar +2 em nada"
>
> "alem disso n tem como upar pericias"

Os dois sao a MESMA familia, e ja aconteceu antes: o item 106 registra que
`feat_concedido` era aberto pelo motor desde 30/07 e a tela nunca desenhou --
"quem pegava `Ancient Elf` nao era perguntado nada".

## Defeito 1 -- `pericias_livres` nao existe na UI

`grep -rn pericias_livres app/src/` fora do motor: **zero ocorrencias**. O
motor abre o slot na criacao:

```
{'slot': 'pericias_livres', 'em': 'criacao', 'kind': 'skill', 'escolhe': 3,
 'fontes': [{'classe': 'Fighter', 'orcamento': 3, 'delta': 3}],
 'rotulo': 'pericias treinadas (3 a escolher)'}
```

Um Guerreiro tem 3 pericias treinadas a escolher e a tela nunca as oferece. O
unico slot de pericia desenhado e `Aumento de pericia`, que so aparece nos
niveis de `aumentos_de_pericia.niveis` (3 e 5 para o Guerreiro) -- por isso um
personagem novo nao tem pericia nenhuma para mexer.

**E o slot nem funcionaria se fosse desenhado:** `candidatos()` nao conhece
`pericias_livres` em NENHUM dos dois motores. O `else` final devolve feats,
entao a tela ofereceria feats onde o slot pede pericia.

> Este e o mesmo achado do item 68, por outra porta: o tradutor de perícias
> mediu hoje que **450 dos 723 pontos** que ainda divergem contra os iconics
> sao `pericias_livres`. O buraco e o mesmo, e aparece na metrica e na tela.

## Defeito 2 -- o boost achata as fontes

O motor entrega os boosts JA separados por origem:

```
Human ................ 1
Human ................ 1
Fighter (chave) ...... 1    opcoes: dex | str
criacao (4 livres) ... 4
```

`BoostPicker` descarta o campo `fontes` inteiro e mostra uma unica fileira de
seis botoes com toggle. Clicar `STR` duas vezes DESMARCA.

**A regra de PF2e que a UI achata:** os 4 boosts livres de um mesmo bloco vao
cada um para um atributo DIFERENTE. Boosts de blocos diferentes podem cair no
mesmo atributo -- e assim que um Guerreiro humano chega a `STR 18` no nivel 1.
Uma fileira unica torna a regra impossivel de expressar: ou proibe tudo, ou
permite o ilegal.

O motor esta correto e foi medido: duas entradas `["str"]` dao `str 14`, e uma
entrada `["str","str"]` tambem. Da para chegar a +2 hoje adicionando uma leva
por vez -- so que nada na tela sugere isso, entao na pratica o Igor esta certo.

## O desenho

**Uma linha por FONTE**, na ordem em que o motor as devolve, cada uma com
tantos seletores quanto `quantidade`:

```
Human              [ STR ]
Human              [ DEX ]
Fighter (chave)    [ STR ]          <- so dex|str, porque a fonte diz `opcoes`
Criacao (4 livres) [ STR ][ CON ][ WIS ][ CHA ]
```

Regras, e cada uma sai de um campo que a fonte ja declara:

1. **`opcoes` restringe.** A fonte da habilidade-chave traz `opcoes: [dex, str]`
   e os outros quatro atributos nem aparecem naquela linha.
2. **Dentro de uma fonte, atributo nao repete** -- e a regra RAW, e vale so
   ali. Entre fontes, repetir e o comportamento CERTO e e o que da +2.
3. **Uma entrada de `boosts_livres` por seletor**, com `pega: [attr]`. O
   formato do documento nao muda: `definirBoosts` ja aceita N entradas no mesmo
   nivel, e o motor ja soma. O que muda e so como a tela agrupa.

> **Nao guardar a fonte no documento.** Tentador escrever `origem: "Human"` na
> escolha, e errado: o documento grava DECISAO, nao derivacao (principio 3 do
> README). A fonte e derivada da classe e da ancestralidade a cada build, e
> gravar congelaria um dado que muda quando a regra muda.

## Como se prova que funciona

1. Um Guerreiro humano nivel 1 mostra **quatro linhas** de boost, nao uma.
2. Da para colocar `STR` na linha do Human E na de criacao, e a ficha mostra
   `STR 14` -- o caso que o Igor reportou como impossivel.
3. Dentro da linha de criacao, escolher `STR` num seletor tira `STR` dos
   outros tres -- a regra RAW, visivel.
4. A linha da habilidade-chave do Guerreiro oferece **dois** atributos.
5. O slot `Pericias treinadas` aparece na criacao com 3 seletores para um
   Guerreiro, e `candidatos("pericias_livres")` devolve **pericias**, nao
   feats.
6. Escolher 3 pericias muda o rank delas na coluna da direita.
7. Paridade Python/TS e os testes do porte continuam passando.

## O que esta spec NAO resolve, e declara

1. **`pericias_livres` so na criacao.** Ancestralidade, background e feat
   tambem concedem treino, e o motor ja soma o orcamento; a tela do nivel N
   nao ganha o slot aqui.
2. **Lore nao entra.** O slot oferece as pericias do kind `skill`; escolher
   uma Lore especifica e outro caminho.
3. **Nao ha desfazer em bloco** -- cada seletor limpa o seu.
4. **A flaw de ancestralidade continua fora.** O motor nao a modela, e a tela
   nao pode mostrar o que nao existe.
