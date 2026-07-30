---
project: waybuilder
---

# LOG -- Waybuilder

## 2026-07-30

### Sessao | 11:00-13:30 | seis itens, e a comparacao achando o que a leitura nao acha | igor + claude-code

Sessao autonoma, sem parada. A ordem foi a do plano
(`docs/planos/2026-07-29-backlog-completo.md`), e o padrao do dia se repetiu
tanto que virou o resumo: **a coisa que estava errada quase nunca era a que o
item dizia.**

- **Item 59** -- 8.360 registros (42% da base) nao emitiam `grants_completos`.
  Oito kinds de tres extratores, e nenhum precisava de dado novo: os tres ja
  computavam a resposta e a jogavam fora dentro do `mechanized` da v1.
  `taticas_kits.py` nem estava no laco do `build.sh` -- a saida em disco era de
  27/07 e envelheceu em silencio. **O numero que importa nao e o total: e
  `class-feature` com 608 `false`, 72% do kind**, que agora diz com marca no
  registro o que o item 40 vinha dizendo em prosa.
- **Item 78** -- a tradicao de conjuracao. Dois achados que nao estavam no item:
  a fonte tem o dado ESTRUTURADO (`tradition: ["Occult"]`, 27/28 bloodline,
  27/27 patron, 13/13 eidolon), e **o registro que o jogador PEGA nao e o que
  tem a tradicao** -- o eixo oferece a `class-feature`, que sai com
  `xref.aon: None`. Dois catalogos paralelos, entao entrou um passo que leva o
  campo para a opcao viva, com trava pela classe dona (`psychopomp` existe como
  bloodline E como eidolon). Casar por NOME dava `arcane` ao Draconic -- a
  tradicao da versao LEGADA.
- **Itens 75a/75b + 95** -- `weapon_proficiency` nunca foi lido: `grep` dava um
  hit, dentro de um docstring. 91 ocorrencias, 28 formas gramaticais. E
  `weapon:*` era LETRA MORTA: um Guerreiro expert em tres categorias respondia
  untrained, e cinco feats eram inalcancaveis por qualquer personagem.
- **Item 72 (parte 1)** -- o total de pericia NAO EXISTIA no motor: era
  calculado em `PainelDireito.tsx:94`. Numero que nasce em React nao tem
  oraculo, nao tem paridade e nao tem onde receber `flat_modifier`. Era essa a
  causa de os 462 bonus incondicionais nunca chegarem na ficha.
- **Fatia 3.2 + velocidade** -- resistencia/fraqueza/imunidade (258 grants que a
  ficha ignorava) e Velocidade, que a ficha do COMPANHEIRO tinha e a do
  personagem nao. Junto saiu um defeito velho: `_resolver_valor` devolvia ZERO
  para qualquer expressao que nao fosse inteiro ou `@actor.level` -- 68 das 233
  resistencias sao formula. Virou mini-avaliador da gramatica medida, e o que
  esta fora devolve `None`, nao zero.
- **Fatias 3.3 e 3.6 medidas e decididas FORA** -- ItemAlteration e 86,5%
  cosmetico (`other-tags`, `description`, `name`, `traits`); RollOption nao
  produz numero, produz estado de rolagem, e o app nao rola dado.
- **Item 84, 3a rodada** -- e aqui a comparacao pagou o investimento. Terreno
  novo (ancestry feat, niveis 12/16/20, skill feat fora do Guerreiro) e achou o
  **defeito mais grave do dia**: `has` de class-feature era SEMPRE falso em
  `candidatos()`, porque a guarda de auto-satisfacao comparava `None != None`.
  139 clausulas em 135 registros -- um Magus nunca podia pegar feat de
  Spellstrike. Nenhuma leitura de codigo tinha achado isso em tres sessoes.

**O que eu errei, e o que pegou:**

- Reconstrui a opcao de ChoiceSet como `{rotulo, valor}` porque medi as chaves
  que eu ESPERAVA; 56 das 570 tambem tem `grants`. Quem pegou foi o teste de
  paridade.
- Converti `tipo` de resistencia com `str()` cego e escrevi `"['fire',
  'sonic']"` na ficha do campeao. Quem pegou foi o diff do fixture -- os 122
  testes passavam com o defeito dentro.
- Usei `git stash` para saber se um vermelho era pre-existente e o `pop` travou
  num `.pyc` TRACKED; depois usei `push -f` no master para consertar um commit
  meu de 30 segundos antes. As duas viraram licao; a segunda nao devia ter
  acontecido.
- `npm run build` estava QUEBRADO no HEAD desde ontem, com tres erros de tipo
  que `npx tsc --noEmit` nao pega. A licao ja estava escrita e eu repeti.

Quatro camadas verdes ao fim de cada commit. TODO: 31 -> 28 abertos (3 fechados,
4 parcialmente). 12 commits, todos empurrados.

## 2026-07-29

### Sessao | 17:00-18:00 | tres termos de predicado, e um "nao" que e resposta | igor + claude-code

Fechando a fatia mecanica do residuo (item 87, spec
`2026-07-29-termos-de-predicado.md`). A medicao foi para um agente; o criterio
foi meu: **termo novo so onde a base ja responde.**

- **`sense`** -- `grants.sense` existia em **81 registros e ninguem lia**, mesmo
  padrao do companheiro. O campo tem tres formas na base (dict, string crua, e
  booleano em `senses` de 37 ancestrias) e o termo aceita as tres, com
  `low_light` normalizando para `low-light-vision`. De quebra, a ficha ganhou
  `visao().sentidos` -- ela nao dizia o que o personagem enxerga.
- **`focus_pool`** -- o motor ja calculava o pool (regra 22); faltava expor.
- **`has_actor`** -- le a concessao de companheiro derivada hoje, e responde
  "tem direito ao bicho", nao "ja escolheu a especie".

Resultado: predicado parseado **3.889 -> 3.919 (92,0%)**, frases rejeitadas
inteiras 372 -> 342.

**O "nao" vale mais que os tres "sim".** Alinhamento -- `evil alignment` (7),
`tenets of good` (4), `tenets of evil` (4), `any good alignment` (3) -- **nao
vira termo**: o Remaster aboliu alinhamento de personagem, e na nossa base
`alignment` so existe em `deity`. Modelar exigiria inventar estado de ficha para
responder pergunta de edicao anterior. As 18 clausulas ficam visiveis em
`requires_residuo`, como requisito de mesa -- que e onde uma regra aposentada
deve morar.

**A armadilha do porte, que custou 14 fichas.** O Python despacha termo por
convencao (`getattr(self, f"_termo_{termo}")`); o TS, por `switch` explicito.
Escrevi os seis metodos e esqueci as tres linhas do `switch` -- e ignorar um
termo NAO reprova (principio zero), entao nada estourou: mudou so a ordem da
lista de candidatos, e 14 fichas divergiram do gabarito com uma mensagem
obscura. Nenhum teste de motor pegaria; o de paridade pegou.

### Sessao | 15:10-17:00 | dois defeitos que a comparacao apontou, fechados | igor + claude-code

Igor: *"quero que vc faca tudo, mas planeja legal, tais sempre atualizando a
spec ne?"* -- e, no meio, *"quero q vc tenha mais autonomia e tal, use agentes
sempre que possivel e eficiente"*. As duas frentes sairam com spec antes do
codigo, e a medicao de cada uma foi para um agente em paralelo.

**Requisito parcial (item 86, spec `2026-07-29-requisito-parcial.md`).** A
premissa mudou na medicao: **158 dos 178** alvos ja tem o pre-requisito
estruturado no Foundry, em itens atomicos. Nao era falta de fonte, era o parser
sendo tudo-ou-nada -- `_combinar` devolvia `None` se qualquer clausula falhasse,
entao "Trained in Occultism; you have been in a psychic duel" perdia as DUAS
coisas por causa da segunda, e o gate de nivel preenchia o vazio, disfarcando a
perda de "dado pobre".

