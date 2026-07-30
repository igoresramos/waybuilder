---
spec: divindade-na-ficha
project: waybuilder
version: 1
status: aprovada
created: 2026-07-30
todo: 98
---

# Spec -- 488 divindades estruturadas e nenhum consumidor

## O problema

`deity` nao aparece **uma vez** em `motor/motor.py`. A base tem 488 divindades
e 61 dominios, e nada os le.

Nao e dado pobre -- e o oposto. Cada divindade traz, em campo proprio:

| campo | preenchido | forma |
|---|---:|---|
| `divine_font` | 479 | `["heal"]` (175), `["harm"]` (167), os dois (137) |
| `domains` | 479 | `{"primary": ["wb:domain/death", ...], "alternate": [...]}` -- ids reais |
| `favored_weapon` | 479 | `["wb:weapon/dagger"]` -- ids reais |
| `divine_attribute` | 479 | `["con", "wis"]` |
| `sanctification` | 373 | holy / unholy |
| `edict`, `anathema` | 481 | prosa |

## O tamanho, medido no residuo de pre-requisito

**54 clausulas** de `requires_residuo` falam de divindade, fonte ou dominio.
Separadas por familia:

| familia | clausulas | exemplo |
|---|---:|---|
| divindade nomeada | 11 | `worshipper of Lamashtu`, `deity is Achaekek` |
| fonte divina | 13 | `healing font`, `deity who grants harm divine font` |
| segue alguma divindade | 5 | `you follow a deity`, `can't have a patron deity` |
| dominio | 3 | `deity who grants the cold, fire, nature, or travel domain` |
| arma favorita / pericia divina / santificacao | 6 | `trained with your deity's favored weapon` |
| alinhamento | 5 | `you follow a good-aligned deity` |
| ruido (a mesa resolve) | 11 | `Worshiper of a specific deity` |

Fora o alinhamento, que segue recusado (conceito que o Remaster aboliu; na base
`alignment` so existe em 33 divindades legadas), **38 clausulas** dependem
apenas da escolha nao existir.

E o efeito hoje e visivel na ficha: `Healing Hands` exige fonte de cura e e
oferecido a qualquer Clerigo, inclusive ao que escolheu `harm`.

## A causa

A escolha existe no jogo desde o nivel 1, e a base ate sabe disso -- ela tem
`wb:class-feature/deity-cleric` e `wb:class-feature/deity-champion`. Mas as
duas chegam por rotas diferentes e nenhuma vira escolha:

- Clerigo: dentro do balaio `outras-opcoes` de nivel 1 (o item 69);
- Campeao: em `progressao`, como feature concedida.

O eixo `doctrine` do Clerigo **nao** cobre: ele so tem cloistered, warpriest e
battle-creed.

## As decisoes

1. **A divindade e um eixo de sub-escolha**, com as 488 opcoes, nivel 1, nas
   duas classes que a exigem. Nao inventa maquinaria: `slots_de_subclasse` ja
   generaliza sobre qualquer `eixo`, e a escolha ja e persistida em
   `escolhas[].slot == "subclasse"`. Um id de divindade so aparece no bloco de
   divindade, entao nao ha risco de uma escolha satisfazer outro eixo.
2. **Quatro termos novos**, todos lendo a divindade escolhida:
   `deity` (e esta, ou uma desta lista), `has_deity`, `deity_font` e `domain`.
3. **A fonte NAO vira sub-escolha nesta versao.** Para 342 das 479 divindades
   com fonte declarada (175 so heal + 167 so harm) a resposta ja esta
   determinada pela divindade, e o termo responde com certeza. Para as 137 que
   permitem as duas, o motor **nao reprova** -- principio zero: ele nao sabe
   qual o jogador escolheu, e recusar seria afirmar o que nao se sabe. O
   motivo fica dito no resultado.
4. **A ficha mostra a divindade**: nome, fonte, dominios, arma favorita e
   atributo divino. Sem isso a escolha nao muda nada visivel, que e o defeito
   que este item descreve.

## O que esta spec NAO resolve, e declara

- **A sub-escolha da fonte para as 137 divindades ambiguas.** Precisa de um
  eixo cujas opcoes dependam da escolha anterior, e nenhum eixo da base filtra
  hoje. E o proximo passo natural do item 98.
- **Divindade para quem NAO e Clerigo nem Campeao.** `you follow a deity` (4
  clausulas) so pode ser respondido com `false` para as outras classes, e e o
  que o termo faz -- mas um Monge que segue uma divindade e legitimo em PF2e.
  Um eixo opcional universal e decisao de produto, nao de motor.
- **Alinhamento** (5 clausulas): recusado de novo, pelo mesmo motivo de sempre.
- **`divine_attribute` nao entra no atributo-chave da classe.** O Clerigo usa
  Sabedoria por regra propria; o campo diz outra coisa (o atributo da
  divindade) e ligar um no outro sem medir seria chute.
- **Dominio nao concede magia de dominio.** `domains` vira consulta, nao
  concessao: os 61 registros `domain` tem `grants` vazio.

## Como se prova que funciona

1. Um Clerigo 1 sem divindade escolhida acusa `falta escolher deity` e
   `slots_abertos()` traz o slot com 488 opcoes.
2. Escolhida `wb:deity/pharasma` (fonte `["heal"]`):
   - `Healing Hands` (exige `healing font`) fica ATENDIDO;
   - `Harming Hands` (exige `harmful font`) fica NAO atendido, com o motivo
     dizendo qual fonte a divindade concede;
   - `Chosen of Lamashtu` (exige adorar Lamashtu) fica NAO atendido.
3. Escolhida `wb:deity/aakriti` (permite as duas), `Harming Hands` e
   `Healing Hands` ficam os DOIS atendidos, e o motivo registra que a
   sub-escolha nao esta modelada.
4. `Domain Focus` e `Environmental Grace` respondem pelo `domains` da
   divindade escolhida, primary ou alternate.
5. Um Guerreiro nao atende `you follow a deity`.
6. `visao()` traz `divindade` com nome, fonte, dominios e arma favorita.
7. Paridade Python/TS, e o diff de fixtures lido -- toda ficha de Clerigo e
   Campeao passa a ter um slot aberto a mais, e isso e correto.
