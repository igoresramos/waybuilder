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

### Heranca nao tem trait em fonte nenhuma -- o que existe e o vinculo
Ao portar a pele do Pathbuilder (2026-07-28) o picker parecia bugado: clicar
numa heranca, numa classe ou num arquetipo nao mostrava trait alguma. A suspeita
obvia -- extrator perdendo campo -- estava errada. Medido nas duas fontes:

| kind | nossa base | Foundry (fonte) |
|---|---|---|
| heranca com trait | 67 / 334 | **66 / 326** |
| classe com trait | 0 / 27 | **0 / 27** |

`Ambitious Human` no Foundry tem `system.traits.value: []` e
`system.ancestry: {name: "Human"}`. O AoN idem: `Fighter` e `Acrobat` vem sem
`trait`. Ou seja: a base espelha a fonte com fidelidade; o que a fonte guarda no
lugar da trait e o **vinculo** (`ancestry`), e a base ja o preserva.

O que a tela faz agora: mostra o vinculo marcado como vinculo -- borda accent,
nao pastilha cheia -- e reserva o aviso vermelho `sem trait na fonte` para quem
nao tem nem trait nem vinculo. Derivar `traits: ["human"]` a partir do vinculo
foi considerado e recusado: fabricaria dado que nenhuma fonte declara e faria a
base deixar de ser espelho -- e `_termo_trait` passaria a satisfazer requisito
com dado inventado.

Metodo que vale repetir: **antes de acusar o pipeline de perder campo, contar o
campo na fonte bruta.** Custou tres comandos e evitou uma re-emissao inteira da
base sobre um defeito que nao existia.

### One for All nao esta na base
Feat de Swashbuckler citado pelo Igor; a base tem 79 feats com trait
`swashbuckler` e esse nao esta entre eles. Ausencia real, ainda nao
diagnosticada -- entra na trilha de censo de ausencias, nao na de UI.

### O payload enxuto amputava o app em silencio
O `sincronizar-base.sh` copiava 8 dos 54 kinds para segurar a carga inicial em
0,53 MB. O custo nao aparecia como erro em lugar nenhum: o motor calcula ataque
e dano por arma, CA com cap de DEX e escudo, slots das 11 conjuradoras e ficha
de companheiro -- e sem `weapon`, `armor`, `shield`, `spell` e
`animal-companion` no payload, nada disso tinha dado com que trabalhar. A aba de
Ataques dizia "nenhuma arma equipada" para sempre e todo personagem saia pelado,
como se fosse comportamento correto.

Pior: 44 das 441 opcoes de subclasse apontavam para 8 kinds ausentes
(`instinct`, `cause`, `mystery`, `hunters-edge`, `lesson`, `patron`,
`arcane-school`, `arcane-thesis`), entao o slot de instinto do Barbaro abria um
picker **vazio** -- o motor tinha os ids, o payload e que nao levava os
registros.

Base inteira: 1,09 MB gzip, cacheada na primeira visita. O gargalo real nunca
foi o indice: a prosa sozinha tem 19 MB e continua sob demanda.

Duas regras que ficam:
1. **Orcamento de bytes que corta CAPACIDADE precisa de teste que falhe.** Nao
   havia um so teste dizendo "personagem com arma equipada tem ataque"; o corte
   passou por 77 testes verdes.
2. **Lista do que carregar vem do manifesto, nao de um array no codigo.** Kind
   novo no pipeline passa a viajar sozinho, e some a classe inteira de defeito
   "esqueceram de editar a constante em dois lugares".

### Campeao sem causa e Bruxa sem patrono
Ao levar a base inteira para o app, 44 opcoes de subclasse que nao resolviam
cairam para 23 -- e as 23 restantes nao sao problema de payload, sao buraco de
DADO: o registro nao existe em `index.json`.

- **8 sao `-legacy`** (`instinct/animal-legacy`, `mystery/ash-legacy`, ...):
  sumiram na fusao Remaster e a referencia ficou apontando para o morto. Defeito
  de integridade referencial pos-fusao -- a fusao apaga o registro legado mas nao
  reescreve quem o citava.
- **6 sao as causas do Campeao** (paladin, redeemer, liberator, tyrant,
  desecrator, antipaladin) e **8 sao os patronos da Bruxa**. Nunca foram
  extraidas. Consequencia pratica: hoje essas duas classes abrem o slot de
  sub-escolha com zero opcoes.

Travadas uma a uma em `fluxo.test.ts` (`ORFAS_CONHECIDAS`), para que o numero so
possa cair: se subir e regressao, se descer o teste cobra a atualizacao da lista.
A correcao pertence ao pipeline (extrator + `resolver_referencias.py`), nao ao app.

### O slot que nao passava pelo motor
O picker de Heranca oferecia as 334 herancas para qualquer ancestralidade -- dava
para fazer um Anao com heranca elfica. A causa nao era o motor: `_aceita_no_slot`
ja fazia exatamente esse gate para feat de ancestria. A tela e que montava este
slot com a lista CRUA (`cru(opcoesDe("heritage"))`, `atende: true` fixo) em vez
de perguntar a `candidatos()`.

O dado para o gate ja estava na base: **309 das 334 herancas declaram
`ancestry`**. As 25 sem o campo sao as versateis do PF2e (Aiuvarin, Nephilim,
Dhampir, Changeling, Suli...), abertas a qualquer ancestralidade -- a ausencia do
campo E a identificacao delas, nao um buraco. Anao passou de 334 para 34 opcoes:
9 anas + 25 versateis.

Regra que fica: **todo slot pergunta ao motor.** Onde a tela monta a lista
sozinha ela vira uma segunda implementacao da regra, sem teste e sem o dado que
o motor tem. Verificados os outros usos de `cru()` -- ancestralidade, background
e classe nao tem gate estrutural, entao ali a lista crua esta correta.

Detalhe de comportamento: sem ancestralidade escolhida, mostrar TUDO. Lista vazia
num slot recem-aberto parece defeito, e o jogador ainda vai voltar ali.

### As 16 pericias de reino do Kingmaker moram no mesmo kind
A ficha listava 33 pericias, e o Igor pegou comparando com o Pathbuilder dele.
As 16 sobrando -- Agriculture, Arts, Boating, Defense, Engineering, Exploration,
Folklore, Industry, Intrigue, Magic, Politics, Scholarship, Statecraft, Trade,
Warfare, Wilderness -- sao as **Kingdom Skills do Kingmaker**, que a base guarda
no mesmo `kind: skill` das de verdade, marcadas com `lore: true` e **sem
`attribute`**. Regra de reino esta fora do escopo do projeto.

