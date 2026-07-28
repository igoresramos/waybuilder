#!/usr/bin/env python3
"""A cadeia de concessao: o que ela aplica, de onde ela parte, e o que ela NAO
pode satisfazer.

Todo caso aqui nasceu de um defeito real achado por review adversarial em
2026-07-27, depois de o motor passar a aplicar `grant_feat` (item 62). Cada
classe abaixo trava um deles.

O mais sutil e o requisito circular: `acrobat-dedication` EXIGE acrobatics
trained e CONCEDE acrobatics. Quando o motor passou a aplicar o que o feat
concede, o feat passou a satisfazer o proprio requisito, e a ficha saia limpa
onde antes sinalizava -- 25 termos ficaram auto-satisfeitos entre os 6.273
feats com `requires`. O conserto e avaliar o `requires` de um feat contra o
estado SEM o efeito dele proprio, o que exige saber a RAIZ de cada concessao.

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
FICHA = os.path.join(EXEMPLOS, "guerreiro4-fa-dedicacao-com-grants.json")

# slots que descrevem o personagem sem nenhum feat escolhido -- a base neutra
# para medir o que uma dedicacao entrega sem contaminacao. Aprendido na marra:
# a primeira medicao usou a ficha inteira, que ja tinha `additional-lore` e
# `double-slice`, e 30 dedicacoes apareceram falsamente como mudas porque
# `_ja_tenho` bloqueava justo o que se queria medir.
SEM_FEATS = ("ancestralidade", "heranca", "background", "nivel_de_classe",
             "subclasse", "boosts_livres")


def doc_base() -> dict:
    with open(FICHA, encoding="utf-8") as fh:
        return json.load(fh)


def neutro(dedicacao: str | None = None) -> dict:
    d = doc_base()
    d["escolhas"] = [e for e in d["escolhas"] if e.get("slot") in SEM_FEATS]
    if dedicacao:
        d["escolhas"].append({"em": 2, "slot": "free_archetype", "pega": dedicacao})
    return d


def motivos(p) -> list[str]:
    return [f"{f['feat']}: {f['motivo']}" for f in p.fora_do_requisito]


class TestRequisitoCircular(unittest.TestCase):
    """Um feat nao satisfaz o proprio requisito."""

    def test_o_dado_sustenta_o_caso(self):
        """Se a dedicacao deixasse de exigir ou de conceder acrobatics, o teste
        abaixo passaria pelo motivo errado."""
        reg = BASE.get("wb:feat/acrobat-dedication")
        texto = json.dumps(reg, ensure_ascii=False)
        self.assertIn('"acrobatics"', json.dumps(reg.get("requires"), ensure_ascii=False))
        self.assertIn("acrobatics", texto)

    def test_dedicacao_que_concede_o_que_exige_e_sinalizada(self):
        p = wb_motor.Personagem(neutro("wb:feat/acrobat-dedication"), BASE)
        self.assertTrue([m for m in motivos(p) if "acrobatics" in m], motivos(p))

    def test_mas_o_efeito_e_aplicado_assim_mesmo(self):
        """Principio zero: sinaliza e nao desfaz. A pericia entra na ficha."""
        p = wb_motor.Personagem(neutro("wb:feat/acrobat-dedication"), BASE)
        self.assertEqual(p.proficiencias.get("acrobatics"), "trained")

    def test_requisito_legitimo_continua_limpo(self):
        """Controle: uma dedicacao cujo requisito a ficha atende de verdade nao
        pode ser afetada pelo desconto."""
        p = wb_motor.Personagem(neutro("wb:feat/shieldmarshal-dedication"), BASE)
        self.assertEqual(p.fora_do_requisito, [], motivos(p))
        self.assertEqual(p.proficiencias.get("society"), "expert")

    def test_rank_sem_desconta_so_a_origem_pedida(self):
        p = wb_motor.Personagem(neutro("wb:feat/shieldmarshal-dedication"), BASE)
        self.assertEqual(p._rank_sem("society", None), "expert")
        self.assertEqual(p._rank_sem("society", "wb:feat/shieldmarshal-dedication"),
                         "untrained")


class TestRaizDaCadeia(unittest.TestCase):
    """Concessao carrega de QUEM ela veio, ate a ponta da cadeia."""

    def setUp(self):
        self.p = wb_motor.Personagem(doc_base(), BASE)

    def test_concedido_sabe_a_origem_imediata_e_a_raiz(self):
        por_id = {c["id"]: c for c in self.p.concedidos}
        streetwise = por_id["wb:feat/streetwise"]
        self.assertEqual(streetwise["concedido_por"], "wb:feat/shieldmarshal-dedication")
        self.assertEqual(streetwise["raiz"], "wb:feat/shieldmarshal-dedication")

    def test_a_ficha_expoe_os_concedidos(self):
        v = self.p.visao()
        ids = {c["id"] for c in v["concedidos"]}
        self.assertIn("wb:feat/streetwise", ids)
        self.assertIn("wb:feat/courtly-graces", ids)


class TestOrigensDaCadeia(unittest.TestCase):
    """A cadeia parte de feat, feature, ancestria, heranca e background."""

    def test_heranca_concede(self):
        """`ambitious-human` concede Fleet. Sao 69 alvos validos nesses tres
        kinds (44 heranca + 25 background) que ficavam inertes."""
        d = doc_base()
        d["escolhas"] = [e for e in d["escolhas"] if e.get("pega") != "wb:feat/fleet"]
        for e in d["escolhas"]:
            if e.get("slot") == "heranca":
                e["pega"] = "wb:heritage/ambitious-human"
        p = wb_motor.Personagem(d, BASE)
        self.assertIn("wb:feat/fleet", {c["id"] for c in p.concedidos})

    def test_o_que_ja_foi_escolhido_nao_e_concedido_de_novo(self):
        """Mesma heranca, mas com Fleet escolhido a mao: nao duplica."""
        d = doc_base()
        for e in d["escolhas"]:
            if e.get("slot") == "heranca":
                e["pega"] = "wb:heritage/ambitious-human"
        p = wb_motor.Personagem(d, BASE)
        self.assertEqual([c for c in p.concedidos if c["id"] == "wb:feat/fleet"], [])

    def test_alvo_nao_resolvido_pelo_pipeline_e_sinalizado(self):
        """O background `warrior` promete Intimidating Glare e o alvo nao esta
        resolvido (item 70). Antes de a cadeia visitar background, este aviso
        era codigo morto: os 476 alvos orfaos estao todos nesse kind."""
        p = wb_motor.Personagem(doc_base(), BASE)
        self.assertTrue([a for a in p.avisos if "nao resolvido pelo pipeline" in a],
                        p.avisos)


class TestRegrasDeDedicacaoEnxergamConcedidos(unittest.TestCase):
    """As checagens de arquetipo leem escolhido MAIS concedido."""

    def test_ids_de_feat_inclui_os_concedidos(self):
        p = wb_motor.Personagem(doc_base(), BASE)
        ids = p._ids_de_feat_escolhidos()
        self.assertIn("wb:feat/shieldmarshal-dedication", ids)   # escolhido
        self.assertIn("wb:feat/streetwise", ids)                 # concedido

    def test_dedicacao_concedida_nao_gera_falso_positivo(self):
        """`gray-corsair-training` concede `pirate-dedication`. Um feat Pirate
        na mesma ficha nao pode ser acusado de faltar a dedicacao."""
        concede = BASE.opcional("wb:feat/gray-corsair-training")
        if concede is None:
            self.skipTest("gray-corsair-training ausente da base neste pin")
        alvos = [a for g in (concede.get("grants") or []) if isinstance(g, dict)
                 for a in (g.get("grant_feat") or [])]
        self.assertIn("wb:feat/pirate-dedication", alvos)
        d = neutro()
        d["escolhas"].append({"em": 2, "slot": "free_archetype",
                              "pega": "wb:feat/gray-corsair-training"})
        p = wb_motor.Personagem(d, BASE)
        self.assertIn("wb:feat/pirate-dedication", p._ids_de_feat_escolhidos())


class TestSemDuplaContagem(unittest.TestCase):
    """O mesmo efeito nunca entra duas vezes."""

    def test_toughness_escolhido_e_concedido_dao_o_mesmo_hp(self):
        so_dedicacao = wb_motor.Personagem(
            neutro("wb:feat/battle-harbinger-dedication"), BASE)
        d = neutro("wb:feat/battle-harbinger-dedication")
        d["escolhas"].append({"em": 2, "slot": "class_feat", "pega": "wb:feat/toughness"})
        com_os_dois = wb_motor.Personagem(d, BASE)
        self.assertEqual(so_dedicacao.hp, com_os_dois.hp)

    def test_toughness_aparece_uma_vez_so_no_detalhe_de_hp(self):
        p = wb_motor.Personagem(neutro("wb:feat/battle-harbinger-dedication"), BASE)
        vezes = [d for d in p.hp_detalhe if "Toughness" in str(d.get("origem"))]
        self.assertEqual(len(vezes), 1, p.hp_detalhe)


if __name__ == "__main__":
    unittest.main()
