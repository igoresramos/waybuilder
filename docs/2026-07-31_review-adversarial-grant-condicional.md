# Review adversarial -- spec `2026-07-31-grant-condicional.md`

Coordenado com quatro sub-agentes de medicao independente (Sonnet), cada
afirmacao refeita contra a fonte (`pipeline/dados_brutos/foundry_repo/packs/pf2e`),
a base (`pipeline/base/index.json`) e os dois motores. Os achados que mudam
veredito foram conferidos pelo coordenador com os proprios olhos antes de
escrever. Scripts descartaveis viveram no scratchpad da sessao; nada do projeto
foi alterado alem deste relatorio.

---

## A) "As 206 sao redundantes com o eixo; nada a fazer" -- CAI

**Medicao.** Os totais da spec conferem casa a casa: 206 item-scope + 15
actor-scope = 221; dentro das 206, 165 com `filter`, 36 lista literal, 4 sem
`choices`, 1 orfa (`Runtsage`). O que NAO confere e a conclusao. Testada a
correspondencia de cada dono com os caminhos de alcance do nosso modelo
(eixo em `subclasses[]` -- inclusive eixo com `opcoes: []` e `filtro`, e via
gemeo `equivale_a` --, conversores dedicados, e slot concedido generico do
item 106), a particao real e:

| grupo | n (aprox.) | situacao |
|---|---:|---|
| auto-referentes tipo `Cause` (escolher = ter, eixo existe) | 84 | spec certa |
| feats/heritages com slot `choice` extraido (ex.: os 26 `Basic X`) | ~50-70 | conclusao certa, justificativa errada: a redundancia e com o SLOT do item 106, nao com o eixo. Conferido em `wb:feat/basic-fury`: o bloco `{"choice": ...}` existe na base e o picker pergunta |
| **backgrounds achatados** | **19** | **bug ATIVO de sobre-concessao**: `Beast Seeker` na fonte e ChoiceSet de 1 entre 2 (Titan Wrestler OU Dirty Trick) + GrantItem dinamico; na base virou `grant_feat: ["wb:feat/titan-wrestler", "wb:feat/dirty-trick"]` e o motor concede OS DOIS (laco de `motor.py:4103-4137` nao tem condicao). Nao e "pulado", e convertido ERRADO |
| class-features sem mecanismo nenhum | ~30-50 | furo real: `grants: []`, sem eixo, sem slot. Familias identificadas: escolha de impulso do Kineticist (~16), `grantedIkon` do Exemplar (9, a arma fisica do ikon), cadeia adept/paragon do Taumaturgo (4), sub-escolha de divindade (3: `Deity (Cleric)`, `Deity (Champion)`, `Mortal Herald`), e singulares |

A "terceira forma" que a spec nega existir, existe: uma decisao que a fonte
declara e que NENHUM caminho nosso pergunta. A frase "nao ha o que implementar
aqui" vale para ~84 casos verificados, nao para 206.

**Ressalva de metodo.** O numero fino de cada grupo (a divisao entre
"coberto por slot" e "sem mecanismo") foi medido por um sub-agente e conferido
por amostragem pelo coordenador (1 caso de cada grupo, nos dois sentidos); a
particao exata pede re-derivacao pelo proprio pipeline. A DIRECAO nao muda:
ha dezenas de furos e 19 conversoes ativamente erradas.

**Emenda.** Reescrever a secao "As 206 ja estao resolvidas" e o ponto 1 de
"o que NAO resolve": (i) trocar "redundante com o eixo" por "redundante com um
caminho de alcance existente (eixo, slot concedido ou conversor dedicado)",
com a particao medida e o relatorio do pipeline declarando em qual grupo cada
uma caiu; (ii) declarar os grupos SEM caminho como divida aberta com numero;
(iii) abrir item de TODO proprio, fora desta spec, para os 19 backgrounds
achatados -- e defeito que ja esta na ficha hoje, independente de `se`.

---

## B) Os 79 pares / 64 acionaveis -- CAI

**Medicao.** Sob o criterio que a propria spec declara (ActiveEffectLike
`flags.system.*` com UUID x GrantItem de escopo `actor`), saem **44 pares**,
nao 79: Gunslinger 10, Clerigo 12, Taumaturgo 10, Alquimista 12, e ZERO
`Spell Effect:`. Os 15 leitores actor-scope conferem, e nenhum escritor/leitor
existe fora dos packs que a spec olhou (varrido o repo inteiro, incluindo
sf2e). O 79/64 so se reproduz trocando de criterio em silencio -- incluindo
leitores de escopo ITEM via ChoiceSet (`Implement Adept`, `Implement Paragon`)
e escolhendo 1 leitor por flag entre 3 existentes (`Second Adept` e `Intense
Implement` leem a mesma `adeptChoices`; contados com a mesma regua, o
Taumaturgo daria 50 pares, nao 30).

