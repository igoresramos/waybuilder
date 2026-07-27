---
projeto: waybuilder
tipo: decisao pendente
data: 2026-07-27
status: itens 1-3 executados; falta a decisao de schema (item 53 do TODO)
---

# Duas linhas paralelas em 27/07, e o que fazer com a segunda

## O que aconteceu

Dois agentes trabalharam o mesmo dia com clones diferentes do Tartarus. O clone
de um deles estava **44 commits atras** do GitHub e nao deu `fetch` (o hook
auto-save commitou 9 vezes em 3 horas sem sincronizar). Resultado: a re-emissao
da base foi refeita do zero sobre um estado antigo, em paralelo com a linha que
ja tinha ido alem.

Nada foi perdido. O merge de sincronizacao (`a636b841`) ficou com a **linha do
GitHub** para os 36 conflitos de waybuilder, e a linha paralela esta inteira no
branch **`waybuilder-reemissao-paralela`**.

## O que a linha paralela tem que esta linha nao tem

Levantado por tres agentes comparando as duas (relatorios na sessao):

1. **Testes** -- 82 automatizados, incluindo invariantes lidos da base emitida
   (prov valido, `traits` nunca null, `rank == level` em spell, uma grafia por
   livro, `superseded_by` integro).
2. **Dois portoes novos** -- o de cobertura varre as **categorias do censo do
   AoN** em vez de uma allow-list de kinds escrita a mao, e por isso achou dois
   kinds de jogador ausentes: `tactic` (37, tacticas do Commander no
   Battlecry!) e `class-kit` (32, kits de equipamento inicial). O outro exige
   `text` em todo registro fora de uma lista de isencao declarada.
3. **Quatro defeitos de correcao achados por review adversarial**, corrigidos
   la: uniao de `traits` rodando na camada errada (o extrator ja colapsou as
   fontes, entao a uniao no reconciliador e vacua e `bastard-sword` perde o
   `-d12`); referencia `wb:` resolvida para o kind errado pela ponte do AoN;
   descarte silencioso quando duas entradas caem na mesma fonte; e comparacao
   normalizada demais mascarando divergencia real de grafia.
4. **Matriz de balanceamento 1-15** com politica de acao simetrica (12 classes
   puras + 10 combinacoes, combate e nao-combate).

## Dois achados que valem independente da decisao

- **Os 35 PDFs oficiais (1,7 GB) NAO se perderam.** Estao neste PC, em
  `pipeline/dados_brutos/pdfs/`. O item 44 do TODO diz o contrario -- foi
  escrito no outro clone, que nao os tinha.
- **`tabelas_conjuracao_pdf.json` tambem existe aqui**, com as 11 conjuradoras,
  livro e pagina. E o artefato que o item 45 registrou como perda real. O
  Animist ja foi recuperado por outra fonte (o campo `markdown` do AoN), entao
  a tabela do PDF vale hoje como **cross-check independente**, nao como fonte
  unica.

## Resultado da comparacao (3 agentes, tudo medido sobre as duas bases)

**Surpresa boa: as duas linhas fizeram a MESMA auditoria em paralelo.** Tres
dos quatro defeitos que o review adversarial achou na linha paralela ja estao
corrigidos aqui, com os mesmos numeros citados nos comentarios do codigo
(61 ids, 46 pares, 88% dos 2.299 conflitos). Nao ha nada a portar neles.

| defeito do review | esta linha |
|---|---|
| uniao de `traits` na camada errada | **ja corrigido** -- `traits_uniao.py` tem `unir()` e `unir_do_conflito()`; `bastard-sword` = `two-hand-d12`; 2.267 registros com 2+ contribuintes em `prov.traits` |
| referencia `wb:` resolvida para kind errado | **ja corrigido** -- `resolver_referencias.py` confere `kind`; 0 citantes de `wb:trait/versatile` |
| `_iguais` mascarando divergencia de grafia | **ja corrigido** -- normaliza so `source.book`; o caso `God's`/`Gods'` esta registrado como conflito |
| **descarte silencioso na colisao de mesma fonte** | **VIVO** -- `reconciliar.py::fundir()` monta `{campo, fa: atual, fb: v}` com `fa == fb`, entao a chave colide e o registro de conflito passa a mentir sobre qual valor venceu. **337 entradas** com essa assinatura |

**Portoes:** os testes sao os mesmos nos dois lados (entraram por este merge).
O que falta aqui:

| portao | estado |
|---|---|
| 4 (queda de cobertura) | **defeito vivo** -- `--gravar-cobertura` grava a baseline mesmo quando o portao falha, entao a regressao e acusada uma vez e nunca mais |
| 8 (kind com 2+ fontes e zero conflito) | nao existe |
| 9 (censo do AoN por **categoria**) | nao existe -- e o unico gabarito EXTERNO; sem ele nao ha como achar kind inteiro ausente. Foi assim que apareceram `tactic` (37) e `class-kit` (32) |
| 10 (`text` obrigatorio fora de isencao) | nao existe |
| 7 (colisao de identidade) | **a versao daqui e melhor** -- detecta direto contra o indice do AoN em vez de conferir se o passo anterior rodou. Nao portar |

**Dados:** `wb:feat/efficient-alchemy` esta com `level: 20` aqui (e o
`Efficient Alchemy (Paragon)`, outro feat) contra `4` na outra linha, com o
mesmo `xref.aon`. E a familia `Aeon Stone` nao tem `superseded_by` (o campo nao
existe neste schema). Ha ainda **374 registros** que so a outra linha tem
(155 feat, 110 equipment, sem `xref.aon` correspondente aqui) -- pelo nome e
pela fonte parecem legado pre-remaster, e **precisam ser checados antes** de
qualquer recuperacao: pode ser exclusao proposital.

**Simulacoes:** nada a portar -- esta linha tem tudo da outra mais a simulacao
da regra 17b.

## Ordem recomendada

1. Guarda no portao 4 (nao gravar baseline quando falha) -- 1 linha
2. Colisao de fonte em `fundir()` -- desambiguar `fa`/`fb` antes do append
3. **Reconciliar a suite de testes**: 34 dos 82 quebram aqui porque vieram da
   outra linha e testam funcoes que este pipeline ja refatorou
   (`carregar_curadoria`, `_parse_pdf_cell`). Ou adaptar, ou remover -- suite
   vermelha nao serve de sinal
4. Portao 9 (censo por categoria) -- o de maior valor futuro; exige remapear o
   dicionario de kinds de 24 para os 52 daqui
5. `efficient-alchemy` level 4
6. Investigar os 374 registros
7. Portoes 10 e 8, depois de calibrar isencao e piso

**Nao fazer:** re-emitir a base (esta linha e superior em arquitetura), portar
testes (ja estao aqui) ou simulacoes.

## Executado (itens 1, 2 e 3)

### 1. Portao 4 nao rebaixa mais a propria linha de base

`--gravar-cobertura` gravava a baseline mesmo com o portao falhando. Agora so
grava com o build limpo, e tambem recusa quando algum portao ficou **NAO
MEDIDO** -- fixar referencia a partir de um build que nao mediu e a mesma
armadilha por outro caminho.

### 2. Colisao de fonte em `fundir()`

Quando os dois lados vinham da mesma fonte, `{campo, fa: atual, fb: v}` colapsava
no literal do dict e o registro de conflito passava a dizer que o vencedor era o
valor perdedor. Desambiguado como `comum.escolher` ja fazia (`aon` / `aon_2`).
Havia **337 entradas** com essa assinatura; as antigas so somem no proximo
build, porque o valor sobrescrito nao esta mais no registro (da para reconstruir
pelo campo emitido, se valer a pena).

### 3. Suite de testes: de 34 quebrados para zero

**85 testes, verde.** Nenhum foi apagado. A classificacao explica o que cada
grupo era de verdade:

| grupo | n | destino |
|---|---|---|
| gap de schema v1 x v2 | 7 | `expectedFailure` com o numero medido -- viram verde sozinhos se a v2 for adotada, e o unittest cobra a retirada do marcador |
| feature pendente (tabela do PDF) | 14 | `skipUnless` guardado por `hasattr` -- caem sozinhos quando a integracao entrar (task 16) |
| API que mudou de lugar | 10 | reescritos contra o ARTEFATO, que e o alvo que interessa |
| defeito real medido | 3 | teste com teto no numero atual (`assertLessEqual`): nao mascara, mas acusa **piora** |

Os reescritos contra o artefato merecem nota: os testes originais chamavam
`reconciliar.desmembrar`, `reconciliar.carregar_curadoria` e
`fundir_renomeados.veto`, que aqui vivem dentro do `main()`. Reescrever para
medir o dado emitido -- `death-from-above` voltou a ter os niveis 8 e 16 em
registros separados, `blade-byrnie` uniu as facetas das duas fontes,
`vicious-swing` guarda `legado_aon: feat-359` -- e mais forte do que testar a
funcao: teste de funcao verde com dado emitido errado foi exatamente o que
deixou a uniao de traits passar na v1.

Duas hipoteses minhas cairam na primeira execucao e o dado estava certo, nao o
teste: `aliases` vazio nao e perda (em 323 dos 616 casos o remaster nao mudou o
nome, so o livro -- o rastro obrigatorio e o `historico`), e no desmembramento
so o irmao CRIADO carrega `desmembrado_de`.

### Bonus: o portao que passava por ausencia de dado

