#!/usr/bin/env python3
"""
Testes do motor: cada um trava UMA regra da spec de multiclasse.

Nao sao testes de "roda sem estourar" -- cada assercao existe porque a regra
correspondente pode ser quebrada por uma mudanca inocente no pipeline, e a
diferenca entre a houserule e o PF2e oficial e justamente onde os dois numeros
(nivel de classe x nivel de personagem) divergem.

Uso: python3 teste_motor.py
"""
import json
import os
import sys
import math

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
from motor import Base, Personagem, melhor_rank, RANK_BONUS   # noqa: E402

BASE = Base()
FALHAS = []


def checar(condicao, descricao, detalhe=""):
    if condicao:
        print(f"  ok    {descricao}")
    else:
        print(f"  FALHA {descricao}   {detalhe}")
        FALHAS.append(descricao)


def personagem(escolhas, **extra):
    doc = {"esquema": "waybuilder/personagem@1", "escolhas": escolhas}
    doc.update(extra)
    return Personagem(doc, BASE)


def niveis(*pares):
    """[('wb:class/fighter', 3), ('wb:class/wizard', 2)] -> escolhas de nivel."""
    saida, n = [], 0
    for cid, quantos in pares:
        for _ in range(quantos):
            n += 1
            saida.append({"em": n, "slot": "nivel_de_classe", "pega": cid})
    return saida


FIGHTER, WIZARD, CLERIC = "wb:class/fighter", "wb:class/wizard", "wb:class/cleric"
RANGER = "wb:class/ranger"


# -- regra 1 ---------------------------------------------------------------
print("\nregra 1 -- nivel de personagem e a SOMA dos niveis de classe")
p = personagem(niveis((FIGHTER, 3), (WIZARD, 2)))
checar(p.nivel == 5, "Fighter 3 + Wizard 2 = personagem nivel 5", f"deu {p.nivel}")
checar(p.nivel_de(FIGHTER) == 3 and p.nivel_de(WIZARD) == 2,
       "cada classe guarda o proprio nivel",
       f"F={p.nivel_de(FIGHTER)} W={p.nivel_de(WIZARD)}")

# -- regra 3 ---------------------------------------------------------------
print("\nregra 3 -- bonus = nivel de PERSONAGEM + rank")
p = personagem(niveis((FIGHTER, 1), (WIZARD, 4)))
esperado = p.nivel + RANK_BONUS["expert"]
checar(p.bonus("perception") == esperado,
       "Fighter 1 num personagem 5: Percepcao usa nivel 5, nao 1",
       f"deu {p.bonus('perception')}, esperado {esperado}")

# -- regra 4 ---------------------------------------------------------------
print("\nregra 4 -- duas classes na mesma proficiencia: vale o MELHOR rank")
checar(melhor_rank("trained", "expert") == "expert", "trained vs expert -> expert")
checar(melhor_rank("master", "trained") == "master", "master vs trained -> master")
p = personagem(niveis((FIGHTER, 3), (WIZARD, 2)))
checar(p.proficiencias.get("will") == "expert",
       "Fighter (will trained) + Wizard (will expert) -> expert",
       f"deu {p.proficiencias.get('will')}")
checar(p.proficiencias.get("martial") == "expert",
       "Fighter (martial expert) + Wizard (untrained) -> expert",
       f"deu {p.proficiencias.get('martial')}")

# -- regra 7 ---------------------------------------------------------------
print("\nregra 7 -- nivel 1 de QUALQUER classe da o pacote cheio")
so_wizard = personagem(niveis((WIZARD, 5)))
com_dip = personagem(niveis((WIZARD, 4), (FIGHTER, 1)))
checar(so_wizard.proficiencias.get("martial") in (None, "untrained"),
       "Mago puro nao tem arma marcial")
checar(com_dip.proficiencias.get("martial") == "expert",
       "um unico nivel de Guerreiro ja entrega marcial expert (aceito de olho aberto)",
       f"deu {com_dip.proficiencias.get('martial')}")
checar(com_dip.proficiencias.get("heavy") == "trained",
       "e armadura pesada junto", f"deu {com_dip.proficiencias.get('heavy')}")

# -- regra 8 ---------------------------------------------------------------
print("\nregra 8 -- key ability e class feat de nivel 1 so da PRIMEIRA classe")
p = personagem(niveis((WIZARD, 3), (FIGHTER, 2)))
tem_wizard = any("Wizard" in o and "1a classe" in o for o in p.origem_boost)
tem_fighter_sem = any("Fighter" in o and "SEM boost" in o for o in p.origem_boost)
checar(tem_wizard, "Wizard entrou primeiro: da o boost de chave")
checar(tem_fighter_sem, "Fighter entrou depois: NAO da boost de chave")
p_inverso = personagem(niveis((FIGHTER, 2), (WIZARD, 3)))
checar(any("Wizard" in o and "SEM boost" in o for o in p_inverso.origem_boost),
       "invertendo a ordem, quem perde o boost e o Wizard")

# -- regra 10 --------------------------------------------------------------
print("\nregra 10 -- pericia livre por DELTA, e o total nao depende da ordem")
a = personagem(niveis((FIGHTER, 3), (WIZARD, 2)))    # 3 livres, depois 2
b = personagem(niveis((WIZARD, 3), (FIGHTER, 2)))    # 2 livres, depois 3
checar(a.pericias_livres == b.pericias_livres == 3,
       "Fighter(3) + Wizard(2) da 3 livres nas duas ordens",
       f"deu {a.pericias_livres} e {b.pericias_livres}")
checar(a.pericias_livres != 5, "nao soma os orcamentos (seria 5)")

# -- regra 11 --------------------------------------------------------------
print("\nregra 11 -- HP por nivel vem da classe QUE RECEBEU aquele nivel")
doc = {"esquema": "x", "escolhas": niveis((FIGHTER, 3), (WIZARD, 2)) + [
    {"em": "criacao", "slot": "ancestralidade", "pega": "wb:ancestry/dwarf"}]}
p = Personagem(doc, BASE)
con = p.modificadores.get("con", 0)
esperado = 10 + 3 * (10 + con) + 2 * (6 + con)
checar(p.hp == esperado,
       f"Anao + Fighter 3 (10/nivel) + Wizard 2 (6/nivel) = {esperado}",
       f"deu {p.hp}")

# -- regra 12 --------------------------------------------------------------
print("\nregra 12 -- class feat a cada nivel PAR de PERSONAGEM, nao por classe")
p = personagem(niveis((FIGHTER, 3), (WIZARD, 2)))
pares = [n for n in p.slots["class"] if n != 1]
checar(pares == [2, 4], "personagem nivel 5 tem class feat em 2 e 4", f"deu {pares}")
checar(1 in p.slots["class"],
       "e o de nivel 1, porque a primeira classe (Fighter) concede")
p_mago_primeiro = personagem(niveis((WIZARD, 3), (FIGHTER, 2)))
checar(1 not in p_mago_primeiro.slots["class"],
       "com Wizard primeiro nao ha class feat no nivel 1 (o Mago nao concede)")

# -- regras 16 e 17 --------------------------------------------------------
print("\nregras 16 e 17 -- slot pelo nivel de CLASSE, rank pelo de PERSONAGEM")
p = personagem(niveis((FIGHTER, 3), (WIZARD, 2)))
conj = p.conjuracao[0]
checar(conj["nivel_de_classe"] == 2, "os slots sao de um Mago 2")
checar(conj["max_rank_do_slot"] == 1,
       "rank maximo do SLOT e 1 (nivel de classe)", f"deu {conj['max_rank_do_slot']}")
checar(conj["rank_efetivo"] == math.ceil(5 / 2) == 3,
       "rank EFETIVO e 3 = ceil(nivel de personagem 5 / 2)",
       f"deu {conj['rank_efetivo']}")
checar(conj["elevacao"] == 2, "a houserule concede +2 ranks de elevacao")

