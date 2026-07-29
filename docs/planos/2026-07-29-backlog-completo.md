# Waybuilder -- plano de execucao do backlog inteiro

> **Para quem executa:** este plano e para execucao autonoma continua. Cada fase
> termina em VERDE nas quatro camadas e em commit. Nao pedir confirmacao entre
> fases -- as decisoes ja estao tomadas na secao "Contrato de autonomia".

**Objetivo:** fechar os 54 itens abertos do TODO, na ordem em que cada um deixa
de bloquear os outros, sem quebrar o que ja esta verde.

**Arquitetura:** o projeto tem quatro camadas de prova e todas valem sempre --
9 portoes de qualidade da base (`pipeline/portoes.py`), o oraculo Python
(`motor/teste_motor.py`, 132 assercoes), o porte TypeScript contra o gabarito do
Python (`app/`, 113 testes) e a verificacao no navegador
(`app/verificacao/*.mjs`). Nada e "pronto" sem as quatro.

**Stack:** Python 3.12 (pipeline + motor oraculo), TypeScript + React + Vite
(app PWA), Playwright (verificacao de navegador e sonda do Pathbuilder).

## Restricoes globais

Valem para TODA tarefa deste plano, sem repetir em cada uma:

- **Spec antes do codigo, medicao antes da spec.** Nenhuma linha de codigo sem
  spec em `specs/`. Nenhuma spec sem numero medido -- premissa nao medida ja
  derrubou o plano tres vezes neste projeto (61 dedicacoes, 178 feats, nomes de
  dedicacao do remaster).
- **Principio zero:** o motor nunca reprova sobre o que nao sabe avaliar. Termo
  desconhecido, requisito nao parseado e prosa narrativa MOSTRAM e MARCAM, nunca
  bloqueiam. Requisito que o motor nao avalia vive em `requires_residuo`.
- **Paridade Python/TS e inegociavel.** Todo termo novo mexe em TRES lugares: o
  metodo no Python, o metodo no TS e a linha do `switch` do TS. A terceira e a
  que se esquece -- ja custou 14 fichas.
- **Toda mudanca de motor regenera os fixtures** (`python3
  motor/gerar_fixtures.py`) e o diff dos fixtures e LIDO antes de commitar: se o
  diff sair de onde a mudanca justifica, e defeito, nao e ruido.
- **Artefato nasce dentro do projeto.** Nada em `/tmp`, `~`, `Downloads`.
  Relatorio em `docs/`, spec em `specs/`, comparacao em `docs/comparacao/`.
- **Agentes em paralelo que ESCREVEM usam `git worktree`.** Dois agentes no
  mesmo checkout fragmentam arquivo -- ja aconteceu duas vezes. Agente de
  MEDICAO (so leitura) pode rodar no checkout normal, varios ao mesmo tempo.
- **Commit por tarefa,** conventional commits, mensagem dizendo o numero medido
  antes e depois. Nunca `git add -A`: staging seletivo por caminho.
- **Nunca pular hook de pre-commit.**
- **Ao fim de cada fase: push.** Codigo sem push ja foi perdido neste ecossistema.

## Contrato de autonomia

O pedido e "faz tudo sem parar". Onde o item pede DECISAO e nao trabalho, sigo o
default abaixo, registro em `LOG.md` e sigo em frente. Todo default e reversivel
-- esta em commit proprio e pode ser desfeito sem tocar no resto.

| item | decisao | default que eu tomo | por que |
|---|---|---|---|
| 46 | cortar arquetipo de multiclasse? | **nao cortar**; so medir (a)-(d) e reportar | cortar remove 27 dedicacoes + 195 feats e tira o chao da regra 21, que usa a dedicacao de conjuracao como piso. Irreversivel na pratica; medir e barato |
| 47 | qual das tres leituras de "a regra serve pra dedicacao tambem" | **(a)** -- regra 17b vale tambem no slot de arquetipo | foi a pergunta que voce deixou aberta duas vezes, e (b) ja caiu hoje. Se estiver errado, e um `if` |
| 35 | 3 registros sem fonte nenhuma | **manter com divida declarada** | remover perde conteudo que existe; manter so mente se ninguem contar, e o registro conta |
| 44 | os 35 PDFs | **usar** (estao em disco neste PC) | nao ha decisao: a premissa de perda era falsa |
| 16 | licenciamento antes de publicar | **adiar** | a spec da fatia 1 diz que o app nao vai ser publicado. Reabrir se mudar |
| 31 | i18n en/pt-BR | **por ultimo**, como voce mandou | so faz sentido com o app fechado |

