# Review adversarial -- motor aplica o efeito das escolhas (commit 3351b9d57)

Data: 2026-07-27
Alvo: `motor/motor.py`, itens 62/63/64/67 (`_grants_em_cadeia`, `_feats_efetivos`,
`_higiene_de_slot`, `_exige_a_dedicacao_do_arquetipo`,
`_nova_dedicacao_exige_dois_feats`, `_aumentos_de_pericia`).
Metodo: toda afirmacao abaixo tem script executado e saida. Nenhum arquivo do
projeto foi editado. Scripts em
`/tmp/claude-1000/-mnt-c-Users-igor0/cf4835ec-3dd1-442c-ad27-6284421f280d/scratchpad/`
(`h01`..`h16`).

Baseline antes e depois de toda a investigacao: `python3 -m unittest discover -s
motor/testes -t .` -> 42 testes, OK (1 expected failure). `python3
motor/teste_motor.py` -> todos passaram. `motor/validar_iconics.py` regenerou
`docs/2026-07-27_validacao-iconics.md` byte a byte igual ao versionado.

Casos executados: **6.881 derivacoes nomeadas** (16 documentos malformados, 2.129
feats de arquetipo, 321 embaralhamentos, 3.000 documentos de fuzz, 675
combinacoes classe x nivel x dedicacao rodadas nos dois motores, ~40 casos
dirigidos) mais a varredura termo a termo dos 6.273 feats com `requires` nos dois
motores (~13 mil derivacoes adicionais).

---

## (a) Defeitos CONFIRMADOS

### D1 -- CRITICO. Personagem sem nivel de classe levanta excecao

`_aumentos_de_pericia` (motor.py:382):

```python
teto = next(r for n, r in self.TETO_DE_RANK if self.nivel >= n)
```

`TETO_DE_RANK` termina em `(1, "expert")`. Com `self.nivel == 0` nenhum termo
casa e o gerador estoura `StopIteration`. Nao ha `default`.

Menor reproducao:

```python
from motor.motor import Base, Personagem
Personagem({}, Base())      # StopIteration em motor.py:382
```

Isso viola a regra explicita do projeto -- o motor sinaliza, nunca explode -- e e
**regressao**: o motor de `3351b9d57^` deriva o mesmo documento sem erro.

```
CRASH doc vazio: StopIteration @ motor.py:382, _aumentos_de_pericia
OK (motor VELHO)   doc vazio
OK (motor VELHO)   so ancestria
```

Alcance medido (`h01`): **12 de 16** documentos malformados quebram, todos pela
mesma linha -- doc vazio, `escolhas: []`, so ancestria escolhida, escolha sem
`pega`, `pega` como lista, `nivel_de_classe` sem `em`, escolha sem `slot`,
`escolhas` nao-lista, `skill_increase` sem classe, ator sem classe, inventario
com item ausente. Todo estado inicial do construtor (antes do jogador escolher a
primeira classe) cai aqui.

Nota: `Base.get` levantando `KeyError` para id de classe ausente tambem quebra,
mas isso e **anterior** ao commit (o motor velho quebra igual) -- nao entra nesta
lista.

### D2 -- GRAVE. Um feat passa a satisfazer o PROPRIO requisito

`_proficiencias` agora aplica `proficiency` e `skill_training.auto` dos feats
(motor.py:321-331), e `_grants_em_cadeia` roda antes de tudo -- mas
`_checar_requisitos` continua sendo o ultimo passo e avalia o `requires` de cada
feat contra um estado que **ja inclui o efeito daquele mesmo feat**. O requisito
deixa de sinalizar exatamente nos casos em que ele existe.

Menor reproducao (Guerreiro 2, Acrobatics untrained):

```python
doc = {"escolhas":[
  {"em":"criacao","slot":"ancestralidade","pega":"wb:ancestry/human"},
  {"em":"criacao","slot":"background","pega":"wb:background/warrior"},
  {"em":1,"slot":"nivel_de_classe","pega":"wb:class/fighter"},
  {"em":1,"slot":"subclasse","pega":"wb:class-feature/warrior-of-legend"},
  {"em":2,"slot":"nivel_de_classe","pega":"wb:class/fighter"},
  {"em":2,"slot":"free_archetype","pega":"wb:feat/acrobat-dedication"}]}
```

