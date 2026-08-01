---
spec: tradutor-de-aumento-de-pericia
project: waybuilder
version: 1
status: aprovada
created: 2026-07-31
todo: 68
---

# Spec -- o aumento de pericia que o tradutor nao emitia, e o que ele nao prova

## A premissa que caiu

O item 68 do TODO registra que a metrica de pericia (62,9%, 1.298 de 2.064
pontos) nao mede a qualidade do motor. A justificativa gravada dentro do
proprio `motor/validar_iconics.py` apoiava isso em duas afirmacoes:

> (a) este tradutor (`validar_iconics.py`) nao emite escolhas `skill_increase`
> [...] e (b) `motor/motor.py` **nao processa o slot `skill_increase` de forma
> alguma** [...] `grep -n skill_increase motor/motor.py` nao retorna nenhuma
> ocorrencia.

**A afirmacao (b) esta falsa.** `grep -c skill_increase motor/motor.py` retorna
**11**: o motor processa o slot em `_aumentos_de_pericia` (linhas 573-642),
com cadencia lida do dado, teto de rank por nivel e recorte de escolha de
nivel futuro. Ela era verdadeira quando foi escrita e nunca foi revisada.

A afirmacao (a) continua verdadeira, e e o que esta spec resolve.

## O metodo, e por que ele nao e chute

Os iconics da Paizo existem como atores separados do Foundry nos niveis 1, 3 e
5 do mesmo build. O rank final de cada pericia esta em cada snapshot. O aumento
de pericia sobe exatamente **um** degrau, em niveis fixos declarados pela
classe. Logo o numero de aumentos gastos numa pericia entre dois snapshots
consecutivos e a **diferenca de rank entre eles** -- aritmetica, nao inferencia
estatistica.

Duas fontes, ambas do proprio ator, nenhuma da nossa base:

1. `pericias_oficiais(doc)` -- rank final por pericia, ja a uniao de
   `system.skills.<pericia>.rank` (discricionario) com `trainedSkills.value`
   do item de classe/antecedente (automatico). A armadilha aqui ja estava
   documentada e foi respeitada: `system.skills` **nao** e o rank final.
2. `system.skillIncreaseLevels.value` do item de classe **do ator** -- a
   cadencia. Medido: presente nos **129** atores traduziveis, ausente nos 7
   que ja nao traduziam.

A fonte da cadencia foi escolhida de proposito. Se ela viesse da nossa base, o
tradutor entregaria ao motor exatamente a tabela que o motor ja usa, e a
comparacao nao testaria nada. Vindo do Foundry e um oraculo independente.

**Medicao que isso libera:** o motor emitiu **zero** avisos de "aumento no
nivel N, que nao tem aumento" nos 129 atores. A cadencia declarada pela nossa
base coincide com a do Foundry em todos os casos -- resultado positivo que
antes nao existia.

## O caso ambiguo, tratado em vez de chutado

O snapshot mais baixo de um personagem nao tem com quem ser comparado.

- **Baseline de nivel 1**: nao ha ambiguidade. Nenhuma classe do corpus tem
  aumento no nivel 1 (a cadencia mais cedo comeca em 2), entao todo rank
  discricionario ali e treino inicial, nunca aumento. O diff e exato.
- **Baseline de nivel > 1**: rank 2 em Furtividade pode ser "treinou no 1 e
  aumentou no 3" ou "aumentou duas vezes", e nada no ator distingue os dois.

Medido: dos **78** personagens distintos, **100 snapshots** tem baseline de
nivel 1 e **36 nao tem** (47 personagens existem num nivel so). Para os 36,
este tradutor **nao emite aumento nenhum**. Emitir o palpite mais provavel
subiria a metrica sem que o motor tivesse acertado nada.

`identidade_do_ator` remove so o sufixo ` (Level N)`. ` (Beginner Box)` fica:
e um build alternativo da mesma personagem, e fundir os dois faz o diff
inventar aumento que nao existiu. Medido: colapsar Beginner Box produz 6
violacoes espurias de monotonicidade (Ezren, Kyra, Merisiel, Sajan, Seoni,
Valeros); mantendo separado, sobram 3 violacoes reais.

## A honestidade da metrica -- o limite deste ganho

