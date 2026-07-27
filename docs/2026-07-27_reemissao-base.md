---
projeto: waybuilder
tipo: verificacao de re-emissao
data: 2026-07-27
base_anterior: 18.176 registros (v1, auditada em 26/07)
---

# Re-emissao da base sob a spec v2

Verificacao do que a re-emissao mudou, com o numero de cada afirmacao medido
sobre `pipeline/base/index.json`. A base v1 esta preservada em
`pipeline/base/index_v1_backup.json` para comparacao.

## O defeito critico (A1 / TODO 24): a fusao por prosa

A v1 deletava o registro absorvido e decidia por similaridade de texto. A v2
funde so com `remaster_id`/`legacy_id` declarado pelo AoN, veta cruzamento de
categoria e **nao deleta nada**.

Os casos concretos que a auditoria citou como perda de dado, na base nova:

| caso | v1 | v2 |
|---|---|---|
| `Poi` (20 gp) | absorvido por `Shield Bash`, deletado | existe, `wb:weapon/poi`, preco 20, sem `superseded_by` |
| `Tonfa` (10 gp) | absorvido por `Shuan Ji` (mesmo livro) | existe, preco 10 |
| `Kris` (70 gp), `Kalis` (300 gp) | absorvidos | existem, precos proprios |
| `Thorn Whip`, `Atlatl`, `Wooden Taws` | absorvidos | existem |
| `Evasion` (class-feature) | destruida, quebrou 5 entradas de `progressao` | existe |
| familia Aeon Stone | **1** registro, nivel 1, sem preco | **38** registros; `Orange Prism` nivel 16 / 975.000 cp e `Clear Spindle` nivel 7 / 32.500 cp de volta |

Das 38 Aeon Stones, **5** carregam `superseded_by` -- exatamente as que o AoN
declara como substituidas. As outras 33 sao entradas vigentes, e continuam
escolhiveis.

Fusoes da v2, por amostragem: `Aasimar's Mercy` -> `Celestial Mercy`,
`Align Ki` -> `Align Qi`, `Angelic Magic` -> `Celestial Magic`. Sao renomeacoes
de remaster de verdade, nao itens de familia colapsados.

**Precisao, medida do jeito que faltava na v1.** Amostra aleatoria de 12
fusoes (seed 20260727), cada uma reconferida contra o `remaster_id` do doc do
AoN: **12/12 confirmadas**. Na v1, a mesma checagem sobre 60 pares deu 21/60
(35%). Exemplos da amostra: `Power Attack` -> `Vicious Swing`,
`Ganzi Gaze` -> `Nephilim Eyes`, `Horseshoes of Speed` ->
`Alacritous Horsehoes`, `Bracers of Armor III` -> `Bands of Force`.

E a metrica agora tem os dois lados: recall (pares declarados que a base
resolveu) **e** precisao (fusoes que a fonte confirma). "Zero par nao unido"
sozinho nao volta a passar por sucesso -- fundir tudo com tudo tambem daria
zero.

**Numeros da fusao:** 734 pares declarados pela fonte, 655 fundidos (441 com
mudanca anotada em `historico[].mudou` -- errata de nivel/preco ou
consolidacao), 79 vetados por categoria diferente (quase todos class-feature
cujo `remaster_id` aponta para a classe), 136 alvos declarados que a base ainda
nao tem. **Nenhum registro deletado.**

## Cobertura

| kind | v1 | v2 | censo AoN vigente |
|---|---|---|---|
| `ritual` | 0 | 151 | 145 |
| `relic` | 0 | 122 | 122 |
| `language` | 0 | 117 | 117 |
| `background` | 332 | 514 | 499 |
| total | 18.176 | 19.359 | -- |

`ritual` e `background` passam do censo porque o AoN conta so o vigente e a
base guarda tambem o legado marcado -- e o principio "nada e descartado".

## Prosa

| metrica | v1 | v2 |
|---|---|---|
| registros com prosa | 17.269 / 18.176 = **95,0%** (reportado como 100%) | 19.191 / 19.359 = **99,1%** |
| registros sem prosa | 907 | 168 |
| chaves de prosa orfas | 597 | 0 |

O denominador agora e a base inteira. Os 168 restantes sao equipamento de
"tesouro" sem texto de regra em fonte nenhuma (gemas, objetos de arte) e tres
bardings.

## Divergencia

`conflitos` registrados subiram de 2.299 para **2.759**, com `traits` fora da
conta (virou uniao). O numero da v1 era piso: seis kinds nao instrumentavam
conflito nenhum.

## Estado dos portoes

Rodando `python3 pipeline/portoes.py` ao fim do pipeline:

| portao | estado |
|---|---|
| 1 prov por campo, vocabulario fechado | PASSA (0 campos sem prov valido; a v1 tinha 2.694 sem `prov.text` e 152 `"desconhecida"`) |
| 2 level/rank divergente sem conflito + espelho `rank==level` | PASSA |
| 3 referencia `wb:` quebrada | **falha residual**: de 111 citacoes / 61 ids na v1 para 12 citacoes / 10 ids |
| 4 queda de cobertura contra o build anterior | PASSA |
| 5 license presente e xref nao vazio | PASSA (os 6 da v1 eram falha de casamento, nao de licenca) |
| 6 traits disjuntos sobrando | PASSA |
| 7 colisao de identidade detectada antes da fusao | PASSA |
| 8 kind com 2+ fontes e zero divergencia | em correcao |
| 9 cobertura contra o censo do AoN | em correcao (`familiar-ability` 133/142) |

### Sobre os ids que seguem quebrados

Dos 61 ids da v1, 51 foram resolvidos: parte por casamento de nome legado
(`Mage Hand` -> `Telekinetic Hand`), parte por sufixo de familia (o parser le
"Enigma Muse", o registro se chama "Enigma"), parte por mapa curado e
verificado em `pipeline/aliases_referencias.json` (as causes do Champion --
`Paladin`/`Redeemer`/`Liberator` viraram `Justice`/`Redemption`/`Liberation` no
Player Core 2; `Wild Order` virou `Untamed Order`).

Os que sobram tem causa conhecida e escrita: as callings miticas vivem num
**subdiretorio** do pack de class-features que o extrator nao lia,
`universalist-wizard` e uma escola do Legacy sem sucessora no remaster, e
`underworld-connections` nao existe em nenhuma das tres fontes.
