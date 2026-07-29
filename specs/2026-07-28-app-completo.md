# Spec -- o app do Waybuilder, inteiro

Status: viva. Atualizada em 2026-07-28.

Escrita para ser suficiente sozinha: alguem que nunca viu este repo deveria
conseguir **recriar o app** a partir daqui, e -- mais importante -- entender
*por que* cada decisao e a que ela e. Onde houver numero, ele foi medido, e a
medicao esta dita.

Complementa, nao substitui:
- `2026-07-26-regras-multiclasse.md` -- as 22 regras da casa
- `2026-07-26-schema-base.md` -- o formato da base canonica
- `2026-07-26-schema-personagem.md` -- o documento de personagem
- `2026-07-27-slots-e-candidatos.md` -- o contrato motor <-> tela
- `2026-07-28-ui-pathbuilder.md` -- a pele

---

## 1. O que o app e

Construtor de personagem de Pathfinder 2e com **regra caseira de multiclasse**:
niveis de classe que se dividem (estilo D&D 5e), em vez dos arquetipos de
dedicacao do PF2e oficial. Usado pelo Igor e pela mesa dele.

**PWA client-side. Sem backend, sem conta, sem sincronizacao.** Roda offline
depois da primeira visita. Isto e decisao, nao limitacao: o app precisa
funcionar numa mesa de jogo sem internet, e uma ficha de RPG nao justifica
operar servidor.

Consequencias que atravessam todo o resto:
- persistencia e `localStorage`; backup e export/import de JSON;
- a base inteira viaja para o cliente (1,09 MB gzip) e fica em cache;
- nao ha "servidor recalcula": o motor roda no navegador, e por isso ele
  precisa ser rapido (mede-se em 0,30 ms por ficha de nivel 20).

## 2. Stack e por que

| peca | escolha | por que |
|---|---|---|
| build | **Vite 8** | dev server instantaneo; o projeto tem base de 9 MB em `public/` e precisa servir estatico sem cerimonia |
| UI | **React 19**, sem router | o app e UMA tela; router seria peso sem uso |
| linguagem | **TypeScript 6**, `strict` | o motor foi portado do Python e o contrato de tipos e o que impede o porte divergir em silencio |
| testes | **Vitest 4** | roda o mesmo codigo do app, sem browser -- os testes exercitam `doc.ts` + motor, que e onde o defeito caro mora |
| lint | **oxlint** | rapido; sem opiniao de formatacao |
| PWA | **vite-plugin-pwa** (Workbox) | precache dos 9,4 MB de base: e o que faz o app abrir offline |
| CSS | **um arquivo, sem framework** | a pele e copiada do Pathbuilder e cabe em ~460 linhas; Tailwind aqui so adicionaria uma etapa de build |
| estado | **`useState` no `App.tsx`** | ha UM estado (o documento) e ele desce por props; store global seria abstracao sem segundo consumidor |

**Zero dependencia de runtime alem de React.** Virtualizacao de lista, parsing de
prosa e formatacao de trait sao ~30 linhas cada, escritas aqui -- uma
dependencia custaria mais que o codigo.

## 3. A regra que organiza tudo

> **O documento e a unica fonte de verdade. Tudo o mais e derivado.**

A tela edita `doc.escolhas[]` e `doc.inventario[]`, e nada mais. HP,
proficiencia, CA, ataque, slot aberto e pendencia sao **re-derivados a cada
mudanca** e nunca guardados.

Por que importa: quando uma regra muda, a ficha salva **re-deriva** em vez de
ficar invalida. Uma ficha de 2026 continua abrindo depois de o motor mudar de
ideia sobre a regra 21.

Custo aceito: derivar tudo a cada tecla. Medido em **0,30 ms** para nivel 20, o
que torna a discussao irrelevante.

## 4. Arquitetura

