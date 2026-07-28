# Ruido de avisos -- as 3 familias novas + 2 novas em `fora_do_requisito`

Medicao executada em 2026-07-27 contra:
- as 9 fichas de `motor/exemplos/*.json` (dado FIEL -- toda escolha real esta no
  documento, incluindo `subclasse` e `skill_increase`);
- as 129 fichas oficiais que `motor/validar_iconics.py` consegue traduzir (de
  136 personagens x niveis; 7 nao traduzem por `classe ausente da base`:
  `Whirp` e `Droogami` sao companion sheets, `wb:class/construct-companion` e
  `wb:class/animal-companion` nao existem na base -- fora de escopo, nao e
  aviso).

Script de coleta (nao commitado, so leitura -- nao editei nenhum `.py` do
projeto): `/tmp/claude-1000/-mnt-c-Users-igor0/cf4835ec-3dd1-442c-ad27-6284421f280d/scratchpad/coletar_avisos.py`.
Carrega `Base()` uma vez, monta `Personagem` para as 9 fichas + reusa
`validar_iconics.traduzir()` para as 129, e classifica cada mensagem por
regex de familia.

## Achado central, antes dos numeros

**A comparacao entre as 9 fichas e as 129 iconics nao e simetrica.** As 9
fichas sao documento waybuilder legitimo (o jogador escolheu tudo, inclusive
subclasse e aumento de pericia). As 129 iconics passam por um tradutor
(`validar_iconics.py:traduzir()`) que foi escrito para validar SO duas coisas
-- HP e rank de pericia (ver docstring do proprio arquivo, linhas 1-28) -- e
por isso deliberadamente:

1. nunca emite escolha de `slot: "subclasse"`;
2. nunca emite escolha de `slot: "skill_increase"` (documentado no proprio
   arquivo, linha 369: "este tradutor nao emite escolhas skill_increase");
3. junta QUALQUER item Foundry de `type: "feat"` num unico
   `{"em": 1, "slot": "class_feat", "pega": wid}` (`validar_iconics.py:122-125`),
   sem separar por nivel real nem por tipo de slot (skill/general/ancestry/
   free_archetype) nem por classe.

Essas tres simplificacoes eram inocuas para o proposito original (HP e
pericia nao dependem de slot nem de subclasse). Ao reusar a mesma montagem
para medir os avisos NOVOS de hoje -- que checam exatamente slot, subclasse e
cadencia de skill_increase -- essas simplificacoes viram a maior fonte de
ruido do relatorio. **Isso e ruido do arnes de validacao (`validar_iconics.py`),
nao do motor nem da base**, e teria acontecido com qualquer regra nova que
tocasse esses tres eixos.

## Numeros gerais

| | valor |
|---|---|
| fichas avaliadas | 138 (9 exemplos + 129 iconics) |
| media de avisos+fora_do_requisito por ficha (so iconics, n=129) | **7,46** |
| mediana (iconics) | 6 |
| pior caso (iconics) | **25** -- `Brave Wanderer` (18 avisos + 7 fora_do_requisito) |
| iconics com >=1 aviso de `higiene_de_slot` | **127 de 129 (98%)** |
| media SEM contar `higiene_de_slot` (iconics) | 4,02 -- pior caso 15 |
| fichas com 0 avisos (iconics) | 0 de 129 |

Top 5 piores fichas: `Brave Wanderer` (25), `Ezren Nv5` (24), `Ruvior` (23),
`Feiya Nv5` (19), `Ezren Nv3` (18).

## Contagem por familia (todas as 138 fichas, avisos + fora_do_requisito)