puro = personagem(niveis((WIZARD, 5)))
checar(puro.conjuracao[0]["max_rank_do_slot"] == 3,
       "Mago 5 puro tem slot rank 3 pela tabela nativa",
       f"deu {puro.conjuracao[0]['max_rank_do_slot']}")
checar(puro.conjuracao[0]["elevacao"] == 0,
       "e nao ganha elevacao nenhuma -- a houserule nao afeta classe pura")

# -- regra 3 aplicada ao DC de conjuracao ----------------------------------
print("\nregra 3 aplicada ao DC -- nivel de personagem + rank pelo nivel de classe")
dc = p.conjuracao[0]["dc"]
checar(dc["rank"] == "trained",
       "Mago 2 e trained (expert so no nivel de classe 7)", f"deu {dc['rank']}")
esperado = 10 + p.nivel + RANK_BONUS["trained"] + p.modificadores.get("int", 0)
checar(dc["dc"] == esperado,
       f"DC = 10 + nivel 5 + trained + mod INT = {esperado}", f"deu {dc['dc']}")

# -- regra 22 --------------------------------------------------------------
print("\nregra 22 -- focus pool unico do personagem, teto 3")
p = personagem(niveis((CLERIC, 3), (WIZARD, 2)))
checar(p.focus_pool <= 3, "nunca passa de 3", f"deu {p.focus_pool}")

# -- principio zero --------------------------------------------------------
print("\nprincipio zero -- `requires` SINALIZA, nunca bloqueia")
doc = {"esquema": "x", "escolhas": niveis((FIGHTER, 2)) + [
    {"em": 2, "slot": "class_feat", "pega": "wb:feat/stonewalker"}]}   # nivel 9
p = Personagem(doc, BASE)
checar(len(p.fora_do_requisito) >= 1,
       "feat de nivel 9 num personagem 2 aparece como fora do requisito")
checar(any(e["pega"] == "wb:feat/stonewalker" for e in p.doc["escolhas"]),
       "e continua no documento -- o motor NAO removeu a escolha")

# -- regra 7 na pratica: identidade de classe ------------------------------
print("\nregra 7 -- a identidade vem inteira, e sub-escolha nao vira concessao")
p = personagem(niveis((WIZARD, 2)))
nomes = {f["nome"] for f in p.features}
checar("Arcane School" in nomes, "Mago 1 recebe a feature 'Arcane School'")
checar("Evocation" not in nomes and "Envy" not in nomes,
       "mas NAO recebe as escolas em si -- elas sao opcao de um slot",
       f"features: {sorted(nomes)}")
eixos = {s["eixo"] for s in p.slots_de_subclasse}
checar("arcane-school" in eixos and "arcane-thesis" in eixos,
       "e ganha slot de escolha para Escola e Tese", f"eixos: {eixos}")

# -- item 1: gate de nivel derivado ---------------------------------------
print("\ngate de nivel derivado -- class_level x character_level")
accompany = BASE.get("wb:feat/accompany")            # bard, nivel 8
checar("class_level" in str(accompany.get("requires")),
       "feat de classe ganha gate em class_level", str(accompany.get("requires"))[:90])

# Bardo 8 dentro de um personagem 8: atende
bardo8 = personagem(niveis(("wb:class/bard", 8)))
atende, _ = bardo8.avaliar(accompany["requires"])
checar(atende, "Bardo 8 (personagem 8) atende um feat de Bardo nivel 8")

# Bardo 2 dentro de um personagem 8: NAO atende, e e o ponto da houserule
misto = personagem(niveis((FIGHTER, 6), ("wb:class/bard", 2)))
atende, motivos = misto.avaliar(accompany["requires"])
checar(not atende,
       "Guerreiro 6 / Bardo 2 (personagem 8) NAO atende -- o gate e por CLASSE",
       f"motivos: {motivos}")
checar(misto.nivel == 8, "e o personagem tem nivel 8 mesmo assim",
       f"deu {misto.nivel}")

# feat geral usa nivel de personagem.
# Escolhido um cujo predicado seja SO o gate: `Advanced First Aid` tambem e
# geral nivel 7, mas exige `medicine >= master` -- reprovaria por outro motivo
# e o teste nao provaria nada sobre o gate.
geral = next((r for r in BASE.por_id.values()
              if r.get("kind") == "feat" and r.get("gate_de_nivel") == "geral"
              and r.get("level") in (7, 8)
              and list(r.get("requires") or {}) == ["character_level"]), None)
checar(geral is not None, "existe feat geral de nivel 7-8 so com gate de nivel")
if geral:
    atende, motivos = misto.avaliar(geral["requires"])
    checar(atende,
           f"e o personagem 8 atende ({geral['name']}, nivel {geral['level']}) "
           f"-- feat geral mira o nivel de PERSONAGEM", f"motivos: {motivos}")
    so_bardo2 = personagem(niveis(("wb:class/bard", 2)))
    atende2, _ = so_bardo2.avaliar(geral["requires"])
    checar(not atende2, "e um personagem 2 nao atende o mesmo feat")

# -- item 2: subclasse -----------------------------------------------------
print("\npredicado sabendo falar de SUBCLASSE")
cleric = BASE.get("wb:class/cleric")
prof = (cleric.get("spellcasting") or {}).get("proficiency") or {}
checar("cloistered_cleric" in prof and "warpriest" in prof,
       "o Clerigo carrega duas progressoes de conjuracao, por Doutrina")

def clerigo(doutrina, n=15):
    esc = niveis((CLERIC, n))
    if doutrina:
        esc.append({"em": 1, "slot": "subclasse", "pega": doutrina})
    return personagem(esc)

cloistered = clerigo("wb:class-feature/cloistered-cleric")
warpriest = clerigo("wb:class-feature/warpriest")
r_clo = cloistered.conjuracao[0]["dc"]["rank"]
r_war = warpriest.conjuracao[0]["dc"]["rank"]
checar(r_clo == "master", "Cloistered 15 e master", f"deu {r_clo}")
checar(r_war == "expert", "Warpriest 15 ainda e expert", f"deu {r_war}")
checar(r_clo != r_war,
       "mesma classe, mesmo nivel, ranks diferentes -- `class_level` sozinho "
       "nao alcancaria isso")

sem_escolha = clerigo(None)
checar(any("subclasse" in a for a in sem_escolha.avisos),
       "sem escolher a Doutrina, o motor AVISA em vez de escolher calado")

# -- item 3: efeito unificado ---------------------------------------------
print("\nmodelo de efeito unificado -- ancestria e background em `grants`")
anao = BASE.get("wb:ancestry/dwarf")
tipos = {k for g in (anao.get("grants") or []) for k in g}
checar("hp_ancestry" in tipos and "size" in tipos and "speed" in tipos,
       "ancestria emite hp, size e speed em grants", f"tipos: {sorted(tipos)}")
checar(anao.get("hp") == 10,
       "e os campos originais permanecem -- a projecao adiciona, nao substitui")
checar(anao.get("mechanized") is True,
       "`mechanized` deixa de mentir: ancestria tem efeito calculavel")

bg = next(r for r in BASE.por_id.values()
          if r.get("kind") == "background" and r.get("grants"))
tipos_bg = {k for g in bg["grants"] for k in g}
checar(bool(tipos_bg & {"skill_training", "ability_boost", "grant_feat"}),
       "background tambem", f"{bg['name']}: {sorted(tipos_bg)}")

# -- a pergunta central do construtor --------------------------------------
print("\na pergunta central -- 'o que meu personagem pode pegar?'")
p = personagem(niveis((FIGHTER, 3), (WIZARD, 2)))
lista = p.disponiveis("feat")
atendem = [f for f in lista if f["atende"]]
checar(len(atendem) > 0, f"{len(atendem)} feats combinam de {len(lista)}")
checar(len(atendem) < len(lista),
       "e a lista NAO e toda a base -- o predicado ordena de verdade")
