"""Testes dos portoes de qualidade.

O risco que estes testes cobrem nao e o portao reprovar quem deve reprovar --
e o portao PASSAR por acidente, medindo conjunto vazio ou campo que nunca
existe. Foi o que aconteceu na v1 com o portao 7 (procurava duplicata depois de
a duplicata ter sido eliminada) e com o relatorio de prosa (dividia pelo
subconjunto ja processado).

Estes testes rodam sobre o artefato real quando ele existe; sem base emitida,
sao pulados em vez de dar falso verde.
"""
import json
import os
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

import comum  # noqa: E402

BASE = os.path.join(RAIZ, "base", "index.json")


@unittest.skipUnless(os.path.exists(BASE), "base ainda nao emitida")
class TestInvariantesDaBase(unittest.TestCase):
    """Invariantes sobre o dado emitido.

    Os marcados `expectedFailure` sao promessas da spec v2, que nasceu na linha
    paralela de 2026-07-27 e NAO foi adotada aqui (esta linha segue a v1, com
    `mechanized` e sem espelho rank/level). Ficam no lugar, com o numero
    medido, porque um deles virar verde e o sinal de que a decisao de schema
    foi tomada -- o unittest acusa "unexpected success" e o marcador sai.
    Ver docs/2026-07-27_duas-linhas-merge-pendente.md.
    """

    @classmethod
    def setUpClass(cls):
        with open(BASE) as fh:
            cls.base = json.load(fh)
        cls.ids = {r["id"] for r in cls.base}

    def test_prov_nunca_e_desconhecida_nem_vazia(self):
        # `prov` existe para dizer de onde o campo veio. "desconhecida" e um
        # nao-resposta que passa pelo portao 1 sem informar nada. Medido em
        # 2026-07-27: 684 campos com "desconhecida" (313 grants, 308 requires,
        # concentrados em background) e 128 com prov vazio.
        ruins = [(r["id"], c) for r in self.base
                 for c, p in (r.get("prov") or {}).items()
                 if not p or "desconhecida" in str(p)]
        self.assertLessEqual(len(ruins), 12,
                             f"{len(ruins)} prov sem fonte -- piora conhecida de 12")

    @unittest.expectedFailure
    def test_nenhum_prov_desconhecida(self):
        # GAP DA SPEC v2: o vocabulario fechado (`<fonte>` ou
        # `<fonte>~inferido:<regra>`) nao vale aqui -- esta linha usa
        # `inferida:livro`, `derivado:gate-de-nivel`, `aon+foundry`. Sao 17.488
        # ocorrencias legitimas nesta convencao. Adotar o vocabulario da v2 e
        # decisao de schema, nao correcao de bug.
        ruins = [(r["id"], c, p) for r in self.base
                 for c, p in (r.get("prov") or {}).items()
                 if not comum.prov_valido(p)]
        self.assertEqual(ruins[:5], [], f"{len(ruins)} prov fora do vocabulario")

    def test_traits_nunca_e_null(self):
        # eram 66 (39 class-feature, 27 class). Decidido medindo as fontes:
        # ausencia real, nao desconhecimento (Foundry 0/66, AoN 2/66 -- e nesses
        # 2 o "trait" e so a raridade, que ja vive em `rarity`).
        nulos = [r["id"] for r in self.base if r.get("traits") is None]
        self.assertEqual(nulos[:5], [], f"{len(nulos)} registros com traits null")

    def test_spell_tem_rank_e_level_espelhados(self):
        # decidido medindo as fontes: as TRES usam `level` e NENHUMA usa `rank`
        # (AoN 2.461/2.461, Foundry 1.802/1.802, pf2etools 2.055/2.055;
        # Fireball e level 3 nas tres). `rank` e a palavra da prosa remaster.
        quebrados = [r["id"] for r in self.base
                     if r.get("kind") == "spell" and r.get("rank") is not None
                     and r.get("level") != r.get("rank")]
        self.assertEqual(quebrados[:5], [])

    def test_superseded_by_aponta_para_registro_existente(self):
        orfaos = [(r["id"], s) for r in self.base
                  for s in (r.get("superseded_by") or []) if s not in self.ids]
        self.assertEqual(orfaos[:5], [])

    def test_id_unico(self):
        self.assertEqual(len(self.ids), len(self.base))

    def test_kind_sem_grants_nao_responde_false(self):
        # `false` significa "perdi mecanica", e kind que nao produz grants nao
        # pode ter perdido nada
        ruins = [r["id"] for r in self.base
                 if r.get("kind") in comum.KINDS_SEM_GRANTS
                 and r.get("grants_completos") is False]
        self.assertEqual(ruins[:5], [])

    def test_mechanized_e_derivado_de_grants(self):
        # enquanto `mechanized` existir, a spec v1 define `mechanized ==
        # bool(grants)`. Se um dia divergir, o campo virou declaracao solta.
        ruins = [r["id"] for r in self.base
                 if "mechanized" in r and bool(r["mechanized"]) != bool(r.get("grants"))]
        self.assertEqual(ruins[:5], [], f"{len(ruins)} registros com mechanized solto")

    @unittest.expectedFailure
    def test_mechanized_nao_voltou(self):
        # GAP DA SPEC v2: `mechanized` seria substituido por
        # `grants_completos` + `requires_parseado` (null = nao se aplica).
        # Aqui os 19.738 registros ainda tem `mechanized` e nenhum tem os dois
        # campos novos. E troca de schema, com impacto no motor.
        sobrou = [r["id"] for r in self.base if "mechanized" in r]
        self.assertEqual(sobrou[:5], [])

    def test_source_book_sem_lixo_bruto(self):
        sujos = [r["id"] for r in self.base
                 if "\r" in ((r.get("source") or {}).get("book") or "")
                 or "\n" in ((r.get("source") or {}).get("book") or "")]
        self.assertEqual(sujos[:5], [])

    def test_uma_grafia_por_livro(self):
        # DEFEITO ABERTO, 2 obras de 236: `Lost Omens: Pathfinder Society
        # Guide` x `Pathfinder Lost Omens Pathfinder Society Guide` e o mesmo
        # par para `The Grand Bazaar`. Nao e o normalizador que falha (os dois
        # caem na mesma chave) -- e `canonico_livros.json`, gerado so a partir
        # do dump do AoN: essas duas obras nao tem entrada la, entao
        # `canonizar_livro` devolve a grafia de entrada e as duas sobrevivem.
        # Some quando o dump for regerado com fallback (ver TODO).
        por_chave = {}
        for r in self.base:
            livro = (r.get("source") or {}).get("book")
            if livro:
                por_chave.setdefault(comum.chave_livro(livro), set()).add(livro)
        ambiguos = {k: v for k, v in por_chave.items() if len(v) > 1}
        self.assertLessEqual(len(ambiguos), 2, ambiguos)


