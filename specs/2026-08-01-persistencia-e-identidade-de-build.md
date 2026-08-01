---
spec: persistencia-e-identidade-de-build
req: WB-076
project: waybuilder
version: 2
status: implementada
created: 2026-08-01
issue: 1
---

# Spec -- persistencia da ficha e identidade de build

Fecha a issue #1 (ficha orfa) e os achados 6, 7 e 17 de
`docs/2026-08-01_avaliacao-arquitetura.md`. A avaliacao ja tinha juntado os
tres: *"sao tres sintomas do mesmo buraco -- nao existe identidade de build em
lugar nenhum"*.

O `localStorage` **e** o banco. Nao ha servidor, nao ha conta, nao ha
sincronizacao (`doc.ts:9-11`). Isso nao e limitacao a contornar: e a decisao do
projeto. O que esta spec faz e dar ao banco as duas colunas que ele nunca teve
-- **quem e esta ficha** e **sobre que base ela foi montada**.

## O defeito, medido

Quatro medicoes no codigo de hoje:

| # | Onde | O que acontece |
|---|---|---|
| 1 | `App.tsx:54` -- `const [id] = useState(() => doc.novoId())` | id **novo a cada mount**. Recarregar a pagina troca a identidade da ficha aberta. |
| 2 | `App.tsx:63-65` -- `useEffect(() => { if (d.escolhas.length) doc.salvar(id, d) }, [d, id])` | grava **sempre**, e **nunca le de volta**. Nao existe um unico `carregar` no app. |
| 3 | `doc.ts:229` (`listar`) e `doc.ts:254` (`apagar`) | `grep -rn "doc.listar\|doc.apagar" app/src` devolve **zero**. Codigo morto no app inteiro; `listar()` so e chamado de dentro de `salvar` e `apagar`. |
| 4 | `doc.ts:15` -- `waybuilder:personagens` | uma entrada nova por recarga-com-edicao, sem teto. |

O efeito composto: **a ficha do jogador nunca volta**, e a chave cresce ate a
cota.

Quanto cresce, medido sobre o exemplo da propria spec de schema
(`specs/2026-07-26-schema-personagem.md:42-88`, um nivel 3 com 13 escolhas):
**1.783 bytes minificados**; o array `escolhas` sozinho da 882 bytes, ou
**67,8 bytes por escolha** (882/13 -- a versao 1 desta spec dizia 68,8, que nao
reproduz), ~5,0 KB extrapolado para
nivel 20. Numa cota de 5 MB isso da ~2.900 entradas -- e metade disso
(~1.450) nos navegadores que contam `localStorage` em UTF-16. Nao e um estouro
imediato; e um vazamento silencioso que termina em `QuotaExceededError` num dia
qualquer, com a sessao inteira dentro.

Agrava: nada no repo mede esta chave. `grep -rn "waybuilder:personagens"` fora
de `doc.ts:15` da zero -- nenhum dos 16 `.mjs` de `app/verificacao/` a toca.

## O buraco maior: nao existe identidade de build

O tipo ja tem o campo. `app/src/motor/tipos.ts:56-57`:

```ts
esquema?: string;
base?: { versao?: string; pin_foundry?: string };
```

E a spec de schema ja o declarou no exemplo canonico
(`specs/2026-07-26-schema-personagem.md:44`):

```json
"base": { "versao": "2026-07-26", "pin_foundry": "87f9e502" }
```

Medido: **ninguem escreve `base`** -- `novoDocumento()` (`doc.ts:25-39`) nao o
emite, e nenhum `.ts`/`.tsx` o le. E **`esquema` e escrito e nunca lido**:
`doc.ts:27` grava `"waybuilder/personagem@1"`, e `grep -rn esquema app/src`
mostra so escritas. Duas colunas declaradas, zero em uso.

O mesmo buraco em outros dois lugares:

- `motor/gerar_fixtures.py:98` -- `"pin_base": base.get("wb:class/fighter").get("id") and "ok"`, que grava a **string literal** `"ok"` em `motor/fixtures/_indice.json:3`. O harness de paridade e cego a mudanca da base (achado 6).
- O payload nao carrega assinatura nenhuma. `app/public/base/_manifesto.json` tem `registros`, `kinds`, `gzip_indice_completo`, `gzip_indice_de_build`, `prosa_bytes_em_disco`, `campos_descartados`, `por_kind` -- e **nenhum hash** (`pipeline/emitir_app.py:104-113`). Hoje: 20.083 registros e 58 kinds; o proprio `_manifesto.json` ocupa **2.990 bytes em disco** (`wc -c`) -- e o tamanho do manifesto, nao do payload, que tem 1,19 MB so de indice gzip.

