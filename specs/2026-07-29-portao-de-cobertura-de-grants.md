---
spec: portao-de-cobertura-de-grants
project: waybuilder
version: 1
status: aprovada
created: 2026-07-29
todo: 59
---

# Spec -- o portao que faltava para `grants_completos`

## O problema

`grants_completos` existe para distinguir **"esse registro nao tem mecanica"** de
**"tinha e o pipeline nao converteu"**. Sem ele, `grants: []` significa as duas
coisas e a diferenca some.

Ele foi criado exatamente para isso -- e **ninguem o vigia**. Resultado medido em
2026-07-29: os 1.564 registros que motivaram o campo foram corrigidos, e **724
novos apareceram**, com perfil de kind completamente diferente (spell 438,
heritage 258, feat 27). Ninguem viu, porque nenhum portao pergunta.

Pior que o numero: o campo esta em **tres** estados, e so um serve.

| estado | no `index.json` | no payload do app |
|---|---:|---:|
| `True` | 4.735 | 4.735 |
| `False` | 724 | 724 |
| **`None`** | **5.204** | **0** (o `compactar` descarta nulo) |
| **ausente** | **9.043** | **14.247** |

Ou seja: **14.247 registros (72%) chegam ao app sem resposta nenhuma**, metade
porque o extrator nunca emitiu e metade porque emitiu a chave com valor nulo --
que e pior, porque parece preenchido no `index.json` e some no app.

Por kind, quem nunca emite:

| kind | registros | com doc do Foundry |
|---|---:|---:|
| `equipment` | 6.122 | 4.352 |
| `weapon` | 1.042 | 966 |
| `class-feature` | 841 | 841 |
| `armor` | 216 | 202 |
| `shield` | 125 | 118 |

`class-feature` doi mais: **841 de 841 tem doc do Foundry** e nenhum declara se a
conversao foi completa -- e class-feature e exatamente onde mora o efeito de
subclasse (item 40).

## A decisao

**Portao 10**, com duas reprovacoes e um relatorio.

### Reprova 1 -- `grants_completos` nulo

O campo e um booleano ou nao existe. `None` e a pior das tres respostas: mente de
preenchido no index e evapora no app. **5.204 ocorrencias hoje.**

### Reprova 2 -- kind que emite pela metade

Se um kind declara o campo em ALGUM registro, tem de declarar em TODOS. Emissao
parcial e o estado em que a metrica parece existir e nao cobre:

| kind | emite | nao emite |
|---|---:|---:|
| `feat` | 6.253 | 20 |
| `spell` | 1.638 | 17 |
| `background` | 514 | 10 |
| `deity` | 487 | 1 |
| `archetype` | 243 | 1 |

### Relatorio -- cobertura ZERO, com nome e numero

Kind que nao emite para nenhum registro **nao reprova o portao**, porque
reprovar deixaria o build vermelho ate quatro extratores aprenderem a emitir --
e portao que fica vermelho para de ser lido, que e o defeito que estes portoes
existem para impedir.

Mas **aparece no relatorio com o numero**, por kind, sempre. Metrica sem
contrapartida de erro e propaganda; cobertura zero silenciosa e a mesma coisa
com outro nome.

## O que esta spec NAO resolve, e declara

Nao ensina os extratores de `equipment`, `weapon`, `class-feature`, `armor` e
`shield` a emitir o campo -- sao 8.346 registros e cinco extratores, trabalho
proprio. O portao existe para que esse trabalho seja MEDIDO quando acontecer, e
para que o que ja esta coberto nao regrida no meio do caminho.

## Como se prova que funciona

1. O portao 10 reprova hoje, com 5.204 nulos e 5 kinds pela metade.
2. Depois de trocar os nulos por booleano, a reprova 1 zera.
3. O relatorio lista os 5 kinds de cobertura zero com o total de cada um.
4. Introduzir um registro novo com `grants_completos: None` reprova.
5. Os outros 9 portoes seguem verdes.
