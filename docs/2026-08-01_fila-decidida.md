# Fila de execucao -- decidida em 2026-08-01

Decidida com o fable DEPOIS de validar as 11 issues do GitHub contra o codigo.
**Todas as 11 aplicam** -- nenhuma fantasma, nenhuma ja resolvida.

Prioridade pelo criterio que o TODO ja usa: `alta` = bloqueia outro item OU
entrega numero/opcao errada na ficha do jogador; `media` = buraco de conteudo;
`baixa` = polimento.

## A fila

**1. Persistencia da ficha + identidade de build** -- issue #1 + achados 6/7/17 (alta)
**FEITO em `750308f`.** Unica perda de dado ativa do lote. Fecha 6+7+17 juntos.
Pronto: F5 retoma; id estavel; listar/apagar deixam de ser codigo morto; hash de
manifesto + versao de schema no documento; carga divergente avisa.

**2. Kingmaker fora, no pipeline, e re-baseline UNICA** -- item 2 do plano (alta)
A linha de base esta fixada em 20.083; ordem errada = fixar duas vezes. Remove
tambem os 16 skills lore que poluem o espaco da issue #2.
Pronto: passo nomeado no `build.sh` (nunca a mao); criterio = uniao livro∪trait;
excecao ao principio 4 registrada por escrito; varredura de orfaos; portoes 4/11
com `--aceitar-queda` + motivo; `comparar_bases` com delta so o esperado.

**3. verificar.sh + triagem dos 35 vermelhos** -- bloco 2 da arquitetura (alta)
Toda posicao abaixo exige trava nova, e trava sem executor e teatro.
Pronto: um comando roda teste_motor, vitest, oraculo, iconics e os .mjs; cada
vermelho adjudicado (bug vs apodrecido) com registro.

**4. Portao de conteudo** -- portao 11 estendido a text/grants/requires/traits/level por kind (alta)
Vai aqui e nao depois, para a linha estendida ser gravada UMA vez, ja pos-Kingmaker.

**5. Progressao respeita `requires`** -- issue #7 (alta: numero errado)
Cleric 5 com expert sem doutrina; Fighter 1 com capstone de nv20 + Diehard.
`motor.py:382-394` e o espelho TS ganham a checagem que o laco de subclasses ja
tem na `:404`, mais 2 registros de dado.

**6. Eixo reconhece a escolha e marca fora-do-requisito por opcao** -- issues #6 + #8 (alta)
`motor.py:413` cruza contra a lista crua (vazia nos 9 eixos por query): Kineticist
e Commander travados com escolha gravada e aviso falso. E opcao descasada entra
em silencio, violando o principio zero pelo lado oposto.

**7. Saneamento dos eixos de subclasse (dado)** -- issue #10 + itens 9/8/5 do plano (alta)
13 classes com eixo duplicado/morto/errado. Inclui a cadeia Base/Extended Kinesis.
Pronto: Oracle com 1 curse concedida e 0 escolhiveis; Kinetic Gate com
cardinalidade derivada single/dual (padrao da spec de escolha aninhada).

**8. `grants[].se` -- grant condicional** -- TODO 107 + resto do 111 (alta)
Miolo mensuravel da issue #3. Campeao e Gunslinger seguem recebendo NADA.

**9. Backgrounds 1-de-2** -- TODO 112 (alta)
4 backgrounds concedem feat a mais, 1 arbitrario, 4 nenhum.

**10. Predicado contra o estado do personagem** -- frente 2 (itens 6+11) + issue #4 (alta)
`{actor|...}` literal nao recorta, e `_aceita_no_slot` sem branch para
`universal-ancestry` esconde 32 feats de TODO personagem.
**Fecha o item 7 do plano de graca:** a pergunta (c) do Igor esta respondida --
sao os feats Reincarnated (25 dos 32) E as 5 herancas versateis ausentes (0/326),
ou seja, defeito de FILTRO no motor **e** de EXTRATOR ao mesmo tempo.

**11. Fusao de pares AoN/Foundry -- so a gravidade (a)** -- TODO 110 (alta)
8 pares de conteudo partido mudam o que o jogador recebe (`voice-of-elements`:
7 grants vs 0). Ruido `Wand of X` fica de fora.

**12. Quantidade de skill increase** -- issue #9 (alta)
Swashbuckler perde 3, Thaumaturge perde 1 (achado NOVO da validacao, fora da
issue). Colado na 13 porque a Frente 1 mexe no mesmo slot. Exige schema
(quantidade por nivel) + os dois motores -- o `Set` em `motor.py:586` /
`personagem.ts:586` colapsa repeticao.

