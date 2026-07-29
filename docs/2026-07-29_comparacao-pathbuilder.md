# Comparacao com o Pathbuilder -- primeira rodada

2026-07-29. Frente destravada: o Pathbuilder roda local e automatizado (receita
em `docs/2026-07-29_pathbuilder-local.md`), entao da para perguntar a ele o que
ele OFERECE num slot e comparar com o que o Waybuilder oferece.

    node app/verificacao/sonda-pathbuilder.mjs      # colhe da tela do Pathbuilder
    python3 motor/comparar_pathbuilder.py           # compara com o nosso motor

## O que a sonda colhe

O modal de escolha de feat tem QUATRO abas, e comparar so a primeira mente. Num
Fighter 1, com o conteudo legado ligado:

| aba | opcoes | disponiveis | em vermelho |
|---|---:|---:|---:|
| Class Feats | 117 | 10 | 107 |
| Dedication Feats | 225 | 0 | 225 |
| Archetype Class Feats | 0 | 0 | 0 |
| All Feats | 342 | 10 | 332 |

**O Pathbuilder tambem MOSTRA o que o personagem nao pode pegar**, em vermelho,
em vez de esconder -- 107 de 117 na aba de classe. E a mesma decisao do
principio zero do Waybuilder, tomada de forma independente por outro
implementador. Vale como confirmacao externa do desenho.

`Archetype Class Feats` fica vazia enquanto nao ha dedicacao: ali sim ele
esconde, e nos mostramos marcado. Diferenca de design consciente, nao defeito --
por isso a aba nao entra no placar.

## Resultado

| aba | waybuilder | pathbuilder | em comum |
|---|---:|---:|---:|
| Class Feats | 125 | 117 | 117 |
| Dedication Feats | 226 | 224 | 224 |

**Quatro pontos** sobraram de 65 da primeira rodada, e **nenhum e buraco
nosso**: tudo que o Pathbuilder oferece, o Waybuilder tambem oferece. Os 61 que
sairam nao eram defeito -- eram quatro recortes diferentes, e cada um custou
uma investigacao:

### 1. O Pathbuilder renomeia o que a Paizo NAO renomeou

A primeira leitura foi que o remaster tinha encurtado os nomes e a nossa base
servia o legado. **Estava errado, e a verificacao derrubou:**

- a ponte `remaster_id` do AoN nao registra **nenhum** desses pares;
- os nomes curtos (`Heavenseeker Dedication`, `Sword Duelist Dedication`,
  `Viking Guard Dedication`...) **nao existem em nenhum dos 43.686 docs** do
  dump do AoN;
- os nossos (`Jalmeri Heavenseeker`, `Aldori Duelist`, `Ulfen Guard`...) existem
  todos.

O padrao e sempre o mesmo: sai o nome proprio de Golarion -- lugar,
organizacao, pessoa -- e entra um generico. `Razmiran Priest` ->
`Priest of the Living God`; `Magaambyan Attendant` -> `Collegiate Attendant`;
`Farabellus Flip` -> `Flip`. Quase certamente licenciamento: nome de setting e
Product Identity.

**Consequencia: a nossa base nao tem o que corrigir aqui.** Ela esta de acordo
com a fonte. O que existe e uma tabela de traducao, em
`docs/comparacao/equivalencias-pathbuilder.json`, com 22 pares -- dado, nao
codigo.

### 2. "Allow outdated CRB and APG?" nasce Off

Com a opcao desligada o Pathbuilder esconde todo o conteudo pre-remaster, que a
nossa base inclui. Era o que fazia `Dragging Strike`, `Dragon Disciple`,
`Horizon Walker`, `Loremaster` e `Shadowdancer` (todos APG) aparecerem como
buraco nosso. A sonda agora liga o interruptor -- que e um
`<label class="switch">` com o checkbox dentro, e nao o texto do rotulo.

