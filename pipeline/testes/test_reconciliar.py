"""Testes da reconciliacao e da fusao legado<->remaster.

Cada caso reproduz um defeito real que a auditoria de 2026-07-26 mediu na base
v1. Se um deles voltar a passar com o comportamento antigo, o teste quebra.

Os testes nasceram na linha paralela de 2026-07-27, contra funcoes que aquele
pipeline expunha (`reconciliar.desmembrar`, `fundir_renomeados.veto`). Aqui a
mesma regra existe, mas dentro do `main()` de `desmembrar_colisoes.py` e de
`fundir_renomeados.py` -- entao a verificacao passou a ser feita sobre o
ARTEFATO, que e o alvo que interessa de qualquer forma: teste de funcao verde
com dado emitido errado foi exatamente o que deixou a uniao de traits passar.
Ver docs/2026-07-27_duas-linhas-merge-pendente.md.
"""
import json
import os
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

import comum        # noqa: E402
import reconciliar  # noqa: E402

BASE = os.path.join(RAIZ, "base", "index.json")


def reg(**kw):
    base = {"id": "wb:feat/x", "kind": "feat", "prov": {}, "xref": {}}
    base.update(kw)
    return base


def carregar_base():
    with open(BASE) as fh:
        return {r["id"]: r for r in json.load(fh)}


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
        # a canonizacao acontece em `carregar()`, antes de comparar -- e o
        # ponto do fix: normalizar so na comparacao deixava o valor emitido
        # sair nas duas grafias. O teste reproduz a ordem real do pipeline.
        a = reg(source={"book": reconciliar.canonizar_livro("Player Core")},
                prov={"source": "aon"}, xref={"aon": "a1"})
        b = reg(source={"book": reconciliar.canonizar_livro("Pathfinder Player Core")},
                prov={"source": "foundry"}, xref={"foundry": "f1"})
        r = reconciliar.fundir([a, b])
        self.assertFalse([c for c in (r.get("conflitos") or []) if c["campo"] == "source"])

    def test_colisao_de_mesma_fonte_nao_apaga_o_vencedor(self):
        # duas entradas da MESMA fonte caiam na mesma chave do dict de
        # conflito: a segunda sobrescrevia a primeira e o registro passava a
        # dizer que o vencedor era o valor perdedor. 337 entradas assim na
        # base de 2026-07-27.
        a = reg(level=5, prov={"level": "aon"}, xref={"aon": "a1"})
        b = reg(level=8, prov={"level": "aon"}, xref={"aon": "a2"})
        r = reconciliar.fundir([a, b])
        c = [x for x in r["conflitos"] if x["campo"] == "level"][0]
        self.assertEqual(r["level"], 5)                    # empate: o 1o fica
        self.assertEqual(c["escolhido"], "aon")
        self.assertEqual(c["aon"], 5)                      # o vencedor, nao o perdedor
        self.assertEqual(c["aon_2"], 8)                    # e o perdedor visivel

    @unittest.expectedFailure
    def test_source_mescla_por_subcampo(self):
        # GAP DA SPEC v2, nao adotada nesta linha: aqui `source` e disputado
        # inteiro por precedencia, entao a pagina que so a outra fonte tinha
        # nao entra. Medido: 1.518 dos 19.738 registros sem `source.page`.
        # Vira verde sozinho no dia em que a fusao por subcampo entrar.
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
        # DECIDIDO 2026-07-27 (TODO item 53): traits ausente vira `[]`, nunca
        # `null` -- ausencia real (Foundry 0/66, AoN 2/66), nao desconhecimento.
        # Corrigido em reconciliar.fundir/traits_ausente_vira_lista_vazia.
        # Medido antes do fix: 66 registros com traits null na base (39
        # class-feature, 27 class); so vale no artefato depois do rebuild.
        r = reconciliar.fundir([reg(xref={"aon": "a1"})])
        self.assertEqual(r["traits"], [])

    @unittest.expectedFailure
    def test_prov_nunca_fica_desconhecida(self):
        # GAP DA SPEC v2: a fonte unica nao ganha `prov` na fusao. Medido: 684
        # campos com "desconhecida" e 128 com prov vazio na base.
        a = reg(level=5, xref={"foundry": "f1"})            # sem prov declarado
        r = reconciliar.fundir([a])
        self.assertTrue(comum.prov_valido(r["prov"]["level"]), r["prov"])


