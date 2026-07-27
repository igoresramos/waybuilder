"""Testes do extrator de conjuracao -- foco na integracao de
`tabelas_conjuracao_pdf.json` como fonte vencedora da tabela numerica de
slots (spec v2, secao "Vocabulario de prov" + "escolher e registrar
divergencia sao a mesma operacao").

Cada caso reproduz um achado real da rodada de 2026-07-27
(docs/pdfs/2026-07-26_tabelas-conjuracao.md): o Oracle diverge do pf2etools
porque o pf2etools so tem a variante legado (2/3 slots) contra o remaster
(3/4) do PDF; o Magus usa '0*' pra marcar rank sem slot base (nao pode virar
divergencia so por notacao); o Animist usa notacao hibrida 'X+Y' que nao
reduz a inteiro.
"""
import os
import sys
import unittest

EXTRATORES = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/extratores"
PIPELINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PIPELINE)
sys.path.insert(0, EXTRATORES)

import comum       # noqa: E402
import conjuracao   # noqa: E402

# A tabela do PDF ainda nao e fonte do extrator nesta linha: o extrator monta a
# tabela de slots do AoN e do pf2etools, e `dados_derivados/tabelas_conjuracao_
# pdf.json` esta em disco esperando integracao (TODO 45 / task 16). Estes testes
# ficam como criterio de aceite dessa integracao -- o guarda cai sozinho no dia
# em que as funcoes existirem.
PDF_INTEGRADO = all(hasattr(conjuracao, f) for f in
                    ("_parse_pdf_cell", "parse_pdf_slot_table",
                     "escolher_slots", "load_pdf_tabelas"))
PENDENTE = "integracao da tabela do PDF ainda nao esta nesta linha (task 16)"


@unittest.skipUnless(PDF_INTEGRADO, PENDENTE)
class TestParsePdfCell(unittest.TestCase):
    def test_inteiro_puro(self):
        self.assertEqual(conjuracao._parse_pdf_cell(3), (3, None))

    def test_string_com_asterisco_preserva_bruto(self):
        self.assertEqual(conjuracao._parse_pdf_cell("1*"), (1, "1*"))

    def test_notacao_hibrida_nao_vira_inteiro(self):
        # Animist: 'X+Y' e dois pools independentes, nao um numero so
        val, bruto = conjuracao._parse_pdf_cell("2+1")
        self.assertIsNone(val)
        self.assertEqual(bruto, "2+1")

    def test_zero_com_asterisco_extrai_zero(self):
        # Magus: '0*' -- so existe via feature studious spells
        self.assertEqual(conjuracao._parse_pdf_cell("0*"), (0, "0*"))


@unittest.skipUnless(PDF_INTEGRADO, PENDENTE)
class TestParsePdfSlotTable(unittest.TestCase):
    def test_rank_zero_nao_entra_em_ranks_mas_fica_no_raw(self):
        """Mesma convencao de parse_slot_table (pf2etools): rank sem slot
        (n=0) fica de fora do dict numerico comparavel, senao um '0*' do PDF
        acusaria divergencia contra um pf2etools que simplesmente omite o
        rank (ver _tabelas_slots_iguais)."""
        pdf_entry = {"slots": {
            "notacao": "irrelevante pro parser",
            "7": {"cantrips": 5, "2": "0*", "3": 2, "4": 2},
        }}
        por_nivel = conjuracao.parse_pdf_slot_table(pdf_entry)
        entry = por_nivel["7"]
        self.assertNotIn("2", entry["ranks"])
        self.assertEqual(entry["ranks_raw"]["2"], "0*")
        self.assertEqual(entry["ranks"], {"3": 2, "4": 2})
        self.assertEqual(entry["max_rank"], 4)

    def test_notacao_hibrida_preservada_sem_forcar_formato(self):
        pdf_entry = {"slots": {
            "1": {"cantrips": "2+2", "1": "1+1"},
        }}
        entry = conjuracao.parse_pdf_slot_table(pdf_entry)["1"]
        self.assertEqual(entry["ranks"], {})
        self.assertEqual(entry["cantrips_raw"], "2+2")
        self.assertEqual(entry["ranks_raw"]["1"], "1+1")
        self.assertEqual(entry["max_rank"], 1)