```
public/base/            payload do pipeline (gitignored, derivado)
  _manifesto.json       <- a lista de kinds vem DAQUI, nao do codigo
  por-kind/*.json       54 arquivos, 1,09 MB gzip somados
  text/*.json           19 MB de prosa, buscada por kind sob demanda

src/
  carregarBase.ts       busca o manifesto, depois os kinds em paralelo
  doc.ts                o documento + localStorage + export/import
  prosa.ts              separa regra de sabor no texto das fontes
  marcacao.ts           limpa `{@skill Athletics|PC1}` -> `Athletics`
  nomeDeTrait.ts        caixa correta, inclusive nos parametrizados de arma
  motor/                porte de motor/motor.py para TypeScript
    tipos.ts            O CONTRATO -- escrito antes do porte
    base.ts             Base: por_id, resolver(), multiclasse()
    personagem.ts       as 22 regras + slots_abertos() + candidatos()
  componentes/
    Slot.tsx            a linha de escolha + o modal (UM picker, reusado)
    Funil.tsx           filtro fino do picker
    ListaVirtual.tsx    janela por scroll
    Traits.tsx          a faixa de traits
    Prosa.tsx           o texto em partes
    Equipamento.tsx     inventario
    PainelDireito.tsx   a ficha viva
    Icones.tsx          SVG proprio
  App.tsx               shell, estado, e a coluna de build
```

### Fluxo de dados, em uma frase
`App` guarda `Documento` -> constroi `Personagem(doc, base)` -> `visao()` desce
para `PainelDireito`; os componentes chamam `doc.*` para produzir um documento
NOVO, e o ciclo recomeca.

## 5. O que o app carrega, e por que TUDO

**54 kinds, 19.705 registros, 1,09 MB gzip.**

Ate 2026-07-28 carregava 8 kinds (0,53 MB) para segurar a primeira carga. O
corte amputava o app **em silencio**, porque o motor sabia fazer o que o dado
nao deixava aparecer:

| faltava | o motor ja fazia | sintoma |
|---|---|---|
| `weapon` | ataque e dano por arma | aba Ataques vazia para sempre |
| `armor`, `shield` | CA com cap de DEX, escudo, penalidade | todo personagem sem armadura |
| `spell` | slots das 11 conjuradoras | conjurador nao escolhe magia |
| `deity`, `domain` | -- | clerigo e campeao sem divindade |
| `animal-companion` | ficha de companheiro em RAW | sem pet |
| 8 kinds de sub-escolha | `candidatos("subclasse")` | instinto do Barbaro abria picker VAZIO |
| `trait` | `_termo_trait` | picker mostrava slug cru (`versatile-b`) |

**A lista de kinds vem do `_manifesto.json`.** Kind novo no pipeline viaja
sozinho; deixa de existir a classe de defeito "esqueceram de editar a constante
em dois lugares" -- que foi exatamente o que aconteceu.

A **prosa** (19 MB) continua fora: e maior que o indice inteiro, e o app busca o
texto de um kind na primeira vez que abre um registro dele.

## 6. Decisoes de interface

### 6.1 Duas colunas, nao abas
Build a esquerda (371px, scroll proprio), ficha viva a direita.

A primeira versao tinha tres abas (criacao / progressao / ficha): o jogador
escolhia um feat e tinha de **trocar de aba para ver o numero mudar**. Num
construtor, o retorno imediato e o ponto todo. Layout refeito a partir do
Pathbuilder, que e o app que o Igor usa na mesa.

A esquerda mostra **todos os niveis ate o alvo**, nao so os alcancados: montar
personagem de PF2e e planejamento, e o jogador quer ver onde os slots caem la na
frente antes de decidir o de agora.

### 6.2 Pericia nao e aba
Fica numa coluna estreita (194px) sempre visivel. E o numero mais consultado na
mesa; poe-la atras de um clique custaria um clique por rolagem.

### 6.3 Um unico picker
Todo slot -- ancestralidade, classe, feat, aumento de pericia, subclasse, item
-- abre **o mesmo componente**. Modal master-detail: lista a esquerda, texto
completo a direita.