Sem `attribute`, elas caiam no fallback de INT e apareciam somando +INT numa
ficha comum. O sintoma (`+1` em tudo) nao parecia bug de catalogo.

Pegadinha dentro da pegadinha: o `Lore` generico tem **`lore: false`**, entao
filtrar por `lore !== true` nao o remove. Sao dois criterios distintos --
`lore: true` tira as de reino, e o id `wb:skill/lore` tira a categoria. A ficha
mostra **16 fixas**; a 17a linha do Pathbuilder e a `Lore: Alcohol` que o
background concede, e essa vem de `proficiencias`, nao do catalogo.

### Marcacao do Pf2eTools sobra em 53% dos requisitos
`requires_texto` vem com a sintaxe de link da fonte -- `trained in
{@skill Athletics|PC1}`, `{@feat Everstand Stance|LOCG}` -- em 2.112 dos 3.960
feats que tem requisito. Sem limpar, o pre-requisito fica ilegivel justo onde
precisa ser lido de relance.

Uma regra so cobre as 20 tags observadas (`{@tag Rotulo|FONTE|apelido}` -> o
primeiro campo, ou o apelido quando ha). Mas **as tags aninham**:
`{@note (or {@feat Shape of the Cloud Dragon|SoT3})}` derrubava um `[^}]*`
ingenuo. Resolver de dentro para fora ate estabilizar cobre qualquer
profundidade -- e um teste varre a base inteira cobrando que nenhum requisito
sobre com `{@`.

### Dedicacao era inalcancavel pelo slot de feat de classe
Ao alinhar as abas do picker com o Pathbuilder (`De classe | Dedicacoes |
De arquetipo | Todos`), a aba de dedicacoes saiu VAZIA -- e o motivo nao era a
tela. `_aceita_no_slot("class_feat")` exigia que o feat tivesse a trait da
classe, e **nenhuma das 226 dedicacoes carrega trait de classe**. Resultado: a
unica porta para dedicacao era o slot de Free Archetype.

Isso e contra o RAW -- no PF2e oficial se entra num arquetipo gastando um slot de
feat de CLASSE -- e e especialmente ruim num projeto cuja regra da casa
substitui a dedicacao: sem o caminho RAW funcionando nao da para comparar os
dois. Corrigido: o slot aceita tambem `archetype`. A regra 23 continua marcando
a dedicacao da propria classe como fora-do-requisito, sem esconder.

**A licao de metodo e o oraculo.** A correcao no TS quebrou 20 testes de paridade
contra o gabarito Python de uma vez -- exatamente o que o gabarito existe para
fazer. Corrigir so o lado que estava na frente teria criado duas regras
divergentes em silencio. O ciclo certo: corrigir nas DUAS implementacoes, rodar
os 95 testes do Python, `gerar_fixtures.py`, e so entao os do TS. Vale para
qualquer mudanca em `candidatos` ou `_aceita_no_slot`.

### A prosa das fontes vem em bloco unico, mas tem estrutura recuperavel
O texto que o picker mostrava era um paragrafo so com tudo colado -- nome, custo
de acao, livro, gatilho, requisito, efeito e, nas ancestralidades, seis secoes de
folclore. Ilegivel na pratica.

A estrutura existe e foi MEDIDA, nao chutada. Ha duas familias:

| familia | marca | kinds |
|---|---|---|
| item de regra | separador `---` entre cabecalho e corpo | feat 98%, spell 100%, weapon 91%, equipment 89% |
| descritivo | rotulos nomeados, sem `---` | ancestry, heritage, background, class, archetype (0%) |

Os rotulos sao vocabulario fixo da Paizo e dao a classificacao de graca:
REGRA -- `Frequency`, `Trigger`, `Requirements`, `Effect`, `Special`, os quatro
graus de sucesso; SABOR -- `You Might`, `Others Probably`,
`Physical Description`, `Society`, `Alignment and Religion`, `Names`,
`Adventurers`, `Ethnicities`. Os seis primeiros aparecem em **50 das 50**
ancestralidades.

Tres pegadinhas que custaram iteracao:
1. **Delimitar a fonte pelo proximo rotulo nao funciona.** Na ancestralidade nao
   ha rotulo entre `Source ... pg. 62` e a descricao, e a fonte engolia o texto
   inteiro. Quem fecha a fonte e o formato dela: `<livro> pg. <numero>`.
2. **A abertura sem rotulo e ambigua** -- num feat e o efeito, numa ancestralidade
   e a descricao. O desempate esta na companhia: se ha blocos de sabor e nao ha
   `---`, a abertura e sabor.
3. `You Might...` deixa a reticencia para tras ao casar o rotulo.

Na tela: campos curtos primeiro (com barra accent), efeito no meio, e a fantasia
RECOLHIDA atras de "ler a descricao (7)" -- ela nao some, porque escolher
ancestralidade e metade sabor, mas nao ocupa a tela de quem compara dois feats.

### Trait parametrizado nao tem registro proprio
62 slugs distintos nao existem como `wb:trait/*` -- `two-hand-d8` (155 usos),
`versatile-p` (71), `deadly-d8` (53), `thrown-20` (37). Nao e buraco de dado: o
parametro faz parte do nome. Apareciam crus e minusculos no meio de traits em
caixa alta. Formatador proprio, com as convencoes do PF2e: dado minusculo
(`Deadly d8`), letra de dano maiuscula (`Versatile P`), numero solto e distancia
(`Thrown 20 ft.`). Um teste varre a base cobrando que nenhum trait saia em
minuscula.

### Auditoria de arquetipos: o que dava para consertar e o que nao dava
Aplicados quatro consertos, todos no PIPELINE (o app nunca corrige dado):

1. **407 feats de arquetipo nao exigiam a propria dedicacao.** A regra existe no
   livro -- "You can't select a feat from an archetype unless you have its
   dedication feat" -- escrita UMA vez e nunca repetida em cada feat, e por isso
   nenhuma das tres fontes a poe em `requires`. Dava para pegar `Absorb Spell`
   sem nunca ter pego `Spellmaster Dedication`. Derivado em
   `derivar_gate_arquetipo.py`, como conjuncao que preserva o requisito
   existente. **Isto nao e fabricar dado**: a diferenca em relacao a inventar
   trait de heranca (recusado) e que aqui a regra esta escrita e vale para todos.
2. **26 ids orfaos em `requires`.** A fusao renomeia o registro (`Attack of
   Opportunity` -> `Reactive Strike`, `Gnoll` -> `Kholo`) e guarda o nome antigo
   em `aliases`, mas nao volta para reescrever quem citava o morto. 24 tinham
   alias -- o mapa existia, so nunca fora aplicado. **O portao 3 foi de 26 para
   0.**
