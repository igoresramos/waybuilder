---
spec: remover-kingmaker
project: waybuilder
version: 2
status: aprovada
created: 2026-08-01
todo: 2
decidido_por: Igor (2026-08-01)
revisao: adversarial (2026-08-01) -- 4 mudancas obrigatorias incorporadas
         (re-build apos aceitar a queda; fragmento derivado do censo e nao de
         xref.aon; commit do estado pre-mudanca como baseline; chave real do
         store de texto), mais a correcao de `exploration` (85, nao 88)
---

# Spec -- remocao do conteudo de Kingmaker

## O pedido, literal

> "todo conteudo de Kingmaker sai -- Kingdom Feats, backgrounds, skill feats,
> acampamento, ficha de reino, assentamento, exercito e as skills. Nada e
> mantido: nao e compativel com a mesa dele."

Quem decidiu: **Igor, 2026-08-01**. Motivo: a mesa nao usa as regras de reino
de Kingmaker, e o conteudo delas polui a base do construtor de personagem.

Registro do defeito observavel, medido antes de escrever esta spec: **33 das 34
fixtures do motor** (`motor/fixtures/*.json`) carregam id de Kingmaker, **1.142
ocorrencias**, e o caminho e sempre o mesmo -- `candidatos` de slot de feat. Em
`motor/fixtures/guerreiro4-fa-lacuna-dedicacao.json` um Guerreiro 4 recebe
`wb:feat/kingdom-assurance`, `wb:feat/skill-training-kingdom` e
`wb:feat/quick-recovery-kingdom` como candidatos de `general_feat@1`. Nao e
hipotese: e o estado congelado do oraculo.

---

## 1. A excecao ao principio 4 -- escrita para durar

O principio 4 do `README.md:23` diz:

> **Nada e descartado.** Conteudo cortado pela Paizo (alinhamento, Legacy sem
> sucessor) fica na base. Renomeado vira um registro so, com os dois nomes.

**Esta spec abre a primeira e unica excecao a ele.** O texto abaixo e a versao
para durar; qualquer agente futuro que ache 125 registros faltando na base deve
ler isto ANTES de "consertar" a remocao.

### Por que este conteudo sai

O principio 4 protege contra **perda por acidente de pipeline**: fusao que
apaga sucessor, extrator que casa por nome e descarta N-1 candidatos, saida em
disco que envelhece. Todos os precedentes do repo sao isso -- os 586 registros
recuperados da fusao por prosa, as 20 herancas legadas de 30/07, a tabela de
conjuracao do Animist. Em nenhum deles alguem *quis* perder o dado.

Aqui o dono do projeto quer. A regra de reino de Kingmaker (`kingdom`,
`settlement`, `army`, `camping`) e um **sistema de jogo paralelo**, com pericias
proprias, ficha propria e feats que so operam sobre a ficha do reino. O
construtor nao monta ficha de reino e nao vai montar. Manter o conteudo nao
custa disco -- custa **candidato falso em slot de escolha**, que e o defeito
medido acima.

### Por que isto NAO abre precedente

A excecao vale sob **tres condicoes cumulativas**, e so sob elas:

1. **O dono do projeto pediu nominalmente**, por escrito, identificando o
   conteudo pelo nome. Nao vale inferencia ("isto parece pouco usado").
2. **O conteudo e um subsistema de jogo fechado**, com vocabulario proprio que
   nao intersecta o resto -- medido, nao suposto. A prova esta na secao 4:
   **zero** registro que fica cita qualquer id removido.
3. **A remocao e um passo nomeado do `build.sh`**, reversivel apagando uma
   linha, com relatorio nominal a cada build.

Falhando qualquer uma das tres, o principio 4 vale integral. Em particular:

- **conteudo legado / cortado pela Paizo continua ficando.** `triagem_legado.py`
  e `artefatos_perdidos.json` existem exatamente para isso e nao mudam.
- **conteudo raro, de Adventure Path, ou "que ninguem usa" continua ficando.**
  A base tem 166 registros de Shining Kingdoms, 24 de *King of the Mountain*, 16
  de *Crown of the Kobold King*. Nada disso e alcancado por esta spec, e a
  semelhanca de nome com "Kingmaker" e coincidencia de grafia -- ver a secao 3.
- **"nao e compativel com a minha mesa" nao e criterio reutilizavel por
  agente.** So o Igor pode dizer isso, e so por escrito.

### Onde mais isto tem de estar registrado

Alterar o `README.md` no mesmo commit do codigo, acrescentando ao principio 4:

> Uma excecao, e uma so: o conteudo de Kingmaker sai, por decisao do Igor em
> 2026-08-01 -- ver `specs/2026-08-01-remover-kingmaker.md`, que explica por que
> ela nao se estende a mais nada.

