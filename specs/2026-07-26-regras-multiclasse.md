---
spec: regras-multiclasse
project: waybuilder
version: 1
status: aprovada
created: 2026-07-26
---

# Regras caseiras de multiclasse -- Waybuilder

Substitui o multiclasse do Pathfinder 2e (arquetipos de dedicacao comprados com
class feats) por multiclasse ao estilo D&D 5e: niveis de classe que se dividem.

Toda afirmacao factual sobre o PF2e neste documento foi verificada contra o
Elasticsearch do Archives of Nethys (indice `aon`) durante o design.

## O principio que organiza tudo

Uma distincao resolve quase toda pergunta de borda:

> **Recurso de personagem** -- boost de atributo, class feat, orcamento de
> pericia. E do personagem: vem uma vez, da primeira classe, ou por orcamento
> fechado.
>
> **Identidade de classe** -- Racket, Rage, Instinct, Thesis, Bloodline,
> Hunter's Edge, a reacao de causa do Campeao, pericias assinatura. E da classe:
> vem com o nivel, sempre, de qualquer classe.

E por isso que gastar nivel de classe vale a pena: ele compra identidade, e
nenhuma dedicacao compra identidade integra. Verificado: o arquetipo do Ladino
nao concede Racket em feat nenhum; o do Mago nao concede Arcane Bond nem Thesis;
Sneak Attacker congela em 1d6 sem escalar; Spellstriker capa a recarga do
Spellstrike em 1 minuto.

---

## Estrutura

**1.** `nivel_de_personagem = SOMA(niveis_de_classe)`. A cada subida, +1 nivel
numa classe existente ou numa classe nova.

**2.** Free Archetype sempre ligado.

## Proficiencia

**3.** Bonus total = `nivel_de_personagem + rank`. O **rank**
(Trained/Expert/Master/Legendary) vem do nivel da classe que concede.

**4.** Duas classes concedendo a mesma proficiencia: vale o melhor rank.

**5.** Class DC e por classe, com rank pelo nivel daquela classe. Efeito que diz
"your class DC" sem especificar qual usa o **maior** class DC do personagem.

**6.** Sem formula de amolecimento de rank. Considerada e **descartada**: o gap
real de um 50/50 marcial e de ~1 rank (Barbaro para em Master via Weapon Mastery
no 13; um Barbaro 10 e Expert), e a formula `floor((char+classe)/2)` zerava o
custo do multiclasse em vez de ajusta-lo.

## Nivel 1 de classe

**7.** Pacote **cheio**, de qualquer classe: saves, Percepcao, armas, armadura e
as features de identidade. Melhor rank entre as classes.

> Aceito de olho aberto. Monge nivel 1 da **Expert nos tres saves** e Expert em
> unarmored (verificado); Guerreiro e Barbaro dao Expert em Percepcao. Um
> Monge 1 / Guerreiro 1 no nivel de personagem 2 tem o melhor perfil defensivo
> do jogo. Racional: o nivel fica gasto pra sempre, e um mago nao vai querer o
> resto do pacote de Monge.

**8.** Somente da **primeira classe**: o boost de habilidade-chave e o class feat
concedido no nivel 1 de classe.

> **16 classes** dao class feat no nivel 1: Alchemist, Barbarian, Champion,
> Commander, Exemplar, Fighter, Guardian, Gunslinger, Inventor, Investigator,
> Kineticist, Monk, Ranger, Rogue, Swashbuckler, Thaumaturge. A implementacao
> **deriva isso de query**, nunca de lista escrita a mao -- essa lista ja errou
> tres vezes durante o design (3 -> 6 -> 16), e a terceira foi por query
> ingenua: o Summoner concede "evolution feat" no nivel 1, que e class feat com
> outro nome, e nao casa com o padrao `"<classe> feat"`. Sao ao menos 17.
>
> **Feat concedido por dentro de uma feature de identidade** -- order feat do
> Druida, evolution feat do Summoner -- acompanha a feature pela regra 7, e nao
> cai nesta regra. Sem isso, a identidade vem oca.