| familia | ocorrencias | classificacao dominante |
|---|---|---|
| `higiene_de_slot` | 444 | **(c) RUIDO ESTRUTURAL** -- 443/444 vem do colapso de slot/nivel do tradutor |
| `fora_requisito` -- checagem de skill rank generica (pre-existente) | 173 | maioria (c), causa: tradutor nao emite `skill_increase` |
| `_features_de_classe`: "falta escolher X" (pre-existente, fora do escopo dos 3 novos) | 183 | (c) -- inclui o `outras-opcoes` ja conhecido + subclasse nunca resolvida pelo tradutor |
| `fora_requisito` -- `class_level` de classe errada (pre-existente) | 45 | **(b) FALSO POSITIVO real na base**, ver abaixo |
| `grants_em_cadeia` -- `grant_item` dinamico | 43 | (a) legitimo por design, mas quase sempre irresolvivel pelo schema atual |
| `fora_requisito` -- `has` de Dedication colidindo com class-feature | 23 | **(b) FALSO POSITIVO do tradutor** |
| `fora_requisito` -- sub-escolha de subclasse | 21 | (c) -- mesmo motivo do `outras-opcoes`: tradutor nunca resolve subclasse |
| `fora_requisito` -- `has` de ancestria (Multitalented) | 9 | (b) gap de modelagem, pre-existente |
| `veto_classe_de_dedicacao_ja_pega`, `veto_dedicacao_da_propria_classe` (regra 23, hoje mas fora do escopo pedido) | 1 + 1 | (a) |
| **`_exige_a_dedicacao_do_arquetipo` (NOVA)** | 1 | (a) SINAL LEGITIMO |
| **`_nova_dedicacao_exige_dois_feats` (NOVA)** | 1 | (a) SINAL LEGITIMO |
| **`_aumentos_de_pericia` (NOVA)** | 0 | sem amostra real -- ver secao propria |
| `grant_feat` alvo nao resolvido pelo pipeline / id ausente / profundidade | 0 | nunca disparou neste corpus (ver nota) |

---

## 1. `_higiene_de_slot` -- a familia mais ruidosa

**444 ocorrencias, 127/129 iconics afetadas.** Mensagem dominante (443 das
444): `slot class_feat: escolha no nivel N, que nao tem slot desse tipo` e
`slot class_feat: N escolha(s) para M slot(s) disponivel(is)`.

**Causa (b/c -- FALSO POSITIVO por defeito do arnes, nao da base nem do
motor):** `motor/validar_iconics.py:122-125`

```python
for it in por_tipo(doc, "feat"):
    wid = f"wb:feat/{slug(re.sub(r'\\s*\\([^)]*\\)\\s*$', '', it['name']))}"
    if base.opcional(wid) is not None:
        escolhas.append({"em": 1, "slot": "class_feat", "pega": wid})
```

Todo feat do ator oficial -- skill feat, general feat, ancestry feat, feat de
arquetipo, ou class feat de qualquer nivel -- vira `slot: "class_feat"` no
`nivel 1`. Um personagem nivel 5 com 8 feats de tipos variados gera ate 8
"escolhas" empilhadas contra o slot `class_feat`, que so tem 2 vagas (niveis
2 e 4) -- daí `"8 escolha(s) para 2 slot(s) disponivel(is)"`. E qualquer feat
que nao seja class feat (a maioria) cai no nivel 1, onde 25 das 27 classes
nao tem slot de `class_feat` nenhum -- daí `"escolha no nivel 1, que nao tem
slot desse tipo (niveis validos: [])"`.

**Prova de que e o arnes, nao o motor:** nos 9 exemplos (dado fiel, com
`skill_feat`/`general_feat`/`ancestry_feat` no slot certo e no nivel certo)
`_higiene_de_slot` produz exatamente **1** aviso em toda a bateria --
`guerreiro4-fa-class-feat-no-slot.json`, onde a ficha DE FATO poe um feat sem
trait `archetype` no slot `free_archetype`. Esse caso e (a) SINAL LEGITIMO:
o motor pega exatamente o que devia.

**Veredito:** a familia esta correta; o corpus de iconics nao serve para
medi-la porque o tradutor descarta a informacao de slot/nivel antes dela
chegar ao motor. Nao ha o que consertar no motor por causa disso.

---

## 2. `_aumentos_de_pericia` -- zero amostras reais

**0 ocorrencias em toda a bateria de 138 fichas.**