Sem essa linha o README contradiz o pipeline, e o proximo agente acredita no
README.

---

## 2. O criterio -- medido, nao suposto

A sugestao original (`docs/2026-08-01_prompt-correcao-13-itens.md`, frente 5,
armadilha 3) supunha dois conjuntos, por LIVRO e por TRAIT, "provavelmente a
uniao". **Medido contra `pipeline/base/index.json` (20.086 registros):**

| criterio | registros |
|---|---:|
| `source.book` e um dos tres livros de Kingmaker | **125** |
| algum registro carrega o trait `kingmaker` em `traits[]` | **0** |
| interseccao | 0 |
| so livro | 125 |
| so trait | 0 |
| **uniao** | **125** |

**O trait `kingmaker` nao existe.** Nao ha vocabulario `kingmaker` em nenhum dos
438 traits distintos da base. A leitura por trait mais generosa possivel --
"carrega algum dos 31 traits DEFINIDOS em livro de Kingmaker" -- devolve **19
registros** (17 com `kingdom`, 2 com `tech`), e os 19 estao **todos dentro dos
125**. A uniao nao acrescenta nada.

**Decisao: o criterio e por livro, sozinho.** Filtrar tambem por trait custaria
uma segunda regra que nunca dispara e daria a impressao falsa de cobrir um caso
que nao existe.

### O criterio exato

`source.book` pertence, apos normalizacao para minusculas e corte de espaco, ao
conjunto **fechado**:

```
"kingmaker adventure path"     -> 80 registros
"kingmaker companion guide"    -> 41 registros
"pathfinder kingmaker"         ->  4 registros
```

**Lista fechada, nao `"kingmaker" in book.lower()`.** Duas razoes:

1. A substring e uma mina. `Shining Kingdoms` (166 registros), *King of the
   Mountain* (24), `Ghost King's Rage` (14), `Sky King's Tomb Player's Guide`
   (6), `Crown of the Kobold King` (16) nao casam com `kingmaker` hoje -- mas
   um livro futuro chamado `Kingmaker Bestiary` casaria, e um chamado
   `Kingmaker: Companion Guide` (com dois pontos) **nao** casaria com a lista
   fechada. Os dois erros existem; a diferenca e que a lista fechada erra
   **alto** e a substring erra **em silencio**.
2. As tres strings sao a saida canonica de `reconciliar.py`, nao a grafia da
   fonte. `pipeline/canonico_livros.json` mapeia `kingmaker` ->
   `Pathfinder Kingmaker` (verbete de `fora_do_aon`),
   `kingmaker adventure path` -> `Kingmaker Adventure Path` e
   `kingmaker companion guide` -> `Kingmaker Companion Guide`. Isso amarra o
   passo a rodar **depois** da canonizacao -- ver secao 5.

### A guarda que torna a lista fechada segura

O passo tambem varre a base atras de `source.book` que **contenha** `kingmaker`
normalizado e **nao** esteja na lista fechada. Achando um: **aborta**, com o
nome do livro e a contagem. Nunca remove por conta propria e nunca ignora.

