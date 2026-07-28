---
project: waybuilder
---

# LESSONS -- Waybuilder

## Decisoes
| data | decisao | motivo |
|------|---------|--------|
| 2026-07-26 | Tres fontes, nao uma | Cada uma tem algo exclusivo: Foundry tem efeito executavel, pf2etools tem pre-requisito com referencia marcada, AoN tem cobertura e atualidade. Nenhuma sozinha basta |
| 2026-07-26 | Base separada do construtor | A base e RAW e verificavel sozinha; nao depende de nenhuma decisao de houserule. Uma spec so nao guiaria nem uma coisa nem outra |
| 2026-07-26 | Remaster como base, Legacy como merge curado | Linha viva, ORC mais limpo que OGL, e o campo `remaster_id`/`legacy_id` do AoN ja entrega o par de dedupe pronto |
| 2026-07-26 | Escopo cortado no que o construtor usa | "Base definitiva do RPG" e escopo infinito. Bestiario sozinho e 10-23 MB e nao serve pra montar ficha |
| 2026-07-26 | Pipeline re-executavel, nao mutirao | Merge manual congela a base na data em que foi feito. Foundry commita diariamente |
| 2026-07-26 | Proveniencia por campo | Sem ela nao da pra ver divergencia entre fontes nem re-sincronizar so o que mudou |
| 2026-07-26 | Predicado sabe falar `class_level[X]` e `character_level` | Nenhuma fonte usa os dois (no PF2e oficial sao o mesmo numero), mas o builder precisa. Barato agora, caro depois |
| 2026-07-26 | SQLite em build, JSON no cliente | Indice inteiro cabe em 0,53 MB gzip -- roda client-side, offline, sem backend |

## Aprendizados

### Se o usuario ja usa uma ferramenta equivalente, olhe ELA antes de desenhar
O app foi entregue com tres abas separadas -- criacao, progressao, ficha. O Igor
abriu e disse "ta bem diferente do que eu esperava", e mandou o HTML exportado do
Pathbuilder 2e, que ele **usa todo dia**. A estrutura real era outra: duas
colunas, build a esquerda e ficha viva a direita, tudo na mesma tela.

O erro nao foi de implementacao -- os 77 testes passavam. Foi de leitura do
problema: com abas, o jogador escolhe um feat e precisa trocar de tela para ver o
numero mudar, e num construtor o retorno imediato E o produto.

Um unico HTML exportado carregava mais requisito do que a spec que escrevi:
layout, que atributo mostrar (modificador, nao score), o que a pericia exibe
(total rolavel, nao o rank), e que o picker precisa do TEXTO do item porque
ninguem escolhe um feat pelo nome. Custou uma reescrita que 15 minutos de leitura
teriam evitado.

Regra: antes de desenhar tela para um dominio onde ja existe ferramenta
estabelecida que o usuario usa, pedir um export, um print, qualquer coisa. Nao
para copiar -- para saber quais decisoes ja estao tomadas na cabeca dele.

### Aplicar o efeito de uma escolha cria requisito circular
No dia em que o motor passou a APLICAR o que um feat concede, ele passou a
avaliar o `requires` desse feat contra um estado que ja inclui o efeito dele.
`acrobat-dedication` exige acrobatics trained e concede acrobatics: o feat
passou a satisfazer o proprio requisito, e a ficha saia limpa exatamente onde
antes sinalizava. Foram 25 termos auto-satisfeitos entre os 6.273 feats com
`requires` -- e nenhum teste existente reprovou, porque todos verificavam que o
efeito FOI aplicado, e nenhum verificava contra o que o requisito e medido.

A correcao nao e caso especial: e o predicado ser avaliado contra o estado SEM o
efeito do proprio item. Isso obriga a guardar, para cada valor derivado, DE QUEM
ele veio -- e, quando ha cadeia (A concede B que concede C), a RAIZ dela, nao o
elo imediato. Quem aplica efeito precisa de proveniencia, nao so de valor.