## Pericias

**9.** As pericias automaticas da classe nova sao sempre concedidas -- sao
identidade.

**10.** As escolhas livres seguem
`delta = max(0, orcamento_livre(C) - total_de_escolhas_livres_ja_concedidas)`,
gastas dentro da lista de C. As pericias automaticas da regra 9 **nao entram**
nessa conta dos dois lados.

> Resolve a contradicao entre "pacote cheio" e "delta zero": um Clerigo tardio
> fica treinado em Religiao porque Religiao e o Clerigo; o que ele nao ganha e
> orcamento livre extra. O delta e matematicamente um `max`, entao a ordem das
> classes nao muda o total.

## Pontos de vida

**11.** Por nivel, da classe que recebeu aquele nivel. HP de ancestralidade no
nivel 1.

## Feats

**12.** Class feat a cada nivel **par de personagem** (10 no total). Gastavel em
qualquer classe do personagem; o requisito de nivel do feat e checado contra o
nivel **daquela classe**.

**13.** Feat de arquetipo vem do slot de Free Archetype e e checado contra o
nivel de **personagem**. Se um class feat for gasto num feat de arquetipo,
tambem vale nivel de personagem -- arquetipo nao pertence a classe nenhuma.

**14.** A cadencia **basica** que todo personagem tem -- ancestry feat, general
feat, skill feat, boosts de 5/10/15/20, skill increase -- segue o nivel de
personagem, sem mudanca.

**15.** Quando uma **classe** concede cadencia extra ("ganha X todo nivel"), o
extra passa a valer a partir do nivel de personagem em que aquela classe entrou.
Escolher cedo compensa muito, escolher tarde vale pouco.

> A regra 15 sempre vence a 14 no que for **concedido pela classe**; a 14
> continua valendo para a linha de base. Casos conhecidos: o Ladino concede
> skill feat **e** skill increase todo nivel; o Investigador concede skill
> increase todo nivel. Levantar os demais e tarefa de query no Projeto A.

## Conjuracao

**16.** Numero de slots e rank base acessivel vem do nivel de classe cru, na
tabela nativa do PF2e. Sem houserule.

**17.** **Elevacao:** `rank_efetivo = ceil(nivel_de_personagem / 2)`.
Vale para truque, focus spell e magia de slot.

**17b.** **Teto para magia que age sozinha.** Magia com o trait `summon`, e magia
de efeito continuo autonomo (Spirit Link, Protector Tree), elevam no maximo
`rank_do_slot + 2`.

> Principio: invocacao **cria** economia de acao em vez de gasta-la. Todo o
> argumento de autocontencao da regra 17 se apoia em o dip perder acoes
> conjurando -- invocacao inverte esse limitador em vez de pagar por ele. Cura
> nao entra: curar custa duas acoes tuas, todas as vezes.
>
> Numeros verificados (Summon Animal, `Heightened (10th) Level 15`, personagem
> nivel 20): dip de Mago 1 cai de criatura nivel 15 para **nivel 2**;
> Mago 10 / Guerreiro 10 fica em **nivel 9**; Mago 20 puro nao muda, porque o
> `+2` nao tem para onde ir a partir do rank 10.
>
> Descartado: usar o rank cru do slot. Mataria tambem o multiclasse honesto --
> um Mago 10 invocando criatura nivel 5 num personagem 20 e decoracao.

> Marcado como botao de playtest ("fecho sem teto a priori").
>
> A regra do trait Cantrip do PF2e ja e *"automatically heightened to half your
> level rounded up"*, e a regra de Focus Spells amarra as duas: *"just like
> cantrips are"*. A houserule so garante que "your level" continua sendo o nivel
> de personagem agora que existem dois numeros.
>
> Tetos de +2 e +4 foram testados por simulacao e descartados. Com teto de +2 o
> dip entregava **225 HP/dia** de cura contra **262** da dedicacao de Clerigo --
> que e **gratis** sob Free Archetype. Um nivel inteiro de personagem rendendo
> menos que um feat gratuito viola a regra 21.