**Onde eu PARO e pergunto, mesmo neste modo:** se uma medicao contradisser a
premissa de uma decisao sua ja registrada (ex: descobrir que a regra 17b em slot
de arquetipo quebra 40 fichas). Ai a decisao volta pra voce com o numero na mao.

---

## Fase 0 -- reconstruir a fila (bloqueia todo o resto)

Sem isto, as fases seguintes trabalham sobre numeros de tres sessoes atras. Ja
achei quatro itens velhos hoje sem procurar.

### Tarefa 0.1: consumir a auditoria dos tres agentes

**Arquivos:**
- Criar: `docs/2026-07-29_auditoria-todo.md`

- [ ] Colher os relatorios dos tres agentes de auditoria (motor: ids 3, 40, 41,
      65, 66, 71, 72, 74, 75, 77, 78, 83; base: 33, 34, 36, 37, 38, 52, 53, 54,
      55, 56, 59, 60, 61, 69, 70, 91; escopo: 7, 8, 9, 10, 13, 16, 18, 19, 22,
      23, 35, 42, 43, 44, 46, 47, 68, 73, 79).
- [ ] Para cada item, gravar no relatorio: classificacao (VALIDO / JA RESOLVIDO
      / PARCIAL / IMPRECISO / SOBREPOSTO / DECISAO / OBSOLETO), o numero medido
      HOJE e o numero que o item afirmava.
- [ ] **Nao confiar cego no agente.** Todo item que o agente marcar JA RESOLVIDO
      ou IMPRECISO eu confiro pessoalmente antes de fechar -- foi assim que
      peguei que a "premissa das 61 dedicacoes" estava errada.

**FEITO em 2026-07-29.** A auditoria completa esta em
`docs/2026-07-29_auditoria-todo.md`, com prova por item. Resultado:

| | itens |
|---|---:|
| abertos antes | 54 |
| **fechados** | **15** (3, 7, 8, 9, 16, 23, 35, 36, 37, 44, 54, 56, 66, 71, 74) |
| fundidos | 2 (41 -> 78, 33 -> 55) |
| **abertos depois** | **37** |

Sete itens mentiam o numero. Os que mudam trabalho:

- **40** dizia "175 de 176 sub-escolhas sem efeito"; sao **114 de 418 ja
  aplicadas** (27%). O mecanismo parou de ser o problema -- a extracao continua.
- **52** dizia 812 campos com `prov` ruim; sao **13**.
- **69** dizia 25 de 27 classes com o balaio; sao **16 de 27**.
- **78**: patron e eidolon ja tem `grants`, mas nenhum carrega tradicao -- o
  defeito central persiste com outro contorno.
- **60** precisa de re-medicao com a metodologia original: as categorias de hoje
  nao mapeiam 1:1 com as do item.

Dois itens mudaram de natureza e precisam de titulo novo antes de virar
trabalho:

- **18** deixa de ser "3 ausencias pontuais" e vira **"heritage so e enumerado
  pelo Foundry, nunca pelo AoN"** -- causa, nao sintoma.
- **59** ficou maior: os gaps originais cairam e outros nasceram (724 com
  `grants_completos == False`), mas o achado grave e que **14.247 registros (72%
  da base) nao emitem o campo** -- equipment, weapon e class-feature inteiros --
  e **nenhum portao cobra**. Vira tarefa de portao antes de tarefa de conteudo.

### Tarefa 0.2: fechar, fundir e reescrever os itens

**Arquivos:**
- Modificar: `TODO.md`