### O corpus de teste cresce e muda o resultado da validacao
Um review adversarial rodou 321 embaralhamentos das escolhas e concluiu que a
ordem do documento nao afetava a ficha. Estava certo -- para o corpus daquele
momento. Enquanto ele rodava, outro agente criou fichas MULTICLASSE, e o mesmo
teste passou a falhar na hora: `ordem_de_classe` era montada na ordem do array,
entao reordenar mudava qual e "a primeira classe" e com ela a regra 8. Com
classe unica o defeito e invisivel.

Licao: "testei N casos e nao achou" vale pelo corpus, nao pelo N. Ao validar
invariante, perguntar primeiro qual e a forma de entrada que poderia quebra-lo
-- e se ela existe no corpus.

### Ficha de referencia contaminada mede a ficha, nao o motor
A primeira varredura das 226 dedicacoes usou como base uma ficha que ja tinha
`additional-lore` e `double-slice` escolhidos. Como o motor (corretamente) nao
concede o que o personagem ja tem, 30 dedicacoes apareceram como "nao entregam
nada". Com uma ficha neutra -- sem nenhum feat escolhido -- o numero caiu para
16, e a conclusao mudou de "muitas dedicacoes estao quebradas" para "quase todas
funcionam". O baseline de uma medicao precisa ser escolhido contra o que se quer
medir, nao ser a ficha que estava aberta.

### Consumir o dado descobre em uma tarde o que auditar nao acha em duas sessoes
Duas auditorias amplas leram a base campo a campo e nao viram que
`wb:class/wizard` declarava 49 features de nivel 1, entre elas as 23 escolas de
magia -- todas ao mesmo tempo. Bastou **um motor tentando montar uma ficha** para
o problema saltar na primeira linha impressa.

Auditoria pergunta "este campo esta preenchido e coerente?". Consumo pergunta
"da para fazer a coisa?". A segunda pergunta e mais barata e acha classe de erro
que a primeira nao alcanca, porque o defeito nao estava em nenhum campo: estava
na **relacao** entre eles.

Corolario para o resto do projeto: antes de investir no item caro (os ~40 Rule
Elements), escrever o consumidor mais simples que exercite o schema.

### A fonte declara a estrutura; inferir e o ultimo recurso
Para separar "o que a classe concede" de "o que ela manda escolher" foram
tentados dois caminhos ruins antes do certo:
1. casar por nome contra as categorias do AoN -- pegava `arcane-school` mas
   perdia as escolas de Runelord e as de organizacao do Lost Omens
2. heuristica de "varias features no mesmo nivel sao mutuamente exclusivas" --
   nunca chegou a ser escrita, e teria falso positivo garantido

O certo estava em `system.items` da classe no Foundry: **15 entradas**, que e
exatamente o que o VTT usa para montar personagem, com "Arcane School" aparecendo
uma vez so, como a escolha que e. A fonte ja respondia a pergunta.

Mesmo padrao das 141 siglas de livro do pf2etools (`js/parser.js`) e do
`remaster_id` do AoN. Tres vezes seguidas a resposta estava declarada na fonte
enquanto o instinto era inferir do conteudo.

### Fonte que vive fora do repo desaparece, e o pipeline mente sobre isso
Ate 26/07 sete dos dez extratores e o `emitir_textos` apontavam para um clone do
Foundry num diretorio de scratchpad de sessao (`/tmp/claude-.../pf2e`). A sessao
acabou, o clone sumiu, e **nada quebrou de forma visivel**: `carregar_aon()`
devolve `[]` quando o dump nao existe, e os candidatos de caminho caem para o
proximo em silencio. Re-executar o extrator de equipamento produzia 5.698
registros contra os 7.496 da base, mono-fonte, exit code 0.

Duas licoes distintas:
1. **Fonte externa tem que ter script de reconstrucao versionado**, com o pin
   dentro dele (`buscar_fontes.sh`, `dump_aon.py`). O `.gitignore` do pipeline
   dizia "reconstruiveis pelos pins registrados na spec" -- mas nao havia
   nenhum script que fizesse isso, so a frase.
2. **Degradar em silencio e pior que falhar.** Toda queda para fonte parcial
   deve ser erro alto, nao lista vazia. O sintoma so apareceu porque a contagem
   foi comparada com a anterior.

