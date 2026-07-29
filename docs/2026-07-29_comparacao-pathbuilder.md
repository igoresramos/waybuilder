# Comparacao com o Pathbuilder -- primeira rodada

2026-07-29. Frente destravada: o Pathbuilder roda local e automatizado (receita
em `docs/2026-07-29_pathbuilder-local.md`), entao da para perguntar a ele o que
ele OFERECE num slot e comparar com o que o Waybuilder oferece.

    node app/verificacao/sonda-pathbuilder.mjs      # colhe da tela do Pathbuilder
    python3 motor/comparar_pathbuilder.py           # compara com o nosso motor

## O que a sonda colhe

O modal de escolha de feat tem QUATRO abas, e comparar so a primeira mente. Num
Fighter 1:

| aba | opcoes | disponiveis | em vermelho |
|---|---:|---:|---:|
| Class Feats | 116 | 10 | 106 |
| Dedication Feats | 221 | 0 | 221 |
| Archetype Class Feats | 0 | 0 | 0 |
| All Feats | 337 | 10 | 327 |

**O Pathbuilder tambem MOSTRA o que o personagem nao pode pegar**, em vermelho,
em vez de esconder -- 106 de 116 na aba de classe. E a mesma decisao do
principio zero do Waybuilder, tomada de forma independente por outro
implementador. Vale como confirmacao externa do desenho.

`Archetype Class Feats` fica vazia enquanto nao ha dedicacao: ali sim ele
esconde, e nos mostramos marcado. Diferenca de design consciente, nao defeito --
por isso a aba nao entra no placar.

## Resultado

| aba | waybuilder | pathbuilder | em comum |
|---|---:|---:|---:|
| Class Feats | 118 | 116 | 115 |
| Dedication Feats | 226 | 220 | 198 |

### Class Feats -- 4 nomes a olhar

- **so no Pathbuilder**: `Flip`
- **so no Waybuilder**: `Farabellus Flip`, `Dragging Strike`, `Stance Savant`

`Farabellus Flip` -> `Flip` e renomeacao do remaster (a Paizo tirou o nome
proprio). Os outros dois precisam de conferencia item a item.

### Dedication Feats -- o padrao e renomeacao do remaster

Sete pares 1:1, todos com a mesma forma: **o remaster encurtou o nome tirando o
lugar ou a organizacao**, e a nossa base ainda serve o nome legado.

| Waybuilder (legado) | Pathbuilder (remaster) |
|---|---|
| Nantambu Chime-Ringer Dedication | Chime-Ringer Dedication |
| Edgewatch Detective Dedication | Detective Dedication |
| Jalmeri Heavenseeker Dedication | Heavenseeker Dedication |
| Nidalese Horselord Dedication | Horselord Dedication |
| Turpin Rowe Lumberjack Dedication | Lumberjack Dedication |
| Lastwall Sentry Dedication | Sentry Dedication |
| Oatia Skysage Dedication | Skysage Dedication |

Sobram 15 so do Pathbuilder e 21 so nossos que a heuristica de sufixo nao
pareou, mas o padrao continua visivel a olho -- `Rivethun Emissary` x
`Spirit Emissary`, `Razmiran Priest` x `Priest of the Living God`,
`Prophet of Kalistrade` x `Prophet of Trade`, `Aldori Duelist` x
`Sword Duelist`, `Ulfen Guard` x `Viking Guard`, `Alkenstar Agent` x
`City Agent`, `Pathfinder Agent` x `Guild Agent`, `Verduran Shadow` x
`Forest Shadow`, `Lepidstadt Surgeon` x `Lightning Surgeon`,
`Magaambyan Attendant` x `Collegiate Attendant`, `Kitharodian Actor` x
`College Actor`, `Scion of Domora` x `Scion of the God Caller`.

Isto liga direto ao item do TODO sobre **69 registros servindo conteudo
pre-remaster sem contrapartida**: a comparacao acabou de dar nome a uma dezena
deles, e o Pathbuilder serve como lista de destino.

Quatro nossos parecem nao ter contrapartida com "Remaster: On":
`Dragon Disciple`, `Horizon Walker`, `Loremaster`, `Shadowdancer` -- coerente
com terem sido removidos, nao renomeados. Conferir antes de agir.

## O que o comparador NAO decide

Ele levanta pontos, nao arbitra. `so no Waybuilder` pode ser acerto nosso: a
houserule muda o que cabe num slot, e o Pathbuilder nao a implementa. A fonte
de regra continua sendo o livro; o Pathbuilder vale como **segundo
implementador do mesmo RAW**, e o que importa e onde os dois discordam.

## Ruido de nome, ja tratado

A primeira rodada acusou 65 pontos; 11 eram diferenca de grafia, nao de regra:

- sufixo de desambiguacao que NOS acrescentamos ao desmembrar colisao de
  identidade (`Guardian's Deflection (Fighter)`);
- apostrofo tipografico e caixa (`Needle In The God's Eyes` x
  `Needle in the Gods' Eyes`).

`norm()` em `comparar_pathbuilder.py` cobre os tres casos. Sem isso o relatorio
enche de falso positivo e esconde o achado real.

## Proximos alvos

1. Outras classes (a sonda so monta o default: Human / Barkeep / Fighter)
2. Outros slots -- `skill_feat`, `general_feat`, `ancestry_feat`
3. Niveis mais altos, onde o predicado tem mais o que errar
4. Comparar tambem o RESULTADO (proficiencia em numero) via export JSON
