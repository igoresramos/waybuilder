---
spec: alias-legado-fora-de-magia
req: WB-023
project: waybuilder
version: 1
status: implementada
created: 2026-07-30
todo: 84
---

# Spec -- quem procura `Gnoll` nao acha `Kholo`

## Como o item apareceu

Na 4a rodada de comparacao com o Pathbuilder (Barbaro 6), ele oferecia
`Reckless Abandon` e nos nao. Investigado: o Barbaro teve esse feat RENOMEADO
para `Desperate Wrath` no Remaster, e nos temos o novo. Recorte de edicao, como
`Lightning Snares` na rodada 3 -- a sonda liga "Allow outdated CRB and APG" de
proposito.

Mas ao conferir apareceu outra coisa: **`Desperate Wrath` nao tem `Reckless
Abandon` como alias.** Quem digitar o nome antigo acha apenas o feat GOBLIN
homonimo (nivel 17, traits `fortune`/`goblin`) -- silenciosamente errado.

Em 30/07 esse buraco foi fechado para MAGIA (159 renomeacoes). Fora de magia,
continuava aberto.

## O tamanho, e as tres guardas que a medicao exigiu

O AoN declara o par com `legacy_id`. A regra crua -- "o doc legado tem outro
nome, entao vira alias" -- pega **1.606** registros e a maioria e lixo. Tres
guardas, cada uma achada olhando o resultado:

| guarda | descarta | por que |
|---|---:|---|
| categoria do legado igual a do canonico | 249 | `wb:class-feature/panache` ganharia o alias **"Swashbuckler"** -- o nome da CLASSE, nao o antigo |
| nome legado nao e nome de classe | (junto acima) | mesma causa |
| um nome nao e prefixo do outro | 1.022 | `Ablative Armor Plating (Lesser)` aponta para `Ablative Armor Plating`: e o doc de GRAU apontando para a base, nao renomeacao |

Sobram **335 renomeacoes de verdade**: equipment 217, weapon 57, feat 31,
heritage 12, ritual 9, armor 7, ancestry 2.

Amostra: `Gnoll -> Kholo`, `Grippli -> Tripkee`, `Remorhaz Armor -> Smoldering
Armor`, `Assassin Vine Wine -> Arbor Wine`, `Choker-Arm Mutagen -> Bendy-Arm
Mutagen`. E o mesmo padrao das 35 renomeacoes do Pathbuilder ja mapeadas: sai o
nome com Product Identity, entra o generico.

## As decisoes

1. **O alias e o NOME antigo**, na mesma forma que magia, feat e ancestria ja
   usam. `Base.resolver()` ja segue `aliases` sem mudanca nenhuma no motor.
2. **Nao apaga alias existente**: acrescenta. Um registro pode ter mais de um
   antecessor.
3. **Homonimo vivo nao veta o alias.** `Reckless Abandon` existe como feat
   goblin de nivel 17, e `Desperate Wrath` passa a carrega-lo como alias assim
   mesmo. `resolver()` devolve o registro VIVO quando o id existe, entao nao ha
   ambiguidade de resolucao -- e na busca, mostrar os dois com o nome atual de
   cada um e mais informativo que esconder um.

## O que esta spec NAO resolve, e declara

- **Os 1.022 pares de GRAU** descartados pela terceira guarda. Nao sao
  renomeacao; o caso deles saiu na spec `grau-legado-nao-fundido`.
- **Os 249 com categoria divergente.** Sao docs de class-feature cujo legado e o
  doc da propria classe. Se algum dia um deles for renomeacao real, vai precisar
  de outro criterio que nao o `legacy_id` cru.

## Como se prova que funciona

1. `wb:ancestry/kholo` responde `aliases` contendo `Gnoll`; `tripkee`, `Grippli`.
2. `wb:feat/desperate-wrath` responde `Reckless Abandon`.
3. `Base.resolver("wb:ancestry/gnoll")` devolve `wb:ancestry/kholo`.
4. `wb:class-feature/panache` NAO ganha o alias "Swashbuckler".
5. `Ablative Armor Plating (Lesser)` NAO ganha alias.
6. Nenhum registro perde alias que ja tinha, e os 10 portoes seguem verdes.
