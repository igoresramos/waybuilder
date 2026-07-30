---
spec: escolha-de-nivel-futuro
project: waybuilder
version: 1
status: aprovada
created: 2026-07-30
todo: 73
---

# Spec -- quem planeja o nivel 8 numa ficha de nivel 4 leva aviso errado

## O problema

Uma ficha de Guerreiro 4 com duas escolhas anotadas para o nivel 8 sai com:

```
skill_increase: aumento no nivel 8, que nao tem aumento (niveis validos: [3])
slot class_feat: escolha no nivel 8, que nao tem slot desse tipo
                 (niveis validos: [1, 2, 4])
```

Os dois avisos estao errados. No nivel 8 o personagem **vai ter** os dois slots;
a lista "niveis validos" so enumera os que existem ATE o nivel atual. O motor
esta cobrando o futuro contra a regua do presente.

## Tres semanticas no mesmo motor

O review adversarial de 27/07 achou isto e nao foi resolvido:

| passo | como trata escolha de nivel futuro |
|---|---|
| `_atributos` | caso NORMAL -- ignora e segue |
| `_higiene_de_slot` | ERRO -- avisa |
| `_aumentos_de_pericia` | ERRO -- avisa |

Alem disso, a contagem `len(usados) > len(niveis)` nao filtra por nivel, entao
uma escolha futura tambem inflava o "gastou mais slots do que tem".

## E a divergencia nao para no aviso: ela chega ao NUMERO

Medido nos dois passos, com a mesma ficha de Guerreiro 4 e escolhas anotadas
para o nivel 8:

| passo | escolha futura e APLICADA? |
|---|---|
| `_atributos` | **nao** -- FOR continua 10 |
| `_aumentos_de_pericia` | **sim** -- Atletismo vira `trained` |

Um Guerreiro 4 ficava treinado numa pericia por um aumento que ele so recebe no
nivel 8. Isso nao e aviso a mais: e rank que o personagem nao tem. O item 73(a)
descrevia o problema como divergencia de AVISO; ele e tambem de valor.

## A decisao

**O motor recorta por nivel em TODA checagem**, adotando a semantica que
`_atributos` ja praticava.

Ficha de personagem e documento de planejamento: o jogador anota o que pretende
pegar. Escolha acima do nivel atual e PLANO, nao erro -- e avisar sobre ela
treina o jogador a ignorar avisos, que e o pior resultado possivel para um
mecanismo de aviso.

A alternativa ("o documento so descreve o presente") foi descartada: obrigaria a
apagar do documento o que ja esta escrito, e o projeto nao apaga escolha do
jogador -- marca. Aqui nem marcar cabe, porque nao ha erro.

**O que e recortado fica CONTADO** em `escolhas_de_nivel_futuro`, pela mesma
razao de `bonus_ignorados`: silenciar por decisao e diferente de silenciar por
descuido, e so o contador distingue os dois depois.

## O que esta spec NAO resolve, e declara

- **Escolha em nivel que NUNCA vai existir** (um `class_feat` no nivel 7 de uma
  cadencia que so tem par). Enquanto o personagem nao chegar la, ela e plano; ao
  chegar, o aviso volta sozinho, porque a checagem passa a valer. Antecipar
  exigiria projetar a cadencia futura, que e modelo novo.
- **O item 73(b)**, `em: "criacao"` desligando a checagem de nivel: e outro
  ponto do mesmo review e continua aberto.

## Como se prova que funciona

1. Guerreiro 4 com escolhas anotadas para o nivel 8 nao leva aviso nenhum sobre
   elas.
2. O mesmo documento num Guerreiro 8 leva os avisos que couberem -- o recorte e
   pelo nivel ATUAL, nao pela existencia da escolha.
3. Escolha em nivel <= nivel atual continua sendo checada e APLICADA como hoje.
3b. O aumento de pericia anotado para o nivel 8 nao muda o rank de um
   personagem de nivel 4 -- mesma semantica que `_atributos` ja praticava para
   o boost.
4. `escolhas_de_nivel_futuro` conta quantas foram recortadas.
5. Nenhum fixture perde aviso legitimo.
6. Quatro camadas verdes.
