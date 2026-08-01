# Prompt de correcao -- 13 itens (2026-08-01)

Prompt colavel, autocontido. Causas medidas contra `pipeline/base/index.json`
(20.083 registros) antes de escrever -- confirme, nao rediagnostique do zero.

O item 13 e de natureza diferente dos outros doze: e **regra nova**, nao defeito.
Esta na frente 0.

---

Voce vai consertar 12 defeitos e implementar 1 regra nova, reportados pelo Igor
no **Waybuilder**
(`/home/igor0/waybuilder`), um construtor de personagem de Pathfinder 2e com
houserule de multiclasse ao estilo D&D 5e. Pipeline Python funde tres fontes
numa base canonica de ~20 mil registros; o motor existe em duas implementacoes
(Python como oraculo, TypeScript no app); o front e um PWA client-side sem
backend, no ar em waybuilder.vercel.app.

Os 12 defeitos NAO sao 12 problemas. Sao **quatro defeitos estruturais**. Trate
por frente, nao por item, ou voce vai consertar o mesmo bug quatro vezes. O item
13 e regra nova, nao defeito: vem antes de tudo que mexe em modelo.

## Leia antes de tocar em qualquer coisa

1. `README.md` -- os quatro principios. Dois governam quase tudo aqui:
   **`requires` sugere e ordena, nunca bloqueia**, e **guardar decisao, nao
   resultado**.
2. `specs/2026-07-26-regras-multiclasse.md` -- as 23 regras.
3. `specs/2026-07-26-schema-personagem.md` -- o documento de personagem.
4. `docs/2026-08-01_avaliacao-arquitetura.md` -- o estado da verificacao. Voce
   vai depender dela, e ela esta furada em pontos nomeados.

## Regras de trabalho

- **SDD.** Item que muda MODELO (frente 1 inteira, item 12) exige spec aprovada
  antes de codigo. Defeito de dado ou de predicado (frentes 2 e 4) vai direto.
- **Todo conserto ganha uma trava.** O projeto tem seis mecanismos de
  verificacao e nenhum comando que rode todos -- foram medidos 31 de 95 testes
  vermelhos sem executor. Nao aumente a pilha: cada fix ganha assercao em
  `motor/teste_motor.py` (regra) ou `pipeline/portoes.py` (dado), citando o
  numero do item.
- **Mudanca cirurgica.** Defeito adjacente que voce notar vai para o TODO, nao
  para o commit.
- **A base em disco nao prova o pipeline.** Foi medido: ela diverge do rebuild
  em 3 registros. Se o fix depende de um campo, confirme que o campo sai do
  EXTRATOR.
- **Ordem do `build.sh` e fragil e nao testada** (36 restricoes so em
  comentario). Passo novo: leia os comentarios em volta e rode
  `comparar_bases.py` contra o HEAD depois.
- **Motor: os dois lados no mesmo commit** (Python + TS), fixtures regeradas.

---

# Frente 0 -- restricao de paridade para entrar em classe nova (item 13)

**REGRA NOVA, combinada na mesa e ainda NAO na spec.** Em nivel PAR o personagem
pode adicionar uma classe nova; em nivel IMPAR so pode subir uma classe que ja
tem.

**Isto nao e defeito de implementacao.** A regra 1 da spec
(`specs/2026-07-26-regras-multiclasse.md:39`) diz literalmente "A cada subida, +1
nivel numa classe existente **ou numa classe nova**", sem restricao de paridade
-- e `grep` por par/impar na spec so devolve a regra 12, que e sobre class feat.
O motor esta correto em relacao ao que foi especificado. Portanto: **altere a
spec primeiro**, com o bloco de "por que" ao lado, como todas as outras regras
tem. So depois o codigo.

## Cinco decisoes que a spec precisa tomar, e que o codigo nao pode inventar

1. **Nivel 1 e impar**, e a primeira classe nasce nele. A regra vale a partir do
   nivel 2, ou o nivel 1 e excecao nomeada? Recomendacao: nomeie a excecao no
   texto ("escolher a classe inicial nao e adicionar classe nova") em vez de
   deixar implicito -- senao a primeira implementacao bloqueia a criacao do
   personagem.