nomes = {f["nome"] for f in atendem}
checar("Accompany" not in nomes,
       "feat de Bardo nivel 8 nao aparece para um Guerreiro 3 / Mago 2")
checar(all(not f["atende"] or f["motivos"] == [] for f in lista),
       "quem atende nao carrega motivo de recusa")

# -- regressao: `pega` nem sempre e um id ---------------------------------
print("\nregressao -- `boosts_livres` guarda LISTA em `pega`")
doc = {"esquema": "x", "escolhas": niveis((FIGHTER, 2)) + [
    {"em": 1, "slot": "boosts_livres", "pega": ["str", "dex", "con", "int"]},
    {"em": 2, "slot": "class_feat", "pega": "wb:feat/double-slice"}]}
try:
    p = Personagem(doc, BASE)
    checar(p.atributos["str"] >= 12, "personagem com boosts livres deriva sem estourar")
except TypeError as exc:
    checar(False, "personagem com boosts livres deriva sem estourar", str(exc))

# -- o predicado pega erro de montagem que o jogador comete ---------------
print("\nsub-escolha errada e detectada, nao silenciada")
esc = niveis((WIZARD, 2)) + [
    {"em": 1, "slot": "subclasse", "pega": "wb:class-feature/school-of-battle-magic"},
    {"em": 1, "slot": "class_feat", "pega": "wb:feat/hand-of-the-apprentice"}]
p = personagem(esc)
checar(any("Hand of the Apprentice" in f["feat"] for f in p.fora_do_requisito),
       "Hand of the Apprentice exige Universalist -- com Battle Magic, sinaliza",
       f"{p.fora_do_requisito}")

# -- regra 21: a rota de nivel nunca entrega menos que a dedicacao ---------
print("\nregra 21 -- sanidade: nivel de classe >= dedicacao")
# Rota A (houserule): Guerreiro 19 / Clerigo 1
rota_a = personagem(niveis((FIGHTER, 19), (CLERIC, 1)))
# Rota B (RAW): Guerreiro 20 + Cleric Dedication pelo slot de Free Archetype
esc_b = niveis((FIGHTER, 20)) + [
    {"em": 2, "slot": "free_archetype", "pega": "wb:feat/cleric-dedication"}]
rota_b = personagem(esc_b)
checar(rota_a.nivel == 20 and rota_b.nivel == 20, "as duas rotas no nivel 20")

ded = BASE.opcional("wb:feat/cleric-dedication")
checar(ded is not None and bool(ded.get("grants")),
       "a dedicacao de Clerigo tem efeito estruturado para comparar",
       f"grants={bool((ded or {}).get('grants'))}")

# o que a rota A entrega e a B nao: conjuracao de verdade
checar(bool(rota_a.conjuracao),
       "a rota de nivel de classe da conjuracao (slots reais)")
conj_a = rota_a.conjuracao[0] if rota_a.conjuracao else None
if conj_a:
    checar(conj_a["nivel_de_classe"] == 1,
           "com os slots de um Clerigo 1 (regra 16)")
    checar(conj_a["rank_efetivo"] == 10,
           "mas conjurando no rank 10 (regra 17: ceil(20/2))",
           f"deu {conj_a['rank_efetivo']}")

# e a identidade de classe, que a dedicacao nao compra integra
ids_a = {f["id"] for f in rota_a.features}
checar(any("cleric" in i or "doctrine" in i for i in ids_a),
       "e a identidade de Clerigo vem junto (regra 7)",
       f"features de Clerigo: {[i for i in ids_a if 'cleric' in i][:3]}")

# -- regra 17b: teto do que cria criatura -----------------------------------
print("\nregra 17b -- teto de invocacao e de ator")


def _monta(classes, atores=None):
    esc, n = [], 0
    for cid, q in classes:
        for _ in range(q):
            n += 1
            esc.append({"em": n, "slot": "nivel_de_classe", "pega": cid})
    return Personagem({"escolhas": esc, "atores": atores or [],
                       "inventario": [], "manual": {}}, BASE)


def _conj(p, nome):
    return next((c for c in p.conjuracao if c["classe"] == nome), None)

# o caso que o Igor deu: Summoner 2 num personagem 12
c = _conj(_monta([("wb:class/summoner", 2), ("wb:class/fighter", 10)]), "Summoner")
checar(c and c["rank_efetivo"] == 6,
       "heightened normal e ceil(12/2) = 6 (regra 17)",
       f"deu {c and c['rank_efetivo']}")
checar(c and c["rank_de_invocacao"] == 4,
       "mas invocacao para em 4 (regra 17b) -- a folga da 2, o PISO da "
       "dedicacao puxa para 4, e o teto de heightened (6) nao morde",
       f"deu {c and c['rank_de_invocacao']}")

# classe unica: o +2 nunca chega a valer, RAW intacto sem caso especial
c = _conj(_monta([("wb:class/summoner", 20)]), "Summoner")
checar(c and c["rank_de_invocacao"] == 10,
       "Summoner 20 puro invoca no 10 -- o teto externo protege o RAW",
       f"deu {c and c['rank_de_invocacao']}")

# a regra 17 tem que sobreviver ao teto, senao o dip morre
c = _conj(_monta([("wb:class/wizard", 2), ("wb:class/fighter", 3)]), "Wizard")
checar(c and c["rank_de_invocacao"] == 3,
       "Mago 2 / personagem 5 invoca no 3 -- a regra 17 sobrevive a 17b",
       f"deu {c and c['rank_de_invocacao']}")

COMP = [{"tipo": "companheiro", "nome": "Princesa", "classe": "wb:class/ranger",
         "escolhas": [{"slot": "animal", "pega": "wb:animal-companion/badger"}]}]
a = _monta([("wb:class/ranger", 2), ("wb:class/fighter", 10)], COMP).atores[0]
checar(a["nivel"] == 4,
       "companheiro de Ranger 2 num personagem 12 fica no nivel 4",
       f"deu {a['nivel']}")
a = _monta([("wb:class/ranger", 12)], COMP).atores[0]
checar(a["nivel"] == 12,
       "Ranger 12 PURO tem companheiro nivel 12 -- classe unica == RAW",
       f"deu {a['nivel']}")

# recorte por trait, sem lista curada
mag = {"traits": ["concentrate", "manipulate", "summon"]}
inc = {"traits": ["concentrate", "incarnate"]}
link = {"traits": ["concentrate", "healing", "manipulate", "spirit"]}
p = _monta([("wb:class/wizard", 5)])
checar(p.eleva_por_invocacao(mag) and p.eleva_por_invocacao(inc),
       "a 17b pega trait `summon` E `incarnate`")
checar(not p.eleva_por_invocacao(link),
       "e NAO pega Spirit Link -- efeito continuo nao cria criatura")

# -- maturidade do companheiro DERIVADA dos feats, nao lida do documento ----
print("\nmaturidade do companheiro -- derivada dos feats de avanco escolhidos")


def _companheiro_ranger(nivel_ranger, feats, escolha_grau=None):
    """Ranger PURO com o companheiro Badger, para isolar a trilha de avanco.

    `wb:feat/mature-animal-companion-ranger` exige (na base) `has:
    wb:feat/animal-companion` -- o id SEM sufixo `-ranger`, mesmo para Ranger
    -- entao o feat de nivel 1 pego e sempre esse."""
    esc = [{"em": n, "slot": "nivel_de_classe", "pega": RANGER}
           for n in range(1, nivel_ranger + 1)]
    esc.append({"em": 1, "slot": "class_feat", "pega": "wb:feat/animal-companion"})
    for f in feats:
        esc.append({"em": nivel_ranger, "slot": "class_feat", "pega": f})
    ator_esc = [{"slot": "animal", "pega": "wb:animal-companion/badger"}]
    if escolha_grau:
        ator_esc.append({"slot": "grau_avancado", "pega": escolha_grau})
    atores = [{"tipo": "companheiro", "nome": "Princesa", "classe": RANGER,
               "escolhas": ator_esc}]
    return Personagem({"escolhas": esc, "atores": atores,
                       "inventario": [], "manual": {}}, BASE)


