---
spec: procedencia-e-grafia-de-livro
project: waybuilder
version: 1
status: aprovada
created: 2026-07-30
todo: [38, 52]
---

# Spec -- os dois ultimos residuos de auditoria

Dois itens antigos que ja tinham a DECISAO escrita no proprio TODO e faltava
executar. Esta spec e o registro do que foi feito e do porque.

## Item 52 -- `prov: "desconhecida"` e um nao-resposta que passa no portao

Eram 684 campos em 29/07 e sobraram **12** (11 `legado_de` + 1
`area_of_concern`). Todos vinham do mesmo ramo de `reconciliar.fundir()`: ao
herdar um campo que o registro base tinha vazio, a procedencia saia
`(outro.prov).get(k, "desconhecida")`.

O portao 1 nao pega isso porque ele cobra que `prov` **exista**, e
`"desconhecida"` existe.

**A decisao:** usar `_origem` como reserva -- exatamente o que a fusao de
`traits` ja fazia oito linhas acima no mesmo arquivo. O registro doador sempre
sabe de que fonte veio, mesmo sem `prov` para aquele campo. Nao foi preciso
inventar valor nem afrouxar o portao.

Resultado medido: **0** campos com `prov` desconhecida ou vazia.

## Item 38 -- a mesma obra com duas grafias

Eram 176 registros com `source.book` fora do mapa canonico. O mapa
`fora_do_aon` (46 obras) ja tinha resolvido quase tudo; sobrou **1**:
`Age of Ashes #6: Broken Promises`, do pf2etools, contra
`Pathfinder #150: Broken Promises`, do AoN.

A regra do item e explicita: *"resolver com mapa de siglas verificado, nunca
por chute"*. A verificacao aqui nao depende de memoria externa -- ela sai do
proprio mapa: o AoN ja traz `145 hellknight hill`, que e o volume 1 de Age of
Ashes, e `150 broken promises`. A serie ocupa #145-#150, entao o volume 6 e o
#150, e o subtitulo bate palavra por palavra. E no dump do AoN a unica coisa
com "Age of Ashes" no nome e o *Player's Guide*, que e outra obra.

**A decisao:** um `SINONIMOS_VERIFICADOS` em `gerar_canonico_livros.py`, com o
raciocinio da verificacao no comentario. Nome de COLECAO em vez de numero de
volume vai reaparecer a cada dump novo do pf2etools, entao o gancho vale mais
que a entrada.

Resultado medido: **0** registros fora do canonico.

## Como se prova que funciona

1. Nenhum campo da base tem `prov` `"desconhecida"`, vazia ou nula.
2. Nenhum `source.book` fica fora de `canonico_livros.json`.
3. `wb:feat/invulnerable-juggernaut` sai com `Pathfinder #150: Broken Promises`.
4. Quatro camadas verdes, e **zero** diff de fixture -- nenhuma das duas mexe
   em numero de ficha.