### O detector tem que mirar o defeito, nao o sintoma imaginado
O portao 7 da spec perguntava "existe `name` normalizado repetido no mesmo
`kind`?". Nunca disparava -- nem antes nem depois da fusao. A razao: a
ambiguidade **nao produz dois registros**. O extrator casa por nome, escolhe um
candidato entre os N da fonte, e os outros somem sem deixar rastro na base.
Perguntar a base sobre duplicata e perguntar para a vitima, nao para a cena.

O detector correto compara a base contra o **censo da fonte**: registro cujo
nome tem N entidades no AoN, com assinatura (level, traits) divergente. Achou
159 colisoes reais, contra as 5 que a inspecao manual conhecia.

Corolario que vale para o resto do projeto: **duas fontes concordarem nao e
evidencia de nada se as duas foram lidas pelo mesmo casamento errado.**

### Quando o casamento erra, a precedencia por campo espalha o erro
`Death from Above` casou com o doc mitico do AoN (nv16) mas ficou com `level: 8`
-- porque a precedencia manda `level` vir do Foundry, e o doc do Foundry era da
**outra** entidade. O registro nao ficou "meio certo": ficou uma quimera que nao
corresponde a nada publicado. Precedencia por campo pressupoe que as fontes
falam do mesmo objeto; quando essa premissa cai, ela deixa de conter o erro e
passa a distribui-lo.

Por isso desmembrar exige realinhar o registro original, nao so criar o irmao.

### Similaridade de prosa nao e evidencia de identidade
A fusao por Jaccard >= 0.62 sobre 900 caracteres deletou 597 registros com 35%
de acerto. `aeon-stone` engoliu 24 pedras distintas porque a prosa de todas
comeca igual. Chave declarada pela fonte (`remaster_id`/`legacy_id`) achou 942
pares -- **mais** cobertura e sem os falsos. Prosa serve para desempatar entre
candidatos ja restritos por uma chave, nunca para criar o par.

### Metrica com denominador errado esconde exatamente o que deveria denunciar
"Prosa em 100%" dividia pelas referencias existentes. Registro sem referencia
nenhuma nao entrava no denominador -- os 907 mais invisiveis do dataset eram os
unicos que a metrica nao conseguia ver. Medida honesta: 82,6%. Depois de usar o
dump completo do AoN e criar as referencias que faltavam: 99,2%.

Ao corrigir uma metrica, corrigir o buraco na mesma passada -- senao ela volta a
mentir na proxima leitura.

### Onde cada fonte e forte e fraca (verificado)
- **Foundry** (`packs/pf2e/`, 28.841 arquivos JSON): unica com efeito mecanico
  executavel. `classFeatLevels: [1,2,4,6,...]` como array literal;
  proficiencia como numero (`MartialProficiency value: 3` = master).
  Rule Elements sao ~40 tipos interpretados por JS -- reusar a *automacao*
  exige reimplementar um interpretador, nao so ler JSON.
- **pf2etools** (`Pf2eToolsOrg/Pf2eTools`, 524 arquivos, 33 MB): tem o mesmo
  bloco `advancement` estruturado do Foundry (da pra cruzar e achar erro de
  importacao). Exclusivo: pre-requisito com referencia marcada --
  `"expert in {@skill Society|PC1}"` contra o `{"value": "Strength +2"}` cru
  do Foundry. Falhas: sem GM Core, catalogo de fontes ~10 meses atrasado.
- **AoN Elasticsearch** (`elasticsearch.aonprd.com`, indice `aon`, 43.686 docs):
  metadados de classe bem estruturados (HP, proficiencias, habilidade-chave,
  pericias em campo proprio). Progressao vem so como nome + nivel, sem efeito.

### Pre-requisito de feat e prosa em todas as fontes
O Foundry guarda como texto livre e **nao valida** -- nao impede pegar feat
cujo pre-requisito nao e satisfeito. Estruturar isso pros 8.460 feats e item
de trabalho proprio, nao detalhe de importacao. As strings do pf2etools ja vem
com as entidades marcadas, o que corta a parte dificil; sobra parsear conector
logico (`and` / `either...or`) e palavra de rank.