### 3. Renomeacao de verdade -- a que a Paizo fez

`Drow Shootist Dedication` aparecia como falta nossa. Nao e: a Paizo renomeou
para **`Crossbow Infiltrator Dedication`** no remaster, a fusao do pipeline
registrou isso em `aliases`, e o Pathbuilder e que ainda oferece o nome antigo
(com o conteudo legado ligado). O comparador passou a casar tambem por `aliases`.

Junto veio outra armadilha de contagem: com alias, um registro entra na tabela
com varias chaves. Contar CHAVES faz quem casou pelo alias aparecer como sobra
pelo nome canonico; e guardar so o primeiro registro de cada chave faz o
DESMEMBRADO (`Dueling Dance (Fighter)`, criado por colisao de identidade) virar
sobra quando o irmao dele ja casou. A conta e: um candidato casa se QUALQUER
chave sua aparece do outro lado.

### 4. Ruido de grafia

Sufixo de desambiguacao que NOS acrescentamos ao desmembrar colisao de
identidade (`Guardian's Deflection (Fighter)`), apostrofo tipografico e caixa
(`Needle In The God's Eyes` x `Needle in the Gods' Eyes`). Tratado em `norm()`.

## Os quatro pontos que sobraram

Todos do MESMO lado -- registros que temos e o Pathbuilder nao oferece:

| ponto | leitura |
|---|---|
| `Stance Savant` | CRB nivel 14, **nao existe no dump do AoN** -- removido no remaster, e a nossa base o carrega do Foundry legado. O unico a decidir: fica ou sai |
| `Chelaxian Scion Dedication` | Pathfinder #223: Hell's Destiny, uncommon -- AP recente |
| `Knight Vigilant` | Character Guide, uncommon |
| `Venture-Gossip Dedication` | Paizo Blog -- fonte que o Pathbuilder pode nao indexar |

**Nenhum e defeito de motor e nenhum e falta de dado nosso.** Um e sobra de dado
legado; tres sao recorte de fonte do outro lado.

Vale dizer o que isso NAO prova: a comparacao cobre um slot, de uma classe, num
nivel. Ela ficou limpa; os proximos alvos e que vao dizer se continua.

## O que o comparador NAO decide

Ele levanta pontos, nao arbitra. `so no Waybuilder` pode ser acerto nosso: a
houserule muda o que cabe num slot, e o Pathbuilder nao a implementa. A fonte
de regra continua sendo o livro; o Pathbuilder vale como **segundo
implementador do mesmo RAW**, e o que importa e onde os dois discordam.

## Proximos alvos

1. Outras classes (a sonda so monta o default: Human / Barkeep / Fighter)
2. Outros slots -- `skill_feat`, `general_feat`, `ancestry_feat`
3. Niveis mais altos, onde o predicado tem mais o que errar
4. Comparar tambem o RESULTADO (proficiencia em numero) via export JSON

## Segunda rodada -- outros slots, outros niveis (2026-07-29)

A sonda passou a aceitar **classe, nivel e slot** por argumento, e a descobrir
as abas do modal em vez de usar lista fixa (elas mudam por slot: `Class Feat`
abre quatro, `General Feat` abre uma, `Skill Feat` tem as suas). Colhidos:
`Fighter 1/6 class_feat`, `Fighter 2 skill_feat`, `Fighter 3 general_feat`.

A categoria mais valiosa apareceu so aqui: **discordam se atende**. Duas
familias, e as duas sao reais.

### Defeito nosso, ja corrigido: proficiencia de arma NOMEADA

10 dedicacoes exigem treino numa arma especifica
(`weapon:aldori-dueling-sword`, `weapon:butterfly-sword`), e **ninguem preenche
essa chave** -- a ficha guarda rank por CATEGORIA. Um Guerreiro 6, treinado em
arma avancada desde o nivel 1, aparecia untrained na Aldori Dueling Sword e a
dedicacao saia como fora do requisito.

