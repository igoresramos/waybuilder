# Avaliacao de arquitetura -- Waybuilder

Data: 2026-08-01. Metodo: 4 avaliadores paralelos, um por eixo, com contrato
anti-slop em `docs/2026-08-01_prompt-avaliador-arquitetura.md` (ancora
obrigatoria, falsificacao obrigatoria, teto de 6 achados, cego declarado).
Sintese e priorizacao revisadas contra o codigo no fim da rodada.

---

## Veredito

A arquitetura de PRODUCAO esta sa. A arquitetura de VERIFICACAO esta quebrada,
e e a mesma causa nos quatro eixos.

O pipeline e deterministico byte a byte (duas execucoes completas, mesmo md5
`b3f4bce6`, 47 passos, 177 s). O motor tem paridade Python/TS real e medida (33
fixtures, 0 divergencias, 146 asserts TS verdes, 24 de 27 commits tocando os
dois lados juntos). A houserule esta de fato isolada -- `class_level` /
`character_level` aparecem zero vezes fora de `src/motor/`. O SDD funciona: 72
das 74 specs sao citadas por nome depois de escritas, e a revisao adversarial da
spec mais recente pegou um bug categorico antes de existir codigo.

O problema e que a verificacao cresceu por acrecao e nao tem dono. Existem SEIS
mecanismos de verificacao -- 11 portoes de pipeline, 132 assercoes do oraculo
Python, 95 testes `unittest`, 146 testes vitest, 16 scripts `.mjs` de navegador,
1 oraculo externo (`validar_iconics`) -- e **nenhum comando roda todos**. Nao ha
CI (`.github` nao existe), nao ha git hook (`.git/hooks` vazio de custom), o
`app/package.json` nao tem script `test`, e `build.sh` nao chama teste nenhum.

O efeito e o mesmo em cada eixo: cada mecanismo nasceu de um defeito real,
resolveu aquele defeito, e depois ficou orfao. Portao 8 nasceu de perda de
artefato real. Portao 11 nasceu de 53 armas perdendo `damage`. A quarta camada
de verificacao do app nasceu porque as tres primeiras passaram verdes sobre uma
base errada. E hoje: 31 dos 95 testes `unittest` estao vermelhos ha dias sem
que ninguem saiba se e bug ou apodrecimento; os portoes ficam verdes com 19.952
registros de prosa zerados; o pino de base do harness de paridade e a string
literal `"ok"`; os 16 `.mjs` com assert real nunca rodam.

Segunda leitura, transversal: a fronteira mais fragil nao esta entre modulos,
esta entre **build e artefato**. A base commitada nao e o que o pipeline
produz, o payload que o teste de paridade le e gitignored, e o `|| true` da
linha 40 do `build.sh` deixa a falha do construtor da base sair com exit 0. O
repositorio nao consegue responder "essa base saiu deste codigo?".

---

## Achados priorizados

Reordenados por risco/custo, nao por eixo. Origem: A=pipeline, B=motor,
C=app, D=specs.

| # | Achado | Sev | Conserto | Origem |
|---|---|---|---|---|
| 1 | `reconciliar.py \|\| true` -- falha do construtor da base sai com exit 0 | P0 | S | A4 |
| 2 | Portao 10 grava a propria linha de base ANTES de verificar | P0 | S | A3 |
| 3 | Base commitada != base que o pipeline produz (3 registros, 1 e pre-requisito errado no ar) | P0 | S | A1 |
| 4 | Os 11 portoes nao olham conteudo: prosa e mecanica podem evaporar e sair verde | P1 | M | A2 |
| 5 | 31 de 95 testes vermelhos, e nada os executa | P1 | M | B1 |
| 6 | Harness de paridade cego a mudanca da base (`pin_base` = `"ok"` literal) | P1 | S | B2 |
| 7 | Ficha salva sem versao: ID trocado degrada indistinguivel de "nunca escolhi" | P1 | M | C1 |
| 8 | Teste de paridade nao roda em clone limpo (payload gitignored) | P1 | S | B3 |
| 9 | Contrato de paridade cobre 5 de 15 tipos de slot, nenhum nivel acima de 10 | P1 | S | B4 |
| 10 | 16 scripts `app/verificacao/*.mjs` com assert real, nenhum executor | P1 | M | C3 |
| 11 | Numero do oraculo externo desatualizado; 65% de rank de pericia nao aparece em lugar nenhum | P2 | S | B5 |
| 12 | Proveniencia por campo cobre 9 de 124 campos; 23 campos preenchidos sem `prov` | P2 | S | A5 |
| 13 | 45 mutacoes in-place, 36 restricoes de ordem que so existem em comentario | P2 | M | A6 |
| 14 | Specs de dado nao ganham teste de regressao; specs de motor quase sempre ganham | P2 | M | D2 |
| 15 | Atribuicao por-registro afirmada no comentario, ausente no runtime | P2 | S | C2 |
| 16 | Drift documental: README parado em 27/07, PROJECT com 3 contagens de portao | P2 | S | D3/D4 |
| 17 | Payload sem validacao de forma: campo renomeado vira ficha vazia, nao erro | P2 | M | C4 |
| 18 | Statblock por especie (382 linhas x2) contradiz a spec de Ator | P2 | -- | B6 |