**13. Frente 0 + Frente 1 JUNTAS** -- itens 13, 1, 3, 4, 10 do plano (alta)
Maior frente; muda o schema do documento. As duas decisoes do Igor ja estao
tomadas (paridade SUGERE e marca; escolhas acima do nivel FICAM guardadas).
Separar as duas frentes faz a segunda desfazer a primeira -- mesma infra
`_avaliando_em` + `nivel_personagem`.

**14. Lore livre + lore-fantasma + bloco `manual`** -- issue #2 = item 12 (media)
Depois da 13 porque persiste texto novo no documento. `wb:skill/lore` deixa de
ser fantasma; bloco `manual` do `doc.ts`: ler ou remover, nao deixar prometendo.

**15. Magia conhecida + recursos de classe** -- issue #11 = TODO 116 (media)
Fatiar: repertorio/preparada primeiro, focus spells depois, recursos proprios um
a um.

**16. Marcacao Foundry na prosa** -- issue #5 (baixa, mas 41% da prosa de class-feature)
Isolada em `marcacao.ts`: **totalmente paralela**, pode rodar por agente separado
a partir da posicao 3.

## Por que a issue #1 fura a fila

(i) unico achado com impacto `perda_de_dado`, e num PWA sem backend o
localStorage **e** o banco; (ii) defeito write-only comprovado -- cada F5 descarta
a ficha da vista do usuario HOJE; (iii) piora sozinho ate a cota estourar, e ai o
autosave da sessao corrente passa a falhar; (iv) taxa todo o resto da fila --
cada fix das posicoes 5-15 e testado no app, e sem retomada cada teste manual
recomeca do zero; (v) e barato, `listar`/`apagar` ja existiam; (vi) fecha os
achados 6, 7 e 17 de carona; (vii) e a unica posicao que nao disputa com o
`build.sh`.

## O que SAI da fila, com motivo

- **TODO 31** (i18n) -- decisao registrada do Igor: por ultimo, app fechado.
- **TODO 96** (acesso estruturado) -- zero consumidor; construir antes de existir
  a pergunta viola a regra da casa.
- **TODO 103** (rules.json) -- a re-medicao derrubou a premissa; alvo real sao ~35
  paginas, quase todas de mestre.
- **TODO 104/101** -- baixas, declaradas com numero nas specs; nao corrompem ficha.
- **TODO 117** (concessao do mestre) -- re-triar DEPOIS da posicao 13: o slot
  `concessao` vai pousar no schema novo.
- **TODO 68** (oraculo do nivel de aumento) -- **nao fazer antes da 13**: a Frente
  1 entrega o dado de graca; antes e retrabalho certo.
- **Ruido `Wand of X`** (107 grupos do TODO 110) -- busca poluida, zero numero errado.
- **Achados P2 12-15 da arquitetura** -- registrar, nao executar.
- **TODO 10** (aviso do importador) -- baixa, sem mudanca de estado.
- **Metade "implementar leitor do bloco `manual`"** -- se a spec decidir remover,
  remove-se; nao construir leitor por inercia.

## Dependencias reais

| de | para | por que |
|---|---|---|
| 2 | 4 | a linha estendida grava uma vez, ja pos-Kingmaker |
| 2 | 14 | os 16 skills lore saem antes de a spec de lore modelar o espaco |
| 3 | 5..16 | toda posicao exige trava; sem executor, trava nao conta |
| 5 | 8 | grant condicional sobre laco que ignora `requires` seria contornado |
| 6 | 7 | sem o eixo reconhecer a escolha, dado saneado e inverificavel na tela |
| 12 | 13 | mesmo slot de `skill_increase`; ordem inversa mexe duas vezes |
| 1 | 13 | migracao de `nivel_atual` exige versao/identidade no documento (achado 7) |
| 13 | 14, 15 | ambos persistem escolha nova ja no formato temporal |

Frente 0 e Frente 1 **nunca separadas**. A 16 e totalmente paralela.

## Fonte de verdade: o `TODO.md` do Tartarus

Decisao, com consequencias:

- **`TODO.md` vira a fonte unica.** E a unica das tres listas com disciplina de
  re-medicao (data de verificacao por item, criterio de prioridade escrito, 55
  fechados arquivados) e a que o fluxo `tartarus:fim` ja commita.
- **Issues do GitHub viram interface publica de entrada e espelho.** Cada uma
  recebe comentario com o veredito da validacao + id do item do TODO, e e fechada
  pelo commit que fecha o item, citando as duas (`TODO #id, closes #N`). Issue
  nova = triagem para o TODO em ate uma sessao, nunca vida propria.
- **O plano de 13 itens congela como documento de execucao.** As decisoes do Igor
  no rodape ja estao absorvidas nesta fila; o arquivo nao recebe mais status.
- **Regra operacional que evita o retrabalho do item 84:** nenhuma triagem,
  medicao ou fechamento conta como feito ate o item do TODO ser atualizado **no
  mesmo ato** -- a mesma regra que a wiki ja impoe para o `INDEX.md`.