Corrigido nos dois motores: `_rank_de_arma` resolve a chave nomeada pela
`weapon_category` da arma na base, e o rank nomeado continua ganhando quando
existe (feat que treina uma arma especifica e mais preciso que a categoria). Um
Mago 6 continua barrado -- a ponte nao afrouxa. 3 assercoes novas.

### Defeito nosso, medido e NAO corrigido: requisito perdido

42 dedicacoes que nos liberamos e o Pathbuilder barra. A causa e a mesma em
todas: o `requires` da nossa base tem **so o nivel**, e a prosa do
pre-requisito diz mais.

    Godless Healing    requires: {character_level >= 2}
                       prosa:    "Trained in Medicine; Battle Medicine"
    Automatic Knowledge requires: {character_level >= 2}
                       prosa:    "expert in a skill with Recall Knowledge; Assurance"

Medido na base inteira: **178 feats** com `requires` so de nivel e prosa citando
pre-requisito. Nem todos sao parseaveis -- parte e narrativa ("member of the
Gray Gardeners", "Exposure to the Well of Axuma"), e pelo principio zero essas
sugerem em vez de bloquear. Mas a fatia mecanica e clara e vale um passo de
pipeline. **Item 86 do TODO.**

### Diferenca de modelo, nao defeito

8 casos em que nos barramos e o Pathbuilder libera: dedicacoes que exigem
pericia treinada, num personagem de comparacao que ainda nao escolheu pericia.
O Pathbuilder trata "pode vir a ter" como disponivel; nos avaliamos o estado
atual e MARCAMOS em vez de esconder. Os dois comportamentos sao defensaveis, e o
nosso e o que o principio zero pede.

## Terceira rodada -- Wizard, Cleric e Rogue (2026-07-29)

A sonda travava em Wizard e Cleric por um motivo que nao era do slot: ao trocar
para essas classes, a barra de menu da FICHA ganha uma aba com o nome da propria
classe, que nao cabe na largura e fica no DOM com tamanho zero. A descoberta de
abas varria `.section-menu` sem escopo e clicava nessa aba fantasma. Escopada
para `.modal:visible .section-menu`.

Com as tres classes colhidas, dois ajustes derrubaram o ruido de **5.846 para
44 pontos**:

1. **Mais quatro pares de nome proprio removido**, o mesmo padrao ja conhecido,
   agora fora das dedicacoes: `Helt's Spelldance` -> `Spelldance`,
   `Devrin's Dazzling Diversion` -> `Dazzling Diversion`,
   `Stella's Stab and Snag` -> `Stab and Snag`,
   `Fane's Fourberie` -> `Card Sharp's Fourberie`. A tabela vai a 26 pares.
2. **A aba `All Feats` saiu do placar** -- ela nao recorta nada do lado deles, e
   do nosso o slot de class feat aceita todo feat de arquetipo (RAW), entao a
   comparacao virava 2.253 contra 341. Ruido por desenho, nao achado. E a aba
   `Class Feats` passou a excluir quem tem trait `archetype`: os 11 feats de
   mascara do Wizard (Pathfinder #174) carregam `wizard` junto com `archetype`,
   e o Pathbuilder os poe na aba de arquetipo.

Placar depois disso:

| classe | Class Feats | Dedication Feats |
|---|---|---|
| Rogue 2 | **zero divergencia** | 22 (a familia conhecida) + 3 de fonte |
| Wizard 2 | 1 | 15 + 3 de fonte |
| Cleric 2 | 3 | 14 + 3 de fonte |

Os `3 de fonte` sao sempre os mesmos tres: `Chelaxian Scion`, `Knight Vigilant`,
`Venture-Gossip` -- fontes que o Pathbuilder nao indexa. A familia restante e a
mesma ja descrita: dedicacoes que exigem pericia treinada, num personagem de
comparacao que ainda nao escolheu pericia.