@unittest.skipUnless(PDF_INTEGRADO, PENDENTE)
class TestEscolherSlots(unittest.TestCase):
    def test_sem_pf2etools_nao_gera_conflito(self):
        pdf = {"1": {"cantrips": 5, "ranks": {"1": 2}, "max_rank": 1}}
        valor, prov, conflitos = conjuracao.escolher_slots(pdf, None)
        self.assertEqual(valor, pdf)
        self.assertEqual(prov, comum.prov_lido("waybuilder"))
        self.assertEqual(conflitos, [])

    def test_fontes_concordam_nao_gera_conflito(self):
        pdf = {"1": {"cantrips": 5, "ranks": {"1": 2}, "max_rank": 1}}
        pf2etools = {"1": {"cantrips": 5, "ranks": {"1": 2}, "max_rank": 1}}
        valor, prov, conflitos = conjuracao.escolher_slots(pdf, pf2etools)
        self.assertEqual(valor, pdf)
        self.assertEqual(conflitos, [])

    def test_oracle_diverge_e_registra_conflito_no_formato_do_comum(self):
        # reproduz o achado real: pf2etools legado (2 no rank de entrada) x
        # PDF remaster (3 no rank de entrada)
        pdf = {"1": {"cantrips": 5, "ranks": {"1": 3}, "max_rank": 1}}
        pf2etools = {"1": {"cantrips": 5, "ranks": {"1": 2}, "max_rank": 1}}
        valor, prov, conflitos = conjuracao.escolher_slots(pdf, pf2etools)
        self.assertEqual(valor, pdf)                      # PDF vence
        self.assertEqual(prov, comum.prov_lido("waybuilder"))
        self.assertEqual(len(conflitos), 1)
        c = conflitos[0]
        self.assertEqual(c["campo"], "slots_per_level")
        self.assertEqual(c["escolhido"], "waybuilder")
        self.assertEqual(c["waybuilder"], pdf)
        self.assertEqual(c["pf2etools"], pf2etools)

    def test_diferenca_so_de_notacao_zero_nao_conflita(self):
        # rank com 0 (via '0*') de um lado e ausente do outro representam a
        # MESMA coisa (nenhum slot base nesse rank) -- nao e divergencia real
        pdf = conjuracao.parse_pdf_slot_table(
            {"slots": {"7": {"cantrips": 5, "2": "0*", "3": 2, "4": 2}}}
        )
        pf2etools = {"7": {"cantrips": 5, "ranks": {"3": 2, "4": 2}, "max_rank": 4}}
        _, _, conflitos = conjuracao.escolher_slots(pdf, pf2etools)
        self.assertEqual(conflitos, [])

    def test_sem_nenhuma_fonte_devolve_none(self):
        self.assertEqual(conjuracao.escolher_slots(None, None), (None, None, []))


@unittest.skipUnless(PDF_INTEGRADO, PENDENTE)
class TestLoadPdfTabelas(unittest.TestCase):
    def test_cobre_as_11_classes_conjuradoras(self):
        tabelas = conjuracao.load_pdf_tabelas()
        self.assertEqual(set(tabelas), set(conjuracao.CLASSES_COBERTAS))

    def test_nao_conjuradoras_ficam_de_fora(self):
        tabelas = conjuracao.load_pdf_tabelas()
        self.assertNotIn("exemplar", tabelas)
        self.assertNotIn("kineticist", tabelas)

    def test_oracle_tem_livro_e_pagina_do_remaster(self):
        oracle = conjuracao.load_pdf_tabelas()["oracle"]
        self.assertEqual(oracle["livro"], "Player Core 2")
        self.assertEqual(oracle["pagina"], 131)


if __name__ == "__main__":
    unittest.main()
