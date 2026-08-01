# Medicao -- tradutor de aumento de pericia

Data: 2026-07-31
Spec: `specs/2026-07-31-tradutor-de-aumento-de-pericia.md`
Arquivo alterado: `motor/validar_iconics.py` (so ele)
Comando: `python3 motor/validar_iconics.py` -- sem `build.sh`, sem regenerar
base nem fixtures.

## Antes e depois

| | pontos que batem | de | % |
|---|---|---|---|
| antes | 1.298 | 2.064 | **62,9%** |
| depois | 1.341 | 2.064 | **65,0%** |

**+43 pontos, +2,1 pontos percentuais.** O denominador nao mudou: 129
personagens traduzidos x 16 pericias. HP inalterado (118 batem, 11 divergem) --
o slot nao toca HP.

Direcao e tamanho da divergencia:

| | antes | depois |
|---|---|---|
| motor da rank MENOR que o oficial | 763 | 720 |
| motor da rank MAIOR que o oficial | 3 | 3 |
| divergencia de 1 degrau | 679 | 670 |
| divergencia de 2 degraus | 80 | 46 |
| divergencia de 3 degraus | 4 | 4 |

O motor-maior nao subiu: emitir aumento nao criou sobre-concessao nenhuma. O
ganho vem quase todo do bloco de 2 degraus (80 -> 46), que e exatamente o
formato esperado de "faltava um aumento em cima de um treino que o motor ja
tinha".

Por nivel de personagem:

| nivel | divergencias antes | depois |
|---|---|---|
| 1 | 218 / 688 | 218 / 688 |
| 2 | 26 / 64 | 26 / 64 |
| 3 | 193 / 528 | 176 / 528 |
| 4 | 45 / 128 | 45 / 128 |
| 5 | 221 / 528 | 195 / 528 |
| 6 | 30 / 64 | 30 / 64 |
| 10 | 33 / 64 | 33 / 64 |

O nivel 1 nao se move nem um ponto, e esta certo que nao se mova: nenhuma
classe do corpus tem aumento de pericia no nivel 1. Isso ja adiantava que o
teto deste trabalho era baixo.

## O metodo de inferencia

Aumento de pericia sobe 1 degrau, em niveis fixos por classe. Os iconics
existem como atores separados nos niveis 1, 3 e 5 do mesmo build. Logo o numero
de aumentos gastos numa pericia entre dois snapshots e a diferenca de rank
entre eles.

Duas fontes, ambas do ator do Foundry, **nenhuma da nossa base**:

1. `pericias_oficiais(doc)` -- rank final, ja unindo `system.skills.<p>.rank`
   com `trainedSkills.value` do item de classe/antecedente. A armadilha de que
   `system.skills` nao e o rank final foi respeitada.
2. `system.skillIncreaseLevels.value` do item de classe do ator -- a cadencia.
   Presente nos 129 atores traduziveis.

A cadencia vem do Foundry, e nao da nossa base, de proposito: se viesse da
base, o tradutor devolveria ao motor a mesma tabela que o motor ja usa e a
comparacao nao testaria nada.

**Resultado limpo que isso liberou:** o motor emitiu **zero** avisos de
"aumento no nivel N, que nao tem aumento" nos 129 atores. A cadencia declarada
pela nossa base coincide com a do Foundry em 100% dos casos.

Inventario da inferencia:

| | |
|---|---|
| personagens distintos | 78 |
| snapshots com baseline de nivel 1 | 100 |
| snapshots sem baseline de nivel 1 | 36 |
| personagens com snapshot unico | 47 |
| aumentos emitidos | 77 |
| aumentos nao localizados nas 16 pericias (Lore) | 4 |
| transicoes com degraus acima da cadencia | 13 |
| rank regredindo entre snapshots | 3 |

## Os casos ambiguos, e o que foi feito com eles

**1. Sem baseline de nivel 1 (36 snapshots).** Rank 2 em Furtividade num
personagem que so existe no nivel 5 pode ser "treinou no 1 e aumentou no 3" ou
"aumentou duas vezes". Nada no ator distingue. **Nao se emite aumento nenhum**
para esses. Chutar o mais provavel subiria a metrica sem o motor ter acertado
nada.

**2. Identidade do personagem.** `identidade_do_ator` remove so ` (Level N)`.
` (Beginner Box)` fica, porque e outro build da mesma personagem. Medido:
colapsar os dois produz 6 violacoes espurias de monotonicidade (Ezren, Kyra,
Merisiel, Sajan, Seoni, Valeros). Mantendo separado sobram 3 violacoes reais
(Harsk `nature`, Nahoa `survival` e `thievery`), que sao defeito da fonte.

**3. Qual nivel da janela recebeu cada degrau.** Nao e recuperavel e nao muda o
rank final -- todos os niveis da janela estao abaixo do snapshot. Pareado por
ordem. So em **31 dos 78** personagens o diff e exato em toda transicao
(degraus == niveis); nos demais o pareamento e uma escolha entre alternativas
equivalentes para o rank final, mas nao uma prova.

**4. Degraus acima da cadencia (13 transicoes, 18 degraus excedentes).** O
excedente e descartado; o tradutor nao fabrica nivel de aumento.

## Honestidade da metrica -- o que estes 65,0% NAO provam

O tradutor entrega o degrau ja calculado do oraculo. O motor faz
`motor[L] = rank_base_derivado + degraus`. Logo o ponto bate **se e somente se
o rank base que o motor derivou estiver certo**.