### Ninguem no ecossistema separa nivel de classe de nivel de personagem
`grep -rn "classLevel" src/` no Foundry retorna zero. So existe
`self:level:N` gerado de `actor.level`. Ate a variante Free Archetype e
`new Array(actor.level).filter(i => i % 2 === 0)`. Os *dados* sao
reaproveitaveis; a *logica* de "quando ganho isso" pressupoe nivel unico.

### Escala do merge legado/remaster
- 43.686 docs no total
- 11.353 legados **com** substituto (`remaster_id`) -- dedupe mecanico
- 2.294 de linhas antigas **sem** substituto -- teto da pilha de triagem,
  nao lista de removidos: muito conteudo antigo nunca foi tocado e segue valido

## Armadilhas

### `Pf2ools` (sem o "e") esta morto
Tentativa de reescrita do pf2etools. Ultimo commit de conteudo real em
abril/2024, app parado desde agosto/2024, o resto e Dependabot. A fonte viva e
`Pf2eToolsOrg/Pf2eTools`. Nao confundir.

### Licenca: texto de regra sim, arte e bestiario nao
Cada registro do Foundry carrega `publication.license` (OGL ou ORC) e
`publication.remaster`. Mas o README cita um **acordo bilateral
Paizo <-> Foundry Gaming LLC**, e parte do conteudo agregado esta la por causa
disso, nao por licenca publica. A arte tem EULA explicito de *"exclusive use
within that project"*. Regra sob OGL/ORC e reutilizavel com atribuicao; arte e
statblock completo de bestiario, nao. Triagem por tipo de conteudo antes de
publicar.

### O campo `archetype` do AoN casa por aproximacao
Consultar feats do arquetipo Mago traz 10 feats de "Mask" de nivel 20 que nao
sao do Mago. O campo e multivalorado e o match e textual. O vinculo
feat -> arquetipo tem que sair de campo exato, senao a lista de opcoes do
construtor vem contaminada.

### Nao assumir tabela de classe por amostragem
Checar 4 classes e generalizar deu errado duas vezes na mesma sessao: a
pergunta "quais classes dao class feat no nivel 1" parecia ser 3 classes,
depois 6, e a varredura completa deu **16**. Toda afirmacao sobre tabela de
classe sai de query sobre as 47, nunca de lista escrita a mao.

### `track_total_hits` no Elasticsearch
O `total` do AoN para em 10.000 por padrao. Sem `"track_total_hits": true` a
contagem mente silenciosamente. E `terms` em campo de texto (`primary_source`,
`name`) retorna zero -- usar `match_phrase`.

### Class-feature e compartilhada entre classes
O Foundry guarda 1 arquivo por feature, referenciado por N classes com nivel
proprio cada. "Weapon Specialization" e um arquivo so: Guerreiro no 7, Mago no
13. Modelar `level` na feature obriga a duplicar o registro por classe (27 nomes
-> 187 registros com texto repetido) e quebra a identidade do id. O nivel
pertence a **progressao da classe**. Corrigido na spec do schema.

### 52% das class-features nao casam com o AoN, e nao e bug de busca
O AoN usa categorias proprias para escolha de subclasse -- `mystery`, `patron`,
`instinct`, `doctrine` -- em vez de `class-feature`. Cair para a categoria `feat`
como fallback **piora**: `Advanced Alchemy` existe como class-feature nativa E
como feat de arquetipo, entidades diferentes com o mesmo nome.

### pf2etools nao cobre o Remaster inteiro
Sem geracao remaster para 8 das 12 classes do Player Core 2 (Alchemist,
Barbarian, Champion, Investigator, Monk, Oracle, Sorcerer, Swashbuckler) e sem
arquivo nenhum para Animist, Commander, Exemplar e Guardian. Cerca de 12 das 27
classes ficam **sem cross-check de `level`**. A precedencia da spec assume duas
fontes independentes para conferir nivel -- em metade das classes existe so uma.

### Vinculo feat -> arquetipo sai do DIRETORIO do Foundry, nao do campo do AoN
`packs/pf2e/feats/archetype/<slug>/` e campo exato: 244 pastas, 2.266 feats,
zero casamento textual. Medida a alternativa: o campo `archetype` do AoN
atribuiria **538 feats a mais**, porque ele significa *"acessivel via este
arquetipo"* e nao *"pertence a"*. Em `martial-artist` sao 9 na pasta contra 32
no AoN -- os 23 extras sao feats de Monge com `trait:["Monk"]`. Validacao
cruzada: dos 2.150 feats com traco `archetype`, 96,1% tem vinculo pelo
diretorio.