```
acrobatics SEM a dedicacao: untrained
requires do feat          : {"all":[{"proficiency":{"acrobatics":{">=":"trained"}}},{"character_level":{">=":2}}]}
grants   do feat          : [{"skill_training": {"auto": ["acrobatics"]}}]
acrobatics COM            : trained | origem: ['Acrobat Dedication']
fora_do_requisito NOVO    : VAZIO  <-- nao sinaliza
fora_do_requisito VELHO   : [{'feat': 'Acrobat Dedication',
                              'motivo': 'exige acrobatics >= trained; tem untrained'}]
```

Alcance medido sobre os 6.273 feats da base, termo a termo, nos dois motores
(`h14`):

| motor | termos auto-satisfeitos |
|---|---|
| `3351b9d57^` (velho) | **0** |
| `3351b9d57` (novo)   | **25** (24 por `proficiency`, 1 por `has`) |

Os 24 de `proficiency` sao dedicacoes que exigem `X >= trained` e concedem `X`:
`acrobat`, `alter-ego`, `archaeologist` (2 termos), `bounty-hunter`,
`cultivator`, `fan-dancer`, `game-hunter`, `medic`, `herbalist`, `marshal`,
`provocator`, `lepidstadt-surgeon`, etc. O de `has` e
`snarecrafter-dedication`, que exige `has wb:feat/snare-crafting` e concede
`wb:feat/snare-crafting` -- fechado por `_termo_has` lendo `self.concedidos`
(motor.py:1415).

Confirmado tambem na matriz classe x nivel x dedicacao (`h12`, 675 combinacoes):
`exige medicine >= trained` sumiu de 108 fichas.

Onde consertar: o `requires` de um feat tem de ser avaliado contra o personagem
**sem aquele feat** (e sem o que ele concede). O passo de checagem precisa de um
estado "antes do pick", nao do estado final.

### D3 -- GRAVE. Regra 63 nao ve dedicacao CONCEDIDA (falso positivo) e regra 64 tambem nao (falso negativo)

`_exige_a_dedicacao_do_arquetipo` (motor.py:1578) e
`_nova_dedicacao_exige_dois_feats` (motor.py:1595) usam **so escolhas do
documento** (`_ids_de_feat_escolhidos()` / `doc["escolhas"]`), enquanto
`_termo_has` no mesmo motor ja conta `self.concedidos`. Duas nocoes de "tenho"
incoerentes na mesma derivacao.

Caso real na base: `wb:feat/gray-corsair-training` concede
`wb:feat/pirate-dedication` (alvo estatico, aplicado pela cadeia).

Reproducao (Guerreiro 12):

```
escolhas: gray-corsair-training (nivel 6) + bitter-taste-of-betrayal (nivel 4)
concedidos: ['wb:feat/pirate-dedication', 'wb:feat/additional-lore', ...]
fora: Bitter Taste of Betrayal | feat do arquetipo Pirate exige Pirate Dedication
      (RAW do trait archetype), que a ficha nao tem
```

A ficha **tem** Pirate Dedication -- esta em `concedidos`, na mesma lista que a
propria `visao()` publica. Falso positivo.

O complemento, mesma raiz (`h08`):

```
escolhas: gray-corsair-training (6) + barbarian-dedication (8)
concedidos: ['wb:feat/pirate-dedication', ...]
flags regra64: NENHUMA
```

O personagem ganhou Pirate Dedication e pegou outra dedicacao sem nenhum feat de
Pirate. A regra 64 devia sinalizar e nao sinaliza, porque `dedicados` so recebe
dedicacao **escolhida**. (Controle: com a dedicacao escolhida a mao, a regra
funciona -- 1 feat de arquetipo -> sinaliza, 2 feats -> limpo.)

O outro sentido da regra 64 tambem: um feat de arquetipo **concedido** nao entra
em `contagem`, entao nunca conta para os dois feats exigidos. Ha 8 alvos com
campo `archetype` concedidos por cadeia na base (`h05`).

