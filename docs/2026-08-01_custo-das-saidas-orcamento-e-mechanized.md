# Custo das saidas: orcamento do payload e invariante `mechanized`

Data: 2026-08-01. Dois testes vermelhos que NAO foram decididos aqui de
proposito -- os dois pedem decisao de projeto, nao conserto mecanico. O teste
fica como esta ate a decisao. Este documento mede o custo de cada saida.

Tudo abaixo foi medido sobre `pipeline/base/index.json` (20.083 registros) e
`pipeline/base/app/` do build de 2026-08-01, com `gzip.compress` sobre o JSON
minificado -- a mesma conta que `pipeline/emitir_app.py::escrever` faz.

---

## 1. `test_o_nucleo_cabe_no_orcamento` (pipeline/testes/test_emitir_app.py:65)

### O estado

```
nucleo (8 kinds)   558.785 bytes gzip
orcamento          555.745 bytes gzip   (0,53 MB, test_emitir_app.py:31)
excesso              3.040 bytes         (+0,55%)
```

Composicao do nucleo, por fatia do manifesto:

| kind | registros | gzip |
|---|---:|---:|
| feat | 6.239 | 439.003 |
| background | 521 | 41.285 |
| class-feature | 847 | 28.243 |
| class | 27 | 17.651 |
| archetype | 243 | 13.518 |
| heritage | 326 | 12.088 |
| ancestry | 50 | 6.068 |
| skill | 33 | 929 |

`feat` sozinho e 78,6% do nucleo.

### Quando estourou, e por quem

Reconstruido rodando a mesma soma sobre cada versao de
`pipeline/base/app/_manifesto.json` no historico:

| commit | data | nucleo | folga |
|---|---|---:|---:|
| 056f606 | 07-31 | 554.775 | -970 |
| e6d75b9 | 07-31 | 557.960 | **+2.215** |
| 7862a3b | 08-01 | 558.785 | +3.040 |

O teto caiu em **e6d75b9** ("kind action -- o pack que nenhum extrator lia",
item 111), que somou 3.185 bytes ao nucleo. A fusao de duplicata (item 84)
somou os outros 825. **Nao foi a fusao que quebrou este teste** -- ela achou o
teste ja vermelho.

### O que o numero 0,53 MB ainda significa

Nada em producao. Esta escrito, com data e autor:

> **Adendo -- o teto de payload saiu (2026-07-28, decisao do Igor)**
> O alvo de 0,53 MB gzip era restricao de projeto, e estava amputando o app em
> silencio. O Igor liberou ("o importante e funcionar"), e a base passa a
> viajar inteira.
> -- `specs/2026-07-28-ui-pathbuilder.md:161`

E o codigo obedeceu: `app/src/carregarBase.ts:78` monta a lista de kinds a
partir de `_manifesto.json` e baixa **todas as 58 fatias**. A primeira carga
real de hoje e:

```
todas as fatias      1.203.316 bytes gzip   (1,148 MB)
o "nucleo" medido      558.785 bytes gzip   = 46,4% do que o app baixa
```

Ou seja: o teste guarda um teto revogado ha 4 dias, sobre um recorte de 8 kinds
que nenhum cliente carrega separadamente. Ele nao reprova quando a carga real
piora (ela ja esta em 2,16x o "orcamento") e reprova quando um kind do recorte
antigo cresce. E medicao no lugar errado, nao aperto de mais.

### As tres saidas, com o custo

**A. Aposentar o teto e travar a carga REAL (recomendada).**
Trocar `ORCAMENTO_NUCLEO` por um ratchet sobre a soma de todas as fatias, que e
o numero que o usuario paga. Custo: ~10 linhas em
`pipeline/testes/test_emitir_app.py` (a constante, o teste, e o bloco de
cabecalho que fala em "nucleo"), mais a citacao do adendo da spec para o teste
nao ser desfeito de novo por quem so ler o codigo. Risco: escolher o teto novo
sem criterio -- 1,148 MB medido hoje sugere 1,25 MB, que da 8,9% de folga.
Beneficio: passa a acusar exatamente o que o cliente sente.

