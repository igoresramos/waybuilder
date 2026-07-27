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

print("\n" + "=" * 58)
if FALHAS:
    print(f"  {len(FALHAS)} FALHA(S):")
    for f in FALHAS:
        print(f"    - {f}")
    sys.exit(1)
print("  todos os testes passaram")
sys.exit(0)
