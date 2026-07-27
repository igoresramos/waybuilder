#!/usr/bin/env python3
"""
Testes do motor: cada um trava UMA regra da spec de multiclasse.

Nao sao testes de "roda sem estourar" -- cada assercao existe porque a regra
correspondente pode ser quebrada por uma mudanca inocente no pipeline, e a
diferenca entre a houserule e o PF2e oficial e justamente onde os dois numeros
(nivel de classe x nivel de personagem) divergem.

Uso: python3 teste_motor.py
"""
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
checar(c and c["rank_de_invocacao"] == 3,
       "mas invocacao para em min(ceil(2/2)+2, 6) = 3 (regra 17b)",
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

print("\n" + "=" * 58)
if FALHAS:
    print(f"  {len(FALHAS)} FALHA(S):")
    for f in FALHAS:
        print(f"    - {f}")
    sys.exit(1)
print("  todos os testes passaram")
sys.exit(0)