- [ ] Fechar (prioridade `concluido`, com a evidencia no texto) todo item que a
      auditoria provou resolvido.
- [ ] Fundir os pares confirmados: **41 dentro do 78** (mesma tradicao de
      conjuracao; o 78 mediu o que o 41 levantou) e **90 dentro do 74** (mesma
      falta de higiene de boost; a bancada e sintoma).
- [ ] Item 3: separar. A parte do companheiro caiu hoje; o que sobra e "predicado
      fala de subclasse", que o termo `subclass` (199 usos) ja responde --
      confirmar e fechar ou reescrever com o que resta.
- [ ] Reescrever a prioridade dos que sobrarem com UM criterio explicito, dito no
      topo do arquivo: **alta = bloqueia outro item ou entrega numero errado na
      ficha do jogador; media = buraco de conteudo; baixa = polimento**. Hoje ha
      18 altas, o que nao ordena nada.

### Tarefa 0.3: por o TODO no padrao do Tartarus

**Arquivos:**
- Modificar: `TODO.md`

O `_Padrao/GUIA.md` manda `desc` + `date` (obrigatoria) + `priority`. O arquivo
usa `texto` + `prioridade` + `id`, e por isso o hook do panorama
(`tartarus-panorama.sh:43` conta `- desc:`) reporta `todo:0` num projeto com 54
itens abertos.

- [ ] Renomear `texto` -> `desc` e `prioridade` -> `priority` em todos os itens.
- [ ] **Manter o campo `id`** -- specs (`todo: 88`) e mensagens de commit
      ("item 89") referenciam por numero.
- [ ] Preencher `date` com a data de criacao/ultima medicao de cada item.
- [ ] Mover os 38 itens `concluido` para uma secao `promoted:` ou para
      `docs/2026-07-29_todo-concluidos.md`, para o panorama contar so trabalho
      vivo. Sao 40% do arquivo.
- [ ] **Prova:** `bash ~/.claude/scripts/tartarus-panorama.sh` (ou rodar o awk do
      hook) e ver `waybuilder | ... | todo:<numero de abertos>`, nao `todo:0`.

### Tarefa 0.4: higiene das specs

**Arquivos:**
- Modificar: `specs/2026-07-27-slots-e-candidatos.md`,
  `specs/2026-07-28-app-fatia-1.md`, e as 4 specs de frontmatter em prosa

- [ ] As duas specs acima ainda dizem `Status: proposta` e o que elas descrevem
      ja esta no ar. Marcar `aprovada` com a data em que passou a valer, ou
      declarar explicitamente o que da spec NAO foi implementado.
- [ ] Uniformizar o frontmatter: 8 specs usam YAML (`spec:`, `status:`,
      `todo:`), 4 usam prosa (`Status: proposta`). Converter as 4.
- [ ] Ligar cada spec ao item de TODO (`todo: N`). Hoje 8 de 12 nao tem link.

**Verde da fase:** as quatro camadas + o panorama contando os itens.
**Commit:** `chore(waybuilder): auditoria do backlog -- N itens fechados, M fundidos, TODO no padrao`

---

## Fase 1 -- o motor mente na ficha (maior dano por linha)

Tudo aqui entrega numero errado ou opcao errada para o jogador HOJE, e nenhum
depende de reemitir a base.

### Tarefa 1.1: termo `spellcasting_tradition` (item 89)

99 clausulas em 27 arquetipos, sem handler em nenhum dos dois motores. Pelo
principio zero elas liberam sempre -- 6 dedicacoes de conjuracao aparecem para
Guerreiro e Ladino. Os dois motores erram IGUAL, entao o teste de paridade e
cego: so um teste de comportamento pega.

**Arquivos:**
- Criar: `specs/2026-07-29-termo-spellcasting-tradition.md`
- Modificar: `motor/motor.py` (metodo `_termo_spellcasting_tradition`),
  `app/src/motor/personagem.ts` (metodo + **linha do switch**),
  `motor/teste_motor.py`

