#!/usr/bin/env python3
"""Testes do aumento de pericia -- `skill_increase` (item 67).

O schema declarava `skill_increase` e o motor nao tinha uma linha a respeito:
toda ficha saia com o rank de origem congelado, e a comparacao com os iconics
media essa lacuna em vez de medir o motor.

O que estes testes travam:

  1  a cadencia vem do DADO da classe, nunca de tabela escrita no motor
  2  a regra 15 vale aqui tambem: cadencia extra conta a partir da entrada
  3  o aumento sobe UM degrau, e serve para entrar numa pericia (untrained ->
     trained), que e RAW
  4  o teto por nivel de personagem (master so no 7, legendary so no 15)
  5  higiene: aumento a mais, ou em nivel sem aumento, e SINALIZADO -- e nunca
     recusado (principio zero)

Rodar: python3 -m unittest discover -s motor/testes -t .
"""
import copy
import importlib.util
import json
import os
import unittest

AQUI = os.path.dirname(os.path.abspath(__file__))
MOTOR = os.path.dirname(AQUI)
EXEMPLOS = os.path.join(MOTOR, "exemplos")

_spec = importlib.util.spec_from_file_location("wb_motor", os.path.join(MOTOR, "motor.py"))
wb_motor = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(wb_motor)

BASE = wb_motor.Base()

LADINO = "ladino4-aumentos-de-pericia.json"
GUERREIRO = "guerreiro4-fa-dedicacao-com-grants.json"


def carregar(nome: str, mutacao=None) -> "wb_motor.Personagem":
    with open(os.path.join(EXEMPLOS, nome), encoding="utf-8") as fh:
        doc = json.load(fh)
    if mutacao:
        mutacao(doc)
    return wb_motor.Personagem(doc, BASE)


def avisos_de_aumento(p) -> list[str]:
    return [a for a in p.avisos if "skill_increase" in a]


class TestCadenciaVemDoDado(unittest.TestCase):
    """Ponto 1 e 2: a lista de niveis sai de `grants`, e respeita a regra 15."""

    def test_o_dado_sustenta_a_cadencia(self):
        """Prova de que nao ha tabela escondida no motor: as duas cadencias
        estao na base, e sao diferentes entre si."""
        def levels(cid):
            return [g["skill_increase"]["levels"]
                    for g in BASE.get(cid).get("grants") or []
                    if isinstance(g, dict) and "skill_increase" in g]
        self.assertEqual(levels("wb:class/fighter"), [[3, 5, 7, 9, 11, 13, 15, 17, 19]])
        self.assertEqual(levels("wb:class/rogue"), [list(range(2, 21))])

    def test_ladino_tem_aumento_todo_nivel(self):
        self.assertEqual(carregar(LADINO).aumentos_de_pericia, [2, 3, 4])

    def test_guerreiro_no_mesmo_nivel_tem_so_um(self):
        """Mesmo nivel 4, cadencia diferente -- e a diferenca vem so do dado."""
        self.assertEqual(carregar(GUERREIRO).aumentos_de_pericia, [3])

    def test_regra_15_a_cadencia_extra_conta_da_entrada(self):
        """Guerreiro 1-2 que vira Ladino no 3: o aumento todo-nivel do Ladino
        so vale do 3 pra frente. O 2 nao entra retroativamente."""
        def virar_ladino(d):
            for e in d["escolhas"]:
                if e.get("slot") == "nivel_de_classe" and e["em"] in (3, 4):
                    e["pega"] = "wb:class/rogue"
        p = carregar(GUERREIRO, virar_ladino)
        self.assertEqual(p.nivel, 4)
        self.assertEqual(p.aumentos_de_pericia, [3, 4])