Ninguem escolhe um feat pelo nome. O jogador le o efeito, os traits, o requisito
e a fonte, e so entao aceita.

### 6.4 PRINCIPIO ZERO -- o requisito sugere e ORDENA, nunca bloqueia
O que nao atende aparece **na mesma lista**, em cinza, depois dos que atendem,
com o motivo no detalhe. Nao existe "mostrar mais": esconder o feat de nivel 6
impede o planejamento, que e metade do que se faz aqui.

**A excecao, e a distincao que importa:** o *slot* filtra por TIPO. Heranca de
outra ancestralidade nao e "escolha ruim", e escolha **inexistente** -- some.
Feat de nivel alto e escolha *futura* -- aparece marcado. A regra:

> tipo filtra; requisito ordena.

### 6.5 Esconder e escolha do jogador
O **funil** oferece "so o que posso pegar agora", "ate o nivel N" e traits (E,
nao OU). Nada ligado por padrao. O botao marca quando ha filtro ativo -- filtro
silencioso e a forma mais facil de mentir sobre o que existe.

### 6.6 Regra separada de sabor
Ver secao 8.

### 6.7 O accent nunca preenche fundo
`#ff5722` marca por texto, borda ou sublinhado. Botao e outline-only, sem
variante preenchida. Copiado do Pathbuilder e mantido por coerencia.

### 6.8 Densidade sobre respiro
Base 14px, cai para 12px abaixo de 1400px -- **encolhe, nunca reflowa**. E uma
ferramenta densa de desktop; espalhar os numeros em telas menores atrapalharia
mais que apertar. Abaixo de 1100px as colunas empilham, porque ai nao ha
alternativa.

## 7. Acessibilidade -- o que e obrigatorio aqui

Medido, nao presumido:

| item | decisao |
|---|---|
| contraste | tudo >= 4.5:1. O vermelho do Pathbuilder (`#d9695f`, 3,78) reprovava justo no "Nao escolhido" -> `#e8867c` (5,01) |
| borda de controle | `--borda-forte` `#677691` (3,23) separada da de divisoria: a borda e a unica coisa que diz que um botao outline e um botao |
| foco | anel `:focus-visible` de 2px. **`:focus-visible`, nao `:focus`** -- o app e todo clique, e o anel piscaria o tempo todo |
| pressionado | fundo, **nao `transform: scale`** -- escala desloca a linha numa coluna densa |
| movimento | `prefers-reduced-motion` zera transicoes |
| botao so-icone | `aria-label` sempre (`x` de limpar slot, `x` de remover item) |
| semantica | `<button>`, `<aside>`, `<section>`, `<nav>` -- nunca `div` com `role` |

## 8. Prosa: regra separada de sabor

O texto das fontes chega como **um paragrafo unico** com nome, custo de acao,
livro, gatilho, requisito, efeito e -- nas ancestralidades -- seis secoes de
folclore, tudo colado.

A estrutura existe e foi **medida**. Duas familias:

| familia | marca | kinds |
|---|---|---|
| item de regra | separador `---` | feat 98%, spell 100%, weapon 91%, equipment 89% |
| descritivo | rotulos nomeados, sem `---` | ancestry, heritage, background, class, archetype (0%) |

Os rotulos sao vocabulario fixo da Paizo, e dao a classificacao de graca:

- **REGRA**: `Frequency`, `Trigger`, `Requirements`, `Cost`, `Effect`,
  `Special`, `Critical Success`, `Success`, `Failure`, `Critical Failure`,
  `Heightened`, `Access`, `Duration`, `Range`, `Area`, `Targets`
- **SABOR**: `You Might`, `Others Probably`, `Physical Description`,
  `Alignment and Religion`, `Society`, `Adventurers`, `Ethnicities`, `Names`
  -- os seis primeiros em **50 das 50** ancestralidades