- [ ] Medir antes: quais das 10 classes conjuradoras tem tradicao resolvivel
      hoje (Feiticeiro, Invocador e Bruxa nao tem -- item 78).
- [ ] Escrever a spec com a decisao do caso nao resolvivel: tradicao
      desconhecida **nao reprova** (principio zero), e o motor MARCA.
- [ ] Teste no oraculo: Clerigo 2 atende `{"spellcasting_tradition": "divine"}`;
      Guerreiro 6 NAO atende nenhuma das quatro; Feiticeiro marca em vez de
      reprovar.
- [ ] Rodar e ver falhar. Implementar nos dois motores. Rodar e ver passar.
- [ ] Regenerar fixtures, ler o diff, conferir que so mexe em arquetipo de
      conjuracao.
- [ ] Rodar a comparacao com o Pathbuilder e confirmar que as 6 dedicacoes
      (`Cathartic Mage`, `Necrologist`, `Shadowcaster`, `Soulforger`,
      `Time Mage`, `War Mage`) sairam da divergencia.

### Tarefa 1.2: alinhar a bancada de comparacao (item 90)

**Encolheu na auditoria.** O item 74 esta RESOLVIDO -- a ficha sem boost
declarado JA avisa ("0 declarado(s) de 9 a que o personagem tem direito", com as
fontes). Sobra so a bancada, que monta um personagem com 9 boosts nao atribuidos
e o compara com um que tem STR 16.

**Arquivos:**
- Modificar: `motor/comparar_pathbuilder.py`

- [ ] Espelhar no `personagem_equivalente` a atribuicao real do Pathbuilder
      (medida em `docs/comparacao/estado-pathbuilder-fighter-nv2.json`: STR 16,
      DEX 12, CON 12, e Acrobatics/Athletics/Stealth/Thievery treinadas).
- [ ] Rodar a comparacao e medir quanto dos 17 pontos de atributo e dos 18 de
      pericia era artefato da bancada.
- [ ] O que sobrar depois disso e **diferenca de modelo declarada**: o
      Pathbuilder conta escolha pendente como alcancavel, nos avaliamos o estado
      atual e marcamos. Registrar no relatorio, nao "consertar".

### Tarefa 1.3: `grant_feat` de background (item 70)

400 dos 926 alvos sao dict Python stringificado
(`"{'name': 'Hobnobber', 'foundry_uuid': ...}"`), mais 76 nome cru. Todos de
background. O motor avisa e nao aplica -- entao nenhum background entrega o feat
que promete.

**Arquivos:**
- Criar: spec **grant-feat-de-background** (a criar em `specs/`)
- Modificar: `pipeline/unificar_efeitos.py:76`
- Rodar: `pipeline/resolver_referencias.py` (ja sabe resolver `name` +
  `foundry_uuid`)

- [ ] Conserto na origem: `grants_de_background` extrai `name`/`foundry_uuid` e
      resolve para id `wb:`, em vez de `str(x)`.
- [ ] Reemitir a base e conferir o portao 3.
- [ ] Prova ponta a ponta: um Barkeep sai com Hobnobber em `concedidos`, e o feat
      **nao** aparece mais como candidato no slot de skill feat.
- [ ] Confirmar na comparacao que `Hobnobber` saiu da divergencia.

### Tarefa 1.4: `_termo_has` sem recorte temporal (item 65)

Pegar `Quick Shot` no nivel 2 satisfaz requisito de um feat de nivel 1 -- o termo
soma `escolhas` inteiras sem olhar `em`. Reproduzido na auditoria: a ordem
ILEGAL devolve `True` igual a legal.

**Encolheu na auditoria:** a outra metade do item (o `disponiveis()` por kind) ja
virou `candidatos(slot, em)` + `slots_abertos()`.

**Arquivos:**
- Criar: spec **recorte-temporal-do-has** (a criar em `specs/`)
- Modificar: `motor/motor.py:1822` (`_termo_has`),
  `app/src/motor/personagem.ts`, `motor/teste_motor.py`