### D4 -- MEDIO. `_grants_em_cadeia` nao percorre ancestria, heranca nem background

`origens` (motor.py:1683-1688) e montado so com feats escolhidos e
`self.features`. Medido sobre a base inteira (`h09`, `h10`):

| kind da origem | grant_feat estaticos resolvidos | percorrido |
|---|---|---|
| feat | 285 | sim |
| class-feature | 95 | sim |
| **heritage** | **44** | **nao** |
| **background** | **25** | **nao** |
| weapon | 1 | nao |

Exemplos perdidos: `wb:background/shielded-fortune -> wb:feat/toughness`
(confirmado: `concedidos` sai sem Toughness), `wb:heritage/ambitious-human ->
wb:feat/fleet`, `wb:heritage/battle-ready-orc -> wb:feat/intimidating-glare`,
`wb:heritage/battle-trained-human-bb -> wb:feat/diehard`.

Consequencia direta: o **aviso novo de alvo nao resolvido** (motor.py:1752-1754)
e codigo morto. Os 476 alvos nao resolvidos que o commit registra como item 70
estao **todos** em `background` -- kind que a cadeia nunca visita. O aviso nao
tem como disparar em nenhum documento.

```
alvos grant_feat NAO RESOLVIDOS, por kind da ORIGEM:
   background       476   percorrido pelo motor: False
total nao resolvido: 476
```

### D5 -- MEDIO. Escolha de nivel futuro tem tres tratamentos diferentes no mesmo documento

`_atributos` documenta explicitamente que planejamento de progressao e caso
normal e **ignora em silencio benigno** (aviso informativo) o boost de nivel
futuro. As duas rotinas novas tratam o mesmo dado como erro. Guerreiro 4 com tres
escolhas identicas marcadas `em: 6` (`h16`):

```
skill_increase: aumento no nivel 6, que nao tem aumento (niveis validos: [2, 3, 4])
boosts de nivel 6 ignorados -- personagem tem nivel 4
slot class_feat: escolha no nivel 6, que nao tem slot desse tipo (niveis validos: [1, 2, 4])
```

Alem disso `_higiene_de_slot` conta `len(usados) > len(niveis)` sobre **todas** as
escolhas do documento, sem filtrar por nivel -- entao um documento com a
progressao ate 20 planejada acusa excesso de slot em toda derivacao intermediaria.

### D6 -- BAIXO. `_aumentos_de_pericia` aceita string arbitraria e cria proficiencia fantasma

Nao ha validacao de que `pega` e uma pericia (a base tem 33 registros `kind:
skill`). Um erro de digitacao entra na ficha sem aviso nenhum:

```
'atletismo' virou chave de proficiencia: True -> trained     avisos: NENHUM
'wb:feat/toughness' como pericia: trained                    aviso : NENHUM
```

### D7 -- BAIXO. `em: "criacao"` desliga a checagem de nivel de `_higiene_de_slot`

`isinstance(em, int)` (motor.py:692) faz a escolha com `em` string escapar. Mesmo
erro, dois resultados:

```
free_archetype em 'criacao' (slots validos [2,4]): NENHUM AVISO
free_archetype em 3         (mesmo erro, com int): ['slot free_archetype: escolha no nivel 3, ...']
```

Nao gera numero errado, mas abre um caminho de silencio.

### D8 -- BAIXO, pre-existente. `_subclasse_de` depende da ordem do array de escolhas

Achado pelo teste de embaralhamento (`h03`, 321 derivacoes). Nao muda numero
nenhum nos exemplos versionados, mas muda o texto do motivo -- e alimenta
`_dc_de_conjuracao`, onde a subclasse escolhida decide a progressao (Cloistered x
Warpriest). Documento com duas escolhas de `subclasse` para a mesma classe pode
render DC diferente conforme a ordem do JSON. Nao e regressao deste commit.

---

## (b) Hipoteses testadas e INFUNDADAS

### Dupla contagem -- NAO acontece. Testada em 5 caminhos independentes (`h08`)

Guerreiro 12, HP baseline 128, Toughness vale `@actor.level` = +12:

| caminho | HP | veredito |
|---|---|---|
| 1 dedicacao que concede Toughness | 140 | +12, correto |
| 2 dedicacoes que concedem Toughness | 140 | **nao soma duas vezes** |
| 3 dedicacoes que concedem Toughness | 140 | **nao soma tres vezes** |
| Toughness escolhido a mao | 140 | +12 |
| Toughness escolhido **+** concedido | 140 | **nao soma** |
| Toughness escolhido **duas vezes** no documento | 140 | **nao soma** |

Todas as 7 combinacoes de `battle-harbinger` / `mummy` / `werecreature`
produziram exatamente 1 registro `wb:feat/toughness` em `concedidos`. O guarda e
`_ja_tenho` (global, populado antes do laco) somado ao dedup de `_feats_efetivos`
por `vistos`.

Orcamento de pericia (aditivo, mesmo risco): 33 feats com
`skill_training.free`, cada um testado escolhido 1x e 2x -- `pericias_livres`
identico nos dois casos (ex.: `battle-harbinger-dedication` 1x=4, 2x=4).

Class-feature concedida que ja vinha da progressao: nao duplica, porque
`_ja_tenho` e inicializado com `{f["id"] for f in self.features}` antes de
qualquer concessao. Confirmado no baseline Guerreiro 4, onde `reactive-strike`,
`shield-block` e `diehard` aparecem uma unica vez cada.

### Ordem de iteracao das origens / `visitados` por origem -- NAO altera a ficha

321 derivacoes com `doc["escolhas"]` embaralhado (9 exemplos versionados x 40
permutacoes, semente fixa). Divergencia numerica: **zero**. A unica divergencia
foi textual, em `fora_do_requisito`, e e o D8 acima (`_subclasse_de`, anterior ao
commit). `hp`, `proficiencias`, `pericias_livres`, `slots`, `concedidos`,
`features`, `aumentos_de_pericia`, `ac`, `ataques`: identicos em 100% dos casos.

### Ordem de derivacao (`_grants_em_cadeia` antes de `_atributos`/`_hp`) -- NAO produz valor errado

`_grants_em_cadeia` le apenas `self.doc` e `self.features`; nao ha grant
condicionado a atributo, nivel ou proficiencia no caminho estatico. Verificado na
matriz de 675 combinacoes (`h12`) comparando os dois motores: **nenhuma
proficiencia caiu de rank** e o delta de HP e sempre 0 ou exatamente
`@actor.level` da fonte de Toughness (`{0: 567, 4: 27, 8: 27, 12: 27, 20: 27}`),
e o delta de pericia livre e sempre 0 ou +1. Nao ha valor derivado antes da hora.

O que a reordenacao realmente causou esta em D2 -- e um problema de **o que
`_checar_requisitos` enxerga**, nao de dado calculado cedo demais.

### Inflacao por dedicacao/arquetipo -- NAO ha valor absurdo nao sinalizado

2.128 feats com trait `archetype` (dos quais as 226 dedicacoes) rodados um a um
numa ficha Guerreiro 4 (`h02`):

- **0 crashes**
- HP fora de faixa: 1 caso, `wb:feat/thick-hide-mask` (+20). E dado correto
  (`flat_modifier hp: 20`, feat de nivel 20) e o motor sinaliza
  `character_level >= 20` em `fora_do_requisito`.
- Proficiencia alta: 31 casos, 29 deles `untrained -> expert` de dedicacoes que
  realmente concedem expert no dado. O unico `master` em nivel 4 e
  `wb:feat/physical-training` (feat de nivel 8 que concede `acrobatics: master` e
  `athletics: master` no proprio dado), tambem sinalizado.
- Pericia livre inflada (>+2): **0 casos**.

Ou seja: aplicar o efeito de uma escolha fora do requisito e comportamento
esperado pelo principio zero, e a marcacao acompanha. A excecao e D2, onde a
marcacao some.

### Robustez do motor com documento valido -- NAO explode