Agora o parser emite o que deu e o resto vai por escrito em `requires_residuo`
-- que o motor **nunca** avalia e a tela mostra como *requisito de mesa*. E o
principio zero aplicado ao pre-requisito.

| | antes | depois |
|---|---:|---:|
| predicado parseado | 3.609 (84,7%) | **3.889 (91,3%)** |
| frase rejeitada inteira | 652 | **372** |
| residuo por escrito | 0 | **593** |
| divergencia com o Pathbuilder (Fighter 6, dedicacao) | 52 | **23** |

**Spellcasting de arquetipo (spec `2026-07-29-spellcasting-de-arquetipo.md`).**
13 dedicacoes prometiam conjuracao e a ficha nao mostrava nada. O levantamento
poupou metade do trabalho: **a tabela de slots ja estava no motor**
(`RANK_DEDICACAO`, verbatim da regra, usada como piso da regra 21 desde 27/07).
Faltava saber QUEM esta na rota -- passo 7g -- e que o rank vem do **feat** que
o personagem pegou, nao do nivel dele: quem so tem Basic para no rank 3 mesmo no
nivel 20.

E ai apareceu o defeito maior, que a spec assumia resolvido: **a conjuracao
NUNCA aparecia na tela, nem a de classe**. O bloco existia so em
`src/telas/Ficha.tsx`, que nao e usado por ninguem -- o motor calculava desde
sempre e o jogador nunca via. A ficha ganhou a aba **Magia**, com a elevacao da
regra 17 na de classe e a marca "nao eleva" na de arquetipo.

Antes disso, tres coisas menores: o legado ficou **achavel** (a busca do modal
passou a olhar `aliases`, entao `Power Attack` acha `Vicious Swing`), a sonda
foi consertada para Wizard e Cleric (uma aba fantasma com o nome da classe, fora
do modal, engolia o clique), e a comparacao caiu de 5.846 para 44 pontos com
mais quatro pares de nome proprio removido e o corte da aba `All Feats`.

Verde: 9 portoes, **124 assercoes** no oraculo (eram 106), **113** no TS, e
quatro verificacoes de navegador.

### Sessao | 13:40-15:10 | manter o legado, e a comparacao achando defeito de verdade | igor + claude-code

**Decisao do Igor: manter todo o conteudo legado.** Medido antes de agir, e a
base ja o mantinha -- as tres pilhas da triagem (971 removidos, 339 renomeados,
5.690 intocados) estao **todas dentro dela**, zero fora. A fusao legacy/remaster
tambem nao perde nada: dos 669 pares, 346 guardam o nome antigo em `aliases` e
323 sao pares de nome identico.

O que faltava era o legado ser ACHAVEL: a busca do modal olhava so `nome` e
`id`, entao quem digitasse `Power Attack` -- o nome que se aprendeu na mesa --
nao achava `Vicious Swing`, com o conteudo na base o tempo todo. Corrigido, com
o nome antigo aparecendo na linha para o resultado nao parecer errado, e travado
em `app/verificacao/verificar-busca-alias.mjs`.

De quebra, `triagem_legado.py` voltou a rodar: quebrava num `sort` que compara
`level` int com str, e o relatorio em disco era de 26/07.

**A comparacao com o Pathbuilder virou ferramenta de achar defeito.** A sonda
passou a aceitar classe, nivel e slot, e a descobrir as abas do modal (elas
mudam por slot). Com `Fighter 6` e os slots de pericia e geral, apareceu a
categoria que faltava: **discordam se atende**.

- **Defeito nosso, corrigido:** 10 dedicacoes exigem treino em arma NOMEADA
  (`weapon:aldori-dueling-sword`) e ninguem preenche essa chave -- a ficha
  guarda rank por CATEGORIA. Um Guerreiro 6, treinado em avancada desde o nivel
  1, aparecia untrained na Aldori Dueling Sword. `_rank_de_arma` faz a ponte nos
  dois motores; o Mago 6 continua barrado.
- **Defeito nosso, medido e nao corrigido:** 42 dedicacoes que liberamos e ele
  barra, todas porque o nosso `requires` tem so o nivel enquanto a prosa diz
  mais. Na base inteira sao **178 feats** -- item 86 do TODO.
- **Diferenca de modelo:** 8 casos em que barramos e ele libera. Ele trata "pode
  vir a ter a pericia" como disponivel; nos avaliamos o estado atual e MARCAMOS.
  O nosso e o que o principio zero pede.

Mais: dano fixo de `Blowgun`/`Dart Umbrella` (o AoN escreve `1 P` e o parser
exigia `dN`), e os dois arquivos de dados do Pathbuilder fora do git com
`baixar-assets.sh` no lugar. 112 assercoes no oraculo, 110 no TS.

### Sessao | 12:40-13:40 | os proximos passos, e a hipotese que a fonte derrubou | igor + claude-code

Tres frentes curtas, e a do meio virou a licao do dia.

**Assets do Pathbuilder fora do git.** O autocommit ja tinha versionado os
3,4 MB de `data_remastered71.txt`. Cada versao nova do app troca o nome do
arquivo (`data131` -> `data_remastered71` -> ...), entao versionar somaria
alguns MB PERMANENTES por versao num repo que ja passou por reescrita por peso.
Os dois arquivos de dados sairam do rastreamento (`git rm --cached`, ficam no
disco) e ganharam `baixar-assets.sh`. Mesmo criterio de `dados_brutos/`:
reconstruivel por receita fica fora. O historico nao foi reescrito.

**Dano fixo (TODO 85).** `Blowgun` e `Dart Umbrella` causam **1 ponto**, sem
dado -- e RAW. O extrator exigia `dN` no texto do AoN e deixava as duas sem
`damage`, fora da aba de Ataques, com o dado inteiro em disco. Nenhuma mudanca
de motor foi precisa: a representacao OMITE a chave `dado` em vez de grava-la
como `None`, porque os dois motores fazem `dano.get("dado", "")` e a chave
presente com None imprimiria "None" na ficha. 3 assercoes novas (106 -> 109).

**A hipotese que a fonte derrubou.** O relatorio da sessao anterior dizia que o
remaster tinha encurtado nomes de dedicacao e que a nossa base servia o legado.
Fui corrigir e a verificacao disse o contrario:

- a ponte `remaster_id` do AoN nao registra **nenhum** desses pares;
- `Heavenseeker Dedication`, `Sword Duelist Dedication`, `Viking Guard
  Dedication` e companhia **nao existem em nenhum dos 43.686 docs** do dump;
- `Jalmeri Heavenseeker`, `Aldori Duelist`, `Ulfen Guard` existem todos.

Quem renomeia e o **Pathbuilder**, removendo nome proprio de Golarion -- Product
Identity. A nossa base esta certa e nao tinha o que corrigir. Virou tabela de
traducao (`docs/comparacao/equivalencias-pathbuilder.json`, 22 pares) em vez de
mudanca de dado.

Com isso mais a opcao "Allow outdated CRB and APG?" (nascia Off, escondendo todo
o conteudo pre-remaster que a nossa base inclui), a comparacao caiu de **65
pontos para 5**, e os 5 sao reais:

| ponto | leitura |
|---|---|
| `Drow Shootist Dedication` | existe no AoN e **falta na nossa base** -- o unico acionavel |
| `Stance Savant` | CRB nv14, nao existe no dump do AoN: removido no remaster e carregado do Foundry legado |
| `Chelaxian Scion`, `Knight Vigilant`, `Venture-Gossip` | fonte que o Pathbuilder pode nao indexar (AP recente, Character Guide, Paizo Blog) |

### Sessao | 11:45-12:40 | o Pathbuilder rodando local, e a primeira comparacao | igor + claude-code

**A frente travada destravou por um `grep`.** O app local ficava no spinner
"Loading" para sempre, e duas hipoteses ja tinham sido gastas (asset faltando,
POST recusado). A causa estava no proprio bundle, visivel em
`grep -o "location\.[a-zA-Z]*"`:

    "www.pathbuilder2e.com" == window.location.hostname ? ... : pede permissao e ESPERA