2. **Bloqueia ou sugere?** O principio 1 do README e explicito: `requires`
   sugere e ordena, **nunca bloqueia**. Mas isto nao e pre-requisito de feat, e
   regra estrutural da mesa. As duas leituras dao apps diferentes:
   - *bloqueia*: o slot de classe nova nao existe em nivel impar;
   - *sugere*: o slot existe e a escolha fora da paridade sai marcada como fora
     da regra, do mesmo jeito que feat sem requisito.

   **Pergunte ao Igor. Nao decida sozinho** -- e a unica regra do projeto que
   colide com um principio do README.

3. **Retroatividade.** Ficha salva que ja tem classe nova entrando em nivel
   impar continua valida ou passa a acusar? Ligado a (2).

4. **Interacao com a regra 23** (exclusao mutua entre nivel de classe X e
   dedicacao de X). Se o jogador quer entrar numa classe nova e o nivel e impar,
   o caminho que sobra e a dedicacao daquela classe -- que pela regra 23 depois
   **impede** pegar nivel de classe nela. A regra de paridade pode empurrar para
   um beco sem saida em silencio. A spec precisa dizer o que acontece: o app
   avisa antes? A regra 23 abre excecao? Ou e consequencia aceita e declarada?

5. **Interacao com a regra 12** (class feat a cada nivel **par** de personagem).
   O nivel par ja e o nivel carregado de decisao, e agora acumula tambem a
   entrada de classe nova. Confirme se e intencional (par = nivel de decisao
   grande) ou coincidencia. Se for intencional, escreva: e um argumento de
   design que sustenta a regra.

## Implementacao, depois da spec

- A paridade e avaliada **no nivel em que a escolha acontece**, nao no nivel
  atual do personagem. E a mesma infraestrutura da frente 1 (`_avaliando_em` +
  `nivel_personagem` no slot) -- **faca as duas juntas** ou a segunda desfaz a
  primeira. No modo planejamento, planejar entrar numa classe nova no nivel 6
  valida a paridade do 6, nao a do nivel atual.
- O slot de `nivel_de_classe` passa a recortar candidatos: em nivel impar, so
  classes ja em `ordem_de_classe` (`motor/motor.py:288`); em par, todas.
- Os dois lados, Python e TS, no mesmo commit.

**Trava:** teste que monte um personagem nivel 3 e afirme que `candidatos` do
slot de nivel de classe no 3 contem apenas as classes ja possuidas, e que no 4
contem todas. Mais um caso de nivel 1 provando que a criacao nao foi bloqueada.

---

# Frente 1 -- modelo temporal do personagem (itens 1, 3, 4, 10)

## O problema, como o Igor descreveu

- **(1)** Quer planejar o personagem acima do nivel em que ele esta. Liberar a
  visualizacao ate o nivel N, mas o personagem continua no nivel atual; so ao
  clicar "avancar para o nivel 4" e que as escolhas do 4 valem. Dano, CA,
  magias, proficiencias e gates so podem ser calculados ate o **nivel atual**;
  o resto e visualizacao para planejamento. O nivel atual aparece perto do nome.
- **(3)** Boost de atributo e treino de pericia estao todos empilhados no topo
  (o "nivel 0", perto do background). Tem que aparecer NO NIVEL em que sao
  ganhos -- ganhou no 3, a opcao esta no 3.
- **(4)** Aumento de pericia: peguei Natureza no nivel 1; no 5, ao liberar um
  aumento, preciso pegar Natureza de novo para subir de trained para expert. A
  regra de progressao de rank tem que ser avaliada NAQUELE nivel.
- **(10)** Pegar Commander no nivel 2 faz os feats de nivel 1 dessa classe
  aparecerem no bloco de nivel 1, como ganho retroativo. Deviam estar no 2.

## Causa

Os quatro sao o mesmo defeito: **o slot nao carrega o nivel em que nasce, e a
ficha so e derivada no estado final.** O item 10 e o espelho do item 3 -- o slot
e gerado por nivel de CLASSE e renderizado no nivel de PERSONAGEM.

## O que ja existe e nao foi aplicado aqui

`_avaliando_em` (`motor/motor.py:2832-2842`, `app/src/motor/personagem.ts:201`,
spec `2026-07-29-recorte-temporal-do-has.md`) ja implementa "avalie este
predicado como se estivessemos no nivel N", com teste passando
(`teste_motor.py:1071-1085`, Dueling Parry / Dueling Dance). Falta estender o
mesmo recorte para geracao de slot, boost, treino e rank de pericia.