**18.** A elevacao **nao** vale para slots de arquetipo. Free Archetype e tudo
que vem por ele roda RAW puro.

## "Your level"

**19.** Em texto de regra impresso, "your level" significa **nivel de
personagem** -- **exceto** onde o arquetipo equivalente do PF2e **nega,
congela, modifica ou gateia atras de feat** a feature. Nesses casos, e o nivel
daquela classe.

> A lista de excecoes **nao e escrita a mao, e derivada**: onde o RAW achou a
> feature perigosa em versao rasa, ele ja sinalizou travando o arquetipo.
>
> | Feature | O que o arquetipo faz | "your level" = |
> |---|---|---|
> | Truque | da, elevando por nivel de personagem | personagem |
> | Focus spell | da, elevando por nivel de personagem | personagem |
> | Companheiro animal | da, escalando por nivel de personagem | personagem |
> | Advanced alchemy | **congela em 1** | nivel de Alquimista |
> | Reacao de causa do Campeao | **gateia** atras do feat Champion's Reaction (Feat 6) | nivel de Campeao |
> | Elemental blast do Kineticist | **gateia** atras de Improved Elemental Blast | nivel de Kineticist |
> | Exploit Vulnerability do Thaumaturge | **modifica** (vira Glimpse Vulnerability) | nivel de Thaumaturge |
>
> Validado sobre 826 documentos que citam "your level" nas categorias `spell`,
> `feat`, `class-feature` e `action`. O universo total e 1.335 -- os 509
> restantes sao majoritariamente equipamento e ficam fora do escopo de ficha.
> A maioria dos 826 e magia de forma de batalha (`AC = N + your level`), que se
> auto-limita pelo rank da magia -- o portao de acesso faz o trabalho, nao o
> termo de nivel.
>
> **A tabela e ilustrativa, nao normativa.** A regra e a derivacao; a tabela e
> so o resultado dela em cinco casos conhecidos. Numa primeira redacao esta
> tabela afirmava que o arquetipo de Campeao **nao** concedia a reacao -- era
> falso, o feat Champion's Reaction existe em CRB e Player Core 2. O verdict
> final nao mudou (gateado atras de feat tambem cai em nivel de classe), mas
> serve de aviso: cada linha sai de consulta, nunca de memoria.

## Arquetipos

**20.** Dedicacoes continuam existindo como rota paralela mais barata, rodando
RAW. **Dedicacao da propria classe e permitida.**

> Decisao consciente, nao omissao. O custo conhecido: o feat **Advanced Dogma**
> e seus irmaos dizem *"your [classe] level is equal to half your character
> level for the purpose of meeting prerequisites"* e sao **repetiveis**. Uma
> classe pura que se dedica a si mesma converte o trilho de Free Archetype em
> class feats extras. O RAW proibe por isso.
>
> Medido durante o design: 24 dos 27 feats que usam esse padrao sao gate de
> pre-requisito, e so 3 escalam efeito -- esses 3 dizem "character level"
> explicitamente e nao sao afetados.
>
> Fica na mesa. Ver "O que o app nao arbitra".

## O que o app nao arbitra

Tres decisoes ficam com o mestre, de proposito. O app modela estrutura; a mesa
resolve julgamento.

| Caso | Por que fica fora |
|---|---|
| **Retraining** de nivel de classe | e negociacao de ficha, nao regra de construcao |
| **Conjurar abaixo do rank efetivo** | e escolha tatica no momento do lance |
| **Dedicacao da propria classe** | e abuso reconhecivel, mais barato de coibir socialmente que de modelar |

