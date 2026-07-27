"""Testes da camada compartilhada. Cada caso sai de um numero medido na
auditoria de 2026-07-26 ou de uma regra escrita na spec v2 -- nao de exemplo
inventado.

Rodar: python3 -m unittest discover -s pipeline/testes -t .
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import comum  # noqa: E402


class TestNormalizacaoLivro(unittest.TestCase):
    def test_grafias_da_auditoria_caem_na_mesma_chave(self):
        pares = [("Player Core", "Pathfinder Player Core"),
                 ("Dark Archives (Remastered)", "Pathfinder Dark Archive (Remastered)"),
                 ("Guns & Gears", "Pathfinder Guns & Gears")]
        for a, b in pares:
            self.assertEqual(comum.chave_livro(a), comum.chave_livro(b), (a, b))

    def test_livros_diferentes_nao_colidem(self):
        self.assertNotEqual(comum.chave_livro("Player Core"),
                            comum.chave_livro("Player Core 2"))

    def test_limpar_tira_crlf_literal(self):
        self.assertEqual(comum.limpar_livro("Pathfinder #218: Titanbane\r\n"),
                         "Pathfinder #218: Titanbane")

    def test_canonica_e_a_mais_frequente(self):
        grafias = ["Player Core"] * 2032 + ["Pathfinder Player Core"] * 83
        canon = comum.eleger_canonicos(grafias)
        self.assertEqual(canon[comum.chave_livro("Player Core")], "Player Core")

    def test_canonica_desempata_pela_mais_curta(self):
        canon = comum.eleger_canonicos(["Dark Archives (Remastered)",
                                        "Pathfinder Dark Archive (Remastered)"])
        self.assertEqual(canon[comum.chave_livro("Dark Archives (Remastered)")],
                         "Dark Archives (Remastered)")


class TestProv(unittest.TestCase):
    def test_lido_e_inferido(self):
        self.assertEqual(comum.prov_lido("aon"), "aon")
        self.assertEqual(comum.prov_inferido("aon", "livro"), "aon~inferido:livro")

    def test_desconhecida_nao_e_prov_valido(self):
        self.assertFalse(comum.prov_valido("desconhecida"))
        self.assertFalse(comum.prov_valido(""))
        self.assertFalse(comum.prov_valido("foundry(deities, por nome)"))

    def test_regra_nao_registrada_e_recusada(self):
        with self.assertRaises(AssertionError):
            comum.prov_inferido("aon", "chute")

    def test_fonte_de(self):
        self.assertEqual(comum.fonte_de("aon~inferido:remaster_id"), "aon")


class TestEscolher(unittest.TestCase):
    def test_precedencia_da_spec(self):
        valor, prov, conf = comum.escolher("grants", {"aon": ["a"], "foundry": ["b"]})
        self.assertEqual(valor, ["b"])
        self.assertEqual(prov, "foundry")
        self.assertEqual(len(conf), 1)

    def test_concordancia_nao_gera_conflito(self):
        _, _, conf = comum.escolher("level", {"foundry": 5, "pf2etools": 5})
        self.assertEqual(conf, [])

    def test_divergencia_registrada_com_os_dois_lados(self):
        _, _, conf = comum.escolher("level", {"foundry": 8, "pf2etools": 9})
        self.assertEqual(conf[0]["campo"], "level")
        self.assertEqual(conf[0]["escolhido"], "foundry")
        self.assertEqual(conf[0]["foundry"], 8)
        self.assertEqual(conf[0]["pf2etools"], 9)

    def test_livro_com_grafia_diferente_nao_e_divergencia(self):
        _, _, conf = comum.escolher("source.book",
                                    {"aon": "Player Core",
                                     "foundry": "Pathfinder Player Core"})
        self.assertEqual(conf, [])

    def test_livro_realmente_diferente_e_divergencia(self):
        # caso real: wb:class-feature/armor-expertise, Foundry Player Core x base PC2
        _, _, conf = comum.escolher("source.book",
                                    {"aon": "Player Core 2",
                                     "foundry": "Player Core"})
        self.assertEqual(len(conf), 1)

    def test_fonte_vazia_e_ignorada(self):
        valor, prov, _ = comum.escolher("name", {"aon": None, "foundry": "Gaff"})
        self.assertEqual(valor, "Gaff")
        self.assertEqual(prov, "foundry")

    def test_sem_candidato_devolve_none(self):
        self.assertEqual(comum.escolher("name", {"aon": None}), (None, None, []))


class TestUniaoTraits(unittest.TestCase):
    def test_facetas_complementares_se_somam(self):
        # blade-byrnie: foundry flexible/noisy, aon invested/magical
        traits, _, fontes = comum.uniao_traits(
            {"foundry": ["flexible", "noisy"], "aon": ["invested", "magical"]})
        self.assertEqual(traits, ["flexible", "invested", "magical", "noisy"])
        self.assertEqual(fontes, ["aon", "foundry"])

    def test_ancestria_legada_vira_remaster_e_vai_para_alias(self):
        traits, aliases, _ = comum.uniao_traits(
            {"aon": ["tiefling"], "foundry": ["nephilim"]})
        self.assertEqual(traits, ["nephilim"])
        self.assertIn("tiefling", aliases)

    def test_parametrizado_absorve_base(self):
        # bastard-sword perdia o dado de dano na v1
        traits, _, _ = comum.uniao_traits(
            {"foundry": ["two-hand-d12"], "aon": ["two-hand"]})
        self.assertEqual(traits, ["two-hand-d12"])

    def test_removido_sem_sucessor_sai_dos_traits_e_fica_no_alias(self):
        traits, aliases, _ = comum.uniao_traits({"aon": ["evocation", "fire"]})
        self.assertEqual(traits, ["fire"])
        self.assertIn("evocation", aliases)

    def test_illusion_sobreviveu_ao_remaster(self):
        traits, _, _ = comum.uniao_traits({"aon": ["illusion"]})
        self.assertEqual(traits, ["illusion"])

    def test_vazio_devolve_lista_vazia_nao_none(self):
        traits, _, _ = comum.uniao_traits({"aon": []})
        self.assertEqual(traits, [])


class TestColisaoIdentidade(unittest.TestCase):
    def test_death_from_above_e_colisao(self):
        self.assertTrue(comum.traits_disjuntos(["archetype"], ["mythic"]))

    def test_divergencia_de_faceta_nao_e_colisao(self):
        self.assertFalse(comum.traits_disjuntos(["flexible", "noisy"],
                                                ["invested", "magical"]))

    def test_sufixo_sai_do_trait_de_categoria(self):
        a = {"traits": ["mythic"], "level": 16}
        b = {"traits": ["archetype"], "level": 8}
        self.assertEqual(comum.sufixo_desambiguador(a, b), "mythic")

    def test_sufixo_cai_para_nivel_quando_nada_mais_distingue(self):
        a = {"traits": ["fighter"], "level": 4, "source": {"book": "Player Core"}}
        b = {"traits": ["fighter"], "level": 6, "source": {"book": "Player Core"}}
        self.assertEqual(comum.sufixo_desambiguador(a, b), "nv4")


class TestMecanizacao(unittest.TestCase):
    def test_kind_sem_grants_responde_null(self):
        # trait tambem nao tem pre-requisito: os dois campos sao "nao se aplica"
        g, r = comum.mecanizacao("trait", tinha_mecanica=False, perdeu_mecanica=False,
                                 tem_requires_texto=False, requires_saiu=False)
        self.assertIsNone(g)
        self.assertIsNone(r)

    def test_sem_mecanica_a_converter_e_sucesso(self):
        g, _ = comum.mecanizacao("feat", False, False, False, False)
        self.assertTrue(g)

    def test_perda_de_rule_element_e_false(self):
        g, _ = comum.mecanizacao("feat", True, True, False, False)
        self.assertFalse(g)

    def test_requires_texto_sem_predicado_e_false(self):
        _, r = comum.mecanizacao("feat", True, False, True, False)
        self.assertFalse(r)

    def test_sem_pre_requisito_nenhum_e_true(self):
        _, r = comum.mecanizacao("feat", True, False, False, False)
        self.assertTrue(r)

    def test_kind_sem_requisito_por_natureza_e_null(self):
        # spell nao tem pre-requisito: null, nao true -- senao as duas regras
        # da spec mandavam valores diferentes para o mesmo registro
        _, r = comum.mecanizacao("spell", True, False, False, False)
        self.assertIsNone(r)

    def test_kind_sem_requisito_com_requires_texto_volta_a_regra_normal(self):
        _, r = comum.mecanizacao("spell", True, False, True, False)
        self.assertFalse(r)

    def test_archetype_nao_concede_grants(self):
        g, _ = comum.mecanizacao("archetype", False, False, False, False)
        self.assertIsNone(g)


class TestPonte(unittest.TestCase):
    """A ponte legado<->remaster e a unica chave de fusao aceita pela spec v2."""

    @classmethod
    def setUpClass(cls):
        cls.ponte = comum.carregar_ponte()

    def test_ponte_carrega_dos_dumps_locais(self):
        self.assertGreater(len(self.ponte), 5000)

    def test_power_attack_declara_vicious_swing(self):
        doc = self.ponte.get("feat-359")
        self.assertIsNotNone(doc, "feat-359 (Power Attack) ausente da ponte")
        self.assertIn("feat-4775", comum.como_lista(doc.get("remaster_id")))

    def test_e_legado_distingue_os_dois_lados(self):
        self.assertTrue(comum.e_legado("feat-359", self.ponte))
        self.assertFalse(comum.e_legado("feat-4775", self.ponte))

    def test_class_feature_aponta_para_classe_e_nao_para_feature(self):
        # 351/351 medidos: por isso existe o veto de categoria na fusao
        doc = self.ponte.get("class-feature-25")   # Evasion
        if doc:
            alvos = comum.como_lista(doc.get("remaster_id"))
            self.assertTrue(all(a.startswith("class-") and not a.startswith("class-feature")
                                for a in alvos), alvos)


if __name__ == "__main__":
    unittest.main()