### Parser de pre-requisito: 84,7%, e o resto nao vale regex
3.609 de 4.263 predicados parseados. A cauda tem 403 assinaturas distintas e
**282 aparecem uma unica vez** -- prosa unica, condicao narrativa ("you died and
returned as a ghost"), alinhamento legado. O unico ganho grande que sobra
(~3 p.p.) vem de alimentar o indice de nomes com as class-features, nao de mais
expressao regular.

Truque que destravou o parser: tentar a **clausula de rank com lista propria
antes** da quebra por virgula, aceitando so se *todo* item resolver como alvo de
proficiencia. E o que distribui `trained in Occultism or Religion` em dois
predicados sem transformar `trained in Crafting, expert in Society` em lista
errada.

### Rule elements: 21 tipos servem para ficha, 14 nao
Convertidos: `GrantItem`, `FlatModifier`, `ActiveEffectLike`, `ChoiceSet`,
`MartialProficiency` e mais 16. Ignorados de proposito: `ItemAlteration` (949),
`RollOption` (546), `Note` (269), `AdjustDegreeOfSuccess` (135) -- sao automacao
de rolagem em mesa, nao construcao de personagem. So 27 feats perdem mecanica
real.

### A tabela de slots de conjuracao nao esta mecanizada em lugar nenhum
Nem AoN, nem pf2etools, nem os campos estruturados do Foundry. Ela vive dentro
de rule elements nao decodificados. Confirmado como o item mais caro do projeto,
que ja era a suspeita no desenho inicial.

### Progressao de classe tem DOIS niveis, nao um
Depois de mover `level` para `wb:class/*.progressao`, sobraram 62 class-features
sem classe dona -- e nenhuma delas e concedida por outra feature tampouco.
Sao **escolhas de segundo nivel**: teses e escolas do Mago, ordens Hellknight,
ikons do Exemplar, gates do Kineticist, research fields do Alchemist.

O grafo real e `classe -> feature -> sub-escolha`. Modelar so o primeiro salto
deixa essas 62 invisiveis para o construtor.

### Dois bugs de casamento achados na reextracao
- O `items{}` das classes do Foundry as vezes cacheia um `name` desatualizado
  (Cleric guarda "Deity" para o item que hoje se chama "Deity (Cleric)").
  Fallback pelo sufixo do `uuid` recuperou 14 vinculos invisiveis.
- O AoN indexa 1 doc por classe dona de uma feature compartilhada, as vezes com
  nome diferente (Ranger tinha "Martial Weapon Mastery" para o que hoje e
  "Weapon Mastery"). Aceitar nome do AoN por match aproximado criava registro
  fantasma. Agora so match exato alimenta `name`; aproximado so alimenta
  rarity/source/page.

### AoN Elasticsearch trava sem `User-Agent`
`elasticsearch.aonprd.com` **pendura indefinidamente** se a requisicao nao tiver
header `User-Agent` -- nao retorna erro, nao dá timeout, so fica esperando. E
throttla banda em resposta grande (~150 KB). Contorno: mandar `User-Agent` e
paginar em blocos de ~80 registros.

Mesma classe do problema ja registrado na wiki para o GraphQL do Railway.

### Similaridade de prosa nao e criterio de identidade
`fundir_renomeados.py` unia pares Legacy<->Remaster por similaridade de texto
(corte 0,62, piso de 15 tokens distintivos). O relatorio saiu bonito -- "597
pares fundidos, **zero par nao unido**" -- e eu tratei isso como sucesso.

Auditado contra o `remaster_id` do AoN: **so 35% das fusoes estavam certas.**
393 dos 597 pares fundiram registros com `level`, `price_cp` ou `damage`
diferentes -- ou seja, o dado ja dizia que eram entidades distintas, e o
criterio de prosa ignorou.

Casos: `wb:equipment/aeon-stone` engoliu **24 pedras diferentes** (Amber Sphere,
Black Disc, Agate Ellipsoid, Azure Briolette...), cada uma com efeito proprio.
`Poi` virou `Shield Bash`. `Tonfa` virou `Shuan Ji`, **do mesmo livro** -- nao
ha nem historia de renomeacao possivel ali. Seis armas viraram `Gaff`.

A causa e estrutural: itens de uma mesma familia **compartilham quase todo o
texto** e diferem em uma linha de efeito. Prosa e exatamente o pior sinal
possivel para distingui-los.

Regra: fusao de identidade usa **chave explicita da fonte** (`remaster_id` /
`legacy_id`, que o AoN entrega prontos). Prosa serve como desempate quando a
chave falta, nunca como criterio.

E a metrica que me enganou: **"zero par nao unido" mede o que sobrou, nao o que
foi unido errado.** Uma metrica de recall sem a de precisao ao lado sempre
parece boa -- fundir tudo com tudo daria zero tambem.

### Metrica que divide pelo subconjunto errado esconde o buraco
Reportei "prosa em 100% (17.866/17.866)" varias vezes. O real e **95%**: ha
**907 registros sem prosa** numa base de 18.176.

O denominador estava errado. `emitir_textos.py` conta *referencias resolvidas
sobre referencias existentes* -- e registro que nunca ganhou referencia nenhuma
nao entra na conta. O caso que mais importa e justamente o que a metrica nao ve.

Vale para qualquer cobertura: **o denominador tem que ser o universo, nao o
subconjunto que ja foi processado.**

### Contar registro por livro nao mede cobertura
Afirmei que os PDFs oficiais nao adicionariam cobertura porque a base ja tinha
centenas de registros de cada um dos 11 livros de regra. A metrica estava certa
e a conclusao errada: um livro pode aparecer com 2.032 registros e ainda assim
faltar uma **categoria inteira**.

O que a contagem por `source.book` nao podia ver, e o teste adversarial viu:
**`ritual` nao existe na base.** Zero registros em 18.176, zero com o trait, e a
palavra nao aparece uma vez sequer na spec do schema. Nao foi falha de extrator
-- foi omissao ao escrever a lista de kinds em escopo.

Medir cobertura exige **gabarito externo**: as listas e o indice remissivo do
proprio livro enumeram o que ele contem. Cruzar essa lista contra a base acha
ausencia; contar o que ja esta la, nunca.

Fora rituals, a cobertura pontual medida foi 99,8% (3 misses em 1.345 nomes,
4 livros). O desvio e pequeno e concentrado -- mas concentrado e justamente o
que a metrica agregada esconde.

### `traits` nao e campo de precedencia, e campo de UNIAO
`traits` responde por **88% dos 2.299 conflitos** da base. A investigacao de por
que mostrou que quase nenhum deles e divergencia: e a regra de precedencia
aplicada a um campo onde ela conceitualmente nao cabe. Trait nao e um valor
escalar disputado -- e um **conjunto que cada fonte descreve parcialmente**.

Dos 137 casos com traits totalmente disjuntos entre as fontes, a classificacao:

| n | causa | exemplo |
|---|---|---|
| 72 | **facetas diferentes** -- foundry lista o trait de arma/armadura, aon lista o de item magico | `blade-byrnie`: foundry `flexible, noisy` / aon `invested, magical` |
| 31 | **ancestria renomeada no remaster** | foundry `nephilim` / aon `tiefling`, `aasimar`, `aphorite`; foundry `naari` / aon `ifrit` |
| 18 | **trait parametrizado vs trait base** | `bastard-sword`: foundry `two-hand-d12` / aon `two-hand` |
| 16 | **colisao de identidade** (dois itens homonimos distintos) | `death-from-above` |

As tres primeiras causas nao pedem escolha, pedem **merge**. E a escolha atual
esta ativamente destruindo dado:

- Nas **facetas**, escolher uma fonte joga fora metade do vocabulario do item.
- Nas **ancestrias**, `traits -> aon` injeta o nome **legado** numa base que se
  declara remaster-first. Direcao invertida, sistematicamente.
- Nos **parametrizados**, `two-hand-d12` vira `two-hand` -- perde-se exatamente
  a informacao mecanica que o construtor precisa. Acontece com arma do Player
  Core, nao com caso exotico.

Correcao: `traits` sai da tabela de precedencia. Passa a ser uniao, com
normalizacao de parametro (`fatal-d10` absorve `fatal`) e um mapa
legado -> remaster para nome de ancestria.

### Slug igual nao e entidade igual
Os 16 restantes sao outro problema: **a identidade `wb:<kind>/<slug>` assume que
nome e unico por kind, e nao e.** Existem homonimos legitimos no mesmo livro.

`Death from Above` sao dois feats: um de arquetipo no nivel 8 e um mitico no
nivel 16 (War of Immortals p.128). O Foundry separa os dois; o AoN indexa so o
mitico. A reconciliacao fundiu por slug e produziu uma quimera -- **nivel do feat
de arquetipo com nome, traits, raridade e texto do mitico**. `Reckless Abandon`
e o mesmo caso: feat de goblin e feat de barbaro nivel 16.

O sintoma que denuncia: **conflito com valores categoricamente disjuntos**
(`archetype` contra `mythic`, `goblin` contra `barbarian`) nao e divergencia de
fonte, e sinal de que duas entidades foram fundidas. Divergencia real e um
numero contra outro numero, ou uma grafia contra outra.

Vale como portao de qualidade: traits disjuntos entre fontes **depois** de
descontar as tres causas de merge acima devem falhar o build.

### O PDF impresso nao e arbitro das fontes digitais
Montei uma arbitragem para validar a tabela de precedencia da spec usando os
PDFs como verdade. Resultado: 63% de acerto geral, e **50% nos dois campos de
maior volume** (`traits`, que e 88% de todos os conflitos, e `level`).

Mas o numero importa menos que o defeito da premissa: em varios casos **nenhuma**
das tres fontes bate com o impresso. As fontes digitais incorporam errata
posterior a publicacao. Entao o teste nao mediu "quem acerta", mediu "quem
concorda com o impresso" -- que nao e a mesma pergunta.

Consequencia: a precedencia continua **sem validacao real**, e valida-la exige
historico de errata, que nenhuma das fontes expoe. Nao trocar a regra: sem
saber quem erra, inverter a direcao so troca qual metade fica errada.

### Metade dos PDFs oficiais e scan puro, e o tamanho denuncia
Dos 35 PDFs, os quatro maiores -- War of Immortals (235 MB), Monster Core
(289 MB), Treasure Vault (229 MB), Menace Under Otari (178 MB) -- **nao tem
camada de texto nenhuma**. `pdftotext` retorna vazio e `pdffonts` lista zero
fontes. `Lost Omens.pdf` e o mesmo caso: 40 bytes extraidos do documento
inteiro, e sem o texto nem da para identificar qual livro e.

Regra pratica: **rodar `pdffonts` antes de qualquer pipeline de extracao.**
Zero fontes = scan. Um PDF de regra acima de ~100 MB quase sempre e imagem.

Para tabela numerica densa em PDF assim, renderizar a pagina com `pdftoppm` e
ler a imagem foi mais confiavel que OCR via tesseract -- o OCR troca digito em
tabela de slots, e o erro passa despercebido porque o numero errado continua
plausivel.

### A base nao tem tabela de slots de NENHUMA classe conjuradora
Refinamento da licao acima sobre conjuracao: o buraco nunca foi so o Animist.
Nenhuma das 11 classes conjuradoras tem a tabela numerica de slots por rank
mecanizada -- so a progressao de proficiencia. O Animist apenas era o caso onde
faltava tambem a proficiencia, o que o tornou visivel.

Recuperadas do PDF na epoca: Animist (War of Immortals p.12-13, hibrido
prepared divine + spontaneous pela apparition), Magus e Summoner (Secrets of
Magic). Exemplar e Kineticist foram **confirmados como nao-conjuradores** -- nao
havia tabela faltando.

> **Correcao de 2026-07-27.** Este paragrafo ficou desatualizado nos dois
> sentidos. Para melhor: as 11 conjuradoras hoje tem a tabela completa em
> `base/index.json`, vinda do pf2etools. Para pior: a tabela do **Animist se
> perdeu** -- ele e a unica classe que dependia so do arquivo lido do PDF, e
> esse arquivo morava em `dados_brutos/`. Ver a licao seguinte.

### O AoN materializa tabela em `markdown`, nao em `text`
A licao mais cara desta sequencia, e a raiz de todas as outras. O doc de classe
do AoN tem **dois** campos de texto: `text`, achatado, sem tabela nenhuma, e
`markdown`, que carrega a pagina inteira em HTML -- **com as tabelas**.

O extrator lia so `text`. Dai saiu a conclusao "nem Foundry nem AoN
materializam a tabela numerica, so citam 'Animist Spells per Day' como nome de
tabela", que virou comentario de funcao, virou relatorio, virou item de TODO --
e mandou alguem ler as paginas 12-13 do War of Immortals a olho, num PDF que e
imagem pura. O resultado foi para um diretorio ignorado pelo git e se perdeu.

**O dado estava no cache que o proprio extrator ja baixava**
(`dados_brutos/aon/class__animist.json` tem o `markdown` com as duas tabelas).

Quando reextraido: as **11** classes conjuradoras tem a tabela completa, e o
parser reproduz **10 delas celula a celula** contra o pf2etools, que e fonte
independente. Validacao assim -- derivar de uma fonte e conferir contra outra
que ja estava na base -- e o que separa "extrai" de "extrai certo".

Regra pratica: antes de declarar que uma fonte **nao tem** um dado, listar os
campos que ela devolve e olhar o maior deles. `text` costuma ser projecao com
perda de um campo mais rico ao lado.

### "Reconstruivel pelos pins" nao vale para o que uma pessoa leu a olho
`pipeline/.gitignore` excluia `dados_brutos/` inteiro justificando que era
"reconstruivel pelos pins registrados na spec". Verdade para o clone do Foundry
(`buscar_fontes.sh`) e o dump do AoN (`dump_aon.py`). **Falso** para
`tabelas_conjuracao_pdf.json`, que veio de paginas renderizadas de um PDF
imagem-only e lidas a olho -- nao ha pin nem comando que refaca.

Ele sumiu sem ruido nenhum: nunca entrou no git (`git log --all
--diff-filter=A` sobre o caminho devolve vazio), o `TODO.md` seguiu marcando o
item 14 como CONCLUIDO, e o relatorio em `docs/` seguiu citando o caminho. O
build passava.

Tres coisas fizeram a perda ser recuperavel em parte:
1. o **relatorio** estava em `docs/`, que e versionado -- livro, pagina, metodo
   e todos os achados qualitativos sobreviveram;
2. a proficiencia registrada nele (1/7/15/19) **bate exatamente** com a base
   hoje, o que prova que o resgate e fiel e nao reconstrucao de memoria;
3. Magus e Summoner tinham segunda fonte (pf2etools), entao nao dependiam dele.

O que nao voltou: a matriz `slots_per_level` do Animist, que era dado de fonte
unica.

Regra que ficou, materializada no **portao 8**: dump de fonte reproduzivel por
pin vive em `dados_brutos/` e fica fora do git; **tudo que exigiu leitura,
julgamento ou arbitragem humana vive em `dados_derivados/` e vai para o git**.
O teste e uma pergunta so -- existe comando que refaz isso sozinho? Perda
conhecida fica registrada em `artefatos_perdidos.json` com motivo, dano medido
e decisao. O portao nao impede perda; impede perda **silenciosa**.

Corolario de metodo: a varredura que achou isso -- conferir todo caminho citado
em arquivo versionado contra o disco -- custou segundos e achou **3** ausencias
em 42 caminhos. Vale rodar em qualquer projeto que guarde artefato fora do git.

### Trait no PF2e e vocabulario puro, nao mecanica
0 de 561 traits tem efeito estruturado. Os campos `resistance`/`weakness`/
`speed`/`skill_mod` do AoN vem vazios em 100% deles, e o Foundry
(`src/scripts/config/traits.ts`) e so dicionario slug->rotulo, sem rule element.
541/561 tem `trait_group`, que e taxonomia e nao mecanica.

Consequencia: nao adianta procurar efeito de trait em fonte nenhuma. Se o
construtor precisar de mecanica por trait, ela e nossa e tem de ser escrita.