- No exemplo dedicado (`ladino4-aumentos-de-pericia.json`), o documento foi
  desenhado para NAO disparar aviso (prova que a cadencia certa nao acusa
  falso positivo) -- confirmado, zero avisos dessa familia.
- Nos 129 iconics, `validar_iconics.py` nunca emite `slot: "skill_increase"`
  (confirmado por grep: a unica mencao a `skill_increase` no arquivo esta no
  texto do relatorio markdown, nao no tradutor) -- entao a familia nunca tem
  chance de disparar nesse corpus, verdadeiro ou falso.

**Verificacao adicional (fora dos 9+129, sondas sinteticas descartaveis em
`/tmp/.../scratchpad/probe{1,2,3}_*.json`, nao commitadas):** copiei o
exemplo de aumento de pericia e forcei tres violacoes de proposito --
aumento num nivel sem cadencia, aumento excedente e aumento acima do teto de
rank do nivel. As tres mensagens dispararam exatamente como o codigo promete:

```
skill_increase: 4 aumento(s) escolhido(s) para 3 disponivel(is) em [2, 3, 4]
skill_increase: aumento no nivel 1, que nao tem aumento (niveis validos: [2, 3, 4])
skill_increase: stealth iria a master, acima do teto expert do nivel 4
```

**Veredito:** sem dado real pra classificar (a)/(b)/(c) porque a familia
nunca disparou nas 138 fichas. Pela leitura do codigo + pelas 3 sondas
sinteticas, a logica responde certo aos tres casos de borda que testei e nao
acusa nada no caso correto (o exemplo). Recomendo tratar como validada por
enquanto, mas registrar que **nenhuma ficha real do corpus a exercitou** --
se `validar_iconics.py` ganhar emissao de `skill_increase` no futuro (nao
pedi para editar), essa familia passaria a ter cobertura real.

---

## 3. `_grants_em_cadeia` -- so um dos quatro sub-avisos disparou

| mensagem | ocorrencias | fichas distintas |
|---|---|---|
| `grant_item depende de escolha do jogador (uuid dinamico ...)` | 43 (iconics) + 1 (exemplo) | 37 de 129 iconics |
| `grant_feat com alvo nao resolvido pelo pipeline` | 0 | -- |
| `grant_feat aponta pra id ausente da base` | 0 | -- |
| `cadeia de grants cortada em profundidade` | 0 | -- |

**Os 3 sub-avisos com zero ocorrencia nao sao "sem problema", sao "sem
alcance".** O commit de hoje (`afcc37894`) registra que ha **476 alvos de
`grant_feat` nao resolvidos, todos vindos de `background`** -- mas
`_grants_em_cadeia` (linhas 1683-1688) so percorre grants de
`self._feats_escolhidos()` e `self.features` (classe/subclasse). Background
nunca entra em `origens`. Logo aqueles 476 casos nunca sao visitados e nunca
geram aviso -- nao e ruido, e uma lacuna de cobertura (fora do que a tarefa
pediu medir, so registrando para nao passar como "zero problema").

**O `grant_item` dinamico (43x) -- classificacao (a), com ressalva.**
Investiguei o caso mais frequente (`natural-ambition`, 31x): a ficha da
Amiri (Foundro Barbarian) tem o item resolvido "Diehard" como feat separado
no ator oficial -- ou seja, o jogo real ja "fechou" essa escolha. Mas o
schema do waybuilder hoje **nao tem um slot que represente "resolucao de
`grant_item`"** -- so ha `class_feat`/`skill_feat`/`general_feat`/
`ancestry_feat`/`free_archetype`/`subclasse`. Mesmo que o jogador va la e
pegue "Diehard" separadamente, nao existe vinculo no documento que diga "isso
resolve o Natural Ambition"; o motor continua, corretamente hoje, sem forma
de saber que a escolha ja foi feita. **E sinal legitimo dado o schema atual**,
mas e alto volume e PREVISIVEL: qualquer humano/meio-elfo/meio-orc com
Natural Ambition/Ancestral Paragon vai sempre disparar essa linha, sem
exceçao, ate o schema ganhar esse slot. Vale documentar como debito de
produto (nao de motor).