- [ ] Teste do caso reproduzido: `Archer Dedication` no nivel 4 exigindo
      `Quick Shot`, com o `Quick Shot` pego no nivel 2 -> legal; pego DEPOIS ->
      nao satisfaz.
- [ ] Rodar e ver falhar. Implementar nos dois motores. Rodar e ver passar.
- [ ] Regenerar fixtures e ler o diff.

**Sairam desta fase pela auditoria:** item 71 (gate de nivel -- ja usa `any`
sobre todos os traits, 123 feats) e item 66 (conjuracao por dedicacao -- entrou
hoje as 16:06).

**Verde da fase:** quatro camadas + comparacao com o Pathbuilder re-rodada, com
o total de divergencia medido antes e depois.
**Push ao fim da fase.**

---

## Fase 2 -- a base perde mecanica em silencio

Nenhum destes muda regra: mudam o que a base ENTREGA. Todos exigem reemissao
(`WB_REEXTRAIR=1` quando mexer em extrator).

### Tarefa 2.0: o portao que falta (item 59, parte nova)

O achado mais grave da auditoria e de VISIBILIDADE, nao de conteudo: **14.247
registros (72% da base) nao emitem `grants_completos`** -- equipment 6.122, feat
3.849, weapon 1.042, class-feature 841 --, e **nenhum portao cobra**. Os 1.564
originais foram consertados e 724 novos apareceram sem ninguem ver.

Isto vem ANTES de qualquer conserto de conteudo desta fase: sem o portao, o
proximo conserto some do radar do mesmo jeito.

**Arquivos:**
- Modificar: `pipeline/portoes.py` (portao 10), os extratores que nao emitem

- [ ] Portao novo: falha quando um kind que DEVERIA declarar `grants_completos`
      nao declara, e reporta a cobertura por kind.
- [ ] Fazer os kinds faltantes emitirem o campo.
- [ ] Registrar a cobertura de hoje como linha de base, para o portao 4
      (cobertura caindo vs build anterior) passar a vigiar tambem isto.

### Tarefa 2.1: revalidar os numeros que a auditoria nao fechou

- [ ] Item **60** (concessoes de `GrantItem`): a auditoria mediu 491 hoje contra
      679 do item, mas as categorias nao mapeiam 1:1 (condicao caiu 156 -> 17,
      UUID subiu 163 -> 184). **Re-medir com a metodologia original** antes de
      decidir se fecha ou trabalha.
- [ ] Itens 59 (1.564 registros que perderam mecanica), 52 (684 campos com
      `prov` desconhecida) e 56 (69 registros
      pre-remaster) foram medidos em 27/07 e varias sessoes de conserto passaram
      por cima. Re-medir CADA UM antes de abrir trabalho. O relatorio da auditoria
      da Fase 0 ja traz esse numero -- aqui e so confirmar o que sobrou.

### Tarefa 2.2: achatamento de "X and either Y or Z" (itens 91 e 75b)

**A auditoria ja respondeu a pergunta:** e falha estrutural de desenho, mas caso
UNICO hoje. `pipeline/extratores/feats.py::_clausula_rank` escolhe **um conector
para o grupo inteiro** (`conector = "any" if " or " in resto else "all"`), sem
posicao estrutural e sem aninhamento. Varredura nos 19.706 registros: 4
candidatos, **1 defeito real** -- nos outros 3, um alvo e feat e nao pericia,
entao a funcao devolve `None` e o parser geral produz o aninhamento certo.

Consertar por ser desenho errado, sem esperar fila. O MESMO registro tem o
defeito irmao no `grants` (da Diplomacy **e** Intimidation expert quando o RAW e
ou-ou, item 75b) -- os dois saem juntos.

**Arquivos:**
- Criar: spec **aninhamento-de-clausula** (a criar em `specs/`)
- Modificar: `pipeline/extratores/feats.py:481-504` (`_clausula_rank`)

