---
title: Auditoria de fichas montadas contra as regras de multiclasse
project: waybuilder
created: 2026-07-27
status: concluido
---

# Auditoria de fichas montadas contra as 22 regras da casa

8 fichas de personagem montadas em `motor/exemplos/` e conferidas a mao contra
`specs/2026-07-26-regras-multiclasse.md` e o PF2e RAW. Cada ficha roda com
`python3 motor/ficha.py motor/exemplos/<arquivo>.json`. Nenhum dos 9 exemplos
pre-existentes foi alterado; `motor/motor.py` e `motor/ficha.py` tambem nao
(outros agentes mexendo neles em paralelo).

Metodologia: pra cada ficha, os atributos e o HP foram recalculados a mao
(ancestria + background + classe + boosts livres declarados) e comparados
com a saida do motor; proficiencias/saves foram conferidos contra os `grants`
crus da base (`pipeline/base/index.json`) e contra o texto RAW quando havia
duvida (`pipeline/base/text/feat.json`); requisitos de feat foram checados
contra o campo `requires` de cada id antes de montar a escolha.

---

## Achados (defeitos), por ordem de impacto

### D1 -- Boosts de ancestria, background e key-ability de classe NUNCA sao aplicados automaticamente

`Personagem._atributos` / `aplicar_boosts` (motor.py): um boost com
`ability_boost.livre = true` (totalmente livre, sem opcoes) ou com
`opcoes` de tamanho > 1 (escolha entre varios) e SO logado em
`self.origem_boost` -- nunca somado a `self.boosts`. Confirmei com um repro
isolado, fora das 8 fichas do pedido:

```
Fighter 1, Human, background Warrior, UM SO boosts_livres [str,dex,con,wis]
-> atributos finais: str=12, dex=12, con=12, wis=12 (10 + so o boosts_livres)
-> os 2 boosts livres do Human, o par con/str e o livre do Warrior,
   e o key ability (dex/str) do Fighter -- tudo ficou de fora, em silencio.
```

So e aplicado o caso `opcoes` de tamanho EXATAMENTE 1 (boost fixo, sem
escolha) -- confirmado com Gnome/Elf/Dwarf/Leshy/Orc (todos tem 2 boosts
fixos + 1 livre): os 2 fixos SEMPRE aplicaram certo nas 8 fichas; o livre
nunca aplicou sozinho. E o mesmo caminho de codigo que aplica a falha
(`ability_flaw`) sem restricao -- por isso falha sempre funciona e boost as
vezes nao.

**Impacto**: toda ficha (as 9 antigas incluidas, quando usam Human ou
qualquer background) fica sistematicamente com atributos, HP e saves
abaixo do RAW **sem nenhum aviso** -- `origem_boost` nem aparece em
`visao()` nem em `ficha.py`. Nas minhas 8 fichas eu compensei manualmente
via `boosts_livres` extra (documentado na nota de cada uma) pra ter numeros
corretos; sem essa compensacao cada ficha teria saido de 2 a 6 pontos de
atributo abaixo do esperado, em silencio.

### D2 -- Marshal Dedication (e provavelmente outras dedicacoes com "escolha condicional") aplica os dois lados da escolha, incondicionalmente

RAW (`pipeline/base/text/feat.json`, `wb:text/feat/marshal-dedication`):
*"Choose Diplomacy or Intimidation. You become trained in that skill or
become an expert if you were already trained in it."* -- uma escolha, um
resultado condicional.

O dado extraido tem 4 `grants` incondicionais: `diplomacy: trained`,
`diplomacy: expert`, `intimidation: trained`, `intimidation: expert`. O
motor aplica todos (regra do "melhor rank"), entao qualquer personagem com
Marshal Dedication sai com **Diplomacy E Intimidation em EXPERT** mesmo
nunca tendo sido treinado em nenhuma das duas antes. Reproduzido em 3 das 8
fichas (`ranger4-fa-marshal`, `barbaro6-fa-duas-dedicacoes-limpo`,
`ladino2-druida2-bardo2-fa`) -- em todas as tres, ambas as pericias saem
Expert de graca no nivel 2/6/2 de personagem.

### D3 -- `requires` de feat multi-classe fica preso a UMA classe so

Feats com traits de VARIAS classes conjuradoras (ex.: Reach Spell --
bard/cleric/druid/oracle/sorcerer/witch/wizard) tem `requires` derivado
travado em **uma unica** classe (a que aparece primeiro na lista de traits,
aparentemente por ordem alfabetica):