Isto converte o aumento de pericia de incognita nao auditavel em pass-through
medido, e desloca o sinal para o rank base. **Nao prova** que o motor
implementa aumento de pericia corretamente alem de conferir cadencia (que
conferiu: zero avisos) e teto de rank.

O que separa isto de fraude de medicao e a fonte: a inferencia le so o ator do
Foundry e **nunca** le a saida do motor. O criterio recusado explicitamente foi
"emitir aumento onde o motor ficou abaixo do oficial" -- isso copiaria o
gabarito para dentro da entrada e produziria um numero sem significado. O ganho
ser pequeno (+2,1 p.p.) e consequencia direta de a inferencia nao tocar no que
estava errado.

## A causa nomeada do que sobra -- 723 pontos

Decomposicao exata (31 + 242 + 450 = 723):

| causa | pontos | % do que sobra |
|---|---|---|
| treino livre inicial (`pericias_livres`) nao emitido | **450** | 62,2% |
| snapshots sem baseline de nivel 1 | **242** | 33,5% |
| residuo real depois das duas | **31** | 4,3% |

### 1. `pericias_livres` -- 450 pontos, a causa dominante

O tradutor tambem nao emite as "N + INT" pericias treinadas na criacao. O slot
existe no motor (`_gastar_pericias_livres`, linha 748) e e alimentado por
`{"em": "criacao", "slot": "pericias_livres", "pega": [...]}`. O oraculo
tambem existe: no snapshot de nivel 1, `system.skills.<p>.rank >= 1` e
exatamente a escolha discricionaria do jogador.

**Contrafactual medido** (script no scratchpad, deliberadamente **nao**
commitado): emitindo tambem `pericias_livres` a partir do snapshot de nivel 1,

- 65,0% -> **86,8%** (1.791 / 2.064)
- nivel 1: de 218 divergencias para **1**
- nivel 3: de 176 para 58; nivel 5: de 195 para 80

Ficou fora por escopo, e por um custo de medicao que precisa de decisao
consciente antes de ser adotado: no nivel 1 o rank oficial e *definido* pelo
mesmo conjunto discricionario que seria alimentado, entao a fatia de nivel 1
(688 pontos, um terco do total) vira quase tautologia -- 1 divergencia em 688.
O numero subiria muito, e a fracao dele que mede o motor cairia. O sinal
sobreviveria nos niveis 3+, e a decisao de aceitar essa troca nao e do autor
deste trabalho.

### 2. Sem baseline de nivel 1 -- 242 pontos

36 snapshots (42,0% dos seus 576 pontos divergem, contra 32,3% dos 1.488
pontos com baseline). Estruturalmente fora do alcance de qualquer tradutor que
se recuse a chutar, com este corpus. So aumentaria com mais snapshots.

### 3. Residuo real -- 31 pontos

O que sobra depois de `skill_increase` **e** `pericias_livres`. Inclui:

- **Sobre-concessao, 3 pontos.** Todos em `crafting`, todos com a mesma causa:
  proficiencia concedida automaticamente por feat/class-feature que o
  `system.skills` do ator nao persiste. `Droven` (Inventor, niveis 3 e 5) pela
  class-feature `Expert Overdrive` ("You become an expert in Crafting"), e
  `Booker Kaar` (Gunslinger, nivel 3) pelo feat `Munitions Crafter`, cujo ator
  traz `skills.crafting.rank == 0` mesmo carregando o feat. **O motor esta
  certo nos 3; a fonte oficial e que esta incompleta.** O texto do relatorio
  dizia "os 2 casos" e listava so Droven -- corrigido.
- **Inconsistencia entre snapshots do mesmo build.** Medido em 13 transicoes,
  18 degraus excedentes. Evidencia concreta: a ficha de nivel 1 da **Nhalmika**
  tem as 16 pericias em rank 0 e nenhum treino automatico, e a de nivel 3 traz
  `athletics:2, crafting:1, medicine:1, society:1`; a **Jirelle** vai de
  `deception:0` no nivel 1 para `deception:2` no nivel 3 com um unico nivel de
  aumento na janela, o que RAW nao permite. Nao e bug do motor nem do tradutor:
  a ficha de um nivel nao e o estado anterior exato do nivel seguinte.

## Texto desatualizado corrigido

O relatorio gerado afirmava que `motor/motor.py` "nao processa o slot
`skill_increase` de forma alguma", citando um `grep` vazio. **Falso desde que o
motor ganhou `_aumentos_de_pericia`**: `grep -c skill_increase motor/motor.py`
retorna **11**. A afirmacao irma, de que o tradutor nao emite `skill_increase`,
era verdadeira e deixou de ser com este trabalho. As duas foram substituidas
por uma secao "Decomposicao do que sobra" que se calcula sozinha a cada
execucao, em vez de prosa fixa que envelhece em silencio -- que foi
exatamente o que aconteceu com as duas afirmacoes anteriores e com a contagem
de sobre-concessao.

## Nao alterado

`pipeline/`, `TODO.md`, `LOG.md`, `PROJECT.md`, `README.md`, `app/`,
`motor/motor.py`, `motor/fixtures/` e as demais specs. Nenhuma mudanca no motor
foi necessaria: o slot ja estava implementado e correto no que este trabalho
conseguiu exercitar.