Esta e uma ferramenta de medicao, entao o que o numero **deixa** de provar
precisa ficar escrito.

O tradutor alimenta o motor com `{"em": nivel, "pega": [pericia]}`. O motor
entao calcula `motor[L] = rank_base_que_ele_derivou + degraus`. Como os degraus
vieram do diff do oraculo, o resultado bate com o oficial **se e somente se o
rank base que o motor derivou estiver certo**. Ou seja: isto converte o aumento
de pericia de incognita nao auditavel em pass-through medido, e desloca o sinal
para o rank base. Nao prova que o motor implementa o aumento corretamente alem
de conferir cadencia e teto.

Isso e o oposto de maquiar a metrica: o ganho e pequeno justamente porque a
inferencia nao toca no que estava errado.

## Como se prova que funciona

`python3 motor/validar_iconics.py`, sem regenerar base nem fixtures.

- antes: **1.298 / 2.064 = 62,9%**
- depois: **1.341 / 2.064 = 65,0%** (+43 pontos)
- direcao: motor-menor cai de 763 para 720; motor-maior fica em 3, inalterado
  (nao houve sobre-concessao nova)
- divergencias de 2 degraus caem de 80 para 46; as de 1 degrau, de 679 para 670
- HP: inalterado (118 batem, 11 divergem) -- o slot nao toca HP

Caso concreto que passou a bater: **Amiri (Level 5)**, `athletics`. Barbaro
treina Atletismo de graca (`trainedSkills.value == ["athletics"]`), e o rank
oficial e `expert` no nivel 5 contra `trained` nos niveis 1 e 3. O diff acusa 1
degrau na janela (3, 5], a cadencia do Barbaro traz o nivel 5, e o tradutor
emite `{"em": 5, "slot": "skill_increase", "pega": ["athletics"]}`. O motor
sobe de `trained` para `expert` e o ponto passa a bater.

## O que esta spec NAO resolve, e declara

1. **O treino livre inicial (`pericias_livres`) -- a causa dominante, com
   numero.** O tradutor tambem nao emite as "N + INT" pericias treinadas na
   criacao. Medido por contrafactual (escrito no scratchpad, deliberadamente
   **nao** commitado): emitindo tambem `pericias_livres` a partir do snapshot
   de nivel 1, a metrica vai de 65,0% para **86,8%** -- **450** dos 723 pontos
   que sobram, 62% do resto. Fica fora por escopo, e porque tem um custo de
   medicao que precisa de decisao: no nivel 1 o rank oficial e *definido* pelo
   mesmo conjunto discricionario que seria alimentado, entao a fatia de nivel 1
   cairia de 218 divergencias para **1** e viraria quase tautologia. O sinal
   sobreviveria nos niveis 3+.
2. **Os 36 snapshots sem baseline de nivel 1** -- **242** dos 723 pontos que
   sobram (33%). Estruturalmente fora do alcance de qualquer tradutor que se
   recuse a chutar, com este corpus.
3. **Inconsistencia entre snapshots do mesmo build no corpus do Foundry.**
   Medido: **13 transicoes** em que o rank oficial sobe mais degraus do que a
   cadencia permite (18 degraus excedentes), que nenhum aumento explica. A
   ficha de nivel 1 da Nhalmika tem as 16 pericias em rank 0 e nenhum treino
   automatico, e a de nivel 3 traz `athletics:2, crafting:1, medicine:1,
   society:1`; a Jirelle vai de `deception:0` no nivel 1 para `deception:2` no
   nivel 3 com um unico nivel de aumento na janela. Nao e bug do motor nem do
   tradutor: e a fonte oficial que nao e um estado anterior exato do nivel
   seguinte. O tradutor descarta o excedente em vez de fabricar nivel.
4. **Em qual nivel exato da janela cada degrau caiu.** Nao e recuperavel do
   ator e nao muda o rank final -- todos os niveis da janela estao abaixo do
   snapshot. O pareamento e por ordem.
5. **Aumento gasto em pericia de Lore.** Fica fora das 16 comparadas; medido em
   4 aumentos nao localizados, que o tradutor simplesmente nao emite.
6. **`motor/motor.py` nao foi tocado.** Se a conclusao fosse que o motor
   precisa mudar, a decisao e do dono do arquivo.