Mesmo desenho de `aplicar_curadoria.py` ("cada entrada declara o valor que
ESPERA achar: se a fonte consertar o dado, este passo falha alto em vez de
sobrescrever em silencio").

### Guarda de contagem

O passo declara `ESPERADO = 125` e **aborta em qualquer divergencia**, com o
diff nominal (ids que apareceram, ids que sumiram) no stderr. Divergencia
significa que alguma coisa a montante mudou -- re-extracao, fusao nova,
desmembramento novo -- e merece olho humano. Atualizar o numero e uma linha, em
dois lugares (script e esta spec), e o commit que atualiza carrega o motivo.

---

## 3. Os falsos positivos, nomeados

A pergunta era: a uniao pega registro que NAO e de Kingmaker? **Pega quatro, e
sao os quatro abaixo.** Nenhum outro.

| id | trait_group | o que e | uso na base |
|---|---|---|---:|
| `wb:trait/shapechanger` | `Monster` | trait de criatura, vocabulario nucleo do PF2e | 0 |
| `wb:trait/wild-hunt` | `Monster` | trait de familia de criatura | 0 |
| `wb:trait/weather` | `Hazard` | trait de perigo ambiental | 0 |
| `wb:trait/tech` | `Mechanics` | trait de item tecnologico | 2 |

Os quatro sao **vocabulario generico atribuido a Kingmaker pelo proprio AoN**:
o hardcover de Kingmaker reimprime o glossario de traits, e o dump do AoN
registra a pagina do hardcover (`Kingmaker Adventure Path` p. 385, 596, 616;
`Kingmaker Companion Guide` p. 123) como fonte unica. Verificado: **nenhum**
dos 125 nomes existe no dump do AoN, na mesma categoria, sob livro nao-Kingmaker
(0 de 125). Ou seja, o AoN nao tem uma segunda entrada de `Shapechanger` para
canonizar -- a atribuicao errada e da fonte, nao de `reconciliar.py`.

**Decisao: os quatro saem junto.** Tres razoes:

1. **Uso medido hoje: zero para tres deles.** Nenhum registro da base carrega
   `shapechanger`, `wild-hunt` ou `weather` em `traits[]`. Os 2 usos de `tech`
   sao `wb:weapon/mindrender-baton` e `wb:weapon/rod-of-razors`, **ambos de
   Kingmaker** e ambos removidos no mesmo ato. Nao ha orfa.
2. **Nada no pipeline depende deles.** `normalizacao_traits.json` e
   `aliases_referencias.json` nao os mencionam; `normalizar_traits.py` e
   `traits_uniao.py` nao consultam registros `kind: trait`.
3. Abrir uma allowlist de 4 excecoes dentro de uma excecao ao principio 4
   compra complexidade que hoje nao paga nada.

**A porta de volta, nomeada:** se algum dia entrar extrator de criatura ou de
perigo, `shapechanger`, `wild-hunt` e `weather` voltam a ser necessarios. O
caminho e re-emiti-los pela fonte real (Monster Core / GM Core), **nao**
desligar o passo de remocao. Este paragrafo existe para que a busca por
"onde foi parar o trait shapechanger" termine aqui.

### O que NAO e falso positivo, e ja foi conferido

- `wb:trait/city`, `wb:trait/metropolis`, `wb:trait/town`, `wb:trait/village`
  (GM Core) tem `trait_group: ["Settlement"]` e **ficam**. Sao tamanho de
  assentamento do nucleo, nao a ficha de assentamento de Kingmaker. O
  `trait_group` e rotulo de taxonomia, nao ponteiro para `wb:trait/settlement`.
- Todos os `trait_group` `Kingdom`, `Kingdom—Event`, `Kingdom—Settlement` e
  `Kingdom—Warfare` (27 traits) estao **dentro** dos 125. O criterio por livro
  nao deixa nenhum para tras.
- `wb:trait/exploration` (Player Core, 85 usos) e um registro **distinto** de
  `wb:skill/exploration` (Kingmaker). Colidem por nome, nao por id. O primeiro
  fica.

### O que sai e nao parece Kingdom -- declarado de proposito

Dos 125, **64 sao maquinaria de reino** (16 skills + 31 traits + 17 feats com o
trait `kingdom`) e **61 sao conteudo comum de personagem** publicado em livro
de Kingmaker:

| bloco | n | exemplos |
|---|---:|---|
| backgrounds | 7 | `Brevic Noble`, `Rostlander`, `Sword Scion` |
| feats sem trait `kingdom` | 14 | `Roll with It (Ranger)`, `Giant Slayer`, `Hamstringing Strike`, `Too Angry to Die` |
| equipment | 23 | runas `Energy-Absorbing`, `Giant-Killing`, `Hooked`; venenos `Feyfoul` |
| weapon | 6 | `Grisly Scythe`, `Mindrender Baton`, `Ovinrbaane` |
| spell | 10 | `Aqueous Blast`, `Inkshot`, `Word of Revision` |
| ritual | 1 | `Incarnate Ancestry` |

**Esses 61 sao conteudo jogavel normal e saem assim mesmo**, porque o pedido
foi "nada e mantido" e o criterio e o LIVRO. Esta tabela existe para que ninguem
olhe a runa `Giant-Killing` faltando e conclua que foi acidente.

---

## 4. Referencias orfas -- medido, e a resposta e nenhuma

A pergunta era se os 31 traits e as 16 skills sao citados por registro que fica,
e se a citacao some ou o citante sai junto. **Medicao, varredura recursiva de
todo valor string dos 19.961 registros que ficam:**

| medida | resultado |
|---|---:|
| ids de Kingmaker citados por registro que fica (`requires`, `grants`, `subclasses`, `aliases`, qualquer campo) | **0** |
| registros que ficam carregando algum dos 31 traits de Kingmaker em `traits[]` | **0** |
| registros que ficam com `aliases` apontando para nome de Kingmaker | **0** |
| portao 3 (`requires` citando id inexistente) apos a remocao | **0** (era 0) |
| portao 10 (cobertura de `grants_completos`) apos a remocao | **0** (era 0) |

**Decisao: nenhuma citacao precisa ser apagada e nenhum registro precisa sair
por arrasto.** O conjunto e fechado. Isto e a prova da condicao 2 da secao 1 --
"subsistema fechado, medido".

### Os tres casamentos por NOME que parecem orfa e nao sao

A varredura por nome/slug (mais frouxa que por id) devolve 12 casamentos.
**Todos falsos**, conferidos um a um:

1. `trait_group: ["Settlement"]` em `city`/`metropolis`/`town`/`village` -- e o
   rotulo do grupo, nao referencia. `wb:trait/settlement` esta em outro grupo
   (`Kingdom—Event`).
2. `area_of_concern` de 24 divindades (`magic`, `weather`, `leadership`,
   `warfare`, `agriculture`, `trade`, `intrigue`, `statecraft`, `defense`,
   `commerce`) -- vocabulario de prosa do dominio da divindade. Nunca foi
   ponteiro para `wb:skill/*`.
3. `traits: ["exploration"]` em **85 registros** (41 `feat`, 43 `action`, 1
   `spell`) -- e `wb:trait/exploration` do Player Core, registro distinto que
   fica. (A v1 desta spec dizia "88 feats"; recontado, sao 85 e nem todos sao
   feat.)

### Um efeito colateral que nao existe: as pericias da ficha

Suspeita natural: 16 skills a mais viram 16 linhas a mais na ficha. **Falso.**
`motor/motor.py:4331` pula todo `skill` com `lore: true`, e as 16 skills de
Kingmaker chegam da fonte com `lore: true` (defeito de dado independente, ver
`wb:skill/agriculture`). Hoje o motor emite 16 linhas de pericia, que e o numero
certo do PF2e. **A remocao nao muda a ficha nesse ponto** -- muda o payload
(`skill` cai de 33 para 17 registros) e limpa o defeito `lore: true` por
consequencia, sem conserta-lo.

Nao afirmar, no commit, que a remocao "conserta as pericias da ficha". Nao
conserta; nunca esteve quebrado.

---

## 5. Onde o passo entra no `build.sh`, e por que ali

**Posicao: passo novo `7h`, entre `7g` (`derivar_spellcasting_arquetipo.py`,
`build.sh:297`) e `8` (portoes fase final, `build.sh:303`).**

Esboco (o comentario que vale e o do `build.sh`, mais longo -- ele e o registro
que o proximo agente le):

```bash
echo "== 7h. remover o conteudo de Kingmaker =="
# Unica excecao ao principio 4 do README, decidida pelo Igor em 2026-08-01.
# Spec: specs/2026-08-01-remover-kingmaker.md -- leia antes de "consertar".
#
# TARDE de proposito, e a ordem tem tres amarras:
#  - DEPOIS de `reconciliar` (2): o criterio e `source.book` CANONIZADO, e quem
#    canoniza e ele, via canonico_livros.json. Antes disso a grafia e a da
#    fonte ("kingmaker", "km") e a lista fechada nao casa.
#  - DEPOIS de `desmembrar_colisoes` (4), `fundir_renomeados` (7) e
#    `fundir_duplicata_de_nome` (7c0): sao eles que cunham e aposentam id.
#    Remover antes muda a familia de homonimos e o conjunto de candidatos da
#    fusao -- `wb:feat/the-harder-they-fall` (Player Core) e
#    `wb:feat/roll-with-it` (Character Guide) tem o id que tem por causa dos
#    irmaos de Kingmaker que estavam no bloco. Tirar os irmaos antes pode
#    renomear o sobrevivente EM SILENCIO, e o diff sairia como "alterado",
#    indistinguivel de defeito.
#  - ANTES do portao 8 e do `emitir_app` (9): portao tem de medir a base que
#    de fato sai, e o payload do cliente e derivado da base auditada.
python3 remover_kingmaker.py
```

### Por que nao mais cedo

O argumento a favor de rodar cedo (logo apos `reconciliar`) seria economia: 20
passos de derivacao trabalhando sobre 125 registros a menos. **Nao paga.** Sao
0,6% da base, e o preco e o risco de id instavel descrito acima. Alem disso a
medicao da secao 4 mostra que nenhum passo de derivacao produz referencia a
Kingmaker -- rodar cedo nao evita nenhuma orfa, porque nao ha orfa.

A ordem ja mordeu duas vezes nesta sessao (`fundir_duplicata_de_nome` rodado a
mao sobre base ja normalizada; `aplicar_aliases_em_requires` em 4h3 antes da
fusao). Nos dois casos a causa foi a mesma: **passo que le id rodando antes de
quem cunha id.** A posicao 7h obedece a regra derivada disso.

### O que o passo obrigatoriamente faz

1. Le `base/index.json`, aplica o criterio da secao 2, aplica as duas guardas.
2. Remove os 125 registros de `base/index.json`.
3. **Remove as 125 entradas correspondentes de `base/text/*.json`.** Medido:
   os 125 tem `text` preenchido (125 de 125) e as entradas existem --
   `feat.json` 31, `trait.json` 31, `equipment.json` 23, `skill.json` 16,
   `spell.json` 10, `background.json` 7, `weapon.json` 6, `ritual.json` 1.
   `emitir_textos.py` roda no passo 5, muito antes; sem esta limpeza a prosa
   fica orfa no repo para sempre. **Nao ha portao que pegue isso** -- e por
   isso a trava da secao 8 mede o store de texto explicitamente.
4. Emite `base/relatorio_kingmaker.md`: os 125 nominalmente, por kind e por
   livro, com id e nome. Contagem sozinha nao prova nada -- 125 remocoes
   ERRADAS tambem batem 125.
5. Emite `base/_kingmaker_ausencias.json`: o fragmento pronto para o portao 9,
   descrito na secao 6. **Derivado do CENSO, nao de `xref.aon`.** Os dois
   conjuntos nao coincidem, medido: 4 dos 125 nao tem `xref.aon`
   (`wb:feat/roll-with-it-kingmaker`, `wb:feat/the-harder-they-fall-kingmaker`,
   `wb:equipment/basic-ingredient`, `wb:equipment/special-ingredient`) e, na
   outra ponta, 3 docs do AoN que nao sao `xref` de ninguem ficam descobertos
   quando o registro homonimo sai -- `equipment-1763-1558` (Energy-Absorbing),
   `equipment-1756-1553` (Giant-Killing) e `equipment-1750-1551` (Ring of the
   Tiger), graus de item que o portao cobria por NOME. Fragmento so com os
   xrefs deixaria esses 3 sem decisao e o portao 9 vermelho. A regra:
   rodar `portoes.censo_aon()` sobre a base ANTES e DEPOIS e emitir a
   **diferenca** -- a mesma lente do portao, nao uma segunda.
6. Nao toca em `requires`, `grants` nem `aliases` de ninguem. Medido na secao 4:
   nao ha o que reapontar. Se um dia houver, o passo tem de **abortar**, nao
   reapontar em silencio -- guarda: apos a remocao, contar orfas em `requires`;
   subiu, aborta.

---

## 6. Como a queda de cobertura e registrada

### O que cai, medido por simulacao dos portoes sobre a base sem os 125

| portao | antes | depois | e catraca? |
|---|---:|---:|---|
| 3 `requires` orfao | 0 | **0** | -- |
| **4** cobertura vs build anterior | 0 | **9** | sim |
| 6 traits disjunto | 0 | 0 | -- |
| 8 artefato citado | 0 | 0 | -- |
| **9** kind ausente vs censo do AoN | 0 | **7** | **NAO** |
| 10 cobertura de `grants_completos` | 0 | 0 | sim |
| **11** campo critico vs build anterior | 0 | **1** | sim |

**O portao 9 tambem cai, e isso nao estava previsto.** A frente 5 do prompt
falava so de 4 e 11. O 9 compara a base contra o censo do AoN e acusa
**7 categorias** com **122 ausencias sem decisao registrada** (`background` 7,
`equipment` 30, `feat` 29, `ritual` 1, `skill` 14, `spell` 10, `trait` 31 --
122 e nao 125 porque 3 nomes ainda casam por colisao com registro que fica).

Isto muda a operacao inteira, porque **o portao 9 nao e catraca**. Pela regra
operacional de `docs/2026-08-01_linha-de-base-de-cobertura-fusao-42.md`,
`--aceitar-queda` so pode ser usado quando os unicos vermelhos sao catracas (4,
10, 11) -- a flag zera o contador agregado (`pipeline/portoes.py:964`) e
perdoa qualquer portao. Rodar com o 9 vermelho gravaria a linha de base
perdoando um invariante.

### Detalhe do portao 4

| kind | linha de base | hoje | removidos | depois |
|---|---:|---:|---:|---:|
| `feat` | 6239 | 6241 | 31 | 6210 |
| `trait` | 551 | 551 | 31 | 520 |
| `equipment` | 6033 | 6034 | 23 | 6011 |
| `skill` | 33 | 33 | 16 | 17 |
| `spell` | 1638 | 1638 | 10 | 1628 |
| `background` | 521 | 521 | 7 | 514 |
| `weapon` | 1038 | 1038 | 6 | 1032 |
| `ritual` | 151 | 151 | 1 | 150 |
| **total** | **20083** | **20086** | **125** | **19961** |

**A base em disco ja esta 3 registros acima da linha de base** (feat +2,
equipment +1, de trabalho posterior a fixacao de 01/08). Consequencia: o portao
4 vai reportar `20083 -> 19961`, uma queda de **122**, nao de 125. Os numeros
so fecham em 125 se a linha de base for refixada a partir de um **build limpo**.
Nao aceitar a queda antes de conferir isso -- e exatamente a aritmetica que
provou, na fusao de 42, que "nenhum registro sumiu por outro motivo".

Portao 11: `weapon.damage` 985 -> 979, que sao as 6 armas removidas. Fecha sem
sobra.

### A sequencia obrigatoria, nesta ordem

```bash
# 0. COMMITAR o estado pre-mudanca (a base em disco esta 3 registros a frente
#    do HEAD -- ver o criterio 3 da secao 9). Sem isto o comparar_bases mistura
#    esta remocao com trabalho anterior nao commitado.
git add pipeline/base && git commit -m "chore(base): fixar estado pre-remocao de Kingmaker (20.086)"

# 1. build completo com o passo 7h novo.
#    ELE SAI != 0, e isso e esperado: `build.sh` tem `set -e` e o passo 8
#    (`portoes.py --fase final`) nao tem `|| true`. Com 4, 9 e 11 vermelhos o
#    script MORRE no passo 8 -- os passos 9 (`emitir_app.py`) e 10
#    (`comparar_bases.py`) NAO rodam, e `base/app/` fica com o payload velho,
#    ainda com os 125 registros dentro.
./pipeline/build.sh || echo "esperado: morreu no portao 8"

# 2. portoes SEM flag -- espera-se exatamente 4, 9 e 11 vermelhos
python3 pipeline/portoes.py --fase final

# 3. fundir POR UNIAO o fragmento em censo_ausencias.json (ver acima) e rodar
#    de novo: so 4 e 11 podem estar vermelhos aqui. Qualquer outro = pare.
python3 pipeline/portoes.py --fase final

# 4. so entao aceitar a queda
python3 pipeline/portoes.py --fase final --gravar-cobertura --aceitar-queda

# 5. conferir que a catraca voltou a servir
python3 pipeline/portoes.py --fase final     # portao 4 = 0, portao 11 = 0

# 6. RE-RODAR O BUILD INTEIRO, agora que os portoes passam.
#    Sem isto o payload do app e os passos 9/10 nunca aconteceram: o cliente
#    continuaria carregando os 125. Este e o build que vale.
./pipeline/build.sh

# 7. so depois do build limpo: fixtures e payload do app
python3 motor/gerar_fixtures.py
./app/sincronizar-base.sh
```

**O passo 3 nao e opcional e nao pode ser trocado de lugar com o 4.** Pular
direto para `--aceitar-queda` com o 9 vermelho e o modo de falha que o proprio
`portoes.py:964` documenta.

**O passo 6 nao e opcional.** O primeiro build morre antes de emitir o payload,
e "rodei o build, deu certo" seria falso: o que rodou foi meio build.

### O texto que vai em `censo_ausencias.json`

Nao e `censo_ausencias.json` que registra a queda de cobertura -- esse arquivo e
do **portao 9** (ausencia vs o censo do AoN). A queda do **portao 4/11** e
registrada no proprio `base/_cobertura.json`, refixado, mais um documento em
`docs/`. Sao dois registros diferentes e os dois sao obrigatorios.

**(a) `pipeline/censo_ausencias.json`** -- uma entrada por categoria do AoN
(`background`, `equipment`, `feat`, `ritual`, `skill`, `spell`, `trait`),
seguindo o formato ja usado por `action` e `heritage`. `ids_aceitos` recebe os
ids do AoN de **todos os 125**, nao so dos 122 que aparecem hoje -- e a mesma
razao que o verbete `action` registra 70 ids para 44 ausencias
(`nota_ids_aceitos`: "registrar so os 44 deixaria os outros 26 quebrando o build
no dia em que a colisao mudar"). Motivo, identico nas sete entradas:

> Conteudo de Kingmaker, removido do escopo do construtor por decisao do Igor em
> 2026-08-01. Nao e lacuna de extracao: os registros ENTRARAM na base e foram
> removidos de proposito pelo passo `pipeline/remover_kingmaker.py` (build.sh
> 7h). Sao 125 registros dos livros `Kingmaker Adventure Path`,
> `Kingmaker Companion Guide` e `Pathfinder Kingmaker` -- a maquinaria de reino
> (16 pericias de reino, 31 traits de reino/exercito/assentamento, 17 Kingdom
> Feats) e o conteudo comum publicado nos mesmos livros (7 backgrounds, 14
> feats, 23 equipamentos, 6 armas, 10 magias, 1 ritual). A mesa nao usa as
> regras de reino, e manter o conteudo produzia candidato falso em slot de
> escolha -- medido em 33 das 34 fixtures do motor. Esta e a UNICA excecao ao
> principio 4 do README ("nada e descartado") e ela nao se estende a mais nada:
> ver specs/2026-08-01-remover-kingmaker.md, secao 1.

Mais os campos do formato: `"quantos": <n da categoria>`,
`"spec": "specs/2026-08-01-remover-kingmaker.md"`, `"decisao"` com a frase
"repor exigiria desligar o passo 7h, nao re-extrair".

O passo 7h **emite** esse fragmento em `base/_kingmaker_ausencias.json`, pela
diferenca do censo antes/depois (secao 5, item 5) -- para nao digitar 125 ids a
mao e para nao errar os 3 docs de grau que so o nome cobria. A fusao no
`censo_ausencias.json` e feita uma vez, por gente, e o arquivo continua curado.

**A fusao e por UNIAO, nunca por substituicao.** Das 7 categorias do fragmento,
`feat` **ja existe** em `censo_ausencias.json` com 5 ids aceitos de outro
assunto (as class-features do TODO 55). Trocar o verbete inteiro pelo do
fragmento deixa essas 5 sem decisao e o portao 9 continua vermelho -- simulado:
`1 categoria sem decisao, 5 ids`. Com a uniao, portao 9 = **0**. O fragmento
marca a categoria em risco com o campo `_fundir`.

**(b) `docs/2026-08-01_linha-de-base-de-cobertura-kingmaker.md`** -- documento
irmao de `docs/2026-08-01_linha-de-base-de-cobertura-fusao-42.md`, mesma
estrutura: o que aconteceu, a tabela por kind, o estado dos portoes antes de
gravar (provando que so 4 e 11 estavam vermelhos), o comando exato rodado, e a
prova de que a linha de base ficou no numero novo.

---

## 7. O que muda fora do pipeline

| artefato | efeito | acao |
|---|---|---|
| `motor/fixtures/*.json` | 33 de 34 mudam (1.142 ocorrencias, todas em `candidatos`) | regerar com `python3 motor/gerar_fixtures.py`, no MESMO commit |
| `app/public/base/` | derivado, gitignored | `app/sincronizar-base.sh` |
| `base/app/index.json` + `por-kind/` | reescritos pelo passo 9 do build | nada |
| `motor/motor.py`, `app/src/motor/personagem.ts` | **nao mudam** | nenhuma logica cita Kingmaker; grep confirma zero ocorrencias em codigo |
| `pipeline/base/text/` | 125 entradas removidas pelo passo | e o proprio passo |

O motor nao e tocado. Esta e uma mudanca de **dado**, nao de regra -- pela regra
de trabalho do prompt de correcao ("defeito de dado vai direto"), so o pipeline
muda. As fixtures mudam porque sao gabarito da base, nao porque o motor mudou.

---

## 8. O que esta spec NAO resolve, e declara

- **`lore: true` nas 16 skills de reino e um defeito de dado que sai junto sem
  ser consertado.** Se algum dia entrar pericia de subsistema legitima, o
  defeito volta. Vira item de TODO proprio, nao entra aqui.
- **A flag `--aceitar-queda` continua perdoando qualquer portao.** O defeito
  esta documentado em `docs/2026-08-01_linha-de-base-de-cobertura-fusao-42.md`
  com correcao sugerida e nao aplicada; esta spec **depende** dele estar
  intacto e apenas obedece a regra operacional (rodar sem flag primeiro). Se
  alguem consertar a flag antes, a secao 6 fica mais simples, nao errada.
- **Nao remove nada de outro Adventure Path.** Shining Kingdoms (166),
  *King of the Mountain* (24), *Crown of the Kobold King* (16) e afins ficam,
  inclusive quando o nome contem "King".
- **Nao define politica de "remover conteudo por livro" em geral.** Nao existe
  arquivo de configuracao de livros excluidos e nao deve existir: um mecanismo
  generico convida ao uso, e o principio 4 e a regra.
- **Nao trata `kingdom-structure`**, ja em `FORA_DE_ESCOPO` do portao 9
  (`pipeline/portoes.py:635-641`) desde antes -- nunca entrou na base.
- **Nao decide o que fazer se a Paizo reimprimir algum desses 61 registros
  comuns em livro nao-Kingmaker.** Nesse dia o criterio por livro deixa de
  alcanca-lo e ele volta sozinho, o que provavelmente e o certo. Medido hoje:
  0 de 125 tem reimpressao fora de Kingmaker no dump do AoN.

---

## 9. Como se prova que funciona -- criterios falseaveis

Cada item abaixo tem um comando e um numero. Falhando qualquer um, a mudanca
nao esta pronta.

1. **A remocao aconteceu e e exatamente a esperada.**
   O **primeiro** `./pipeline/build.sh` sai `!= 0`, morrendo no passo 8 com os
   portoes 4, 9 e 11 vermelhos -- esperado, ver a sequencia da secao 6. O que
   tem de rodar ate o fim e o build do passo 6 daquela sequencia, depois de a
   linha de base ser refixada. Nele, `base/relatorio_kingmaker.md` lista
   **125** registros nominalmente, distribuidos `feat 31 | trait 31 |
   equipment 23 | skill 16 | spell 10 | background 7 | weapon 6 | ritual 1` e
   `Kingmaker Adventure Path 80 | Kingmaker Companion Guide 41 |
   Pathfinder Kingmaker 4`. Qualquer outro numero reprova.

2. **A base nao tem mais nada de Kingmaker, nem prosa orfa.**
   Teste novo `pipeline/testes/test_remover_kingmaker.py`, citando o item 2:
   - `index.json`: **0** registros com `source.book` normalizado contendo
     `kingmaker`;
   - `base/text/*.json`: a chave da prosa e `wb:text/{kind}/{slug}` (o valor do
     campo `text` do registro, **nao** o id). Asserir os dois lados: **125 de
     125** presentes na base ANTES da remocao (medido) e **0** presentes
     depois. So o lado "depois" passa com implementacao errada -- uma chave que
     nunca existiu tambem esta ausente;
   - `base/app/index.json`: **0** registros com esses livros.

3. **A remocao NAO alterou mais nada.**
   Exige **commit previo do estado pre-mudanca**: a base em disco esta em
   20.086 e o `HEAD` em 20.083 (feat +2, equipment +1, de trabalho anterior nao
   commitado). Sem esse commit, `comparar_bases.py HEAD` responde
   `NASCERAM: 3` e reprova uma implementacao correta. O baseline e o ref do
   passo 0 da secao 6. Contra ele, nas tres linhas que ele imprime
   (`comparar_bases.py:73-75`):
   `registros que SUMIRAM: 125`, `registros que NASCERAM: 0`,
   `registros ALTERADOS: 0`. Este e o criterio mais forte da spec -- e ele que
   prova que a posicao 7h nao mexeu em id de sobrevivente. "ALTERADOS > 0" ou
   "NASCERAM > 0" reprova ate que cada caso seja explicado: foi assim que os 3
   registros nascidos no rebuild expuseram o defeito de ordem do
   `fundir_duplicata_de_nome`.

4. **Nenhuma orfa nova.** `python3 pipeline/portoes.py --fase final`:
   portao 3 = **0**, portao 6 = **0**, portao 8 = **0**, portao 10 = **0**.

5. **Os unicos vermelhos sao catracas, antes de aceitar a queda.**
   Apos registrar `censo_ausencias.json`: portao 9 = **0**, e os vermelhos sao
   **exatamente {4, 11}**. Se o 9 continuar vermelho, a lista de `ids_aceitos`
   esta incompleta -- nao usar a flag.

6. **A linha de base ficou no numero novo.** Depois de
   `--gravar-cobertura --aceitar-queda`, uma reexecucao **sem flags** tem
   portao 4 = 0 e portao 11 = 0, e `base/_cobertura.json` diz
   `total: 19961`, `skill: 17`, `trait: 520`, `feat: 6210`, e
   `por_campo_critico.weapon.damage: 979`.

7. **O defeito relatado sumiu.** Apos `python3 motor/gerar_fixtures.py`, a
   busca pelos **125 ids** nas fixtures devolve **0 ocorrencias** (era 1.142,
   em 33 dos 34 arquivos). Em particular `wb:feat/kingdom-assurance`,
   `wb:feat/skill-training-kingdom` e `wb:feat/quick-recovery-kingdom` somem de
   `candidatos.general_feat@1` em `guerreiro4-fa-lacuna-dedicacao.json`.

   **Buscar pelos ids, nao pela palavra.** `grep -rl kingdom motor/fixtures/`
   nao serve como criterio: `wb:feat/my-kingdom-my-blood` (War of Immortals,
   p. 136) fica na base e pode virar candidato a qualquer momento. Medido hoje
   ele nao aparece em fixture nenhuma -- removendo os 125 ids do texto das
   fixtures, sobram **0** ocorrencias de "kingdom" --, mas isso e estado de
   hoje, nao invariante.

8. **O oraculo continua verde e ganhou trava.** `./verificar.sh` sem regressao
   nova, e `motor/teste_motor.py` com uma assercao nova citando o item 2:
   `base.opcional("wb:feat/kingdom-assurance") is None` e
   `base.opcional("wb:skill/agriculture") is None`. Esta assercao falha alto no
   dia em que alguem desligar o passo 7h -- que e o cenario contra o qual a
   secao 1 inteira foi escrita.

9. **O README nao contradiz mais o pipeline.** O principio 4 carrega a linha de
   excecao apontando para esta spec, no mesmo commit.
