---
spec: portao-de-campo-critico
req: WB-068
project: waybuilder
version: 1
status: implementada
created: 2026-07-31
altera: [WB-002]
todo: [113]
---

# Spec -- o portao que conta CAMPO, e nao registro

## O que aconteceu, e por que nenhum portao viu

Em 31/07, ao regenerar a base para o item 111, apareceu que
`recuperar_mecanica_equipamento.py` estava quebrado **nas duas fontes**, e ha
semanas: o caminho do Foundry era fixo em `dados_brutos/foundry/` quando esta
maquina tem `foundry_repo/`, e o do AoN apontava para nomes de arquivo que nao
existem mais. Ele imprimia

```
fontes: foundry=0 itens, aon=0 itens
```

e seguia em frente. **53 armas perdiam `damage` a cada rebuild** -- `Blowgun`,
`Fist` e `Shield Bash` entre elas. A base versionada sobrevivia so porque
carregava o dado de um build antigo, feito quando o clone tinha o outro nome.

Os dez portoes passaram o tempo todo:

| portao | por que nao viu |
|---|---|
| 4 -- cobertura | conta REGISTRO por kind. As 53 armas continuaram existindo, so ficaram sem dano |
| 8 -- artefato | cobre arquivo que sumiu do disco, nao campo que sumiu do registro |
| 10 -- grants | cobre `grants_completos`, nao mecanica de equipamento |

> **O buraco tem nome: nenhum portao conta CAMPO.** Um registro pode perder o
> dado que o torna util e continuar contando como cobertura.

## O portao 11

Para cada kind com campo critico declarado, quantos registros tem o campo
preenchido. Falha quando esse numero **cai** em relacao ao build anterior --
mesma semantica do portao 4, um nivel abaixo.

Os campos criticos **nao sao lista nova**: ja estao declarados em
`recuperar_mecanica_equipamento.py`, no dict `CRITICO`, e sao a definicao que o
projeto ja usa para "registro sem isto nao serve".

```python
CAMPO_CRITICO = {
    "weapon": "damage",
    "armor":  "ac_bonus",
    "shield": "ac_bonus",
}
```

O portao IMPORTA esse dict em vez de copia-lo. Duas listas do mesmo conceito
divergem -- e a licao do `DEFAULT` do comparador, que ficou em 13 classes
enquanto o mundo tinha 27.

## Por que "cai" e nao "existe um limiar"

Tentador escrever "toda arma tem de ter `damage`". Nao passaria hoje, e nao
deveria: sobram 102 registros sem o campo critico depois do conserto, e a
maioria e conteudo que a fonte realmente nao mecaniza (bombas com dano por
formula, itens de aventura). Exigir 100% faria o portao nascer vermelho, e
portao que nasce vermelho e desligado na primeira semana.

A pergunta certa e a do portao 4: **piorou?**

## Onde grava a linha de base

Em `base/_cobertura.json`, que ja existe e ja e o arquivo do portao 4 --
ganha uma chave `por_campo_critico`. Sem arquivo novo: mais um lugar para
esquecer de gravar.

```json
{"total": 20162,
 "por_kind": {"weapon": 1038, "...": 0},
 "por_campo_critico": {"weapon.damage": 995, "armor.ac_bonus": 214,
                       "shield.ac_bonus": 122}}
```

Grava junto com o resto, por `--gravar-cobertura`. Linha de base ausente
devolve `None` (n/a), igual ao portao 4 -- nao falha, avisa.

## Fase

`final` apenas. Na fase pre-fusao o campo ainda esta sendo montado por
`recuperar_mecanica_equipamento`, e cobrar antes seria cobrar de um estado
intermediario.

## Como se prova que funciona

1. Com a base atual, o portao 11 **passa** (nenhuma queda contra a linha
   gravada).
2. Reverter o conserto do caminho em `recuperar_mecanica_equipamento.py` faz o
   portao 11 **falhar**, apontando `weapon.damage` e o numero da queda. Este e
   o teste que importa: o portao existe para pegar exatamente isto.
3. `--gravar-cobertura` escreve a chave nova sem quebrar a leitura do portao 4.
4. Base sem linha gravada devolve `n/a`, nao falha.

## O que esta spec NAO resolve, e declara

1. **So tres campos, tres kinds.** `spell` sem `rank`, `feat` sem `level`,
   `class` sem `progressao` sao candidatos obvios e ficam de fora ate alguem
   medir quantos ja nascem vazios hoje -- acrescentar um campo que ja falha em
   massa transforma o portao em ruido.
2. **Nao detecta campo ERRADO, so campo AUSENTE.** Uma arma com `damage`
   trocado passa. Isso e trabalho de `auditar_conflitos.py`.
3. **Nao substitui o alarme na origem.** O passo que le fonte e acha zero
   itens deveria gritar sozinho; hoje ele imprime e segue. O portao e a
   segunda linha de defesa, nao a primeira.
