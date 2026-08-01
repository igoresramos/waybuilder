---
spec: alvo-e-salvaguarda-de-magia
req: WB-024
project: waybuilder
version: 1
status: implementada
created: 2026-07-30
altera: [WB-002]
todo: 79
---

# Spec -- a magia na ficha nao diz em QUEM pega nem que salva pede

## O problema

Uma carta de magia de PF2e tem seis linhas: Range, Area, Targets, Duration,
Saving Throw, e o efeito. A base emite tres.

| campo | preenchidos na base | preenchidos no AoN |
|---|---:|---:|
| `alcance` | 1.116 de 1.655 | **1.714** (`range_raw`) |
| `duracao` | 1.099 | **1.658** (`duration_raw`) |
| `area` | 385 | 571 (`area_raw`) |
| **`alvos`** | **0** | **1.234** (`target`) |
| **`salvaguarda`** | **0** | **894** (`saving_throw`) |

Alvo e salvaguarda **nao existem como campo** -- e nao e lacuna de fonte, e
lacuna de leitura: os dois estao no dump do AoN, em texto simples
(`"1 creature"`, `"Fortitude"`), em 1.234 e 894 registros.

## A causa dos outros tres

`magias.py:479` le `fsys["range"]["value"]` -- e `fsys` e o doc do **Foundry**.
Magia sem par no Foundry sai sem alcance, sem area e sem duracao, mesmo com o
AoN preenchido. Sao 539 sem alcance e 556 sem duracao.

Nao ha decisao de precedencia a tomar aqui: nenhum dos dois campos existe nos
dois lados em desacordo -- o Foundry preenche ou nao preenche. O AoN entra como
segunda fonte, na ordem que o resto do schema ja usa.

## As decisoes

1. **`alvos` e `salvaguarda` passam a existir**, lidos do AoN, em TEXTO. O
   Foundry guarda `defense` como slug (`fortitude`) e o AoN como rotulo
   (`Fortitude`); fica o rotulo, porque o campo e para LER na ficha e nao para
   o motor avaliar -- nenhuma regra do construtor pergunta "qual a salva desta
   magia".
2. **`alcance`, `duracao` e `area` ganham fallback para o AoN** quando o
   Foundry nao tem. `prov` diz qual dos dois respondeu, como em todo campo.
3. **Texto cru, sem parse.** `"20-foot burst"` fica assim. Transformar em
   `{tipo, valor}` e outra decisao, e a area do Foundry ja vem estruturada -- os
   dois formatos conviveriam no mesmo campo, que e pior que texto honesto. O
   `area` estruturado do Foundry continua vindo primeiro.

## O que esta spec NAO resolve, e declara

- **`heightened` estruturado** segue em 31% (item 79d). E outro campo e outra
  medicao.
- **Ritual** ganha o mesmo tratamento de `alcance` e `alvos` porque o extrator
  reusa as funcoes de `magias.py`; se a fonte do ritual nao tiver os campos, o
  numero fica onde esta -- sem inventar.
- **Parse de `"1 creature"` em estrutura.** So faz sentido se algum dia o motor
  precisar contar alvos, e hoje nao precisa.

## Como se prova que funciona

1. `wb:spell/abyssal-plague` responde `alvos: "1 creature"` e
   `salvaguarda: "Fortitude"`.
2. `alvos` sai preenchido em ~1.230 de 1.655; `salvaguarda`, em ~890.
3. Magia sem alvo declarado na fonte NAO ganha o campo -- ausencia continua
   sendo ausencia.
4. `alcance` sobe de 1.116 para perto de 1.650, e `prov.alcance` diz `aon` nos
   que vieram do fallback.
5. Nenhum campo que ja vinha do Foundry muda de valor -- o fallback so preenche
   o que estava vazio, e o diff dos fixtures prova.
6. Os 10 portoes seguem verdes; o portao 1 cobra `prov` dos campos novos.
