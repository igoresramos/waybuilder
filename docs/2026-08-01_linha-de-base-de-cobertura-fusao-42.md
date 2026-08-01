# Linha de base de cobertura refixada apos a fusao de 42 duplicatas

Data: 2026-08-01
Arquivo alterado: `pipeline/base/_cobertura.json`
Spec da queda: `specs/2026-08-01-fusao-de-duplicata-de-nome.md`

## O que aconteceu

O passo novo `pipeline/fundir_duplicata_de_nome.py` fundiu 42 duplicatas aon/foundry.
O portao 4 (`pipeline/portoes.py:901`, catraca de cobertura) leu isso como regressao e
ficou vermelho com 4 ocorrencias -- que sao exatamente as 42 fusoes distribuidas por kind:

| kind | antes | depois | delta |
|---|---|---|---|
| `feat` | 6265 | 6239 | -26 |
| `background` | 524 | 521 | -3 |
| `equipment` | 6046 | 6033 | -13 |
| **total** | **20125** | **20083** | **-42** |

26 + 3 + 13 = 42, e 20125 - 20083 = 42. A queda fecha com o numero de fusoes, sem sobra:
nenhum registro sumiu por outro motivo. Por isso a queda e aceitavel -- e o resultado
revisado do passo, nao perda de dado.

## Estado dos portoes antes de gravar

Rodada limpa (`python3 pipeline/portoes.py --fase final`), 2026-08-01:

```
portao 1  OK  | portao 5  OK  | portao 9   OK
portao 2  OK  | portao 6  OK  | portao 10  OK
portao 3  OK  | portao 7  n/a | portao 11  OK
portao 4  FALHA  cobertura caindo vs build anterior: 4
portao 8  OK
```

O 4 era o UNICO vermelho. Essa verificacao e obrigatoria antes de usar `--aceitar-queda`
(motivo na secao seguinte).

## O que foi rodado

```
python3 pipeline/portoes.py --fase final --gravar-cobertura --aceitar-queda
```

Resultado: `linha de base de cobertura gravada em pipeline/base/_cobertura.json`.
Prova de que a linha de base ficou no numero novo:

```
total gravado: 20083
registros reais em index.json: 20083
feat: 6239  background: 521  equipment: 6033
por_campo_critico: {'weapon.damage': 985, 'armor.ac_bonus': 206, 'shield.ac_bonus': 118}
```

Reexecucao SEM flags depois disso: os 11 portoes aplicaveis passam, portao 4 com 0
ocorrencias. Ou seja, a catraca voltou a ser util -- proxima queda nao intencional
sera acusada contra 20083.

O piso de grants (`pipeline/base/_cobertura_grants.json`) foi reescrito no mesmo ato com
`{"sem_resposta": 0}`, que e o valor que ja estava la. Sem mudanca de fato.

## Defeito de desenho da flag `--aceitar-queda`

`pipeline/portoes.py:964`:

```python
if "--aceitar-queda" in sys.argv and falhou and not desligados:
    print("  queda de cobertura aceita explicitamente (--aceitar-queda)")
    falhou = 0
```

`falhou` e um contador agregado de TODOS os portoes reprovados. Zerar ele perdoa qualquer
falha, nao so a queda de cobertura. Com o nome que a flag tem, um portao 3 (`requires`
citando id inexistente) ou um portao 5 (`license` ausente) vermelho na mesma rodada seria
engolido em silencio -- e ainda gravaria a linha de base a partir de um build defeituoso,
que e precisamente o que o comentario logo acima dela diz que nao pode acontecer
("gravar depois de falhar rebaixa a referencia e a regressao e acusada uma vez so").

O escopo correto da flag sao os tres portoes de catraca, os unicos que comparam contra a
linha de base anterior e portanto os unicos onde "cair" pode ser intencional:

- portao 4 -- cobertura caindo vs build anterior (`portoes.py:901`)
- portao 10 -- cobertura de `grants_completos` (`portoes.py:907`, catraca declarada no
  proprio docstring em `portoes.py:770`)
- portao 11 -- campo critico ausente vs build anterior (`portoes.py:908`)

Os outros oito sao invariantes absolutos: nao existe queda intencional de "license
ausente". Perdoar eles nunca e a intencao de quem digita `--aceitar-queda`.

### Correcao sugerida (nao aplicada aqui)

Trocar o contador agregado por um conjunto de numeros de portao reprovado e perdoar
so a interseccao com as catracas:

```python
CATRACAS = {4, 10, 11}
...
reprovados = set()          # em vez de falhou += 1
...
if "--aceitar-queda" in sys.argv and reprovados and not desligados:
    if reprovados <= CATRACAS:
        reprovados = set()
    else:
        print(f"  --aceitar-queda NAO se aplica: portoes {sorted(reprovados - CATRACAS)} "
              f"nao sao catracas")
```

Assim a flag falha alto quando usada fora do escopo, em vez de esconder defeito real.
Enquanto isso nao existir, a regra operacional e a que foi seguida nesta rodada:
**so usar `--aceitar-queda` depois de rodar os portoes sem flag e confirmar que os
unicos vermelhos sao catracas.**

## Pendente

A correcao da flag nao foi aplicada -- este documento so registra o defeito. Alterar
`portoes.py` para isso e mudanca de comportamento de portao e pede spec propria antes
do codigo.