p1 = _companheiro_ranger(6, [])
checar(p1.atores[0]["maturidade"] == "young",
       "Ranger 6 sem feat de avanco: companheiro fica young",
       f"deu {p1.atores[0]['maturidade']}")

p2 = _companheiro_ranger(6, ["wb:feat/mature-animal-companion-ranger"])
checar(p2.atores[0]["maturidade"] == "mature",
       "Ranger 6 com Mature Animal Companion (Ranger): mature",
       f"deu {p2.atores[0]['maturidade']}")

# houserule: o gate do feat compara com o nivel de CLASSE que concedeu o
# companheiro, nunca com o nivel de personagem
doc3 = {"esquema": "x",
        "escolhas": niveis((FIGHTER, 14), (RANGER, 6)) + [
            {"em": 20, "slot": "class_feat", "pega": "wb:feat/animal-companion"},
            {"em": 20, "slot": "class_feat", "pega": "wb:feat/mature-animal-companion-ranger"},
            {"em": 20, "slot": "class_feat", "pega": "wb:feat/incredible-companion-ranger"},
        ],
        "atores": [{"tipo": "companheiro", "nome": "Princesa", "classe": RANGER,
                    "escolhas": [{"slot": "animal", "pega": "wb:animal-companion/badger"}]}]}
p3 = Personagem(doc3, BASE)
checar(p3.nivel == 20 and p3.nivel_de(RANGER) == 6,
       "Guerreiro 14 / Ranger 6: personagem 20, mas so 6 niveis de Ranger",
       f"nivel={p3.nivel} ranger={p3.nivel_de(RANGER)}")
checar(p3.atores[0]["maturidade"] == "mature",
       "Incredible Companion (Ranger) pego com Ranger 6 (exige >=10) NAO sobe "
       "de mature -- o gate e por nivel de CLASSE, nao de personagem 20",
       f"deu {p3.atores[0]['maturidade']}")
checar(not any(e["ator"] == "Princesa" for e in p3.escolhas_de_feat),
       "e nem chega a abrir o picker nimble/savage -- o teto real e mature")

# Incredible Companion nao decide sozinho entre nimble/savage -- isso e
# escolha do jogador. Sem a escolha, a ficha NAO vira nimble por default: fica
# capada no ultimo grau CERTO (mature) e a escolha aparece como PENDENTE, no
# mesmo vocabulario que o eixo de subclasse ja usa (eixo/nivel/slot/escolhe/opcoes).
p4 = _companheiro_ranger(10, ["wb:feat/mature-animal-companion-ranger",
                              "wb:feat/incredible-companion-ranger"])
checar(p4.atores[0]["maturidade"] == "mature",
       "Incredible Companion valido mas sem escolher nimble/savage: ficha fica "
       "no ultimo grau CERTO -- nunca vira nimble por default silencioso",
       f"deu {p4.atores[0]['maturidade']}")
checar(p4.atores[0]["grau_pendente"] is True,
       "e o ator fica marcado com a escolha pendente")
pend = next((e for e in p4.escolhas_de_feat if e["ator"] == "Princesa"), None)
checar(pend is not None, "a escolha pendente aparece em `escolhas_de_feat`")
if pend:
    checar(pend["eixo"] == "grau-incredible-companion" and pend["slot"] == "grau_avancado"
           and pend["escolhe"] == 1 and set(pend["opcoes"]) == {"nimble", "savage"},
           "registrada com o MESMO vocabulario do eixo de subclasse "
           "(eixo/nivel/slot/escolhe/opcoes)", f"{pend}")
    checar(pend["escolhido"] is None, "e sem default silencioso -- escolhido fica None")
checar(any("falta escolher" in a for a in p4.avisos),
       "o motor avisa que falta escolher, em vez de assumir")

# Com a escolha declarada (no `escolhas` do proprio ator, slot `grau_avancado`),
# savage se aplica, e Specialized Companion (Player Core p.211, rules-2120)
# soma o delta -- unarmed vira expert, saves/Percepcao viram master, dano
# extra DOBRA (savage 3 -> 6) e os dados sobem de 2 para 3.
p5 = _companheiro_ranger(16, ["wb:feat/mature-animal-companion-ranger",
                              "wb:feat/incredible-companion-ranger",
                              "wb:feat/specialized-companion-ranger"],
                         escolha_grau="savage")
a5 = p5.atores[0]
checar(a5["maturidade"] == "savage" and a5["especializado"] is True,
       "com a escolha declarada: savage + specialized aplicados",
       f"maturidade={a5['maturidade']} especializado={a5['especializado']}")
checar(a5["grau_pendente"] is False, "e o ator nao fica mais pendente")
checar(a5["atributos"]["dex"] == 5 and a5["atributos"]["int"] == -2,
       "Specialized soma DEX+1/INT+2 por cima do savage "
       "(Badger DEX 2->4 savage->5 specialized; INT -4->-2 specialized)",
       f"{a5['atributos']}")
checar(a5["hp"] == 168, "HP = 8 de ancestria + (6+4) x 16 = 168", f"deu {a5['hp']}")
jaws = next(x for x in a5["ataques"] if x["nome"] == "jaws")
checar(jaws["dano"] == "3d8+11",
       "dano extra dobra (savage 3 -> 6) e os dados sobem pra 3d8 "
       "(Specialized Animal Companions)", f"deu {jaws['dano']}")
checar(a5["proficiencias"]["unarmed"] == "expert"
       and a5["proficiencias"]["perception"] == "master",
       "unarmed vira expert (1a vez) e saves/Percepcao viram master",
       f"{a5['proficiencias']}")

# -- regra 21: o dip nunca pode render menos que a rota gratuita ------------
print("\nregra 21 -- dip >= dedicacao no mesmo nivel de personagem")


def _dip(nivel_de_classe, nivel_total, classe=WIZARD):
    """`nivel_de_classe` niveis da classe, o resto em Fighter."""
    esc = [{"em": i + 1, "slot": "nivel_de_classe",
            "pega": classe if i < nivel_de_classe else FIGHTER}
           for i in range(nivel_total)]
    return personagem(esc)


# Varredura exaustiva, nao amostra: e um invariante, entao vale em TODO par.
# Sem o piso, a simulacao de 2026-07-27 achou 50 destes 204 pares violando.
violacoes = []
for nivel_personagem in range(4, 21):
    for nc in range(1, nivel_personagem + 1):
        p = _dip(nc, nivel_personagem)
        if p.cap_invocacao(nc) < p.rank_de_dedicacao():
            violacoes.append((nc, nivel_personagem,
                              p.cap_invocacao(nc), p.rank_de_dedicacao()))
checar(not violacoes,
       "em 204 pares (nivel de classe x nivel de personagem), nenhum dip "
       "invoca abaixo da dedicacao gratuita",
       f"{len(violacoes)} violacoes, ex: {violacoes[:3]}")

# e o piso nao pode furar o teto de heightened: classe unica continua RAW
furou = [n for n in range(1, 21) if _dip(n, n).cap_invocacao(n) != math.ceil(n / 2)]
checar(not furou,
       "e classe unica segue exatamente o RAW nos 20 niveis",
       f"furou em {furou}")

p = _dip(2, 12)
checar(p.cap_invocacao(2) == 4,
       "Mago 2 / personagem 12 sobe de 3 para 4 -- empata com a dedicacao",
       f"deu {p.cap_invocacao(2)}")
p = _dip(2, 5)
checar(p.cap_invocacao(2) == 3,
       "e Mago 2 / personagem 5 segue em 3: o piso nao distorce nivel baixo",
       f"deu {p.cap_invocacao(2)}")

# -- regra 23: dedicacao da propria classe ---------------------------------
print("\nregra 23 -- exclusao mutua entre nivel de classe e dedicacao da mesma classe")

