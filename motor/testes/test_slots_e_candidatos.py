#!/usr/bin/env python3
"""A terceira pergunta do construtor: o que falta escolher, e o que cabe aqui.

O motor sabia responder "o que eu tenho" (`visao`) e "o que esta errado"
(`fora_do_requisito`, `avisos`). Faltava a pergunta que a TELA faz:

    "o que eu posso escolher agora, neste slot?"

`disponiveis(kind="feat")` devolve os 6.273 feats da base -- inutil para um
picker. `candidatos(slot, em)` recorta pelo que o slot aceita.

A distincao que estes testes travam:

  elegibilidade de SLOT  -> FILTRA   (o slot gratuito so aceita arquetipo)
  requisito (`requires`) -> ORDENA   (principio zero: sugere, nunca bloqueia)

Um feat sem trait `archetype` nao e candidato ao slot de Free Archetype -- isso
nao e bloquear escolha, e a definicao do slot. Ja um feat de arquetipo cujo
requisito o personagem nao atende APARECE na lista, marcado com `atende: False`.

Spec: specs/2026-07-27-slots-e-candidatos.md

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
FICHA = "guerreiro4-fa-dedicacao-com-grants.json"


def carregar(nome=FICHA, mutacao=None):
    with open(os.path.join(EXEMPLOS, nome), encoding="utf-8") as fh:
        doc = json.load(fh)
    if mutacao:
        mutacao(doc)
    return wb_motor.Personagem(doc, BASE)


def ids(lista):
    return {c["id"] for c in lista}


class TestCandidatosRecortamPeloSlot(unittest.TestCase):

    def setUp(self):
        self.p = carregar()

    def test_slot_gratuito_so_traz_feat_de_arquetipo(self):
        c = self.p.candidatos("free_archetype", em=2)
        self.assertTrue(c, "lista vazia")
        for item in c:
            traits = BASE.get(item["id"]).get("traits") or []
            self.assertIn("archetype", traits, item["id"])

    def test_class_feat_puro_nao_aparece_no_slot_gratuito(self):
        """`Reactive Shield` tem traits fighter/guardian, nao archetype."""
        self.assertNotIn("wb:feat/reactive-shield",
                         ids(self.p.candidatos("free_archetype", em=2)))

    def test_a_lista_encolhe_em_ordem_de_grandeza(self):
        """E o ponto todo: um picker nao pode receber a base inteira."""
        todos = self.p.disponiveis("feat")
        do_slot = self.p.candidatos("free_archetype", em=2)
        self.assertLess(len(do_slot) * 2, len(todos),
                        f"{len(do_slot)} de {len(todos)} -- recorte fraco demais")

    def test_skill_feat_pede_trait_skill(self):
        for item in self.p.candidatos("skill_feat", em=2)[:50]:
            self.assertIn("skill", BASE.get(item["id"]).get("traits") or [])

    def test_class_feat_traz_a_classe_do_personagem(self):
        c = ids(self.p.candidatos("class_feat", em=4))
        self.assertIn("wb:feat/reactive-shield", c)      # fighter
        self.assertNotIn("wb:feat/archer-dedication", c)  # arquetipo puro

    def test_slot_de_atributo_traz_os_seis(self):
        c = self.p.candidatos("boosts_livres")
        self.assertEqual(ids(c), set(wb_motor.ATRIBUTOS))


class TestRequisitoOrdenaNuncaFiltra(unittest.TestCase):
    """Principio zero aplicado a lista: o que nao atende aparece, marcado."""

    def setUp(self):
        self.p = carregar()

    def test_feat_de_nivel_alto_aparece_marcado(self):
        c = self.p.candidatos("free_archetype", em=2)
        altos = [x for x in c if (x["level"] or 0) > 2]
        self.assertTrue(altos, "nenhum feat de nivel alto na lista")
        for x in altos:
            self.assertFalse(x["atende"])
            self.assertTrue(x["motivos"])

    def test_quem_atende_vem_primeiro(self):
        c = self.p.candidatos("free_archetype", em=4)
        atendem = [i for i, x in enumerate(c) if x["atende"]]
        nao = [i for i, x in enumerate(c) if not x["atende"]]
        if atendem and nao:
            self.assertLess(max(atendem), min(nao))

    def test_regra_23_entra_como_motivo_nao_como_filtro(self):
        """A dedicacao da propria classe CONTINUA na lista, sinalizada."""
        c = {x["id"]: x for x in self.p.candidatos("free_archetype", em=2)}
        alvo = c.get("wb:feat/fighter-dedication")
        self.assertIsNotNone(alvo, "sumiu da lista -- deveria estar marcada")
        self.assertFalse(alvo["atende"])
        self.assertTrue([m for m in alvo["motivos"] if "regra 23" in m], alvo)

    def test_o_que_ja_foi_pego_vem_marcado(self):
        c = {x["id"]: x for x in self.p.candidatos("free_archetype", em=2)}
        self.assertTrue(c["wb:feat/shieldmarshal-dedication"]["ja_pego"])


class TestSlotsAbertos(unittest.TestCase):

    def test_so_fica_aberto_o_que_nao_foi_gasto(self):
        """Esta ficha usa o slot gratuito do nivel 2 e deixa o do 4 vazio --
        entao a pendencia tem de ser exatamente uma, no nivel 4."""
        p = carregar()
        pend = [s for s in p.slots_abertos() if s["slot"] == "free_archetype"]
        self.assertEqual([s["em"] for s in pend], [4])
        # e os trilhos que a ficha preencheu nao aparecem
        self.assertEqual([s for s in p.slots_abertos()
                          if s["slot"] in ("class_feat", "ancestry_feat")], [])

    def test_remover_uma_escolha_abre_o_slot(self):
        p = carregar(mutacao=lambda d: d.__setitem__(
            "escolhas", [e for e in d["escolhas"]
                         if not (e.get("slot") == "free_archetype")]))
        abertos = [s for s in p.slots_abertos() if s["slot"] == "free_archetype"]
        self.assertEqual([s["em"] for s in abertos], [2, 4])

    def test_subclasse_por_escolher_aparece(self):
        """De proposito numa ficha de LADINO: depois do conserto do item 69, o
        Guerreiro nao tem eixo de subclasse nenhum -- `Warrior of Legend` voltou
        a ser progressao, que e o que sempre foi. Ladino tem `racket`, que e
        escolha de verdade."""
        p = carregar("ladino4-aumentos-de-pericia.json", lambda d: d.__setitem__(
            "escolhas", [e for e in d["escolhas"] if e.get("slot") != "subclasse"]))
        abertos = [s for s in p.slots_abertos() if s["slot"] == "subclasse"]
        self.assertTrue(abertos, "racket do Ladino deveria estar aberto")
        self.assertEqual(abertos[0]["kind"], "racket")

    def test_guerreiro_nao_pede_subclasse_nenhuma(self):
        """Contraprova do item 69: o Guerreiro nao escolhe subclasse no PF2e, e
        depois do conserto ele nao pede mais."""
        p = carregar()
        self.assertEqual(BASE.get("wb:class/fighter").get("subclasses") or [], [])
        self.assertEqual([s for s in p.slots_abertos() if s["slot"] == "subclasse"], [])

    def test_aumento_de_pericia_por_gastar_aparece(self):
        p = carregar("ladino4-aumentos-de-pericia.json", lambda d: d.__setitem__(
            "escolhas", [e for e in d["escolhas"] if e.get("slot") != "skill_increase"]))
        abertos = [s for s in p.slots_abertos() if s["slot"] == "skill_increase"]
        self.assertEqual([s["em"] for s in abertos], [2, 3, 4])


class TestOrcamentoDeBoost(unittest.TestCase):
    """Item 74: ficha sem boost declarado saia com tudo 10 e ZERO avisos."""

    def test_ficha_sem_boost_declarado_e_sinalizada(self):
        p = carregar(mutacao=lambda d: d.__setitem__(
            "escolhas", [e for e in d["escolhas"] if e.get("slot") != "boosts_livres"]))
        self.assertEqual(p.atributos, {a: 10 for a in wb_motor.ATRIBUTOS})
        self.assertTrue([a for a in p.avisos if "boosts de atributo" in a], p.avisos)

    def test_o_direito_e_maior_que_zero_e_bate_com_as_fontes(self):
        p = carregar()
        self.assertGreater(p.boosts_direito, 0)
        self.assertEqual(p.boosts_direito,
                         sum(b["quantidade"] for b in p.boosts_pendentes))

    def test_pendencia_aparece_em_slots_abertos(self):
        p = carregar(mutacao=lambda d: d.__setitem__(
            "escolhas", [e for e in d["escolhas"] if e.get("slot") != "boosts_livres"]))
        b = [s for s in p.slots_abertos() if s["slot"] == "boosts_livres"]
        self.assertEqual(len(b), 1)
        self.assertEqual(b[0]["escolhe"], p.boosts_direito)

    def test_boost_a_mais_tambem_e_sinalizado(self):
        """Quanto declarar para estourar sai do proprio direito -- numero fixo
        aqui viraria teste obsoleto a cada ajuste da regra, que foi o que
        aconteceu quando os 4 boosts da criacao entraram."""
        base = carregar()
        excesso = base.boosts_direito - base.boosts_declarados + 1
        p = carregar(mutacao=lambda d: d["escolhas"].append(
            {"em": 1, "slot": "boosts_livres", "pega": ["str"] * excesso}))
        self.assertGreater(p.boosts_declarados, p.boosts_direito)
        self.assertTrue([a for a in p.avisos if "a mais" in a], p.avisos)

    def test_humano_tem_dois_livres_de_ancestria(self):
        """Prova que o direito sai do DADO, nao de tabela escrita no motor."""
        p = carregar()
        da_ancestria = [b for b in p.boosts_pendentes
                        if b.get("origem_id") == "wb:ancestry/human"
                        or "Human" in str(b.get("origem"))]
        self.assertEqual(sum(b["quantidade"] for b in da_ancestria), 2)

    def test_niveis_de_boost_entram_a_partir_do_5(self):
        p4 = carregar()
        self.assertEqual([b for b in p4.boosts_pendentes if b["em"] == 5], [])
        p10 = carregar("campeao6-alquimista4-fa-nivel10.json")
        de_nivel = [b for b in p10.boosts_pendentes if isinstance(b["em"], int)
                    and b["em"] in (5, 10)]
        self.assertEqual(sum(b["quantidade"] for b in de_nivel), 8)


if __name__ == "__main__":
    unittest.main()