3. **Fighter Dedication treinava so armas simples.** O texto oficial da simples
   E marciais; conferido no Foundry, o unico rule element de proficiencia e
   `attacks.simple.rank`. A fonte esta incompleta, nao o extrator -- caso de
   curadoria, com a guarda de `valor_atual` que impede sobrescrever em silencio
   se a fonte consertar depois.
4. **`grants_completos: true` mentia.** `not tinha_mecanica -> True` tratava
   "a fonte nao declarou nada" como "converti tudo". 61 dedicacoes tinham
   `grants: []` e `grants_completos: true` ao mesmo tempo. Passa a `None`, que
   obriga quem le a tratar o caso.

**O que NAO deu para consertar, e por que nao e preguica:** as 61 dedicacoes sem
mecanica (Cavalier deveria dar montaria, Blessed One `lay on hands`) e o
spellcasting das dedicacoes de conjurador. Fui a fonte: no Foundry, **45 das 192
dedicacoes tambem tem zero rule elements**, e Wizard Dedication tem UM (arcana).
O dado nao existe em forma estruturada em lugar nenhum -- e o mesmo padrao das
traits de heranca e das causas do Campeao. Exige mecanizacao manual via
curadoria, uma a uma.

Mudar dado quebrou a paridade de novo -- 3 fichas do gabarito. O ciclo e sempre:
mudou base ou regra -> `teste_motor.py` (95) -> `gerar_fixtures.py` -> vitest.

### O comparador mentia mais que a base
Escrevi `comparar_com_aon.py` para cruzar a base contra o dump do AoN e ele
acusou **~370 ausencias**. Os quatro agentes de triagem devolveram o mesmo
veredito, cada um pelo seu lado: **quase nada era ausencia real.** Dois defeitos
meus, os dois de identidade:

1. **Homonimo colidia.** 647 dos 2.461 nomes de magia se repetem (reimpressao em
   Adventure Path). Um `dict[norm(nome)]` deixava o ultimo processado vencer em
   silencio, e a comparacao de campo atribuia id errado.
2. **Nao seguia o rename.** 800 docs do dump trazem `remaster_id` apontando para
   o sucessor, e a nossa base guarda o caminho inverso em
   `aliases`/`historico`/`legado_de`. Comparar so por nome acusava ausencia onde
   houve troca de nome.

Depois de casar pelos dois lados: **magia 158 -> 0, feat 163 -> 5, heranca
12 -> 0, ritual 10 -> 0, arquetipo/divindade/ancestralidade -> 0**.

A licao vale alem deste script, e a wiki ja tinha a frase: *identidade pede chave
explicita, nao similaridade de texto*. **Ferramenta de auditoria precisa ser
auditada antes de se acreditar nela** -- eu quase abri 370 itens de trabalho
inexistente, e o que salvou foi mandar quatro agentes conferirem item a item em
vez de confiar no numero agregado.

### O que a comparacao realmente achou: campo mecanico vazio
O valor nao estava em "falta conteudo", estava em "o conteudo esta la e nao
funciona":

- **110 de 1.041 armas sem `damage`**, entre elas `Fist` e `Shield Bash` -- que
  toda ficha usa;
- **14 de 216 armaduras sem `ac_bonus`**, entre elas `Leather`, `Hide` e
  `Studded Leather`. Equipar couro nao mudava numero nenhum.

E de novo **nao era falta de fonte, era falha de matching**, com duas causas
confirmadas no disco: o Foundry escreve `Leather Armor` onde o AoN escreve
`Leather`, e `Fist`/`Shield Bash` nao existem como arquivo no Foundry (so no
dump do AoN). Recuperados 63 registros.

Pegadinha dentro do conserto, que eu mesmo criei e precisei reverter: indexar a
fonte so por nome fazia `Hide` (armadura) casar com o primeiro item cujo nome
colapsasse em "hide" na ordem arbitraria do `glob` -- entrou `ac_bonus: 2` onde
a fonte diz 3. **A chave tem de incluir o TIPO.** Reverti do backup e refiz;
guardar `index.json` antes de todo passo destrutivo pagou-se na primeira vez.

### Campeao e Bruxa: o conteudo estava la o tempo todo
Eu havia reportado ao Igor que as 6 causas do Campeao e os 8 patronos da Bruxa
"nao existem na base". **Errado, e a correcao mudou o custo do conserto de caro
para trivial.** `kind:cause` tem 7 entradas e `kind:patron` tem 17, com texto
oficial. O que quebrou foi a REFERENCIA: as classes citavam os ids que a fusao
aposentou (`wb:cause/paladin` -> `wb:cause/justice`).

E o vinculo estava no proprio dado, em `historico[].id_legado` -- nao precisou
tabela escrita a mao nem extracao nova. Bastou estender o passo de aliases para
varrer tambem `subclasses[].opcoes`, e nao so `requires`. Resultado: `cause`
13/13, `patron` 24/24, `lesson` 20/20, `instinct` 16/16.

Metodo que se confirma: **antes de declarar que falta conteudo, procure o
conteudo sob o nome novo.** Ja falhei nisto duas vezes no mesmo dia.

### Item magico herda a base, e o livro diz isso na prosa
Sobravam 11 armaduras e 7 escudos sem numero -- `Celestial Armor`, `Demon
Armor`, `Sturdy Shield`, `Mithral Shield`. Procurei nas TRES fontes: o Foundry
nao tem esses itens, o Pf2eTools so traz `bulk` e `category`, o AoN idem. Parecia
lacuna sem saida.

Nao era. No PF2e a armadura magica **herda a estatistica da base**, e o livro nao
repete os numeros -- mas DECLARA a base, no cabecalho do proprio texto:

    Celestial Armor ... Bulk 1 Base Armor Chain Mail --- This suit of +2 ...
    Sturdy Shield   ... Bulk 1 Base Shield Steel Shield --- With a superior ...

E campo estruturado morando na prosa. Extrair `Base (Armor|Shield|Weapon) X` e
herdar o bloco do item base resolveu 10 dos 18. `Celestial Armor` agora e
`ac_bonus 4, dex_cap 1, check_penalty -2`, herdado de `chain-mail`.

`Unarmored` era caso a parte e ficou explicito: nao e armadura, e a AUSENCIA
dela, entao `ac_bonus: 0` declarado vale mais que nulo -- o motor para de
precisar de caso especial.

Saldo: armadura 14 -> 5, escudo 7 -> 5, arma 110 -> 54. O que sobra nao declara
base em fonte nenhuma (`Elven Chain` e `Mithral Shield` falam de MATERIAL, nao de
item base) ou sao bombas alquimicas, cujo dano e do efeito e nao da arma.