**B. Subir o orcamento e registrar.**
`0,53 -> 0,55 MB` (576.716 bytes) da 17.931 bytes de folga. Ao ritmo medido
(+46.725 bytes de nucleo entre 27/07 e 01/08, ~9.300/dia) isso dura menos de
duas semanas, e a conversa volta. Custo: 1 linha + comentario. E o mais barato
e o unico que nao resolve nada: mantem um numero que nao mede a carga real.

**C. Cortar payload ate caber.**
Campos SEM nenhum consumidor em `app/src/` ou `motor/` (grep por nome, fora de
comentario), com o custo medido sobre a carga inteira:

| campo | registros | gzip na carga real | so no nucleo |
|---|---:|---:|---:|
| `legado_de` | 5.870 | 27.926 | 14.511 |
| `historico` | 665 | 17.515 | 8.297 |
| `requires_parseado` | 20.083 | 13.127 | 6.312 |
| `remaster_de` | 424 | 1.332 | 570 |
| `gate_arquetipo_derivado` | 291 | 1.054 | 1.054 |

Qualquer um dos dois primeiros, sozinho, cobre os 3.040 de excesso. Custo: uma
entrada em `DESCARTAR` (`pipeline/emitir_app.py:41`) por campo. Contras, em
ordem de peso:

1. `requires_parseado` esta em `TRI_ESTADO` (`emitir_app.py:51`) por decisao
   escrita: `null` e resposta, nao vazio. Tirar contradiz essa decisao.
2. `historico` e o vinculo id-antigo -> id-novo que a fusao acabou de produzir
   (spec `2026-08-01-fusao-de-duplicata-de-nome.md`). Nao ha consumidor HOJE, e
   ele existe justamente para ficha salva com id aposentado -- cortar agora e
   apostar que a tela nunca vai precisar mostrar "era Exemplar Resiliency".
3. Cortar so pelo tamanho, com o teto ja revogado, e pagar auditabilidade por
   uma meta que ninguem mais tem.

Fora da lista, mas medido porque e o maior item cortavel: `requires_texto`
custa **48.786 bytes** (4.142 registros) e TEM consumidor
(`app/src/componentes/Prosa.tsx:38`). Ele e prosa, e a arquitetura ja diz que
prosa viaja sob demanda (`carregarBase.ts:96`); move-lo para o pacote de texto
renderia 16x o excesso. E refactor de app, nao ajuste de constante.

### Recomendacao

A, com B como paliativo se a decisao demorar. C so se o teto voltar a ser meta
de projeto -- e ai a decisao e do Igor, nao do teste.

---

## 2. `test_mechanized_e_derivado_de_grants` (pipeline/testes/test_portoes.py:144)

### O estado

A invariante da spec v1 e `mechanized == bool(grants)`. Quebrada em **12**
registros, por **tres** causas distintas, todas do mesmo tipo: passo derivado
que mexe em `grants` depois de a invariante ja ter sido calculada.

| # | registros | causa | linha |
|---|---:|---|---|
| 1 | 4 | grant somado por passo derivado, `mechanized` intocado | `pipeline/derivar_parcelas_de_dano.py:150-155` |
| 2 | 6 | fusao herda `grants` do perdedor, `mechanized` fica o do vencedor | `pipeline/fundir_duplicata_de_nome.py:202-208` |
| 3 | 2 | registro nasce com `mechanized: True` e `grants: []` literal | `pipeline/derivar_estatisticas_de_ator.py:90` |

Causa 1 -- `weapon_specialization` entra em `grants` e a linha seguinte
atualiza `prov`, mas nao `mechanized`:
`wb:class-feature/weapon-specialization`, `...-barbarian`,
`greater-weapon-specialization`, `psychic-weapon-specialization`.

Causa 2 -- os 6 sao `wb:feat/automatic-psychic-action`,
`wb:feat/exemplar-resilency`, `wb:feat/fautless-defense`,
`wb:equipment/comandants-scabbard`, `wb:equipment/submersible-helm`,
`wb:equipment/submersible-helm-greater`. Todos com
`historico[].passo == "fundir_duplicata_de_nome"`. A fusao move `grants` e move
a `prov` do campo (`fundir_duplicata_de_nome.py:206-208`) -- so nao move o
derivado que depende dele.

Causa 3 -- `wb:stat-formula/familiar` e `wb:stat-formula/eidolon`: o literal diz
`True`, o campo `grants` diz `[]`.