class TestAplicacao(unittest.TestCase):
    """Ponto 3: sobe um degrau, e tambem serve para ENTRAR na pericia."""

    def setUp(self):
        self.p = carregar(LADINO)

    def test_sobe_um_degrau(self):
        de_para = {d["pericia"]: (d["de"], d["para"]) for d in self.p.aumentos_detalhe}
        self.assertEqual(de_para["stealth"], ("trained", "expert"))
        self.assertEqual(de_para["thievery"], ("trained", "expert"))

    def test_untrained_vira_trained(self):
        """RAW: o aumento pode ser gasto para ficar treinado numa pericia nova."""
        self.assertEqual(dict((d["pericia"], d["para"])
                              for d in self.p.aumentos_detalhe)["athletics"], "trained")
        self.assertEqual(self.p.proficiencias["athletics"], "trained")

    def test_o_rank_final_reflete_o_aumento(self):
        self.assertEqual(self.p.proficiencias["stealth"], "expert")
        self.assertIn("aumento de pericia (nivel 2)",
                      self.p.origem_proficiencia["stealth"])

    def test_sem_aumento_o_rank_fica_no_de_origem(self):
        """O par 'com e sem', para provar que a mudanca veio daqui."""
        sem = carregar(LADINO, lambda d: d.__setitem__(
            "escolhas", [e for e in d["escolhas"] if e.get("slot") != "skill_increase"]))
        self.assertEqual(sem.proficiencias["stealth"], "trained")
        self.assertIsNone(sem.proficiencias.get("athletics"))
        self.assertEqual(sem.aumentos_detalhe, [])
        # a cadencia continua existindo: o que mudou foi so o gasto
        self.assertEqual(sem.aumentos_de_pericia, [2, 3, 4])

    def test_a_ficha_de_referencia_esta_limpa(self):
        """Se a ficha tivesse outro defeito, os testes acima poderiam passar
        pelo motivo errado."""
        self.assertEqual(self.p.fora_do_requisito, [])
        self.assertEqual(avisos_de_aumento(self.p), [])


class TestTetoPorNivel(unittest.TestCase):
    """Ponto 4: master so a partir do 7, legendary so a partir do 15."""

    def test_nivel_4_nao_passa_de_expert(self):
        def dobrar(d):
            # dois aumentos na MESMA pericia: trained -> expert -> master
            for e in d["escolhas"]:
                if e.get("slot") == "skill_increase":
                    e["pega"] = "stealth"
        p = carregar(LADINO, dobrar)
        self.assertEqual(p.proficiencias["stealth"], "expert")
        self.assertTrue([a for a in avisos_de_aumento(p) if "teto" in a],
                        avisos_de_aumento(p))

    def test_no_nivel_7_o_teto_sobe_para_master(self):
        def ate_sete(d):
            for n in (5, 6, 7):
                d["escolhas"].append({"em": n, "slot": "nivel_de_classe",
                                      "pega": "wb:class/rogue"})
            for e in d["escolhas"]:
                if e.get("slot") == "skill_increase":
                    e["pega"] = "stealth"
        p = carregar(LADINO, ate_sete)
        self.assertEqual(p.nivel, 7)
        self.assertEqual(p.proficiencias["stealth"], "master")


class TestHigiene(unittest.TestCase):
    """Ponto 5: sinaliza, nunca recusa."""

    def test_aumento_a_mais_e_sinalizado(self):
        p = carregar(LADINO, lambda d: d["escolhas"].append(
            {"em": 4, "slot": "skill_increase", "pega": "medicine"}))
        self.assertTrue([a for a in avisos_de_aumento(p) if "disponivel" in a],
                        avisos_de_aumento(p))

    def test_aumento_em_nivel_sem_aumento_e_sinalizado(self):
        p = carregar(GUERREIRO, lambda d: d["escolhas"].append(
            {"em": 2, "slot": "skill_increase", "pega": "medicine"}))
        self.assertEqual(p.aumentos_de_pericia, [3])
        self.assertTrue([a for a in avisos_de_aumento(p) if "nivel 2" in a],
                        avisos_de_aumento(p))

    def test_sinaliza_mas_aplica(self):
        """Principio zero: o aviso nao apaga a escolha do jogador."""
        p = carregar(GUERREIRO, lambda d: d["escolhas"].append(
            {"em": 2, "slot": "skill_increase", "pega": "medicine"}))
        self.assertEqual(p.proficiencias["medicine"], "trained")


if __name__ == "__main__":
    unittest.main()