- [ ] Teste do parser: "trained in martial weapons and either Diplomacy or
      Intimidation" produz `all[proficiency martial, any[diplomacy,
      intimidation]]`.
- [ ] Conferir que os outros 3 candidatos NAO regridem.
- [ ] Reemitir. Provar que `Marshal Dedication` deixa de liberar para um Clerigo
      que so tem Diplomacy, e que o `grants` parou de dar as duas pericias.

### Tarefa 2.3: lore com rank vazado (resto do item 88)

5 registros com `lore:expert-in-demon` onde deveria ser `lore:demon` + `>=
expert`. Erram a chave E o rank.

- [ ] Conserto em `pipeline/extratores/feats.py`, reemitir, provar que
      `demon-hunter` passou a pedir `lore:demon >= expert`.

### Tarefa 2.4: heritage nao e enumerado pelo AoN (item 18, reescrito)

**Mudou de natureza na auditoria.** Nao sao "3 ausencias pontuais":
`Life-Saving Yowl` era premissa errada (existe como `Caterwaul`). A causa e que
**heritage so e enumerado a partir do Foundry**, nunca do AoN -- por isso
`Cavern Kobold` e `Spellscale Kobold` faltam.

- [ ] Enumerar heritage tambem pelo AoN, como ja se faz nos outros kinds.
- [ ] Portao 9 (censo por categoria) passa a cobrir heritage.
- [ ] Os 4 class-features que o portao 9 ainda acusa (`Incredible Senses`,
      `Vigilant Senses`, `Lightning Reflexes`, `Premonition's Reflexes`) --
      item 55, mesma passada.

**Saiu desta fase:** item 54 (`tactic` = 37 e `class-kit` = 32, conferidos) e
item 23 (falso alarme).

### Tarefa 2.5: eixo `outras-opcoes` e um balaio (item 69)

**16 de 27** classes ainda tem um (eram 25 -- Fighter e Monk, os piores
exemplos, ja foram corrigidos por `aplicar_subclasses.py`). O caso que sobra e o
Alchemist, que mistura `Advanced Alchemy` (progressao) com `Advanced Vials`
(sub-escolha de verdade).

- [ ] Medir o que caiu no balaio por classe, propor o recorte na spec, aplicar.

**Verde da fase:** 9 portoes + as tres outras camadas + relatorio de cobertura
antes/depois.

---

## Fase 3 -- subclasse nao altera nada (o maior custo do projeto)

Item 40, e a propria spec o chama assim -- mas a auditoria **corrigiu o numero e
o diagnostico**. O item dizia "175 das 176 sub-escolhas sem efeito"; hoje sao
**114 de 418 (27%) com `grants` que o motor JA aplica**. O mecanismo de
aplicacao deixou de ser o gargalo: `_proficiencias` e `_grants_em_cadeia` leem
`self.features`, que inclui a subclasse escolhida.

**O que trava e a EXTRACAO** -- 304 opcoes com `grants: []`, porque
`converter_rule_elements.py` so converteu os 99 declarativos. Falta o grosso:
1.784 FlatModifier, 1.495 ItemAlteration, 1.113 GrantItem, 1.077 RollOption, 563
ChoiceSet, 337 Resistance.

**Esta fase e um projeto dentro do projeto.** Ela nao cabe numa passada e nao
deve ser tratada como se coubesse. O plano aqui e deliberadamente incremental:
cada tipo de Rule Element vira uma fatia propria, com spec, teste e ficha de
prova, e a fase entrega valor a cada fatia -- nao no fim.

- [ ] **3.1** -- FlatModifier de numero estatico (o mais comum e o mais barato).
      Prova: uma subclasse que da +1 em alguma coisa muda a ficha.
- [ ] **3.2** -- Resistance (337). Prova: Instinto do Barbaro muda resistencia.
- [ ] **3.3** -- ItemAlteration limitado ao que altera numero ja modelado.
- [ ] **3.4** -- GrantItem com alvo estatico (o dinamico ja e sinalizado hoje).
- [ ] **3.5** -- ChoiceSet: vira sub-escolha de verdade, com slot na ficha.
- [ ] **3.6** -- RollOption: decidir na spec se entra. Ele so tem sentido com
      rolagem, e o app nao rola dado. Provavel: **nao entra**, registrar como
      fora de escopo com o motivo.