BOOSTS = [{"em": 1, "slot": "boosts_livres", "pega": ["int", "wis", "dex", "con"]},
          {"em": 5, "slot": "boosts_livres", "pega": ["int", "wis", "con", "dex"]}]


def _com_dedicacao(nivel_de_wizard, nivel_total):
    esc = [{"em": i + 1, "slot": "nivel_de_classe",
            "pega": WIZARD if i < nivel_de_wizard else FIGHTER}
           for i in range(nivel_total)]
    p = personagem(esc + BOOSTS)
    return next(f for f in p.disponiveis("feat")
                if f["id"] == "wb:feat/wizard-dedication")


for nivel_wizard, rotulo in ((20, "Mago 20 puro"), (2, "Mago 2 / Guerreiro 18"),
                             (10, "Mago 10 / Guerreiro 10")):
    f = _com_dedicacao(nivel_wizard, 20)
    checar(not f["atende"] and any("regra 23" in m for m in f["motivos"]),
           f"{rotulo} nao pega Wizard Dedication, e o motivo aparece",
           f"atende={f['atende']} motivos={f['motivos']}")
checar(_com_dedicacao(0, 20)["atende"],
       "quem nao tem nivel de Mago nenhum segue pegando, como sempre")

# sentido inverso: mesma ficha, ordem trocada -- tem de pegar igual
esc = [{"em": i + 1, "slot": "nivel_de_classe",
        "pega": WIZARD if i < 2 else FIGHTER} for i in range(20)]
esc += [{"em": 2, "slot": "archetype_feat", "pega": "wb:feat/wizard-dedication"}]
p = personagem(esc + BOOSTS)
checar(any("nivel de classe" in x["feat"] for x in p.fora_do_requisito),
       "e pegar NIVEL de Mago tendo Wizard Dedication cai igual (exclusao mutua)",
       f"fora_do_requisito={[x['feat'] for x in p.fora_do_requisito]}")

esc_sem = [{"em": i + 1, "slot": "nivel_de_classe", "pega": FIGHTER} for i in range(20)]
esc_sem += [{"em": 2, "slot": "archetype_feat", "pega": "wb:feat/wizard-dedication"}]
checar(not personagem(esc_sem + BOOSTS).fora_do_requisito,
       "Guerreiro 20 so com a dedicacao, sem nivel de Mago: nada a apontar")

# o veto e cirurgico: so a dedicacao DAQUELA classe
p = personagem([{"em": i + 1, "slot": "nivel_de_classe", "pega": WIZARD}
                for i in range(20)] + BOOSTS)
outra = next(f for f in p.disponiveis("feat")
             if f["id"] == "wb:feat/cleric-dedication")
checar(outra["atende"],
       "e o Mago 20 puro continua podendo pegar Cleric Dedication",
       f"motivos={outra['motivos']}")

# -- companheiro CONCEDIDO por feat -----------------------------------------
# Spec: specs/2026-07-29-companheiro-concedido.md. Antes disto, pegar
# `Animal Companion` no nivel 1 nao mudava nada na ficha: o ator so entrava por
# `doc["atores"]` escrito a mao, e nao havia slot nem aviso.
print("\ncompanheiro concedido -- o feat abre o slot da especie")

AC_RANGER = "wb:feat/animal-companion-ranger"
esc = niveis((RANGER, 1)) + [{"em": 1, "slot": "class_feat", "pega": AC_RANGER}]
p = personagem(esc)
checar(len(p.concessoes_de_ator) == 1
       and p.concessoes_de_ator[0]["classe"] == RANGER,
       "o feat vira concessao, e a classe sai do NIVEL em que foi pego",
       f"{p.concessoes_de_ator}")
aberto = [s for s in p.slots_abertos() if s["slot"] == "companheiro"]
checar(len(aberto) == 1 and aberto[0]["em"] == 1
       and aberto[0]["kind"] == "animal-companion",
       "concessao sem ator abre slot de companheiro no nivel do feat",
       f"{aberto}")

cands = p.candidatos("companheiro", 1)
checar(len(cands) == 96,
       "candidatos sao as 96 ESPECIES; as 17 sem stat block (Ambusher, Nimble, "
       "Savage...) sao especializacao e nao cabem no slot", f"deu {len(cands)}")

# `opcoes` do concessor ORDENA, nao filtra -- principio zero aplicado a especie
p_rr = personagem(niveis((FIGHTER, 2))
                  + [{"em": 2, "slot": "general_feat", "pega": "wb:feat/rough-rider"}])
c_rr = p_rr.candidatos("companheiro", 2)
checar(c_rr[0]["nome"] == "Wolf" and c_rr[0]["sugerida"] is True
       and len(c_rr) == 96,
       "Rough Rider ('you gain a wolf') poe o Wolf na frente sem sumir com o resto",
       f"primeiro={c_rr[0]['nome']} total={len(c_rr)}")

# escolhida a especie, o slot fecha e a ficha sai igual a do ator escrito a mao
ATOR = [{"tipo": "companheiro", "nome": "Princesa", "concedido_por": AC_RANGER,
         "em": 1, "escolhas": [{"slot": "animal",
                                "pega": "wb:animal-companion/wolf"}]}]
p2 = personagem(esc, atores=ATOR)
checar(not [s for s in p2.slots_abertos() if s["slot"] == "companheiro"],
       "escolhida a especie, o slot fecha")
a = p2.atores[0]
checar(a["especie"] == "Wolf" and a["classe"] == "Ranger" and a["nivel"] == 1,
       "e a ficha do companheiro sai completa, ancorada na classe da concessao",
       f"{a.get('especie')} {a.get('classe')} {a.get('nivel')}")

# regra 17b com a classe CERTA: o cap segue a classe que concedeu, nao a maior
esc_mc = niveis((RANGER, 3), (FIGHTER, 5)) + [
    {"em": 1, "slot": "class_feat", "pega": AC_RANGER}]
p3 = personagem(esc_mc, atores=ATOR)
checar(p3.atores[0]["nivel"] == 5 and p3.atores[0]["nota"] is None,
       "Ranger 3 / Fighter 5: cap = min(3+2, 8) = 5, sem chute",
       f"nivel={p3.atores[0]['nivel']} nota={p3.atores[0]['nota']}")

# compatibilidade: ator escrito a mao, sem `concedido_por`, continua valendo
p4 = personagem(esc_mc, atores=[{k: v for k, v in ATOR[0].items()
                                 if k not in ("concedido_por", "em")}])
checar(p4.atores[0]["nivel"] == 7 and p4.atores[0]["nota"] is not None,
       "sem `concedido_por` o motor segue chutando a maior classe -- e AVISANDO",
       f"nivel={p4.atores[0]['nivel']}")

# feat removido depois deixa o ator orfao: avisa, nao apaga a decisao
p5 = personagem(niveis((FIGHTER, 1)), atores=ATOR)
checar(any("concedido_por" in x for x in p5.avisos),
       "ator cuja origem sumiu da ficha vira aviso, nao silencio",
       f"{p5.avisos}")

# -- dano FIXO, sem dado ----------------------------------------------------
# Blowgun e Dart Umbrella causam 1 ponto, nao 1dX -- e RAW. O extrator exigia
# `dN` no texto do AoN e deixava as duas sem `damage`, entao elas nem apareciam
# na aba de Ataques com o dado inteiro em disco. A representacao OMITE a chave
# `dado` em vez de grava-la como None: os dois motores fazem
# `dano.get("dado", "")`, e a chave presente com None imprimiria "None".
print("\ndano fixo -- arma sem dado de dano")
# STR explicito: com FOR +0 o dano da adaga sairia "1d4" e o teste passaria sem
# provar que o modificador continua entrando
p = personagem(niveis((FIGHTER, 1))
               + [{"em": 1, "slot": "boosts_livres", "pega": ["str", "dex", "con", "wis"]}],
               inventario=[{"item": "wb:weapon/blowgun", "qtd": 1, "equipado": True},
                           {"item": "wb:weapon/dagger", "qtd": 1, "equipado": True}])