Sem assinatura, o achado 3 da avaliacao (`wb:feat/ki-cutting-sight` com
`requires` errado no ar) e invisivel para qualquer ficha salva: a base mudou
debaixo dela e o documento nao tem como saber.

---

## Decisao 1 -- a identidade da ficha

**O id nasce uma vez e mora DENTRO do documento**, em `doc.id`.

```json
{ "esquema": "waybuilder/personagem@2", "id": "pm7k2x9abc", ... }
```

Por que dentro do documento, e nao num indice separado:

- o documento e a unica fonte de verdade (`doc.ts:2-5`). Id que so existe no
  indice **nao sobrevive ao `exportar()`** (`doc.ts:266-280`, que serializa
  `doc` e mais nada), e reimportar o proprio backup criaria uma segunda ficha;
- o indice ja carrega `Salvo.id` (`doc.ts:19`). Ele deixa de ser identidade e
  passa a ser **espelho**, com a invariante `salvo.id === salvo.doc.id`.

Consequencia direta na API: `salvar(id, doc)` (`doc.ts:242`) vira
`salvar(doc)`. Passar o id por fora e exatamente o que permitiu ao `App.tsx:54`
inventar um id novo a cada mount.

**Varias fichas, nao uma.** O armazenamento sempre foi um array (`doc.ts:229`
devolve `Salvo[]`, `salvar` chaveia por id). Reduzir a uma ficha jogaria fora
codigo que funciona e contradiz o principio 4 -- e um jogador de PF2e tem mais
de um personagem. O que muda e que a lista finalmente **aparece**: `listar()` e
`apagar()` ganham chamador na tela.

**Qual ficha o app abre.** Precedencia, primeira que resolve ganha:

1. `location.hash` no formato `#/p/<id>`, se nomear uma entrada existente;
2. o ponteiro `waybuilder:ultima`, se nomear uma entrada existente;
3. a entrada de maior `atualizado` (unica pista que a bagunca legada tem);
4. nada: documento novo, id cunhado, **nao gravado ainda**.

Hash, e nao path: nao exige rota no `vercel.json` nem no service worker, e o
app continua estatico. Abrir uma ficha reescreve o hash -- entao cada ficha
ganha um endereco marcavel, e F5 numa aba especifica volta naquela ficha, nao
na ultima global.

O passo 4 e o que impede o defeito de voltar por outra porta: uma visita que
nao escolhe nada nao pode deixar entrada.

**Hash que nomeia ficha inexistente AVISA e cai no passo 4 -- nunca abre
outra.** Um bookmark de ficha apagada, ou levado para outra maquina, resolve o
passo 1 em falso. Deixar a precedencia escorrer para o passo 2 ou 3 abriria uma
ficha DIFERENTE com o endereco de outra, e o debounce gravaria por cima dela em
500 ms: e o cenario "abre a ficha errada e salva por cima", que e o defeito que
esta spec existe para fechar. Entao: aviso *"o endereco pede a ficha `<id>`, que
nao existe neste navegador"* mais documento novo (passo 4), que nao grava nada
enquanto o jogador nao editar.

## Decisao 2 -- retomada, e o lixo que ja esta la

**"A ultima" e um ponteiro explicito**, `waybuilder:ultima`, escrito ao ABRIR
uma ficha -- nao o maior `atualizado`.

Motivo: `atualizado` e resultado de uma gravacao. Usa-lo como "ultima aberta"
faz a resposta depender de efeito colateral -- um import que toca varias
entradas, um relogio errado, um autosave em outra aba movem o alvo. Ponteiro e
**decisao**; `atualizado` e **derivacao**. Principio 3.

**A retomada muda um habito, e o substituto e explicito.** Hoje `App.tsx:54`
cunha id novo a cada mount: recarregar a pagina E o unico jeito de comecar uma
ficha nova. Com a retomada, o mesmo F5 passa a REABRIR a ficha anterior -- e sem
um substituto o jogador que quisesse a segunda ficha acabaria editando a
primeira por cima. Entao o seletor da Decisao 2 tem tres acoes, nao duas:
**abrir**, **apagar** e **nova ficha**.