@unittest.skipUnless(os.path.exists(BASE), "base ainda nao emitida")
class TestPortoesMedemAlgo(unittest.TestCase):
    """Portao que passa sobre conjunto vazio nao esta medindo nada."""

    @classmethod
    def setUpClass(cls):
        with open(BASE) as fh:
            cls.base = json.load(fh)

    def test_ha_registro_com_duas_fontes_para_o_portao_8_medir(self):
        multi = sum(1 for r in self.base
                    if len([k for k in (r.get("xref") or {})
                            if k in ("aon", "foundry", "pf2etools")]) >= 2)
        self.assertGreater(multi, 1000)

    def test_ha_conflito_registrado_para_o_portao_2_medir(self):
        com_conf = sum(1 for r in self.base if r.get("conflitos"))
        self.assertGreater(com_conf, 100)

    def test_ha_referencia_wb_para_o_portao_3_medir(self):
        # o portao 3 conta orfaos; se `requires` nao citasse nenhum id `wb:`,
        # ele passaria por conjunto vazio. Medido: 4.206 citacoes.
        def refs(o):
            if isinstance(o, dict):
                for k, v in o.items():
                    if k == "has" and isinstance(v, str):
                        yield v
                    else:
                        yield from refs(v)
            elif isinstance(o, list):
                for x in o:
                    yield from refs(x)

        citados = sum(1 for r in self.base for x in refs(r.get("requires"))
                      if str(x).startswith("wb:"))
        self.assertGreater(citados, 1000)

    def test_o_censo_do_aon_mede_o_kind_ausente(self):
        # o portao 9 e o unico gabarito EXTERNO: os outros comparam a base com
        # ela mesma. Se o censo vier vazio ou a lista de fora-de-escopo comer
        # tudo, ele passa medindo nada -- que e o defeito que os portoes
        # existem para pegar.
        import portoes
        censo = portoes.censo_aon()
        self.assertGreater(len(censo), 20, "censo do AoN quase vazio")
        emescopo = [c for c in censo if c not in portoes.FORA_DE_ESCOPO]
        self.assertGreater(len(emescopo), 25, "fora-de-escopo comeu o censo")
        # e tem de continuar enxergando os dois kinds que so ele achou
        self.assertIn("tactic", censo)
        self.assertIn("class-kit", censo)
        self.assertGreaterEqual(len(censo["tactic"]), 37)

    def test_ausencia_conhecida_do_censo_esta_declarada_com_motivo(self):
        import portoes
        caminho = os.path.join(os.path.dirname(BASE), "..", "censo_ausencias.json")
        with open(os.path.normpath(caminho)) as fh:
            declarado = json.load(fh)["ausencias"]
        for cat, reg in declarado.items():
            self.assertTrue(reg.get("motivo"), cat)
            self.assertTrue(reg.get("ids_aceitos"), cat)
        n, _ = portoes.portao_9_censo(self.base, {})
        self.assertEqual(n, 0, "ausencia nova no censo do AoN")

    def test_os_portoes_que_dependem_de_fonte_nao_passam_por_ausencia(self):
        # o defeito que estava vivo: sem o dump do AoN em disco os portoes 2 e
        # 7 devolviam 0 ocorrencias -- isto e, PASSAVAM -- em vez de dizer que
        # nao mediram nada. Agora devolvem None e o main() reporta NAO MEDIDO.
        import portoes
        vazio = {"aon": {}, "foundry": {}}
        for num, _, fn, _ in portoes.PORTOES:
            if num in (2, 7):
                n, _detalhe = fn(self.base, vazio)
                self.assertIsNone(n, f"portao {num} passou sem fonte para medir")