O app so monta em `pathbuilder2e.com`. **A saida nao foi mexer em `/etc/hosts`**:
navega-se para a URL REAL e o Playwright serve tudo do disco por
`page.route()` -- o hostname passa a bater sem que um byte saia da maquina, e o
Cloudflare nunca e contatado. Tres detalhes custaram uma rodada cada: a rota
registrada por ultimo ganha (o catch-all engolia a navegacao), o app redireciona
`www` para o apex (glob com `www.` deixava a segunda requisicao vazar), e o
dialogo de permissao de storage so aparece depois desse redirect. Faltava ainda
`data_remastered71.txt` (3,4 MB) no disco -- e o que o app pede com "Remaster: On".

Com ele de pe, a primeira comparacao real. Num Fighter 1, slot de Class Feat:

| | waybuilder | pathbuilder | em comum |
|---|---:|---:|---:|
| Class Feats | 118 | 116 | 115 |
| Dedication Feats | 226 | 220 | 198 |

Dois achados:

- **O Pathbuilder tambem MOSTRA o que nao se pode pegar**, em vermelho (106 de
  116 na aba de classe). Principio zero confirmado por um segundo implementador,
  de forma independente.
- 22 dedicacoes com nome diferente dos dois lados. **A primeira leitura foi
  errada e a verificacao derrubou** -- ver a sessao seguinte.

Ferramentas que ficam: `app/verificacao/pathbuilder-comum.mjs` (abre o app),
`sonda-pathbuilder.mjs` (colhe as quatro abas do modal) e
`motor/comparar_pathbuilder.py` (compara aba a aba, com normalizacao de nome --
sem ela 11 dos 65 pontos eram grafia, nao regra).

### Sessao | 11:00-11:45 | o companheiro que o motor sabia montar e ninguem podia pegar | igor + claude-code

**A premissa "falta modelar companheiro" era falsa.** O motor implementava
companheiro inteiro nas duas linguagens desde 2026-07-27 -- cap da regra 17b,
maturidade, Specialized, HP, AC, ataques. O buraco estava uma ponta antes:
nenhum registro da base dizia *"eu concedo um companheiro"*, entao o ator so
existia se alguem editasse `doc["atores"]` a mao. Pegar `Animal Companion` no
nivel 1 nao mudava nada na ficha e nao gerava aviso.

Fechado nas quatro camadas, com spec antes do codigo
(`specs/2026-07-29-companheiro-concedido.md`):

- **dado** -- termo novo `grant_actor`, derivado da prosa oficial em
  `derivar_concessao_de_ator.py` (passo **7f**). 12 concessores; 4 de divida
  (construct/undead, que nao tem stat block na base); 1 vetado (`Dragon Grip`
  da ACESSO a especie Riding Drake, nao um companheiro). A ancora em "you
  gain" derruba de 23 para 12 -- `Captain Dedication` e `Necrologist` citam
  companheiro para PROIBI-LO, e outros cinco falam do bicho que voce ja tem
- **motor** -- `_concessoes_de_ator` casa por `concedido_por` + `em`, abre slot
  `companheiro` e serve 96 especies (as outras 17 do kind sao especializacao,
  sem stat block, e nao cabem no slot)
- **regra 17b** -- o cap passa a sair da classe que CONCEDEU, e nao da de maior
  nivel: num `Ranger 3 / Fighter 5` o companheiro do Ranger dava 7 e agora da 5
- **app** -- slot no nivel do feat, escolha gravada em `doc.atores`, aba do bicho
  na ficha com atributos, HP, CA, sentidos, salvaguardas, ataques e support

Prova nas quatro camadas: 9 assercoes novas no Python (97 -> 106), fixture
`ranger3-guerreiro5-companheiro-concedido` comparada campo a campo pelo TS (110
testes), 9 portoes verdes no build completo, e
`app/verificacao/verificar-companheiro.mjs` no navegador, com screenshot em
`docs/screenshots/`.

### Sessao | 07:20-09:00 | a validacao que faltava achou o que os portoes nao viam | igor + claude-code

**Rodar o pipeline inteiro era o passo pendente, e ele nao estava limpo.** Os
nove portoes passaram verdes, mas o teste de paridade com o oraculo Python
acusou o eixo `arcane-thesis` do Mago apontando para um id inexistente.

Causa: `aplicar_aliases_em_requires.py` rodava no passo 4h3, **antes** da fusao
legacy/remaster -- e quem aposenta o id e a fusao. Na sessao anterior o script
tinha sido rodado a mao sobre base ja fundida, e por isso funcionou la e
regrediu aqui. Movido para 7c: 26 -> 47 ids resolvidos.

O caso rendeu tres consertos encadeados, cada um revelado pelo anterior:
- **portao 3 era cego a `subclasses`** -- varria so `requires`, entao nao
  vigiava o campo que o passo 7c conserta. Ampliado, acusou 16 orfas na hora
- **consertar as orfas revelou duplicata**: a mesma causa do Campeao existe como
  `wb:cause/justice` e `wb:class-feature/justice`, em kinds diferentes que a
  fusao nao pareia. Enquanto uma era orfa o app a descartava em silencio; vivas,
  o Campeao passou a oferecer `Justice` duas vezes. Dai `colapsar_opcoes_irmas.py`
  (7d), que mantem quem tem mais sinal -- 15 referencias em 3 classes
- **os nove portoes ficaram verdes sobre isso tudo**, o que motivou
  `app/verificacao/verificar-eixos.mjs`: a checagem final e no navegador

**A premissa das 61 dedicacoes sem mecanica estava errada.** O plano dizia que
so o Pathbuilder resolveria. Medindo uma a uma, o buraco e de MODELO e nao de
fonte: 17 sao proficiencia (o motor sabe), 9 concedem item nomeado (sabe), mas
17 sao modificador numerico, 16 sao companheiro e 14 sao spellcasting de
arquetipo -- e para esses tres o motor nao tem onde guardar a resposta, entao o
Pathbuilder tambem nao ajudaria. `derivar_mecanica_dedicacao.py` (7e) colheu da
prosa oficial o que o motor consome: 5 mecanizadas, 25 com divida declarada.
Numero baixo de proposito -- o passo so emite quando o sujeito da frase e "you"
e o alvo resolve na base. Sem essas guardas, `Rose Warden` dava Stealth de graca
e `Animal Trainer` dava Performance ao jogador em vez de ao bicho.

**Achado colateral, e provavelmente o mais util no dia a dia:**
`sincronizar-base.sh` fazia `rm -rf public/base`. Com o Vite de pe, o servidor
perde o diretorio e passa a responder `index.html` para todo pedido em `/base/`
-- que chega como `Unexpected token '<', "<!doctype "...` **com o arquivo
intacto no disco**. E parte do que o Igor viu ontem, e nao era cache.

Verde no fim: 9 portoes, 97 do oraculo Python, 107 do TS, e os 11 eixos de
sub-escolha conferidos no navegador sem repeticao.

## 2026-07-28

### Sessao | 00:20-07:45 | o app nasceu, e a referencia do Igor o reescreveu | igor + claude-code

**O motor foi portado para TypeScript e roda no navegador.** O gabarito sao as
20 fichas derivadas pelo Python (visao inteira, campos internos, listas de
candidatos): o TS roda os MESMOS documentos e compara campo a campo. **20 de 20
identicas, zero divergencia.** O Python continua como oraculo -- validar_iconics,
teste de carga e os nove portoes rodam nele.

**O porte achou um defeito que 95 testes nao acharam:** `candidatos("subclasse")`
iterava a CONTAGEM de opcoes como se fosse a lista, e levantava TypeError. Nunca
explodiu porque nenhuma ficha de exemplo exercitava aquele slot -- e a tela
exercita. E o terceiro caso do mesmo padrao no projeto: **consumir o dado acha o
que auditar nao acha**.