---

## 4 e 5. As duas familias novas de `fora_do_requisito`

Ambas com **exatamente 1 ocorrencia em toda a bateria** (a do proprio
exemplo desenhado pra isso) e **zero falsos positivos nas 129 fichas oficiais**:

- `_exige_a_dedicacao_do_arquetipo` -- disparou em
  `guerreiro4-fa-lacuna-dedicacao.json` (`Barbarian Resiliency` sem
  `Barbarian Dedication`). (a) SINAL LEGITIMO.
- `_nova_dedicacao_exige_dois_feats` -- disparou em
  `guerreiro6-fa-duas-dedicacoes.json` (`Marshal Dedication` no nivel 4 sem
  2 feats de `Archer`). (a) SINAL LEGITIMO.

Zero das 129 fichas oficiais (RAW, single-classe, todas seguem a regra do
trait `dedication`/`archetype` por definicao) dispara qualquer uma das duas
-- e o resultado esperado: se alguma tivesse disparado, seria evidencia forte
de bug, porque personagem oficial da Paizo nunca viola RAW de arquetipo.

**Veredito: as duas familias novas de `fora_do_requisito` sao as mais limpas
de toda a medicao** -- baixo volume, alta precisao, sem ruido detectado.

---

## Achados adicionais (fora do escopo das 5 familias pedidas, mas no mesmo
"campo de visao" de `fora_do_requisito`/avisos que o jogador ve)

Encontrados investigando a causa dos numeros altos acima. Nao sao avisos
NOVOS de hoje, mas contaminam a mesma tela que o jogador ve e valem registro
porque tem causa raiz confirmada, nao so suspeita.

### A. `pipeline/derivar_gate_nivel.py:92-94` -- feat multi-classe perde as
outras classes (FALSO POSITIVO confirmado, 122 registros afetados na base)

```python
elif traits & set(classes):
    nome = sorted(traits & set(classes))[0]
    gate = {"class_level": {classes[nome].split("/")[-1]: {">=": nivel}}}
```

Quando um feat tem mais de um trait de classe (feats compartilhados de
metamagia -- `Reach Spell`, `Widen Spell` -- ou feats de multiclasse como
`Trap Finder`, `Bespell Strikes`, `Reactive Strike`), o gate deriva SO da
classe que vem primeiro em ordem alfabetica entre as que casam, descartando
as outras. `Reach Spell` tem traits
`{bard, cleric, druid, oracle, sorcerer, witch, wizard}` e vira
`class_level: {bard: >=1}` -- um Ezren (Wizard puro, sem nenhum nivel de
Bardo) que pegou Reach Spell (legitimo, e um feat de metamagia universal)
sai marcado fora do requisito.

Contei **122 feats na base** com mais de um trait de classe (nao-arquetipo).
No corpus de 129 iconics isso gerou **45 ocorrencias em 31 fichas**
distintas -- e o segundo maior bloco de ruido depois do `higiene_de_slot`.

Fix sugerido (nao apliquei, e `.py` do projeto): trocar `class_level` de
valor unico por `{"any": [...]}` com uma clausula por classe que casa, em vez
de `sorted(...)[0]`.

### B. `motor/validar_iconics.py:122-125` -- colisao de slug entre
class-feature e feat de arquetipo (FALSO POSITIVO do arnes, 23 ocorrencias
em 20 fichas)

Alguns nomes de class-feature (`Advanced Alchemy`, `Quick Alchemy`) tambem
existem na base como `wb:feat/...` -- a versao ARQUETIPO desse mesmo poder,
que EXIGE `Alchemist Dedication` (regra 19, "Advanced alchemy congela em 1").
O tradutor, ao converter QUALQUER item Foundry `type: "feat"` para
`wb:feat/{slug}` sem checar se o nome corresponde a um `wb:class-feature/`
em vez disso, injeta a versao arquetipo na ficha de um Alquimista de classe
pura (que ja tem o poder de graca, via
`wb:class-feature/quick-alchemy` -> `grants: [{"grant_feat": [...]}]`, ja
resolvido corretamente por `_grants_em_cadeia`). O resultado e um
`fora_do_requisito` duplicado e errado: "exige Alchemist Dedication" para um
personagem que E Alquimista.