@unittest.skipUnless(os.path.exists(BASE), "base ainda nao emitida")
class TestLegadoNoArtefato(unittest.TestCase):
    """A ponte legado<->remaster, medida onde ela importa: no dado emitido."""

    @classmethod
    def setUpClass(cls):
        cls.base = carregar_base()

    def test_dois_docs_aon_para_o_mesmo_nome_nao_se_apagam(self):
        # 5.599 pares declarados tem o MESMO nome e caem no mesmo slug. Power
        # Attack (feat-359) foi renomeado para Vicious Swing (feat-4775): o id
        # legado tem de sobreviver no registro, nao ser sobrescrito.
        r = self.base["wb:feat/vicious-swing"]
        self.assertEqual(r["xref"]["aon"], "feat-4775")
        self.assertEqual(r["xref"]["legado_aon"], "feat-359")
        self.assertTrue(comum.e_legado("feat-359", comum.carregar_ponte()))

    def test_a_fusao_legado_remaster_realmente_aconteceu(self):
        com_legado = [r for r in self.base.values() if (r.get("xref") or {}).get("legado_aon")]
        self.assertGreater(len(com_legado), 500)

    def test_nada_foi_deletado_na_fusao(self):
        # o legado absorvido deixa rastro em `historico` (nome e livro antigos)
        # e, quando o nome mudou, tambem em `aliases`. Em 323 dos 616 casos o
        # nome nao mudou -- so o livro -- entao `aliases` vazio e normal e o
        # rastro obrigatorio e o `historico`.
        for r in self.base.values():
            for entrada in (r.get("historico") or []):
                self.assertTrue(entrada.get("nome_legado"), r["id"])
                self.assertTrue(entrada.get("id_legado"), r["id"])

    def test_nenhuma_class_feature_foi_absorvida_por_uma_classe(self):
        # 351/351 class-features com remaster_id apontam para a CLASSE, nao
        # para a feature sucessora. Nesta linha quem barra e o veto por campo
        # estruturado divergente (`kind` esta em CAMPOS_VETO); na linha
        # paralela era um veto explicito de categoria. Efeito igual.
        import fundir_renomeados
        self.assertIn("kind", fundir_renomeados.CAMPOS_VETO)
        classes_com_historico = [r["id"] for r in self.base.values()
                                 if r["kind"] == "class" and r.get("historico")]
        self.assertEqual(classes_com_historico, [])


@unittest.skipUnless(os.path.exists(BASE), "base ainda nao emitida")
class TestDesmembramentoNoArtefato(unittest.TestCase):
    """Colisao de identidade: um id da base casando com N entidades da fonte."""

    @classmethod
    def setUpClass(cls):
        cls.base = carregar_base()

    def test_traits_disjuntos_desmembram(self):
        # `Death from Above`: 1 doc no Foundry (nv8, archetype) e 2 no AoN
        # (feat-7610 archetype nv8; feat-7380 mitico nv16). A base v1 emitiu
        # um registro quimera -- nivel 8 com traits `mythic`.
        irmaos = [i for i in self.base if i.startswith("wb:feat/death-from-above")]
        self.assertGreaterEqual(len(irmaos), 2, irmaos)
        # o irmao criado aponta de volta para o id que colidiu
        criados = [i for i in irmaos
                   if self.base[i].get("desmembrado_de") == "wb:feat/death-from-above"]
        self.assertTrue(criados, irmaos)
        # e os dois feats voltaram a ter niveis distintos, nao um so quimera
        niveis = {self.base[i].get("level") for i in irmaos}
        self.assertIn(8, niveis)
        self.assertIn(16, niveis)

    def test_curadoria_separa_pelo_xref_declarado(self):
        curada = json.load(open(os.path.join(RAIZ, "colisoes_identidade.json")))
        self.assertIn("wb:feat/play-to-the-crowd", curada)
        self.assertIn("wb:feat/play-to-the-crowd-dandy", self.base)

    def test_faceta_complementar_nao_desmembra(self):
        # blade-byrnie: foundry traz flexible/noisy, aon traz invested/magical.
        # Sao facetas do MESMO item -- uniao, nao colisao. Continua um registro.
        r = self.base["wb:armor/blade-byrnie"]
        self.assertEqual(sorted(r["traits"]), ["flexible", "invested", "magical", "noisy"])
        self.assertIsNone(r.get("desmembrado_de"))


if __name__ == "__main__":
    unittest.main()
