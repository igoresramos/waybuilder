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
  Relatorio em `docs/`, spec em `specs/`, prototipo em `docs/prototypes/`.
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

**Ja apurado (fatia escopo/decisao, 2026-07-29), a conferir e fechar:**

| id | veredito | evidencia |
|---|---|---|
| 7, 8 | JA RESOLVIDO | `docs/simulacoes/2026-07-27_balanceamento.md` responde os dois, e ja usa a politica de acao SIMETRICA que corrige o vies do Fable |
| 9 | JA RESOLVIDO | o app existe: Vite+React PWA offline, picker modal reusado, o JSON e a ficha |
| 16 | OBSOLETO | o app nao vai ser publicado (decisao de 27/07) -- licenciamento saiu do escopo |
| 23 | OBSOLETO | `Triggerbrand Salvo` esta na base (falso alarme); os wayfinders do PFS Guide sao limite de fonte declarado |
| 35 | JA RESOLVIDO | os 3 registros tem `source` e `license` hoje, resolvidos de carona no re-dump do pf2etools |
| 44 | JA RESOLVIDO | a tabela de conjuracao saiu do campo `markdown` do AoN, sem depender dos PDFs |
| 18 | PARCIAL | `Life-Saving Yowl` era premissa errada (existe como `Caterwaul`). Sobra defeito ESTRUTURAL: heritage so e enumerado pelo Foundry, nunca pelo AoN -- por isso `Cavern Kobold` e `Spellscale Kobold` faltam |
| 47 | PARCIAL | (b) caiu hoje; (a) e (c) sao decisao sua -- ver contrato de autonomia |
| 68 | PARCIAL | vies 1 corrigido; falta o oraculo de EM QUE NIVEL cada aumento de pericia foi gasto |
| 10, 13, 19, 22, 42, 73, 79 | VALIDO | seguem de pe, nenhuma sessao posterior tocou |

O item 18 muda de natureza: deixa de ser "3 ausencias pontuais" e vira
**"heritage nao e enumerado pelo AoN"**, que e causa e nao sintoma. Reescrever
com esse titulo antes de trabalhar.

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
- Criar: `specs/2026-07-30-termo-spellcasting-tradition.md`
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

### Tarefa 1.2: higiene de boost + bancada (itens 74 e 90, fundidos)

Ficha sem boost declarado sai com tudo 10 e **nenhum aviso**. O motor aplica o
que o jogador declara mas nunca confronta DIREITO com DECLARADO. A bancada de
comparacao com o Pathbuilder sofre exatamente disso: monta um personagem com 9
boosts nao atribuidos e compara com um que tem STR 16.

**Arquivos:**
- Criar: `specs/2026-07-30-higiene-de-boost.md`
- Modificar: `motor/motor.py` (`_higiene_de_boost`, espelhando
  `_higiene_de_slot`), `app/src/motor/personagem.ts`,
  `motor/comparar_pathbuilder.py`

- [ ] Teste: ficha de Guerreiro 1 sem `boosts_livres` declarado produz aviso
      dizendo quantos boosts faltam escolher, por origem.
- [ ] Implementar nos dois motores.
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
- Criar: `specs/2026-07-30-grant-feat-de-background.md`
- Modificar: `pipeline/unificar_efeitos.py:76`
- Rodar: `pipeline/resolver_referencias.py` (ja sabe resolver `name` +
  `foundry_uuid`)

- [ ] Conserto na origem: `grants_de_background` extrai `name`/`foundry_uuid` e
      resolve para id `wb:`, em vez de `str(x)`.
- [ ] Reemitir a base e conferir o portao 3.
- [ ] Prova ponta a ponta: um Barkeep sai com Hobnobber em `concedidos`, e o feat
      **nao** aparece mais como candidato no slot de skill feat.
- [ ] Confirmar na comparacao que `Hobnobber` saiu da divergencia.

### Tarefa 1.4: gate de nivel na primeira classe alfabetica (item 71)

122 feats travados na classe errada.