Resolvido durante a propria auditoria: a fusao de duplicata de nome rodava fora
do `build.sh` (achado D1) -- `grep` agora confirma a chamada presente.

---

## Os tres P0, com evidencia verificada na sintese

### 1. `reconciliar.py || true`

`pipeline/build.sh:40`:

```bash
python3 reconciliar.py || true      # portao 5 ainda falha em 3 registros orfaos
```

Unico `|| true` de um script com `set -euo pipefail`. `reconciliar.py` so grava
`index.json` na ultima linha (`reconciliar.py:360`) -- qualquer morte antes
disso deixa a base do build ANTERIOR intacta, e a cadeia segue mutando ela.
Medido, simulando os 45 passos seguintes sobre base ja construida: 24 registros
destruidos, 40 fabricados, 6.462 com conteudo diferente. Dos 11 portoes, so o 4
acusou.

O comentario mostra que a intencao era tolerar UM codigo de saida especifico. O
efeito e tolerar todos.

Conserto: `rc=$?; [ $rc -eq 0 ] || [ $rc -eq 5 ] || exit $rc`.

### 2. Portao 10 rebaixa a propria linha de base

`pipeline/portoes.py:811-814` -- dentro da funcao do portao, antes de qualquer
verificacao:

```python
if "--gravar-cobertura" in sys.argv:
    json.dump({"sem_resposta": hoje}, open(LINHA_DE_BASE, "w"))
    detalhe.append(f"linha de base GRAVADA em {hoje}")
    return 0, detalhe
```