Na tela: campos curtos primeiro (barra accent), efeito no meio, fantasia
**recolhida** atras de "ler a descricao (7)". Ela nao some -- escolher
ancestralidade e metade sabor -- mas nao ocupa a tela de quem compara feats.

Tres armadilhas que custaram iteracao e nao podem ser reintroduzidas:
1. **delimitar a fonte pelo proximo rotulo nao funciona** -- na ancestralidade
   nao ha rotulo entre `Source ... pg. 62` e a descricao, e a fonte engolia o
   texto inteiro. Quem fecha a fonte e o formato dela (`<livro> pg. <numero>`);
2. **a abertura sem rotulo e ambigua** -- efeito num feat, descricao numa
   ancestralidade. Desempata pela companhia: havendo sabor e nao havendo `---`,
   a abertura e sabor;
3. `You Might...` deixa a reticencia para tras ao casar o rotulo.

### Marcacao das fontes
`{@skill Athletics|PC1}` aparece em **53% dos 3.960 requisitos**. Uma regra
cobre as 20 tags (`{@tag Rotulo|FONTE|apelido}`), mas **as tags aninham**
(`{@note (or {@feat ...})}`) -- resolver de dentro para fora ate estabilizar. Um
teste varre a base cobrando que nada sobre com `{@`.

## 9. Nomes e caixa
Trait usa o `name` do registro (`Dwarf`, `Flourish`). **62 slugs nao tem
registro** -- sao os parametrizados de arma, onde o parametro faz parte do nome.
Formatador com as convencoes do PF2e: dado minusculo (`Deadly d8`), letra de
dano maiuscula (`Versatile P`), numero solto e distancia (`Thrown 20 ft.`). Um
teste varre a base cobrando que nenhum trait saia em minuscula.

## 10. Desempenho -- onde ele importa
- **derivacao**: 0,30 ms para nivel 20. Nao e gargalo.
- **listas**: o picker de Free Archetype tem 2.128 feats e o de equipamento
  6.122. Renderizar tudo a cada tecla engasgava a busca. `ListaVirtual` mantem
  so a janela visivel; os espacadores preservam a barra de rolagem do tamanho
  real -- **nao e paginacao e nao esconde nada**.
- **primeira carga**: 54 requisicoes em paralelo. Serializar multiplicaria a
  latencia pelo numero de kinds.

## 11. O que o app NAO faz, de proposito
Dice tray, multiplos personagens abertos, modo Play, condicoes, PDF, GM mode,
login, IndexedDB, retraining. Registrados em
`docs/referencia-pathbuilder/ui-arquitetura.md` como material para decidir
depois -- nao como esquecimento.

## 12. Contrato com o pipeline
O app **nunca corrige dado**. Onde a base esta errada, corrige-se o pipeline e
re-emite. A tela pode *formatar* (limpar marcacao, dar caixa a um slug), nunca
*fabricar*.

Caso que fixou a regra: 260 das 326 herancas nao tem trait em fonte nenhuma. A
tentacao era derivar `traits: ["human"]` do vinculo `ancestry`. Recusado --
faria `_termo_trait` satisfazer requisito com dado inventado. A tela mostra o
**vinculo como vinculo**, marcado.

### Consertos de dado aplicados em 2026-07-28
| achado | conserto | onde |
|---|---|---|
| 407 feats de arquetipo sem exigir a dedicacao | derivado da regra do livro | `derivar_gate_arquetipo.py` |
| 47 ids orfaos em `requires`/`subclasses` (remaster renomeou) | aliases aplicados **depois da fusao** | `aplicar_aliases_em_requires.py` |
| a mesma opcao em dois kinds (`wb:cause/justice` e `wb:class-feature/justice`) | fica quem tem mais sinal | `colapsar_opcoes_irmas.py` |
| Fighter Dedication so treinava armas simples | curadoria (o Foundry tambem erra) | `correcoes_curadas.json` |
| `grants_completos: true` sem mecanica declarada | passa a `None` | `comum.py` |

