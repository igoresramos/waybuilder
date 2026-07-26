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

**5.** Class DC e por classe, com rank pelo nivel daquela classe.

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
> duas vezes durante o design.

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

**14.** Ancestry feat, general feat, skill feat, boosts de 5/10/15/20 e skill
increases seguem o nivel de personagem, sem mudanca.

**15.** Feature de "ganha X todo nivel" passa a valer a partir do nivel de
personagem em que aquela classe entrou. Vale pro skill feat do Ladino e pra
qualquer outra que apareca: escolher cedo compensa muito, escolher tarde vale
pouco.

## Conjuracao

**16.** Numero de slots e rank base acessivel vem do nivel de classe cru, na
tabela nativa do PF2e. Sem houserule.

**17.** **Elevacao:** `rank_efetivo = ceil(nivel_de_personagem / 2)`.
Vale para truque, focus spell e magia de slot, sem excecao.

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
personagem** -- **exceto** onde o arquetipo equivalente do PF2e trava ou nega a
feature. Nesses casos, e o nivel daquela classe.

> A lista de excecoes **nao e escrita a mao, e derivada**: onde o RAW achou a
> feature perigosa em versao rasa, ele ja sinalizou travando o arquetipo.
>
> | Feature | O que o arquetipo faz | "your level" = |
> |---|---|---|
> | Truque | da, elevando por nivel de personagem | personagem |
> | Focus spell | da, elevando por nivel de personagem | personagem |
> | Companheiro animal | da, escalando por nivel de personagem | personagem |
> | Advanced alchemy | **congela em 1** | nivel de Alquimista |
> | Reacao de causa do Campeao | **nao da** | nivel de Campeao |
>
> Validado sobre 826 documentos que citam "your level". A maioria e magia de
> forma de batalha (`AC = N + your level`), que se auto-limita pelo rank da
> magia -- o portao de acesso faz o trabalho, nao o termo de nivel.

## Arquetipos

**20.** Dedicacoes continuam existindo como rota paralela mais barata, rodando
RAW. Dedicacao da propria classe e permitida, por simplicidade de codigo.

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

O Clerigo puro causa **mais dano que o Guerreiro**. O dip empata so na cura --
porque Heal e a unica magia de rank 1 que escala bem indefinidamente -- e perde
em tudo mais: 2,4x menos dano, 3x menos slots, e multiplicador de 0,30 contra
0,95 em magia de save. O dip nao substitui o especialista.
