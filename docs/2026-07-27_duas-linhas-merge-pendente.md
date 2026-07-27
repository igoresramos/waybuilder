---
projeto: waybuilder
tipo: decisao pendente
data: 2026-07-27
status: aguardando decisao do Igor
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
