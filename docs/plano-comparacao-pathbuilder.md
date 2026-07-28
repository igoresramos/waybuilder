# Plano de acao -- comparacao Waybuilder x Pathbuilder

Escrito em 2026-07-28 a pedido do Igor, em duas propostas independentes (uma
minha, uma do Fable) e consolidado aqui. Onde as duas divergiram, a divergencia
esta dita e resolvida, nao apagada.

**Nada deste plano foi executado ainda.** Ele existe para ser aprovado antes.

---

## 0. A tese que reorienta tudo

> **O Pathbuilder nao e oraculo de DADO. E oraculo de COMPORTAMENTO.**

Esta e a contribuicao do Fable, e ela muda a ordem de tudo o que vem abaixo.

Nossa base sai de tres fontes (Foundry, Pf2eTools, dump do AoN) e e **mais nova**
que a do Pathbuilder. Ja tenho a prova medida: `Reactive Shield` tem traits
`[fighter, guardian]` aqui e so `Fighter` la, porque Guardian e Commander sao
classes de 2025 que aquele install nao conhece. Comparar campo a campo contra o
Pathbuilder inverteria a direcao da verdade -- geraria milhares de diferencas
**onde nos estamos certos**, e a triagem consumiria o projeto.

O que o Pathbuilder tem que nos nao temos nao e dado: e **logica curada a mao**.
O que aparece em cada slot, como o filtro reage ao contexto, e sobretudo a
mecanica das dedicacoes -- que, medido, **nao existe estruturada em fonte
nenhuma** (61 das 226 dedicacoes tem `grants: []` aqui; no Foundry, 45 de 192
tambem tem zero rule elements).

Disso decorrem duas regras que valem para o plano inteiro:

1. **Compare listas de slot e elegibilidade, nao fichas de item.** Detalhe de
   item so entra quando presenca, nivel ou pre-requisito ja divergiram.
2. **Divergencia de campo mecanico se resolve contra o AoN, nunca copiando o
   Pathbuilder.** Ele e o detector de suspeita; a fonte e o juiz.