Confirmado consultando `pipeline/base/index.json`: `wb:feat/advanced-alchemy`
(`traits: ["archetype"]`, `requires: {has: wb:feat/alchemist-dedication}`) e
`wb:class-feature/advanced-alchemy` (`traits: ["alchemist"]`) coexistem como
registros DIFERENTES com o MESMO nome de exibicao.

### C. `_termo_has` nao modela "Multitalented" (meio-elfo/meio-orc) --
gap de modelagem pre-existente, 9 ocorrencias em 2 personagens

`Jirelle` (Human, heranca Half-Elf) e `Droven` (Human, heranca Dromaar/
Half-Orc) tomam `Nimble Elf` e `Orc Ferocity` -- ancestry feats de Elfo/Orc
que o RAW libera para essas herancas via a regra "Multitalented". `_termo_has`
(linha 1406-1423) so aceita `has` quando o id bate exatamente com
`self.ancestria`/`self.heranca`/`self.background` -- nao ha excecao pra
Multitalented. Nao e uma das 5 familias pedidas (codigo pre-existente), mas
e um falso positivo real, de baixo volume.

---

## Resumo executivo (para a pergunta "sinal demais?")

Das **5 familias que a tarefa pediu para medir**, tres tem volume real
(`higiene_de_slot`, `grants_em_cadeia`) ou zero volume
(`_aumentos_de_pericia`), e duas (`_exige_a_dedicacao_do_arquetipo`,
`_nova_dedicacao_exige_dois_feats`) sao limpas.

- **`higiene_de_slot` E ruidosa no relatorio (444x), mas o ruido e 100%
  atribuivel ao tradutor de validacao, nao ao motor.** Nos 9 exemplos fieis,
  ela acerta 1 de 1. Nao ha acao no motor a fazer; se algo, `validar_iconics.py`
  precisaria emitir slot/nivel reais para servir de oraculo dessa familia --
  mas a tarefa pediu para nao editar `.py`.
- **`_aumentos_de_pericia` nunca disparou em dado real** -- nem sinal nem
  ruido, so ausencia de cobertura no corpus disponivel.
- **`grants_em_cadeia` tem 1 sub-aviso ativo (43x) que e tecnicamente
  correto, mas vai disparar em TODA ficha com Natural Ambition/Ancestral
  Paragon ate o schema aceitar resolver a escolha** -- vale nota de produto,
  nao e bug.
- **As duas familias novas de `fora_do_requisito` sao as mais confiaveis
  medidas: 1 disparo cada, ambos corretos, zero falso positivo em 129
  personagens oficiais.**
- **Os dois falsos positivos REAIS e acionaveis encontrados** (item A, base;
  item B, tradutor) nao sao das 5 familias pedidas, mas moram na mesma tela
  (`fora_do_requisito`) e valem mais a pena consertar do que qualquer coisa
  nas 5 familias -- juntos respondem por 68 das 276 linhas do balaio
  "checagem generica" que ja existia antes de hoje.

**Se o criterio for "o jogador para de ler com 20 avisos por ficha":** hoje
a media real medida (iconics, que e o corpus mais parecido com uso real) e
7,46, com pior caso 25 -- ja perto do limite citado, e 98% disso vem de UMA
causa (o tradutor). Numa ficha waybuilder de verdade (schema completo, como
os 9 exemplos), a mesma bateria de avisos produz **0 a 2 avisos por ficha**,
todos corretos. A recomendacao e nao mexer nas 5 familias novas -- elas
funcionam --, e sim: (1) considerar item A (`derivar_gate_nivel.py`) prioridade
alta por ser bug de base com 122 registros afetados; (2) documentar o item B
como limitacao conhecida do `validar_iconics.py`, ja que ele foi construido
para outro proposito e esta sendo reusado alem do que sua propria docstring
promete.