ataques = {a["arma"]: a for a in p.visao()["ataques"]}
checar(ataques["Blowgun"]["dano"] == "1",
       "Blowgun sai com dano 1, sem dado e sem 'None' na string",
       f"deu {ataques['Blowgun']['dano']!r}")
checar(ataques["Blowgun"]["tipo_de_dano"] == "piercing",
       "e com o tipo de dano preservado")
checar(ataques["Dagger"]["dano"] == "1d4+1",
       "e a arma com dado normal nao muda", f"deu {ataques['Dagger']['dano']!r}")

# -- proficiencia de arma NOMEADA cai na categoria --------------------------
# Achado comparando com o Pathbuilder (docs/2026-07-29_comparacao-pathbuilder.md):
# 10 dedicacoes exigem treino numa arma especifica (`weapon:aldori-dueling-sword`)
# e ninguem preenche essa chave -- a ficha guarda rank por CATEGORIA. O
# Guerreiro, treinado em advanced desde o nivel 1, aparecia untrained nelas.
print("\nproficiencia de arma nomeada -- cai na categoria da arma")
guerreiro6 = personagem(niveis((FIGHTER, 6)) + BOOSTS)
mago6 = personagem(niveis((WIZARD, 6)) + BOOSTS)
aldori = BASE.opcional("wb:feat/aldori-duelist-dedication")
checar(guerreiro6.proficiencias.get("advanced") == "trained",
       "Guerreiro 6 e treinado em arma avancada (premissa do caso)",
       f"deu {guerreiro6.proficiencias.get('advanced')}")
checar(guerreiro6.avaliar(aldori.get("requires"))[0],
       "e por isso atende Aldori Duelist Dedication, que exige a arma nomeada",
       f"{guerreiro6.avaliar(aldori.get('requires'))[1]}")
checar(not mago6.avaliar(aldori.get("requires"))[0],
       "ja o Mago 6, untrained em avancada, continua fora -- a ponte nao afrouxa")

# -- requisito parcial: emitir o que deu, escrever o que nao deu ------------
# Spec: specs/2026-07-29-requisito-parcial.md. O parser era tudo-ou-nada, entao
# "Trained in Occultism; you have been in a psychic duel" perdia as DUAS coisas
# por causa da segunda -- e o gate de nivel preenchia o vazio, disfarcando a
# perda de "dado pobre".
print("\nrequisito parcial -- o mecanico avalia, o narrativo fica por escrito")
psychic = BASE.opcional("wb:feat/psychic-duelist-dedication")
checar("occultism" in json.dumps(psychic.get("requires")),
       "Psychic Duelist Dedication passou a exigir Occultism no predicado",
       f"{psychic.get('requires')}")
checar(psychic.get("requires_residuo") == ["you have been in a psychic duel"],
       "e a clausula que so a mesa resolve ficou em `requires_residuo`",
       f"{psychic.get('requires_residuo')}")

# o residuo NAO entra na avaliacao: se entrasse, viraria bloqueio silencioso
p_alto = personagem(niveis((WIZARD, 6)) + BOOSTS
                    + [{"em": 1, "slot": "skill_increase", "pega": "wb:skill/occultism"}])
atende, motivos = p_alto.avaliar(psychic.get("requires"))
checar(not any("psychic duel" in m for m in motivos),
       "o motor nunca avalia o residuo -- ele nao vira motivo de reprovacao",
       f"{motivos}")

com_residuo = sum(1 for r in BASE.por_id.values() if r.get("requires_residuo"))
checar(com_residuo > 500,
       f"e a base inteira carrega o residuo em {com_residuo} registros, "
       "visivel em vez de descartado")

# -- spellcasting de arquetipo ---------------------------------------------
# Spec: specs/2026-07-29-spellcasting-de-arquetipo.md. 13 dedicacoes prometiam
# conjuracao na prosa e a ficha nao mostrava nada. O rank vem do FEAT que o
# personagem pegou, nao do nivel dele: a tabela RANK_DEDICACAO descreve a rota
# completa (e e o piso da regra 21), mas quem so tem Basic para no rank 3.
print("\nspellcasting de arquetipo -- a rota que a dedicacao abre")
DED_MAGO = {"em": 2, "slot": "free_archetype", "pega": "wb:feat/wizard-dedication"}
BASIC = {"em": 4, "slot": "free_archetype", "pega": "wb:feat/basic-wizard-spellcasting"}

f8 = personagem(niveis((FIGHTER, 8)) + BOOSTS + [DED_MAGO, BASIC])
arq = [c for c in f8.conjuracao if c.get("de_arquetipo")]
checar(len(arq) == 1, "a dedicacao com Basic Spellcasting cria UMA entrada de conjuracao",
       f"{len(arq)}")
if arq:
    c = arq[0]
    checar(c["tradicao"] == "arcane" and c["tipo"] == "prepared",
           "com a tradicao lida da propria classe citada na prosa",
           f"{c['tradicao']}/{c['tipo']}")
    checar(c["slots"] == {"1": 1, "2": 1, "3": 1},
           "um slot de cada rank ate o teto do degrau Basic (3)", f"{c['slots']}")
    checar(c["elevacao"] == 0 and c["rank_efetivo"] == c["max_rank_do_slot"],
           "e SEM elevacao: pela regra 18 o arquetipo roda RAW puro",
           f"elevacao={c['elevacao']}")
    checar(c["dc"]["dc"] == 10 + f8.nivel + RANK_BONUS["trained"],
           "DC pela regra 3: 10 + nivel de PERSONAGEM + trained", f"{c['dc']}")

so_ded = personagem(niveis((FIGHTER, 8)) + BOOSTS + [DED_MAGO])
arq2 = [c for c in so_ded.conjuracao if c.get("de_arquetipo")]
checar(arq2 and arq2[0]["slots"] == {},
       "a dedicacao SOZINHA nao da slot nenhum -- so os truques",
       f"{arq2[0]['slots'] if arq2 else 'sem entrada'}")

f20 = personagem(niveis((FIGHTER, 20)) + BOOSTS + [DED_MAGO, BASIC])
arq3 = [c for c in f20.conjuracao if c.get("de_arquetipo")]
checar(arq3 and arq3[0]["max_rank_do_slot"] == 3,
       "e no nivel 20, so com Basic, o teto continua 3 -- o rank vem do FEAT",
       f"{arq3[0]['max_rank_do_slot'] if arq3 else '-'}")

# tradicao que depende de outra escolha: avisa em vez de arbitrar
bruxo = personagem(niveis((FIGHTER, 8)) + BOOSTS + [
    {"em": 2, "slot": "free_archetype", "pega": "wb:feat/witch-dedication"},
    {"em": 4, "slot": "free_archetype", "pega": "wb:feat/basic-witch-spellcasting"}])
checar(any("tradicao vem da escolha" in a for a in bruxo.avisos),
       "Witch Dedication sem patron escolhido AVISA em vez de inventar tradicao",
       f"{[a for a in bruxo.avisos if 'tradicao' in a]}")

# -- tradicao por subclasse, rota NATIVA (item 78) --------------------------
# Spec: specs/2026-07-30-tradicao-por-subclasse.md. Ate agora `_conjuracao()`
# copiava `spellcasting.tradition` cru, e nas tres classes sem tradicao fixa
# isso e uma FRASE EM PORTUGUES -- o campo que filtra quais magias o personagem
# pode aprender saia como prosa. O resolvedor ja existia; faltava liga-lo.
SORC, WITCH = "wb:class/sorcerer", "wb:class/witch"

feiticeiro_genie = personagem(niveis((SORC, 5)) + BOOSTS + [
    {"em": 1, "slot": "subclasse", "pega": "wb:class-feature/bloodline-genie"}])