**A licao cara da sessao foi de PRODUTO, nao de codigo.** Montei o app com tres
abas separadas (criacao / progressao / ficha). O Igor abriu e disse "ta bem
diferente do que eu esperava", e mandou o HTML exportado do Pathbuilder 2e --
que ele **ja usa**. A estrutura real e outra: duas colunas, build a esquerda e
ficha viva a direita, tudo na mesma tela. Com abas, o jogador escolhe um feat e
tem de trocar de tela para ver o numero mudar -- num construtor, o retorno
imediato e o ponto todo.

Reescrito a partir da referencia. Junto vieram dois erros meus que o print
deixou obvios: atributo e MODIFICADOR (`DEX +3`, nao `16`) e pericia mostra o
TOTAL rolavel (`+8`), com o rank como etiqueta -- ninguem rola "expert" na mesa.
E o picker virou MODAL com filtros, lista e o **texto completo** do item:
ninguem escolhe um feat pelo nome.

Carga: 76 KB gzip de app + 511 KB do nucleo. PWA com service worker; a prosa
(6,3 MB) fica fora do pre-cache e entra sob demanda.

Testes: 95 no motor Python, 97 no pipeline, **77 no app** (67 de porte + 10 de
fluxo, que monta um Guerreiro 4 do zero pelo mesmo caminho da tela).

Referencia do Pathbuilder guardada em `docs/referencia/`.

## 2026-07-27

### Sessao | 22:20-23:50 | os 5 itens que faltavam para o app, e a validacao por dominio | igor + claude-code