- [ ] Reproduzir com ficha montada antes de mexer.
- [ ] Spec, conserto nos dois motores, fixtures, comparacao.

### Tarefa 1.5: `_termo_has` sem recorte temporal (item 65)

Pegar `Quick Shot` no nivel 2 satisfaz requisito de um feat de nivel 1 -- o
termo avalia o documento inteiro, sem olhar QUANDO.

- [ ] Reproduzir, spec, conserto nos dois motores, fixtures.

### Tarefa 1.6: conjuracao por dedicacao na ficha (item 66)

`_conjuracao` itera so `ordem_de_classe`. Conferir contra o que a spec de
spellcasting de arquetipo (2026-07-29) ja entregou -- pode ter caido junto.

- [ ] Medir primeiro. Se ja caiu, fechar o item com a evidencia.

**Verde da fase:** quatro camadas + comparacao com o Pathbuilder re-rodada, com
o total de divergencia medido antes e depois.
**Push ao fim da fase.**

---

## Fase 2 -- a base perde mecanica em silencio

Nenhum destes muda regra: mudam o que a base ENTREGA. Todos exigem reemissao
(`WB_REEXTRAIR=1` quando mexer em extrator).

### Tarefa 2.1: revalidar os numeros antes de trabalhar

- [ ] Os itens 59 (1.564 registros que perderam mecanica), 60 (679 concessoes de
      `GrantItem`), 52 (684 campos com `prov` desconhecida) e 56 (69 registros
      pre-remaster) foram medidos em 27/07 e varias sessoes de conserto passaram
      por cima. Re-medir CADA UM antes de abrir trabalho. O relatorio da auditoria
      da Fase 0 ja traz esse numero -- aqui e so confirmar o que sobrou.

### Tarefa 2.2: achatamento de "X and either Y or Z" (item 91)

`Marshal Dedication` virou `any[martial, diplomacy, intimidation]` onde o RAW e
`all[martial, any[diplomacy, intimidation]]`.

- [ ] **Primeiro medir se e sistematico.** Varrer a prosa dos pre-requisitos
      procurando o padrao "and either ... or"; se forem muitos, o conserto e no
      parser e vale para o conjunto. Se for so o Marshal, e curadoria.
- [ ] Spec com o numero. Conserto. Reemitir. Comparacao.

### Tarefa 2.3: lore com rank vazado (resto do item 88)

5 registros com `lore:expert-in-demon` onde deveria ser `lore:demon` + `>=
expert`. Erram a chave E o rank.

- [ ] Conserto em `pipeline/extratores/feats.py`, reemitir, provar que
      `demon-hunter` passou a pedir `lore:demon >= expert`.

### Tarefa 2.4: kinds ausentes e ausencias pontuais (itens 54, 55, 18, 23, 27)

- [ ] `tactic` (37 tacticas do Commander) e o outro kind do item 54: extrair,
      reconciliar, portao 9 verde.
- [ ] Ausencias pontuais de `pipeline/censo_ausencias.json`, uma a uma, cada
      uma com a fonte citada.

### Tarefa 2.5: eixo `outras-opcoes` e um balaio (item 69)

25 das 27 classes tem um. E o que fez um Guerreiro 4 sair com `Warrior of
Legend`.

- [ ] Medir o que caiu no balaio por classe, propor o recorte na spec, aplicar.

**Verde da fase:** 9 portoes + as tres outras camadas + relatorio de cobertura
antes/depois.

---

## Fase 3 -- subclasse nao altera nada (o maior custo do projeto)

Item 40, e a propria spec o chama assim. 175 das 176 opcoes de sub-escolha nao
mudam numero nenhum na ficha. O dado existe: 584 das 841 class-features do
Foundry tem Rule Elements, e `converter_rule_elements.py` converteu so os 99
declarativos. Falta o grosso: 1.784 FlatModifier, 1.495 ItemAlteration, 1.113
GrantItem, 1.077 RollOption, 563 ChoiceSet, 337 Resistance.

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