A guarda que existe em `portoes.py:946-958` (com comentario explicito: "gravar
depois de falhar rebaixa a referencia e a regressao e acusada uma vez so")
protege `_cobertura.json`. Nao protege `_cobertura_grants.json`, que ja foi
reescrito dentro do portao. Medido: com 3 portoes vermelhos, o processo
imprimiu `linha de base NAO gravada` e o piso de grants foi de 0 para 300 no
mesmo run.

E o defeito que `docs/2026-07-27_duas-linhas-merge-pendente.md` registra como
consertado, reintroduzido num segundo arquivo de piso.

### 3. A base commitada nao e a que o pipeline produz

Rebuild da cadeia sobre os mesmos `saida/*.json`: mesmas 20.125 ids, zero
adicoes, zero remocoes, **3 registros com conteudo diferente**.

```
wb:feat/ki-cutting-sight -> requires
  disco : {"has": "wb:feat/qi-spells"}
  rebuild: {"has": "wb:spell/inner-upheaval"}
```

O extrator emite alvo de tipo `spell`; o rebuild resolve certo, o disco tem o
valor velho. O app serve hoje o pre-requisito errado. Nenhum relatorio em
`base/*.md` menciona o registro -- a troca aconteceu sem rastro.

`pipeline/comparar_bases.py` existe no repo, foi escrito exatamente para isso, e
`grep` confirma zero chamadas em `build.sh` ou em qualquer teste.

---

## O que esta certo, com evidencia

1. **Determinismo real, nao declarado.** Duas execucoes completas, `md5sum`
   identico (`b3f4bce625d49ef83204c2f8fde612ba`). A disciplina que sustenta
   isso e visivel: `traits_uniao.py:91`, `reconciliar.py:199`,
   `aplicar_subclasses.py:180-182` ordenam antes de gravar -- set nunca vaza
   para o disco.
2. **Paridade Python/TS medida, nao suposta.** 33 fixtures regeradas em memoria
   e comparadas com as commitadas: 0 divergencias. O comparador
   (`motor.test.ts:52,61-99,205`) trata `undefined` como chave ausente e exige
   os 14 extras presentes -- nao mascara `None`.
3. **Disciplina de porte sincronizado.** 24 dos 27 commits que tocaram
   `motor/motor.py` desde 30/07 tocaram `app/src/motor/` no MESMO commit; os 3
   restantes sao auto-saves alcancados pelo commit seguinte.
4. **A houserule nao vazou.** `class_level`/`character_level`: 6+5 em
   `motor.py`, 7+5 em `personagem.ts`, 1 em `predicado.ts`, **zero** em
   qualquer `.ts`/`.tsx` fora de `src/motor/`.
5. **Ausencia decidida e registro, nao silencio.** `artefatos_perdidos.json` e
   `censo_ausencias.json` fazem a ausencia aparecer no relatorio sem bloquear o
   build, e o portao 9 continua acusando o que NAO esta la (hoje: 44 `action`
   do AoN sem decisao registrada).
6. **Portao desligado nao conta como aprovado.** `portoes.py:923-931` devolve
   `None` com fonte ausente, o relatorio diz `NAO MEDIDO` e
   `--gravar-cobertura` se recusa a gravar. Reproduzido.
7. **SDD com trava real onde o mecanismo existe.** 25 das 74 specs tem
   assercao nomeada em `teste_motor.py`; a varredura da regra 21 e exaustiva
   (204 pares, nao amostra); `background-sem-beneficio` bate campo a campo com
   o exemplo da spec (`refugee-fop` com `con`/`int` e `Hunting Lore`).
8. **O app degrada com mensagem acionavel.** `carregarBase.ts:33-56` detecta
   HTML no lugar de JSON (sintoma de service worker velho) e devolve a
   instrucao de correcao, em vez do `Unexpected token '<'` cru.

---

## Juizo sobre dois achados, divergindo dos avaliadores

**Achado 18 (statblock por especie).** O avaliador tratou como divida de
duplicacao a ser reconciliada com a spec. Leitura alternativa: a SPEC e que
esta errada. "Ator e o mesmo motor com menos slots" e elegante no papel, mas
companion, familiar e eidolon do PF2e tem progressoes estruturalmente distintas
-- o eidolon usa as estatisticas do proprio Summoner, o companion tem maturidade
por feat, o familiar tem economia de acao propria. O Foundry chegou ao mesmo
lugar por conta propria, e a spec cita isso como defeito dele. Recomendacao:
corrigir a spec, nao refatorar 382 linhas que funcionam. Isto e juizo, nao
medicao.

**Achado 7 (versao da ficha).** Marcado P1 pelo avaliador com conserto M.
Concordo com a severidade, discordo do custo: gravar o hash do manifesto no
documento e compara-lo no carregamento resolve de uma vez este achado, o 6
(`pin_base` = `"ok"`) e metade do 17 (drift de forma do payload). Sao tres
sintomas do mesmo buraco -- nao existe identidade de build em lugar nenhum.
Fazer disso um conserto so muda a relacao custo/beneficio.

---

## Ordem de ataque recomendada

**Bloco 1 -- quatro consertos S que fecham a maior parte do risco (~1 sessao):**
1. `|| true` do `build.sh:40` vira tolerancia ao codigo especifico
2. Escrita de `_cobertura_grants.json` sai do portao e vai para o `main()`, sob
   a guarda que ja existe
3. `comparar_bases.py HEAD` entra como ultimo passo do `build.sh`
4. Identidade de build: hash do manifesto gravado em `_indice.json` das
   fixtures e no documento de personagem, verificado na carga

**Bloco 2 -- um comando de verificacao (~1 sessao):**
Um `verificar.sh` (ou `npm test`) que roda: `teste_motor.py`, `motor/testes/`,
vitest, `validar_iconics.py` com limiar, e os `.mjs` contra um dev server
efemero. Antes disso, triar os 31 vermelhos -- pelo menos 4 ja foram adjudicados
como teste apodrecido, nao bug (a regra 13 da spec contradiz
`test_class_feat_traz_a_classe_do_personagem`).

**Bloco 3 -- fechar o buraco conceitual (~2 sessoes):**
Estender a catraca do portao 11 de 3 campos para o conjunto de campos de
conteudo (`text`, `grants`, `requires`, `traits`, `level`), por kind. E a mesma
funcao `_contar_campo_critico` com a lista maior, e e o que impede prosa e
mecanica de evaporarem em verde.

**Nao urgente, mas barato:** atualizar README e fixar uma linha canonica de
numeros no topo do `## Estado atual` do PROJECT.md. O drift ja foi diagnosticado
em 31/07 e nao virou acao.

---

## Ressalvas desta avaliacao

- **O repositorio mudou durante a auditoria.** Uma sessao paralela rodou
  `rebuild.sh` e commitou entre 14:15 e 14:21: `index.json` foi de 20.125 para
  20.085 para 20.089 registros, e a spec `fusao-de-duplicata-de-nome` passou de
  v1 rascunho para v2 aprovada. Todas as medicoes dos eixos A, B e D estao
  ancoradas em snapshots congelados do HEAD daquele momento. Os tres P0 foram
  reverificados por mim no codigo ao final, depois dos commits.
- **A camada de extracao nao foi avaliada.** Tudo rodou com `WB_REEXTRAIR=0`,
  partindo de `pipeline/saida/*.json` ja em disco. Determinismo e idempotencia
  dos 11 extratores ficam sem medicao -- e e onde o projeto ja registrou tres
  defeitos.
- **Mudanca de pin de fonte nao foi testada** (exigiria refazer 615 MB de clone
  + dump do AoN). Nenhum portao compara o pin gravado com o pin em disco.
- **Nenhum `.mjs` de `app/verificacao/` foi executado** -- exigem dev server e
  browser Playwright sem binario instalado. Nao se sabe se os 16 passam hoje.
- **`simular_raw.py` nao foi executado** (2.000 personagens, custo de tempo).
- **As 27 falhas parametricas de `test_class_feat_traz_feat_da_classe_certa`**
  foram tratadas como uma assinatura so; 2 de 27 foram lidas no traceback.
