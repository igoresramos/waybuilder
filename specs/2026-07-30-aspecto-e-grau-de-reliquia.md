---
spec: aspecto-e-grau-de-reliquia
project: waybuilder
version: 1
status: aprovada
created: 2026-07-30
todo: 61
---

# Spec -- o item 61 estava errado: nao e extrator redundante, e dado perdido

## O que o item dizia

O item 61 media `extratores/relicos_idiomas.py` e concluia: *"e trabalho
duplicado que ninguem consome, nao um buraco"*, porque `aon_kinds.json` cobre
mais registros (122 de 122 relic contra 51; 121 de 123 language contra 95). A
decisao pendente era **tirar do runner ou promover a fonte**.

A contagem estava certa. A conclusao nao: ela comparou **registros**, e a
pergunta certa era sobre **campos**.

## O que a medicao por campo mostra

Conferindo campo a campo os 239 registros do extrator dedicado contra a base:

| campo | registros | a base tem? |
|---|---:|---|
| `relic` (`aspect`, `grade`, `school`, `element`) | 122 | **nao** |
| `texto` | 239 | nao -- e resto de schema v1 (a prosa mora em `text`) |
| `aliases_traits` | 30 | nao -- idem |
| `requires_texto` | 17 | nao |

O `relic` e mecanica de verdade: em PF2e o dom de reliquia e organizado por
**aspecto** (o tema: Beast, Celestial, Air...) e **grau** (minor/major/grand),
e e o grau que define quando o dom entra. Sem isso a base tem 122 reliquias que
o construtor nao consegue ordenar.

E o extrator dedicado nao inventa nada: `aspect` vem do campo `aspect` do AoN,
que existe em **233 de 233** docs de reliquia, e `grade` sai do campo `type`
(`"Relic Minor Gift"` -> `minor`). Mais uma vez o AoN publica e ninguem le --
o mesmo padrao de `alvos`/`salvaguarda`, `access`, `heighten_level`, do
`attribute` de background e dos alias legados.

## A decisao: portar o campo, nao ligar a segunda fonte

Havia tres caminhos:

1. ligar `relicos_idiomas.json` no `reconciliar.ENTRADA` -- **recusado**:
   deixaria duas fontes para o mesmo kind, com conflito e manutencao dobrada, e
   ainda exigiria migrar o extrator para o schema v2 antes (ele emite `texto` e
   `aliases_traits`, que nenhum outro extrator emite);
2. remover do runner -- **recusado**: perderia o `relic`, que e o unico motivo
   pelo qual o arquivo importa;
3. **portar as ~6 linhas de `aspect`/`grade` para `aon_kinds.py`** e deixar o
   dedicado sair do runner. Uma fonte, sem merge, e a conclusao do item 61
   ("tirar do runner") passa a valer sem perder dado.

Fica o caminho 3.

`relicos_idiomas.py` **nao e apagado** -- sai de `rodar.py::EXTRATORES`. A
regra do projeto e mencionar dead code, nao deletar, e o arquivo ainda e o
registro escrito de como o grau se deriva.

## O que esta spec NAO resolve, e declara

- **`requires_texto` em 17 reliquias** ("The relic is a weapon."). E requisito
  de mesa, e cabe no mesmo tratamento de `requires_residuo`; nao entra aqui
  porque o AoN publica em `prerequisite` e quem le esse campo e outro caminho.
- **`element`/`school`** entram junto no bloco por serem o mesmo campo do AoN,
  mas nada no motor os consulta ainda.
- **Nenhum termo de predicado novo.** A base passa a ter o dado; quem pergunta
  "de que aspecto e esta reliquia" e trabalho de outro item, quando houver
  consumidor -- mesmo criterio que segurou o item 96.

## Como se prova que funciona

1. `wb:relic/absorb-injury` responde `relic.aspect == ["soul"]` e
   `relic.grade == "minor"`.
2. As 122 reliquias da base tem `relic.grade` em `minor|major|grand`.
3. `prov.relic == "aon"` em todas -- portao 1 continua verde.
4. `relicos_idiomas.py` some de `rodar.py::EXTRATORES` e o arquivo continua no
   disco.
5. Quatro camadas verdes.