### A ordem do `build.sh` e uma decisao, nao arrumacao
Um passo que conserta REFERENCIA tem que rodar depois de quem MATA o id. Vale
para `aplicar_aliases_em_requires.py`: ele nasceu no passo 4h3, antes da fusao,
e ali nao havia orfa nenhuma para consertar -- quem aposenta o id e a fusao, no
passo 7. A orfa nascia logo depois, sem ninguem para reescreve-la. Sintoma: o
eixo `arcane-thesis` do Mago oferecia uma opcao apontando para o nada, e a base
saiu assim com **os nove portoes verdes**.

Corrigido movendo o passo para 7c (pos-fusao). Efeito medido: 26 -> 47 ids
resolvidos.

O caso deixou uma segunda licao, mais cara que a primeira: **o portao 3 era cego
ao campo que existe para ser consertado**. Ele varria `requires` e nunca
`subclasses[].opcoes`, entao a verificacao nao cobria o conserto. Ampliado, ele
acusou 16 orfas na hora -- todas invisiveis ate ali. Portao que nao vigia o
passo correspondente e decoracao.

E uma terceira: consertar a orfa **revelou** a duplicata que ela escondia. Com o
id morto vivo de novo, o Campeao passou a oferecer `Justice` duas vezes -- uma
por `wb:cause/justice`, outra por `wb:class-feature/justice`, dois registros da
mesma coisa em kinds diferentes, que a fusao nao pareia porque ela compara
dentro do kind. Dai `colapsar_opcoes_irmas.py` (passo 7d): dentro de um eixo,
nome repetido vira uma opcao so, e fica **quem tem mais sinal** -- tem `grants`,
tem `traits`, tem prosa, e so em ultimo caso o kind `class-feature`. O criterio
e por sinal e nao por kind de proposito: no dia em que a casca for a mais rica,
ela ganha sozinha. O passo reescreve REFERENCIA e nao deleta registro -- os
kinds dedicados nao sao citados em nenhum outro lugar da base (52 citacoes,
todas em `subclasses`), entao o perdedor continua no acervo, buscavel.

**Nao consertavel por extracao**, e registrado como divida: 61 das 226
dedicacoes nao tem mecanica em fonte nenhuma (no Foundry, 45 de 192 tambem tem
zero rule elements), e nenhuma dedicacao de conjurador concede spellcasting.
Exige mecanizacao manual via curadoria.

## 13. Como verificar que esta certo
```bash
cd app && npx tsc -b --noEmit && npx vitest run    # 107 testes
cd ../motor && python3 teste_motor.py              # 97 assercoes, o oraculo
cd ../pipeline && python3 portoes.py --fase final  # 9 portoes
cd ../app && node verificacao/verificar-eixos.mjs  # na tela, com o app de pe
```
O ultimo e o unico que roda no NAVEGADOR, e existe porque os outros tres
passaram verdes sobre uma base que oferecia `Justice` duas vezes ao jogador.
Verificacao de dado nao substitui olhar a tela.

**O oraculo nao e opcional.** O Python e o gabarito: `gerar_fixtures.py` congela
20 fichas e o TS compara campo a campo. Qualquer mudanca em `candidatos` ou
`_aceita_no_slot` entra **nas duas implementacoes**, roda os 95 testes do
Python, regera as fixtures, e so entao os do TS. Corrigir so o lado da frente
cria duas regras divergentes em silencio -- ja aconteceu, e foram 20 testes
vermelhos de uma vez que avisaram.

Mudou a base? `pipeline/build.sh`, depois `app/sincronizar-base.sh`.

---

## 14. Estado em 2026-07-29

