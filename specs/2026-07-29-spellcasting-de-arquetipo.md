---
spec: spellcasting-de-arquetipo
project: waybuilder
version: 1
status: aprovada
created: 2026-07-29
---

# Spec -- spellcasting de arquetipo

## O problema

21 dedicacoes prometem conjuracao na propria prosa (`"you can cast spells like
a wizard"`) e **nenhuma entrega nada** na ficha. Sob Free Archetype -- que a
regra 2 mantem sempre ligada -- essa e a rota de conjuracao mais comum de um
personagem nao-conjurador, e ela e invisivel para o motor.

Medido na base (levantamento de 2026-07-29):

| | numero |
|---|---|
| feats com trait `dedication` | 226 |
| que citam magia na prosa | 77 |
| que **concedem** conjuracao (ancora em "you cast"/"you gain a spell repertoire") | **21** |
| feats da cadeia Basic/Expert/Master | **67**, em 21 arquetipos |
| desses, com algo estruturado em `grants` | **zero** |

## O que ja existe, e barateia tudo

**A tabela RAW ja esta no motor**, citada verbatim da regra "Spellcasting
Archetypes" e usada desde 2026-07-27 como piso da regra 21:

```python
RANK_DEDICACAO = [(20, 8), (18, 7), (16, 6), (14, 5), (12, 4),
                  (8, 3), (6, 2), (4, 1)]
```

Ela responde "que rank a rota gratuita entrega no nivel N". O que falta nao e a
tabela: e **saber que ESTE personagem esta nessa rota**, e ate onde ele foi.

Tambem existe o formato de saida: `visao().conjuracao` ja e uma lista, e cada
entrada ja carrega `tradicao`, `tipo`, `slots`, `max_rank_do_slot`,
`rank_efetivo`, `elevacao` e `dc`. A conjuracao de arquetipo entra **na mesma
lista**, e nao numa estrutura paralela.

## Parte 1 -- dado: `grant_spellcasting`

Termo novo em `grants`, na dedicacao:

```json
{"grant_spellcasting": {
   "tradicao": "arcane",
   "tipo": "prepared",
   "cadeia": "wb:archetype/wizard",
   "truques": 2
}}
```

| campo | valor | por que |
|---|---|---|
| `tradicao` | `arcane`/`divine`/`occult`/`primal`, ou `escolha` | 15 das 21 fixam; 5 dependem de outra escolha |
| `tipo` | `prepared` / `spontaneous` | muda o que a tela pergunta, nao os slots |
| `cadeia` | id do arquetipo cujos Basic/Expert/Master valem | **nao e sempre o proprio**: `spellshot-dedication` diz em prosa que "counts as the wizard archetype for the benefits of Basic Wizard Spellcasting" |
| `truques` | quantos cantrips a dedicacao da | RAW: 2 na maioria |

Quando a tradicao depende de outra escolha (`sorcerer-dedication` usa a do
bloodline; `witch-dedication`, a do patron; `bloodrager`, arcana ou divina a
escolher), `tradicao: "escolha"` mais `de: "<eixo>"`. O motor resolve pelo eixo
de subclasse ja escolhido; sem escolha, **avisa** em vez de assumir -- mesmo
tratamento do grau do companheiro.

### De onde vem

Passo novo, **7g**, `derivar_spellcasting_arquetipo.py`, na mesma janela dos
passos 7e e 7f: depois da prosa (5) e depois da fusao (7).

Regra de emissao, a mesma dos outros dois: **so com o sujeito ancorado em
"you"**, e so quando a tradicao resolve. Uma varredura crua por "spell" nas
dedicacoes traz 77 registros; a ancora derruba para 21, e as 56 quedas sao
legitimas (citam magia para dar resistencia, para calcular DC, ou para
condicionar um feat posterior).

Tres casos que o passo tem de tratar por nome, porque a prosa nao basta:

- **`spellshot-dedication`** aponta a cadeia do Wizard;
- **`red-mantis-assassin`** e **`gelid-shard`** tem cadeia Basic/Expert/Master
  (com outros nomes: "Red Mantis Magic", "Snowcasting") mas o feat de entrada
  **nao tem trait `dedication`** -- se o passo filtrar so por trait, os dois
  ficam de fora tendo cadeia funcional;