`nova ficha` = documento novo com id cunhado, `waybuilder:ultima` apagado e o
hash limpo. Ela **nao e gravada no clique**: segue a regra do passo 4, e so
entra na lista quando o jogador editar algo. Consequencia declarada: recarregar
antes da primeira edicao volta na ficha anterior, porque um rascunho intocado
nunca chegou ao disco. Gravar no clique seria a outra escolha possivel, e ela
transforma cada clique curioso em entrada morta -- exatamente o tipo de lixo que
esta spec esta limpando.

**Quando grava.** Hoje o efeito de `App.tsx:63-65` dispara a cada tecla do
campo de nome. Passa a: debounce de 500 ms, e nada e escrito se o documento
serializado for identico ao ultimo gravado.

**Com flush obrigatorio em `pagehide` e em `visibilitychange`/`hidden`.** Sem
ele o debounce e uma REGRESSAO contra o codigo de hoje, que grava a cada tecla:
fechar a aba dentro da janela de 500 ms perderia a ultima edicao. O flush grava
sincronamente o que estiver pendente. `pagehide` cobre fechar e navegar;
`visibilitychange` cobre o unico caminho de descarte do iOS, onde `pagehide`
pode nao chegar.

**O lixo das sessoes anteriores: MIGRA, LISTA, e nunca descarta sozinho.**

Principio 4 -- nada e descartado -- vale para a ficha do jogador antes de valer
para o conteudo da Paizo. Cada entrada acumulada e uma ficha real: o defeito
nao fabricava documentos vazios, ele duplicava documentos com pelo menos uma
escolha (`App.tsx:64` so grava com `d.escolhas.length`).

Entao:

- toda entrada e migrada na leitura (ver Decisao 5) e entra na lista;
- a tela ganha um seletor de fichas com `nome`, nivel derivado, `atualizado` e
  os 8 primeiros hex do pin da base. Ficha migrada tem `pin: null`: a coluna
  mostra `base nao registrada`, e nao um vazio que se le como bug;
- apagar e **ato do jogador, um por vez, com confirmacao**. Nenhum caminho de
  codigo chama `apagar()` sem clique.

**A migracao NAO tenta fundir duplicatas.** Vinte entradas podem ser vinte
sessoes do mesmo personagem ou vinte personagens; distinguir exigiria adivinhar
por similaridade de `escolhas`, e adivinhar e gravar resultado no lugar de
decisao. A fusao fica com o jogador, que sabe.

**Cota.** Sem despejo automatico. Quando `setItem` lancar `QuotaExceededError`,
o app: mantem a lista intacta em memoria e em disco, mostra o que aconteceu,
oferece `exportar()` da ficha aberta e abre o seletor para o jogador apagar o
que quiser. Perder ficha para caber e o unico desfecho que esta spec proibe. A
edicao que nao coube **continua na memoria e continua exportavel** -- a
gravacao falhou, a ficha aberta nao. O aviso de cota aparece **uma vez por
sessao**, e nao a cada tentativa de gravacao: com o debounce falhando de novo a
cada 500 ms, repetir viraria ruido que esconde o proprio aviso.

## Decisao 3 -- identidade de build

**O documento grava o pin do payload sob o qual foi editado.**

### O que e o pin

```
pin = sha256( canonico(_manifesto.json) ).hex[0..16]
canonico(x) = JSON com chaves ordenadas recursivamente, sem espaco
```