## Sugestao de resolucao

**Escreva a spec primeiro.** Ela decide:

1. `nivel_atual` entra no documento de personagem (o schema nao tem o campo
   hoje). Documento antigo sem o campo assume `nivel_atual` = maior nivel com
   escolha registrada.
2. `nivel_planejado` e estado de UI, nao regra -- nao precisa entrar no schema
   se a tela puder derivar. Decida e escreva.
3. **Escolha acima do `nivel_atual` e gravada, mas nao entra no fold de
   efeitos.** Recomendacao forte: ela tambem NAO conta para `requires` de
   escolha posterior, senao o planejamento contamina o calculo e o jogador
   destrava coisa que nao tem.
4. Como a tela distingue o real do planejado.

**Depois, no motor:**

- Todo slot passa a carregar **dois** numeros: `nivel_classe` (o que a
  progressao da classe diz) e `nivel_personagem` (quando o jogador de fato
  ganha). A tela agrupa por `nivel_personagem` -- e isso sozinho conserta o
  item 10 e o item 3.
- `visao()` ganha recorte por nivel, reusando `_avaliando_em`: efeito de
  escolha com `nivel_personagem > nivel_atual` nao entra no fold.
- Aumento de pericia (item 4) passa a resolver o **rank alvo no nivel do
  aumento**: o candidato mostra o rank resultante (trained -> expert -> master
  -> legendary), respeitando o teto por nivel de personagem do PF2e. Pegar a
  mesma pericia de novo e o comportamento CERTO, e a tela precisa dizer isso --
  "Natureza (expert)" em vez de repetir "Natureza".

**Trava:** um teste que monte Guerreiro 1 -> Commander 2 e afirme que nenhum
slot de nivel 1 aparece depois da escolha do nivel 2; e um que pegue a mesma
pericia duas vezes e afirme `expert` no segundo.

**Pergunte ao Igor antes de fechar a spec:** ao recuar o `nivel_atual`, as
escolhas dos niveis acima ficam guardadas ou sao descartadas?

---

# Frente 2 -- predicado nao resolvido contra o estado (itens 6, 11)

## O problema

- **(6)** Ancestral Paragon libera um feat de ancestralidade. Deveria ser da
  ancestralidade E da heranca que o personagem pegou. Hoje pega a ancestralidade
  certa e **todas** as herancas.