**O erro que importa mais que o numero** (conferido pelo coordenador na
fonte, `class-features/amulet.json` e `implement-adept.json`): Adept e Paragon
do Taumaturgo NAO sao pares estaticos. `Amulet` ADICIONA uma entrada na lista
`flags.system.thaumaturge.adeptChoices` (mode `add`, predicate
`class:thaumaturge`, value com template dinamico `{item|name}`), e `Implement
Adept` (nv 7) apresenta um **ChoiceSet sobre essa lista** e concede o
ESCOLHIDO. E "escolha UM dos seus implements para avancar" -- escolha
filtrada pelo que se tem, nao grant condicional. Modelado como a spec manda
(`se: {has: amulet}`), um Taumaturgo 7 com Amulet e Wand (Second Implement e
progressao normal, nv 5) receberia OS DOIS adept benefits -- numero errado na
ficha, exatamente o que a spec diz evitar. A afirmacao "a opcao declara o mapa
INTEIRO, estaticamente" e falsa para as 10 entradas de `adeptChoices`.

**O que sobrevive, verificado limpo:** Clerigo 12/2 e Alquimista 12/4
(`Cloistered Cleric` e `Bomber` sao `override` com mapa estatico completo,
sem predicate -- conferido). Gunslinger 10/5 confere como par, mas ver E.
Orfaos que a spec nao menciona: 3 flags do Alquimista
(`perpetualPerfection/Infusions/Potency`) tem leitor e NENHUM escritor --
cadeia quebrada na propria fonte.

**Emenda.** (i) Corrigir a medicao central: 44 pares sob o criterio declarado;
(ii) RETIRAR o Taumaturgo desta spec -- a familia dele e um slot/eixo de
escolha filtrado pelos implements possuidos (o mesmo desenho de eixo por query
ja existente), nao `se`; com isso cai tambem a frase "a cadeia de dois lances
so exercita a recursao" e a linha "Taumaturgo bate 30/30" da sobreposicao com
o item 69; (iii) declarar os 3 leitores orfaos do Alquimista; (iv) o escopo
util da spec passa a ser Clerigo 12 + Alquimista 12 = 24 pares aplicaveis
hoje, + Gunslinger 10 bloqueados pelo pack (ver E).

---

## C) A inversao de default -- SOBREVIVE COM EMENDA

**Principio zero: nao viola.** A leitura da spec ja esta assentada no codigo:
`avaliar()` (motor.py:2549) declara "nunca e usado para negar uma escolha", e
o docstring de `_grants_em_cadeia` (4004-4010) distingue explicitamente
"bloquear a ESCOLHA" de "esconder o efeito de escolha ja feita". Conceder a
variante da subclasse errada poe numero errado na ficha -- pior, para o
jogador, do que marcar. O argumento se sustenta.

**Dois defaults na mesma gramatica: o risco e real e ja foi pago tres vezes**
-- linha 2578 (`continue` do termo desconhecido), o `not` invertido de
`_casa_filtro` (3560-3572, achado do item 106), e o envelope `{"and": ...}`
do item 108 que virou no-op em DOIS passos. A spec mitiga com o modo estrito,
mas cobre so "termo desconhecido" e deixa tres buracos:

1. **Chave estrutural desconhecida no topo** -- o caso exato do item 108.
   `avaliar()` itera `predicado.items()` e engole chave que nao e
   `all`/`any`/`not` nem termo. O modo estrito precisa devolver INDECIDIVEL
   para CHAVE desconhecida, nao so para termo.
2. **`not(INDECIDIVEL)`** nao e definido pela spec. O precedente ja existe no
   codigo (`_filtro_indecidivel`): indecidivel sob negacao continua
   indecidivel, nunca decide o NAO. Escrever isso.
3. **Tipo de retorno.** `avaliar()` devolve `(bool, motivos)`; um modo
   estrito embutido por flag e o vazamento de modo esperando acontecer.
   Avaliador proprio (tri-state, vocabulario fechado), reusando os `_termo_*`
   -- como `_atomo_de_filtro` ja faz com `None` = "nao sei".

**O desenho melhor existe e e barato: portao de BUILD.** Todo `se` da base
nasce de UM passo de pipeline que so escreve `{has: <id>}`. Um portao que
valide, no build, que todo `se` usa apenas o vocabulario que o avaliador
estrito sabe decidir (e que todo alvo de `has` resolve) transforma o
INDECIDIVEL de runtime em linha de defesa que nunca dispara -- o erro morre
no build, nao na ficha de um usuario. A prova 6 continua existindo, mas como
teste do mecanismo de defesa, nao como unica barreira.

**Emenda.** Acrescentar a secao da regra: os itens 1-3 acima e o portao de
build como barreira primaria.