O criterio comum: quando o custo de modelar supera o custo de um mestre dizer
"nao", nao modela. O app nunca **impede** esses casos -- so nao os automatiza.

**21.** **Regra de sanidade:** a rota de nivel de classe nunca pode entregar
menos que a rota de dedicacao. Se entregar, niveis param de valer a pena e o
design inteiro cai.

## Focus points

**22.** Pool unico do personagem, teto 3, independente de quantas classes.

---

## Fora de escopo

- **Retraining** de nivel de classe: resolvido na mesa, nao no app.

## Itens de playtest, nao de regra

1. **Dip tardio compensa mais que dip cedo.** Guerreiro 19 / Clerigo 1 no nivel
   20 quase nao paga nada: o ataque usa nivel de personagem, entao Guerreiro 19 e
   Guerreiro 20 batem igual. So se perde o class feat e a feature de nivel 20.
2. **Conjurador 50/50 fica -4 no DC.** Proficiencia de conjuracao tem quatro
   degraus (1/7/15/19) contra tres dos marciais.
3. **Homogeneizacao:** com 750 HP/dia de cura por um nivel barato, todo marcial
   vai querer Clerigo 1 no fim. Se virar problema, encarecer o dip tardio -- nao
   mexer na elevacao.
4. O teto de poder geral fica acima do baseline do PF2e (pacote cheio +
   Free Archetype + best-of). Encontros pedem ~+1 de dificuldade efetiva.

## Simulacoes que calibraram o design

Monte Carlo, 200k iteracoes por cenario, contra alvos de nivel equivalente.

**Nivel 10, Guerreiro 9 / Mago 1, combate de 4 rodadas:**

| | So atacando | +1 Breathe Fire rank 3 | +1 rank 5 |
|---|---|---|---|
| 4 mooks (cone pega 3) | 214,3 | 225,5 (+5,2%) | 250,3 (+16,8%) |
| 2 bosses (cone pega 2) | 172,5 | 171,2 (**-0,7%**) | 183,5 (+6,4%) |

No rank 3 a magia rende **menos que dar mais um ataque** contra boss. Foi o que
matou o teto de +2.

**Nivel 20, dia de aventura (4 encontros x 4 rodadas):**

| | Dano/dia | Cura/dia | Slots | DC |
|---|---|---|---|---|
| Guerreiro 20 puro | 1078 | 0 | -- | -- |
| Guerreiro 19 / Clerigo 1 | 733 | 750 | 6, so rank 1 | 34 |
| Clerigo 20 puro | **1789** | 750 | 18, ranks 1-10 | 45 |

O Clerigo puro causa **mais dano que o Guerreiro**. O dip empata na cura e perde
em tudo mais: 2,4x menos dano, 3x menos slots, e multiplicador de 0,30 contra
0,95 em magia de save. O dip nao substitui o especialista.

### Limites conhecidos destas simulacoes

Registrados porque a conclusao depende deles:

1. **O 733 do dip e artefato de estilo, nao custo de multiclasse.** A simulacao
   fez o dip gastar 12 acoes curando e comparou com um Guerreiro que so ataca.
   Isso mede o custo de jogar de healbot. Re-rodar com o dip atacando full-time.
2. **Heal nao e a unica magia de rank 1 que escala bem.** Soothe (rank 1,
   oculta) faz `Heightened (+1) +1d10+4` -> 95 HP no rank 10, 76% do Heal, em
   outra tradicao. A afirmacao original estava errada.
3. **Nao foram testadas magias sem rolagem contra defesa** alem de Heal --
   invocacao, buff, HP temporario, muralha. Foi o que a regra 17b endereca.
4. **Assuncoes assimetricas:** o Clerigo roda com DC de apex sempre contra o
   save fraco; o Guerreiro roda sem buff nem flanqueamento. Inflam o conjurador.
5. Gear, atributos e nivel dos alvos nao estavam declarados -- agora estao no
   codigo em `docs/simulacoes/`.