### Service worker devolvendo a pagina no lugar do dado
O Igor viu `Unexpected token '<', "<!doctype "...` e a tela dizendo "nao
carregou a base". O servidor estava certo -- `curl` devolvia 200 em todos os 54
kinds, e o headless limpo carregava. Era **service worker de build anterior**
ainda registrado: o `vite-plugin-pwa` poe `navigateFallback: index.html`, e um
recurso fora do precache volta como HTML.

Dois consertos, e o segundo importa mais que o primeiro:
1. `navigateFallbackDenylist: [/^\\/base\\//]` -- pedido de dado nunca recebe
   pagina;
2. `buscarJson()` detecta resposta que comeca com `<` e diz **o que fazer**
   (desregistrar o service worker), citando a URL. O `JSON.parse` cru nao
   dizia nem qual arquivo falhou.

Licao de metodo: o erro do usuario nao reproduzia no meu ambiente porque meu
headless nao tinha service worker. **Reproduzir com o estado do usuario, nao com
o meu**, e o que separou "funciona aqui" de achar a causa.

### O passo que conserta tem que rodar depois do passo que quebra
`aplicar_aliases_em_requires.py` existe para reescrever quem cita um id que o
remaster aposentou. Ele estava no passo 4h3 -- **antes** da fusao legacy/remaster
(passo 7), que e exatamente quem aposenta o id. Ao rodar, nao havia orfa
nenhuma: `metamagical-experimentation` ainda existia. A fusao o absorvia em
seguida e ninguem voltava para reescrever a referencia.

Funcionou na sessao em que foi escrito porque rodei o script **a mao**, sobre uma
base ja fundida. Integrado ao `build.sh` na posicao errada, regrediu em silencio.
Quem pegou foi o teste de paridade com o oraculo Python, nao os portoes.

Tres licoes, em ordem crescente de valor:

1. **Ordem de pipeline e semantica, nao arrumacao.** Passo que conserta
   referencia vai depois de quem mata o id. Mover de 4h3 para 7c: 26 -> 47 ids
   resolvidos.

2. **Portao cego ao proprio conserto e decoracao.** O portao 3 varria `requires`
   e nunca `subclasses[].opcoes` -- o campo que o passo 7c conserta nao era
   verificado por ninguem. Ampliado, acusou 16 orfas na hora. Ao escrever um
   passo de conserto, checar se algum portao olha o campo que ele toca.

3. **Consertar um defeito revela o que ele escondia.** Com os ids vivos de novo,
   o Campeao passou a oferecer `Justice` DUAS VEZES: a mesma causa existe como
   `wb:cause/justice` e como `wb:class-feature/justice`, e a fusao nao as pareia
   porque compara dentro do kind. Enquanto uma das duas era orfa, o app
   descartava e ninguem via. Dai `colapsar_opcoes_irmas.py`.

E a licao de metodo: os **nove portoes ficaram verdes** sobre uma base que
oferecia a mesma causa duas vezes na tela. Verificacao de dado nao substitui
abrir o app. `app/verificacao/verificar-eixos.mjs` existe por isso.

### `rm -rf` no `public/` derruba o dev server, e parece cache
`sincronizar-base.sh` apagava `public/base` inteiro antes de copiar. Com o Vite
de pe, o servidor perde o handle do diretorio e passa a responder `index.html`
para todo pedido em `/base/` -- que chega no navegador como
`Unexpected token '<', "<!doctype "...` **com o arquivo intacto no disco**.

Sintoma cruel: `ls` mostra o JSON, `curl` devolve `text/html`, e o defeito so
some ao reiniciar o servidor. Parece cache do navegador; nao e. Foi
provavelmente parte do que o Igor viu em 2026-07-28, junto com o service worker.