- **(11)** No slot de arquetipo sem dedicacao previa aparecem opcoes validas
  (Goliath's Chard, Splinter of Finality, Ursaian Avenger) misturadas com
  invalidas (Dragon Disciple, Dual Weapon Reload, Harsh Judgment).

## Causa (item 6, medida e literal)

```json
"filtro": ["item:level:1", "item:category:ancestry",
  {"or": ["item:trait:{actor|system.details.ancestry.trait}",
          "item:trait:{actor|system.details.ancestry.adopted}",
          "item:trait:{actor|system.details.ancestry.versatile}",
          "item:trait:{actor|system.details.heritage.trait}"]},
  {"not": "item:trait:lineage"}]
```

As expressoes `{actor|...}` do Foundry vieram **como string literal nao
resolvida**. O motor nao sabe avalia-las, entao o `or` inteiro nao recorta.
E o "alvo dinamico" que o projeto ja sinaliza como pendente, aparecendo na tela.

## Sugestao de resolucao

Nao conserte o Ancestral Paragon. Conserte a **classe**:

1. Meca quantos registros tem `{actor|` em `filtro`/`requires`/`grants` --
   `grep -c '{actor|' pipeline/base/index.json` e por campo. Isso dimensiona o
   item de verdade.
2. Adicione termos de predicado que leiam o estado do personagem
   (`ancestry_trait`, `heritage_trait`, `adopted_trait`, `versatile_trait`),
   seguindo o padrao de `specs/2026-07-29-termos-de-predicado.md`.
3. Traduza as expressoes `{actor|system.details.*}` para esses termos em
   `pipeline/converter_rule_elements.py`, no mesmo lugar onde os outros Rule
   Elements ja sao convertidos.
4. O que nao tiver traducao continua sinalizado como pendente -- **nao invente
   default permissivo**. Filtro que nao resolve deve marcar o slot como
   "requisito nao verificado", nunca liberar tudo em silencio.

**Item 11 primeiro passo:** compare o `requires` de `Goliath's Chard` (aceito)
com o de `Dragon Disciple` (nao deveria aparecer). Se o segundo usa alvo
dinamico ou nao tem `requires`, e o mesmo defeito e o mesmo conserto. Se tiver
`requires` valido, entao o bug esta no filtro do slot de Free Archetype, que
provavelmente casa so por trait `archetype` em vez de exigir a dedicacao
correspondente.

**Trava:** assercao de que um Elfo com heranca X so recebe feats de nivel 1 com
o trait da ancestralidade e o da heranca escolhida -- e nao os de outra heranca.

---

# Frente 3 -- eixo de subclasse mal modelado (itens 5, 8, 9)

## Item 8 -- Kineticist obriga dois elementos no nivel 1

**Problema:** no nivel 1 o personagem deveria escolher um ou dois elementos (o
Kinetic Gate pergunta se e single-gate ou dual-gate). No app e obrigatorio pegar
os dois.

**Causa medida:**
```
kinetic-gate  nivel 1  escolhe: 2  opcoes: []  filtro: ["item:tag:kineticist-kinetic-gate"]
```
Dois defeitos empilhados: `escolhe` e **cardinalidade fixa em 2** (a regra pede
escolha de ESTRUTURA do gate, que por sua vez determina quantos elementos), e
`opcoes` esta **vazio**, dependendo de um filtro por tag que ninguem resolveu em
lista.

**Escopo real, medido:** 8 eixos tem `escolhe: 2` com opcoes vazias; 9 eixos no
total tem opcoes vazias. Consertar so o Kineticist deixa os outros sete.

**Sugestao:**
1. No pipeline, resolver `filtro: item:tag:*` em `opcoes` concretas -- e isso
   que faz o eixo existir na tela.
2. No modelo de eixo, permitir **cardinalidade derivada da escolha anterior**:
   o eixo `kinetic-gate` escolhe a estrutura (single/dual), e a estrutura abre
   N slots de elemento. Isso e escolha aninhada, e ja existe precedente --
   `specs/2026-07-31-escolha-aninhada-do-inventor.md`. Siga aquele padrao em
   vez de inventar um novo.

## Item 9 -- Oracle deixa escolher a maldicao

**Problema:** ao selecionar o misterio do oraculo, ele tambem deixa escolher a
maldicao -- mas o misterio ja define qual e.

**Causa medida:** o Oracle tem exatamente dois eixos, `mystery` e
**`outras-opcoes`**. Nao existe eixo `curse`. As `wb:class-feature/curse-of-*`
estao caindo no balaio `outras-opcoes`, que o PROJECT.md ja registra como
defeito conhecido ("balaio em 25 das 27 classes").

**Sugestao:** cada `mystery` ganha um `grants` para a sua `curse`, e as curses
saem do balaio. **Nao esconda por filtro de UI** -- o dado e que esta errado, e
esconder deixa o proximo consumidor da base com o mesmo problema. Se der,
aproveite e nomeie o resto do balaio do Oracle (o item ja esta no TODO).

## Item 5 -- Kineticist nao consegue pegar Extended Kinesis

**Causa medida:** colisao de homonimo, identica ao bug `reactive-strike` que o
projeto ja consertou.
```
extended-kinesis.requires = {all:[{has:"wb:feat/base-kinesis"}, {class_level:{kineticist:{">=":1}}}]}
wb:feat/base-kinesis   = nivel 4, traits:[archetype], exige kineticist-dedication
wb:action/base-kinesis = existe, traits:[impulse, kineticist, primal]
```
O predicado aponta para o feat de **arquetipo** (nv4). O Kineticist de classe
nunca recebe esse id -- ele recebe a acao.

**Sugestao:** reaponte o `has` para o atomo que o personagem de fato recebe, ou
faca o gate conceder o id que o predicado testa -- decida qual dos dois e a
regra e escreva. Antes disso, verifique se este item nao esta bloqueado pela
traducao dos 26 `predicate` da spec `2026-07-31-kind-action.md`, que o
PROJECT.md registra como **nao implementada** e que e a mesma causa do Campeao e
do Gunslinger sem reacoes.

**Trava dos tres:** um Kineticist nivel 1 single-gate existe, tem 1 elemento, e
`candidatos("class_feat")` inclui Extended Kinesis; um Oracle nivel 1 tem
exatamente uma curse e ela nao aparece como escolha.

---

# Frente 4 -- dado ausente ou nao concedido (itens 12, 7)

## Item 12 -- Additional Lore e feat de lore nao adicionam lore

**Problema:** feat geral que da lore adicional nao funciona. Deveria permitir
adicionar mais um item nas pericias, como o background ja faz muito bem.

**Causa medida:** `wb:feat/additional-lore` tem **`grants: []`** -- vazio. O feat
nao concede nada.

**O mecanismo que funciona ja existe**, do lado do background:
```json
"skill_training": {"skills": ["religion"], "lore": ["Goka Lore"]}
```

**Diferenca que exige modelo novo:** o background tem lore **fixa**; o feat tem
lore **escolhida pelo jogador**, texto livre ("Academia Lore", "Dragon Lore").
Isso e um slot de escolha aberta, que provavelmente nao existe hoje.

**Sugestao:** leia `specs/2026-07-29-pericia-de-lore.md` antes de inventar --
parte do modelo pode ja estar decidida la. Escreva spec para o slot de lore
livre (o que e persistido: o texto? um id sintetico? como a ficha soma o rank?),
depois implemente e faca `additional-lore` conceder esse slot. Varra os outros
71 feats com "lore" no id -- provavelmente varios tem o mesmo `grants` vazio.

## Item 7 -- feat de ancestralidade de AP nao aparece

**Nao reproduzido.** `grep` por `reincarn` devolve so
`wb:feat/reincarnated-companion` (nv14), `wb:feat/reincarnated-ridiculer`
(Season of Ghosts, nv5), `wb:trait/reincarnated` e `wb:ritual/reincarnate`.

**Pergunte ao Igor qual e o feat exato e de qual ancestralidade.** Se o feat nao
existir na base, e defeito de EXTRATOR (fonte nao coberta) e o conserto e no
pipeline; se existir, e defeito de FILTRO de slot e o conserto e no motor.
Diagnosticos opostos -- nao chute.

---

# Frente 5 -- remocao de Kingmaker (item 2)

**Problema:** todo conteudo de Kingmaker tem que sair -- Kingdom Feats,
backgrounds, skill feats, background feats, acampamento, ficha de reino,
assentamento, exercito, e as skills. Nada pode ser mantido: nao e compativel.

**Medido:** 125 registros citam Kingmaker.
```
por livro: Kingmaker Adventure Path 80 | Kingmaker Companion Guide 41 | Pathfinder Kingmaker 4
por kind:  feat 31 | trait 31 | equipment 23 | skill 16 | spell 10 | background 7 | weapon 6 | ritual 1
```

**Sugestao, com tres armadilhas:**

1. **Isto contradice o principio 4 do README** ("nada e descartado"). O Igor
   decidiu o contrario para este conteudo. **Registre a excecao por escrito**
   -- spec curta ou nota no README -- senao o proximo agente "conserta" a
   remocao de volta.
2. **A remocao acontece no PIPELINE**, num passo com nome proprio e posicao
   definida no `build.sh`. Nunca editando `index.json` a mao: o proximo
   `./build.sh` traz tudo de volta em silencio. Precedente exato: a fusao de
   duplicata de nome rodou fora do `build.sh` e seria revertida no rebuild
   seguinte.
3. **Decida o criterio antes de codar:** filtro por LIVRO (`source.book`) ou por
   TRAIT (`kingmaker`)? Sao conjuntos diferentes -- 4 registros vem de
   "Pathfinder Kingmaker" e podem nao carregar o trait. Provavelmente e a uniao
   dos dois.
4. **Depois de remover:** varra `requires`/`grants` dos ~20 mil registros atras
   de referencia orfa (31 traits e 16 skills podem ser citados por registro que
   fica) e rode o portao 3.
5. **A queda de contagem vai reprovar os portoes 4 e 11.** E intencional: use
   `--aceitar-queda` e registre em `censo_ausencias.json` com motivo. Sem isso o
   piso e rebaixado sem rastro.

---

# Ordem recomendada

1. **Item 2 (Kingmaker)** -- reduz o espaco de busca de todo o resto e nao
   depende de nada.
2. **Frente 2 (itens 6 + 11)** -- se a hipotese se confirmar e um conserto so,
   e resolve uma classe inteira de bugs de filtro.
3. **Frente 3 (itens 9, 8, 5)** -- nessa ordem: 9 e o mais simples e valida o
   entendimento do eixo; 8 e o mais estrutural; 5 pode estar bloqueado.
4. **Frente 0 + Frente 1 juntas (itens 13, 1, 3, 4, 10)** -- a maior. Uma spec
   so, ou duas specs irmas escritas na mesma sessao: as duas decidem "em que
   nivel a escolha acontece e o que ela vale", e separa-las faz a segunda
   desfazer a primeira. Por ultimo entre as frentes de codigo, porque mexem no
   schema do documento e todos os testes acima vao rodar em cima delas.
5. **Item 12** -- spec de slot de lore livre.
6. **Item 7** -- bloqueado ate o Igor nomear o feat.

**Antes de comecar a frente 0/1, leve ao Igor as tres perguntas abertas:** (a)
bloqueia ou sugere, na paridade; (b) ao recuar o `nivel_atual`, as escolhas dos
niveis acima ficam guardadas ou sao descartadas; (c) qual e o feat do item 7.

# Definition of done, por item

- Reproduzido **antes** do fix -- diga como.
- Causa nomeada com ancora (`arquivo:linha` ou id de registro).
- Fix cirurgico.
- Trava nova citando o numero do item.
- Mexeu no pipeline: `comparar_bases.py` contra HEAD, delta so o esperado.
- Mexeu no motor: Python e TS no mesmo commit, fixtures regeradas.
- Mexeu em modelo: spec atualizada **antes** do codigo, nao depois.

---

# Decisoes do Igor (2026-08-01) -- fecham 2 das 3 perguntas abertas

## (a) Paridade, item 13: SUGERE E MARCA -- nao bloqueia

O slot de classe nova EXISTE em nivel impar; a escolha fora da paridade sai
MARCADA como fora da regra, do mesmo jeito que feat sem requisito.

Consequencias que a spec tem de escrever:
- o principio 1 do README (`requires` sugere e ordena, nunca bloqueia) fica
  intacto -- a regra de paridade nao vira a primeira excecao dele;
- **retroatividade resolvida de graca** (decisao 3 da frente 0): ficha salva com
  classe nova em nivel impar continua VALIDA, so passa a acusar;
- o beco sem saida da regra 23 (decisao 4) deixa de ser beco: quem quer entrar
  numa classe nova em nivel impar pode, marcado, em vez de ser empurrado para a
  dedicacao que depois o impede de pegar nivel naquela classe;
- nivel 1 (decisao 1) continua exigindo excecao NOMEADA no texto -- escolher a
  classe inicial nao e "adicionar classe nova".

## (b) Recuo de `nivel_atual`, frente 1: AS ESCOLHAS ACIMA FICAM GUARDADAS

Escolha de nivel acima do `nivel_atual` permanece no documento, mas NAO entra no
fold de efeitos e NAO conta para `requires` de escolha posterior (a recomendacao
forte do item 3 da frente 1 vale). Coerente com o principio 3 do README --
guardar decisao, nao resultado.

## (c) Item 7 -- PENDENTE

Continua bloqueado ate o Igor nomear o feat e a ancestralidade. Diagnostico
depende disso e os dois caminhos sao opostos: se o feat nao existe na base e
defeito de EXTRATOR (conserto no pipeline); se existe, e defeito de FILTRO de
slot (conserto no motor).

## Correcoes de fato a este documento, medidas em 2026-08-01

- "31 de 95 testes vermelhos" -> sao **195 testes, 35 vermelhos** (100 testes de
  pipeline estavam fora da conta).
- "a base em disco diverge do rebuild em 3 registros" -> `comparar_bases.py` da
  **0 sumiu / 0 nasceu / 0 alterado**. O numero antigo vinha de quando o script
  estava morto com `RAIZ_GIT` e `REL` hardcoded do monorepo.
- "a fusao de duplicata rodou fora do build.sh e seria revertida no rebuild" ->
  ja esta wired como passo 7a do `build.sh`.

## Colisao de ordem a resolver antes do item 2 (Kingmaker)

Remover os 125 registros de Kingmaker derruba os portoes 4 e 11 de novo. A linha
de base esta sendo fixada AGORA em total=20.083. Ou o Kingmaker sai antes de
fixar, ou a linha de base e fixada duas vezes -- de proposito e registrado, nunca
como efeito colateral.
