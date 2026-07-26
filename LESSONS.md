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

Recuperadas do PDF ate agora: Animist (War of Immortals p.12-13, hibrido
prepared divine + spontaneous pela apparition), Magus e Summoner (Secrets of
Magic). Exemplar e Kineticist foram **confirmados como nao-conjuradores** -- nao
havia tabela faltando.

### Trait no PF2e e vocabulario puro, nao mecanica
0 de 561 traits tem efeito estruturado. Os campos `resistance`/`weakness`/
`speed`/`skill_mod` do AoN vem vazios em 100% deles, e o Foundry
(`src/scripts/config/traits.ts`) e so dicionario slug->rotulo, sem rule element.
541/561 tem `trait_group`, que e taxonomia e nao mecanica.

Consequencia: nao adianta procurar efeito de trait em fonte nenhuma. Se o
construtor precisar de mecanica por trait, ela e nossa e tem de ser escrita.
