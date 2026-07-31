---
spec: colisao-no-comparador
project: waybuilder
version: 1
status: aprovada
created: 2026-07-31
todo: 84
---

# Spec -- a colisao de normalizacao que faz a cobertura mentir

## O defeito, como o item 84 o registrou

> `incredible-familiar` e `incredible-familiar-animist` colidem na normalizacao
> e o script conta como "casado", entao par assim nunca aparece no placar --
> consertar antes da proxima rodada, senao a cobertura mente.

## O mecanismo, lido no codigo

`norm()` apaga o sufixo de desambiguacao (`\s*\([^)]*\)\s*$`), e isso e
DELIBERADO: `Guardian's Deflection (Fighter)` e o mesmo feat que o
`Guardian's Deflection` deles. O problema nao e a normalizacao, e o que vem
depois dela:

```python
for chave in chaves:
    nossos.setdefault(chave, c)     # so o PRIMEIRO registro da chave
...
casadas = nossos.keys() & deles.keys()
for c in todos:
    if chaves_de[c["id"]] & casadas: continue   # mas TODOS sao pulados
```

`nossos` guarda um registro por chave; `chaves_de` guarda a chave em **todos**
os registros que a produzem. Entao, com tres `Incredible Familiar`:

1. `nossos["incredible familiar"]` e o primeiro deles;
2. a chave entra em `casadas` porque o Pathbuilder tem a entrada dele;
3. os **tres** somem de `so_no_waybuilder`, contados como casados;
4. e o laco de divergencia so olha `nossos[k]` -- o `atende` dos outros dois
   nunca e comparado com nada.

O passo 3 e intencional e fica: e o que impede o DESMEMBRADO
(`Dueling Dance (Fighter)`, criado por colisao de identidade) de virar sobra
falsa quando o irmao ja casou. O passo **4 e o buraco**: divergencia de regra
num registro colidido e invisivel por construcao.

## O tamanho, medido

Na base inteira, kind `feat`: **75 chaves** normalizam igual, envolvendo
**205 registros**. Nas 35 sondas ja gravadas, **34 chaves** colidem dentro de
um mesmo slot. A maioria e desmembramento legitimo (`(Fighter)`, `(Ranger)`,
`(Kingmaker)`) ou alias de remaster (`Stance Savant` -> `Opening Stance`,
`Domain Wellspring` -> `Domain Focus`) -- e por isso o passo 3 esta certo. Mas
os 205 sao exatamente os registros cuja disponibilidade o comparador nunca
checa.

## O conserto

Duas mudancas, ambas no `comparar()`:

1. **O veredito passa a ser do GRUPO**, nao do primeiro registro da chave.
   Quando a colisao e desmembramento nosso, UM dos irmaos e o par legitimo da
   entrada deles: se ele concorda, nao ha divergencia, e cobrar do outro irmao
   fabrica falso positivo. So ha divergencia quando **nenhum** dos nossos
   concorda -- e ai ela sai nomeando todos. Um registro que entra por duas
   chaves (nome e alias) e comparado uma vez, nao duas.
2. **Declarar a colisao no relatorio** (`colisoes_de_normalizacao`). Truncar
   cobertura em silencio faz o relatorio dizer "cobri tudo" quando nao cobriu;
   o projeto ja pagou por isso no item 97, medido tres vezes.

O `norm()` nao muda, `casadas` nao muda, `so_no_waybuilder` nao muda. Nao ha
nova heuristica para separar "desmembrado" de "feat distinto": o relatorio
mostra o par e quem le decide.

## O resultado, medido contra as 35 sondas ja gravadas

Rodando o comparador ANTIGO e o NOVO sobre a mesma base, para separar o efeito
do conserto da deriva da base (que existe: `em_comum` subiu 222->224, 223->225
e 98->99 desde a rodada 6, e isso e a base tendo crescido, nao o conserto):

| | |
|---|---|
| contagens (`em_comum`, `so_no_*`, totais) | **identicas em todos os slots** |
| colisoes agora declaradas | **48**, em 14 relatorios |
| linhas duplicadas removidas | **12** (`Crossbow Infiltrator Dedication` x11, `Domain Focus`) |
| falsos positivos eliminados | **2** |
| divergencias novas | 0 nesta amostra |

Os dois falsos positivos sao o caso exato, e valem por serem o oposto do que o
item previa. Na chave `green empathy` o Pathbuilder tem `Green Empathy` (nivel
6, indisponivel) e nos temos DOIS registros: `Plant Empathy`, que carrega
`Green Empathy` em `aliases` e esta disponivel, e o `Green Empathy` de verdade,
que nao esta. O codigo antigo pegava o primeiro e acusava
`Plant Empathy: wb=true pb=false`. **Nao era divergencia de regra nenhuma** --
era o irmao errado sendo comparado. Idem `Domain Focus` / `Domain Wellspring`
no Clerigo 20.

O item dizia que a colisao ESCONDIA pontos do placar. Escondia -- e tambem
INVENTAVA. As duas metades saem pela mesma porta.

## Como se prova que funciona

1. Contagens identicas slot a slot entre o comparador antigo e o novo. **Feito.**
2. As colisoes aparecem no relatorio com os nomes dos dois lados. **Feito: 48.**
3. Nenhum registro reportado duas vezes no mesmo relatorio. **Feito.**
4. Cada divergencia que sumiu tem causa lida, nao suposta. **Feito: as 2 acima.**