- **`Master Summoner Spellcasting`** tem `archetype: null` enquanto Basic e
  Expert do mesmo arquetipo apontam para `wb:archetype/summoner`. Defeito de
  tagging na fonte; o join por `archetype` tem de tolerar.

Fora do escopo, declarado: `captivator`, `ghost-hunter` e `soul-warden` prometem
**magia inata fixa**, nao progressao de slots. Modelo diferente; ficam na divida.

## Parte 2 -- motor

### O rank vem do FEAT que o personagem tem, nao do nivel dele

A tabela `RANK_DEDICACAO` diz o que a rota entrega **quando o personagem pega
os feats na hora certa**. Isso e o piso teorico da regra 21 e continua valendo
para ela. Para a ficha real vale o que ele PEGOU:

| feat mais alto da cadeia | teto de rank |
|---|---|
| so a dedicacao | 0 (so cantrips) |
| Basic Spellcasting | 3 |
| Expert Spellcasting | 6 |
| Master Spellcasting | 8 |

E dentro do teto, o rank concedido segue a tabela pelo nivel de PERSONAGEM.
Slots: **1 de cada rank**, do 1 ate o teto vigente -- que e o que a regra RAW
descreve e o que a tabela ja codifica.

### Regra 18: arquetipo roda RAW puro

`elevacao: 0` e `rank_efetivo == max_rank_do_slot` na entrada de arquetipo. A
elevacao da regra 17 e da conjuracao **de classe**; aplica-la aqui daria ao
arquetipo o beneficio da casa em cima do beneficio do livro.

### DC e ataque

Regra 3, como todo o resto: `10 + nivel_de_PERSONAGEM + rank`. A proficiencia
vem `trained` da propria dedicacao e sobe com os feats da cadeia, se a prosa
disser.

### Focus pool

A regra 22 nao muda: pool unico, teto 3. Dedicacao que da magia de foco entra
no mesmo pool.

## Parte 3 -- app

**Correcao de premissa (2026-07-29):** eu escrevi aqui que "a ficha ja tem o
bloco de Conjuracao". Nao tem. O bloco existe em `src/telas/Ficha.tsx`, que
**nao e usado por ninguem** -- a ficha viva e `PainelDireito.tsx`, e ela nao
mostra conjuracao NENHUMA, nem a de classe. O motor calcula desde sempre e a
tela nunca mostrou.

Entao a parte 3 e maior do que parecia, e cobre as duas rotas:

- aba **Magia** no `PainelDireito`, com uma entrada por linha de
  `visao().conjuracao`;
- por entrada: tradicao, tipo, DC e ataque, truques, e os slots por rank;
- a de CLASSE mostra a elevacao da regra 17 quando houver (`+N ranks`), porque
  e o numero mais surpreendente da houserule;
- a de ARQUETIPO aparece marcada como tal e **sem** elevacao -- o jogador
  precisa distinguir os slots que elevam dos que nao elevam, porque isso muda a
  decisao de gastar.

## Como se prova que funciona

1. Um `Fighter 8` com `Wizard Dedication` + `Basic Wizard Spellcasting` tem, em
   `visao().conjuracao`, uma entrada arcana com slots de rank 1 a 3, `elevacao:
   0` e DC = 10 + 8 + trained.
2. O mesmo Fighter **sem** o feat Basic tem so os 2 cantrips: a dedicacao
   sozinha nao da slot.
3. Um `Fighter 20` com a cadeia completa chega ao rank 8 -- e nao ao 10.
4. Um `Wizard 2 / Fighter 18` (rota de classe) **nao** ganha entrada de
   arquetipo: a regra 23 ja proibe a dedicacao da propria classe.
5. `sorcerer-dedication` sem bloodline escolhido **avisa** e nao inventa
   tradicao.
6. A regra 21 continua verde nos 204 pares -- a mudanca nao mexe em
   `rank_de_dedicacao`, que e o piso, e sim no que a ficha real recebe.
7. As 21 fichas de exemplo derivam identicas nas duas linguagens.