3.000 documentos aleatorios (`h11`, semente fixa): 1 a 4 classes sorteadas,
niveis 1 a 20, ate 10 feats aleatorios entre os 6.273, `pega` removido em 5% das
escolhas, `em` removido em 5%, `pega` como lista em 3%, `em` fora da faixa,
`skill_increase` e `boosts_livres` aleatorios, ordem embaralhada, ator com
companheiro. **0 crashes, 0 tipos de excecao distintos.** Todos os pontos de
quebra encontrados estao concentrados em `nivel == 0` (D1).

Especificamente testados e OK: 20 classes diferentes numa ficha, `em: 0`,
`skill_increase` com `pega` ausente, `em` como string.

### Guarda de ciclo -- adequada

`MAX_PROFUNDIDADE_GRANTS = 8`; a profundidade maxima real do grafo estatico de
`grant_feat` na base e **2** (medida independente, `h04`/`h16`). Os 31 registros
que concedem a si mesmos sao podados por `visitados` como a docstring afirma. O
teto nunca e alcancado -- e folga, nao risco.

### Empilhamento de `skill_increase` -- correto

Guerreiro/Ladino 8, aumentos repetidos na mesma pericia:
`0 -> untrained, 1 -> trained, 2 -> expert, 3 -> master`. O teto por nivel e
respeitado e o `aplicar` com `melhor_rank` nao trava o segundo degrau, como eu
suspeitava que travaria.

### `_nova_dedicacao_exige_dois_feats` com dedicacao escolhida -- correto

Guerreiro 8 com `rogue-dedication` + N feats de Rogue + `barbarian-dedication`:
com 1 feat sinaliza, com 2 feats fica limpo. A contagem no tempo funciona. O
defeito e so o cego para concedidos (D3).

### `_higiene_de_slot` nos exemplos versionados -- sem falso positivo

Os 9 documentos de `motor/exemplos/` geram 1 aviso de higiene no total, e e o
aviso desejado (`guerreiro4-fa-class-feat-no-slot.json`: Reactive Shield sem
trait `archetype` no slot gratuito). Os outros 8 saem limpos.

### `_aumentos_de_pericia` com personagem de nivel >= 1 sem aumento disponivel -- correto

Guerreiro 1 com um `skill_increase` no nivel 3 avisa duas vezes com mensagem
precisa (`1 aumento(s) escolhido(s) para 0 disponivel(is) em []`) e nao explode.
O crash e exclusivo do nivel 0 (D1).

---

## (c) Contagem

**6.881 derivacoes nomeadas** + varredura termo a termo dos 6.273 feats com
`requires` nos dois motores (~13 mil derivacoes adicionais).

| script | o que | casos |
|---|---|---|
| `h01` | documentos malformados | 16 |
| `h02` | feats com trait `archetype`, um a um | 2.129 |
| `h03` | embaralhamento das escolhas | 321 |
| `h04`/`h05`/`h10` | analise do grafo sobre 19.705 registros | -- |
| `h06`/`h07` | falso positivo das regras 63/64/67 | 15 |
| `h08` | dupla contagem (HP, pericia livre, background) | 25 |
| `h09` | gap de origens + higiene nos exemplos | 11 |
| `h11` | fuzz aleatorio | 3.000 |
| `h12` | matriz classe x nivel x dedicacao, velho x novo | 1.350 |
| `h13`/`h14` | auto-satisfacao de requisito, velho x novo | ~13.000 |
| `h15`/`h16` | casos minimos e verificacoes finais | 14 |

## Ordem sugerida de correcao

1. **D1** -- `next(..., "expert")` ou guarda de `self.nivel == 0`. Uma linha,
   destrava todo o estado inicial do construtor.
2. **D2** -- avaliar `requires` contra o estado sem o proprio feat. E o defeito
   que apaga sinal, que e o oposto do que o principio zero pede.
3. **D3** -- unificar a nocao de "tenho": as regras 63 e 64 precisam ler
   `concedidos` como `_termo_has` ja le.
4. **D4** -- incluir ancestria, heranca e background em `origens` (e o aviso de
   alvo nao resolvido passa a ter alcance).
5. **D5** -- decidir uma politica unica para escolha de nivel futuro e aplicar
   nas tres rotinas.
6. **D6**/**D7**/**D8** -- higiene.
