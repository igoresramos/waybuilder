"""Testes da reconciliacao e da fusao legado<->remaster.

Cada caso reproduz um defeito real que a auditoria de 2026-07-26 mediu na base
v1. Se um deles voltar a passar com o comportamento antigo, o teste quebra.
"""
import os
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

import comum        # noqa: E402
import reconciliar  # noqa: E402


def reg(**kw):
    base = {"id": "wb:feat/x", "kind": "feat", "prov": {}, "xref": {}}
    base.update(kw)
    return base


class TestFundir(unittest.TestCase):
    def test_divergencia_entre_fontes_vira_conflito(self):
        # A3: 6 kinds saiam do build com 2+ fontes e ZERO conflitos
        a = reg(level=5, prov={"level": "foundry"}, xref={"foundry": "f1"})
        b = reg(level=8, prov={"level": "aon"}, xref={"aon": "a1"})
        r = reconciliar.fundir([a, b])
        self.assertEqual(r["level"], 5)                     # precedencia: foundry
        self.assertTrue(r["conflitos"])
        self.assertEqual(r["conflitos"][0]["campo"], "level")

    def test_grafia_de_livro_nao_vira_conflito(self):
        a = reg(source={"book": "Player Core"}, prov={"source": "aon"}, xref={"aon": "a1"})
        b = reg(source={"book": "Pathfinder Player Core"}, prov={"source": "foundry"},
                xref={"foundry": "f1"})
        r = reconciliar.fundir([a, b])
        self.assertFalse([c for c in (r.get("conflitos") or []) if c["campo"] == "source"])

    def test_source_mescla_por_subcampo(self):
        # um lado tem o livro, o outro tem a pagina: os dois entram
        a = reg(source={"book": "Player Core"}, prov={"source": "aon"}, xref={"aon": "a1"})
        b = reg(source={"book": "Pathfinder Player Core", "page": 145},
                prov={"source": "foundry"}, xref={"foundry": "f1"})
        r = reconciliar.fundir([a, b])
        self.assertEqual(r["source"]["book"], "Player Core")
        self.assertEqual(r["source"]["page"], 145)
        self.assertEqual(r["prov"]["source.page"], "foundry")

    def test_traits_e_uniao_e_nunca_null(self):
        a = reg(traits=["two-hand-d12"], prov={"traits": "foundry"}, xref={"foundry": "f1"})
        b = reg(traits=["two-hand", "magical"], prov={"traits": "aon"}, xref={"aon": "a1"})
        r = reconciliar.fundir([a, b])
        self.assertEqual(r["traits"], ["magical", "two-hand-d12"])

    def test_registro_sem_traits_sai_com_lista_vazia(self):
        r = reconciliar.fundir([reg(xref={"aon": "a1"})])
        self.assertEqual(r["traits"], [])

    def test_prov_nunca_fica_desconhecida(self):
        a = reg(level=5, xref={"foundry": "f1"})            # sem prov declarado
        r = reconciliar.fundir([a])
        self.assertTrue(comum.prov_valido(r["prov"]["level"]), r["prov"])

    def test_xref_com_dois_docs_aon_nao_sobrescreve_em_silencio(self):
        # 5.599 pares declarados tem o MESMO nome e caem no mesmo slug
        ponte = comum.carregar_ponte()
        legado, vigente = "feat-359", "feat-4775"           # Power Attack / Vicious Swing
        a = reg(name="Vicious Swing", xref={"aon": legado})
        b = reg(name="Vicious Swing", xref={"aon": vigente})
        r = reconciliar.fundir([a, b])
        self.assertEqual(r["xref"]["aon"], vigente)
        self.assertEqual(r["xref"]["legado_aon"], legado)
        self.assertTrue(comum.e_legado(legado, ponte))


class TestDesmembramento(unittest.TestCase):
    def test_traits_disjuntos_desmembram_antes_da_fusao(self):
        a = reg(id="wb:feat/death-from-above", traits=["archetype"], level=8,
                xref={"foundry": "j8CLa6RoohfKCWoO"})
        b = reg(id="wb:feat/death-from-above", traits=["mythic"], level=16,
                xref={"aon": "feat-7380"})
        saida = reconciliar.desmembrar([a, b])
        self.assertIsNotNone(saida)
        self.assertEqual(len({r["id"] for r in saida}), 2)

    def test_curadoria_separa_pelo_xref_declarado(self):
        curadoria = reconciliar.carregar_curadoria()
        self.assertIn("wb:feat/play-to-the-crowd", curadoria)
        a = reg(id="wb:feat/play-to-the-crowd", level=12, xref={"aon": "feat-7637"})
        b = reg(id="wb:feat/play-to-the-crowd", level=4, xref={"foundry": "KrYvJ5n06yHCipCZ"})
        saida = reconciliar.desmembrar_curado([a, b], curadoria)
        ids = sorted(r["id"] for r in saida)
        self.assertEqual(ids, ["wb:feat/play-to-the-crowd", "wb:feat/play-to-the-crowd-dandy"])
        dandy = [r for r in saida if r["id"].endswith("dandy")][0]
        self.assertEqual(dandy["level"], 12)

    def test_faceta_complementar_nao_desmembra(self):
        # blade-byrnie: foundry flexible/noisy, aon invested/magical
        a = reg(traits=["flexible", "noisy"])
        b = reg(traits=["invested", "magical"])
        self.assertIsNone(reconciliar.desmembrar([a, b]))


class TestFusaoLegadoRemaster(unittest.TestCase):
    """A regra que a v1 errou: chave da fonte, veto so de categoria, nada deletado."""

    def setUp(self):
        import fundir_renomeados
        self.f = fundir_renomeados

    def test_veto_de_categoria_impede_feature_virar_classe(self):
        # 351/351 class-features com remaster_id apontam para uma CLASSE
        legado = {"id": "wb:class-feature/evasion", "kind": "class-feature"}
        alvo = {"id": "wb:class/alchemist", "kind": "class"}
        motivo = self.f.veto(legado, alvo,
                             {"category": "class-feature"}, {"category": "class"})
        self.assertIsNotNone(motivo)

    def test_mesma_categoria_nao_veta(self):
        legado = {"id": "wb:feat/power-attack", "kind": "feat"}
        alvo = {"id": "wb:feat/vicious-swing", "kind": "feat"}
        self.assertIsNone(self.f.veto(legado, alvo,
                                      {"category": "feat"}, {"category": "feat"}))

    def test_n_para_1_e_anotacao_e_nao_veto(self):
        # `Magic Wand` recebe as 10 varas por rank -- consolidacao declarada
        notas = self.f.anotacoes({"level": 3}, {"level": 3}, {}, 10)
        self.assertTrue(any("consolidacao" in n for n in notas))
        self.assertIsNone(self.f.veto({"kind": "equipment"}, {"kind": "equipment"},
                                      {"category": "equipment"}, {"category": "equipment"}))

    def test_errata_de_level_vira_anotacao(self):
        notas = self.f.anotacoes({"level": 2}, {"level": 3}, {}, 1)
        self.assertEqual(notas, ["level: 2 -> 3"])


if __name__ == "__main__":
    unittest.main()