nativa = [c for c in feiticeiro_genie.conjuracao if not c.get("de_arquetipo")]
checar(nativa and nativa[0]["tradicao"] == "arcane",
       "Feiticeiro de bloodline Genie conjura ARCANE, e nao a frase em prosa",
       f"{nativa[0]['tradicao'] if nativa else 'sem conjuracao'}")

bruxa_baba = personagem(niveis((WITCH, 5)) + BOOSTS + [
    {"em": 1, "slot": "subclasse", "pega": "wb:class-feature/baba-yaga"}])
n_bruxa = [c for c in bruxa_baba.conjuracao if not c.get("de_arquetipo")]
checar(n_bruxa and n_bruxa[0]["tradicao"] == "occult",
       "Bruxa de patron Baba Yaga conjura OCCULT",
       f"{n_bruxa[0]['tradicao'] if n_bruxa else 'sem conjuracao'}")

# o teste que so passa com o filtro por CLASSE: sem ele o resolvedor devolve a
# primeira escolha de subclasse que tiver tradicao, e as duas linhas de
# conjuracao saem iguais.
multi = personagem(niveis((SORC, 5), (WITCH, 3)) + BOOSTS + [
    {"em": 1, "slot": "subclasse", "pega": "wb:class-feature/bloodline-genie"},
    {"em": 6, "slot": "subclasse", "pega": "wb:class-feature/baba-yaga"}])
por_classe = {c["classe"]: c["tradicao"]
              for c in multi.conjuracao if not c.get("de_arquetipo")}
checar(por_classe.get("Sorcerer") == "arcane" and por_classe.get("Witch") == "occult",
       "Feiticeiro 5 / Bruxa 3: cada linha com a SUA tradicao, nao a primeira",
       f"{por_classe}")

# Draconic no remaster depende de uma SEGUNDA escolha (o draconic-exemplar), que
# nao esta ligado como eixo em classe nenhuma. Principio zero: avisa, nao chuta.
# Casar por NOME daria `arcane`, que e a tradicao da versao LEGADA -- numero
# errado com cara de certo.
feiticeiro_draconic = personagem(niveis((SORC, 5)) + BOOSTS + [
    {"em": 1, "slot": "subclasse", "pega": "wb:class-feature/bloodline-draconic"}])
n_drac = [c for c in feiticeiro_draconic.conjuracao if not c.get("de_arquetipo")]
checar(n_drac and n_drac[0]["tradicao"] is None,
       "Draconic no remaster nao resolve -- devolve None em vez de chutar arcane",
       f"{n_drac[0]['tradicao'] if n_drac else 'sem conjuracao'}")
checar(any("tradicao vem da escolha" in a for a in feiticeiro_draconic.avisos),
       "e o motivo aparece nos avisos",
       f"{[a for a in feiticeiro_draconic.avisos if 'tradicao' in a]}")

oraculo = personagem(niveis(("wb:class/oracle", 5)) + BOOSTS)
n_ora = [c for c in oraculo.conjuracao if not c.get("de_arquetipo")]
checar(n_ora and n_ora[0]["tradicao"] == "divine",
       "Oraculo continua divine sem consultar escolha nenhuma",
       f"{n_ora[0]['tradicao'] if n_ora else 'sem conjuracao'}")

checar(feiticeiro_genie.avaliar({"spellcasting_tradition": "arcane"})[0]
       and not feiticeiro_genie.avaliar({"spellcasting_tradition": "divine"})[0],
       "e com a tradicao resolvida o predicado para de atender as quatro")

# -- termos novos de predicado ---------------------------------------------
# Spec: specs/2026-07-29-termos-de-predicado.md. Sao os padroes do residuo que a
# base JA respondia e nao tinham termo: sentido (81 registros com `grants.sense`
# que ninguem lia), focus pool (o motor ja calculava) e companheiro (a concessao
# derivada hoje).
print("\ntermos novos -- sentido, focus pool, companheiro")
ELFO = [{"em": "criacao", "slot": "ancestralidade", "pega": "wb:ancestry/elf"}]
ANAO = [{"em": "criacao", "slot": "ancestralidade", "pega": "wb:ancestry/dwarf"}]

checar(personagem(ELFO + niveis((FIGHTER, 1))).avaliar({"sense": "low-light vision"})[0],
       "Elfo atende `low-light vision` -- e ele declara so no campo `senses` do topo")
checar(personagem(ANAO + niveis((FIGHTER, 1))).avaliar({"sense": "darkvision"})[0],
       "Anao atende `darkvision`")
checar(not personagem(niveis((FIGHTER, 1))).avaliar({"sense": "darkvision"})[0],
       "e quem nao tem sentido nenhum nao atende -- o termo nao afrouxa")

bardo = personagem(niveis(("wb:class/bard", 1)))
checar(bardo.avaliar({"focus_pool": {">=": 1}})[0],
       "Bardo 1 atende `focus pool` (composition cantrip)", f"{bardo.focus_pool}")
checar(not personagem(niveis((FIGHTER, 1))).avaliar({"focus_pool": {">=": 1}})[0],
       "Guerreiro 1 nao atende")

com_bicho = personagem(niveis((RANGER, 1))
                       + [{"em": 1, "slot": "class_feat",
                           "pega": "wb:feat/animal-companion-ranger"}])
checar(com_bicho.avaliar({"has_actor": "companheiro"})[0],
       "quem pegou Animal Companion atende `has_actor` ANTES de escolher a especie")
checar(not personagem(niveis((FIGHTER, 1))).avaliar({"has_actor": "companheiro"})[0],
       "e quem nao pegou, nao")

# alinhamento NAO vira termo: o conceito nao existe no Remaster
checar(personagem(niveis((FIGHTER, 1))).avaliar({"alignment": "evil"})[0],
       "termo inexistente (`alignment`) nao reprova -- o motor nao arbitra o "
       "que nao sabe, e a clausula fica visivel em `requires_residuo`")

# ---------------------------------------------------------------------------
# `grant_item` apontava para o Foundry e o motor nao aplicava NENHUM -- 619
# concessoes inertes. O pipeline passou a resolver o nome do uuid para id `wb:`.
# Spec: specs/2026-07-29-grant-item-por-nome.md
print("\ngrant_item resolvido e aplicado")

bh = personagem(niveis((FIGHTER, 4)) + [
    {"em": 2, "slot": "free_archetype", "pega": "wb:feat/battle-harbinger-dedication"}])
concedidos = {c["nome"] for c in bh.concedidos}
checar("Toughness" in concedidos,
       "Battle Harbinger Dedication concede Toughness por grant_item",
       f"{sorted(concedidos)}")
sem_bh = personagem(niveis((FIGHTER, 4)))
checar(bh.hp > sem_bh.hp,
       "e o HP sobe por causa dela -- o efeito chega na ficha",
       f"com={bh.hp} sem={sem_bh.hp}")

# ---------------------------------------------------------------------------
# ChoiceSet: `Marshal Dedication` da UMA entre Diplomacy e Intimidation, e a
# base concedia as QUATRO opcoes (as duas pericias, trained E expert).
# Spec: specs/2026-07-29-choiceset.md
print("\nescolha embutida em grants (ChoiceSet)")

def _marshal(escolha=None):
    esc = niveis((FIGHTER, 2)) + [
        {"em": 2, "slot": "free_archetype", "pega": "wb:feat/marshal-dedication"}]
    if escolha:
        esc.append({"em": 2, "slot": "escolha_de_grant", "pega": escolha})
    return personagem(esc)

sem = _marshal()
checar(sem.proficiencias.get("intimidation") is None,
       "sem escolher, a dedicacao NAO da Intimidation de graca",
       f"{sem.proficiencias.get('intimidation')}")
checar(any("falta escolher `marshal-skill`" in a for a in sem.avisos),
       "e a ficha avisa que falta escolher", f"{sem.avisos[-2:]}")
checar(any(s["slot"] == "escolha_de_grant" for s in sem.slots_abertos()),
       "slots_abertos oferece a escolha -- sem isso a tela nao tem picker")