Fonte: `app/public/base/_manifesto.json`, o arquivo que `carregarNucleo()` ja
busca primeiro (`carregarBase.ts:73-78`). Ele muda quando o conteudo muda:
`por_kind[k].gzip_bytes` e `registros` sao funcao do payload, e o pipeline e
deterministico byte a byte (md5 `b3f4bce6` em duas execucoes completas, achado
"o que esta certo" #1 da avaliacao).

Duas consequencias que a implementacao nao pode inventar:

- **Nao exige mexer no `pipeline/`.** O pin e derivado no cliente, com
  `crypto.subtle.digest("SHA-256", ...)`, dentro de `carregarNucleo()`, que ja
  e `async`.
- **Se um dia o manifesto passar a trazer `hash` proprio, ele ganha.** Regra
  fixada agora para nao haver ambiguidade depois: se `_manifesto.json.hash`
  existir, `pin = hash` e `origem = "pipeline"`; senao o pin e derivado e
  `origem = "manifesto"`, e o campo `hash` fica fora do canonico.

**Quando `crypto.subtle` nao existe ou falha.** Ele so e exposto em *secure
context* -- `https:` ou `localhost`. Servido de `file://` ou de um `http:` de
rede local, `crypto.subtle` e `undefined`, e `digest()` pode rejeitar. Nesse
caso: `pin = null`, `origem = "indisponivel"`, e **nada mais muda** -- a base
carrega, a ficha abre, e o aviso de divergencia nao dispara (comparar contra
`null` seria afirmar divergencia que nao se mediu, o mesmo motivo do
`origem: "desconhecido"` da Decisao 5). O documento tambem nao carimba `pin`
naquela sessao: gravar `null` por cima de um pin real apagaria a unica
informacao boa que a ficha ja tinha.

Limite conhecido e aceito: uma mudanca de conteudo que preserve exatamente
`registros` e todos os `gzip_bytes` passa despercebida. Improvavel (o achado 3
da avaliacao -- 3 registros com `requires` diferente -- move bytes), e o
conserto e o `hash` no pipeline, que esta spec ja acomoda.

### O que entra no documento

```json
"base": {
  "pin": "9f3c1a70b2d4e5f6",
  "origem": "manifesto",
  "registros": 20083,
  "kinds": 58,
  "visto_em": "2026-08-01T18:20:04.000Z",
  "nascida_em_pin": "9f3c1a70b2d4e5f6"
}
```

- `pin` / `visto_em`: reescritos a cada gravacao. Dizem **sob que base a ficha
  foi editada pela ultima vez**.
- `nascida_em_pin`: escrito uma vez na criacao, **nunca sobrescrito**. Dizem
  sob que base ela foi montada.
- `registros` e `kinds`: redundantes com o pin, e de proposito -- sao o que um
  humano consegue ler num relatorio de bug sem ter o payload em maos.
- `versao` e `pin_foundry` continuam validos no tipo (`tipos.ts:57`) e
  reservados para o pin da fonte (`dump_aon.py:149` grava um `_pin` de data que
  ainda nao chega aqui). Esta spec nao os preenche.

### O que acontece quando o pin diverge

**AVISA, nunca recusa.** Principio 1. Em concreto, ao carregar uma ficha cujo
`base.pin` difere do pin atual:

1. a ficha abre **inteira**. O motor re-deriva de `escolhas` como sempre --
   principio 3: regra que muda **re-deriva**, nao invalida;
2. um aviso nao-bloqueante no topo: *"esta ficha foi editada sobre outra base
   (`9f3c1a70`, 20.083 registros); a atual e `e21b8c44`, 20.089. A ficha foi
   re-derivada."*;
3. **nada e removido de `escolhas`, `atores` ou `inventario`.** Um id que a
   base atual nao resolve (`base.opcional()` devolvendo `null`) fica no
   documento e aparece no slot marcado como `id desconhecido nesta base:
   wb:feat/x`. Se uma base futura o trouxer de volta, ele volta a resolver
   sozinho -- que e a diferenca inteira entre re-derivar e invalidar;
4. na proxima gravacao, `base.pin` passa a ser o atual e o aviso do item 2 para
   de aparecer. `nascida_em_pin` nao muda.

Os avisos 2 e 3 sao **de naturezas diferentes, e por isso tem vidas
diferentes**: o do pin e um registro de decisao (dispara uma vez por troca de
base, e cala); o dos ids nao resolvidos e derivado da base a cada carga (e
persiste enquanto os ids nao resolverem). Colar os dois faria o segundo sumir
junto com o primeiro, que e o sinal que o jogador realmente precisa.

## Decisao 4 -- versao de schema

`doc.esquema` ja existe (`doc.ts:16`) e ja e escrito; passa a ser **lido**.

- Formato mantido: `waybuilder/personagem@N`, `N` inteiro.
- Esta spec leva a `@2`. O que `@2` adiciona sobre `@1`: `id` e `base`. Nada e
  removido nem renomeado.
- Na carga, `migrar(doc)` decide por `N`:

| `N` lido | O que faz |
|---|---|
| ausente ou ilegivel | trata como `@1` -- todo documento gravado ate hoje e `@1` por `doc.ts:16`, e um escrito a mao pode nao ter o campo |
| `< atual` | aplica a cadeia de migracoes, em ordem, cada passo puro `Documento -> Documento`, e carimba o `esquema` novo |
| `= atual` | segue |
| `> atual` | **abre assim mesmo**, com aviso. `specs/2026-07-26-schema-personagem.md:175-176` ja assumiu: *"Documento de versao futura tem que abrir numa versao velha do app."* |

Duas invariantes que sustentam a linha do `>`:

- **campo desconhecido e preservado literalmente** na gravacao. O
  `importar()` de hoje ja tem essa propriedade (`doc.ts:300`:
  `{ ...novoDocumento(), ...doc }` nao descarta chave extra) -- ela passa a ser
  contratual, nao acidental;
- **toda migracao e idempotente e so adiciona.** Rodar duas vezes da o mesmo
  resultado; nenhum passo apaga campo.

## Decisao 5 -- a ficha que ja esta salva hoje

Estado medido do que esta em disco agora: entradas `{id, nome, atualizado, doc}`
(`doc.ts:242-252`), com `doc.esquema === "waybuilder/personagem@1"`, **sem**
`doc.id` e **sem** `doc.base`.

Migracao `@1 -> @2`, por entrada, na leitura:

```
doc.id      ??= entrada.id          // ja unico e ja estavel em disco
doc.base    ??= { pin: null, origem: "desconhecido" }
doc.esquema  =  "waybuilder/personagem@2"
```

- `doc.id ??= entrada.id` e o ponto que faz a migracao ser barata: o id
  utilizavel **ja existe**, foi `novoId()` que o gerou (`doc.ts:260`), e so
  nunca esteve dentro do documento.
- `pin: null` com `origem: "desconhecido"` significa *"montada sob base nao
  registrada"*. Consequencia deliberada: o aviso de pin divergente **nao**
  dispara (nao ha com o que comparar -- afirmar divergencia seria inventar),
  mas o aviso de ids nao resolvidos dispara normalmente, porque ele e derivado
  da base e nao do pin.
- **A migracao acontece na leitura e so e persistida na proxima gravacao
  daquela ficha.** Migrar as N entradas de uma vez reescreveria a lista
  inteira; com a cota perto do limite -- o cenario que este defeito produz --
  essa unica escrita pode falhar e levar tudo junto.
- Nenhuma entrada e removida, renomeada ou fundida pela migracao.
- **Ficha migrada NUNCA ganha `nascida_em_pin`.** Ela nasceu sob uma base que
  ninguem registrou; preencher no primeiro save carimbaria como "nascida" a base
  de HOJE, que e uma afirmacao falsa inventada pela implementacao. O campo entra
  na migracao como `nascida_em_pin: null` -- presente e nulo, para que o
  carimbo posterior (que so preenche o campo AUSENTE) nao o toque nunca.

### Os tres casos que a migracao tem de nomear

**1. Entrada malformada dentro do array: preserva e pula.** `doc` ausente,
`null` ou nao-objeto faz `doc.id ??= entrada.id` lancar `TypeError` e derrubar a
carga inteira -- uma entrada podre levaria todas as outras. A regra: entrada que
nao tem `doc` objeto **nao e migrada, nao e listada e nao e descartada**. Ela
volta ao disco byte-identica na proxima gravacao, junto com as boas. Principio
4: nao entender nao autoriza jogar fora.

**2. `doc.id` presente e diferente de `entrada.id`: o documento ganha.** Um
backup editado a mao, ou um export `@2` reimportado por fora, chega com id
proprio. O documento e a fonte de verdade (`doc.ts:2-5`) e o indice e espelho
(Decisao 1), entao `entrada.id` e corrigido para `doc.id` na proxima gravacao.

Com **uma excecao, que existe para nao criar duas fichas com o mesmo id**: se
aquele `doc.id` ja pertence a uma entrada ANTERIOR da lista, quem chegou depois
mantem o proprio `entrada.id` e e o `doc.id` que passa a espelha-lo. A ordem do
array decide, e por isso a resolucao e deterministica: a mesma lista lida duas
vezes da o mesmo resultado, sem cunhar id aleatorio no meio de uma leitura. Se
nem `entrada.id` estiver livre (lista ja duplicada por fora), o desempate e
`<entrada.id>#<indice>` -- unico porque o indice e unico.

Em todos os ramos vale a invariante da Decisao 1: `salvo.id === salvo.doc.id`
na lista devolvida por `listar()`.

**3. A chave inteira ilegivel: preserva os bytes crus ANTES de qualquer
`setItem`.** `listar()` (`doc.ts:229-240`) devolve `[]` quando o JSON nao
parseia -- e a proxima gravacao (`doc.ts:250`) escreveria uma lista de UM
elemento por cima, destruindo tudo o que estava la. E o unico caminho de perda
total silenciosa que sobrou, e ele contradiz frontalmente o "perder ficha e o
unico desfecho proibido" da Decisao 2.

Entao, antes do primeiro `setItem` que substituiria a chave: copiar o conteudo
cru para `waybuilder:personagens:corrompido-<ISO>` e so entao gravar. Se essa
copia falhar (a cota tambem pode estourar aqui), **a gravacao nao acontece** e o
jogador recebe o aviso de cota -- perder a chance de gravar e recuperavel,
sobrescrever o que nao se conseguiu copiar nao e. O prefixo com timestamp
permite mais de um resgate sem um sobrescrever o outro.

## Forma final do documento

Diferenca sobre `specs/2026-07-26-schema-personagem.md`, so o que muda:

```json
{
  "esquema": "waybuilder/personagem@2",
  "id": "pm7k2x9abc",
  "base": {
    "pin": "9f3c1a70b2d4e5f6",
    "origem": "manifesto",
    "registros": 20083,
    "kinds": 58,
    "visto_em": "2026-08-01T18:20:04.000Z",
    "nascida_em_pin": "9f3c1a70b2d4e5f6"
  },
  "identidade": { "nome": "...", "jogador": "", "notas": "" },
  "escolhas": [ ... ],
  "atores": [ ... ],
  "inventario": [ ... ],
  "manual": { ... }
}
```

`identidade` continua sendo **o que o jogador escreve**; `id` e `base` sao
cunhados pela maquina e ficam fora dele de proposito.

Chaves de `localStorage`:

| Chave | Conteudo |
|---|---|
| `waybuilder:personagens` | a lista `Salvo[]` -- **mesma chave de hoje** (`doc.ts:15`), senao a migracao nao acha o que migrar |
| `waybuilder:ultima` | o `id` da ultima ficha ABERTA |
| `waybuilder:personagens:corrompido-<ISO>` | os bytes crus de uma lista ilegivel, copiados antes de a chave ser substituida (Decisao 5, caso 3). O app nunca le esta chave: ela existe para o resgate manual |

## Export e import

`exportar()` (`doc.ts:266`) passa a levar `id` e `base` junto, porque eles sao
do documento. `importar()` (`doc.ts:286`) decide por tres casos, sem outros:

| `lido.id` | O que faz |
|---|---|
| ausente | cunha um id novo |
| presente e desconhecido localmente | mantem o id do arquivo |
| presente e ja existe localmente | cunha um id novo e avisa *"esta ficha ja existia; entrou como copia"* |

O terceiro caso e o unico que tem escolha real, e a escolha e **nunca
sobrescrever**: importar o proprio backup por cima de uma ficha editada
depois seria descartar trabalho sem perguntar.

---

## O que esta spec NAO resolve, e declara

1. **Nao ha sincronizacao entre maquinas.** `exportar()`/`importar()` continuam
   sendo o unico caminho. Sem backend e decisao, nao pendencia (`doc.ts:9-11`).
2. **Nao ha politica de cota alem de avisar e oferecer export.** Sem despejo
   LRU, sem compressao, sem migracao para IndexedDB. Se a cota apertar de
   verdade, e outra spec.
3. **Nao dedupe o lixo legado.** A fusao de entradas quase-iguais fica com o
   jogador (Decisao 2).
4. **Nao toca em `pipeline/`.** O `hash` no `_manifesto.json` -- que tornaria o
   pin autoritativo em vez de derivado -- e spec propria. Esta aqui so fixa a
   regra de precedencia para quando ele chegar.
5. **Nao conserta o achado 6 no harness Python.** `motor/gerar_fixtures.py:98`
   continua gravando `pin_base: "ok"`. Esta spec define QUAL pin ele deveria
   gravar; trocar o harness e outro trabalho.
6. **Nao conserta o achado 17 (validacao de forma do payload).** Campo
   renomeado no payload continua virando ficha vazia em vez de erro. O pin
   detecta que a base MUDOU, nao que ela esta MALFORMADA.
7. **Nao trata duas abas.** Nem na mesma ficha, nem em fichas diferentes.
   Ultima gravacao vence; sem `storage` event, sem lock. Na mesma ficha isso e
   so a edicao mais nova ganhando. Em fichas DIFERENTES ha um caso pior e
   declarado: `salvar()` reescreve a lista INTEIRA (`doc.ts:242-251`), entao um
   save debounced da aba B, disparado com a lista que B leu antes, **ressuscita
   a ficha que a aba A acabou de apagar** -- e ha a corrida `listar`/`setItem`
   entre as duas, de janela curta mas real. O desfecho e sempre ficha a mais,
   nunca ficha a menos, que e o lado certo de errar pelo principio 4.
8. **Nao ha desfazer nem historico de edicao.** O documento guarda o estado
   atual das escolhas, nao a sequencia delas.
9. **Nao ha migracao `@2 -> @3`.** A cadeia existe com um elo so; o segundo
   nasce quando houver um `@3`.
10. **Nao muda o formato de export Pathbuilder.** `id` e `base` sao do
    documento proprio e nao tem equivalente la.

## Como se prova que funciona

Falseavel, em `app/src/persistencia.test.ts` (vitest, com um `localStorage`
falso em memoria -- o mesmo contrato sincrono do navegador, e o unico jeito de
esgotar cota e corromper chave sem depender de um browser real). Cada item
nomeia o que o derrubaria.

1. **F5 volta na mesma ficha.** Escolher uma ancestralidade, ler `doc.id`,
   recarregar: `doc.id` identico e `escolhas.length` identico.
   *Falseia:* qualquer id diferente depois do reload.
2. **Uma ficha, uma entrada.** 50 ciclos de editar + recarregar na mesma ficha:
   `JSON.parse(localStorage["waybuilder:personagens"]).length === 1`.
   *Falseia:* qualquer contagem > 1. Hoje o mesmo roteiro da 50.
3. **Visita ociosa nao grava.** Carregar e recarregar 5 vezes sem escolher
   nada: a chave continua ausente (ou com o mesmo tamanho de antes).
   *Falseia:* a chave aparecer.
4. **`novoId()` sai do `App.tsx`.** `grep -n "novoId" app/src/App.tsx` devolve
   zero; o id vem do documento carregado.
   *Falseia:* qualquer ocorrencia.
5. **`listar()` e `apagar()` tem chamador.** Medido por identificador, nao por
   `doc.listar`: `import { listar } from "./doc"` e implementacao correta que um
   grep de `doc.listar` reprovaria. O teste procura `\blistar\s*\(` e
   `\bapagar\s*\(` nos `.ts`/`.tsx` de `app/src` FORA de `doc.ts`, e exige >= 1
   de cada. Hoje: zero e zero.
   *Falseia:* zero em qualquer um dos dois.
6. **Nenhum `apagar()` sem clique.** Todo call site de `apagar` esta dentro de
   um handler com confirmacao.
   *Falseia:* uma chamada em `useEffect`, em migracao ou em tratamento de cota.
7. **Migracao legada preserva tudo.** Semear a chave com 7 entradas na forma
   antiga (sem `doc.id`, sem `doc.base`), carregar: as 7 continuam listadas, e
   cada uma tem `doc.id === entrada.id` e `escolhas` byte-identico ao semeado.
   Medido **em memoria**, na saida de `listar()` -- a migracao e lazy por
   projeto (Decisao 5) e em DISCO as entradas seguem antigas ate a proxima
   gravacao. Mais uma segunda medicao que fecha o buraco: gravar UMA das sete e
   reler o disco -- aquela entrada tem `id === doc.id` e as outras seis
   continuam la, intactas.
   *Falseia:* 6 entradas, `escolhas` alterado, ou a gravacao de uma entrada
   mexendo nas outras.
7b. **Entrada malformada nao derruba nem some.** Semear 3 entradas boas mais uma
   com `doc: null`: `listar()` devolve as 3 sem lancar, e depois de gravar uma
   delas a entrada podre continua no disco byte-identica.
   *Falseia:* excecao na carga, ou a entrada podre sumindo do disco.
7c. **Chave ilegivel nao e destruida.** Semear `waybuilder:personagens` com
   `"{lixo"`, gravar uma ficha: existe uma chave
   `waybuilder:personagens:corrompido-*` com os bytes originais, e a lista nova
   tem a ficha gravada.
   *Falseia:* os bytes originais nao aparecerem em lugar nenhum.
8. **Pin divergente avisa e nao recusa.** Semear uma ficha com 13 escolhas e
   `base.pin = "0000000000000000"`, carregar: o aviso existe no DOM **e** as 13
   escolhas estao na tela e no documento.
   *Falseia:* tela de erro, `escolhas` vazio, retorno antecipado, ou aviso
   ausente.
9. **Id nao resolvido sobrevive ao ciclo de gravacao.** Injetar
   `wb:feat/inexistente-nesta-base` em `escolhas`, carregar, editar outra
   coisa, recarregar: o id continua em `doc.escolhas` e aparece marcado no
   slot.
   *Falseia:* o id sumir do documento, ou a ficha nao abrir.
10. **Schema futuro abre, e nao e rebaixado.** Semear
    `esquema: "waybuilder/personagem@99"` com um campo extra `bugiganga`,
    carregar, salvar, reler: abre com aviso, `bugiganga` volta identico **e o
    `esquema` relido continua `@99`**. Sem esta ultima assercao, uma
    implementacao que rebaixa o documento para `@2` passaria no criterio
    inteiro -- a bugiganga voltaria pelo spread e o aviso ja teria aparecido --
    enquanto destruia a informacao de que aquele documento veio do futuro.
    *Falseia:* recusa de carga, `bugiganga` ausente, ou `esquema` != `@99`.
11. **Migracao idempotente.** Rodar `migrar()` duas vezes sobre o mesmo
    documento da resultado byte-identico.
    *Falseia:* qualquer diferenca.
12. **O pin e estavel e sensivel.** Medido sobre o MANIFESTO, com o `fetch`
    mockado -- e nao reemitindo a base: o pipeline nao e tocado por esta spec
    (limitacao 4), rodar `./build.sh` dentro de uma verificacao e impraticavel,
    e a limitacao ja admitida (mudanca que preserve todos os `gzip_bytes` passa
    despercebida) faria uma reemissao legitimamente NAO mudar o pin, reprovando
    codigo correto. Entao: duas derivacoes do mesmo manifesto dao o mesmo pin;
    mudar um `por_kind[k].gzip_bytes` ou `registros` muda o pin; reordenar as
    chaves do manifesto NAO muda o pin (e o que o canonico existe para
    garantir); manifesto com `hash` proprio devolve aquele hash e
    `origem: "pipeline"`.
    *Falseia:* pin instavel entre derivacoes, pin igual apos mudanca de
    conteudo, ou pin diferente so por ordem de chave.
13. **Cota nao come ficha, e a edicao continua exportavel.** Encher
    `localStorage` ate estourar e disparar uma gravacao: a lista em disco
    continua com todas as entradas, a mensagem de cota aparece, **e o documento
    devolvido pelo app ainda contem a edicao que nao coube** -- o que
    `exportar()` serializaria. Sem esta ultima parte, uma implementacao que
    descarta a edicao em memoria ao falhar a gravacao passaria: a lista em disco
    estaria intacta justamente porque o trabalho foi jogado fora.
    *Falseia:* qualquer entrada a menos, ou a edicao pendente sumindo da
    memoria.
14. **A chave passa a ser medida.** `grep -rn "waybuilder:personagens"
    app/verificacao app/src/fluxo.test.ts` devolve >= 1. Hoje: zero.
    *Falseia:* zero.
15. **Paridade Python/TS intacta.** As 33 fixtures e os testes do porte
    continuam verdes -- esta spec nao toca no motor.
    *Falseia:* qualquer divergencia nova.
16. **Existe caminho para a segunda ficha.** Com uma ficha ja gravada, a acao
    `nova ficha` devolve documento com `id` diferente e `escolhas` vazio, e o
    ponteiro `waybuilder:ultima` sai do caminho; editar e gravar essa segunda
    ficha deixa a chave com DUAS entradas, e a primeira intacta.
    *Falseia:* a segunda edicao caindo sobre a primeira entrada, ou a lista
    continuar com uma so.
17. **Hash desconhecido nao abre outra ficha.** Com uma ficha `A` gravada, abrir
    com `#/p/naoexiste`: o aviso existe, e o documento devolvido nao e `A` (id
    novo, `escolhas` vazio).
    *Falseia:* abrir `A` em silencio.
18. **Sem `crypto.subtle` o app nao quebra.** Derivar o pin com o `subtle`
    ausente devolve `pin: null` e `origem: "indisponivel"`, sem lancar; e a
    gravacao seguinte nao apaga o `base.pin` que a ficha ja tinha.
    *Falseia:* excecao, ou `pin` real virando `null` no documento.
