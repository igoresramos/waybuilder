---
spec: alias-de-magia-renomeada
req: WB-022
project: waybuilder
version: 1
status: implementada
created: 2026-07-30
altera: [WB-002]
todo: 83
---

# Spec -- as 159 magias que o Remaster renomeou e a base nao registra

## O problema

O Remaster renomeou magia em massa: `Magic Missile` virou `Force Barrage`,
`Mage Armor` virou `Mystic Armor`, `True Strike` virou `Sure Strike`. A base
carrega o nome NOVO, que e o certo -- e nao guarda o antigo em lugar nenhum.

| | |
|---|---:|
| magias canonicas no dump do AoN | 1.661 |
| com `legacy_id` declarado | 794 |
| **em que o nome MUDOU** | **159** |
| magias da base com `aliases` hoje | **1** |

Consequencias medidas:

- **22 referencias orfas** em `deity.cleric_spell`: a divindade cita a magia
  pelo nome legado e nao ha ponte. O portao 3, depois de virar varredura
  completa, e quem passou a contar.
- **A busca do app nao acha pelo nome antigo.** Existe ate uma verificacao de
  navegador para isso (`verificar-busca-alias.mjs`), e ela so testa o caso de
  FEAT -- porque em magia nao havia alias para testar.

Nao e falha de fonte: **o AoN declara o par**, com `remaster_id` de um lado e
`legacy_id` do outro. E o extrator que emite so o lado canonico e joga o nome
antigo fora.

## Por que sobrou: um no-op silencioso de tres dias

`build.sh` chamava `extratores/magias.py` no laco de re-extracao, e o
`__main__` desse arquivo **so imprime a contagem** -- quem escreve
`saida/magias.json` e `_gerar_saida_magias.py`, que nao estava no laco.
`saida/magias.json` estava parado em **27/07** e atravessou todos os builds
desde entao.

E a segunda ocorrencia do mesmo padrao no mesmo dia (`taticas_kits.py` estava
FORA do laco). O conserto do laco entra junto com esta spec.

## A decisao

O extrator de magias passa a registrar, em `aliases`, o nome de toda entrada
legada que o AoN aponta como antecessora -- e SO quando o nome difere. Mesmo
mecanismo que feat e ancestria ja usam, e `Base.resolver()` ja segue `aliases`
sem mudanca nenhuma no motor.

`Cleanse Affliction` tem TRES antecessores (`Neutralize Poison`,
`Remove Disease`, `Remove Curse`): a lista aceita varios, porque a fonte declara
varios. Nao ha o que escolher.

## O que esta spec NAO resolve, e declara

- **As 635 magias com `legacy_id` e MESMO nome.** Nao ha alias a criar: o nome
  nao mudou.
- **`favored_weapon` de `wb:deity/malthus`,** que cita `Light Crossbow`. O AoN
  nao tem arma com esse nome -- as duas entradas dele se chamam `Crossbow`. E
  inconsistencia entre duas tabelas da propria fonte, e inventar o mapeamento
  seria pior que deixar contado. Fica como a unica orfa do portao 3.
- **Renomeacao fora de magia.** Se aparecer o mesmo padrao em outro kind, e
  medicao propria.

## Como se prova que funciona

1. `wb:spell/force-barrage` responde `aliases` contendo `Magic Missile`.
2. `wb:spell/mystic-armor` idem para `Mage Armor`, e `sure-strike` para
   `True Strike`.
3. `Cleanse Affliction` carrega os TRES nomes antigos.
4. As 22 referencias orfas de `deity.cleric_spell` caem para perto de zero --
   o portao 3 e quem mede.
5. `Base.resolver("wb:spell/magic-missile")` devolve o id canonico.
6. A busca do app acha `Force Barrage` digitando `Magic Missile`.
7. Nenhuma magia ganha alias igual ao proprio nome.
8. Quatro camadas verdes.
