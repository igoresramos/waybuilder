---
spec: aninhamento-de-clausula
req: WB-008
project: waybuilder
version: 1
status: implementada
created: 2026-07-29
todo: 91
---

# Spec -- "X and either Y or Z" tem duas camadas, e o parser so via uma

## O problema

`Marshal Dedication` exige, em RAW, **treino em armas marciais E (Diplomacy OU
Intimidation)**. A base grava:

```json
{"any": [{"proficiency": {"martial":      {">=": "trained"}}},
         {"proficiency": {"diplomacy":    {">=": "trained"}}},
         {"proficiency": {"intimidation": {">=": "trained"}}}]}
```

O AND sumiu. Com o OR achatado, um Clerigo ou um Mago que so tem Diplomacy --
que o background Barkeep da de graca -- libera a dedicacao. O Pathbuilder barra,
e ali ele esta certo.

A causa e uma linha em `pipeline/extratores/feats.py::_clausula_rank`:

```python
conector = "any" if re.search(r"\s+or\s+", resto, re.I) else "all"
```

**Um conector para o grupo inteiro.** A funcao quebra o texto por virgula, `or`
e `and` de uma vez so, perde a posicao estrutural, e depois pergunta apenas "tem
um `or` em algum lugar?". Nao ha suporte a aninhamento.

## Quanto disso existe

Varredura nos 19.706 registros por clausula de rank com `and` e (`or`/`either`)
misturados: **4 candidatos, 1 defeito real**.

Nos outros tres (`golem-grafter-dedication`, `leverage-connections`) pelo menos
um dos alvos e um feat e nao uma pericia, entao `_pericia()` devolve `None`,
`_clausula_rank` desiste, e o parser geral -- que trata `either ... or` na etapa
4, antes do `and` na etapa 6 -- assume e produz o aninhamento certo.

**Consertar mesmo sendo caso unico**, porque o desenho e que esta errado: a
funcao acerta hoje por sorte de vocabulario, nao por estrutura.

## A decisao

Reconhecer a segunda camada **antes** de decidir o conector: quando o texto tem
a forma `<cabeca> and either <a> or <b>`, emitir

```
all[ <cabeca parseada>, any[<a>, <b>] ]
```

Fora desse padrao, nada muda -- a lista pura (`expert in Acrobatics, Athletics,
or Stealth`) continua caindo no conector unico, que ali esta certo.

O recorte e deliberadamente estreito: o parser geral ja resolve as outras formas
compostas, e alargar `_clausula_rank` para uma gramatica completa mexeria em
1.063 clausulas de `proficiency` para consertar uma.

## O que esta spec NAO resolve, e declara

**O defeito irmao do Marshal, no `grants`, NAO e a mesma causa.** Os dois
aparecem no mesmo registro e por isso foram lidos como um so -- errado:

```json
"grants": [{"choice": {"flag": null, "opcoes": 4}},
           {"proficiency": {"diplomacy": "trained"}},
           {"proficiency": {"diplomacy": "expert"}},
           {"proficiency": {"intimidation": "trained"}},
           {"proficiency": {"intimidation": "expert"}}]
```

O pipeline **registra** que havia uma escolha de 4 opcoes e mesmo assim emite as
quatro como IRMAS, concedidas todas. Isso e ChoiceSet nao modelado, nao
achatamento de prosa. Medido: **248 registros** (243 feat, 5 familiar-ability)
tem esse marcador com as opcoes soltas -- o personagem recebe todas as opcoes de
toda escolha. Vai para item proprio, na frente de ChoiceSet.

## Como se prova que funciona

1. `Marshal Dedication` passa a ter
   `all[proficiency martial, any[diplomacy, intimidation]]`.
2. Um Clerigo 2 que so tem Diplomacy **deixa de** atender a dedicacao.
3. Um Guerreiro 2, treinado em marcial e com Diplomacy do Barkeep, **atende**.
4. Os outros tres candidatos da varredura nao regridem -- continuam com o
   aninhamento que o parser geral ja produzia.
5. `expert in Acrobatics, Athletics, or Stealth` continua virando `any` de tres.
6. Os 9 portoes seguem verdes e o total de predicado parseado nao cai.