@unittest.skipUnless(os.path.exists(BASE), "base ainda nao emitida")
class TestUniaoDeTraitsNoArtefato(unittest.TestCase):
    """Teste de funcao nao substitui invariante sobre o artefato.

    A uniao de traits tinha teste unitario verde enquanto o dado emitido
    continuava perdendo o parametro do trait -- porque a uniao rodava numa
    camada onde ja chegava uma fonte so. Este teste le a base de verdade.
    """

    @classmethod
    def setUpClass(cls):
        with open(BASE) as fh:
            cls.base = json.load(fh)

    def test_bastard_sword_mantem_o_dado_do_trait(self):
        bs = [r for r in self.base if r["id"] == "wb:weapon/bastard-sword"]
        self.assertTrue(bs, "wb:weapon/bastard-sword sumiu da base")
        self.assertIn("two-hand-d12", bs[0].get("traits") or [])

    def test_parametrizado_absorve_o_base_na_base_inteira(self):
        # nenhum registro pode ter os dois: o parametrizado engole o base
        ruins = [r["id"] for r in self.base
                 if "two-hand" in (r.get("traits") or [])
                 and any(t.startswith("two-hand-") for t in r["traits"])]
        self.assertEqual(ruins, [])

    def test_traits_nao_gera_mais_conflito(self):
        # eram 113 (95 equipment) enquanto a reparacao rodava dentro de
        # `reconciliar.main`: quem CRIA conflito de `traits` depois dela --
        # auditar_conflitos.py e desmembrar_colisoes.py -- nunca passava por
        # ela. `normalizar_traits.py` roda no fim do build e fecha isso.
        conf = [r["id"] for r in self.base
                for c in (r.get("conflitos") or []) if c.get("campo") == "traits"]
        self.assertEqual(conf[:5], [], f"{len(conf)} registros com conflito de traits")

    def test_nome_legado_de_ancestria_nao_sobrevive_nos_traits(self):
        # eram 13 (grippli 5, aasimar 3, gnoll 3, ifrit 2): o mapa de
        # `normalizacao_traits.json` existia, mas `unir()` so era chamado
        # quando havia conflito ENTRE FONTES, e registro de fonte unica nunca
        # passava por ele.
        legados = {"tiefling", "aasimar", "ifrit", "gnoll", "half-elf", "grippli"}
        ruins = [r["id"] for r in self.base if legados & set(r.get("traits") or [])]
        self.assertEqual(ruins[:5], [], f"{len(ruins)} com nome legado nos traits")

    def test_realinhamento_nao_e_desfeito_pela_uniao(self):
        # `desmembrar_colisoes` grava o valor DESCARTADO sob a chave `antes`.
        # Se a uniao tratar `antes` como fonte, ela ressuscita o trait que o
        # realinhamento acabou de tirar -- `death-from-above` voltava a ter
        # `archetype` junto de `mythic`, que e a quimera original.
        import traits_uniao
        self.assertFalse(traits_uniao.e_fonte("antes"))
        self.assertTrue(traits_uniao.e_fonte("aon"))
        self.assertTrue(traits_uniao.e_fonte("aon_2"))
        # o canonico e o feat de ARQUETIPO (feat-7610, nv8) por decisao da
        # curadoria; o mitico vive no irmao. Ter os dois traits e a quimera.
        dfa = [r for r in self.base if r["id"] == "wb:feat/death-from-above"]
        if dfa:
            self.assertNotIn("mythic", dfa[0].get("traits") or [])


if __name__ == "__main__":
    unittest.main()