---

## D) Ordem de avaliacao -- CAI (como esta escrito)

**O que a spec afirma e verdade -- e insuficiente.** Verificado:
`_features_de_classe()` (motor.py:250) roda antes de `_grants_em_cadeia()`
(254) e poe a opcao de subclasse escolhida em `self.features` (376, 458-466);
idem no TS (personagem.ts:222/226). Para `se: {has: <opcao de subclasse>}` --
o caso Clerigo/Alquimista -- a ordem e segura.

**Onde quebra:** `origens` e um SNAPSHOT (4028) percorrido em passada UNICA,
sem fixpoint, enquanto `self.features`/`self.concedidos` crescem AO VIVO
durante a propria cadeia (4063-4065) e `_termo_has` os le ao vivo. Um `se`
que dependa de item concedido pela MESMA cadeia devolve `True` ou `False`
conforme a posicao da origem no snapshot -- e `False` explicito, pela regra 3
da spec, **descarta em silencio, sem pendencia**. A ficha sai errada e limpa.
Os dois motores tem a mesma estrutura (TS 4243-4301), entao a paridade nao
acusaria: os dois errariam IGUAL, deterministicamente.

**A prova 5 da spec nao pega isso.** Embaralhar as escolhas do DOCUMENTO nao
reordena o snapshot de origens, que vem da ordem das features de progressao.
O teste de invariante certo embaralha a ordem das ORIGENS -- e a licao do
corpus (LESSONS: "321 embaralhamentos passaram ate existir ficha
multiclasse") vale de novo aqui.

**Mais dois fatos medidos que a spec nao trata:** durante a cadeia,
`_avaliando_em` e `_avaliando` sao `None` nos dois motores (so sao setados em
`_checar_requisitos`, que roda depois) -- logo um `se` avaliado na cadeia roda
(i) SEM recorte temporal (spec 2026-07-29) e (ii) SEM exclusao por raiz: pode
ser satisfeito por algo que o proprio grant concedeu, a circularidade exata da
licao do `acrobat-dedication`.

**Atenuante que nao salva:** com a emenda B (Taumaturgo fora), nenhum par
restante da spec depende de item concedido na propria cadeia -- Clerigo e
Alquimista condicionam so em opcao de subclasse, que esta pronta antes. Mas o
vocabulario `se` e GERAL ("um campo, opcional, em qualquer entrada de
grants"): a primeira base futura que escrever um `se` encadeado reintroduz o
defeito sem tocar no motor. Vocabulario geral pede semantica geral.

**Emenda.** Escolher e escrever na spec UMA das duas: (a) fixpoint -- repetir
a passada da cadeia ate nenhum `se` mudar de valor (com guarda de rodadas;
grants sao monotonicos, entao converge); ou (b) fila de pendentes -- `se`
indecidido-ou-falso re-avaliado ao fim da cadeia antes de virar descarte.
Definir tambem: `se` avalia com recorte temporal? com exclusao por raiz?
(recomendo: raiz SIM, pela licao do acrobat; recorte temporal declarado
explicitamente). E trocar a prova 5 por embaralhamento de ORIGENS.

---

## E) O que a spec declara nao resolver -- SOBREVIVE COM EMENDA

**Confirmado com evidencia direta:**
- Os 9 alvos do Gunslinger vivem em `packs/pf2e/actions/class/gunslinger/` e
  nao existem na base (busca por nome, slug e alias); o pack `actionspf2e`
  nao esta em `PACK_PARA_KIND` e nao ha kind `action`. (Ressalva literal:
  `taticas_kits.py` LE arquivos desse pack, mas so licenca das taticas do
  Commander -- a afirmacao substantiva fica de pe.)
- O Campeao: confirmado nos dois sentidos. `Justice` concede `Retributive
  Strike` por GrantItem com UUID **estatico** e `predicate`
  (`{"or": ["class:champion", "feat:champions-reaction"]}`);
  `converter_rule_elements.py:124-127` pula GrantItem com predicate
  incondicionalmente (relatorio oficial: 293, bate); `Retributive Strike` e
  `Liberating Step` estao no mesmo pack `actionspf2e`, ausentes da base. O
  item 107 aponta mesmo a familia errada -- **a spec ganha essa disputa**, e
  o TODO 107 deve ser corrigido.
- `Runtsage` confirmado orfa, com precisao: o item TEM ChoiceSet irmao, mas
  SEM campo `flag` -- nada escreve `rulesSelections.runtsage`. Defeito da
  fonte.

**O que cai:** "o Gunslinger entra com 1 dos 10 pares funcionando" e falso.
O 10o alvo, `Into the Fray`, resolve por colisao de nome para
`wb:feat/into-the-fray` -- o feat de arquetipo VIKING (nv 8, carga com
escudo), item sem relacao com a deed. Com a resolucao por pack que a propria
spec prescreve no passo 3, `actionspf2e` nao resolve e o par morre no
relatorio: **0 de 10**, e o unico "funcionando" seria uma concessao errada.

**Emenda.** Corrigir o ponto 2 de "nao resolve" para 0/10, citando a colisao
Viking como o motivo de a resolucao por pack ser obrigatoria tambem aqui; e
anotar no ponto 1 a precisao do Runtsage (ChoiceSet sem flag).

---

## F) O que ninguem olhou -- tres riscos reais

1. **Dupla via para o mesmo item.** As variantes que o `se` passa a conceder
   continuam existindo como OPCOES escolhiveis -- no gate do item 69 e, no
   Taumaturgo, em tres eixos `outras-opcoes` (niveis 1/7/17) que hoje pedem
   escolha do jogador. `_ja_tenho` impede a dupla APLICACAO, mas a spec nao
   diz o que acontece com o eixo/slot que fica aberto pedindo uma escolha que
   o grant ja fez -- pendencia fantasma na UI, e um jogador que escolher a
   variante da OUTRA subclasse (permitido pelo principio zero) fica com as
   duas na ficha. A spec precisa declarar o comportamento dos dois lados.
2. **Motor velho + base nova concede TUDO.** "Ausencia de `se` significa
   incondicional" implica que um motor que nao conhece `se` ignora o campo e
   aplica todos os grants da entrada -- todas as variantes de uma vez, o
   defeito exato que a spec quer evitar. Nao e hipotetico: o projeto ja teve
   service worker de build anterior servindo app velho (LESSONS). Pede guarda
   de versao no payload da base (motor recusa base com vocabulario que nao
   conhece) ou, no minimo, declaracao do risco e do porque de aceita-lo.
3. **Multiclasse: seguro no desenho atual, por sorte de dados.** Clerigo 3 /
   Alquimista 2 dispara leitores das duas classes e as condicoes discriminam
   por opcao de cada eixo -- ok. Mas a seguranca vem de as flags serem
   namespaced por classe NA FONTE (`flags.system.cleric.*`); o pipeline deve
   preservar esse namespace na chave do par (nao so o nome da flag), senao
   uma colisao futura de nome de flag entre classes cruza os pares.

`equivale_a`/gemeos e recorte temporal do `has` ja estao cobertos em C/D.
Ficha salva sobrevive a mudanca de vocabulario pelo principio 3 (re-derivacao)
-- sem risco novo alem do item 2 acima.

---

## Veredito global

**A spec CAI como esta e precisa de revisao antes de qualquer implementacao.**
O nucleo conceitual sobrevive: o vocabulario `se`, o modo estrito com
pendencia, e a leitura do principio zero sao solidos e bem ancorados no
codigo. Mas as DUAS medicoes que dimensionam a spec estao erradas -- a
redundancia das 206 (ha dezenas de furos e 19 conversoes ativamente erradas)
e os 79/64 pares (44 sob o criterio declarado, e a maior familia, o
Taumaturgo, e escolha e nao grant condicional) -- e a garantia de ordem que a
spec chama de segura tem um buraco silencioso que a propria bateria de provas
nao exercita.

### O que corrigir ANTES de implementar, em ordem

1. **(B) Recortar o escopo dos pares.** Clerigo 12 + Alquimista 12 sao o
   conteudo aplicavel; Taumaturgo SAI para spec propria (slot filtrado por
   implements possuidos); Gunslinger declarado 0/10 ate `actionspf2e` ser
   extraido; refazer a tabela e a sobreposicao com o item 69.
2. **(D) Fechar a semantica de ordem.** Fixpoint ou fila pos-cadeia; recorte
   temporal e exclusao por raiz definidos para `se`; prova de determinismo
   embaralhando ORIGENS.
3. **(A) Reescrever a secao das 206** com a particao medida (redundante com
   eixo / redundante com slot / sem mecanismo / achatado) e relatorio do
   pipeline por caso. Abrir TODO proprio para os **19 backgrounds achatados**
   -- bug ativo hoje, nao depende desta spec.
4. **(C) Endurecer o avaliador estrito**: chave desconhecida (nao so termo),
   `not(INDECIDIVEL)` = INDECIDIVEL, avaliador tri-state proprio, e o portao
   de BUILD do vocabulario de `se` como barreira primaria.
5. **(E) Corrigir os numeros declarados**: Gunslinger 0/10 (colisao Viking),
   Runtsage com ChoiceSet sem flag; corrigir o TODO 107 (a spec ganha a
   disputa sobre o Campeao).
6. **(F) Declarar**: comportamento do eixo/gate quando o grant ja decidiu;
   guarda de versao motor/base; namespace de classe na chave do par.