Achado ao tentar rodar o build aqui. `indice_aon()` e `indice_foundry()` vinham
**vazios nesta maquina** -- procuravam `dados_brutos/foundry_repo/` e
`dados_brutos/aon_dump/`, que aqui se chamam `foundry/` e nunca foram gerados --
e os portoes 2 e 7 respondiam `return 0`: **passaram**. E a mesma falha que eles
existem para pegar.

Corrigido: `comum.packs_foundry()` conhece os dois nomes de pasta (os extratores
ja tinham o fallback; portoes, `emitir_textos`, `aplicar_subclasses` e
`converter_rule_elements` nao), `indice_aon()` cai nos apelidos versionados
(`dados_brutos/aon_*.json`, 33.348 docs) completando campo em vez de
sobrescrever, e portao desligado agora devolve `None` = **NAO MEDIDO**.

Resultado com os indices carregando de verdade: portao 2 passa limpo (0 `level`
divergente sem conflito registrado, contra 28.689 docs do Foundry e 33.348 do
AoN) e o **portao 7 acusou 2 colisoes de identidade novas** -- item 49 do TODO.

O que isto NAO significa: a base emitida nao foi afetada. Ela foi construida no
outro PC, onde `foundry_repo/` existia; os `grants` convertidos de rule element
(1.709 `flat_modifier`, 896 `grant_feat`, ...) estao la. O defeito bloqueava
**rebuild aqui**, e mentia no relatorio de portoes.

### 4. Portao 9 -- censo do AoN por categoria

O unico gabarito **externo**. Os outros oito comparam a base com ela mesma (o
build anterior) ou com o que ela ja cita; nenhum responde "existe conteudo la
fora que nunca entrou".

Duas decisoes de projeto fizeram a diferenca entre um portao util e um barulhento:

- **Por ID, nao por contagem.** Contar deixa registro extra mascarar ausencia:
  20 itens que so o pf2etools tem escondem 20 itens do AoN que faltam, e o total
  bate. Com id, nada se compensa.
- **Nome tambem cobre.** O AoN publica a mesma entidade em varios docs quando
  ela reaparece em outro livro (`Aldori Dueling Sword` tem 3 docs, sem
  `legacy_id` ligando os tres). So por id, isso viraria 1.083 falsas ausencias.
  Cobrindo tambem por nome, sobram **238 reais**.

Ausencia ja decidida vive em `censo_ausencias.json` com motivo, mesmo contrato
do portao 8: aparece no relatorio, nao bloqueia; ausencia **nova** quebra.

O que ele achou de primeira:

| achado | n | destino |
|---|---|---|
| `tactic` -- tacticas do Commander (Battlecry!) | 37 | kind nunca extraido, dump ja em disco -- TODO 54 |
| `class-kit` -- kits de equipamento inicial | 32 | idem |
| class-feature de verdade fora da base | 4 | Incredible/Vigilant Senses, Lightning Reflexes, Premonition's Reflexes -- TODO 55 |
| linha de tabela de progressao | 159 | ausencia por design (a base modela em `class.progressao`) |
| entrada de piada do proprio AoN | 5 | Dad Joke, Wombat Style... nao e conteudo |

### Bonus 2: 69 registros servindo conteudo pre-remaster

Medido de passagem, com a ponte que o portao 9 usa. **646 registros** tem
`xref.aon` apontando para doc que o AoN marca com `remaster_id` de mesma
categoria. Em **577** o sucessor tambem esta na base como registro proprio --
isso e correto, e a fusao vetada por campo estruturado divergente (a regra do
item 24: se discorda, nao funde).

Os outros **69 nao tem sucessor nenhum na base**: o unico dado disponivel e o
pre-remaster. 63 sao arquetipos (`Acrobat` aponta `archetype-45`, cujo sucessor
`archetype-236` nunca entrou). Passou despercebido porque o extrator casa por
nome e o nome nao mudou. TODO 56.

Fora dessa conta, sem acao: 38 class-features cujo `remaster_id` aponta para a
CLASSE (padrao do AoN, o veto por `kind` ja barra) e 71 com `remaster_id: '0'`,
que e "removido no remaster" -- mantidos de proposito.

### O que continua sem poder rodar nesta maquina

`build.sh` passo 0 (`buscar_fontes.sh` + `dump_aon.py`) nunca rodou aqui, entao
`dados_brutos/aon_dump/` nao existe. Com os fallbacks acima a cadeia inteira
passou a carregar, mas **nao re-emiti a base** de proposito: isso e decisao do
Igor e o doc dizia para nao fazer. Um rebuild resolveria de uma vez os itens 50
e 51 (113 conflitos de traits residuais, 13 nomes legados de ancestria, 2 obras
com grafia dupla), que hoje sao residuo do dado emitido, nao do codigo.