Conserto: limpar o CONTEUDO, nunca o diretorio.

    mkdir -p "$DESTINO/por-kind" "$DESTINO/text"
    rm -f "$DESTINO"/por-kind/*.json "$DESTINO"/text/*.json "$DESTINO"/_manifesto.json

Provado nos dois sentidos: com o servidor de pe, sincronizar antes devolvia
`200 text/html`; depois do conserto devolve `200 application/json`.

### Verificador que passa sem ter verificado e pior que verificador que falha
A primeira versao de `verificar-eixos.mjs` imprimiu "todos os eixos com uma
opcao por nome" tendo encontrado ZERO eixos -- o clique de escolher a classe
nao acontecia, a lista de eixos saia vazia, e o laco nao rodava nenhuma vez.
Verde perfeito, cobertura nenhuma.

Duas guardas entraram por causa disso:
1. lista de eixos vazia **falha**, e imprime os slots que achou na tela;
2. a varredura da lista virtualizada acumula em `Set` e mede repeticao DENTRO de
   cada leitura. Acumular em array fazia o total crescer a cada rolada (o mesmo
   item e relido), o laco nunca convergia, e o script travava em vez de mentir
   -- que foi sorte, nao projeto.

Vale para qualquer verificador: se ele pode chegar ao fim sem ter olhado nada,
o caminho vazio tem que ser FALHA, nunca sucesso.

### Pathbuilder roda local, mas nao inicializa (parcial)
So a PAGINA do Pathbuilder esta atras do Cloudflare (403 em headless). O CDN de
assets responde 200 a `curl` sem verificacao nenhuma. Da para baixar o app
inteiro -- inclusive `data131.txt`, 4,2 MB de dados do jogo que so aparece
rastreando as requisicoes depois do "Accept" -- e servir local.

Resultado: menu completo com ids estaveis (`sidenav-json`, `sidenav-new`,
`sidenav-feat-browser`), IndexedDB criado, zero erro de JS. Mas a tela fica no
spinner "Loading" para sempre.

Duas hipoteses gastas, ambas FALSAS:
- asset faltando -- resolvido com `page.route()` servindo o CDN do disco;
- POST recusado pelo `python -m http.server` (`501`) -- `servir.py` passou a
  responder `200 {}` e nao mudou nada.

**RESOLVIDO na mesma sessao, e a suspeita estava certa:** o bundle tem
`"www.pathbuilder2e.com" == window.location.hostname` e, fora desse host, para
para pedir permissao de storage -- sem timeout, entao a tela fica em "Loading"
sem erro nenhum. Achado com um `grep -o "location\.[a-zA-Z]*"` no minificado,
que custou dois minutos; as duas hipoteses anteriores custaram uma sessao.

A saida foi elegante e vale de padrao: **navegar para a URL real e servir tudo
do disco por `page.route()`**. O hostname passa a bater sem tocar em
`/etc/hosts` e sem que um byte saia da maquina -- o Cloudflare nunca e
contatado. Receita completa em `docs/2026-07-29_pathbuilder-local.md`.

Licao de orcamento, que vale mais que a tecnica: parei ao ver que a proxima
pista exigia ler minificado. Frente com custo aberto e retorno incerto merece
uma caixa de tempo -- e um registro do que ja foi descartado, para o proximo
nao repetir as mesmas duas hipoteses.

## "Falta modelar X" pode ser "falta ligar X" -- medir antes de escrever motor

O plano dizia que companheiro exigia modelo novo no motor. Antes de escrever
uma linha, li o motor: `cap_ator`, `_maturidade_do_companheiro`,
`_resolver_grau_incredible` e `_ficha_de_companheiro` ja estavam la, nas DUAS
implementacoes, com teste. O que faltava era uma ponta antes -- nenhum feat da
base declarava conceder companheiro, entao o ator so entrava por
`doc["atores"]` escrito a mao.

O trabalho real foi um termo de dado (`grant_actor`), um casamento por
`concedido_por` + `em` e um slot na tela. Nada de matematica nova.

**Como aplicar:** ao pegar um item de divida escrito por mim mesmo em sessao
anterior, reler o codigo antes de aceitar o diagnostico. Divida herdada
descreve o sintoma da epoca, nao o estado de hoje -- foi a SEGUNDA premissa
minha derrubada por medicao em duas sessoes seguidas (a primeira: "so o
Pathbuilder resolve as 61 dedicacoes").

E o efeito colateral que so aparece ligando as pontas: com a concessao, o motor
passou a saber em que NIVEL o feat foi pego, e dai a classe. O cap da regra 17b
deixou de ser chutado na classe de maior nivel -- num `Ranger 3 / Fighter 5` o
companheiro do Ranger dava 7 e agora da 5. O conserto nao estava no plano;
apareceu porque o dado novo carregava a resposta.


## No minificado, procure a CONSTANTE, nao a logica

Duas sessoes gastas em hipoteses de infraestrutura (asset faltando, POST
recusado) para um app que travava por checar o proprio hostname. O que resolveu
foi grepar o bundle por `location.` -- cinco ocorrencias, uma delas a resposta.

**Como aplicar:** app de terceiro que trava sem erro, sem requisicao pendente e
sem timeout esta esperando uma CONDICAO, e condicao em codigo minificado
costuma comparar contra uma constante legivel (hostname, versao, chave de
storage). Grepar por essas constantes e barato e responde antes de qualquer
teoria sobre rede. Ler minificado assusta mais do que custa quando se procura
uma string, e nao um fluxo.

## Semelhanca de nome nao e evidencia -- pergunte a fonte

Escrevi num relatorio que o remaster tinha encurtado os nomes de 12 dedicacoes
e que a nossa base servia o legado. O padrao era limpo demais para ser
coincidencia: `Nantambu Chime-Ringer` -> `Chime-Ringer`,
`Jalmeri Heavenseeker` -> `Heavenseeker`, `Turpin Rowe Lumberjack` ->
`Lumberjack`. Parecia obvio.

Ao ir corrigir, a fonte disse o contrario: a ponte `remaster_id` do AoN nao
registra nenhum desses pares, e os nomes curtos nao existem em nenhum dos
43.686 docs do dump. Quem renomeia e o **Pathbuilder**, tirando nome proprio de
Golarion -- Product Identity, quase certamente licenciamento.

Se eu tivesse "corrigido" a base, teria trocado 22 nomes CERTOS por nomes que
nenhuma fonte oficial usa, num passo do pipeline, em silencio.

**Como aplicar:** quando dois conjuntos divergem e o padrao "explica" a
divergencia, a explicacao e HIPOTESE ate a fonte confirmar. O teste custa
minutos -- `o nome deles existe na minha fonte?` -- e a diferenca entre
confirmar e supor e a diferenca entre uma tabela de traducao e um estrago no
dado. Vale especialmente quando o outro lado e um app, e nao um livro: app tem
motivo proprio (licenca, tela, versao) para se afastar da fonte.

## Codigo morto nao e so peso -- ele mente sobre o que o app faz

Escrevi numa spec que "a ficha ja tem o bloco de Conjuracao e itera
`visao().conjuracao`". Tinha lido isso em `src/telas/Ficha.tsx`. O arquivo esta
la, compila, tem o bloco -- e **nao e importado por ninguem**. A ficha viva e
outra, e ela nao mostrava conjuracao nenhuma: nem a de arquetipo (que eu estava
implementando), nem a de CLASSE, que o motor calcula desde o primeiro dia e o
porte TS reproduz campo a campo.

Ou seja: um conjurador montado no app nunca viu um slot de magia, e nem os 124
testes do oraculo nem os 113 do porte podiam pegar isso -- os dois medem o
motor, e o motor estava certo.

**Como aplicar:** antes de afirmar "a tela ja faz X", conferir quem IMPORTA o
arquivo, nao se o arquivo existe (`grep -rn "<Componente"` resolve em segundos).

`Picker.tsx` e `Ficha.tsx` foram REMOVIDOS em 2026-07-29, com a autorizacao do
Igor e depois de conferir importador por importador -- 315 linhas que existiam
so para enganar a proxima leitura.

## Convencao de um lado, switch do outro -- o porte esquece a terceira linha

O motor Python despacha termo de predicado por convencao:
`getattr(self, f"_termo_{termo}")`. Metodo novo ja fica ativo. O porte
TypeScript despacha por `switch` explicito.

Ao adicionar tres termos (`sense`, `focus_pool`, `has_actor`) escrevi os seis
metodos -- e esqueci as tres linhas do `switch`. O TS passou a IGNORAR os termos,
e ignorar nao reprova (principio zero: termo desconhecido nao arbitra), entao
nada estourou: mudou so a ORDEM da lista de candidatos. Quatorze fichas
divergiram do gabarito com uma mensagem obscura -- `candidatos.free_archetype@2[31]`,
um feat no lugar de outro.

**Como aplicar:** termo novo mexe em TRES lugares, nao dois -- o metodo no
Python, o metodo no TS, e a linha do `switch`. E a terceira e a unica que nao
falha sozinha: sem ela o codigo compila, roda e mente baixinho. Quem pegou foi o
teste de paridade entre as duas implementacoes; nenhum teste de motor pegaria,
porque cada lado estava coerente consigo mesmo.

## `npx tsc --noEmit` nao e o build -- ele nao viu dois erros meus

Rodei `npx tsc --noEmit` a cada mudanca do porte e ele passou limpo o dia
inteiro. Ao remover codigo morto, rodei `npm run build` (`tsc -b && vite build`)
por precaucao e apareceram **dois erros de tipo introduzidos por mim naquele
mesmo dia**: um `em` alargado para `string | number` onde o contrato pedia
`number | "criacao" | null`, e um `Dict[]` devolvido onde a `Visao` declara uma
lista tipada.

A diferenca: `tsc --noEmit` sem argumento usa o tsconfig da raiz; `tsc -b`
percorre as REFERENCIAS do projeto, e e nele que o app de verdade e checado.

**Como aplicar:** neste projeto a checagem que vale antes de dar por pronto e
`npm run build`, nao `npx tsc --noEmit`. O segundo serve para o ciclo rapido de
edicao; o primeiro e o que diz se o app compila. E o mesmo padrao de "verde
sobre uma medicao que nao mede o que interessa" que ja apareceu nos portoes e no
verificar-eixos: a checagem barata passa, e a que importa nao foi rodada.

## Passo que ENRIQUECE roda depois de quem DERIVA -- e a invariante fica velha

`mechanized == bool(grants)` e derivado uma vez, no reconciliador (passo 2 do
build). Tres passos posteriores -- `derivar_mecanica_dedicacao` (7e),
`derivar_concessao_de_ator` (7f) e `derivar_spellcasting_arquetipo` (7g) --
APPENDAM em `grants` e nenhum refazia a conta. Resultado: 26 registros com
`grants` cheio e `mechanized: false`.

Nao foi um esquecimento, foram TRES, escritos em dias diferentes. Isso descarta
"falta de atencao" como causa: o desenho e que convida ao erro, porque o campo
derivado mora a sete passos de distancia de quem o invalida.

**Como aplicar:** quando um campo e derivado de outro, todo passo que escreve na
origem precisa refazer o destino -- e a unica coisa que garante isso e um teste
de invariante sobre o artefato final, nao a disciplina de quem escreve o passo.
Aqui quem achou os tres foi `test_mechanized_e_derivado_de_grants`, rodando
sobre `base/index.json`. Antes de adicionar um passo novo ao `build.sh`, olhar
que invariantes o artefato ja carrega.

## `git stash` para testar o HEAD e uma armadilha neste repo

Quis saber se dois testes vermelhos eram meus ou pre-existentes e fiz `git stash`
para rodar a suite no HEAD limpo. O `stash pop` falhou duas vezes: primeiro por
um `.pyc` TRACKED (ha 3 em `pipeline/__pycache__/`), depois pelo `.claude.json`
da raiz, que o hook de auto-save reescreve o tempo todo. O trabalho ficou preso
no stash com a arvore revertida.

Recuperado com `git checkout stash@{0} -- <caminho do projeto>`, que traz so os
caminhos que interessam e ignora os arquivos em disputa. Mas esse comando deixa
tudo STAGED, e o commit seguinte engoliu dois consertos independentes numa
mensagem so -- corrigido com `git reset --soft HEAD~1` + `git reset`.

**Como aplicar:** para saber se um vermelho e pre-existente, `git stash` nao e o
caminho neste repo (Tartarus tem auto-save escrevendo na raiz). Use
`git worktree add` num diretorio temporario, ou rode a suite contra
`git show HEAD:<arquivo>`. E depois de qualquer `git checkout <ref> -- <path>`,
conferir o INDICE antes de commitar: ele nao esta vazio.

## Medir as chaves que voce ESPERA nao e medir o dado

Ao estreitar o tipo da opcao de `ChoiceSet` no TS, medi a base inteira -- e medi
`rotulo` e `valor`, que eram as duas chaves que eu esperava. As duas eram texto
em 570 de 570, entao reconstrui a opcao como `{rotulo, valor}` e dei por
provado.

56 das 570 opcoes tambem carregam `grants`: as consequencias aninhadas, que sao
justamente o que faz escolher a opcao mudar numero na ficha. Reconstruir a opcao
apagava esse campo. Quatro fichas divergiram do gabarito.

A medicao certa era enumerar as COMBINACOES de chaves
(`Counter(tuple(sorted(op)))`), nao conferir o tipo das que eu ja tinha em
mente. A primeira responde "o que existe?"; a segunda so confirma a hipotese.

**Como aplicar:** ao tipar ou reconstruir um objeto vindo do dado, enumerar o
conjunto de chaves antes de escrever o tipo. E preferir REPASSAR o objeto a
reconstrui-lo campo a campo -- reconstruir e o que perde o que voce nao sabia
que existia. Quem pegou foi o teste de paridade contra o gabarito do Python;
`npm run build` e os 113 testes passavam.

## O payload do app envelhece calado quando o portao falha (2026-07-30)

`build.sh` roda com `set -euo pipefail` e o passo 8 e `portoes.py --fase final`
sem `|| true`. Portao vermelho **aborta o build**, e o passo 9 (`emitir_app.py`,
que escreve `base/app/`) nunca roda. Isso esta certo -- nao se publica payload de
uma base reprovada.

O que nao esta obvio e a consequencia: `base/app/` fica com o conteudo do build
ANTERIOR, e e ele que os 131 testes de paridade do TS consomem. Nesta sessao o
porte de `slots_concedidos` ficou vazio no TS e igual no Python, e a divergencia
apontava para um indice de `slots_abertos` -- o defeito parecia ser de ordenacao
da lista. Nao era: o `Versatile Human` do payload nao tinha o `choice` porque o
payload era de antes da mudanca no extrator.

Regra: **depois de qualquer build que tenha abortado nos portoes, rodar
`emitir_app.py` explicitamente antes de acreditar no resultado do vitest.**
Divergencia Python/TS em que o Python "sabe" algo que o TS ignora e sintoma
tipico de payload velho, nao de porte errado.

Quarta ocorrencia do mesmo padrao no mesmo dia (taticas_kits fora do laco,
magias.py no-op, saida/ancestrias.json de 27/07): artefato derivado que
sobrevive a mudanca da fonte porque ninguem o reescreveu.

## Fundir registro quebra ficha salva se o lookup nao seguir alias (2026-07-30)

`Base.resolver()` segue `aliases` desde 27/07 e existe justamente porque o
Remaster renomeia em massa. Mas `Base.opcional()` era `por_id.get()` cru, e e
ELE que o inventario, os atores e as escolhas usam.

Efeito: no dia em que a fusao aposenta um id, toda ficha salva que o cite perde
aquele item **em silencio** -- sem aviso, sem slot aberto, sem nada. O numero
simplesmente muda. Isso contradiz a promessa escrita no proprio `Personagem`:
"mudanca de regra re-deriva em vez de invalidar ficha salva".

Foi encontrado por acidente: fundi `cloak-of-elvenkind-greater` no canonico e o
fixture de validacao, que citava o id antigo, estourou com `KeyError: 'bonus'`.
Se o fixture nao existisse, a perda teria passado.

Regra: **todo caminho de lookup que recebe id vindo do DOCUMENTO do jogador tem
de resolver alias.** `por_id.get()` cru so vale para id que o proprio pipeline
acabou de produzir. E ao aposentar id em massa, o teste a rodar antes do commit
e "uma ficha que cita o id antigo continua igual?".

## Mexer em extrator sem `WB_REEXTRAIR=1` e um build verde sobre dado velho (2026-07-30)

`build.sh` PULA a etapa 1 (extratores) por padrao: so roda com
`WB_REEXTRAIR=1`. Faz sentido -- extrair das fontes e a parte cara --, mas cria
uma armadilha de sentido unico: editar `extratores/*.py` e rodar `build.sh` da
os 10 portoes VERDES, o oraculo verde e a paridade verde, e nada do que se
editou entrou. A base foi remontada a partir de `saida/*.json` antigo.

Aconteceu ao ampliar `ATOR_RE` para familiar: a base saiu identica, e a unica
pista foi eu ter conferido o registro em vez de acreditar no "todos passaram".

Regra: **mudou algo em `pipeline/extratores/`, o build e `WB_REEXTRAIR=1 bash
pipeline/build.sh`.** E a prova nunca e o placar dos portoes -- e ler o REGISTRO
que a mudanca deveria alterar. Mesma familia das saidas orfas ja registradas
aqui (`taticas_kits` fora do laco, `magias.py` no-op): artefato derivado que
sobrevive a mudanca da fonte porque ninguem o reescreveu.

## Verificacao no navegador roda contra `app/public/base`, que o build NAO atualiza (2026-07-30)

`pipeline/build.sh` escreve o payload em `pipeline/base/app/`. Quem copia para
`app/public/base/` -- que e o que o dev server serve -- e `app/sincronizar-base.sh`,
e **o build nao o chama**. Entao a quarta camada pode rodar contra uma base de
horas atras.

Aconteceu com o dano decomposto: o Python dava `+2 Rage` e a tela nao mostrava
parcela de furia nenhuma. Gastei a investigacao no motor TS -- conferi
`melhorGrau`, `idsDaFicha`, `verdadeiro(null)` -- e o codigo estava certo o
tempo todo: `app/public/base/por-kind/class-feature.json` tinha
`rage_damage: None` porque era o arquivo de antes do build.

Aqui a defasagem produziu FALSA FALHA, que e o lado seguro. Mas o lado
perigoso existe: campo REMOVIDO da base continua na tela, e a verificacao passa
por dado que nao existe mais.

Regra: **mexeu no payload (passo 9 do build), rodar `bash app/sincronizar-base.sh`
antes de qualquer `verificacao/*.mjs`.** E o sintoma que denuncia: motor Python e
TS discordando quando os dois arquivos de motor estao iguais -- a divergencia nao
esta no codigo, esta no dado que cada um leu. Mesma familia do `WB_REEXTRAIR`
logo acima: artefato derivado que sobrevive a mudanca da fonte.

## Ancora de edicao por TEXTO apaga o que esta entre duas ocorrencias (2026-07-31)

Editando `TODO.md` por script, usei como ancora
`t.index("- desc: 'RE-MEDIDO 2026-07-29, e o item mudou de gravidade")` achando
que era o item 97. Era o item **55**. O `replace` foi de la ate o `priority:`
seguinte ao `id: 97`, e **apagou os 8 itens que viviam no meio** -- 55, 68, 69,
84, 10, 31, 85 e 96.

Passou pelo commit e pelo push. Nao ha portao para isso: os 10 portoes olham a
BASE, e `TODO.md` nao e base. O que denunciou foi contar a fila no fim da
sessao e ver 7 onde eram 15.

Regra: **ancorar no marcador UNICO do proprio item (`  id: N\n`) e caminhar
para tras ate o `- desc:` dele**, nunca num trecho de prosa que outro item pode
compartilhar. E conferir a CONTAGEM antes e depois de toda edicao estrutural:

    grep -cE "^  id: |^- id: " TODO.md

Vale para qualquer arquivo de lista editado por script -- TODO, LOG, INDEX da
wiki. O texto de um item nao e chave primaria; o id e.

## `vitest` nao type-checa: o build do app ficou quebrado sem ninguem ver (2026-07-31)

Ao rodar `npm run build` pela primeira vez desde o item 43, o `tsc -b` acusou
`TS6133: 'nivel' is declared but its value is never read` em
`_ficha_de_eidolon`. O parametro entrou por simetria com `_ficha_de_familiar`
-- que USA o dele nas pericias -- e ficou vestigial nos dois motores: o eidolon
nao tem nivel proprio, usa o do personagem (`self.nivel` / `this.nivel`).

O ponto nao e o parametro, e **quanto tempo ele sobreviveu**. As 137 (hoje 140)
paridades passavam verdes o tempo todo, porque `vitest` roda o TypeScript via
transpile e **nao faz type-check**. Python nao reclama de parametro nao usado, e
por isso o gemeo nao denunciou. As quatro camadas estavam verdes com o app
inconstruivel.

Regra: **`npm run build` faz parte das camadas, ao lado do oraculo, da paridade
e do navegador.** Ele e a unica coisa no projeto que type-checa. E quando um
parametro sai de um motor, sai do outro no mesmo commit -- os gemeos so servem
de gabarito enquanto forem gemeos.

## Implementar o atomo antes de existir quem o avalie e codigo morto (2026-07-31)

O item 105 pedia `item:slug` no `_atomo_de_filtro`. Medido antes de escrever:
dos 79 usos, **77 nao passam por la**. Sessenta vivem em `grants/choice` de
`tipo: spell`, e `slots_concedidos` so coleta `tipo == "feat"` -- o filtro nunca
e consultado. E nem adiantaria coletar: a ficha modela CAPACIDADE de conjuracao
(slots, tradicao, DC) e nao QUAIS magias o personagem sabe, entao a escolha nao
teria onde pousar.

Sobraram dois, e esses eram numero errado na ficha -- mas por outro caminho
(`_arma_casa`, o remap de proficiencia), nao pelo que o item apontava.

Regra: antes de ensinar um vocabulario novo ao motor, **medir quem consome cada
ocorrencia**, uma a uma. "O motor ignora X" nao implica "implementar X muda
algo": pode nao haver ninguem do outro lado. E o mesmo erro de metodo do item
97, que contava citacoes sem perguntar por qual caminho o jogador chega.

## O motor abrir o slot nao significa que o jogador o veja (2026-07-31)

Generalizando o slot concedido, o oraculo, a paridade e as fixtures ficaram
verdes -- `slots_abertos` trazia o slot de magia, com nivel, flag e rotulo. No
navegador nao havia nada. `feat_concedido` **nunca foi renderizado pela UI**,
nem para feat: o motor abria o slot desde a spec de 30/07 e a tela nunca o
desenhou, entao quem pegava `Ancient Elf` nao era perguntado nada.

E a terceira vez na mesma semana: o slot de familiar (`em: null`, a UI so
desenha onde `em === n`) e a conjuracao (que existia so em `Ficha.tsx`, tela que
ninguem usa). O padrao e sempre o mesmo -- **o motor calcula, a tela nao le**, e
nenhuma camada abaixo do navegador enxerga isso, porque as tres testam o motor.

Regra: quando a mudanca acrescenta ALGO QUE O JOGADOR ESCOLHE, a verificacao de
navegador nao e a quarta camada, e a primeira pergunta -- "onde isso aparece na
tela?" antes de escrever o motor. Fixture verde com tela vazia e o modo de falha
mais caro do projeto, porque parece pronto.

## Atomo desconhecido conta como satisfeito, e isso se INVERTE sob `not` (2026-07-31)

`_casa_filtro` trata atomo que nao sabe avaliar como satisfeito -- certo pelo
principio zero, porque ALARGA o slot em vez de esvazia-lo. Sob `not`/`nor` a
mesma coercao vira o contrario: `Adopted Ancestry` filtra
`{"not": "item:slug:{actor|...ancestry.trait}"}`, referencia dinamica que o
motor nao resolve, e o `not` de "satisfeito" rejeitava as 50 ancestralidades. O
slot nascia VAZIO.

E o MESMO erro que apareceu no `tokens()` de `derivar_parcelas_de_dano.py`, onde
achatar `{"not": "target:caster"}` trocava o sinal do grau 13 do Superstition.
Duas vezes no mesmo mes, em codigos diferentes.

Regra: **default permissivo nao atravessa negacao.** Onde houver `not`/`nor`,
clausula composta so de desconhecido nao pode decidir nada -- pula, nao inverte.

## `and` nao existe no avaliador, e chave desconhecida vira NO-OP (2026-07-31)

Escrevi `{"and": [<requires que existia>, <termo novo>]}` em dois passos de
pipeline no mesmo dia. O avaliador conhece `all`, `any` e `not` -- **`and` nao**
--, e pelo default do principio zero chave desconhecida **passa**. O predicado
inteiro virou no-op: o campo gravado, o relatorio contando "3 gateados", e nada
sendo checado.

O que denunciou foi o absurdo do RESULTADO, nao o codigo: `masterful-obfuscation`
pede rank *master* e apareceu atendido por um personagem de nivel 2. Se o teste
tivesse so o caso positivo, teria passado verde.

Regra: **todo gate novo precisa de um caso NEGATIVO no oraculo** -- alguem que
nao atende, com o motivo esperado. O caso positivo sozinho nao distingue "gate
funcionando" de "gate desligado". E antes de envelopar predicado, conferir o
vocabulario de operadores que o motor realmente implementa.

## Consertar um caminho quebrado ACORDA os bugs que dormiam atras dele (2026-07-31)

`recuperar_mecanica_equipamento.py` lia `fontes: foundry=0 itens, aon=0 itens`
havia semanas -- caminho fixo `dados_brutos/foundry/` numa maquina cujo clone e
`foundry_repo/`, e nomes de dump do AoN que nao existem mais. Consertar os dois
caminhos foi certo e trouxe 53 armas de volta.

E ligou um bug **da fonte** que estava dormindo com a fonte desligada: o dump do
AoN traz `damage_type: ["Piercing"]` chumbado nas 11 armas de combinacao
`(Melee)`, contradizendo a propria string no MESMO documento --
`Gun Sword (Melee)` tem `damage: "1d8 S"` e `damage_type: ["Piercing"]` lado a
lado. O passo lia o campo estruturado e gravou `piercing` em arma cortante.

O saldo liquido foi positivo (53 armas certas contra 11 erradas), mas a troca
tem uma assimetria que importa: **`None` honesto virou valor errado plausivel**,
e valor errado plausivel nao levanta suspeita de ninguem. Um campo vazio alguem
vai investigar; `piercing` numa espada ninguem confere.

Duas regras que saem daqui:

1. Ao religar uma fonte que estava desligada, **conferir uma amostra do que ela
   passa a escrever** -- ela nunca foi exercitada nesse caminho.
2. Entre campo ESTRUTURADO e a STRING que o descreve, quando os dois vem da
   mesma fonte e discordam, **a string costuma estar certa**: ela e o que o
   editor humano escreveu, o campo e o que alguem derivou depois.

## Cobertura que conta REGISTRO nao ve perda de CAMPO (2026-07-31)

Os dez portoes passaram verdes enquanto 53 armas perdiam `damage` a cada
rebuild. Nenhum estava quebrado: o portao 4 conta registros por kind (as armas
continuavam existindo, so sem dano), o 8 cobre arquivo que sumiu do disco, o 10
cobre `grants_completos`. **O buraco tinha nome: nenhum portao contava campo.**

O portao 11 fecha isso, e a prova de que ele fecha e o par: tirando `damage` de
53 armas, o 11 falha (`weapon.damage: 986 -> 933`) e o 4, na mesma base, passa.

E "caiu?", nao "existe?" -- 102 registros seguem sem campo critico por razao
legitima (bomba com dano por formula), e portao que nasce vermelho e desligado
na primeira semana.

## O motor abre o slot e a tela nao desenha -- terceira vez (2026-07-31)

`feat_concedido` (item 106), `pericias_livres` e as fontes de boost. Nos tres, o
motor estava certo e completo, as fixtures passavam verdes, e o jogador
simplesmente nao era perguntado.

`pericias_livres` foi o pior: alem de a tela nao desenhar, `candidatos()` nem
conhecia o slot em nenhum dos dois motores -- caia no `else` final e devolveria
FEATS se alguem o tivesse desenhado. Ninguem tinha exercitado o caminho porque
ninguem chegava nele.

**O gabarito nao pega isso, por construcao**: ele congela a saida do motor, e a
saida do motor estava certa. So a quarta camada -- navegador -- ve o que o
jogador ve. Quando o motor ganhar um slot novo, a pergunta a fazer nao e "o
teste passa?", e "que tela desenha isto?".