Isto contraria em parte o pedido literal ("quanto mais parecido com o
Pathbuilder melhor"). A meta correta e **fidelidade ao RAW**, com o Pathbuilder
como instrumento. Onde ele estiver desatualizado, parecer com ele seria piorar.

---

## 1. Onde eu divirjo do Fable

**Flag de RAW puro.** O Fable pede uma flag que desligue a houserule, sem a qual
toda comparacao estaria contaminada. O diagnostico esta certo, a solucao nao.

O problema real e mais estreito do que ele supos: personagem **mono-classe ja e
RAW** -- a regra da casa so aparece quando os niveis se dividem. O que contamina
de verdade e outra coisa: a **regra 2, Free Archetype sempre ligado**, que da
slot de arquetipo em todo nivel par e nao tem como ser desligada (esta fixa em
`personagem.ts`, `faixa.filter(n => n % 2 === 0)`).

Solucao melhor: **ligar o Free Archetype no lado do Pathbuilder**, que ja
oferece a variante oficial em `Character Options`, em vez de criar uma flag para
desligar a regra da casa no nosso lado. Nao mexe no motor, nao inventa modo de
execucao que so o comparador usa, e compara a variante que o Igor de fato joga.

Fica um item de Fase 0 mais barato: **confirmar que o toggle existe no
Pathbuilder e liga-lo na sonda**.

**Heranca sem trait.** O Fable manda tirar da pauta por ser modelagem, nao
comparacao. Concordo, e ja esta resolvido: o vinculo `system.ancestry` e exibido
como vinculo, e o gate de heranca por ancestralidade ja esta no motor com tres
testes. Nao entra no plano.

---

## 2. Fase 0 -- antes de qualquer coleta em massa

| # | item | por que primeiro |
|---|---|---|
| 0.1 | Ligar Free Archetype na sonda do Pathbuilder (confirmar o toggle em `Character Options`) | sem isso toda lista de slot diverge por construcao |
| 0.2 | Corrigir o que ja sabemos sem comparador: 23 sub-escolhas ausentes (6 causas do Campeao, 8 patronos da Bruxa), `One for All` | rodar comparacao antes so redescobre o conhecido e polui o relatorio |
| 0.3 | Endurecer o extrator: seletores num modulo unico, snapshot de DOM como fixture, contexto persistente unico, coleta **serial** | o Pathbuilder e app de terceiro atras de Cloudflare; layout muda e coleta paralela derruba |
| 0.4 | Verificar o **Feat Browser** do Pathbuilder (menu > Data) | se ele listar catalogo sem montar personagem, o custo de coleta despenca. **Ainda nao confirmado** -- minha primeira tentativa nao abriu a tela |

---

## 3. Ordem de ataque

A ordem do pedido era classes -> dedicacoes -> racas -> armas -> pets -> magias.
A ordem abaixo diverge, e o motivo esta em cada linha.

### 1. Colheita das dedicacoes -- **prioridade maxima**
Nao e comparacao, e **colheita**. As 61 dedicacoes sem mecanica nao tem fonte
estruturada em lugar nenhum, e o Pathbuilder e o unico lugar onde essa mecanica
existe codificada. Finito (226 itens) e de valor unico.

Sai daqui: o que cada dedicacao concede, o spellcasting de arquetipo, os feats
que ela libera. Entra como curadoria, com a guarda de `valor_atual`.

### 2. Classes -- progressao e class features
Amostrar niveis 1/5/10/15/20 nas 27 classes. Erro aqui quebra **todo**
personagem daquela classe: e motor, nao dado. Comparar features concedidas por
nivel, proficiencias e quais slots o nivel abre.

### 3. Listas de slot por contexto
Class feat, skill feat, general feat, ancestry feat, com personagens-sonda. E
onde a elegibilidade aparece -- a categoria de defeito mais cara e a mais
invisivel sem comparador.

### 4. Ancestralidades e herancas
Cruzamento de catalogo: presenca e nivel. Barato, offline.

### 5. Magias
**So presenca, nivel, tradicao e heightening. Nunca texto** -- diferenca de
wording OGL/ORC e ruido garantido.

### 6. Armas, armaduras, escudos, equipamento
Cruzamento offline de campo mecanico (dano, traits, bulk, preco). Dado estatico,
risco baixo, por ultimo.

### 7. Pets -- **fora do escopo automatizado**
O Pathbuilder poe a secao atras de paywall ("only available in the fully
unlocked version"). Nao se automatiza contra paywall. Os 113
`animal-companion` se conferem **contra o AoN**, por amostragem manual.

---

## 4. Granularidade: hibrida, com dump cacheado

- **Uma passada de coleta por frente**, nunca uma por comparacao. A sonda monta o
  personagem no Pathbuilder, abre cada slot e **despeja a lista para disco**
  (JSON datado, versionado). Todo cruzamento posterior e offline e
  re-executavel sem tocar no app de terceiro.
- **Comparacao viva pareada** so para amostra contextual: 3 a 5 builds por classe
  com atributos e escolhas anteriores diferentes, para ver se o **filtro**
  coincide -- o que some e o que aparece quando o contexto muda. E onde bug de
  motor mora.

---

## 5. Taxonomia da divergencia

Sem isto a saida vira lista de 5.000 linhas que ninguem le.

| cat | significado | destino |
|---|---|---|
| **D-CONTEXTO** | mesmo personagem, o slot lista coisa diferente | bug de motor -- P0 |
| **B-SOBRA-ERRO** | temos a mais, e a elegibilidade esta errada | bug de motor -- P0 |
| **A-FALTA** | o Pathbuilder tem, nos nao | validar no AoN, depois adicionar -- P1 |
| **C-CAMPO** | nivel, pre-requisito ou trait mecanico difere | julgar **contra o AoN** -- P2 |
| **B-SOBRA-NOVA** | temos a mais, conteudo posterior aquele install | esperado -- `wontfix` datado |
| **F-RUIDO** | rename de remaster, wording, ordenacao | tabela de mapeamento, suprimir |

Separar B-NOVA de B-ERRO e automatico: cruza com o campo `source` da nossa base.

---

## 6. Registro

```
docs/comparacao/
  dumps/{data}/pathbuilder-{classe}-{slot}.json   coleta bruta, versionada
  findings.jsonl                                  1 linha por divergencia
  triage.yaml                                     allowlist do esperado
  baseline/{frente}.json                          o ratchet
```

- `findings.jsonl` com chave estavel `kind:slug:campo`, categoria, evidencia dos
  dois lados e `status: open | fixed | wontfix`.
- **Ratchet**: baseline congelado por frente; re-execucao reporta **so o novo**.
  Sem isso o relatorio se regenera inteiro toda semana e para de ser lido.
- Achado `open` de categoria D ou A vira item no `TASKS.md` do projeto.
- Tudo dentro do projeto. Nada em `/tmp` -- o script de coleta escreve direto em
  `docs/comparacao/`.

---

## 7. Criterio de parada

Uma frente esta pronta quando:
- zero **D-CONTEXTO** e zero **B-SOBRA-ERRO** em aberto;
- **A-FALTA** triado -- adicionado, ou justificado por escrito;
- **C-CAMPO** mecanico zerado contra o AoN.

**Diferente para sempre, por design:** texto e wording, ordenacao de lista,
conteudo mais novo que aquele install, e tudo que decorre da regra da casa.
Registrado uma vez em `triage.yaml`, nunca mais reportado.

---

## 8. Esforco e paralelismo

| fase | esforco | paralelizavel? |
|---|---|---|
| Fase 0 | 2-3 sessoes | parcialmente |
| Colheita de dedicacoes | 1-2 de coleta + 2-3 de modelagem | coleta **nao** (serial); modelagem sim |
| Classes e progressao | coleta longa automatizada + 2-3 de triagem | triagem sim |
| Slots por contexto | 2-3 sessoes | triagem sim |
| Ancestralidades, magias, equipamento | ~1 sessao de cruzamento cada | sim |

**Nao paralelizavel: a coleta no Pathbuilder.** Um contexto, serial, com pausa
-- Cloudflare derruba coleta agressiva, e perder o acesso mata a campanha.

Total: 3 a 4 semanas de sessoes intermitentes, com o grosso do valor -- as
dedicacoes e o motor de classes -- nas duas primeiras.

---

## 9. O que nao vale o esforco

- **Comparar texto de item.** Nossa base e mais nova e as fontes divergem em
  wording por licenca. Ruido garantido.
- **Exaustao dos 6.273 feats via browser.** Semanas de coleta e risco real de
  bloqueio, para achar o que o cruzamento offline de catalogo acha de graca.
- **Pets contra paywall.**

---

## 10. Validacao por amostra (2026-07-28, executada)

O Igor pediu amostra de cada frente antes de aprovar a campanha. Feita. O
resultado **mudou o plano de novo**, e para melhor.

### Achado que barateia metade das frentes

O dump do AoN esta **inteiro no disco** (`dados_brutos/aon_*.json`): 8.460 feats,
2.461 magias, 614 armas, 436 herancas, 405 companheiros, 717 divindades.

Como o AoN e o **juiz** (secao 0) e nao o Pathbuilder, as frentes de CATALOGO
nao precisam de browser nenhum. Escrito `pipeline/comparar_com_aon.py`: cruza a
base contra o dump, offline, em segundos, re-executavel, sem Cloudflare e sem
coleta serial.

Primeira execucao, 13 frentes:

| frente | nossa | AoN | faltam | so nosso | nivel≠ | rar≠ |
|---|---|---|---|---|---|---|
| feat | 6247 | 6294 | **163** | 116 | **21** | 6 |
| magia | 1638 | 1796 | **158** | 0 | 0 | 5 |
| arma | 1029 | 327 | 16 | 718 | 6 | 2 |
| heranca | 334 | 342 | 12 | 4 | 0 | 0 |
| ritual | 151 | 155 | 10 | 6 | 0 | 0 |
| arquetipo | 243 | 247 | 4 | 0 | 0 | 0 |
| divindade | 487 | 484 | 3 | 6 | 0 | 0 |
| ancestralidade | 50 | 52 | 2 | 0 | 0 | 0 |
| familiar | 208 | 172 | 2 | 38 | 0 | 0 |
| companheiro | 113 | 96 | 0 | 17 | 0 | 0 |
| background | 521 | 496 | 0 | 25 | 0 | 0 |
| armadura | 216 | 38 | 0 | 178 | 0 | 0 |
| escudo | 125 | 16 | 0 | 109 | 0 | 0 |

~370 itens ausentes e 27 niveis divergentes, numa execucao offline.

O "so nosso" alto em equipamento (718 armas, 178 armaduras) e esperado: o dump de
equipamento do AoN e parcial e o nosso veio do Foundry. **Nao e erro** -- e por
isso que a taxonomia separa B-SOBRA-NOVA.

Pegadinha achada e corrigida na hora: filtrar por `type` zerava quatro frentes em
silencio -- o dump de equipamento marca tudo como `Item` (ja separado por
arquivo) e o de magias nao traz `type` nenhum.

### Frente 1 (dedicacoes) -- viavel, e cara como previsto

O Pathbuilder mostra o detalhe da dedicacao (nome, nivel, traits, prosa) e a
ficha muda ao aceitar. Confirmado com `Archer Dedication`. Mas colher **o que**
mudou exige um extrator que compare o ESTADO da ficha antes e depois -- ler o
icone de proficiencia linha a linha, nao so o texto. E o item de maior valor do
plano e continua sendo o mais caro; a estimativa de 1-2 sessoes de coleta mais
2-3 de modelagem se mantem.

### Consequencia para a ordem

A ordem da secao 3 continua valendo para o que depende do Pathbuilder. Mas as
frentes 4, 5 e 6 (ancestralidades, magias, equipamento) **saem da fila do
browser** e viram triagem offline paralelizavel -- que ja foi lancada em quatro
agentes simultaneos, um por grupo de kinds.
