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

## O que precisa ser decidido

Portar da linha paralela: (a) so as correcoes que forem bug real aqui,
(b) tambem os testes e portoes, ou (c) nada -- fechar o branch.