Antes da fusao eram 6 (causas 1 e 3); depois, 12. Medido rodando a mesma
checagem sobre `git show c2bcfab:pipeline/base/index.json`.

### Por que isso se repete

`reconciliar.py:297-311` deriva `mechanized` de `grants` uma vez -- e e o
**1o** dos 50 comandos `python3` do `build.sh`. Depois dele vem a fusao (20o),
`derivar_parcelas_de_dano` (37o), `derivar_estatisticas_de_ator` (45o) e o
`emitir_app` (49o). Todo passo posterior que toque `grants` tem de repetir a
regra na mao, e **quatro ja repetem**, cada um com o proprio comentario
explicando a mesma coisa:

```
pipeline/derivar_concessao_de_ator.py:213-217
pipeline/derivar_mecanica_dedicacao.py:177-182
pipeline/derivar_spellcasting_arquetipo.py:196-199
pipeline/unificar_efeitos.py:234
```

Sao 14 arquivos do pipeline que escrevem em `grants`. A invariante nao esta
guardada em lugar nenhum: esta copiada em quatro, esquecida em tres, e o teste
e o unico que percebe.

### As duas saidas, com o custo

**A. Consertar e manter o campo.**
Duas variantes:

- *Remendo por ponto*: 3 linhas, uma em cada um dos tres arquivos acima.
  Custo minimo, e a quinta copia da mesma regra. A sexta chega no proximo passo
  derivado que mexer em `grants`.
- *Derivar no fim, uma vez*: um passo final (ou uma chamada no `portoes.py`,
  que ja le a base inteira) que reaplica `mechanized = bool(grants)` sobre
  todos os registros e imprime quantos corrigiu. Custo: ~8 linhas + 1 passo no
  `build.sh`. Isso apaga a classe inteira do defeito, inclusive as 4 copias
  existentes, que passam a ser redundantes. Risco: o passo tem de rodar depois
  de TODOS os que tocam `grants` -- ordem errada e o mesmo bug de novo, agora
  com falsa sensacao de cobertura.

**B. Aposentar o campo pela spec v2.**
A spec v2 substitui `mechanized` por `grants_completos` + `requires_parseado`
(`test_portoes.py:146-147`, marcado `expectedFailure`). Tres medicoes que dizem que
a troca esta mais barata do que o marcador sugere:

1. Os dois campos de substituicao **ja existem em 20.083 de 20.083 registros**.
   O `mechanized` esta em 20.077. O que falta nao e dado, e decisao.
2. O app **nunca ve `mechanized`**: ele esta em `DESCARTAR`
   (`pipeline/emitir_app.py:41`) desde que o payload existe. Zero registros do
   payload tem o campo. Nao ha impacto de cliente.
3. Sobram dois consumidores, os dois em teste:
   - `motor/teste_motor.py:264` le a base de BUILD -- assercao real, 1 linha.
   - `app/src/fluxo.test.ts:585-590` filtra
     `r.mechanized === false && r.grants_completos === true` sobre o PAYLOAD.
     Como o payload nao tem o campo, o filtro sai vazio: **o teste passa sobre
     conjunto vazio hoje**. E o defeito que este projeto ja nomeou -- portao
     verde que nao mede nada. Ele nao vai piorar com a aposentadoria; ele ja
     esta quebrado e a aposentadoria e a ocasiao de conserta-lo (ler
     `pipeline/base/index.json`, ou reescrever a checagem em cima de
     `grants_completos`).

Custo total de B: tirar `mechanized` de `comum.mecanizacao()` e dos 4 pontos
que o repetem, tirar os dois testes de invariante e o `expectedFailure` do
`test_mechanized_nao_voltou`, e consertar os dois consumidores acima. E maior
que A em linhas e **menor em superficie**: some o campo derivado que todo passo
novo precisa lembrar de atualizar, que e a causa raiz das tres.

### Recomendacao

B, porque a causa e o campo existir duplicado com o que ja o descreve melhor.
Se B ficar para depois, entao A na variante "derivar no fim" -- nunca o remendo
por ponto, que e a quinta copia da regra.

O teste fica vermelho ate a decisao. Vermelho com causa conhecida e catalogada
e melhor que verde por complacencia -- e a mesma razao pela qual o
`expectedFailure` da spec v2 continua no lugar.