Igor autorizou trabalho autonomo ("manda bala, faz tudo que tu puder, valida
tudo") e foi dormir. Licenciamento saiu do escopo: o app e para ele e os amigos,
nao vai ser publicado.

**Os cinco itens que separavam o projeto de comecar o front, todos fechados.**

- **Item 71 -- gate travado numa classe.** `derivar_gate_nivel.py` fazia
  `sorted(traits & classes)[0]` e emitia gate de UMA classe. `Reach Spell`
  (7 classes conjuradoras) saia como `class_level: {bard}`: pelo motor, um Mago
  nao podia pega-lo. Agora emite `any`. Na base re-emitida, 125 feats saem como
  "classe (varias)" e 8 como "ancestria (varias)".
- **Item 69 -- eixo `outras-opcoes` como balaio.** Duas causas: o `min(nivel)`
  colapsava niveis diferentes num so (dai o Campeao pedindo escolha no NIVEL 0)
  e uma "escolha" com UMA opcao virava eixo. Agora chaveia por (eixo, nivel) e
  devolve a progressao o que tem opcao unica -- 31 devolvidas em 19 classes.
  Guerreiro e Monge nao pedem mais escolha nenhuma; `Warrior of Legend` voltou
  a ser progressao, que e o que sempre foi.
- **Item 74 -- atributo sem higiene.** Ficha sem boost declarado derivava com
  tudo 10, HP menor e ZERO avisos.
- **Item 65 -- a terceira pergunta do construtor.** O motor sabia dizer "o que
  eu tenho" e "o que esta errado", nunca "o que posso escolher agora, neste
  slot" -- `disponiveis("feat")` devolve os 6.273 feats da base. Entraram
  `slots_abertos()` e `candidatos(slot, em)`, com a distincao que virou spec:
  o slot FILTRA por tipo, o requisito ORDENA e marca.
- **Item 4 -- payload.** O artefato de build e o do app passaram a ser coisas
  diferentes. Indice completo de 2,15 para **1,04 MB gzip**, e o nucleo que
  monta ficha em **0,49 MB** -- abaixo do alvo de 0,53 do projeto.

**Erro meu, achado e corrigido na mesma sessao:** a primeira versao do orcamento
de atributo esquecia os **4 boosts livres da criacao**, e por isso o aviso saia
INVERTIDO -- acusava "6 declarados de 5" numa ficha cujo direito e 9. Fui
conferir na fonte oficial (AoN, Step 6: Finish Attribute Modifiers) antes de
mexer, em vez de escrever de memoria.

**Quatro agentes de validacao por dominio**, como o Igor pediu. O que eles
acharam, com os numeros conferidos por mim depois:

- **Spell e ritual: cobertura COMPLETA contra o AoN** -- 0 ausentes nos dois,
  `level` em 100% dos 1.655 spells, ritual com `level`/`acoes`/`primary_check`
  em 100% dos 151.
- **Runa de potencia FUNCIONA** (ataque +10 -> +11, AC 21 -> 22 verificado em
  ficha). Runa de propriedade nao existe -- e `striking` corta o dano pela
  metade em qualquer personagem acima do nivel 4 (item 77).
- **Tradicao de conjuracao nao resolve** para Feiticeiro, Invocador e Bruxa: as
  48 subclasses que a determinam tem `grants: []` em 100% dos casos. DC e slots
  seguem corretos (item 78).
- **Teste de carga: 285 fichas, ZERO excecoes**, determinismo e invariantes
  limpos. As 6 unicas violacoes eram todas Psychic -- a unica classe sem
  `key_ability`, e por culpa da FONTE (o Foundry declara `[]`).

**O achado que mais valeu, e que nenhuma das quatro frentes tinha como alvo:**
o motor nao resolvia **alias**, e o portao 3 resolvia. A base guarda o nome
pre-remaster como alias (`stunning-fist` = `stunning-blows`, `wild-shape` =
`untamed-form`) -- 348 ids alternativos. O portao passava verde reportando zero
orfaos, enquanto 24 `requires` de feats de classes centrais nunca eram
satisfeitos no motor. **Portao verde escondendo defeito e pior que portao
ausente**, porque da a impressao de que o ponto foi verificado.

**Desempenho:** derivacao de ficha de nivel 20 caiu de 5,76 ms para **0,30 ms**
(19x). O profile mostrou 90% do tempo em `_classes_multiclasse`, que varria os
19.705 registros a cada `Personagem` novo -- cache de instancia onde o
resultado depende so do catalogo. Era o unico ponto cujo custo escalava com o
tamanho da BASE em vez do tamanho da FICHA.

Base re-emitida do zero duas vezes, **nove portoes verdes** nas duas.
Testes: **95 no motor** (eram 28 no inicio do dia) e **97 no pipeline**.
Itens novos: 76 a 83.

### Sessao | 21:35-22:15 | quatro frentes de validacao em paralelo | igor + claude-code

"Validar validar e validar." Quatro agentes, cada um numa frente independente, com
ownership de arquivo declarado. Antes deles, uma varredura propria passou as **226
dedicacoes** pelo motor: zero excecoes, 105 entregam algo, HP mexe em 5 e sempre
exatamente `+nivel` (Toughness), nenhuma proficiencia master/legendary indevida.

**A varredura pegou um erro de metodo meu antes de qualquer agente:** a primeira
medicao usou a ficha do Guerreiro que ja tinha `additional-lore` e `double-slice`
escolhidos, entao `_ja_tenho` bloqueava justamente as concessoes que se queria
medir -- 30 dedicacoes apareceram falsamente como mudas. Com ficha neutra, caem
para 16. Ficha de referencia contaminada mede a ficha, nao o motor.

**A adversarial (Opus, 6.881 derivacoes) achou defeito real no que eu tinha
acabado de commitar**, e os consertos entraram no mesmo dia:

- **Regressao critica.** `Personagem({}, Base())` estourava `StopIteration`: o
  `next` que escolhe o teto de rank nao tinha default e a tupla parava em nivel 1.
  Nivel 0 e o ESTADO INICIAL do construtor, nao caso exotico. Mais tres pontos que
  explodiam com documento malformado. Fuzz agora: **1440/1440** sem excecao.
- **Requisito circular.** Ao aplicar grants de feat, um feat que concede o que
  exige passou a satisfazer o proprio requisito (`acrobat-dedication` exige
  acrobatics trained e concede acrobatics; a ficha saia limpa onde antes
  sinalizava -- 25 termos auto-satisfeitos entre os 6.273 feats com `requires`).
  Consertado rastreando de quem veio cada proficiencia e a RAIZ de cada concessao.
- **Regras de arquetipo cegas** para o que foi concedido, e a cadeia nunca partia
  de ancestria/heranca/background -- 69 alvos validos inertes.

**Um defeito que nenhum agente pegou, e o teste novo pegou:** a ficha dependia da
ORDEM das escolhas no JSON. `ordem_de_classe` era montada na ordem do array, entao
reordenar mudava `primeira_classe` e com ela a regra 8. A adversarial rodou 321
embaralhamentos e passou limpo, porque **so ficha multiclasse com classes entrando
em niveis diferentes expoe** -- e foi uma das fichas que o agente de fichas criou
que revelou. O corpus cresceu no meio da validacao e mudou o resultado dela.

**Achados de DADO, que e onde estava o estrago maior:** 122 feats com o gate de
nivel travado na primeira classe em ordem alfabetica (`Reach Spell` sai
`class_level: {bard}`, entao pelo motor um Mago nao pode pega-lo); o eixo
`outras-opcoes` como balaio em 25 das 27 classes; 476 alvos de `grant_feat` sem
resolver, todos de background; e atributo sem higiene nenhuma -- ficha sem boost
declarado sai com tudo 10, HP menor e ZERO avisos.

Fichas de exemplo foram de 9 para **17**, cobrindo multiclasse de tres classes,
nivel 10 e classes incomuns (Kineticist, Exemplar, Feiticeiro). Testes do motor:
**63** (eram 28 no inicio do dia). Itens novos no TODO: 69 a 75.

Correcao de registro: a entrada anterior desta sessao foi gravada com horario
"22:30-00:10", que era estimativa errada -- os commits mostram 21:04-22:13.

### Sessao | 21:05-21:35 | os quatro defeitos do motor, fechados | igor + claude-code

A rodada anterior tinha diagnosticado, com numero, quatro defeitos do motor e
deixado teste `expectedFailure` para cada um. Esta sessao fechou os quatro. O
diagnostico comum era uma frase so -- **o motor aceitava as escolhas e nao
aplicava os efeitos delas** -- e por isso os quatro consertos couberam num
arquivo.

**Item 62 -- a dedicacao agora entrega.** `_grants_em_cadeia` deixou de so
sinalizar e passou a APLICAR o que a cadeia concede com alvo estatico:
class-feature vira linha de feature, feat vira feat efetivo, e
`_proficiencias`, `_hp` e `_termo_has` leem os feats efetivos em vez de so os
escolhidos. Alvo dinamico (`{item|flags...}`) continua so sinalizado -- esse
sim depende de escolha ainda nao feita, e a distincao entre "pendente" e
"ausente" e o que o app precisa. Os tres numeros do diagnostico foram
reconferidos na ficha depois do conserto: battle-harbinger 52 -> **56 HP** (e
pegar Toughness a mao junto nao soma duas vezes), shieldmarshal com **society:
expert**, Fighter 4 + barbarian-dedication com **Rage** nas features.

**Item 63 -- higiene de slot.** `_higiene_de_slot` confronta gasto com slot nos
cinco trilhos. Pega escolha a mais, escolha em nivel sem slot, e feat sem trait
`archetype` ocupando o slot gratuito -- que era o que fazia o Free Archetype
virar um segundo class feat de graca.

**Item 64 -- as duas regras de dedicacao.** Antes de codar, o texto RAW foi
conferido na PROPRIA base, nao de memoria: 76 dedicacoes repetem a clausula
"two other feats from the <X> archetype", e e isso que a implementacao faz --
contagem em ordem de nivel, por arquetipo. A outra regra (feat de arquetipo
exige a dedicacao) saiu do vinculo que ja existia no dado: 225 arquetipos, cada
um com exatamente uma dedicacao, entao nao precisou de lista escrita a mao.

**Item 67 -- aumento de pericia.** A cadencia vem do dado: as 27 classes
declaram `skill_increase.levels`, 25 no padrao [3,5,..,19] e duas (Ladino e
Investigador) em todo nivel de 2 a 20. Vale a regra 15, o aumento serve para
entrar numa pericia (untrained -> trained, que e RAW) e o teto por nivel e
respeitado. Ficha de referencia nova, `ladino4-aumentos-de-pericia.json`,
escolhida de proposito numa das duas classes de cadencia diferente: a mesma
ficha prova que a cadencia veio do dado e nao de tabela escrita no motor.

**Dois achados novos, os dois de dado, os dois registrados (itens 69 e 70):**
o eixo `outras-opcoes` e um balaio em 25 das 27 classes -- foi por ele que um
Guerreiro 4 saia com `Warrior of Legend`, que agora tambem concede Diehard, ou
seja, o erro de dado virou numero na ficha; e 476 alvos de `grant_feat` estao
sem resolver, **todos de background** (400 sao um dict serializado como
string), o que so nao travou o item 62 porque nenhum e de feat.

**Honestidade sobre a metrica:** a validacao contra os iconics foi de 62,4% a
**62,9%** em pericia. Implementar `skill_increase` nao fecha essa lacuna,
porque as fichas derivadas dos iconics nao declaram em que nivel cada aumento
foi gasto -- falta o oraculo, nao o motor (item 68). HP seguiu em 117/129, sem
regressao.

Suites: **42 testes no motor** (era 28) e 88 no pipeline, verdes. Sobrou **um**
`expectedFailure`, o do item 65 -- `has` avaliado contra o documento inteiro,
sem recorte temporal.

### Sessao | 21:00-22:30 | tres agentes no motor: Free Archetype, ciclos e pericias | igor + claude-code

Igor pediu foco no Free Archetype e levantou o medo de cadeia infinita de
concessao ("feat que da feat que da feat"). Tres agentes em paralelo, com
ownership de arquivo declarado para nao repetirem o atropelo da rodada anterior.

**O achado central, e o mais caro: a dedicacao entra e nao entrega nada.** O
motor le `grants` so de CLASSE e de FEATURE; grant vindo de FEAT ESCOLHIDO
nunca e aplicado. Medido em ficha: `battle-harbinger-dedication` concede
Toughness e o personagem sai com 52 HP contra 56 pegando Toughness a mao;
`shieldmarshal-dedication` concede `society: expert` e a linha nem aparece;
Fighter 4 + `barbarian-dedication` sai sem Rage. Entre as 226 dedicacoes:
grant_item 114, grant_feat 67 (todos com alvo estatico), proficiency 49,
flat_modifier 34, skill_training 20. Sob Free Archetype -- regra 2, sempre
ligada -- isso significa que o trilho gratuito custa um slot e devolve so o
nome. Itens 62 a 66.

**O medo do ciclo infinito nao se sustenta no dado, e agora ha numero.** Grafo
de concessao dos 19.705 registros: ZERO ciclos, cadeia mais funda de 3 nos, 31
auto-concessoes que sao artefato do rule element do Foundry. Pesquisa na web
confirma que nao ha loop conhecido com `Ancestral Paragon` -- ele e mao unica
(geral -> ancestria). O guarda entrou como cinto de seguranca contra dado
malformado: profundidade 8, com aviso visivel, nunca truncar calado.

**A validacao por pericia corrigiu uma suposicao minha.** Eu tinha recomendado
o rank de pericia do Foundry como oraculo forte; ele NAO e o rank final -- so
registra escolha discricionaria, e o treino automatico de classe vive em
`trainedSkills.value` dentro do item de classe. Mesmo com o oraculo corrigido,
os 62,4% medem a lacuna, nao o motor. O que a medicao entregou de verdade foi
outro achado: o motor NAO implementa `skill_increase`, slot que o schema
declara -- o aumento de pericia por nivel, que todo personagem faz. Itens 67-68.

As tres frentes convergem no mesmo diagnostico: **o motor aceita as escolhas e
nao aplica os efeitos delas.**

### Sessao | 15:10-21:00 | quatro agentes em paralelo, base re-emitida, nove portoes verdes | igor + claude-code

Igor mandou seguir em tudo, em agentes, validando cada retorno. Quatro frentes
em paralelo: dump do AoN + re-extracao, extrator de `tactic`/`class-kit`,
integracao da tabela de conjuracao do PDF, e as decisoes de schema.

**As decisoes da v2 sairam da MEDICAO, nao de opiniao.** Spell passa a emitir
`level` porque as tres fontes usam `level` e nenhuma usa `rank` (AoN 2.461/2.461,
Foundry 1.802/1.802, pf2etools 2.055/2.055). `traits` ausente vira `[]` porque
as fontes concordam que nao ha trait. Fusao de `source` por subcampo foi
DESCARTADA: o Foundry nao publica pagina (0 de 28.788) e a mudanca recuperaria
quatro paginas. E o `mechanized` nao valia o rename -- o que vale sao os 1.564
registros cujo doc do Foundry TEM rule elements e que sairam com `grants` vazio.

**A base foi re-emitida**: 19.705 registros, 54 kinds, nove portoes verdes. Ao
longo da validacao apareceram cinco defeitos que nenhum portao pegava antes:
`aon_kinds.py` dava o slug limpo a quem chegasse primeiro no dump (o canonico
saia como `alchemical-sciences-methodology-5` e sumia na fusao); a curadoria de
colisao corrigia xref e level mas nao os traits, deixando a quimera de pe dentro
do proprio caso curado; `prov` de campo vazio fazia a metrica medir a si mesma;
e dois bugs de extrator (caminho e glob nao-recursivo em `ancestrias.py`,
apostrofo no slug de `classes.py`).

**Licao de coordenacao:** meus `git checkout --` de restauracao apagaram o
trabalho nao-commitado de um agente que estava escrevendo no mesmo diretorio.
Com agentes ativos, restaurar por arquivo e usar backup no scratchpad.

### Sessao | 14:00-15:10 | porte da linha paralela: portoes, fusao e suite verde | igor + claude-code

Igor mandou tocar os itens 1, 2 e 3 do doc de comparacao das duas linhas.

**Item 1 e 2, cirurgicos.** Portao 4 nao grava mais a linha de base a partir de
build sujo. `reconciliar.fundir()` nao apaga mais o vencedor quando os dois
lados vem da mesma fonte -- eram 337 registros de conflito dizendo que o
escolhido era o valor perdedor.

**Item 3, a suite: 34 quebrados -> 85 testes verdes, nenhum apagado.** A leitura
que estava errada no doc era "testes obsoletos". Eles nao eram obsoletos: 7 sao
gaps de schema (spec v2 x v1), 14 sao criterio de aceite de feature pendente,
10 testavam funcoes que aqui vivem dentro do `main()` e 3 apontavam defeito real
do dado. Cada grupo ganhou o tratamento que se auto-limpa -- `expectedFailure`
acusa "unexpected success" quando o gap fechar, `skipUnless(hasattr(...))` cai
quando a funcao existir, e defeito real virou teto (`assertLessEqual`) que
acusa piora sem mascarar o numero.

**O achado da sessao veio de tentar rodar o build aqui.** `indice_aon()` e
`indice_foundry()` voltavam vazios nesta maquina (nome de pasta diferente:
`foundry/` contra `foundry_repo/`, e `aon_dump/` nunca gerado) e os portoes 2 e
7 respondiam `return 0` -- **passavam por ausencia de dado**, que e literalmente
a falha que eles existem para pegar. Com o fallback de caminho e o estado NAO
MEDIDO, o portao 2 passou limpo de verdade e o **portao 7 acusou 2 colisoes de
identidade novas**: `hellknight-dedication` (feat-8812 nv2 x feat-1078 nv6, com
a assinatura ja visivel no conflito de level onde o pf2etools dizia 6) e
`cane-pistol-melee`. A base emitida nao foi afetada -- ela nasceu no outro PC,
onde os caminhos batiam.

Rebuild NAO foi feito, de proposito: e decisao do Igor. Fica registrado que a
cadeia inteira volta a carregar aqui e que um rebuild fecharia sozinho os itens
50 e 51.

### Sessao | 05:41-07:03 | perda de artefato, Animist recuperado, regras 17b/21/23 | igor + claude-code

**Perda de artefato, e o portao que faltava.** `dados_brutos/tabelas_conjuracao_pdf.json`
-- as tabelas de conjuracao lidas a olho de paginas renderizadas do War of
Immortals -- nunca entrou no git e sumiu. O `.gitignore` excluia `dados_brutos/`
alegando "reconstruivel pelos pins": verdade para o clone do Foundry e o dump do
AoN, falso para trabalho derivado a mao. O `TODO.md` seguia marcando o item 14
como CONCLUIDO e o relatorio seguia citando o caminho; nada reclamava.

Varredura de todo caminho citado em arquivo versionado: 42 caminhos, **3 nao
existiam**. Um era perda real, dois eram scripts de dump substituidos por
`dump_aon.py` (sem perda de dado, mas `companheiros.py` mandava rodar um script
inexistente -- bug real). Criados `pipeline/dados_derivados/` (versionado),
`artefatos_perdidos.json` (perda registrada com motivo, dano medido e decisao) e
o **portao 8**: caminho citado que some quebra o build; perda ja conhecida
aparece no relatorio sem bloquear.

**O Animist voltou, e de fonte melhor que o PDF.** A conclusao de 26/07 dizia
que "nem Foundry nem AoN materializam a tabela". Meia verdade: o item de classe
do Foundry so tem o flag `spellcasting: 1`, mas o doc de classe do AoN carrega a
tabela inteira em HTML no campo `markdown` -- e o extrator lia so `text`, a
projecao achatada. **O dado estava no cache que o proprio extrator ja baixava.**
Foi essa conclusao errada que mandou alguem ler o PDF a olho.

Parser em `pipeline/tabelas_conjuracao_aon.py`, validado contra as outras 10
conjuradoras: reproduz as 10 **celula a celula**, incluindo truques, contra o
pf2etools -- fonte independente. As 11 conjuradoras agora tem tabela completa.
Animist tem teto de rank 9 (terceira classe assim, com Magus e Summoner) mais um
slot de apparition rank 10 pela Supreme Incarnation.

**A conferencia registro a registro pagou.** `build.sh` rodado e comparado com o
commit anterior via `comparar_bases.py` novo: 19.738 -> 19.738, zero sumiram,
zero nasceram. O primeiro build alterou **dois** registros, e o segundo era
regressao minha: o focus pool do Cloistered Cleric zerou. Causa raiz maior que o
sintoma -- `load_foundry_feat` le de `dados_brutos/foundry/feats/`, que tem **0
arquivos contra 6.045 no clone**, porque `classes.py` so popula `classes/` e
`class-features/`. Falta silenciosa: devolve `None` e o campo vira `null`.
Corrigido com fallback para o clone. Build final: **1 registro alterado**, o
pretendido.

**Regra 17b -- teto do que cria criatura.** Escopo corrigido pelo Igor: Spirit
Link e Protector Tree saem (nao criam nada), `incarnate` entra -- 23 magias, zero
interseccao com `summon`, sao as invocacoes de rank 4 a 10. 37 no total, so por
trait, zero curadoria.

**Regra 21 virou invariante testado.** A simulacao (Opus, relatorio em
`docs/simulacoes/`) achou **50 de 204 pares** violando: no nivel 20 o dip ficava
em 0% da dedicacao gratuita. Decisao do Igor: *"o dip tem que obrigatoriamente
ser pelo menos tao forte quanto uma dedicacao no mesmo nivel de personagem"*.
Piso implementado, e a regra virou varredura EXAUSTIVA dos 204 pares em
`teste_motor.py`.

**Regra 23 -- exclusao mutua** entre nivel de classe X e dedicacao de X, nos dois
sentidos. Corrige divergencia que ja existia: um Mago 20 puro recebia
`atende: true` para Wizard Dedication, porque a proibicao mora numa regra geral
de arquetipo e nao no `requires` do feat.

**Ficha do companheiro, RAW puro**, com as regras citadas verbatim em
`docs/2026-07-27_atores.md`. Maturidade derivada dos feats, nao lida do
documento. A escolha nimble/savage virou **slot no vocabulario generico**
(`eixo/nivel/slot/escolhe/opcoes`), nao campo ad-hoc -- correcao de rumo do Igor
no meio da tarefa do agente.

**Medido a pedido do Igor:** 243 dos 6.044 feats (4%) abrem escolha, e a cadeia
de desbloqueio na base chega a **profundidade 4**. O encadeamento NAO esta no
formato do Foundry (opcoes de `ChoiceSet` sao valores ou consultas, nunca
ponteiro para item com escolha dentro) -- e grafo de dependencia, nao arvore
aninhada. Conclusao: slot tem de ser derivado do estado a cada escolha, nunca
arvore estatica.

**Duas afirmacoes minhas corrigidas no caminho**, registradas para nao voltarem:
o item 39 nao era defeito (heightened vem do nivel de personagem e independe do
teto de slot -- a assercao do validador e que estava errada, com 18 falsas
violacoes); e o argumento de que bloquear a dedicacao propria custaria 8 slots
estava inflado (o personagem pega qualquer uma das outras 26).

### Sessao | fonte limpa + fatia vertical 1 | igor + claude-code

**Item 37 -- pf2etools completo.** A terceira fonte vivia como 242 arquivos
baixados um a um por HTTP, adivinhando nomes; os 50 `.json.missing` eram chutes
de nome, nao conteudo faltando. Clone no pin (7d1ec43f), 382 arquivos em escopo.
Os 140 novos caem nos buracos: `baseitems.json`, `deities.json`, `traits.json`,
`archetypes.json`, `companionsfamiliars.json`, `optionalfeatures.json`.

Prova de reproducibilidade: 7 dos 8 extratores deram contagem **identica**. O
oitavo (rituais) achou defeito real -- nao existe pasta `rituals/` no Foundry,
ritual e magia com `system.ritual`; o extrator lia um recorte feito a mao numa
sessao antiga e, quando sumiu, 6 rituais exclusivos do Foundry sumiam calados.

Portao 5 zerado: os 3 orfaos nao eram falta de licenca -- o bloco de `source` do
extrator de equipamento so tinha ramo para AoN e Foundry, entao item exclusivo do
pf2etools saia com `source` vazio por construcao. Mais as 141 siglas de livro
extraidas de `js/parser.js` da propria fonte. Itens magicos ligados: +2.632.

**Fatia vertical 1 -- o motor monta ficha.** `motor/` implementa 11 das 22
regras, com 24 assercoes travando cada uma. Guerreiro 3 / Mago 2 sai completo.
A houserule aparece viva: Mago 2 num personagem 5 tem os slots de um Mago 2 e
conjura no rank 3 (+2 de elevacao); Mago 5 puro ganha elevacao zero.

O que a fatia descobriu, que era o motivo de faze-la:
- **a progressao misturava concessao com escolha** -- `wb:class/wizard` declarava
  49 features, sendo 15 concedidas; o resto sao as 23 escolas e 5 teses, opcao
  mutuamente exclusiva. Um motor ingenuo daria todas ao Mago 1. Fonte
  autoritativa: `system.items` da classe no Foundry
- **item 2 fechado**: as 28 categorias de sub-escolha do AoN viraram kind proprio
- **item 14 fechado**: a tabela de slots existia desde a primeira sessao e nunca
  entrou na base, por ser mapa e nao lista
- **portao 3: 80 -> 23** -- nao faltava conteudo, faltava vocabulario unificado

Base: 19.429 -> 19.738. Portoes 1, 2, 4 e 5 passam.

**Avaliacao pedida pelo Igor, registrada porque muda a prioridade:** o risco do
projeto saiu de "os dados estao errados" para "o modelo de efeito e fragmentado e
a regra nunca foi testada na mesa". O efeito mecanico mora em tres formatos
(classe usa `grants`, ancestria usa campos soltos, background usa outro
conjunto) e a spec define `grants` como a linguagem unica. E `class_level`, a
razao de o projeto existir, aparece em 79 de 19.738 registros.

## 2026-07-26

### Sessao | re-emissao do bloco 1 | igor + claude-code
Executado o bloco 1 inteiro do TODO (re-emissao da base). 11 itens fechados.

**Bloqueio achado antes de qualquer item, e nao registrado em lugar nenhum:**
7 dos 10 extratores e o `emitir_textos` apontavam para um clone do Foundry em
`/tmp/claude-.../scratchpad/pf2e-research`, de uma sessao ja encerrada. O clone
nao existia mais e **o pipeline nao rodava** -- re-executar o extrator de
equipamento dava 5.698 registros contra os 7.496 da base, mono-fonte, exit code
0. Pior: `carregar_aon()` cai para lista vazia em silencio quando o dump falta,
e os dumps do AoN para equipamento nunca tinham sido salvos. **A base de 18.176
registros nao era reproduzivel a partir do repo.**
- clone refeito no pin dentro de `dados_brutos/`, `buscar_fontes.sh` reconstroi
- `dump_aon.py` novo: indice `aon` inteiro em disco, 43.686 docs em 93
  categorias (bate com o censo remoto)
- os 7 caminhos hardcoded de `/tmp` foram substituidos

**Itens fechados:** 29 (os 7 portoes), 20 (traits como uniao), 24 (fusao por
`remaster_id`), 30 (metrica de prosa), 17 (rituais), 28 e 11 (grafia de livro),
27 (relic/language/background), 21 (colisoes desmembradas), 26 (divergencia
detectada), 25 (`mechanized` derivado), 31 (confirmado: era falha de casamento).

**Numeros:** base 18.176 -> **19.250 registros em 24 kinds**. Prosa de 95%
reportado (82,6% real) para **99,2%**. 586 registros que a fusao por prosa tinha
deletado foram recuperados. 318 irmaos criados no desmembramento. Portoes 1, 2 e
4 passam; 3, 5 e 7 seguem abertos com causa documentada.

**Duas correcoes a spec, verificadas contra as fontes:**
- `Death from Above`: a spec dizia "o Foundry separa os dois; o AoN indexa so o
  mitico". E o contrario nos dois lados. O defeito nunca foi fusao de
  duplicatas -- e **casamento ambiguo**, escolher 1 entre N em silencio
- `mechanized` passou a ser derivado (`== bool(grants)`); significava quatro
  coisas conforme o extrator

**Aberto para decisao do Igor:** 3 registros (`heavy-power-suit`,
`nine-ring-sword`, `wind-and-fire-wheel`) nao existem em fonte nenhuma em disco
-- vieram de consulta ao vivo ao pf2etools. Nao inventei licenca (item 35). E o
dump local do pf2etools esta incompleto, sem script de reconstrucao (item 37) --
`requires`, cuja precedencia e pf2etools, roda hoje com fonte parcial.


### Sessao | 18:40-21:30 | igor + claude-code
Exploracao dos PDFs oficiais e revisao ampla da base. **O pipeline nao foi
re-rodado**, entao o `index.json` esta byte a byte como estava no inicio -- mas
a sessao descobriu que ele ja continha dano. Esta sessao produziu diagnostico,
correcao de spec e um extrator novo.

- **35 PDFs oficiais** extraidos dos zips do Downloads (1,7 GB, fora do git).
  Os 1.027 mapas `.webp` foram ignorados por decisao do Igor
- **8 agentes despachados**, a maioria em paralelo: tabelas de conjuracao,
  arbitragem de divergencias, ambientacao, cobertura, mecanica dos Lost Omens,
  normalizacao de traits, colisoes de identidade, extrator de rituais
- **Achado 1 -- `traits` nao e campo de precedencia, e de uniao.** Responde por
  88% dos 2.299 conflitos e quase nenhum era divergencia: 72 facetas
  complementares, 31 ancestria renomeada no remaster (com a precedencia
  escolhendo o nome LEGADO numa base remaster-first), 18 granularidade
  (`two-hand-d12` virando `two-hand`, perdendo o dado de dano). Spec corrigida
- **Achado 2 -- `wb:<kind>/<slug>` assume nome unico por kind, e nao e.**
  5 colisoes confirmadas contra AoN e Foundry (`death-from-above` sao dois
  feats distintos fundidos numa quimera). Detector melhor achado pelo agente:
  registro-irmao com sufixo e `xref` incompleto -- 59 candidatos, com falso
  positivo conhecido nos `-greater`/`-major` de item
- **Achado 3 -- faltava o kind `ritual` inteiro.** Zero em 18.176, e a palavra
  nao aparecia na spec: omissao de escopo, nao falha de extrator. Extrator
  escrito, **151 rituais** (a estimativa de 31 era so dos dois Player Core)
- **Achado 4 -- a tabela de slots de conjuracao nao existe para classe nenhuma.**
  Nao era buraco do Animist. Animist, Magus e Summoner recuperados do PDF;
  Exemplar e Kineticist confirmados nao-conjuradores
- **Arbitragem contra PDF: premissa invalida.** Montei um teste tratando o
  impresso como arbitro; deu 63% e o defeito foi meu -- as fontes digitais
  incorporam errata posterior a publicacao, entao o teste mediu concordancia
  com o impresso, nao acerto
- **Lost Omens: ambientacao ignorada** por decisao do Igor (e flavor puro, e o
  conteudo mecanico daqueles capitulos ja esta na base). Mas sobrou mecanica
  real nao estruturada: 305 registros com linha `Access` citando organizacao ou
  regiao e `requires` vazio
- **Cobertura auditada**: Treasure Vault 898 nomes / 100%; Player Core, Player
  Core 2, War of Immortals e Ancestry Guide 1.377 nomes / 99,8% fora rituals
- **`pipeline/normalizacao_traits.json`**: 17 renomeados, 9 removidos sem
  sucessor, 18 familias parametrizadas, cada entrada com `prov` citando pagina.
  Corrigiu dois erros meus que ja estavam na spec -- `oread`/`sylph`/`undine`
  nao viraram `naari` (so `ifrit`), e `illusion` sobreviveu ao remaster
- Nota de wiki criada: `merge-n-fontes-precedencia-vs-uniao.md`
- **A auditoria ampla voltou no fim e mudou o estado do projeto.** 13 achados;
  o critico e que a **fusao Legacy<->Remaster destruiu dado**: decide por
  similaridade de prosa, deletou 597 registros e so 35% das fusoes estavam
  certas. `wb:equipment/aeon-stone` engoliu 24 pedras distintas. Tambem
  derrubou dois numeros que eu vinha reportando: prosa e **95%, nao 100%**
  (907 sem prosa -- a metrica dividia pelo subconjunto errado), e das 2.299
  divergencias, 6 kinds simplesmente **nao detectam conflito**, entao o numero
  e piso e nao total. Dos 7 portoes de qualidade, so 1 esta implementado, e o
  portao 7 e tautologico -- pergunta por duplicata depois de a fusao ja ter
  acontecido
- **A base NAO esta fechada.** Precisa de re-emissao antes de qualquer trabalho
  de construtor. Detalhe nos itens 24-34 do TODO

### Evento | igor + claude-code
- Projeto criado via /tartarus:novo

### Sessao | igor + claude-code
- Brainstorming completo das regras caseiras de multiclasse -- 21 regras fechadas
- Pesquisa em 4 agentes paralelos: Foundry pf2e (Sonnet), pf2etools (Sonnet),
  Pathbuilder 2e (Sonnet), review adversarial do design (Fable)
- Endpoint Elasticsearch do Archives of Nethys validado e usado como fonte de
  verificacao ao longo da sessao (43.686 docs, indice `aon`)
- Dataset medido: 29.236 registros relevantes -- indice 0,53 MB gzip,
  prosa 3,6 MB gzip. Confirma arquitetura client-side sem backend
- Simulacoes de Monte Carlo (200k iteracoes) para calibrar a regra de elevacao
  de magia. Derrubaram duas propostas minhas e fecharam em "sem teto"
- Decidido: base e construtor sao um projeto so, construidos em fatias
  verticais. Fatia 1 = Guerreiro + Mago, niveis 1-5

### Evento | igor
- Projeto renomeado de `nethys` para `waybuilder` -- piada com o Pathbuilder 2e,
  e eco do Wayfinder, a bussola da Pathfinder Society

### Sessao | igor + claude-code
- Spec `2026-07-26-schema-base.md` aprovada -- contrato unico de envelope,
  `prov`, `conflitos`, linguagem de predicado e efeito
- Primeiro extrator do pipeline escrito e rodado: `pipeline/extratores/ancestrias.py`
  (stdlib-only, `extrair() -> list[dict]`), cobrindo ancestry + heritage + background
- 708 registros emitidos em `pipeline/saida/ancestrias.json` (50 ancestrias,
  326 heranças, 332 backgrounds), enumerados a partir do Foundry pf2e
  (commit `87f9e5028baaa10b70fdc766260b7886def17e04`), enriquecidos via dump
  local do AoN (94/436/612 docs) e cross-check com pf2etools
- Portoes de qualidade do schema verificados manualmente: 0 ids fora do
  padrao, 0 duplicados, 0 campo preenchido sem `prov`, 0 sem `license`,
  0 referencia orfa heritage<->ancestry
- Mapa Legacy->Remaster calculado do conjunto AoN inteiro: 4 ancestrias e 12
  heranças renomeadas via `remaster_id`/`legacy_id` (Gnoll->Kholo, Grippli->
  Tripkee, Half-Elf->Aiuvarin, Half-Orc->Dromaar); 9 ancestrias e 7 heranças
  legado sem substituto (Ifrit/Oread/Suli/Sylph/Undine/Beastkin/Aphorite da
  Ancestry Guide, Ardande/Talos ja remaster mas sem legado, Aasimar/Tiefling
  sem ponte formal no AoN -- fundiram em Nephilim (Player Core) sem
  `remaster_id`, confirmado por leitura direta do texto); 97 backgrounds
  legado sem substituto (maioria player's guide de AP encerrada)
- Achado: 19/50 ancestrias e 121/326 heranças no Foundry ainda sao Legacy/OGL
  (nunca remasterizadas oficialmente -- Android, Anadi, Kitsune, Sprite,
  Strix, Skeleton, etc.)
- Relatorio completo em `pipeline/relatorios/ancestrias.md`

### Sessao | ~14:30-18:30 (estimado) | igor + claude-code
- Projeto criado, renomeado `nethys` -> `waybuilder`, e escopo colapsado em um
  projeto so (base + construtor), construido em fatias verticais
- **3 specs escritas e aprovadas**: as 22 regras caseiras de multiclasse, o
  schema da base canonica, e o schema do documento de personagem
- **Review adversarial em Fable duas vezes.** O primeiro demoliu uma regra que o
  Igor nunca propos -- erro meu de transcricao. O segundo, sobre a spec real,
  achou 7 defeitos legitimos, todos endereçados
- **Base canonica montada**: 6 extratores em paralelo (classes, feats, magias,
  ancestrias, conjuracao, e mais 3 rodando), reconciliacao, emissao de prosa e
  fusao de renomeados. ~9,9k registros com prosa em 100% e portoes passando
- Simulacoes de Monte Carlo (200k iteracoes) calibraram a regra de elevacao de
  magia; benchmark de 3.624 criaturas do AoN extraido e guardado
- **Principio zero definido pelo Igor**: isto e um construtor de personagem, nao
  um sistema de jogo. `requires` sugere, nunca bloqueia
- README.md criado como ponto de retomada para sessoes futuras
- Encerrada com 3 extratores ainda rodando (equipamento, companheiros,
  referencia) -- base deve chegar a ~21k registros