### Consertos de dado (todos no pipeline)
| conserto | passo no build.sh | resultado |
|---|---|---|
| gate de arquetipo derivado da regra do livro | `derivar_gate_arquetipo.py` (4h2) | 407 feats |
| mecanica de equipamento nao casada | `recuperar_mecanica_equipamento.py` (4h4) | arma 110->54, armadura 14->5, escudo 7->5 |
| aliases do remaster em `requires` e `subclasses` | `aplicar_aliases_em_requires.py` (**7c**, pos-fusao) | 47 ids resolvidos; portao 3: 16 -> 0 |
| opcao publicada em dois kinds | `colapsar_opcoes_irmas.py` (7d) | 15 referencias em 3 classes |
| raridade e Fighter Dedication | `correcoes_curadas.json` | 7 correcoes |

### Consertos de verificacao
- portao 3 passa a varrer `subclasses[].opcoes`, nao so `requires` -- era cego
  justamente ao campo que o passo 7c conserta
- `app/verificacao/verificar-eixos.mjs`: checagem no navegador, porque os nove
  portoes ficaram verdes sobre uma base com opcao duplicada na tela
- `sincronizar-base.sh` limpa o CONTEUDO de `public/base`, nunca o diretorio:
  `rm -rf` derrubava o Vite em execucao, que passava a servir `index.html` no
  lugar do JSON -- com o arquivo intacto no disco

### Consertos de app
- prosa separada em regra/sabor (`prosa.ts` + `Prosa.tsx`)
- marcacao `{@tag}` limpa, com aninhamento (`marcacao.ts`)
- trait com caixa correta, inclusive parametrizado (`nomeDeTrait.ts`)
- funil do picker (`Funil.tsx`) e lista virtualizada (`ListaVirtual.tsx`)
- inventario (`Equipamento.tsx`) -- a porta que faltava para arma e armadura
- gate de heranca por ancestralidade, no motor
- `navigateFallbackDenylist` para `/base/` e `buscarJson()` com erro que explica
- trocar a classe de um nivel **zera o que dependia dela** dali para a frente
  (`class_feat`, `subclasse`, `free_archetype`) -- ancestralidade, antecedente e
  pericia ficam. Sem isso um feat de Alquimista sobrevivia num Campeao
- o eixo entra na chave da sub-escolha: as tres sub-escolhas do Campeao gravavam
  em `(slot:"subclasse", em:1)` e uma sobrescrevia a outra. O motor nao mudou --
  ele varre `_escolhas("subclasse")` inteiro e casa por `pega`
- item concedido abre em leitura (`Detalhe.tsx`), com traits e prosa em partes

### Divida conhecida, com dono
| item | onde | por que nao foi feito |
|---|---|---|
| 56 dedicacoes sem mecanica (eram 61) | `base/relatorio_mecanica_dedicacao.md` | **a premissa mudou** -- ver abaixo |
| familiar, eidolon e companheiro construct/undead | `base/relatorio_concessao_de_ator.md` | o companheiro ANIMAL foi fechado em 2026-07-29; os outros tres tem stat block proprio (ou nenhum) |
| spellcasting de dedicacao de conjurador | idem | o motor nao tem modelo de spellcasting de arquetipo |
| 54 armas sem dano | `base/relatorio_mecanica_equipamento.md` | 41 sao bombas (dano e do efeito), 36 sao modos de arma de combinacao |
| 5 armaduras / 5 escudos | idem | declaram MATERIAL, nao item base (`Elven Chain`, `Mithral Shield`) |
| 5 feats candidatos, 23 familias com `xref` suspeito | `docs/comparacao/triagem-feat.md` | precisa revisao item a item |
| 2 orfas sem alias | `base/relatorio_aliases_requires.md` | `wb:heritage/versatile` e `you-have-a-versatile` sao ruido de parse |

### As 61 dedicacoes: a premissa estava errada
O plano dizia que so o Pathbuilder resolveria, porque a mecanica "nao existe em
fonte estruturada". Medindo as 61 uma a uma, o buraco nao e de FONTE, e de
MODELO -- e por isso o Pathbuilder tambem nao resolveria:

| natureza do efeito | quantas | o motor sabe? |
|---|---|---|
| proficiencia / treino de pericia | 17 | sim -- `proficiency`, `skill_training` |
| modificador numerico (dado de dano, penalidade) | 17 | nao |
| companheiro (animal, eidolon, familiar, drake) | 16 | nao |
| spellcasting de arquetipo | 14 | nao |
| item/feat nomeado concedido | 9 | sim -- `grant_feat` |

`derivar_mecanica_dedicacao.py` (passo 7e) colhe o que o motor sabe consumir,
**da prosa oficial que ja temos**, e mecanizou 5. O numero e baixo de proposito:
o passo so emite quando (a) o sujeito da frase e "you" e (b) o alvo resolve para
um registro existente. As duas guardas nasceram de erro real --
`Animal Trainer` diz "This trained animal is trained in Performance", e o
cabecalho traz "Prerequisites Trained in Nature"; sem elas o jogador ganhava
pericia que a regra nao deu. `Rose Warden` foi o caso mais claro: a versao sem
guarda dava Stealth de graca, quando a regra e "expert in your choice of
Deception **or** Stealth".

Os 25 restantes viram **divida declarada** no relatorio, com o que a prosa
promete, em vez de ficarem invisiveis.

O que sobra depende de decisao de produto, nao de colheita: modelar companheiro
e spellcasting de arquetipo no motor. Ate la, nem Pathbuilder nem prosa ajudam
-- nao ha onde guardar a resposta.

### 2026-07-29: companheiro concedido -- a segunda premissa errada
"Falta modelar companheiro no motor" tambem era falso. O motor implementa
companheiro INTEIRO nas duas linguagens (cap da regra 17b, maturidade
young/mature/nimble/savage, Specialized, HP, AC, ataques, support). O que
faltava era a ponta anterior: **nenhum registro da base dizia "eu concedo um
companheiro"**, entao o ator so entrava por `doc["atores"]` escrito a mao e
pegar `Animal Companion` no nivel 1 nao mudava nada -- sem slot, sem aviso.

Fechado pela spec `specs/2026-07-29-companheiro-concedido.md`:

| camada | o que entrou |
|---|---|
| dado | termo `grant_actor`, derivado da prosa em `derivar_concessao_de_ator.py` (passo **7f**) -- 12 concessores, 4 de divida (construct/undead), 1 vetado (Dragon Grip da ACESSO a especie, nao companheiro) |
| motor | `_concessoes_de_ator`, casamento por `concedido_por` + `em`, slot `companheiro` em `slots_abertos`, `candidatos("companheiro")` com as 96 especies (as 17 sem stat block sao especializacao) |
| regra 17b | o cap passa a sair da classe que CONCEDEU. Num `Ranger 3 / Fighter 5` o companheiro do Ranger dava 7 e agora da 5 |
| app | o slot nasce no nivel do feat, a escolha grava em `doc.atores`, e a ficha ganha a aba do bicho |
| prova | 9 assercoes novas no Python, fixture `ranger3-guerreiro5-companheiro-concedido` comparada campo a campo pelo TS, e `app/verificacao/verificar-companheiro.mjs` no navegador |

Segue na divida, agora **declarada em relatorio**: companheiro construct (3
feats) e undead (1), familiar (29 feats + Witch + 18 lessons + 16 patrons),
eidolon (Summoner + 63 feats) e `access` a especie.

### Ponto de retomada
Comparacao pratica com o Pathbuilder (`docs/plano-comparacao-pathbuilder.md`,
frentes 2 e 3): montar o mesmo personagem nos dois e comparar quais feats abrem
por slot. O Pathbuilder vale como oraculo de COMPORTAMENTO -- a tese do Fable --
e o export JSON dele (`build.proficiencies`, `build.specials`) da o estado da
ficha em numero, sem precisar ler icone na tela.