```
Reach Spell        traits [bard,cleric,druid,...,wizard]  requires class_level bard>=1
Widen Spell         traits [druid,...,wizard]              requires class_level druid>=1
Cantrip Expansion   traits [bard,cleric,...,wizard]         requires class_level bard>=2
Enhanced Familiar    traits [animist,druid,...,wizard]       requires class_level animist>=2
Conceal Spell        traits [animist,...,witch,wizard]        requires class_level animist>=2
Irezoko Tattoo       traits [bard,champion,...,wizard] (13!)  requires class_level bard>=4
```

Um Mago pegando Reach Spell sairia **injustamente** marcado em
`fora_do_requisito`, mesmo cumprindo o requisito real (qualquer conjurador
nivel1+). Descobri isso tentando usar Conceal Spell/Silent Spell no Mago da
ficha 6 e vendo o requisito travado em Animist; troquei por feats de trait
unico pra nao confundir o teste da regra 23. O bug e do pipeline de derivacao
de gate (`pipeline/derivar_gate_nivel.py`, provavelmente pega so o primeiro
elemento de `traits` em vez de montar um `any` com todas as classes listadas
no feat).

### D4 -- Class-features compartilhadas entre classes perdem a variancia de cada classe

`wb:class-feature/weapon-expertise` e usado por **14 classes diferentes**
(Champion, Druid, Exemplar, Guardian, Investigator, Kineticist, Magus,
Oracle, Psychic, Sorcerer, Swashbuckler, Thaumaturge, Witch, Wizard) com um
UNICO `grants`: `{simple: expert, unarmed: expert}`. Isso e o beneficio de
Mago/Druida (que so ganham isso); o Campeao de verdade ganha **martial**
tambem no mesmo feature (RAW: *"simple weapons, martial weapons, and
unarmed attacks increase to expert"*), mas como o registro e compartilhado
e generico, o Campeao nunca recebe o bump de martial.

Reproduzido na ficha 7 (`campeao6-alquimista4-fa-nivel10`, Campeao 6): a
ficha mostra `martial=trained` quando deveria virar `expert` a partir do
nivel 5 de Campeao (a feature "Weapon Expertise" aparece corretamente na
lista de identidade, so o numero que ela deveria mudar nao muda).

### D5 -- `weapon_proficiency` (tipo de grant do Archer Dedication) e ignorado pelo motor

`_proficiencias` so olha `g["proficiency"]` e `g["skill_training"]`; nunca
`g["weapon_proficiency"]`. O beneficio PRINCIPAL do Archer Dedication --
elevar a proficiencia de arcos/bestas ao nivel de martial/simple -- fica
sem nenhum efeito mecanico. Nas fichas com Ranger/Barbaro o efeito ficou
mascarado porque a classe ja dava `martial` treinado por outro caminho; na
ficha 8 (Kineticist, que so tem `simple` treinado nativamente) o buraco
aparece cru: **Composite Shortbow (categoria martial) sai `untrained`,
ataque +2**, quando o Archer Dedication deveria pelo menos deixar essa arma
utilizavel.

---

## Achados menores

- **Eixo `outras-opcoes`** (pipeline de subclasses): pra varias classes
  (Cleric 21 opcoes, Barbarian 11, Champion 6, Alchemist 35) mistura
  features de VARIOS niveis (1 a 19) sob `nivel=1` (ou `nivel=0` no
  Champion) e so permite escolher UMA. Ou fica sem escolher (gera aviso
  sempre) ou escolhe e o `nivel_de_classe` gravado fica errado (sempre 1,
  mesmo pra uma feature real de nivel 9). Para Druida (a Ordem legitima
  cai nesse balaio, mas so ela), Bardo, Rogue e Kineticist o mesmo padrao
  por acaso nao causou problema pratico nas minhas fichas (ou a unica
  opcao real era mesmo de nivel1, ou o bloco ficou fora do alcance do
  nivel de classe atual) -- pra Cleric/Barbarian/Champion/Alchemist e uma
  lacuna real.
- **`grant_feat` de background com alvo nao resolvido** (nome cru em vez
  de id) -- ja documentado no proprio `motor.py`
  (`_resolver_cadeia_de_grants`), reconfirmado em 3 fichas (Gladiator ->
  Impressive Performance, Field Medic -> Battle Medicine, Herbalist ->
  Natural Medicine). Nao e achado novo.
- **Grant duplicado**: `wb:feat/clan-lore` tem
  `{"skill_training":{"free":1}}` DUAS vezes no array `grants`, inflando
  o contador exibido `pericias_livres` em +1 (so o numero mostrado, nao
  afeta nenhuma pericia real).
- `spellcasting.tradition` do Feiticeiro fica com um texto explicativo
  ("variavel, definida pela escolha de bloodline...") em vez da tradicao
  resolvida a partir da bloodline escolhida (deveria virar `divine` pra
  Diabolic).
- Rotulo "prof N" nas linhas de detalhe de `_ataques` mistura nivel+rank
  num so numero em vez de separar -- confuso de ler, mas o total final
  bate certo (nao e erro de conta).

---

## O que conferiu CERTO

- **Regra 1** (nivel de personagem = soma dos niveis de classe) -- 8/8.
- **Regra 3** (bonus = nivel de personagem + rank) -- em todo save, AC,
  ataque, pericia e DC conferido.
- **Regra 4** (duas classes com a mesma proficiencia, vale o melhor rank)
  -- testado em cruzamentos reais: Fighter/Cleric (Fort/Ref do Fighter,
  Will do Cleric vencendo cada um no seu forte) e Champion/Alchemist
  (Reflex do Alchemist vencendo o do Champion).
- **Regra 7** (nivel1 de qualquer classe da o pacote cheio) -- confirmado
  inclusive o caso conhecido do Fighter (Expert em armas desde o nivel 1,
  nao so nivel 5 como eu suspeitei por engano antes de checar o dado).
- **Regra 8** (key ability e class feat de nivel1 SO da 1a classe) --
  quando a classe tem 1 unica opcao de key ability (Barbarian, Sorcerer,
  Wizard, Kineticist) o boost aplica sozinho, corretamente; quando tem 2
  (Fighter, Ranger, Champion) cai no D1.
- **Regra 9/10** (pericias automaticas sempre; orcamento livre por delta)
  -- testado na multiclasse tripla (Ladino/Druida/Bardo): o orcamento nao
  duplicou entre as 3 classes.
- **Regra 11** (HP por nivel da classe daquele nivel; ancestria uma vez)
  -- bateu nas 8 fichas (48, 100, 48, 68, 53, 34, 132, 80).
- **Regra 12** (class feat em nivel PAR de personagem, checado contra a
  classe daquele feat) -- inclusive cruzado (Domain Initiate de Clerigo
  gasto num slot que veio do Fighter, checado contra nivel de Clerigo).
- **Regra 13** (feat de arquetipo em slot de classe conta nivel de
  personagem) -- Crossbow Terror gasto em class_feat, contando pra regra
  RAW de "2 feats antes da proxima dedicacao".
- **Regra 14/15** (cadencia basica + cadencia extra por classe a partir do
  nivel de entrada) -- Ladino concedendo skill feat E skill increase em
  TODO nivel de personagem 1-6, testado slot a slot.
- **Regra 16/17** (slots pelo nivel de classe cru; elevacao
  ceil(personagem/2)) -- inclusive o caso limite: em classe unica
  (Feiticeiro 5 puro, Mago 4 puro) a elevacao deu exatamente 0, como a
  spec promete ("com classe unica os dois numeros sao iguais, elevacao
  nunca chega a valer").
- **Regra 22** (focus pool unico, teto 3, somado entre classes) --
  Warpriest sem foco vs Cloistered com foco, e soma de Druida+Bardo
  batendo 2.
- **Regra 23** (exclusao mutua nivel-de-classe x dedicacao-da-mesma-
  classe) -- as DUAS direcoes sinalizaram em `fora_do_requisito`
  simultaneamente (Wizard 4 + Wizard Dedication), e a ficha continuou
  derivando normalmente (HP, atributos, conjuracao, tudo calculado): o
  motor NUNCA bloqueou, exatamente como o principio zero exige.
- Cadeia de `grant_feat` estatica: Duelist Dedication -> Quick Draw,
  Warrior of Legend -> Diehard, ambos conferidos contra o texto RAW.
- Teto de rank por nivel (`TETO_DE_RANK`) barrando um `skill_increase`
  que iria virar master fora do nivel permitido, sem quebrar nada.
- O motor nao quebra numa classe sem `spellcasting` (Kineticist) nem
  quando um feat pede algo que a ficha nao tem -- sempre sinaliza, nunca
  lanca excecao.

---

## As 8 fichas

### 1. `ranger4-fa-marshal.json` -- Talia Vento-Leste
Ranger 4 puro + Free Archetype com Marshal Dedication (arquetipo comum,
NAO-multiclasse). HP 56 (8 + 4x12) certo. AC 20 certo. Saves certos
(regra7: Ranger da Expert em Percepcao e nos 3 saves e melhora Will pro
Expert no nv3). `fora_do_requisito` vazio. Achados aqui: D1 (compensado
manualmente) e D2 (Diplomacy/Intimidation ambos Expert).

### 2. `barbaro6-fa-duas-dedicacoes-limpo.json` -- Grosh Punho-de-Ferro
Barbaro 6 + DUAS dedicacoes de FA respeitando a regra RAW de 2 feats entre
elas (Archer@2 -> Quick Shot@4 -> Crossbow Terror gasto no slot de CLASSE
@6, ANTES de Marshal Dedication@6 no array -- contagem bate 2 antes da 2a
dedicacao ser avaliada). Zero `fora_do_requisito`. HP 100 certo. Confirmei
que Brutality (nv5) da Expert em simple/martial/unarmed -- bati contra o
texto RAW antes de aceitar como certo (nao e defeito, e como o Barbaro
funciona mesmo). Achados: D1, D2.

### 3. `guerreiro2-clerigo2-fa.json` -- Ser Aldric Punho-Sagrado
Exatamente o exemplo que o dono deu: Guerreiro 2 / Clerigo 2 + FA. Cleric
com subclasse Warpriest (proficiencia de conjuracao mais lenta, sem foco
de graca -- testei contra Cloistered pra ver a diferenca). class_feat@4
gasto em Domain Initiate (feat de Clerigo) checado contra nivel de
Clerigo (2), nao de personagem (4) -- regra 12 na pratica. Saves mostram
a regra 4 em acao: Fort/Reflex vem do Fighter, Will vem do Cleric. DC de
conjuracao 19 conferida a mao. Zero `fora_do_requisito`.

### 4. `ladino2-druida2-bardo2-fa.json` -- Fizzle Tres-Chapeus
Multiclasse tripla: Ladino 2 / Druida 2 / Bardo 2, personagem 6. Skill
feat em TODOS os niveis 1-6 (regra 15, Ladino) e 5 aumentos de pericia
usados (niveis 2-6), incluindo um que treina pericia nova do zero
(Diplomacy -- so que ja saiu Expert por causa do D2, entao o aumento bateu
no teto e ficou capado -- o proprio motor pegou isso certo, so o alvo que
ja estava "contaminado" pelo D2). Focus pool = 2 (Druida 1 + Bardo 1,
somado certo). Duas conjuracoes simultaneas (Druida e Bardo) com elevacao
+2 cada, checadas.

### 5. `feiticeiro5-fa-diabolico.json` -- Ondina Sangue-de-Chifre
Conjurador puro nivel 5 (Feiticeiro, Bloodline Diabolic) + FA. Elevacao
deu **+0** -- confirma que classe unica == RAW puro, como a spec promete.
Slots 4/4/3 nos ranks 1/2/3 batem com a tabela nativa. DC 21 conferida.
Focus pool 1. Achado menor aqui: tradicao da magia aparece como texto
explicativo em vez de "divine".

### 6. `mago4-fa-regra23-propria-dedicacao.json` -- Cassian Duas-Faces
O caso da regra 23: Mago 4 com Wizard Dedication pega no slot de FA do
nivel 2. Resultado: DUAS entradas em `fora_do_requisito` (uma por
`_veto_dedicacao_da_propria_classe`, outra por
`_veto_classe_de_dedicacao_ja_pega`), e a ficha inteira continua
calculando normal -- HP 34, DC 20, tudo certo, nada bloqueado. Confirmei
tambem que o efeito mecanico da dedicacao (Arcana treinada) foi aplicado
mesmo com a escolha marcada como invalida -- o sinal e puramente
informativo, exatamente como o principio zero pede.

### 7. `campeao6-alquimista4-fa-nivel10.json` -- Borin Escudo-Sagrado
Nivel 10 (Campeao 6 / Alquimista 4) pra exercitar cadencia de slot e
aumento de pericia num nivel mais alto: 6 class feat, 5 skill feat, 2
general, 3 ancestry, 5 free_archetype, 4 aumentos de pericia disponiveis.
HP 132 certo. Aqui apareceu o D4 (martial deveria ser Expert pelo Weapon
Expertise do Campeao nv5 e ficou Trained). `fora_do_requisito` tem 2
entradas: Disarming Block (exige Athletics treinado, personagem nao tem --
de proposito, pra mostrar sinalizacao de pre-requisito comum, nao so da
regra 23) e uma segunda que eu mesmo causei escolhendo Battleforger sem
ter Crafting Master -- corrigido na ficha (troquei por Kneel for No God,
que bate certo com a heranca escolhida).

### 8. `kineticista6-fa-fogo.json` -- Braseiro Raiz-Funda
Classe incomum pedida explicitamente: Kineticist 6 puro + FA (impulsos de
fogo: Burning Jet, Blazing Wave, Crawling Fire). HP 80 certo. Motor nao
quebra numa classe sem `spellcasting`. Aqui o D5 aparece cru: Composite
Shortbow com Archer Dedication sai `untrained`, ataque +2, porque
`weapon_proficiency` e ignorado e o Kineticist nao tem martial por
nenhuma outra via -- nas fichas 1 e 2 (Ranger/Barbaro) o mesmo defeito
ficou mascarado porque a classe ja dava martial treinado de outro jeito.