- [ ] **3.7** -- tradicao de conjuracao por subclasse (item 78, com o 41 dentro):
      48 subclasses com `grants: []`. Derivar do texto o padrao
      "Spell List <tradicao>". Fecha o buraco que a Tarefa 1.1 deixou marcado.

Cada fatia: spec, teste no oraculo, implementacao nos dois motores, fixtures,
navegador, commit. Entre fatias, rodar a comparacao com o Pathbuilder -- e nela
que o efeito de subclasse aparece como candidato certo ou errado.

---

## Fase 4 -- equipamento e os numeros de combate (item 43)

Sua correcao de escopo de 27/07: o app constroi o personagem INTEIRO, e os
numeros de combate sao numeros de ficha.

- [ ] **4.1** -- runa de propriedade (item 77): nao existe no motor nem no
      schema. Potencia ja funciona.
- [ ] **4.2** -- `weapon_proficiency` ignorado, 91 ocorrencias (item 75).
      Fecha tambem a guarda morta de `_rank_de_arma` no TS (ver "divida
      conhecida" abaixo).
- [ ] **4.3** -- `flat_modifier` nao-HP e `proficiency` com expressao (item 72),
      1.709 ocorrencias. Decidir na spec ate onde interpretar.
- [ ] **4.4** -- duas armas sem dano sem fonte em disco (resto do item 85):
      dump novo do AoN ou entrada curada.

---

## Fase 5 -- validacao larga contra o Pathbuilder (item 84)

A 1a rodada fechou com 4 pontos; a 2a (hoje) abriu 85 divergencias em 7
combinacoes. A ferramenta esta pronta -- falta cobertura.

- [ ] Sonda em mais classes, mais slots (ancestry feat, que nunca foi comparado)
      e niveis altos (12, 16, 20), onde o predicado tem mais o que errar.
- [ ] Cada rodada: triar em **defeito nosso / diferenca de modelo / recorte de
      fonte**, e so o primeiro vira trabalho.
- [ ] Fechar o item 10 (importador do Pathbuilder avisando o que se perde) com o
      que a sonda ja ensinou sobre o formato deles.

---

## Fase 6 -- polimento e o que ficou por ultimo

- [ ] Itens `baixa` que sobrarem da Fase 0.
- [ ] Item 8 (re-rodar simulacao corrigindo o vies do Fable) e item 7
      (balanceamento) -- so depois da base fechar de verdade.
- [ ] **Item 31 (i18n en/pt-BR) por ULTIMO**, como voce mandou.

---

## Divida conhecida que este plano carrega de proposito

- **`personagem.ts:1951` usa `Object.hasOwn` num `Map`.** A guarda "rank de arma
  nomeada ganha da categoria" nunca dispara no TS; no Python dispara. Divergencia
  de paridade DORMENTE -- so acorda quando alguem preencher chave `weapon:` na
  ficha, que e exatamente o que a Tarefa 4.2 vai fazer. **Consertar junto com a
  4.2, nao antes**, para o teste de paridade provar o conserto.
- **`lore:*` responde presenca, nao contagem.** Nenhum registro pede "duas Lores
  diferentes" hoje. Se aparecer, vira termo proprio.
- **Dois nomes de Lore malformados na fonte** (`**Boneyard Lore (with Additional
  Lore perks)` e `Art Lore and Underworld Lore`, dois nomes numa string). Defeito
  do extrator de background; nao afeta nenhum dos 44 registros com requisito de
  Lore.

## Como sei que terminei

Nao e "os itens fecharam". E:

1. As quatro camadas verdes, com o numero de assercoes SUBINDO a cada fase.
2. A comparacao com o Pathbuilder rodada em pelo menos 12 combinacoes de
   classe/slot/nivel, com toda divergencia restante classificada por escrito em
   **defeito nosso / diferenca de modelo / recorte de fonte**, e zero na primeira
   categoria.
3. O panorama do Tartarus contando os itens abertos do waybuilder.
4. Tudo com push.
