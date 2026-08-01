---
spec: grant-feat-de-background
req: WB-011
project: waybuilder
version: 1
status: implementada
created: 2026-07-29
altera: [WB-002]
todo: 70
---

# Spec -- o feat que o background promete e nunca entrega

## O problema

A base tem 926 alvos de `grant_feat`. **476 nao sao id** -- e os 476 sao de
`background`, 100%:

| forma | quantos | exemplo |
|---|---:|---|
| id `wb:` valido | 450 | `wb:feat/assurance` |
| **dict Python stringificado** | **400** | `"{'name': 'Hobnobber', 'foundry_uuid': 'Compendium.pf2e.feats-srd.Item.Hobnobber'}"` |
| **nome cru** | **76** | `"Assurance"` |

A causa e uma linha: `pipeline/unificar_efeitos.py:76` faz

```python
g.append({"grant_feat": [str(x) for x in lista]})
```

`str()` sobre um dict devolve o `repr` do dict. O dado para resolver estava
DENTRO do valor o tempo todo (`name` + `foundry_uuid`) e foi carimbado como
texto.

O motor sabe que isso esta errado e ja avisa
(`grant_feat com alvo nao resolvido pelo pipeline`), mas avisar nao entrega:
**nenhum background concede o feat que promete**. Um Barkeep deveria nascer com
Hobnobber e nao nasce.

Achado com preco medido na comparacao com o Pathbuilder: `Hobnobber` aparece na
nossa lista de candidatos de skill feat e some da dele -- porque no Pathbuilder o
personagem **ja tem** o feat e nao pode pegar de novo.

## A medicao que fecha o desenho

Resolvendo os 476 por nome normalizado contra os feats da base:

| resultado | quantos |
|---|---:|
| **resolve para exatamente UM `wb:feat`** | **476** |
| ambiguo (nome em mais de um feat) | **0** |
| nao encontrado | **0** |

Zero ambiguidade e zero ausencia. Isso muda a natureza do conserto: nao e "dar o
melhor palpite", e **traducao completa**. Se sobrar um alvo nao resolvido depois
disto, e regressao, nao residuo.

## A decisao

**Resolver na origem, em `unificar_efeitos.py`.**

O `main()` ja carrega a base inteira, entao da para montar o indice
`nome normalizado -> wb:feat/<id>` ali e passar para o conversor de background.
Cada alvo vira:

1. ja comeca com `wb:` -> mantem;
2. dict stringificado -> extrai `name` e resolve;
3. nome cru -> resolve;
4. **nao resolveu** -> mantem o valor original E conta no relatorio. O motor
   continua avisando, e o numero aparece no build em vez de ficar invisivel.

A normalizacao e a mesma de `resolver_referencias.py` (minusculas, sem acento,
sem apostrofo, pontuacao virando espaco) -- nao inventar uma terceira.

### Por que nao em `resolver_referencias.py`

Ele roda no passo 4d e so mexe em `requires`; `unificar_efeitos.py` roda no 4g e
e quem CRIA o `grant_feat` de background. Resolver depois seria consertar o que
acabamos de escrever errado. O lugar certo e nao escrever errado.

## O que esta spec NAO resolve, e declara

**Nao cria portao.** Hoje o portao 3 cobra id inexistente em `requires`, e nada
cobra alvo de `grants`. Enquanto nao existir, uma regressao aqui volta a ser
invisivel -- exatamente o que aconteceu com o item 59. Fica ligado a tarefa de
portao daquele item, e nao repetido aqui.

## Como se prova que funciona

1. Depois de reemitir, **0** alvos de `grant_feat` fora do formato `wb:`.
2. Um personagem de background Barkeep tem `Hobnobber` em `concedidos`.
3. `Hobnobber` aparece no slot de skill feat com **`ja_pego: true`**. Ele
   **nao some** da lista: pelo principio zero o motor mostra e MARCA, e a tela
   desenha "ja possui". Foi assim que o Pathbuilder tambem resolveu -- ele
   mostra em vermelho o que nao se pode pegar.
4. O motor para de emitir `grant_feat com alvo nao resolvido pelo pipeline`.
5. Os 9 portoes seguem verdes.
6. Na comparacao com o Pathbuilder, `Hobnobber` sai da divergencia.