com_int = _marshal("marshal-skill:imtimidation-trained")
checar(com_int.proficiencias.get("intimidation") == "trained",
       "escolhendo Intimidation, ela vem trained",
       f"{com_int.proficiencias.get('intimidation')}")

com_dip = _marshal("marshal-skill:diplomacy-expert")
checar(com_dip.proficiencias.get("diplomacy") == "expert",
       "escolhendo Diplomacy expert, ela sobe a expert",
       f"{com_dip.proficiencias.get('diplomacy')}")
checar(com_dip.proficiencias.get("intimidation") is None,
       "e a opcao NAO escolhida continua fora")

# ---------------------------------------------------------------------------
# `_termo_has` olhava o documento INTEIRO, sem perguntar QUANDO cada coisa foi
# pega -- entao a ordem ilegal passava limpa. A ficha e historico, nao foto.
# Spec: specs/2026-07-29-recorte-temporal-do-has.md
print("\nrecorte temporal do `has`")

def _duelista(em_parry, em_dance):
    return personagem(niveis((FIGHTER, 12)) + [
        {"em": em_parry, "slot": "class_feat", "pega": "wb:feat/dueling-parry-fighter"},
        {"em": em_dance, "slot": "class_feat", "pega": "wb:feat/dueling-dance-fighter"}])

legal = _duelista(2, 12)
checar(not legal.fora_do_requisito,
       "Dueling Parry no 2 e Dance no 12 -- ordem legal, ficha limpa",
       f"{legal.fora_do_requisito}")

ilegal = _duelista(12, 2)
checar(any("Dueling Parry" in f["motivo"] for f in ilegal.fora_do_requisito),
       "Parry no 12 e Dance no 2 -- ordem ILEGAL, agora acusada",
       f"{ilegal.fora_do_requisito}")

# o recorte nao pode inventar falso positivo fora de contexto
checar(personagem(niveis((FIGHTER, 12)) + [
    {"em": 2, "slot": "class_feat", "pega": "wb:feat/dueling-parry-fighter"}])
    .avaliar({"has": "wb:feat/dueling-parry-fighter"})[0],
    "`avaliar()` chamado de fora, sem contexto, responde como antes")

# ---------------------------------------------------------------------------
# Pericias livres: o motor CONTAVA o orcamento (`pericias_livres: 3`) e nao
# tinha onde receber a escolha -- nenhum `_escolhas("pericias_livres")` existia.
# Achado ao alinhar a bancada de comparacao com o Pathbuilder.
# Spec: specs/2026-07-29-pericias-livres.md
print("\npericias livres -- o orcamento que ninguem gastava")

PERICIAS_G = ["acrobatics", "athletics", "stealth"]
guerreiro_com = personagem(niveis((FIGHTER, 2)) + [
    {"em": "criacao", "slot": "pericias_livres", "pega": PERICIAS_G}])
checar(all(guerreiro_com.proficiencias.get(p) == "trained" for p in PERICIAS_G),
       "Guerreiro 2 que declara 3 pericias sai com as 3 trained",
       f"{[guerreiro_com.proficiencias.get(p) for p in PERICIAS_G]}")

guerreiro_sem = personagem(niveis((FIGHTER, 2)))
checar(any("pericias livres" in a for a in guerreiro_sem.avisos),
       "sem declarar nada, a higiene cobra as 3 que faltam",
       f"{guerreiro_sem.avisos}")

guerreiro_demais = personagem(niveis((FIGHTER, 2)) + [
    {"em": "criacao", "slot": "pericias_livres",
     "pega": PERICIAS_G + ["thievery"]}])
checar(any("pericias livres" in a and "sobra" in a.lower()
           for a in guerreiro_demais.avisos),
       "declarar 4 num orcamento de 3 avisa que sobrou 1",
       f"{guerreiro_demais.avisos}")

# regra 9: Athletics ja e automatica do Barbaro -- escolher de novo desperdica,
# mas nao reprova nem rebaixa (principio zero vale para a escolha do jogador)
barbaro = personagem(niveis(("wb:class/barbarian", 1)) + [
    {"em": "criacao", "slot": "pericias_livres", "pega": ["athletics"]}])
checar(barbaro.proficiencias.get("athletics") == "trained",
       "escolher pericia que a classe ja deu nao rebaixa")
checar(any("desperdic" in a.lower() for a in barbaro.avisos),
       "e avisa o desperdicio", f"{barbaro.avisos}")

abertos = {s["slot"]: s for s in guerreiro_sem.slots_abertos()}
checar("pericias_livres" in abertos,
       "slots_abertos lista `pericias_livres` -- sem isso a tela nao tem picker")
checar(abertos.get("pericias_livres", {}).get("escolhe") == 3,
       "e diz que faltam 3",
       f"{abertos.get('pericias_livres', {}).get('escolhe')}")
checar("pericias_livres" not in {s["slot"] for s in guerreiro_com.slots_abertos()},
       "e para de listar quando o orcamento foi cumprido")

# ---------------------------------------------------------------------------
# `spellcasting_tradition` -- 99 clausulas em 27 arquetipos que nenhum dos dois
# motores sabia ouvir. Sem o termo, o `any` de cathartic-mage passava a vacuo e
# um Guerreiro 6 recebia seis dedicacoes de conjuracao.
# Spec: specs/2026-07-29-termo-spellcasting-tradition.md
print("\ntermo `spellcasting_tradition`")

clerigo2 = personagem(niveis((CLERIC, 2)))
checar(clerigo2.avaliar({"spellcasting_tradition": "divine"})[0],
       "Clerigo 2 conjura divine")
checar(not clerigo2.avaliar({"spellcasting_tradition": "arcane"})[0],
       "e NAO conjura arcane")

guerreiro6 = personagem(niveis((FIGHTER, 6)))
checar(not any(guerreiro6.avaliar({"spellcasting_tradition": t})[0]
               for t in ("arcane", "divine", "occult", "primal")),
       "Guerreiro 6 nao atende NENHUMA tradicao -- e o ganho inteiro da spec")

# conjuracao de arquetipo conta: o personagem conjura de verdade
fa_clerigo = personagem(niveis((FIGHTER, 6)) + [
    {"em": 2, "slot": "free_archetype", "pega": "wb:feat/cleric-dedication"},
    {"em": 4, "slot": "free_archetype", "pega": "wb:feat/basic-cleric-spellcasting"}])
checar(fa_clerigo.avaliar({"spellcasting_tradition": "divine"})[0],
       "Guerreiro com Cleric Dedication + Basic Spellcasting atende divine")

# principio zero: Feiticeiro guarda PROSA no lugar da tradicao (item 78), entao
# o motor nao sabe qual e -- e nao reprova sobre o que nao sabe
feiticeiro = personagem(niveis(("wb:class/sorcerer", 5)))
checar(all(feiticeiro.avaliar({"spellcasting_tradition": t})[0]
           for t in ("arcane", "divine", "occult", "primal")),
       "Feiticeiro atende as quatro -- tradicao em prosa nao reprova (item 78)")

# a prova que a comparacao com o Pathbuilder apontou. Pelo principio zero o feat
# CONTINUA na lista -- o que muda e que agora vem MARCADO, com o motivo.
cathartic = next(c for c in guerreiro6.candidatos("class_feat", em=6)
                 if c["id"] == "wb:feat/cathartic-mage-dedication")
checar(not cathartic["atende"],
       "Cathartic Mage Dedication vem MARCADA para um Guerreiro 6")
checar(any("nao conjura" in m for m in cathartic["motivos"]),
       "e o motivo diz que ele nao conjura, nao so que falta CHA")

print("\n" + "=" * 58)
if FALHAS:
    print(f"  {len(FALHAS)} FALHA(S):")
    for f in FALHAS:
        print(f"    - {f}")
    sys.exit(1)
print("  todos os testes passaram")
sys.exit(0)
