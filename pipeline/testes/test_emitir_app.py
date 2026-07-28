#!/usr/bin/env python3
"""O payload do app: o que o cliente carrega nao e o artefato de build.

`base/index.json` carrega proveniencia por campo, referencia cruzada para as
tres fontes e registro de conflito. Isso existe para AUDITAR a base -- o
construtor nunca le nada disso, e mandar para o navegador seria pagar 52% de
transferencia por metadado.

O que estes testes travam:

  1  nenhum campo de build vaza para o payload
  2  o que monta ficha continua inteiro (o corte e por lista NEGRA: campo novo
     entra por padrao, senao o app perderia dado novo em silencio)
  3  o nucleo cabe no orcamento do projeto -- PWA offline, client-side
  4  a prosa NAO viaja junto (ela sozinha e maior que o indice inteiro)

Rodar: python3 -m unittest discover -s pipeline/testes -t .
"""
import gzip
import json
import os
import unittest

AQUI = os.path.dirname(os.path.abspath(__file__))
PIPELINE = os.path.dirname(AQUI)
BASE = os.path.join(PIPELINE, "base")
APP = os.path.join(BASE, "app")

# orcamento do projeto para a PRIMEIRA carga, em bytes gzip. Sai da spec: o
# indice tem de caber em ~0,53 MB para o app rodar offline sem backend.
ORCAMENTO_NUCLEO = int(0.53 * 1024 * 1024)

# o que a primeira tela precisa: escolher classe, ancestria, background e feat.
# Equipamento, magia e catalogo de referencia entram sob demanda.
NUCLEO = ("class", "class-feature", "feat", "ancestry", "heritage",
          "background", "archetype", "skill")


def existe():
    return os.path.exists(os.path.join(APP, "_manifesto.json"))


@unittest.skipUnless(existe(), "payload do app ainda nao emitido (build.sh passo 9)")
class TestPayloadDoApp(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        with open(os.path.join(APP, "_manifesto.json"), encoding="utf-8") as fh:
            cls.manifesto = json.load(fh)
        with open(os.path.join(APP, "index.json"), encoding="utf-8") as fh:
            cls.app = json.load(fh)

    def test_nenhum_metadado_de_build_vaza(self):
        proibidos = {"prov", "xref", "conflitos", "texto"}
        vazaram = {k for r in self.app for k in r if k in proibidos}
        self.assertEqual(vazaram, set())

    def test_o_indice_do_app_e_bem_menor_que_o_de_build(self):
        self.assertLess(self.manifesto["gzip_indice_completo"],
                        self.manifesto["gzip_indice_de_build"] * 0.75)

    def test_o_nucleo_cabe_no_orcamento(self):
        fatias = self.manifesto["por_kind"]
        nucleo = sum(fatias[k]["gzip_bytes"] for k in NUCLEO if k in fatias)
        self.assertLessEqual(
            nucleo, ORCAMENTO_NUCLEO,
            f"nucleo em {nucleo / 1048576:.2f} MB gzip, orcamento "
            f"{ORCAMENTO_NUCLEO / 1048576:.2f} MB")

    def test_nao_perde_registro(self):
        with open(os.path.join(BASE, "index.json"), encoding="utf-8") as fh:
            build = json.load(fh)
        self.assertEqual(len(self.app), len(build))
        self.assertEqual({r["id"] for r in self.app}, {r["id"] for r in build})

    def test_o_que_monta_ficha_continua_inteiro(self):
        """Corte por lista negra: se um extrator passar a emitir campo novo,
        ele entra no payload por padrao. Lista branca faria o app perder dado
        novo em silencio."""
        por_id = {r["id"]: r for r in self.app}
        essenciais = {
            "wb:class/fighter": ("grants", "progressao", "key_ability"),
            "wb:feat/toughness": ("grants", "level", "traits"),
            "wb:ancestry/human": ("grants", "hp"),
            "wb:feat/shieldmarshal-dedication": ("grants", "requires", "traits"),
        }
        for wb_id, campos in essenciais.items():
            reg = por_id.get(wb_id)
            self.assertIsNotNone(reg, wb_id)
            for campo in campos:
                self.assertIn(campo, reg, f"{wb_id} perdeu `{campo}`")

    def test_o_ponteiro_de_prosa_sobrevive(self):
        """A prosa nao viaja junto, mas o app precisa saber onde busca-la."""
        com_ponteiro = [r for r in self.app if r.get("text")]
        self.assertGreater(len(com_ponteiro), len(self.app) * 0.9)

    def test_a_prosa_nao_viaja_junto(self):
        """Ela sozinha e maior que o indice inteiro -- e a razao de existir
        carga sob demanda."""
        self.assertGreater(self.manifesto["prosa_bytes_em_disco"],
                           self.manifesto["gzip_indice_completo"])

    def test_cada_kind_tem_a_propria_fatia(self):
        for kind, dados in self.manifesto["por_kind"].items():
            caminho = os.path.join(APP, "por-kind", f"{kind}.json")
            self.assertTrue(os.path.exists(caminho), kind)
            with open(caminho, encoding="utf-8") as fh:
                itens = json.load(fh)
            self.assertEqual(len(itens), dados["registros"], kind)

    def test_o_arquivo_gravado_bate_com_o_manifesto(self):
        """Guarda contra manifesto desatualizado: o numero declarado tem de ser
        o do arquivo em disco, nao o da ultima vez que alguem rodou."""
        with open(os.path.join(APP, "index.json"), "rb") as fh:
            real = len(gzip.compress(fh.read()))
        declarado = self.manifesto["gzip_indice_completo"]
        self.assertLess(abs(real - declarado), max(2048, declarado * 0.02),
                        f"manifesto diz {declarado}, arquivo tem {real}")


if __name__ == "__main__":
    unittest.main()
